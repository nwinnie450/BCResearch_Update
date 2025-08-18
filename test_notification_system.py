#!/usr/bin/env python3
"""
Mock Data Notification Test System
Test email and desktop notifications with simulated new proposals
"""
import sys
sys.path.insert(0, '.')

import json
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from services.schedule_executor import ScheduleExecutor

# Windows notification
try:
    from win10toast import ToastNotifier
    DESKTOP_NOTIFICATIONS = True
except ImportError:
    DESKTOP_NOTIFICATIONS = False

def create_mock_previous_data():
    """Create mock previous proposal data (smaller set)"""
    mock_previous = {
        'last_updated': '2025-08-17T10:30:00',
        'proposals': {
            'eips': [
                'EIP-7995', 'EIP-7996', 'EIP-7997'  # Only 3 old EIPs
            ],
            'tips': [
                'TIP-540', 'TIP-541'  # Only 2 old TIPs
            ],
            'bips': [
                'BIP-341', 'BIP-342'  # Only 2 old BIPs
            ],
            'beps': [
                'BEP-20', 'BEP-95'  # Only 2 old BEPs
            ]
        }
    }
    
    # Save mock previous data
    with open('data/last_proposal_check.json', 'w', encoding='utf-8') as f:
        json.dump(mock_previous, f, indent=2)
    
    print("Created mock previous proposal data")
    return mock_previous

def create_mock_current_data():
    """Create mock current proposal data (with new proposals)"""
    mock_current = {
        'eips': [
            'EIP-7995', 'EIP-7996', 'EIP-7997',  # Old ones
            'EIP-7998', 'EIP-7999', 'EIP-8000'   # NEW ones
        ],
        'tips': [
            'TIP-540', 'TIP-541',  # Old ones
            'TIP-542', 'TIP-543'   # NEW ones
        ],
        'bips': [
            'BIP-341', 'BIP-342',  # Old ones
            'BIP-343'              # NEW one
        ],
        'beps': [
            'BEP-20', 'BEP-95',    # Old ones
            'BEP-102', 'BEP-103'   # NEW ones
        ]
    }
    
    print("Created mock current proposal data")
    return mock_current

def detect_new_proposals(previous_data, current_data):
    """Detect new proposals by comparing current vs previous"""
    new_proposals = {}
    
    for protocol in current_data:
        previous_set = set(previous_data['proposals'].get(protocol, []))
        current_set = set(current_data[protocol])
        new_items = current_set - previous_set
        
        if new_items:
            new_proposals[protocol] = list(new_items)
    
    return new_proposals

def test_desktop_notification(new_proposals):
    """Test desktop notification"""
    print("\n=== TESTING DESKTOP NOTIFICATION ===")
    
    if not DESKTOP_NOTIFICATIONS:
        print("ERROR: win10toast not available for desktop notifications")
        return False
    
    try:
        toaster = ToastNotifier()
        
        # Create notification message
        total_new = sum(len(proposals) for proposals in new_proposals.values())
        title = "Blockchain Research Agent"
        message = f"New proposals detected: {total_new} total"
        
        print(f"Sending desktop notification...")
        print(f"  Title: {title}")
        print(f"  Message: {message}")
        
        # Show the notification
        toaster.show_toast(
            title,
            message,
            icon_path=None,
            duration=10,
            threaded=True
        )
        
        print("SUCCESS: Desktop notification sent!")
        return True
        
    except Exception as e:
        print(f"ERROR: Desktop notification failed: {e}")
        return False

def test_email_notification(new_proposals):
    """Test email notification"""
    print("\n=== TESTING EMAIL NOTIFICATION ===")
    
    executor = ScheduleExecutor()
    email_config = executor.load_email_config()
    
    if not email_config or not email_config.get('enabled'):
        print("ERROR: Email not configured or not enabled")
        return False
    
    # Check required fields
    required_fields = ['sender_email', 'sender_password', 'recipient_emails']
    for field in required_fields:
        if field not in email_config or not email_config[field]:
            print(f"ERROR: Missing email config field: {field}")
            return False
    
    try:
        # Create email content
        subject = "Blockchain Research Agent - New Proposals Detected"
        
        # Build email body
        body_lines = [
            "Hello!",
            "",
            "New blockchain improvement proposals have been detected:",
            ""
        ]
        
        protocol_names = {
            'eips': 'Ethereum (EIP)',
            'tips': 'Tron (TIP)',
            'bips': 'Bitcoin (BIP)', 
            'beps': 'BNB Chain (BEP)'
        }
        
        for protocol, proposals in new_proposals.items():
            protocol_name = protocol_names.get(protocol, protocol.upper())
            body_lines.append(f"{protocol_name}:")
            for proposal in proposals:
                body_lines.append(f"  • {proposal}")
            body_lines.append("")
        
        body_lines.extend([
            "Check the Blockchain Research Agent for detailed analysis.",
            "",
            "This is a test notification to verify the email system is working.",
            "",
            "Best regards,",
            "Blockchain Research Agent",
            f"Generated at: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"
        ])
        
        email_body = "\n".join(body_lines)
        
        print(f"Email configuration:")
        print(f"  SMTP Server: {email_config['smtp_server']}:{email_config['smtp_port']}")
        print(f"  From: {email_config['sender_email']}")
        print(f"  To: {email_config['recipient_emails']}")
        print(f"  Subject: {subject}")
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = email_config['sender_email']
        msg['To'] = ', '.join(email_config['recipient_emails'])
        msg['Subject'] = subject
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        print(f"\nSending email...")
        
        # Connect and send
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['sender_email'], email_config['sender_password'])
        
        text = msg.as_string()
        server.sendmail(email_config['sender_email'], email_config['recipient_emails'], text)
        server.quit()
        
        print("SUCCESS: Email sent successfully!")
        print("Check your inbox for the test notification email.")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Email sending failed: {e}")
        return False

def main():
    print("=== MOCK DATA NOTIFICATION TEST SYSTEM ===")
    print(f"Test started at: {datetime.now().strftime('%I:%M:%S %p')}")
    print()
    
    # Step 1: Create mock data
    print("Step 1: Creating mock data...")
    previous_data = create_mock_previous_data()
    current_data = create_mock_current_data()
    
    # Step 2: Detect new proposals
    print("\nStep 2: Detecting new proposals...")
    new_proposals = detect_new_proposals(previous_data, current_data)
    
    if new_proposals:
        total_new = sum(len(proposals) for proposals in new_proposals.values())
        print(f"SUCCESS: {total_new} new proposals detected!")
        
        for protocol, proposals in new_proposals.items():
            print(f"  {protocol.upper()}: {proposals}")
    else:
        print("No new proposals detected")
        return
    
    # Step 3: Test notifications
    print(f"\nStep 3: Testing notification systems...")
    
    # Test desktop notification
    desktop_success = test_desktop_notification(new_proposals)
    
    # Test email notification
    email_success = test_email_notification(new_proposals)
    
    # Summary
    print(f"\n=== TEST RESULTS SUMMARY ===")
    print(f"Mock data creation: SUCCESS")
    print(f"New proposal detection: SUCCESS ({total_new} new proposals)")
    print(f"Desktop notification: {'SUCCESS' if desktop_success else 'FAILED'}")
    print(f"Email notification: {'SUCCESS' if email_success else 'FAILED'}")
    
    if desktop_success and email_success:
        print(f"\nALL TESTS PASSED! Your notification system is working perfectly.")
    else:
        print(f"\nSome tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()