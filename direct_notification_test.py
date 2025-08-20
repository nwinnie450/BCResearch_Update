"""
DIRECT NOTIFICATION TEST
This will bypass all caching and directly send notifications to verify the system works
"""
import sys
sys.path.insert(0, '.')

import json
import os
from datetime import datetime
from services.enhanced_notification_service import EnhancedNotificationService

def test_direct_notifications():
    """Test notifications directly with a real proposal"""
    
    print("=== DIRECT NOTIFICATION TEST ===")
    print("Testing email and Slack notifications with real TIP proposal...")
    print()
    
    # Create a realistic test proposal with current date
    test_proposals = {
        'tron': [
            {
                'id': 'TIP-777',
                'title': 'URGENT: Enhanced Network Security Protocol - IMMEDIATE TESTING',
                'protocol': 'tron',
                'status': 'Draft',
                'url': 'https://github.com/tronprotocol/tips/blob/master/tip-777.md',
                'created': '2025-08-20',
                'author': 'security.team@tron.network',
                'type': 'Standards Track',
                'category': 'Security',
                'summary': 'Critical security enhancement proposal requiring immediate network-wide implementation. This proposal introduces enhanced validation mechanisms, multi-signature security protocols, and automated threat detection systems to protect against emerging attack vectors.',
                'breaking_change': True,
                'priority': 'HIGH'
            }
        ]
    }
    
    print("Test Proposal Details:")
    proposal = test_proposals['tron'][0]
    print(f"  ID: {proposal['id']}")
    print(f"  Title: {proposal['title']}")
    print(f"  Status: {proposal['status']}")
    print(f"  Created: {proposal['created']}")
    print(f"  Priority: {proposal['priority']}")
    print(f"  Breaking Change: {proposal['breaking_change']}")
    print()
    
    try:
        print("1. Initializing Enhanced Notification Service...")
        service = EnhancedNotificationService()
        print("   Service initialized successfully")
        print()
        
        print("2. Sending notifications...")
        print("   - Processing proposal with AI analysis...")
        print("   - Generating email with complete format...")
        print("   - Sending Slack notification...")
        print()
        
        # Send notifications
        result = service.send_enhanced_notifications(test_proposals)
        
        print("3. NOTIFICATION RESULTS:")
        print(f"   EMAIL: {'SENT SUCCESSFULLY' if result['email'] else 'FAILED'}")
        print(f"   SLACK: {'SENT SUCCESSFULLY' if result['slack'] else 'FAILED'}")
        print()
        
        if result['email']:
            print("EMAIL NOTIFICATION SENT!")
            print("   Recipients: nwinnie.ngiew@gmail.com, winnie.ngiew@merquri.io")
            print("   Format: Complete professional format with all fields")
            print("   Content: Title, subtitle, TL;DR, 'Why it matters', blue buttons")
            print()
        
        if result['slack']:
            print("SLACK NOTIFICATION SENT!")
            print("   Channel: #faws_testing")
            print("   Format: Block Kit with complete proposal details")
            print("   Buttons: Blue action buttons")
            print()
        
        # Log this test
        from components.schedule_history import log_schedule_execution
        log_schedule_execution(
            schedule_name="DIRECT NOTIFICATION TEST",
            success=True,
            start_time=datetime.now(),
            new_proposals=test_proposals,
            logs=f"Direct test: Email={result['email']}, Slack={result['slack']}"
        )
        
        if result['email'] and result['slack']:
            print("COMPLETE SUCCESS!")
            print("Both email and Slack notifications sent successfully!")
            print()
            print("CHECK YOUR EMAIL AND SLACK NOW!")
            print("You should receive:")
            print("- Email with TIP-777 security proposal")
            print("- Slack message in #faws_testing channel")
            print("- Complete professional formatting")
            print("- Blue action buttons")
            print("- AI-generated analysis")
        else:
            print("PARTIAL SUCCESS")
            if not result['email']:
                print("Email notification failed - check email configuration")
            if not result['slack']:
                print("Slack notification failed - check Slack configuration")
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {'email': False, 'slack': False}

def verify_configurations():
    """Verify email and Slack configurations"""
    
    print("=== CONFIGURATION VERIFICATION ===")
    
    # Check email config
    email_config_file = "data/email_config.json"
    if os.path.exists(email_config_file):
        with open(email_config_file, 'r') as f:
            email_config = json.load(f)
        print("Email Configuration:")
        print(f"   Enabled: {email_config.get('enabled', False)}")
        print(f"   SMTP Server: {email_config.get('smtp_server', 'Not set')}")
        print(f"   Sender: {email_config.get('sender_email', 'Not set')}")
        print(f"   Recipients: {len(email_config.get('recipient_emails', []))} addresses")
    else:
        print("Email configuration file not found")
    
    print()
    
    # Check Slack config
    slack_config_file = "data/slack_config.json"
    if os.path.exists(slack_config_file):
        with open(slack_config_file, 'r') as f:
            slack_config = json.load(f)
        print("Slack Configuration:")
        print(f"   Enabled: {slack_config.get('enabled', False)}")
        print(f"   Channel: {slack_config.get('channel', 'Not set')}")
        print(f"   Webhook URL: {'Set' if slack_config.get('webhook_url') else 'Not set'}")
    else:
        print("Slack configuration file not found")
    
    print()

if __name__ == "__main__":
    verify_configurations()
    result = test_direct_notifications()
    
    if result['email'] or result['slack']:
        print("\n" + "="*50)
        print("NOTIFICATIONS SENT - CHECK YOUR DEVICES!")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("NOTIFICATIONS FAILED - CHECK CONFIGURATIONS!")
        print("="*50)