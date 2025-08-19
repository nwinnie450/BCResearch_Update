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
        results = {}
        
        # Enhanced email notification
        print(f"\nSending enhanced email notification...")
        results['email'] = self.send_enhanced_email(new_proposals, impact_analysis)
        
        # Enhanced Slack notification  
        print(f"Sending enhanced Slack notification...")
        results['slack'] = self.send_enhanced_slack(new_proposals, impact_analysis)
        
        return results
    
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