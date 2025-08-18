#!/usr/bin/env python3
"""
Slack Notification System for Blockchain Research Agent
Sends rich formatted notifications to Slack channels via webhooks
"""
import sys
sys.path.insert(0, '.')

import json
import os
import requests
from datetime import datetime
from services.schedule_executor import ScheduleExecutor

class SlackNotificationService:
    """Service for sending notifications to Slack"""
    
    def __init__(self):
        self.config_file = "data/slack_config.json"
        self.load_config()
    
    def load_config(self):
        """Load Slack configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = {}
        else:
            self.config = {}
    
    def save_config(self, config):
        """Save Slack configuration"""
        os.makedirs("data", exist_ok=True)
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.config = config
            return True
        except Exception as e:
            print(f"Error saving Slack config: {e}")
            return False
    
    def setup_slack_webhook(self):
        """Interactive setup for Slack webhook"""
        print("=== SLACK WEBHOOK SETUP ===")
        print("To set up Slack notifications, you need to create a webhook URL.")
        print()
        print("Steps to get Slack Webhook URL:")
        print("1. Go to https://api.slack.com/messaging/webhooks")
        print("2. Click 'Create a Slack app' -> 'From scratch'")
        print("3. Choose app name (e.g., 'Blockchain Research Agent') and workspace")
        print("4. Go to 'Incoming Webhooks' -> Enable webhooks")
        print("5. Click 'Add New Webhook to Workspace'")
        print("6. Choose the channel to send notifications to")
        print("7. Copy the webhook URL (starts with https://hooks.slack.com/...)")
        print()
        
        webhook_url = input("Enter your Slack webhook URL: ").strip()
        channel_name = input("Enter channel name (e.g., #blockchain-alerts): ").strip()
        
        if not webhook_url.startswith('https://hooks.slack.com/'):
            print("WARNING: URL doesn't look like a Slack webhook URL")
            confirm = input("Continue anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                return False
        
        config = {
            "enabled": True,
            "webhook_url": webhook_url,
            "channel": channel_name,
            "username": "Blockchain Research Agent",
            "icon_emoji": ":robot_face:",
            "setup_date": datetime.now().isoformat()
        }
        
        if self.save_config(config):
            print("✓ Slack configuration saved successfully!")
            return True
        else:
            print("✗ Failed to save Slack configuration")
            return False
    
    def create_slack_message(self, new_proposals):
        """Create rich Slack message with proposal details"""
        
        # Count proposals by type
        counts = {}
        total = 0
        for protocol, proposals in new_proposals.items():
            count = len(proposals)
            counts[protocol] = count
            total += count
        
        # Create main message
        protocol_names = {
            'eips': 'EIPs',
            'tips': 'TIPs', 
            'bips': 'BIPs',
            'beps': 'BEPs'
        }
        
        # Header with summary
        breakdown_parts = []
        for protocol, count in counts.items():
            if count > 0:
                name = protocol_names.get(protocol, protocol.upper())
                breakdown_parts.append(f"{count} {name}")
        
        header_text = f"🚨 *New Blockchain Proposals Detected!*\n"
        header_text += f"📊 Summary: {', '.join(breakdown_parts)} (Total: {total})\n"
        
        # Create detailed blocks for Slack's block kit format
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": header_text
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add sections for each protocol with proposals
        protocol_info = {
            'eips': {
                'name': '🔷 Ethereum Improvement Proposals (EIPs)',
                'emoji': '⚡',
                'base_url': 'https://eips.ethereum.org/EIPS/'
            },
            'tips': {
                'name': '🔶 Tron Improvement Proposals (TIPs)',
                'emoji': '🚀',
                'base_url': 'https://github.com/tronprotocol/tips/blob/master/'
            },
            'bips': {
                'name': '🟡 Bitcoin Improvement Proposals (BIPs)', 
                'emoji': '₿',
                'base_url': 'https://github.com/bitcoin/bips/blob/master/'
            },
            'beps': {
                'name': '🟨 BNB Chain Evolution Proposals (BEPs)',
                'emoji': '🌟',
                'base_url': 'https://github.com/bnb-chain/BEPs/blob/master/'
            }
        }
        
        for protocol, proposals in new_proposals.items():
            if proposals:
                protocol_data = protocol_info.get(protocol, {
                    'name': protocol.upper(), 
                    'emoji': '📋',
                    'base_url': ''
                })
                
                # Protocol header
                protocol_text = f"*{protocol_data['name']}*\n"
                protocol_text += f"_{len(proposals)} new proposal{'s' if len(proposals) > 1 else ''}_\n\n"
                
                # Add each proposal
                for proposal in proposals[:5]:  # Limit to 5 to avoid message length issues
                    proposal_id = proposal['id']
                    title = proposal.get('title', 'No title available')
                    status = proposal.get('status', 'Unknown')
                    link = proposal.get('link', f"{protocol_data['base_url']}{proposal_id.lower()}")
                    
                    protocol_text += f"{protocol_data['emoji']} *<{link}|{proposal_id}>*: {title}\n"
                    protocol_text += f"   _Status: {status}_\n"
                
                if len(proposals) > 5:
                    protocol_text += f"   _... and {len(proposals) - 5} more_\n"
                
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
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": footer_text
                }
            ]
        })
        
        # Create final message payload
        message = {
            "username": self.config.get("username", "Blockchain Research Agent"),
            "icon_emoji": self.config.get("icon_emoji", ":robot_face:"),
            "blocks": blocks
        }
        
        return message
    
    def send_slack_notification(self, new_proposals):
        """Send notification to Slack"""
        
        if not self.config.get("enabled") or not self.config.get("webhook_url"):
            print("Slack notifications not configured or disabled")
            return False
        
        try:
            # Create message
            message = self.create_slack_message(new_proposals)
            
            print(f"Sending Slack notification...")
            print(f"  Channel: {self.config.get('channel', 'Default')}")
            print(f"  Webhook: {self.config['webhook_url'][:50]}...")
            
            # Send to Slack
            response = requests.post(
                self.config['webhook_url'],
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✓ Slack notification sent successfully!")
                return True
            else:
                print(f"✗ Slack API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Slack notification failed: {e}")
            return False

def test_slack_notification():
    """Test Slack notification with mock data"""
    print("=== SLACK NOTIFICATION TEST ===")
    print(f"Test started at: {datetime.now().strftime('%I:%M:%S %p')}")
    print()
    
    slack_service = SlackNotificationService()
    
    # Check if Slack is configured
    if not slack_service.config.get("webhook_url"):
        print("Slack not configured. Starting setup...")
        if not slack_service.setup_slack_webhook():
            print("Slack setup failed or cancelled")
            return False
    
    # Create mock new proposals data
    mock_new_proposals = {
        'eips': [
            {
                'id': 'EIP-7998', 
                'title': 'Turn randao_reveal into a VRF', 
                'status': 'Draft',
                'link': 'https://eips.ethereum.org/EIPS/eip-7998'
            },
            {
                'id': 'EIP-7999', 
                'title': 'Smart Contract Verification Standard', 
                'status': 'Draft',
                'link': 'https://eips.ethereum.org/EIPS/eip-7999'
            }
        ],
        'tips': [
            {
                'id': 'TIP-542', 
                'title': 'Tron Energy Efficiency Improvement', 
                'status': 'Draft',
                'link': 'https://github.com/tronprotocol/tips/blob/master/tip-542.md'
            }
        ],
        'bips': [
            {
                'id': 'BIP-343', 
                'title': 'Bitcoin Script Enhancements', 
                'status': 'Draft',
                'link': 'https://github.com/bitcoin/bips/blob/master/bip-0343.mediawiki'
            }
        ]
    }
    
    print("Mock data created:")
    total = sum(len(proposals) for proposals in mock_new_proposals.values())
    print(f"  Total new proposals: {total}")
    for protocol, proposals in mock_new_proposals.items():
        print(f"  {protocol.upper()}: {len(proposals)} proposals")
    
    print()
    
    # Send test notification
    success = slack_service.send_slack_notification(mock_new_proposals)
    
    print()
    print("=== TEST RESULTS ===")
    print(f"Slack notification: {'SUCCESS' if success else 'FAILED'}")
    
    if success:
        print("✓ Check your Slack channel for the notification!")
        print(f"✓ Rich formatting with proposal links")
        print(f"✓ Organized by protocol type")
        print(f"✓ Emoji indicators for easy reading")
    
    return success

if __name__ == "__main__":
    test_slack_notification()