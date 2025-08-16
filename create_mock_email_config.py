#!/usr/bin/env python3
"""
Create Mock Email Configuration for Testing
"""
import json
import os

def create_mock_email_config():
    """Create a mock email configuration for testing"""
    
    mock_email_config = {
        "enabled": False,  # Disabled by default for safety
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your-email@gmail.com",
        "sender_password": "your-app-password",
        "recipient_emails": [
            "recipient1@example.com",
            "recipient2@example.com"
        ]
    }
    
    # Save mock email configuration
    os.makedirs("data", exist_ok=True)
    with open("data/email_config.json", 'w') as f:
        json.dump(mock_email_config, f, indent=2)
    
    print("Created mock email configuration")
    print("   SMTP Server: smtp.gmail.com")
    print("   Port: 587")
    print("   Sender: your-email@gmail.com")
    print("   Recipients: 2 mock emails")
    print("   Status: DISABLED (for safety)")
    print("")
    print("To use email notifications:")
    print("   1. Go to Schedule page")
    print("   2. Open 'Email Settings' section")
    print("   3. Enable email notifications")
    print("   4. Enter your real email credentials")
    print("   5. Click 'Test Email' to verify")
    
    return mock_email_config

if __name__ == "__main__":
    create_mock_email_config()