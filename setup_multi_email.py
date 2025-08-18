#!/usr/bin/env python3
"""
Setup Multiple Email Recipients
Tool to configure multiple email recipients for notifications
"""
import json
import os

def setup_multi_email():
    """Setup multiple email recipients"""
    
    print("=== MULTI-EMAIL RECIPIENT SETUP ===\n")
    
    email_config_file = "data/email_config.json"
    
    # Load existing config
    if os.path.exists(email_config_file):
        with open(email_config_file, 'r') as f:
            config = json.load(f)
        print("Current email configuration loaded.")
    else:
        print("No existing email config found. Please run email setup first.")
        return
    
    print(f"\nCurrent recipients:")
    for i, email in enumerate(config.get('recipient_emails', []), 1):
        print(f"  {i}. {email}")
    
    print(f"\nOptions:")
    print(f"1. Add new recipient email")
    print(f"2. Remove recipient email")
    print(f"3. Replace all recipients")
    print(f"4. Show current configuration")
    print(f"5. Test email sending")
    
    choice = input(f"\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        # Add new email
        new_email = input("Enter new recipient email: ").strip()
        if new_email and '@' in new_email:
            if 'recipient_emails' not in config:
                config['recipient_emails'] = []
            config['recipient_emails'].append(new_email)
            print(f"Added: {new_email}")
        else:
            print("Invalid email address")
            return
    
    elif choice == "2":
        # Remove email
        current_emails = config.get('recipient_emails', [])
        if not current_emails:
            print("No recipients to remove")
            return
        
        print("Select email to remove:")
        for i, email in enumerate(current_emails, 1):
            print(f"  {i}. {email}")
        
        try:
            index = int(input("Enter number: ")) - 1
            if 0 <= index < len(current_emails):
                removed = current_emails.pop(index)
                print(f"Removed: {removed}")
            else:
                print("Invalid selection")
                return
        except ValueError:
            print("Invalid input")
            return
    
    elif choice == "3":
        # Replace all
        print("Enter new recipient emails (comma-separated):")
        emails_input = input("Emails: ").strip()
        
        if emails_input:
            new_emails = [email.strip() for email in emails_input.split(',')]
            # Validate emails
            valid_emails = [email for email in new_emails if email and '@' in email]
            
            if valid_emails:
                config['recipient_emails'] = valid_emails
                print(f"Updated recipients:")
                for email in valid_emails:
                    print(f"  • {email}")
            else:
                print("No valid emails provided")
                return
        else:
            print("No emails provided")
            return
    
    elif choice == "4":
        # Show config
        print(f"\nCurrent Email Configuration:")
        print(f"  Enabled: {config.get('enabled', False)}")
        print(f"  SMTP Server: {config.get('smtp_server', 'Not set')}")
        print(f"  SMTP Port: {config.get('smtp_port', 'Not set')}")
        print(f"  Sender: {config.get('sender_email', 'Not set')}")
        print(f"  Recipients: {len(config.get('recipient_emails', []))}")
        for email in config.get('recipient_emails', []):
            print(f"    • {email}")
        return
    
    elif choice == "5":
        # Test email
        print(f"\nTesting email to {len(config.get('recipient_emails', []))} recipients...")
        
        try:
            import sys
            sys.path.insert(0, '.')
            from services.unified_notification_service import UnifiedNotificationService
            
            # Create test data
            test_proposals = {
                'eips': [{
                    'id': 'TEST-EMAIL',
                    'title': 'Multi-Recipient Email Test',
                    'description': 'Testing email delivery to multiple recipients.',
                    'status': 'Test',
                    'link': 'https://example.com/test'
                }],
                'bips': [], 'tips': [], 'beps': []
            }
            
            service = UnifiedNotificationService()
            results = service.send_unified_notifications(test_proposals)
            
            if results.get('email'):
                print(f"✓ Test email sent successfully to all {len(config['recipient_emails'])} recipients!")
            else:
                print(f"✗ Test email failed")
        except Exception as e:
            print(f"✗ Test failed: {e}")
        return
    
    else:
        print("Invalid choice")
        return
    
    # Save updated config
    with open(email_config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✓ Email configuration updated!")
    print(f"✓ Total recipients: {len(config['recipient_emails'])}")
    print(f"\nFinal recipient list:")
    for i, email in enumerate(config['recipient_emails'], 1):
        print(f"  {i}. {email}")

if __name__ == "__main__":
    setup_multi_email()