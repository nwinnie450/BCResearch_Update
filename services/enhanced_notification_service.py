"""
Enhanced Notification Service with Impact Analysis
Sends rich notifications with development and product impact insights
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
from typing import Dict, List

# OpenAI import
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from services.proposal_impact_analyzer import ProposalImpactAnalyzer
from services.ai_impact_analyzer import AITransactionImpactAnalyzer

class EnhancedNotificationService:
    """Enhanced notification service with impact analysis"""
    
    def __init__(self):
        self.impact_analyzer = ProposalImpactAnalyzer()
        self.ai_analyzer = AITransactionImpactAnalyzer()
        self.email_config_file = "data/email_config.json"
        self.slack_config_file = "data/slack_config.json"
    
    def load_email_config(self):
        """Load email configuration"""
        if os.path.exists(self.email_config_file):
            try:
                with open(self.email_config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def load_slack_config(self):
        """Load Slack configuration"""
        if os.path.exists(self.slack_config_file):
            try:
                with open(self.slack_config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def send_enhanced_notifications(self, new_proposals: Dict[str, List[Dict]]):
        """Send enhanced notifications with impact analysis"""
        
        print(f"=== ENHANCED NOTIFICATION SERVICE ===")
        print(f"Analyzing {sum(len(props) for props in new_proposals.values())} new proposals...")
        
        # Flatten proposals for analysis
        all_proposals = []
        for protocol, proposals in new_proposals.items():
            for proposal in proposals:
                proposal['protocol'] = protocol
                all_proposals.append(proposal)
        
        # Analyze impact
        impact_analysis = self.impact_analyzer.analyze_multiple_proposals(all_proposals)
        
        print(f"Basic analysis complete:")
        print(f"  High priority: {impact_analysis['priority_breakdown']['high']}")
        print(f"  Medium priority: {impact_analysis['priority_breakdown']['medium']}")
        print(f"  Low priority: {impact_analysis['priority_breakdown']['low']}")
        
        # Enhance with AI analysis
        print(f"Generating AI-enhanced transaction impact analysis...")
        ai_enhanced = self.ai_analyzer.enhance_multiple_proposals(impact_analysis['analyses'])
        
        # Merge AI insights into impact analysis
        impact_analysis['ai_enhanced_analyses'] = ai_enhanced['enhanced_analyses']
        impact_analysis['cross_proposal_insights'] = ai_enhanced['cross_proposal_insights']
        impact_analysis['ai_statistics'] = ai_enhanced['summary_statistics']
        
        # Send notifications
        results = {'email': True, 'slack': True}
        
        # Send ONE grouped email with all proposals
        print(f"\nSending grouped email notification...")
        email_result = self.send_grouped_email_notification(all_proposals, impact_analysis)
        if not email_result:
            results['email'] = False
        
        # Send individual Slack notifications
        print(f"Sending individual Slack notifications...")
        
        for i, proposal in enumerate(all_proposals):
            print(f"Sending Slack notification {i+1}/{len(all_proposals)}: {proposal.get('id', 'Unknown')}")
            
            # Find the analysis for this proposal
            proposal_analysis = None
            for analysis in impact_analysis['analyses']:
                # Handle different data structures
                analysis_id = None
                if 'proposal' in analysis and 'id' in analysis['proposal']:
                    analysis_id = analysis['proposal']['id']
                elif 'id' in analysis:
                    analysis_id = analysis['id']
                elif 'proposal_id' in analysis:
                    analysis_id = analysis['proposal_id']
                
                if analysis_id == proposal['id']:
                    proposal_analysis = analysis
                    break
            
            # Find AI enhancement for this proposal
            ai_analysis = None
            if proposal_analysis:
                for ai_enhanced_analysis in impact_analysis['ai_enhanced_analyses']:
                    if ai_enhanced_analysis['proposal_id'] == proposal['id']:
                        ai_analysis = ai_enhanced_analysis
                        break
            
            # Send individual Slack notification
            slack_result = self.send_individual_slack_notification(proposal, proposal_analysis, ai_analysis)
            if not slack_result:
                results['slack'] = False
                
        print(f"Notifications sent: 1 grouped email + {len(all_proposals)} individual Slack messages")
        
        return results
    
    def send_individual_slack_notification(self, proposal: Dict, proposal_analysis: Dict, ai_analysis: Dict) -> bool:
        """Send individual Slack notification for a single proposal"""
        
        slack_config = self.load_slack_config()
        if not slack_config or not slack_config.get('enabled'):
            return False
        
        try:
            protocol = proposal.get('protocol', 'unknown').upper()
            protocol_emoji = {
                'TRON': ':diamond_shape_with_a_dot_inside:',
                'BITCOIN': ':diamond_shape_with_a_dot_inside:',
                'BINANCE_SMART_CHAIN': ':diamond_shape_with_a_dot_inside:',
                'ETHEREUM': ':diamond_shape_with_a_dot_inside:'
            }.get(protocol, ':diamond_shape_with_a_dot_inside:')
            
            # Get AI analysis details (matching email format)
            breaking_change = False
            impact_summary = "Protocol enhancement with governance implications"
            user_impact = "Users may experience changes in transaction processing times and fees."
            required_actions = ["upgrade nodes", "test compatibility"]
            impact_type = "governance"
            why_matters = ["introduces new instructions", "affects consensus rules"]
            
            if ai_analysis:
                impact_summary = ai_analysis.get('impact_summary', impact_summary)
                user_impact = ai_analysis.get('user_impact', user_impact)
                required_actions = ai_analysis.get('required_actions', required_actions)
                breaking_change = ai_analysis.get('breaking_change', False)
                impact_type = ai_analysis.get('impact_category', impact_type)
                why_matters = ai_analysis.get('why_matters', why_matters)
            elif proposal_analysis:
                try:
                    ai_summary = self._generate_detailed_ai_summary(proposal)
                    if ai_summary:
                        impact_summary = ai_summary.get('impact_summary', impact_summary)
                        user_impact = ai_summary.get('user_impact', user_impact)
                        required_actions = ai_summary.get('required_actions', required_actions)
                        breaking_change = ai_summary.get('breaking_change', False)
                        impact_type = ai_summary.get('impact_category', impact_type)
                        why_matters = ai_summary.get('why_matters', why_matters)
                except Exception as e:
                    print(f"  AI summary generation failed: {e}")
            
            # Get priority from analysis (matching email logic)
            priority = "Medium"
            if proposal_analysis and proposal_analysis.get('priority_score', 5) >= 7:
                priority = "High"
            elif proposal_analysis and proposal_analysis.get('priority_score', 5) <= 3:
                priority = "Low"
            
            # Truncate TL;DR to ≤160 chars (matching email)
            tldr_truncated = impact_summary[:160] + "..." if len(impact_summary) > 160 else impact_summary
            
            # Format required actions as numbered list (matching email)
            actions_list = "\n".join([f"{i+1}. {action}" for i, action in enumerate(required_actions[:3])]) if required_actions else "No specific actions required"
            
            # Format why it matters as bullet points (matching email)
            matters_list = "\n".join([f"• {matter}" for matter in why_matters[:3]]) if why_matters else "• Standard protocol enhancement"
            
            # Create neutral Slack notification (matching email design)
            notification_payload = {
                "username": slack_config.get('username', 'Blockchain Research Agent'),
                "icon_emoji": slack_config.get('icon_emoji', ':robot_face:'),
                "text": f"{protocol} {proposal.get('id', 'Unknown')} — {proposal.get('title', 'Unknown Proposal')}",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{protocol} {proposal.get('id', 'Unknown')} — {proposal.get('title', 'Unknown Proposal')}*\n{proposal.get('status', 'Draft')} | Impact: {priority} | Consensus | Created: {proposal.get('created', 'Unknown')} | Breaking: {'Yes' if breaking_change else 'No'}"
                        }
                    },
                    {
                        "type": "section", 
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*TL;DR:* {tldr_truncated}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Why it matters*\n{matters_list}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Impact reason*\n{impact_type}"
                            },
                            {
                                "type": "mrkdwn", 
                                "text": f"*Activation*\nTBD"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Effect on users*\n{user_impact}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Effort*\nL (1+ months)"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Required actions*\n{actions_list}"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View Proposal",
                                    "emoji": False
                                },
                                "style": "primary",
                                "url": proposal.get('url', '#')
                            },
                            {
                                "type": "button", 
                                "text": {
                                    "type": "plain_text",
                                    "text": f"{self._get_protocol_repo_name(protocol)}",
                                    "emoji": False
                                },
                                "style": "primary",
                                "url": self._get_protocol_repo_url(protocol)
                            }
                        ]
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Confidence: Medium • Source: ethereum.org • Checked: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC"
                            }
                        ]
                    }
                ]
            }
            
            # Send to Slack
            response = requests.post(
                slack_config['webhook_url'],
                json=notification_payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"  Error sending individual Slack notification: {e}")
            return False
    
    def _get_protocol_repo_name(self, protocol: str) -> str:
        """Get the repository name for each protocol"""
        protocol_repos = {
            'TRON': 'Go-Tron',
            'BITCOIN': 'Bitcoin Core',
            'BINANCE_SMART_CHAIN': 'BSC Node',
            'ETHEREUM': 'Go-Ethereum'
        }
        return protocol_repos.get(protocol, f'{protocol} Repo')
    
    def _get_protocol_repo_url(self, protocol: str) -> str:
        """Get the main repository URL for each protocol"""
        protocol_urls = {
            'TRON': 'https://github.com/tronprotocol/java-tron',
            'BITCOIN': 'https://github.com/bitcoin/bitcoin',
            'BINANCE_SMART_CHAIN': 'https://github.com/bnb-chain/bsc',
            'ETHEREUM': 'https://github.com/ethereum/go-ethereum'
        }
        return protocol_urls.get(protocol, 'https://github.com/')
    
    def send_grouped_email_notification(self, all_proposals: List[Dict], impact_analysis: Dict) -> bool:
        """Send one grouped email with all proposals using neutral table layout"""
        
        email_config = self.load_email_config()
        if not email_config or not email_config.get('enabled'):
            return False
        
        try:
            # Create email subject
            total_proposals = len(all_proposals)
            subject = f"📊 Blockchain Impact Alert: {total_proposals} Proposals"
            
            # Get priority breakdown
            high_count = impact_analysis['priority_breakdown']['high']
            medium_count = impact_analysis['priority_breakdown']['medium']
            
            # Build neutral, professional email template with table layout
            html_body = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Blockchain Proposals</title>
            </head>
            <body style="margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
                
                <!-- Main Email Container -->
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 680px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding: 24px; text-align: center; background-color: #f8f9fa; border-bottom: 1px solid #e9ecef;">
                            <h1 style="margin: 0 0 8px 0; font-size: 24px; font-weight: 700; color: #212529;">Blockchain Proposals</h1>
                            <p style="margin: 0; font-size: 14px; color: #6c757d; font-weight: 500;">{total_proposals} new proposals • {high_count} high priority</p>
                        </td>
                    </tr>
                    
                    <!-- Content Area -->
                    <tr>
                        <td style="padding: 0;">
            """
            
            # Add each proposal as a table-based card
            for i, proposal in enumerate(all_proposals):
                protocol = proposal.get('protocol', 'unknown').upper()
                
                # Find analysis for this proposal
                proposal_analysis = None
                ai_analysis = None
                
                for analysis in impact_analysis['analyses']:
                    analysis_id = None
                    if 'proposal' in analysis and 'id' in analysis['proposal']:
                        analysis_id = analysis['proposal']['id']
                    elif 'id' in analysis:
                        analysis_id = analysis['id']
                    elif 'proposal_id' in analysis:
                        analysis_id = analysis['proposal_id']
                    
                    if analysis_id == proposal['id']:
                        proposal_analysis = analysis
                        break
                
                if proposal_analysis:
                    for ai_enhanced_analysis in impact_analysis['ai_enhanced_analyses']:
                        if ai_enhanced_analysis['proposal_id'] == proposal['id']:
                            ai_analysis = ai_enhanced_analysis
                            break
                
                # Get AI analysis details
                breaking_change = False
                impact_summary = "Protocol enhancement with governance implications"
                user_impact = "Users may experience changes in transaction processing times and fees."
                required_actions = ["upgrade nodes", "test compatibility"]
                impact_type = "governance"
                why_matters = ["introduces new instructions", "affects consensus rules"]
                
                if ai_analysis:
                    impact_summary = ai_analysis.get('impact_summary', impact_summary)
                    user_impact = ai_analysis.get('user_impact', user_impact)
                    required_actions = ai_analysis.get('required_actions', required_actions)
                    breaking_change = ai_analysis.get('breaking_change', False)
                    impact_type = ai_analysis.get('impact_category', impact_type)
                    why_matters = ai_analysis.get('why_matters', why_matters)
                elif proposal_analysis:
                    try:
                        ai_summary = self._generate_detailed_ai_summary(proposal)
                        if ai_summary:
                            impact_summary = ai_summary.get('impact_summary', impact_summary)
                            user_impact = ai_summary.get('user_impact', user_impact)
                            required_actions = ai_summary.get('required_actions', required_actions)
                            breaking_change = ai_summary.get('breaking_change', False)
                            impact_type = ai_summary.get('impact_category', impact_type)
                            why_matters = ai_summary.get('why_matters', why_matters)
                    except Exception as e:
                        print(f"  AI summary generation failed: {e}")
                
                # Get priority from analysis
                priority = "Medium"
                if proposal_analysis and proposal_analysis.get('priority_score', 5) >= 7:
                    priority = "High"
                elif proposal_analysis and proposal_analysis.get('priority_score', 5) <= 3:
                    priority = "Low"
                
                # Truncate TL;DR to ≤160 chars
                tldr_truncated = impact_summary[:160] + "..." if len(impact_summary) > 160 else impact_summary
                
                # Format required actions as numbered list (for complete display)
                actions_list = "\n".join([f"{i+1}. {action}" for i, action in enumerate(required_actions[:3])]) if required_actions else "No specific actions required"
                
                # Format why it matters as bullet points
                matters_list = "\n".join([f"• {matter}" for matter in why_matters[:3]]) if why_matters else "• Standard protocol enhancement"
                
                # Add proposal card using table layout (matching Slack format)
                html_body += f"""
                            <!-- Proposal Card {i+1} -->
                            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0 0 24px 0;">
                                
                                <!-- Proposal Header -->
                                <tr>
                                    <td style="padding: 20px 24px; background-color: #f8f9fa; border-top: 1px solid #e9ecef;">
                                        <h2 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 600; color: #212529;">
                                            {protocol} {proposal.get('id', 'Unknown')} — {proposal.get('title', 'Unknown Proposal')}
                                        </h2>
                                        
                                        <!-- Subtitle with metadata -->
                                        <p style="margin: 0; font-size: 14px; color: #6c757d; font-weight: 500;">
                                            {proposal.get('status', 'Draft')} | Impact: {priority} | Consensus | Created: {proposal.get('created', 'Unknown')} | Breaking: {'Yes' if breaking_change else 'No'}
                                        </p>
                                    </td>
                                </tr>
                                
                                <!-- TL;DR Section -->
                                <tr>
                                    <td style="padding: 16px 24px; background-color: #ffffff;">
                                        <p style="margin: 0; font-size: 14px; line-height: 1.5; color: #495057; font-weight: 400;">
                                            <strong style="color: #212529;">TL;DR:</strong> {tldr_truncated}
                                        </p>
                                    </td>
                                </tr>
                                
                                <!-- Why it matters Section -->
                                <tr>
                                    <td style="padding: 16px 24px; background-color: #ffffff;">
                                        <p style="margin: 0 0 8px 0; font-size: 12px; font-weight: 600; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">WHY IT MATTERS</p>
                                        <p style="margin: 0; font-size: 14px; color: #495057; line-height: 1.4; white-space: pre-line;">{matters_list}</p>
                                    </td>
                                </tr>
                                
                                <!-- Details Grid (2x2 layout) -->
                                <tr>
                                    <td style="padding: 16px 24px; background-color: #ffffff;">
                                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                            <tr>
                                                <td width="50%" style="padding: 0 12px 12px 0; vertical-align: top;">
                                                    <p style="margin: 0 0 4px 0; font-size: 12px; font-weight: 600; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">IMPACT REASON</p>
                                                    <p style="margin: 0; font-size: 14px; color: #495057;">{impact_type}</p>
                                                </td>
                                                <td width="50%" style="padding: 0 0 12px 12px; vertical-align: top;">
                                                    <p style="margin: 0 0 4px 0; font-size: 12px; font-weight: 600; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">ACTIVATION</p>
                                                    <p style="margin: 0; font-size: 14px; color: #495057;">TBD</p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="50%" style="padding: 12px 12px 0 0; vertical-align: top;">
                                                    <p style="margin: 0 0 4px 0; font-size: 12px; font-weight: 600; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">EFFECT ON USERS</p>
                                                    <p style="margin: 0; font-size: 14px; color: #495057;">{user_impact}</p>
                                                </td>
                                                <td width="50%" style="padding: 12px 0 0 12px; vertical-align: top;">
                                                    <p style="margin: 0 0 4px 0; font-size: 12px; font-weight: 600; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">EFFORT</p>
                                                    <p style="margin: 0; font-size: 14px; color: #495057;">L (1+ months)</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                
                                <!-- Required Actions Section -->
                                <tr>
                                    <td style="padding: 16px 24px; background-color: #ffffff;">
                                        <p style="margin: 0 0 8px 0; font-size: 12px; font-weight: 600; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">REQUIRED ACTIONS</p>
                                        <p style="margin: 0; font-size: 14px; color: #495057; line-height: 1.4; white-space: pre-line;">{actions_list}</p>
                                    </td>
                                </tr>
                                
                                <!-- Buttons (neutral styling) -->
                                <tr>
                                    <td style="padding: 20px 24px; background-color: #ffffff; text-align: center;">
                                        <table cellpadding="0" cellspacing="0" border="0" style="margin: 0 auto;">
                                            <tr>
                                                <td style="padding: 0 8px 0 0;">
                                                    <a href="{proposal.get('url', '#')}" style="display: inline-block; padding: 10px 16px; background-color: #627eea; color: #ffffff; border: 1px solid #627eea; border-radius: 4px; text-decoration: none; font-weight: 500; font-size: 14px;">
                                                        View Proposal
                                                    </a>
                                                </td>
                                                <td style="padding: 0 0 0 8px;">
                                                    <a href="{self._get_protocol_repo_url(protocol)}" style="display: inline-block; padding: 10px 16px; background-color: #627eea; color: #ffffff; border: 1px solid #627eea; border-radius: 4px; text-decoration: none; font-weight: 500; font-size: 14px;">
                                                        {self._get_protocol_repo_name(protocol)}
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                
                                <!-- Footer Line (matching Slack context) -->
                                <tr>
                                    <td style="padding: 16px 24px; background-color: #ffffff; border-top: 1px solid #e9ecef; text-align: center;">
                                        <p style="margin: 0; font-size: 11px; color: #6c757d;">
                                            Confidence: Medium • Source: ethereum.org • Checked: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC
                                        </p>
                                    </td>
                                </tr>
                                
                            </table>
                """
            
            # Close HTML structure
            html_body += """
                        </td>
                    </tr>
                    
                    <!-- Main Footer -->
                    <tr>
                        <td style="padding: 24px; text-align: center; background-color: #f8f9fa; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0; font-size: 12px; color: #6c757d;">
                                Generated by Blockchain Research Agent
                            </p>
                        </td>
                    </tr>
                    
                </table>
                
            </body>
            </html>
            """
            
            # Send email to all recipients
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['sender_email'], email_config['sender_password'])
                
                for recipient in email_config['recipient_emails']:
                    msg = MIMEMultipart('alternative')
                    msg['From'] = email_config['sender_email']
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    
                    msg.attach(MIMEText(html_body, 'html'))
                    server.send_message(msg)
            
            print(f"  Grouped email sent to {len(email_config['recipient_emails'])} recipients")
            return True
            
        except Exception as e:
            print(f"  Error sending grouped email notification: {e}")
            return False
    
    def send_individual_email_notification(self, proposal: Dict, proposal_analysis: Dict, ai_analysis: Dict) -> bool:
        """Send individual email notification for a single proposal"""
        
        email_config = self.load_email_config()
        if not email_config or not email_config.get('enabled'):
            return False
        
        try:
            protocol = proposal.get('protocol', 'unknown').upper()
            
            # Get AI analysis details (same as Slack)
            breaking_change = False
            impact_summary = "Protocol enhancement with governance implications"
            user_impact = "Users may experience changes in transaction processing times and fees."
            required_actions = ["upgrade nodes", "test compatibility"]
            impact_type = "governance"
            why_matters = ["introduces new instructions", "affects consensus rules"]
            
            if ai_analysis:
                impact_summary = ai_analysis.get('impact_summary', impact_summary)
                user_impact = ai_analysis.get('user_impact', user_impact) 
                required_actions = ai_analysis.get('required_actions', required_actions)
                breaking_change = ai_analysis.get('breaking_change', False)
                impact_type = ai_analysis.get('impact_category', impact_type)
                why_matters = ai_analysis.get('why_matters', why_matters)
            elif proposal_analysis:
                try:
                    ai_summary = self._generate_detailed_ai_summary(proposal)
                    if ai_summary:
                        impact_summary = ai_summary.get('impact_summary', impact_summary)
                        user_impact = ai_summary.get('user_impact', user_impact)
                        required_actions = ai_summary.get('required_actions', required_actions)
                        breaking_change = ai_summary.get('breaking_change', False)
                        impact_type = ai_summary.get('impact_category', impact_type)
                        why_matters = ai_summary.get('why_matters', why_matters)
                except Exception as e:
                    print(f"  AI summary generation failed: {e}")
            
            # Create HTML email content
            subject = f"🚨 {protocol} {proposal.get('id', 'Unknown')} — {proposal.get('title', 'Unknown Proposal')}"
            
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .proposal-title {{ font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
                    .meta-info {{ font-size: 14px; color: #666; margin-bottom: 15px; }}
                    .section {{ margin: 20px 0; }}
                    .section-title {{ font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
                    .content {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
                    .impact-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
                    .impact-item {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; }}
                    .actions {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .button-container {{ text-align: center; margin: 30px 0; }}
                    .button {{ display: inline-block; padding: 12px 24px; margin: 0 10px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                    .primary-button {{ background-color: #007bff; color: white; }}
                    .secondary-button {{ background-color: #6c757d; color: white; }}
                    ul {{ margin: 10px 0; padding-left: 20px; }}
                    ol {{ margin: 10px 0; padding-left: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="proposal-title">🚨 {protocol} {proposal.get('id', 'Unknown')} — {proposal.get('title', 'Unknown Proposal')}</div>
                    <div class="meta-info">
                        <strong>{proposal.get('status', 'Draft')}</strong> | 
                        <strong>Impact: {impact_type}</strong> | 
                        <strong>Consensus</strong> | 
                        <strong>Created: {proposal.get('created', 'Unknown')}</strong> | 
                        <strong>Breaking: {'Yes' if breaking_change else 'No'}</strong>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">📋 TL;DR</div>
                    <div class="content">{impact_summary}</div>
                </div>
                
                <div class="section">
                    <div class="section-title">❗ Why it matters</div>
                    <div class="content">
                        <ul>
                            {''.join([f'<li>{matter}</li>' for matter in why_matters[:3]])}
                        </ul>
                    </div>
                </div>
                
                <div class="impact-grid">
                    <div class="impact-item">
                        <strong>Impact reason</strong><br>
                        {impact_type}
                    </div>
                    <div class="impact-item">
                        <strong>Activation</strong><br>
                        TBD
                    </div>
                </div>
                
                <div class="impact-grid">
                    <div class="impact-item">
                        <strong>Effect on users</strong><br>
                        {user_impact}
                    </div>
                    <div class="impact-item">
                        <strong>Effort</strong><br>
                        L (1+ months)
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">✅ Required actions</div>
                    <div class="actions">
                        <ol>
                            {''.join([f'<li>{action}</li>' for action in required_actions[:3]])}
                        </ol>
                    </div>
                </div>
                
                <div class="button-container">
                    <a href="{proposal.get('url', '#')}" class="button primary-button">📄 View Proposal</a>
                    <a href="{self._get_protocol_repo_url(protocol)}" class="button secondary-button">🔗 {self._get_protocol_repo_name(protocol)}</a>
                </div>
                
                <hr style="margin: 30px 0;">
                <p style="color: #666; font-size: 12px; text-align: center;">
                    This is an automated notification from your Blockchain Research & Monitoring System.<br>
                    Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </body>
            </html>
            """
            
            # Send email to all recipients
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['sender_email'], email_config['sender_password'])
                
                for recipient in email_config['recipient_emails']:
                    msg = MIMEMultipart('alternative')
                    msg['From'] = email_config['sender_email']
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    
                    msg.attach(MIMEText(html_body, 'html'))
                    server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"  Error sending individual email notification: {e}")
            return False
    
    def _generate_detailed_ai_summary(self, proposal: Dict) -> Dict:
        """Generate detailed AI summary for individual proposal using OpenAI"""
        
        if not OPENAI_AVAILABLE:
            print("  OpenAI not available - using default summary")
            return None
        
        try:
            # Check if OpenAI is configured
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("  OpenAI API key not configured")
                return None
            
            # Create OpenAI client
            client = OpenAI(api_key=api_key)
            
            # Create prompt for detailed analysis
            prompt = f"""
            Analyze this blockchain proposal and provide a detailed impact summary:
            
            Protocol: {proposal.get('protocol', 'Unknown')}
            Title: {proposal.get('title', 'Unknown')}
            ID: {proposal.get('id', 'Unknown')}
            Status: {proposal.get('status', 'Draft')}
            Author: {proposal.get('author', 'Unknown')}
            Created: {proposal.get('created', 'Unknown')}
            Summary: {proposal.get('summary', 'No summary available')[:500]}
            
            Provide a JSON response with:
            {{
                "impact_summary": "One sentence TL;DR of what this proposal does",
                "impact_category": "governance|protocol|security|performance|interoperability",
                "breaking_change": true/false,
                "user_impact": "How this affects end users in practical terms",
                "why_matters": ["reason 1", "reason 2", "reason 3"],
                "required_actions": ["action 1", "action 2"]
            }}
            
            Focus on practical impacts and be concise but informative.
            """
            
            try:
                response = client.chat.completions.create(
                    model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
                    messages=[
                        {"role": "system", "content": "You are a blockchain protocol expert. Analyze proposals and provide clear, concise impact summaries in JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '500')),
                    temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
                )
                
                # Parse JSON response
                content = response.choices[0].message.content.strip()
                
                # Extract JSON from response (handle cases where AI adds extra text)
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_content = content[start_idx:end_idx]
                    return json.loads(json_content)
                    
            except Exception as api_error:
                print(f"  OpenAI API error: {api_error}")
                return None
                
        except Exception as e:
            print(f"  AI summary generation error: {e}")
            return None
    
    def _summarize_transaction_impacts(self, analyses: List[Dict]) -> Dict:
        """Summarize transaction impacts across all proposals"""
        
        summary = {
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'critical_impacts': [],
            'high_impacts': [],
            'gas_fee_changes': {'increase': 0, 'decrease': 0},
            'confirmation_time_changes': {'faster': 0, 'slower': 0},
            'wallet_compatibility_issues': 0,
            'user_action_required_count': 0
        }
        
        for analysis in analyses:
            tx_impact = analysis.get('transaction_impact', {})
            impact_level = tx_impact.get('user_impact_level', 'none')
            
            # Count by impact level
            if impact_level == 'critical':
                summary['critical_count'] += 1
                summary['critical_impacts'].append({
                    'proposal_id': analysis['proposal_id'],
                    'summary': tx_impact.get('summary', '')
                })
            elif impact_level == 'high':
                summary['high_count'] += 1
                summary['high_impacts'].append({
                    'proposal_id': analysis['proposal_id'],
                    'summary': tx_impact.get('summary', '')
                })
            elif impact_level == 'medium':
                summary['medium_count'] += 1
            else:
                summary['low_count'] += 1
            
            # Count specific impacts
            if tx_impact.get('gas_fee_impact') == 'increase':
                summary['gas_fee_changes']['increase'] += 1
            elif tx_impact.get('gas_fee_impact') == 'decrease':
                summary['gas_fee_changes']['decrease'] += 1
            
            if tx_impact.get('confirmation_time_impact') == 'faster':
                summary['confirmation_time_changes']['faster'] += 1
            elif tx_impact.get('confirmation_time_impact') == 'slower':
                summary['confirmation_time_changes']['slower'] += 1
            
            if tx_impact.get('wallet_compatibility_impact') == 'breaking':
                summary['wallet_compatibility_issues'] += 1
            
            if tx_impact.get('user_action_required'):
                summary['user_action_required_count'] += 1
        
        return summary
    
    def send_enhanced_email(self, new_proposals: Dict, impact_analysis: Dict) -> bool:
        """Send enhanced email with impact analysis"""
        
        email_config = self.load_email_config()
        if not email_config or not email_config.get('enabled'):
            print("  Email not configured")
            return False
        
        try:
            # Create enhanced email content
            subject = f"🚨 Blockchain Proposals Alert: {impact_analysis['total_proposals']} New Proposals with Impact Analysis"
            
            # Analyze transaction impacts
            transaction_impacts = self._summarize_transaction_impacts(impact_analysis['analyses'])
            
            # Build comprehensive email body
            body_lines = [
                "# 🚨 New Blockchain Proposals Detected",
                "",
                f"**{impact_analysis['total_proposals']} new proposals** have been detected with comprehensive impact analysis.",
                "",
                "## 💳 Transaction Impact Summary",
                "",
                f"**{transaction_impacts['critical_count']} Critical** | **{transaction_impacts['high_count']} High** | **{transaction_impacts['medium_count']} Medium** | **{transaction_impacts['low_count']} Low/None**",
                ""
            ]
            
            # Add AI-enhanced transaction impacts
            ai_enhanced_analyses = impact_analysis.get('ai_enhanced_analyses', [])
            if ai_enhanced_analyses:
                body_lines.extend([
                    "### 🤖 AI-ENHANCED TRANSACTION IMPACT ANALYSIS",
                    ""
                ])
                
                for analysis in ai_enhanced_analyses:
                    ai_analysis = analysis.get('ai_transaction_analysis', {})
                    if ai_analysis:
                        body_lines.extend([
                            f"#### {analysis['proposal_id']}: AI Analysis",
                            f"**Executive Summary**: {ai_analysis.get('executive_summary', 'Analysis pending')}",
                            "",
                            "**Detailed Impact Analysis:**"
                        ])
                        
                        detailed = ai_analysis.get('detailed_impact', {})
                        for impact_type, description in detailed.items():
                            if description and description != "No significant changes detected":
                                body_lines.append(f"• **{impact_type.replace('_', ' ').title()}**: {description}")
                        
                        body_lines.append("")
                        
                        # Add user action items
                        user_actions = ai_analysis.get('user_action_items', [])
                        if user_actions:
                            body_lines.append("**Required User Actions:**")
                            for action in user_actions[:3]:  # Limit to top 3
                                body_lines.append(f"• {action}")
                            body_lines.append("")
                        
                        # Add real-world scenarios
                        scenarios = ai_analysis.get('real_world_scenarios', [])
                        if scenarios:
                            body_lines.append("**Real-World Impact:**")
                            for scenario in scenarios[:2]:  # Limit to top 2
                                body_lines.append(f"• {scenario}")
                            body_lines.append("")
                        
                        body_lines.append("---")
                        body_lines.append("")
            
            # Add critical transaction impacts (fallback)
            if transaction_impacts['critical_impacts']:
                body_lines.extend([
                    "### 🚨 CRITICAL TRANSACTION IMPACTS",
                    ""
                ])
                for impact in transaction_impacts['critical_impacts']:
                    body_lines.append(f"• **{impact['proposal_id']}**: {impact['summary']}")
                body_lines.append("")
            
            # Add high transaction impacts (fallback)
            if transaction_impacts['high_impacts']:
                body_lines.extend([
                    "### ⚠️ HIGH TRANSACTION IMPACTS",
                    ""
                ])
                for impact in transaction_impacts['high_impacts']:
                    body_lines.append(f"• **{impact['proposal_id']}**: {impact['summary']}")
                body_lines.append("")
            
            body_lines.extend([
                "## 📊 Executive Summary",
                "",
                f"• **High Priority**: {impact_analysis['priority_breakdown']['high']} proposals requiring immediate attention",
                f"• **Medium Priority**: {impact_analysis['priority_breakdown']['medium']} proposals for next sprint planning", 
                f"• **Low Priority**: {impact_analysis['priority_breakdown']['low']} proposals for regular monitoring",
                "",
            ])
            
            # Add critical proposals section
            if impact_analysis['critical_proposals']:
                body_lines.extend([
                    "## 🚨 CRITICAL PROPOSALS - IMMEDIATE ACTION REQUIRED",
                    ""
                ])
                
                for analysis in impact_analysis['critical_proposals']:
                    body_lines.extend([
                        f"### {analysis['proposal_id']}: {analysis['title']}",
                        f"**Status**: {analysis['status']} | **Priority Score**: {analysis['priority_score']}/10",
                        "",
                        "**🏗️ Development Impact:**"
                    ])
                    
                    dev_impact = analysis['development_impact']
                    if dev_impact['breaking_changes']:
                        body_lines.append("• ⚠️ **Breaking Changes** - Migration required")
                    if dev_impact['api_changes']:
                        body_lines.append("• 🔧 **API Changes** - Update integrations")
                    
                    body_lines.extend([
                        f"• ⏱️ **Estimated Effort**: {dev_impact['estimated_effort']}",
                        f"• 🎯 **Affected Components**: {', '.join(dev_impact['affected_components'])}",
                        "",
                        "**💼 Product Impact:**"
                    ])
                    
                    prod_impact = analysis['product_impact']
                    for implication in prod_impact['business_implications']:
                        body_lines.append(f"• {implication}")
                    
                    body_lines.extend([
                        "",
                        "**🎯 Recommended Actions:**"
                    ])
                    
                    for action in analysis['recommended_actions']:
                        body_lines.append(f"• {action}")
                    
                    body_lines.extend(["", "---", ""])
            
            # Add detailed proposal breakdown by protocol
            protocol_info = {
                'eips': '🔷 Ethereum Improvement Proposals (EIPs)',
                'tips': '🔶 Tron Improvement Proposals (TIPs)',
                'bips': '🟡 Bitcoin Improvement Proposals (BIPs)',
                'beps': '🟨 BNB Chain Evolution Proposals (BEPs)'
            }
            
            body_lines.extend([
                "## 📋 Detailed Proposal Analysis",
                ""
            ])
            
            for protocol, proposals in new_proposals.items():
                if not proposals:
                    continue
                    
                protocol_name = protocol_info.get(protocol, protocol.upper())
                body_lines.extend([
                    f"### {protocol_name}",
                    f"**{len(proposals)} new proposals**",
                    ""
                ])
                
                for proposal in proposals:
                    # Find the analysis for this proposal
                    analysis = next((a for a in impact_analysis['analyses'] 
                                   if a['proposal_id'] == proposal['id']), None)
                    
                    if analysis:
                        body_lines.extend([
                            f"#### {proposal['id']}: {proposal.get('title', 'No title')}",
                            f"**Status**: {proposal.get('status', 'Unknown')} | **Priority**: {analysis['priority_score']}/10",
                            f"**Link**: {proposal.get('link', 'N/A')}",
                            "",
                            f"**Impact Areas**: {', '.join(analysis['impact_areas'])}",
                            f"**Development Effort**: {analysis['development_impact']['estimated_effort']}",
                            f"**Timeline**: {analysis['timeline_impact']['recommended_timeline']}",
                            ""
                        ])
                        
                        if analysis['development_impact']['action_items']:
                            body_lines.append("**Development Actions:**")
                            for action in analysis['development_impact']['action_items']:
                                body_lines.append(f"• {action}")
                            body_lines.append("")
                        
                        if analysis['product_impact']['business_implications']:
                            body_lines.append("**Business Impact:**")
                            for implication in analysis['product_impact']['business_implications']:
                                body_lines.append(f"• {implication}")
                            body_lines.append("")
                        
                        body_lines.append("---")
                        body_lines.append("")
            
            # Add strategic insights
            if impact_analysis['strategic_insights']:
                body_lines.extend([
                    "## 🧠 Strategic Insights",
                    ""
                ])
                
                for insight in impact_analysis['strategic_insights']:
                    body_lines.append(f"• {insight}")
                
                body_lines.append("")
            
            # Add immediate actions summary
            if impact_analysis['recommended_immediate_actions']:
                body_lines.extend([
                    "## ⚡ Immediate Actions Required",
                    ""
                ])
                
                for action in impact_analysis['recommended_immediate_actions']:
                    body_lines.append(f"• {action}")
                
                body_lines.append("")
            
            # Footer
            body_lines.extend([
                "---",
                "",
                "**📊 Impact Areas Summary:**",
                ""
            ])
            
            for area, count in impact_analysis['impact_areas_summary'].items():
                body_lines.append(f"• **{area.title()}**: {count} proposals")
            
            body_lines.extend([
                "",
                f"Generated by **Blockchain Research Agent** at {datetime.now().strftime('%Y-%m-%d %I:%M %p')}",
                "",
                "*This analysis is automated and should be reviewed by technical and product teams.*"
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
            
            print(f"  Enhanced email sent to {len(email_config['recipient_emails'])} recipients")
            return True
            
        except Exception as e:
            print(f"  Email failed: {e}")
            return False
    
    def send_enhanced_slack(self, new_proposals: Dict, impact_analysis: Dict) -> bool:
        """Send enhanced Slack notification with impact analysis"""
        
        slack_config = self.load_slack_config()
        if not slack_config or not slack_config.get('enabled'):
            print("  Slack not configured")
            return False
        
        try:
            # Analyze transaction impacts
            transaction_impacts = self._summarize_transaction_impacts(impact_analysis['analyses'])
            
            # Create enhanced Slack blocks
            blocks = []
            
            # Header with summary
            total_proposals = impact_analysis['total_proposals']
            high_priority = impact_analysis['priority_breakdown']['high']
            
            header_text = f":warning: *New Blockchain Proposals Alert: {total_proposals} Detected*\n"
            header_text += f":bar_chart: *Priority Breakdown*: {high_priority} High | {impact_analysis['priority_breakdown']['medium']} Medium | {impact_analysis['priority_breakdown']['low']} Low"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": header_text
                }
            })
            
            # Transaction Impact Summary
            if transaction_impacts['critical_count'] > 0 or transaction_impacts['high_count'] > 0:
                tx_summary_text = f":credit_card: *Transaction Impact Summary*\n"
                tx_summary_text += f":red_circle: {transaction_impacts['critical_count']} Critical | :orange_circle: {transaction_impacts['high_count']} High | :yellow_circle: {transaction_impacts['medium_count']} Medium | :green_circle: {transaction_impacts['low_count']} Low/None\n"
                
                if transaction_impacts['gas_fee_changes']['decrease'] > 0:
                    tx_summary_text += f":money_with_wings: {transaction_impacts['gas_fee_changes']['decrease']} proposals may reduce gas fees\n"
                if transaction_impacts['gas_fee_changes']['increase'] > 0:
                    tx_summary_text += f":chart_with_upwards_trend: {transaction_impacts['gas_fee_changes']['increase']} proposals may increase gas fees\n"
                if transaction_impacts['wallet_compatibility_issues'] > 0:
                    tx_summary_text += f":warning: {transaction_impacts['wallet_compatibility_issues']} proposals require wallet updates\n"
                if transaction_impacts['user_action_required_count'] > 0:
                    tx_summary_text += f":point_right: {transaction_impacts['user_action_required_count']} proposals require user action"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": tx_summary_text
                    }
                })
            
            blocks.append({"type": "divider"})
            
            # Critical proposals section
            if impact_analysis['critical_proposals']:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":rotating_light: *CRITICAL PROPOSALS - IMMEDIATE ATTENTION REQUIRED*"
                    }
                })
                
                for analysis in impact_analysis['critical_proposals']:
                    critical_text = f"*{analysis['proposal_id']}*: {analysis['title']}\n"
                    critical_text += f":chart_with_upwards_trend: Priority: {analysis['priority_score']}/10 | Status: {analysis['status']}\n"
                    critical_text += f":hammer_and_wrench: Effort: {analysis['development_impact']['estimated_effort']}\n"
                    critical_text += f":clock1: Timeline: {analysis['timeline_impact']['recommended_timeline']}"
                    
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": critical_text
                        }
                    })
                
                blocks.append({"type": "divider"})
            
            # Proposal breakdown by protocol
            protocol_emojis = {
                'eips': ':large_blue_diamond:',
                'tips': ':large_orange_diamond:',
                'bips': ':large_yellow_circle:',
                'beps': ':large_yellow_square:'
            }
            
            protocol_names = {
                'eips': 'Ethereum (EIPs)',
                'tips': 'Tron (TIPs)',
                'bips': 'Bitcoin (BIPs)',
                'beps': 'BNB Chain (BEPs)'
            }
            
            for protocol, proposals in new_proposals.items():
                if not proposals:
                    continue
                
                emoji = protocol_emojis.get(protocol, ':diamond_shape_with_a_dot_inside:')
                name = protocol_names.get(protocol, protocol.upper())
                
                protocol_text = f"{emoji} *{name}*\n_{len(proposals)} new proposals_\n\n"
                
                for i, proposal in enumerate(proposals[:3]):  # Limit to 3 per protocol
                    # Find analysis
                    analysis = next((a for a in impact_analysis['analyses'] 
                                   if a['proposal_id'] == proposal['id']), None)
                    
                    priority_emoji = ":red_circle:" if analysis and analysis['priority_score'] >= 7 else ":yellow_circle:" if analysis and analysis['priority_score'] >= 4 else ":green_circle:"
                    
                    link = proposal.get('link', '#')
                    protocol_text += f"{priority_emoji} *<{link}|{proposal['id']}>*: {proposal.get('title', 'No title')}\n"
                    
                    if analysis:
                        protocol_text += f"   :dart: Priority {analysis['priority_score']}/10 | Impact: {', '.join(analysis['impact_areas'][:2])}\n"
                        if analysis['development_impact']['breaking_changes']:
                            protocol_text += "   :warning: Breaking changes detected\n"
                        if analysis['product_impact']['performance_improvement']:
                            protocol_text += "   :zap: Performance improvement opportunity\n"
                    
                    protocol_text += "\n"
                
                if len(proposals) > 3:
                    protocol_text += f"   _... and {len(proposals) - 3} more proposals_\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": protocol_text
                    }
                })
            
            # Strategic insights
            if impact_analysis['strategic_insights']:
                insights_text = ":bulb: *Strategic Insights*\n"
                for insight in impact_analysis['strategic_insights'][:3]:
                    insights_text += f"• {insight}\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": insights_text
                    }
                })
            
            # Immediate actions
            if impact_analysis['recommended_immediate_actions']:
                actions_text = ":point_right: *Immediate Actions Required*\n"
                for action in impact_analysis['recommended_immediate_actions'][:3]:
                    actions_text += f"• {action}\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": actions_text
                    }
                })
            
            # Footer
            footer_text = f":robot_face: Generated by Blockchain Research Agent | {datetime.now().strftime('%Y-%m-%d %I:%M %p')}"
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": footer_text
                    }
                ]
            })
            
            # Send to Slack
            message = {
                "username": slack_config.get("username", "Blockchain Research Agent"),
                "icon_emoji": slack_config.get("icon_emoji", ":robot_face:"),
                "blocks": blocks
            }
            
            response = requests.post(slack_config['webhook_url'], json=message, timeout=10)
            
            if response.status_code == 200:
                print(f"  Enhanced Slack notification sent to {slack_config.get('channel', 'default channel')}")
                return True
            else:
                print(f"  Slack failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Slack failed: {e}")
            return False