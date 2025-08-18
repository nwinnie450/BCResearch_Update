"""
Schedule Executor Service
Runs saved schedules and fetches proposals automatically with notifications
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

# Desktop notification imports
try:
    import win10toast
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

# Email imports
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_AVAILABLE = True
except ImportError as e:
    EMAIL_AVAILABLE = False
    print(f"Email import error: {e}")

# Slack imports
try:
    import requests
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

class ScheduleExecutor:
    """Execute saved schedules and trigger proposal fetching with notifications"""
    
    def __init__(self):
        self.running = False
        self.schedules_file = "data/simple_schedules.json"
        self.last_check_file = "data/last_proposal_check.json"
        self.email_config_file = "data/email_config.json"
        self.slack_config_file = "data/slack_config.json"
        self.thread = None
        self.last_proposals = {}  # Store last known proposals for comparison
        
    def load_schedules(self):
        """Load saved schedules"""
        if os.path.exists(self.schedules_file):
            try:
                with open(self.schedules_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def load_email_config(self):
        """Load email configuration"""
        if os.path.exists(self.email_config_file):
            try:
                with open(self.email_config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_email_config(self, config):
        """Save email configuration"""
        os.makedirs("data", exist_ok=True)
        try:
            with open(self.email_config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving email config: {e}")
            return False
    
    def load_slack_config(self):
        """Load Slack configuration"""
        if os.path.exists(self.slack_config_file):
            try:
                with open(self.slack_config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_slack_config(self, config):
        """Save Slack configuration"""
        os.makedirs("data", exist_ok=True)
        try:
            with open(self.slack_config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving Slack config: {e}")
            return False
    
    def load_last_check(self):
        """Load last check data to compare for new proposals"""
        if os.path.exists(self.last_check_file):
            try:
                with open(self.last_check_file, 'r') as f:
                    data = json.load(f)
                    # Convert lists back to sets for comparison
                    if 'proposals' in data:
                        proposals = {}
                        for protocol, proposal_list in data['proposals'].items():
                            if isinstance(proposal_list, list):
                                proposals[protocol] = set(proposal_list)
                            else:
                                proposals[protocol] = set()
                        return proposals
                    return {}
            except:
                return {}
        return {}
    
    def save_last_check(self, proposals_data):
        """Save current proposals for next comparison"""
        os.makedirs("data", exist_ok=True)
        try:
            # Convert sets to lists for JSON serialization
            serializable_data = {}
            for protocol, proposal_set in proposals_data.items():
                if isinstance(proposal_set, set):
                    serializable_data[protocol] = list(proposal_set)
                else:
                    serializable_data[protocol] = proposal_set
            
            with open(self.last_check_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'proposals': serializable_data
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving last check: {e}")
    
    def get_current_proposals(self):
        """Get current proposals from all protocols"""
        protocols = {
            'ethereum': 'data/eips.json',
            'tron': 'data/tips.json', 
            'bitcoin': 'data/bips.json',
            'binance_smart_chain': 'data/beps.json'
        }
        
        current_proposals = {}
        
        for protocol, file_path in protocols.items():
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        proposals = data.get('items', [])
                        # Store proposal numbers for comparison
                        current_proposals[protocol] = set(p.get('number') for p in proposals if p.get('number'))
                except Exception as e:
                    print(f"Error reading {protocol} proposals: {e}")
                    current_proposals[protocol] = set()
            else:
                current_proposals[protocol] = set()
        
        return current_proposals
    
    def fetch_latest_proposals(self, selected_protocols=None):
        """Run the proposal fetching script for selected protocols or all"""
        try:
            print(f"Fetching latest proposals at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
            
            if selected_protocols and len(selected_protocols) > 0:
                # Use the real-time fetcher for selected protocols
                try:
                    from services.realtime_data_fetcher import realtime_data_fetcher
                    
                    print(f"Using real-time fetcher for protocols: {', '.join(selected_protocols)}")
                    
                    if len(selected_protocols) == 1:
                        result = realtime_data_fetcher.fetch_protocol_data(selected_protocols[0])
                        success = result.get('success', False)
                        if success:
                            print(f"SUCCESS: Fetched {result.get('count', 0)} proposals for {selected_protocols[0]}")
                        else:
                            print(f"ERROR: {result.get('error', 'Unknown error')}")
                        return success
                    else:
                        result = realtime_data_fetcher.fetch_multiple_protocols(selected_protocols)
                        success = result.get('success', False)
                        if success:
                            print(f"SUCCESS: Fetched {result.get('total_proposals_fetched', 0)} proposals from {result.get('successful_protocols', 0)} protocols")
                        else:
                            print(f"ERROR: {result.get('error', 'Unknown error')}")
                        return success
                        
                except ImportError:
                    print("Real-time fetcher not available, falling back to generate_all_data.py")
                    # Fall back to original method
                    pass
            
            # Original method - fetch all protocols
            result = subprocess.run([
                sys.executable, 'scripts/generate_all_data.py'
            ], cwd='.', capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("SUCCESS: Proposal fetching completed successfully")
                return True
            else:
                print(f"ERROR: Proposal fetching failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"ERROR running proposal fetch: {e}")
            return False
    
    def check_for_new_proposals(self):
        """Check for new proposals and send notifications"""
        try:
            # Get proposals before fetching
            old_proposals = self.get_current_proposals()
            
            # Fetch latest proposals
            if not self.fetch_latest_proposals():
                return False
            
            # Get proposals after fetching  
            new_proposals = self.get_current_proposals()
            
            # Compare and find new ones
            new_found = {}
            total_new = 0
            
            for protocol in new_proposals:
                old_set = old_proposals.get(protocol, set())
                new_set = new_proposals.get(protocol, set())
                new_numbers = new_set - old_set
                
                if new_numbers:
                    new_found[protocol] = list(new_numbers)
                    total_new += len(new_numbers)
                    print(f"NEW: Found {len(new_numbers)} new {protocol} proposals")
            
            # Send notification if new proposals found
            if new_found:
                self.send_notification(new_found, total_new)
                print(f"TOTAL: {total_new} new proposals found")
            else:
                print("SUCCESS: No new proposals found")
            
            # Save current state for next comparison
            self.save_last_check(new_proposals)
            
            return True
            
        except Exception as e:
            print(f"ERROR checking for new proposals: {e}")
            return False
    
    def send_notification(self, new_proposals: Dict, total_new: int):
        """Send desktop and email notifications about new proposals"""
        try:
            # Create notification message
            title = f"{total_new} New Blockchain Proposals!"
            
            message_parts = []
            for protocol, numbers in new_proposals.items():
                protocol_name = protocol.replace('_', ' ').title()
                if protocol == 'binance_smart_chain':
                    protocol_name = 'BSC'
                message_parts.append(f"{protocol_name}: {len(numbers)} new")
            
            message = " | ".join(message_parts)
            
            # Send desktop notification
            self.send_desktop_notification(title, message)
            
            # Send email notification
            self.send_email_notification(new_proposals, total_new)
                
        except Exception as e:
            print(f"ERROR sending notification: {e}")
    
    def send_desktop_notification(self, title: str, message: str):
        """Send desktop notification"""
        try:
            if NOTIFICATIONS_AVAILABLE:
                try:
                    toaster = win10toast.ToastNotifier()
                    toaster.show_toast(
                        title,
                        message,
                        duration=10,
                        threaded=True,
                        icon_path=None
                    )
                    print(f"Desktop notification sent: {title}")
                except Exception as e:
                    print(f"Desktop notification failed: {e}")
            else:
                print(f"Notification: {title} - {message}")
        except Exception as e:
            print(f"Error sending desktop notification: {e}")
    
    def send_email_notification(self, new_proposals: Dict, total_new: int):
        """Send email notification about new proposals"""
        try:
            # Load email configuration
            email_config = self.load_email_config()
            
            if not email_config.get('enabled', False):
                print("Email notifications disabled")
                return
            
            if not EMAIL_AVAILABLE:
                print("Email functionality not available")
                return
            
            # Get email settings
            smtp_server = email_config.get('smtp_server')
            smtp_port = email_config.get('smtp_port', 587)
            sender_email = email_config.get('sender_email')
            sender_password = email_config.get('sender_password')
            recipient_emails = email_config.get('recipient_emails', [])
            
            if not all([smtp_server, sender_email, sender_password, recipient_emails]):
                print("Email configuration incomplete")
                return
            
            # Create email content
            subject = f"New Blockchain Proposals Alert - {total_new} Updates Found"
            
            # HTML email body
            html_body = f"""
            <html>
            <body>
                <h2 style="color: #2c3e50;">🔔 New Blockchain Proposals Detected</h2>
                <p>We found <strong>{total_new}</strong> new blockchain proposals:</p>
                
                <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Protocol</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">New Proposals</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Proposal Numbers</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for protocol, numbers in new_proposals.items():
                protocol_name = protocol.replace('_', ' ').title()
                if protocol == 'binance_smart_chain':
                    protocol_name = 'Binance Smart Chain'
                elif protocol == 'ethereum':
                    protocol_name = 'Ethereum'
                elif protocol == 'tron':
                    protocol_name = 'Tron'
                elif protocol == 'bitcoin':
                    protocol_name = 'Bitcoin'
                
                numbers_str = ', '.join(map(str, sorted(numbers)))
                
                html_body += f"""
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 12px;">{protocol_name}</td>
                            <td style="border: 1px solid #ddd; padding: 12px; text-align: center;"><strong>{len(numbers)}</strong></td>
                            <td style="border: 1px solid #ddd; padding: 12px;">{numbers_str}</td>
                        </tr>
                """
            
            html_body += f"""
                    </tbody>
                </table>
                
                <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4 style="margin: 0; color: #2c3e50;">📊 Summary</h4>
                    <p style="margin: 5px 0;">Total new proposals: <strong>{total_new}</strong></p>
                    <p style="margin: 5px 0;">Check time: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong></p>
                </div>
                
                <hr style="margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    This email was sent automatically by your Blockchain Proposal Monitor.<br>
                    Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </body>
            </html>
            """
            
            # Send email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipient_emails)
            
            # Add HTML part
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Connect and send
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            print(f"Email notification sent to {len(recipient_emails)} recipients")
            
        except Exception as e:
            print(f"Error sending email notification: {e}")
    
    def setup_schedules(self):
        """Setup all saved schedules"""
        schedules = self.load_schedules()
        
        if not schedules:
            print("SCHEDULES: No schedules found")
            return
        
        # Clear existing schedules
        schedule.clear()
        
        for sched in schedules:
            if not sched.get('enabled', True):
                continue
                
            name = sched.get('name', 'Unnamed')
            frequency = sched.get('frequency', '')
            days = sched.get('days', [])
            time_24h = sched.get('time_24h', '09:00')
            
            try:
                # Parse time
                hour, minute = map(int, time_24h.split(':'))
                time_str = f"{hour:02d}:{minute:02d}"
                
                print(f"SCHEDULE: Setting up schedule: {name}")
                print(f"   Frequency: {frequency}")
                print(f"   Days: {', '.join(days)}")
                print(f"   Time: {time_str}")
                
                # Setup based on frequency
                if "Daily" in frequency:
                    # Every day
                    schedule.every().day.at(time_str).do(
                        self.run_scheduled_check, 
                        schedule_name=name
                    ).tag(sched.get('id', name))
                    
                elif "Weekdays" in frequency:
                    # Monday to Friday
                    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                        getattr(schedule.every(), day).at(time_str).do(
                            self.run_scheduled_check,
                            schedule_name=name
                        ).tag(sched.get('id', name))
                        
                elif "Weekly" in frequency or "Bi-weekly" in frequency:
                    # Specific days
                    day_mapping = {
                        'Monday': 'monday', 'Tuesday': 'tuesday', 'Wednesday': 'wednesday',
                        'Thursday': 'thursday', 'Friday': 'friday', 'Saturday': 'saturday', 'Sunday': 'sunday'
                    }
                    
                    for day in days:
                        if day in day_mapping:
                            getattr(schedule.every(), day_mapping[day]).at(time_str).do(
                                self.run_scheduled_check,
                                schedule_name=name
                            ).tag(sched.get('id', name))
                            
                elif "Custom" in frequency:
                    # Custom selected days
                    day_mapping = {
                        'Monday': 'monday', 'Tuesday': 'tuesday', 'Wednesday': 'wednesday',
                        'Thursday': 'thursday', 'Friday': 'friday', 'Saturday': 'saturday', 'Sunday': 'sunday'
                    }
                    
                    for day in days:
                        if day in day_mapping:
                            getattr(schedule.every(), day_mapping[day]).at(time_str).do(
                                self.run_scheduled_check,
                                schedule_name=name
                            ).tag(sched.get('id', name))
                
                print(f"SUCCESS: Schedule '{name}' setup complete")
                
            except Exception as e:
                print(f"ERROR setting up schedule '{name}': {e}")
        
        print(f"TOTAL: {len([s for s in schedules if s.get('enabled', True)])} active schedules")
    
    def run_scheduled_check(self, schedule_name: str):
        """Run a scheduled proposal check"""
        print(f"SCHEDULED: Running scheduled check: {schedule_name}")
        success = self.check_for_new_proposals()
        
        if success:
            print(f"SUCCESS: Scheduled check '{schedule_name}' completed successfully")
        else:
            print(f"ERROR: Scheduled check '{schedule_name}' failed")
        
        return success
    
    def start(self):
        """Start the schedule executor"""
        if self.running:
            print("WARNING: Schedule executor is already running")
            return
        
        print("STARTING: Schedule Executor...")
        
        # Setup schedules
        self.setup_schedules()
        
        # Start background thread
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        print("SUCCESS: Schedule Executor started successfully")
        print("NOTIFICATIONS: Will send desktop notifications when new proposals are found")
    
    def stop(self):
        """Stop the schedule executor"""
        print("STOPPING: Schedule Executor...")
        self.running = False
        schedule.clear()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        
        print("SUCCESS: Schedule Executor stopped")
    
    def _run_scheduler(self):
        """Background scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"ERROR Scheduler: {e}")
                time.sleep(60)
    
    def get_status(self):
        """Get current status"""
        schedules = self.load_schedules()
        active_schedules = [s for s in schedules if s.get('enabled', True)]
        email_config = self.load_email_config()
        
        return {
            'running': self.running,
            'total_schedules': len(schedules),
            'active_schedules': len(active_schedules),
            'notifications_available': NOTIFICATIONS_AVAILABLE,
            'email_available': EMAIL_AVAILABLE,
            'email_enabled': email_config.get('enabled', False),
            'email_configured': bool(email_config.get('smtp_server') and email_config.get('sender_email')),
            'next_jobs': [str(job) for job in schedule.jobs[:5]]  # Next 5 scheduled jobs
        }
    
    def run_manual_check(self):
        """Run a manual check for testing"""
        print("MANUAL: Running manual proposal check...")
        return self.check_for_new_proposals()

# Global instance
schedule_executor = ScheduleExecutor()