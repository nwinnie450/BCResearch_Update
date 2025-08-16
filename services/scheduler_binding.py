"""
APScheduler binding for persistent schedules
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
import threading
import logging

try:
    from pytz import timezone
except ImportError:
    # Fallback if pytz not available
    from datetime import timezone as _tz, timedelta
    def timezone(name):
        if name == "Asia/Singapore":
            return _tz(timedelta(hours=8))
        return _tz.utc

# Global lock to prevent concurrent fetcher runs
_run_lock = threading.Lock()

def standalone_job_function(sched_id: str):
    """Standalone job function that can be serialized by APScheduler"""
    logger = logging.getLogger("ScheduledJob")
    
    # Try to acquire lock (non-blocking)
    if not _run_lock.acquire(blocking=False):
        logger.warning(f"Schedule {sched_id[:8]} skipped (previous run still in progress)")
        return
    
    try:
        # Load current schedule data and fetcher fresh each time
        from .schedules_store import load_schedules, save_schedules
        from .auto_proposal_fetcher import AutoProposalFetcher
        
        schedules = load_schedules()
        sched = next((s for s in schedules if s["id"] == sched_id), None)
        
        if not sched:
            logger.error(f"Schedule {sched_id[:8]} not found")
            return
            
        if not sched.get("enabled", True):
            logger.info(f"Schedule {sched_id[:8]} disabled, skipping")
            return
        
        # Check time window
        try:
            from pytz import timezone
        except ImportError:
            from datetime import timezone as _tz, timedelta
            def timezone(name):
                if name == "Asia/Singapore":
                    return _tz(timedelta(hours=8))
                return _tz.utc
                
        tz = timezone(sched.get("timezone", "Asia/Singapore"))
        now = datetime.now(tz)
        
        # Check weekdays only rule
        if sched.get("weekdays_only", True) and now.weekday() >= 5:  # 5/6 = Sat/Sun
            logger.info(f"Schedule {sched_id[:8]} skipped (outside time window - weekdays only)")
            return
        
        # Check end time rule
        end_time_str = sched.get("end_time")
        if end_time_str:
            try:
                from datetime import time
                hh, mm = map(int, end_time_str.split(":"))
                end_time_obj = time(hh, mm)
                if now.time() > end_time_obj:
                    logger.info(f"Schedule {sched_id[:8]} skipped (past end time)")
                    return
            except (ValueError, AttributeError):
                logger.warning(f"Invalid end_time format: {end_time_str}")
        
        logger.info(f"Starting fetch for schedule {sched_id[:8]}: {sched.get('name', 'Untitled')}")
        
        # Create fresh fetcher instance
        fetcher = AutoProposalFetcher()
        
        # Set protocols for this specific schedule
        if sched.get("chains"):
            fetcher.config['protocols'] = sched["chains"]
        
        # Run the actual fetch
        result = fetcher.fetch_new_proposals()
        
        # Update last run time
        sched["last_run"] = datetime.now().isoformat()
        save_schedules(schedules)
        
        logger.info(f"Completed fetch for schedule {sched_id[:8]}")
        
    except Exception as e:
        logger.error(f"Error in schedule {sched_id[:8]}: {e}")
        
    finally:
        _run_lock.release()

class SchedulerManager:
    """Manages APScheduler jobs for persistent schedules"""
    
    def __init__(self, jobstore_url="sqlite:///data/jobs.db"):
        # Ensure data directory exists
        import os
        os.makedirs("data", exist_ok=True)
        
        self.scheduler = BackgroundScheduler(
            jobstores={"default": SQLAlchemyJobStore(url=jobstore_url)},
            timezone=timezone("Asia/Singapore")
        )
        self.logger = logging.getLogger(__name__)
        
        # Start scheduler
        try:
            self.scheduler.start()
            self.logger.info("Scheduler started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}")
    
    def _job_id(self, sched_id: str) -> str:
        """Generate APScheduler job ID from schedule ID"""
        return f"fetch_{sched_id}"
    
    def upsert_job(self, sched: dict):
        """Create or update APScheduler job for a schedule"""
        job_id = self._job_id(sched["id"])
        sched_id = sched["id"]
        
        # Remove existing job if it exists
        try:
            # Remove main job and any sub-jobs (for specific_times)
            existing_jobs = [j for j in self.scheduler.get_jobs() if j.id.startswith(job_id)]
            for job in existing_jobs:
                self.scheduler.remove_job(job.id)
        except Exception as e:
            self.logger.debug(f"No existing job to remove: {e}")
        
        # Don't create job if disabled
        if not sched.get("enabled", True):
            self.logger.info(f"Schedule {sched['id'][:8]} disabled, no job created")
            return
        
        try:
            tz = timezone(sched.get("timezone", "Asia/Singapore"))
            mode = sched.get("mode", "interval")
            
            if mode == "interval":
                # Interval-based scheduling
                minutes = int(sched.get("interval_minutes", 60))
                trigger = IntervalTrigger(minutes=minutes, timezone=tz)
                
                self.scheduler.add_job(
                    standalone_job_function,
                    trigger,
                    id=job_id,
                    args=[sched_id],
                    replace_existing=True,
                    max_instances=1,
                    coalesce=True,
                    misfire_grace_time=600
                )
                
            elif mode == "specific_times":
                # Specific times scheduling
                times = sched.get("times", ["09:00"])
                for time_str in times:
                    try:
                        h, m = map(int, time_str.split(":"))
                        sub_job_id = f"{job_id}_{h:02d}{m:02d}"
                        
                        trigger = CronTrigger(hour=h, minute=m, timezone=tz)
                        self.scheduler.add_job(
                            standalone_job_function,
                            trigger,
                            id=sub_job_id,
                            args=[sched_id],
                            replace_existing=True,
                            max_instances=1,
                            coalesce=True
                        )
                    except (ValueError, IndexError) as e:
                        self.logger.error(f"Invalid time format {time_str}: {e}")
                        
            else:  # cron
                # Cron expression scheduling
                cron_expr = sched.get("cron", "0 */1 * * *")
                trigger = CronTrigger.from_crontab(cron_expr, timezone=tz)
                
                self.scheduler.add_job(
                    standalone_job_function,
                    trigger,
                    id=job_id,
                    args=[sched_id],
                    replace_existing=True,
                    max_instances=1,
                    coalesce=True,
                    misfire_grace_time=600
                )
            
            self.logger.info(f"Job created for schedule {sched['id'][:8]}: {sched.get('name', 'Untitled')}")
            
        except Exception as e:
            self.logger.error(f"Failed to create job for schedule {sched['id']}: {e}")
    
    def delete_job(self, sched_id: str):
        """Delete APScheduler job(s) for a schedule"""
        job_id = self._job_id(sched_id)
        
        # Remove main job and any sub-jobs
        removed_count = 0
        for job in list(self.scheduler.get_jobs()):
            if job.id.startswith(job_id):
                try:
                    self.scheduler.remove_job(job.id)
                    removed_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to remove job {job.id}: {e}")
        
        self.logger.info(f"Removed {removed_count} job(s) for schedule {sched_id[:8]}")
    
    def get_job_info(self, sched_id: str) -> dict:
        """Get information about jobs for a schedule"""
        job_id = self._job_id(sched_id)
        jobs = [j for j in self.scheduler.get_jobs() if j.id.startswith(job_id)]
        
        return {
            "job_count": len(jobs),
            "next_run": jobs[0].next_run_time if jobs else None,
            "jobs": [{"id": j.id, "next_run": j.next_run_time} for j in jobs]
        }
    
    def refresh_all_jobs(self):
        """Refresh all jobs from persistent storage"""
        from .schedules_store import load_schedules
        schedules = load_schedules()
        
        for sched in schedules:
            self.upsert_job(sched)
        
        self.logger.info(f"Refreshed {len(schedules)} schedule jobs")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        try:
            self.scheduler.shutdown(wait=False)
            self.logger.info("Scheduler shut down")
        except Exception as e:
            self.logger.error(f"Error shutting down scheduler: {e}")