#!/usr/bin/env python3
"""
Unified Notification System
Supports Desktop, Email, and Slack notifications
"""
import sys
sys.path.insert(0, '.')

import json
import os
import smtplib
import requests
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

class UnifiedNotificationService:
    """Unified service for all notification types"""
    
    def __init__(self):
        self.executor = ScheduleExecutor()
        self.slack_config_file = "data/slack_config.json"
        self.load_slack_config()
    
    def load_slack_config(self):
        """Load Slack configuration"""
        if os.path.exists(self.slack_config_file):
            try:
                with open(self.slack_config_file, 'r') as f:
                    self.slack_config = json.load(f)
            except:
                self.slack_config = {}
        else:
            self.slack_config = {}
    
    def send_all_notifications(self, new_proposals):
        """Send notifications via all configured channels"""
        
        print("=== SENDING UNIFIED NOTIFICATIONS ===")
        print(f"Time: {datetime.now().strftime('%I:%M:%S %p')}")
        
        total_new = sum(len(proposals) for proposals in new_proposals.values())
        print(f"New proposals to notify: {total_new}")
        print()
        
        results = {}
        
        # 1. Desktop notification
        print("1. Desktop Notification:")
        try:
            results['desktop'] = self.send_desktop_notification(new_proposals)
        except Exception as e:
            print(f"   Error: {e}")
            results['desktop'] = False
        
        # 2. Email notification
        print("\n2. Email Notification:")
        try:
            results['email'] = self.send_email_notification(new_proposals)
        except Exception as e:
            print(f"   Error: {e}")
            results['email'] = False
        
        # 3. Slack notification
        print("\n3. Slack Notification:")
        try:
            results['slack'] = self.send_slack_notification(new_proposals)
        except Exception as e:
            print(f"   Error: {e}")
            results['slack'] = False
        
        # Summary
        print(f"\n=== NOTIFICATION RESULTS ===")
        success_count = sum(1 for success in results.values() if success)
        total_channels = len(results)
        
        for channel, success in results.items():
            status = "SUCCESS" if success else "FAILED"
            print(f"  {channel.capitalize()}: {status}")
        
        print(f"\nOverall: {success_count}/{total_channels} channels successful")
        
        return results
    
    def send_desktop_notification(self, new_proposals):
        """Send enhanced desktop notification"""
        
        if not DESKTOP_NOTIFICATIONS:
            print("   Desktop notifications not available")
            return False
        
        try:
            toaster = ToastNotifier()
            
            # Create detailed breakdown
            counts = {}
            total = 0
            for protocol, proposals in new_proposals.items():
                count = len(proposals)
                counts[protocol] = count
                total += count
            
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
            
            print(f"   Title: {title}")
            print(f"   Message: {message}")
            
            toaster.show_toast(title, message, duration=15, threaded=True)
            print("   Status: SUCCESS")
            
            return True
            
        except Exception as e:
            print(f"   Status: FAILED - {e}")
            return False
    
    def send_email_notification(self, new_proposals):
        """Send enhanced email notification"""
        
        email_config = self.executor.load_email_config()
        
        if not email_config or not email_config.get('enabled'):
            print("   Email not configured or disabled")
            return False
        
        try:
            subject = "Blockchain Research Agent - New Proposals Detected"
            
            # Create email body with links
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
                    protocol_data = protocol_info.get(protocol, {'name': protocol.upper(), 'base_url': ''})
                    
                    body_lines.append(f"📋 {protocol_data['name']}:")
                    body_lines.append(f"   {len(proposals)} new proposal{'s' if len(proposals) > 1 else ''}:")
                    body_lines.append("")
                    
                    for proposal in proposals:
                        proposal_id = proposal['id']
                        title = proposal.get('title', 'No title available')
                        status = proposal.get('status', 'Unknown')
                        link = proposal.get('link', f"{protocol_data['base_url']}{proposal_id.lower()}")
                        
                        body_lines.append(f"   • {proposal_id}: {title}")
                        body_lines.append(f"     Status: {status}")
                        body_lines.append(f"     Link: {link}")
                        body_lines.append("")
            
            body_lines.extend([
                f"Total: {total_count} new proposal{'s' if total_count > 1 else ''} detected",
                "",
                "Best regards,",
                "Blockchain Research Agent",
                f"Generated at: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"
            ])
            
            email_body = "\n".join(body_lines)
            
            # Send email
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = ', '.join(email_config['recipient_emails'])
            msg['Subject'] = subject
            msg.attach(MIMEText(email_body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            server.sendmail(email_config['sender_email'], email_config['recipient_emails'], msg.as_string())
            server.quit()
            
            print(f"   To: {email_config['recipient_emails'][0]}")
            print(f"   Subject: {subject}")
            print("   Status: SUCCESS")
            
            return True
            
        except Exception as e:
            print(f"   Status: FAILED - {e}")
            return False
    
    def send_slack_notification(self, new_proposals):
        """Send enhanced Slack notification"""
        
        if not self.slack_config.get("enabled") or not self.slack_config.get("webhook_url"):
            print("   Slack not configured or disabled")
            return False
        
        try:
            # Create rich Slack message
            counts = {}
            total = 0
            for protocol, proposals in new_proposals.items():
                count = len(proposals)
                counts[protocol] = count
                total += count
            
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
            
            header_text = f"🚨 *New Blockchain Proposals Detected!*\n"
            header_text += f"📊 Summary: {', '.join(breakdown_parts)} (Total: {total})\n"
            
            # Create blocks for rich formatting
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": header_text
                    }
                },
                {"type": "divider"}
            ]
            
            # Add proposal details
            protocol_info = {
                'eips': {'name': '🔷 Ethereum Improvement Proposals (EIPs)', 'emoji': '⚡'},
                'tips': {'name': '🔶 Tron Improvement Proposals (TIPs)', 'emoji': '🚀'},
                'bips': {'name': '🟡 Bitcoin Improvement Proposals (BIPs)', 'emoji': '₿'},
                'beps': {'name': '🟨 BNB Chain Evolution Proposals (BEPs)', 'emoji': '🌟'}
            }
            
            for protocol, proposals in new_proposals.items():
                if proposals:
                    protocol_data = protocol_info.get(protocol, {'name': protocol.upper(), 'emoji': '📋'})
                    
                    protocol_text = f"*{protocol_data['name']}*\n"
                    protocol_text += f"_{len(proposals)} new proposal{'s' if len(proposals) > 1 else ''}_\n\n"
                    
                    for proposal in proposals[:3]:  # Limit to avoid message length issues
                        proposal_id = proposal['id']
                        title = proposal.get('title', 'No title available')
                        status = proposal.get('status', 'Unknown')
                        link = proposal.get('link', '#')
                        
                        protocol_text += f"{protocol_data['emoji']} *<{link}|{proposal_id}>*: {title}\n"
                        protocol_text += f"   _Status: {status}_\n"
                    
                    if len(proposals) > 3:
                        protocol_text += f"   _... and {len(proposals) - 3} more_\n"
                    
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": protocol_text
                        }
                    })
            
            # Footer
            footer_text = f"🤖 Generated by Blockchain Research Agent at {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"
            blocks.append({
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": footer_text}]
            })
            
            # Send to Slack
            message = {
                "username": self.slack_config.get("username", "Blockchain Research Agent"),
                "icon_emoji": self.slack_config.get("icon_emoji", ":robot_face:"),
                "blocks": blocks
            }
            
            response = requests.post(
                self.slack_config['webhook_url'],
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   Channel: {self.slack_config.get('channel', 'Default')}")
                print("   Status: SUCCESS")
                return True
            else:
                print(f"   Status: FAILED - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   Status: FAILED - {e}")
            return False

def test_unified_notifications():
    """Test all notification channels with mock data"""
    
    print("=== UNIFIED NOTIFICATION SYSTEM TEST ===")
    print(f"Started at: {datetime.now().strftime('%I:%M:%S %p')}")
    print()
    
    # Create mock data
    mock_new_proposals = {
        'eips': [
            {'id': 'EIP-7998', 'title': 'Turn randao_reveal into a VRF', 'status': 'Draft', 'link': 'https://eips.ethereum.org/EIPS/eip-7998'},
            {'id': 'EIP-7999', 'title': 'Smart Contract Verification Standard', 'status': 'Draft', 'link': 'https://eips.ethereum.org/EIPS/eip-7999'}
        ],
        'tips': [
            {'id': 'TIP-542', 'title': 'Tron Energy Efficiency Improvement', 'status': 'Draft', 'link': 'https://github.com/tronprotocol/tips/blob/master/tip-542.md'}
        ],
        'bips': [
            {'id': 'BIP-343', 'title': 'Bitcoin Script Enhancements', 'status': 'Draft', 'link': 'https://github.com/bitcoin/bips/blob/master/bip-0343.mediawiki'}
        ]
    }
    
    # Initialize service
    notification_service = UnifiedNotificationService()
    
    # Send all notifications
    results = notification_service.send_all_notifications(mock_new_proposals)
    
    # Final summary
    print(f"\n=== FINAL TEST RESULTS ===")
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"🎉 ALL NOTIFICATIONS SUCCESSFUL! ({success_count}/{total_count})")
        print("✓ Desktop: Rich breakdown notification")
        print("✓ Email: Detailed proposals with links")  
        print("✓ Slack: Rich formatted channel message")
    else:
        print(f"⚠️ PARTIAL SUCCESS: {success_count}/{total_count} channels")
        print("Check individual channel results above")
    
    return results

if __name__ == "__main__":
    test_unified_notifications()