#!/usr/bin/env python3
"""
Enhanced Notification System with Detailed Breakdown and Links
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

def create_enhanced_mock_data():
    """Create mock data with proposal names and details"""
    
    # Mock previous data (smaller set)
    mock_previous = {
        'last_updated': '2025-08-17T10:30:00',
        'proposals': {
            'eips': [
                {'id': 'EIP-7995', 'title': 'Previous EIP 1', 'status': 'Draft'},
                {'id': 'EIP-7996', 'title': 'Previous EIP 2', 'status': 'Final'},
                {'id': 'EIP-7997', 'title': 'Previous EIP 3', 'status': 'Draft'}
            ],
            'tips': [
                {'id': 'TIP-540', 'title': 'Previous TIP 1', 'status': 'Final'},
                {'id': 'TIP-541', 'title': 'Previous TIP 2', 'status': 'Draft'}
            ],
            'bips': [
                {'id': 'BIP-341', 'title': 'Previous BIP 1', 'status': 'Final'},
                {'id': 'BIP-342', 'title': 'Previous BIP 2', 'status': 'Draft'}
            ],
            'beps': [
                {'id': 'BEP-20', 'title': 'Previous BEP 1', 'status': 'Final'},
                {'id': 'BEP-95', 'title': 'Previous BEP 2', 'status': 'Final'}
            ]
        }
    }
    
    # Mock current data (with NEW proposals including names and links)
    mock_current = {
        'eips': [
            # Old ones
            {'id': 'EIP-7995', 'title': 'Previous EIP 1', 'status': 'Draft'},
            {'id': 'EIP-7996', 'title': 'Previous EIP 2', 'status': 'Final'},
            {'id': 'EIP-7997', 'title': 'Previous EIP 3', 'status': 'Draft'},
            # NEW ones
            {'id': 'EIP-7998', 'title': 'Turn randao_reveal into a VRF', 'status': 'Draft', 'link': 'https://eips.ethereum.org/EIPS/eip-7998'},
            {'id': 'EIP-7999', 'title': 'Smart Contract Verification Standard', 'status': 'Draft', 'link': 'https://eips.ethereum.org/EIPS/eip-7999'},
            {'id': 'EIP-8000', 'title': 'Enhanced Gas Fee Optimization', 'status': 'Draft', 'link': 'https://eips.ethereum.org/EIPS/eip-8000'}
        ],
        'tips': [
            # Old ones
            {'id': 'TIP-540', 'title': 'Previous TIP 1', 'status': 'Final'},
            {'id': 'TIP-541', 'title': 'Previous TIP 2', 'status': 'Draft'},
            # NEW ones
            {'id': 'TIP-542', 'title': 'Tron Energy Efficiency Improvement', 'status': 'Draft', 'link': 'https://github.com/tronprotocol/tips/blob/master/tip-542.md'},
            {'id': 'TIP-543', 'title': 'Smart Contract Gas Optimization', 'status': 'Draft', 'link': 'https://github.com/tronprotocol/tips/blob/master/tip-543.md'}
        ],
        'bips': [
            # Old ones
            {'id': 'BIP-341', 'title': 'Previous BIP 1', 'status': 'Final'},
            {'id': 'BIP-342', 'title': 'Previous BIP 2', 'status': 'Draft'},
            # NEW ones
            {'id': 'BIP-343', 'title': 'Bitcoin Script Enhancements', 'status': 'Draft', 'link': 'https://github.com/bitcoin/bips/blob/master/bip-0343.mediawiki'}
        ],
        'beps': [
            # Old ones
            {'id': 'BEP-20', 'title': 'Previous BEP 1', 'status': 'Final'},
            {'id': 'BEP-95', 'title': 'Previous BEP 2', 'status': 'Final'},
            # NEW ones
            {'id': 'BEP-102', 'title': 'BSC Cross-Chain Bridge Improvement', 'status': 'Draft', 'link': 'https://github.com/bnb-chain/BEPs/blob/master/BEP102.md'},
            {'id': 'BEP-103', 'title': 'Enhanced Validator Rewards', 'status': 'Draft', 'link': 'https://github.com/bnb-chain/BEPs/blob/master/BEP103.md'}
        ]
    }
    
    return mock_previous, mock_current

def detect_enhanced_new_proposals(previous_data, current_data):
    """Detect new proposals with full details"""
    new_proposals = {}
    
    for protocol in current_data:
        # Get previous IDs
        previous_items = previous_data['proposals'].get(protocol, [])
        if isinstance(previous_items[0], dict) if previous_items else False:
            previous_ids = {item['id'] for item in previous_items}
        else:
            previous_ids = set(previous_items)
        
        # Get current items  
        current_items = current_data[protocol]
        current_ids = {item['id'] for item in current_items}
        
        # Find new IDs
        new_ids = current_ids - previous_ids
        
        if new_ids:
            # Get full details for new proposals
            new_proposals[protocol] = [
                item for item in current_items 
                if item['id'] in new_ids
            ]
    
    return new_proposals

def create_enhanced_desktop_notification(new_proposals):
    """Create detailed desktop notification with breakdown"""
    if not DESKTOP_NOTIFICATIONS:
        return False
    
    try:
        toaster = ToastNotifier()
        
        # Count by protocol
        counts = {}
        total = 0
        for protocol, proposals in new_proposals.items():
            count = len(proposals)
            counts[protocol] = count
            total += count
        
        # Create detailed message
        protocol_names = {
            'eips': 'EIPs',
            'tips': 'TIPs', 
            'bips': 'BIPs',
            'beps': 'BEPs'
        }
        
        breakdown_parts = []
        for protocol, count in counts.items():
            if count > 0:
                name = protocol_names.get(protocol, protocol.upper())
                breakdown_parts.append(f"{count} {name}")
        
        title = "Blockchain Research Agent"
        if breakdown_parts:
            breakdown_text = ", ".join(breakdown_parts)
            message = f"New proposals: {breakdown_text} (Total: {total})"
        else:
            message = f"New proposals detected: {total} total"
        
        print(f"Enhanced Desktop Notification:")
        print(f"  Title: {title}")
        print(f"  Message: {message}")
        
        # Show the notification
        toaster.show_toast(
            title,
            message,
            icon_path=None,
            duration=15,  # Longer duration for detailed message
            threaded=True
        )
        
        return True
        
    except Exception as e:
        print(f"Desktop notification error: {e}")
        return False

def create_enhanced_email_notification(new_proposals):
    """Create detailed email notification with links and names"""
    
    executor = ScheduleExecutor()
    email_config = executor.load_email_config()
    
    if not email_config or not email_config.get('enabled'):
        print("Email not configured")
        return False
    
    try:
        # Create enhanced email content
        subject = "Blockchain Research Agent - New Proposals Detected"
        
        # Build detailed email body with links
        body_lines = [
            "Hello!",
            "",
            "New blockchain improvement proposals have been detected:",
            ""
        ]
        
        protocol_info = {
            'eips': {
                'name': 'Ethereum Improvement Proposals (EIPs)',
                'base_url': 'https://eips.ethereum.org/EIPS/'
            },
            'tips': {
                'name': 'Tron Improvement Proposals (TIPs)',
                'base_url': 'https://github.com/tronprotocol/tips/blob/master/'
            },
            'bips': {
                'name': 'Bitcoin Improvement Proposals (BIPs)', 
                'base_url': 'https://github.com/bitcoin/bips/blob/master/'
            },
            'beps': {
                'name': 'BNB Chain Evolution Proposals (BEPs)',
                'base_url': 'https://github.com/bnb-chain/BEPs/blob/master/'
            }
        }
        
        total_count = sum(len(proposals) for proposals in new_proposals.values())
        
        for protocol, proposals in new_proposals.items():
            if proposals:
                protocol_info_data = protocol_info.get(protocol, {'name': protocol.upper(), 'base_url': ''})
                protocol_name = protocol_info_data['name']
                
                body_lines.append(f"📋 {protocol_name}:")
                body_lines.append(f"   {len(proposals)} new proposal{'s' if len(proposals) > 1 else ''}:")
                body_lines.append("")
                
                for proposal in proposals:
                    proposal_id = proposal['id']
                    title = proposal.get('title', 'No title available')
                    status = proposal.get('status', 'Unknown')
                    link = proposal.get('link', f"{protocol_info_data['base_url']}{proposal_id.lower()}")
                    
                    body_lines.append(f"   • {proposal_id}: {title}")
                    body_lines.append(f"     Status: {status}")
                    body_lines.append(f"     Link: {link}")
                    body_lines.append("")
        
        body_lines.extend([
            f"Total: {total_count} new proposal{'s' if total_count > 1 else ''} detected",
            "",
            "You can review these proposals in detail by visiting the links above.",
            "The Blockchain Research Agent will continue monitoring for new updates.",
            "",
            "Best regards,",
            "Blockchain Research Agent",
            f"Generated at: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"
        ])
        
        email_body = "\n".join(body_lines)
        
        print(f"Enhanced Email Notification:")
        print(f"  To: {email_config['recipient_emails']}")
        print(f"  Subject: {subject}")
        print(f"  Content: {len(email_body)} characters with links and titles")
        
        # Create and send email
        msg = MIMEMultipart()
        msg['From'] = email_config['sender_email']
        msg['To'] = ', '.join(email_config['recipient_emails'])
        msg['Subject'] = subject
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        print("Sending enhanced email...")
        
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['sender_email'], email_config['sender_password'])
        
        text = msg.as_string()
        server.sendmail(email_config['sender_email'], email_config['recipient_emails'], text)
        server.quit()
        
        print("SUCCESS: Enhanced email sent!")
        
        return True
        
    except Exception as e:
        print(f"Email error: {e}")
        return False

def main():
    print("=== ENHANCED NOTIFICATION SYSTEM TEST ===")
    print(f"Test started at: {datetime.now().strftime('%I:%M:%S %p')}")
    print()
    
    # Create enhanced mock data
    print("Step 1: Creating enhanced mock data with titles and links...")
    previous_data, current_data = create_enhanced_mock_data()
    
    # Detect new proposals
    print("Step 2: Detecting new proposals with details...")
    new_proposals = detect_enhanced_new_proposals(previous_data, current_data)
    
    if new_proposals:
        # Show what was detected
        total_new = sum(len(proposals) for proposals in new_proposals.values())
        print(f"SUCCESS: {total_new} new proposals detected!")
        
        for protocol, proposals in new_proposals.items():
            print(f"  {protocol.upper()}: {len(proposals)} new")
            for proposal in proposals:
                print(f"    - {proposal['id']}: {proposal['title']}")
    else:
        print("No new proposals detected")
        return
    
    # Test enhanced notifications
    print(f"\nStep 3: Testing enhanced notification systems...")
    
    # Enhanced desktop notification
    print("\n--- Enhanced Desktop Notification ---")
    desktop_success = create_enhanced_desktop_notification(new_proposals)
    
    # Enhanced email notification  
    print("\n--- Enhanced Email Notification ---")
    email_success = create_enhanced_email_notification(new_proposals)
    
    # Summary
    print(f"\n=== ENHANCED TEST RESULTS ===")
    print(f"Enhanced desktop notification: {'SUCCESS' if desktop_success else 'FAILED'}")
    print(f"Enhanced email notification: {'SUCCESS' if email_success else 'FAILED'}")
    
    if desktop_success and email_success:
        print(f"\nALL ENHANCED TESTS PASSED!")
        print(f"✓ Desktop shows detailed breakdown: '3 EIPs, 2 TIPs, 1 BIPs, 2 BEPs'")
        print(f"✓ Email includes proposal names and direct links")
    else:
        print(f"\nSome tests failed - check error messages above")

if __name__ == "__main__":
    main()