#!/usr/bin/env python3
"""
Automatic Blockchain Proposal Scheduler
Runs continuously and triggers notifications at scheduled times
"""
import sys
import time
import datetime
import signal
import logging

# Add current directory to path
sys.path.append('.')

from services.schedule_executor import ScheduleExecutor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AutomaticScheduler:
    """Persistent automatic scheduler for blockchain proposal notifications"""
    
    def __init__(self):
        self.running = False
        self.executor = None
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info("Received shutdown signal. Stopping scheduler...")
        self.stop()
    
    def start(self):
        """Start the automatic scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info("=== STARTING AUTOMATIC BLOCKCHAIN PROPOSAL SCHEDULER ===")
        logger.info(f"Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Initialize and start the schedule executor
            self.executor = ScheduleExecutor()
            self.executor.start()
            self.running = True
            
            logger.info("✅ Automatic scheduler started successfully!")
            logger.info("📅 Schedule: Daily at 10:00 AM")
            logger.info("🔄 Scheduler will run continuously...")
            logger.info("⏹️  Press Ctrl+C to stop")
            
            # Keep the scheduler running
            self._run_loop()
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            self.stop()
    
    def _run_loop(self):
        """Main scheduler loop"""
        last_status_time = datetime.datetime.now()
        
        while self.running:
            try:
                time.sleep(10)  # Check every 10 seconds
                current_time = datetime.datetime.now()
                
                # Print status every 5 minutes
                if (current_time - last_status_time).total_seconds() >= 300:
                    logger.info(f"🔄 Scheduler active - Next run: Daily at 10:00 AM")
                    last_status_time = current_time
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(30)  # Wait before retrying
    
    def stop(self):
        """Stop the scheduler gracefully"""
        if not self.running:
            return
        
        logger.info("🛑 Stopping automatic scheduler...")
        self.running = False
        
        if self.executor:
            try:
                self.executor.stop()
                logger.info("✅ Schedule executor stopped")
            except Exception as e:
                logger.error(f"Error stopping executor: {e}")
        
        logger.info("✅ Automatic scheduler shutdown complete")

def main():
    """Main entry point"""
    scheduler = AutomaticScheduler()
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt in main")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        scheduler.stop()

if __name__ == "__main__":
    main()