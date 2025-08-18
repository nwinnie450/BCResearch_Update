#!/usr/bin/env python3
"""
Quick Test Notification Trigger
Easy way to test notifications anytime
"""
import sys
sys.path.insert(0, '.')

import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from services.schedule_executor import ScheduleExecutor

try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
    DESKTOP_OK = True
except ImportError:
    DESKTOP_OK = False

def quick_test():
    print("=== QUICK NOTIFICATION TEST ===")
    print(f"Time: {datetime.now().strftime('%I:%M:%S %p')}")
    print()
    
    # Test desktop notification
    print("1. Testing desktop notification...")
    if DESKTOP_OK:
        toaster.show_toast(
            "Blockchain Research Agent - TEST",
            "This is a test notification",
            duration=5
        )
        print("   Desktop notification sent!")
    else:
        print("   Desktop notification not available")
    
    # Test email notification  
    print("2. Testing email notification...")
    
    executor = ScheduleExecutor()
    email_config = executor.load_email_config()
    
    if email_config and email_config.get('enabled'):
        try:
            # Quick email
            msg = MIMEText("This is a quick test from Blockchain Research Agent")
            msg['Subject'] = "Test Notification - System Check"
            msg['From'] = email_config['sender_email']
            msg['To'] = email_config['recipient_emails'][0]
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            server.sendmail(email_config['sender_email'], email_config['recipient_emails'], msg.as_string())
            server.quit()
            
            print("   Email sent successfully!")
            
        except Exception as e:
            print(f"   Email failed: {e}")
    else:
        print("   Email not configured")
    
    print()
    print("Test completed!")

if __name__ == "__main__":
    quick_test()