#!/usr/bin/env python3
"""
Automatic proposal fetching service with notification system
Enhanced for Streamlit integration and desktop notifications
"""
import json
import os
import time
import threading
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
import subprocess
import sys
import requests
import logging

# Email imports with fallback handling
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print("Warning: Email functionality not available due to import error")

# Timezone and cron imports with fallback
try:
    import pytz
    TIMEZONE_AVAILABLE = True
except ImportError:
    TIMEZONE_AVAILABLE = False
    print("Warning: Timezone functionality limited - install pytz for full support")

try:
    from croniter import croniter
    CRON_AVAILABLE = True
except ImportError:
    CRON_AVAILABLE = False
    print("Warning: Cron scheduling not available - install croniter for cron support")

class DesktopNotificationService:
    """Service for desktop notifications"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.show_popup = config.get('show_popup', True)
        self.play_sound = config.get('play_sound', False)
    
    def show_notification(self, title: str, message: str):
        """Show desktop notification"""
        if not self.enabled or not self.show_popup:
            return
        
        try:
            # Try to use platform-specific notification
            if sys.platform == "win32":
                self._show_windows_notification(title, message)
            elif sys.platform == "darwin":
                self._show_macos_notification(title, message)
            else:
                self._show_linux_notification(title, message)
                
        except Exception as e:
            print(f"Desktop notification failed: {e}")
    
    def _show_windows_notification(self, title: str, message: str):
        """Show Windows notification using win10toast"""
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=10, threaded=True)
        except ImportError:
            # Fallback to simple print
            print(f"🔔 {title}: {message}")
    
    def _show_macos_notification(self, title: str, message: str):
        """Show macOS notification"""
        try:
            os.system(f"""
                osascript -e 'display notification "{message}" with title "{title}"'
            """)
        except:
            print(f"🔔 {title}: {message}")
    
    def _show_linux_notification(self, title: str, message: str):
        """Show Linux notification using notify-send"""
        try:
            os.system(f'notify-send "{title}" "{message}"')
        except:
            print(f"🔔 {title}: {message}")

class NotificationService:
    """Service for sending notifications about new proposals"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.email_config = config.get('email', {})
        self.webhook_config = config.get('webhook', {})
        self.desktop_service = DesktopNotificationService(config.get('desktop', {}))
        self.enabled = config.get('enabled', True)
    
    def send_email_notification(self, subject: str, body: str, recipients: List[str]):
        """Send email notification"""
        if not EMAIL_AVAILABLE:
            print("Email functionality not available - skipping email notification")
            return
            
        if not self.email_config.get('enabled', False):
            return
        
        try:
            smtp_server = self.email_config.get('smtp_server')
            smtp_port = self.email_config.get('smtp_port', 587)
            email = self.email_config.get('email')
            password = self.email_config.get('password')
            
            if not all([smtp_server, email, password]):
                print("Email configuration incomplete, skipping email notification")
                return
            
            msg = MimeMultipart()
            msg['From'] = email
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'html'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email, password)
            
            for recipient in recipients:
                msg['To'] = recipient
                text = msg.as_string()
                server.sendmail(email, recipient, text)
                del msg['To']
            
            server.quit()
            print(f"Email notification sent to {len(recipients)} recipients")
            
        except Exception as e:
            print(f"Failed to send email notification: {e}")
    
    def send_webhook_notification(self, data: Dict):
        """Send webhook notification (e.g., to Discord, Slack)"""
        if not self.webhook_config.get('enabled', False):
            return
        
        try:
            webhook_url = self.webhook_config.get('url')
            if not webhook_url:
                return
            
            webhook_type = self.webhook_config.get('type', 'generic')
            
            if webhook_type == 'discord':
                payload = {
                    "embeds": [{
                        "title": "🔔 New Blockchain Proposals Detected",
                        "description": data.get('message', ''),
                        "color": 3447003,  # Blue
                        "timestamp": datetime.utcnow().isoformat(),
                        "fields": data.get('fields', [])
                    }]
                }
            elif webhook_type == 'slack':
                payload = {
                    "text": "🔔 New Blockchain Proposals Detected",
                    "attachments": [{
                        "color": "good",
                        "text": data.get('message', ''),
                        "fields": data.get('fields', [])
                    }]
                }
            else:
                payload = data
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                print("Webhook notification sent successfully")
            else:
                print(f"Webhook notification failed: {response.status_code}")
                
        except Exception as e:
            print(f"Failed to send webhook notification: {e}")
    
    def notify_new_proposals(self, new_proposals: Dict[str, List[Dict]]):
        """Send notifications about new proposals"""
        if not self.enabled or not new_proposals:
            return
        
        total_new = sum(len(proposals) for proposals in new_proposals.values())
        
        # Prepare notification content
        subject = f"🔔 {total_new} New Blockchain Proposals Detected"
        message = f"Found {total_new} new proposals across {len(new_proposals)} protocols"
        
        # Desktop notification
        self.desktop_service.show_notification(
            "New Blockchain Proposals", 
            f"{total_new} new proposals detected"
        )
        
        # Email body (HTML)
        email_body = f"""
        <html>
        <body>
        <h2>🔔 New Blockchain Proposals Detected</h2>
        <p>Found <strong>{total_new}</strong> new proposals across {len(new_proposals)} protocols:</p>
        """
        
        # Webhook fields
        webhook_fields = []
        
        for protocol, proposals in new_proposals.items():
            if not proposals:
                continue
                
            protocol_name = protocol.upper()
            email_body += f"""
            <h3>{protocol_name} ({len(proposals)} new)</h3>
            <ul>
            """
            
            webhook_fields.append({
                "name": f"{protocol_name}",
                "value": f"{len(proposals)} new proposals",
                "inline": True
            })
            
            for proposal in proposals[:5]:  # Show max 5 per protocol
                email_body += f"""
                <li>
                    <strong>{proposal.get('type', 'Proposal')}-{proposal.get('number', 'N/A')}</strong>: 
                    {proposal.get('title', 'No title')[:80]}
                    <br><small>Status: {proposal.get('status', 'Unknown')} | 
                    Created: {proposal.get('created', 'Unknown')}</small>
                </li>
                """
            
            if len(proposals) > 5:
                email_body += f"<li><em>...and {len(proposals) - 5} more</em></li>"
            
            email_body += "</ul>"
        
        email_body += f"""
        <p><small>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </body>
        </html>
        """
        
        # Send notifications
        recipients = self.config.get('recipients', [])
        if recipients:
            self.send_email_notification(subject, email_body, recipients)
        
        webhook_data = {
            'message': message,
            'fields': webhook_fields
        }
        self.send_webhook_notification(webhook_data)

class AdvancedScheduler:
    """Advanced scheduling manager with cron support and time windows"""
    
    def __init__(self, config: Dict):
        self.config = config
        if TIMEZONE_AVAILABLE:
            try:
                self.timezone = pytz.timezone(config.get('timezone', 'UTC'))
            except:
                self.timezone = pytz.UTC
        else:
            # Fallback to basic datetime without timezone support
            self.timezone = None
        self.runs_today = 0
        self.last_run_date = None
        self.failed_attempts = 0
        
    def is_valid_time_window(self) -> bool:
        """Check if current time is within the allowed time window"""
        if self.timezone:
            now = datetime.now(self.timezone)
        else:
            now = datetime.now()
        
        # Check if weekdays only
        if self.config.get('weekdays_only', True):
            if now.weekday() >= 5:  # Saturday=5, Sunday=6
                return False
        
        # Check enabled days
        enabled_days = self.config.get('enabled_days', [1, 2, 3, 4, 5])
        current_day = now.isoweekday()  # Monday=1, Sunday=7
        if current_day not in enabled_days:
            return False
        
        # Check time window
        start_time = self.config.get('start_time', '00:00')
        end_time = self.config.get('end_time', '23:59')
        
        if start_time and end_time:
            start_hour, start_min = map(int, start_time.split(':'))
            end_hour, end_min = map(int, end_time.split(':'))
            
            current_time = now.time()
            start_time_obj = now.replace(hour=start_hour, minute=start_min).time()
            end_time_obj = now.replace(hour=end_hour, minute=end_min).time()
            
            if not (start_time_obj <= current_time <= end_time_obj):
                return False
        
        return True
    
    def check_daily_limit(self) -> bool:
        """Check if daily run limit has been reached"""
        if self.timezone:
            now = datetime.now(self.timezone)
        else:
            now = datetime.now()
        today = now.date()
        
        # Reset counter if it's a new day
        if self.last_run_date != today:
            self.runs_today = 0
            self.last_run_date = today
        
        max_runs = self.config.get('max_runs_per_day', 24)
        return self.runs_today < max_runs
    
    def get_next_run_times(self, count: int = 5) -> List[datetime]:
        """Get the next scheduled run times"""
        schedule_type = self.config.get('type', 'interval')
        next_times = []
        
        if self.timezone:
            now = datetime.now(self.timezone)
        else:
            now = datetime.now()
        
        if schedule_type == 'cron' and CRON_AVAILABLE:
            cron_expr = self.config.get('cron_expression', '0 */1 * * *')
            try:
                cron = croniter(cron_expr, now)
                for _ in range(count):
                    next_time = cron.get_next(datetime)
                    if self._is_valid_schedule_time(next_time):
                        next_times.append(next_time)
            except Exception as e:
                print(f"Invalid cron expression: {e}")
        elif schedule_type == 'cron':
            print("Cron scheduling not available - install croniter package")
                
        elif schedule_type == 'specific_times':
            specific_times = self.config.get('specific_times', ['09:00'])
            for _ in range(count):
                for time_str in specific_times:
                    try:
                        hour, minute = map(int, time_str.split(':'))
                        next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        
                        # If time has passed today, schedule for tomorrow
                        if next_time <= now:
                            next_time += timedelta(days=1)
                        
                        if self._is_valid_schedule_time(next_time):
                            next_times.append(next_time)
                            
                    except ValueError:
                        continue
                now += timedelta(days=1)
                
        else:  # interval
            interval_minutes = self.config.get('interval_minutes', 60)
            next_time = now + timedelta(minutes=interval_minutes)
            
            for i in range(count):
                check_time = next_time + timedelta(minutes=interval_minutes * i)
                if self._is_valid_schedule_time(check_time):
                    next_times.append(check_time)
        
        return sorted(next_times)[:count]
    
    def _is_valid_schedule_time(self, dt: datetime) -> bool:
        """Check if a specific datetime is valid for scheduling"""
        # Create a temporary config for the specific datetime
        temp_config = self.config.copy()
        
        # Temporarily adjust for the datetime being checked
        if self.timezone and TIMEZONE_AVAILABLE:
            check_dt = dt.astimezone(self.timezone) if dt.tzinfo else self.timezone.localize(dt)
        else:
            check_dt = dt
        
        # Check weekdays
        if temp_config.get('weekdays_only', True) and check_dt.weekday() >= 5:
            return False
        
        # Check enabled days
        enabled_days = temp_config.get('enabled_days', [1, 2, 3, 4, 5])
        if check_dt.isoweekday() not in enabled_days:
            return False
        
        # Check time window
        start_time = temp_config.get('start_time', '00:00')
        end_time = temp_config.get('end_time', '23:59')
        
        if start_time and end_time:
            start_hour, start_min = map(int, start_time.split(':'))
            end_hour, end_min = map(int, end_time.split(':'))
            
            check_time = check_dt.time()
            start_time_obj = check_dt.replace(hour=start_hour, minute=start_min).time()
            end_time_obj = check_dt.replace(hour=end_hour, minute=end_min).time()
            
            return start_time_obj <= check_time <= end_time_obj
        
        return True
    
    def should_run_now(self) -> bool:
        """Check if a scheduled run should happen now"""
        return (self.is_valid_time_window() and 
                self.check_daily_limit())
    
    def record_run(self, success: bool = True):
        """Record a completed run"""
        if self.timezone:
            now = datetime.now(self.timezone)
        else:
            now = datetime.now()
        today = now.date()
        
        # Reset counter if it's a new day
        if self.last_run_date != today:
            self.runs_today = 0
            self.last_run_date = today
        
        self.runs_today += 1
        
        if success:
            self.failed_attempts = 0
        else:
            self.failed_attempts += 1
    
    def should_retry(self) -> bool:
        """Check if should retry after failure"""
        if not self.config.get('retry_on_failure', True):
            return False
        
        max_attempts = self.config.get('retry_max_attempts', 3)
        return self.failed_attempts < max_attempts
    
    def get_retry_delay(self) -> int:
        """Get delay before retry in minutes"""
        base_delay = self.config.get('retry_delay_minutes', 5)
        # Exponential backoff
        return base_delay * (2 ** (self.failed_attempts - 1))
    
    def get_status(self) -> Dict:
        """Get current scheduler status"""
        return {
            'timezone': str(self.timezone) if self.timezone else 'Local',
            'timezone_available': TIMEZONE_AVAILABLE,
            'cron_available': CRON_AVAILABLE,
            'is_valid_time_window': self.is_valid_time_window(),
            'daily_limit_reached': not self.check_daily_limit(),
            'runs_today': self.runs_today,
            'max_runs_per_day': self.config.get('max_runs_per_day', 24),
            'failed_attempts': self.failed_attempts,
            'schedule_type': self.config.get('type', 'interval'),
            'next_run_times': [dt.isoformat() for dt in self.get_next_run_times(3)],
            'should_run_now': self.should_run_now()
        }

class AutoProposalFetcher:
    """Automatic proposal fetching service"""
    
    def __init__(self, config_file: str = "config/auto_fetcher_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.notification_service = NotificationService(self.config.get('notifications', {}))
        self.scheduler = AdvancedScheduler(self.config.get('scheduling', {}))
        self.data_dir = self.config.get('data_dir', 'data')
        self.running = False
        self.last_check = {}
        self.logger = self._setup_logging()
        
        # Load previous state
        self.state_file = os.path.join(self.data_dir, 'fetcher_state.json')
        self.load_state()
    
    def _setup_logging(self):
        """Setup logging for the auto fetcher"""
        log_config = self.config.get('logging', {})
        if not log_config.get('enabled', True):
            return None
        
        # Create logs directory
        log_dir = os.path.dirname(log_config.get('file', 'logs/auto_fetcher.log'))
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup logger
        logger = logging.getLogger('AutoProposalFetcher')
        logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))
        
        # File handler
        file_handler = logging.FileHandler(log_config.get('file', 'logs/auto_fetcher.log'))
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log(self, message: str, level: str = 'info'):
        """Log message with appropriate level"""
        if self.logger:
            getattr(self.logger, level.lower())(message)
        else:
            print(f"[{level.upper()}] {message}")
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "enabled": True,
            "polling_interval_minutes": 60,
            "protocols": ["ethereum", "tron", "bitcoin", "binance_smart_chain"],
            "data_dir": "data",
            "notifications": {
                "enabled": True,
                "recipients": [],
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "smtp_port": 587,
                    "email": "",
                    "password": ""
                },
                "webhook": {
                    "enabled": False,
                    "type": "discord",
                    "url": ""
                },
                "desktop": {
                    "enabled": True,
                    "show_popup": True,
                    "play_sound": False
                }
            },
            "scheduling": {
                "auto_start": False,
                "type": "interval",  # "interval", "cron", "specific_times"
                "interval_minutes": 60,  # For interval type
                "cron_expression": "0 */1 * * *",  # For cron type (hourly)
                "specific_times": ["09:00", "13:00", "17:00"],  # For specific_times type
                "start_time": "09:00",
                "end_time": "18:00",
                "timezone": "Asia/Singapore",  # SGT (GMT+8)
                "weekdays_only": True,
                "enabled_days": [1, 2, 3, 4, 5],  # Monday=1 to Sunday=7
                "max_runs_per_day": 24,
                "retry_on_failure": True,
                "retry_delay_minutes": 5,
                "retry_max_attempts": 3
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file": "logs/auto_fetcher.log"
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            self.log("Configuration saved successfully")
        except Exception as e:
            self.log(f"Error saving config: {e}", 'error')
    
    def load_state(self):
        """Load previous state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.last_check = state.get('last_check', {})
        except Exception as e:
            self.log(f"Error loading state: {e}", 'error')
            self.last_check = {}
    
    def save_state(self):
        """Save current state to file"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            state = {
                'last_check': self.last_check,
                'last_update': datetime.now().isoformat()
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.log(f"Error saving state: {e}", 'error')
    
    def get_current_proposals(self, protocol: str) -> Set[int]:
        """Get set of current proposal numbers for a protocol"""
        protocol_files = {
            'ethereum': 'eips.json',
            'tron': 'tips.json',
            'bitcoin': 'bips.json',
            'binance_smart_chain': 'beps.json'
        }
        
        file_path = os.path.join(self.data_dir, protocol_files.get(protocol, f"{protocol}.json"))
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    proposals = data.get('items', [])
                    return set(p.get('number') for p in proposals if p.get('number'))
            return set()
        except Exception as e:
            self.log(f"Error reading {protocol} data: {e}", 'error')
            return set()
    
    def fetch_new_proposals(self) -> Dict[str, List[Dict]]:
        """Fetch new proposals and return them by protocol"""
        new_proposals = {}
        
        # Store current state before fetching
        current_state = {}
        for protocol in self.config.get('protocols', []):
            current_state[protocol] = self.get_current_proposals(protocol)
        
        # Run the data generation script
        try:
            self.log("🔄 Running proposal data update...")
            result = subprocess.run([
                sys.executable, 'scripts/generate_all_data.py'
            ], cwd='.', capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                self.log(f"Data generation failed: {result.stderr}", 'error')
                return {}
            
            self.log("✅ Data generation completed")
            
        except Exception as e:
            self.log(f"Error running data generation: {e}", 'error')
            return {}
        
        # Compare with new state to find new proposals
        for protocol in self.config.get('protocols', []):
            old_proposals = current_state.get(protocol, set())
            new_proposal_numbers = self.get_current_proposals(protocol) - old_proposals
            
            if new_proposal_numbers:
                # Get details of new proposals
                protocol_files = {
                    'ethereum': 'eips.json',
                    'tron': 'tips.json',
                    'bitcoin': 'bips.json',
                    'binance_smart_chain': 'beps.json'
                }
                
                file_path = os.path.join(self.data_dir, protocol_files.get(protocol, f"{protocol}.json"))
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        proposals = data.get('items', [])
                        
                        new_proposal_details = []
                        for proposal in proposals:
                            if proposal.get('number') in new_proposal_numbers:
                                new_proposal_details.append(proposal)
                        
                        if new_proposal_details:
                            new_proposals[protocol] = new_proposal_details
                            self.log(f"🆕 Found {len(new_proposal_details)} new {protocol} proposals")
                
                except Exception as e:
                    self.log(f"Error reading new {protocol} proposals: {e}", 'error')
        
        return new_proposals
    
    def check_for_updates(self):
        """Check for new proposals and send notifications"""
        # Check if we should run based on schedule
        if not self.scheduler.should_run_now():
            self.log("⏰ Skipping check - outside scheduled time window or daily limit reached")
            return
        
        self.log(f"🔍 Checking for new proposals at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        success = False
        try:
            new_proposals = self.fetch_new_proposals()
            
            if new_proposals:
                total_new = sum(len(proposals) for proposals in new_proposals.values())
                self.log(f"🎉 Found {total_new} new proposals!")
                
                # Send notifications
                self.notification_service.notify_new_proposals(new_proposals)
                
                # Update last check time
                self.last_check = {
                    'timestamp': datetime.now().isoformat(),
                    'new_proposals_count': total_new,
                    'protocols_with_new': list(new_proposals.keys())
                }
                self.save_state()
                success = True
                
            else:
                self.log("✅ No new proposals found")
                self.last_check = {
                    'timestamp': datetime.now().isoformat(),
                    'new_proposals_count': 0,
                    'protocols_with_new': []
                }
                self.save_state()
                success = True
                
        except Exception as e:
            self.log(f"❌ Error during update check: {e}", 'error')
            success = False
        
        # Record the run attempt
        self.scheduler.record_run(success)
        
        # Schedule retry if failed and retries are enabled
        if not success and self.scheduler.should_retry():
            retry_delay = self.scheduler.get_retry_delay()
            self.log(f"🔄 Scheduling retry in {retry_delay} minutes (attempt {self.scheduler.failed_attempts})")
            schedule.every(retry_delay).minutes.do(self._retry_check).tag('retry')
    
    def _retry_check(self):
        """Retry method for failed checks"""
        # Clear retry jobs
        schedule.clear('retry')
        # Perform the check
        self.check_for_updates()
        return schedule.CancelJob
    
    def start_scheduler(self):
        """Start the background scheduler with advanced scheduling support"""
        if not self.config.get('enabled', True):
            self.log("Auto fetcher is disabled in configuration")
            return
        
        scheduling_config = self.config.get('scheduling', {})
        schedule_type = scheduling_config.get('type', 'interval')
        
        self.log(f"🚀 Starting auto proposal fetcher with {schedule_type} scheduling")
        
        # Clear any existing schedules
        schedule.clear()
        
        # Set up scheduling based on type
        if schedule_type == 'cron':
            self._setup_cron_schedule()
        elif schedule_type == 'specific_times':
            self._setup_specific_times_schedule()
        else:  # interval
            self._setup_interval_schedule()
        
        # Show next run times
        next_runs = self.scheduler.get_next_run_times(3)
        if next_runs:
            self.log(f"📅 Next scheduled runs: {[dt.strftime('%Y-%m-%d %H:%M:%S %Z') for dt in next_runs]}")
        
        # Initial check if auto_start is enabled
        if scheduling_config.get('auto_start', False):
            self.log("🏃 Running initial check...")
            self.check_for_updates()
        
        self.running = True
        
        # Keep the scheduler running
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute if it's time to run
    
    def _setup_interval_schedule(self):
        """Setup interval-based scheduling"""
        scheduling_config = self.config.get('scheduling', {})
        interval = scheduling_config.get('interval_minutes', 60)
        self.log(f"⏰ Interval scheduling: every {interval} minutes")
        schedule.every(interval).minutes.do(self.check_for_updates)
    
    def _setup_cron_schedule(self):
        """Setup cron-like scheduling"""
        if not CRON_AVAILABLE:
            self.log("⚠️ Cron scheduling not available - install croniter package. Falling back to hourly schedule.")
            schedule.every().hour.do(self.check_for_updates)
            return
            
        scheduling_config = self.config.get('scheduling', {})
        cron_expr = scheduling_config.get('cron_expression', '0 */1 * * *')
        self.log(f"⏰ Cron scheduling: {cron_expr}")
        
        # Convert cron to schedule.py format (simplified)
        try:
            # This is a simplified cron parser - for full cron support, 
            # you might want to use APScheduler instead
            parts = cron_expr.split()
            if len(parts) == 5:
                minute, hour, day, month, weekday = parts
                
                if hour.startswith('*/'):  # Every N hours
                    hours_interval = int(hour[2:])
                    schedule.every(hours_interval).hours.do(self.check_for_updates)
                elif minute.startswith('*/'):  # Every N minutes
                    minutes_interval = int(minute[2:])
                    schedule.every(minutes_interval).minutes.do(self.check_for_updates)
                else:
                    # For specific times, fall back to hourly checks with validation
                    schedule.every().hour.do(self.check_for_updates)
                    
        except Exception as e:
            self.log(f"⚠️ Invalid cron expression, falling back to hourly: {e}")
            schedule.every().hour.do(self.check_for_updates)
    
    def _setup_specific_times_schedule(self):
        """Setup specific times scheduling"""
        scheduling_config = self.config.get('scheduling', {})
        specific_times = scheduling_config.get('specific_times', ['09:00'])
        self.log(f"⏰ Specific times scheduling: {specific_times}")
        
        for time_str in specific_times:
            try:
                schedule.every().day.at(time_str).do(self.check_for_updates)
            except Exception as e:
                self.log(f"⚠️ Invalid time format '{time_str}': {e}")
    
    def set_schedule(self, schedule_type: str, **kwargs):
        """Dynamically update the schedule configuration"""
        scheduling_config = self.config.setdefault('scheduling', {})
        scheduling_config['type'] = schedule_type
        
        if schedule_type == 'interval':
            interval_minutes = kwargs.get('interval_minutes', 60)
            scheduling_config['interval_minutes'] = interval_minutes
            self.log(f"📝 Updated to interval scheduling: every {interval_minutes} minutes")
            
        elif schedule_type == 'cron':
            cron_expression = kwargs.get('cron_expression', '0 */1 * * *')
            scheduling_config['cron_expression'] = cron_expression
            self.log(f"📝 Updated to cron scheduling: {cron_expression}")
            
        elif schedule_type == 'specific_times':
            specific_times = kwargs.get('specific_times', ['09:00'])
            scheduling_config['specific_times'] = specific_times
            self.log(f"📝 Updated to specific times scheduling: {specific_times}")
        
        # Update other scheduling parameters
        for key, value in kwargs.items():
            if key in ['start_time', 'end_time', 'timezone', 'weekdays_only', 
                      'enabled_days', 'max_runs_per_day']:
                scheduling_config[key] = value
        
        # Recreate the scheduler with new config
        self.scheduler = AdvancedScheduler(scheduling_config)
        
        # Save updated configuration
        self.save_config()
        
        # Restart scheduler if it's running
        if self.running:
            self.log("🔄 Restarting scheduler with new configuration...")
            schedule.clear()
            if schedule_type == 'cron':
                self._setup_cron_schedule()
            elif schedule_type == 'specific_times':
                self._setup_specific_times_schedule()
            else:
                self._setup_interval_schedule()
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.log("🛑 Stopping auto proposal fetcher")
        self.running = False
        schedule.clear()
    
    def run_in_background(self):
        """Run the scheduler in a background thread"""
        if hasattr(self, '_scheduler_thread') and self._scheduler_thread.is_alive():
            self.log("Auto fetcher is already running")
            return
        
        self._scheduler_thread = threading.Thread(target=self.start_scheduler, daemon=True)
        self._scheduler_thread.start()
        self.log("🔄 Auto proposal fetcher started in background")
    
    def get_status(self) -> Dict:
        """Get current status of the auto fetcher"""
        base_status = {
            'enabled': self.config.get('enabled', True),
            'running': self.running,
            'last_check': self.last_check,
            'protocols': self.config.get('protocols', []),
            'notifications_enabled': self.notification_service.enabled,
            'config_file': self.config_file,
            'data_dir': self.data_dir
        }
        
        # Add detailed scheduler status
        scheduler_status = self.scheduler.get_status()
        base_status['scheduler'] = scheduler_status
        
        return base_status
    
    def get_schedule_preview(self, days: int = 7) -> List[Dict]:
        """Get a preview of upcoming scheduled runs"""
        next_runs = self.scheduler.get_next_run_times(days * 4)  # Estimate more than needed
        
        preview = []
        for run_time in next_runs[:days * 4]:  # Limit to reasonable number
            if self.scheduler.timezone and TIMEZONE_AVAILABLE:
                local_time = run_time.astimezone(self.scheduler.timezone)
                time_str = local_time.strftime('%Y-%m-%d %H:%M:%S %Z')
            else:
                local_time = run_time
                time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')
            
            preview.append({
                'datetime': run_time.isoformat(),
                'local_time': time_str,
                'day_of_week': local_time.strftime('%A'),
                'valid': self.scheduler._is_valid_schedule_time(run_time)
            })
        
        return preview[:20]  # Limit to 20 entries for display

# Global instance
auto_fetcher = AutoProposalFetcher()