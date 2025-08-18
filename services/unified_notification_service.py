"""
Unified Notification Service
Sends single, compact impact-focused alerts for blockchain proposals
"""
import json
import os
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from services.unified_impact_analyzer import UnifiedImpactAnalyzer, ProposalImpact

class UnifiedNotificationService:
    """Unified notification service using impact-focused schema"""
    
    def __init__(self):
        self.analyzer = UnifiedImpactAnalyzer()
        self.email_config_file = "data/email_config.json"
        self.slack_config_file = "data/slack_config.json"
    
    def load_config(self, config_file: str) -> Dict:
        """Load configuration file"""
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def send_unified_notifications(self, new_proposals: Dict[str, List[Dict]]) -> Dict:
        """Send unified impact-focused notifications"""
        
        print(f"=== UNIFIED NOTIFICATION SERVICE ===")
        print(f"Processing {sum(len(props) for props in new_proposals.values())} proposals...")
        
        # Analyze all proposals with unified impact framework
        impact_analyses = []
        
        for protocol, proposals in new_proposals.items():
            for proposal in proposals:
                try:
                    impact = self.analyzer.analyze_proposal(proposal)
                    impact_analyses.append(impact)
                    print(f"  {impact.proposal_id}: {impact.impact_level} impact")
                except Exception as e:
                    print(f"  Error analyzing {proposal.get('id', 'Unknown')}: {e}")
        
        # Sort by impact level (Critical > High > Medium > Low)
        impact_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        impact_analyses.sort(key=lambda x: impact_order.get(x.impact_level, 3))
        
        # Send notifications
        results = {}
        
        if impact_analyses:
            print(f"\nSending unified notifications...")
            results['email'] = self.send_unified_email(impact_analyses)
            results['slack'] = self.send_unified_slack(impact_analyses)
        
        return results
    
    def send_unified_slack(self, impacts: List[ProposalImpact]) -> bool:
        """Send unified Slack notifications"""
        
        slack_config = self.load_config(self.slack_config_file)
        if not slack_config or not slack_config.get('enabled'):
            print("  Slack not configured")
            return False
        
        try:
            # Send one Block Kit message per proposal
            for impact in impacts:
                # Skip low-impact items unless specifically requested
                if impact.impact_level == 'Low' and impact.confidence == 'Low':
                    continue
                
                message_blocks = self._create_slack_message(impact)
                
                payload = {
                    "username": slack_config.get("username", "Blockchain Impact Bot"),
                    "icon_emoji": slack_config.get("icon_emoji", ":robot_face:"),
                    **message_blocks  # Spread the blocks into the payload
                }
                
                response = requests.post(
                    slack_config['webhook_url'], 
                    json=payload, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"  Slack: {impact.proposal_id} ({impact.impact_level}) sent with Block Kit")
                else:
                    print(f"  Slack: {impact.proposal_id} failed - HTTP {response.status_code}")
                    print(f"    Response: {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  Slack failed: {e}")
            return False
    
    def _create_slack_message(self, impact: ProposalImpact) -> Dict:
        """Create structured Slack Block Kit message"""
        
        # Single emoji in header based on impact level
        emoji_map = {
            'Critical': '🚨',
            'High': '⚡', 
            'Medium': '⚠️',
            'Low': '📝'
        }
        emoji = emoji_map.get(impact.impact_level, '📝')
        
        # Build Block Kit structure
        blocks = []
        
        # 1. Header - clean title
        header_text = f"{emoji} {impact.chain} {impact.proposal_id} — {impact.title[:50]}"
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text", 
                "text": header_text
            }
        })
        
        # 2. Compact context line - merge all metadata into one clean line
        breaking_text = "**Yes**" if impact.breaking_changes else "**No**"
        context_line = f"*{impact.stage}* • **Impact: {impact.impact_level}** • {impact.type} • Breaking: {breaking_text} • Compat: **{impact.compatibility}** • Mig: **{impact.migration_complexity}**"
        
        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": context_line}
            ]
        })
        
        # 3. TL;DR - single clear sentence (≤160 chars)
        tldr_text = impact.tl_dr[:160]
        if len(impact.tl_dr) > 160:
            tldr_text += "..."
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*TL;DR* {tldr_text}"
            }
        })
        
        # 4. Why it matters - max 2 bullets
        if impact.impact_reasons:
            why_text = "*Why it matters*\n"
            for reason in impact.impact_reasons[:2]:
                why_text += f"• {reason}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": why_text.strip()
                }
            })
        
        # 5. Field grid (2x3) - key info in structured format
        fields = []
        
        # Impact reason - keep short
        if impact.impact_reasons:
            fields.append({
                "type": "mrkdwn",
                "text": f"*Impact reason*\n{impact.impact_reasons[0][:40]}"
            })
        
        # Activation - better term than "Execution Date"
        execution_date = impact.deadline_or_activation
        if execution_date and execution_date != 'TBD':
            # Format activation nicely
            if '2024-03-13' in execution_date:
                date_display = "Activated with *Dencun* (2024-03-13)"
            elif '2021-08-05' in execution_date:
                date_display = "Activated with *London* (2021-08-05)"
            elif 'Block' in execution_date:
                date_display = execution_date
            elif len(execution_date) == 10 and '-' in execution_date:  # YYYY-MM-DD format
                date_display = f"Planned: {execution_date}"
            else:
                date_display = execution_date[:25]
        else:
            date_display = "TBD"
        
        fields.append({
            "type": "mrkdwn", 
            "text": f"*Activation*\n{date_display}"
        })
        
        # Effect on users - keep to 2 short lines
        user_effect = impact.user_facing_effects[:60]
        if len(impact.user_facing_effects) > 60:
            user_effect += "..."
        # Split long text into 2 lines if possible
        if ';' in user_effect:
            user_effect = user_effect.replace(';', '\n', 1)
        
        fields.append({
            "type": "mrkdwn",
            "text": f"*Effect on users*\n{user_effect}"
        })
        
        # Required actions - only if not already activated
        if impact.required_actions and not (execution_date and '2024' in execution_date and 'Activated' in date_display):
            actions_text = ""
            for i, action in enumerate(impact.required_actions[:2], 1):
                action_short = action[:35]
                if len(action) > 35:
                    action_short += "..."
                actions_text += f"{i}. {action_short}\n"
            
            fields.append({
                "type": "mrkdwn",
                "text": f"*Do now*\n{actions_text.strip()}"
            })
        
        # Effort - shorter description
        effort_desc = {
            'S': '1-2 days',
            'M': '1-2 weeks',
            'L': '1+ months',
            'TBD': 'TBD'
        }.get(impact.estimated_effort, 'Unknown')
        
        fields.append({
            "type": "mrkdwn",
            "text": f"*Effort*\n{impact.estimated_effort} ({effort_desc})"
        })
        
        if fields:
            blocks.append({
                "type": "section",
                "fields": fields
            })
        
        # 6. Divider
        blocks.append({"type": "divider"})
        
        # 7. Actions - buttons for links
        actions = []
        
        # Only include the essential "View Proposal" button
        if impact.url:
            actions.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "📋 View Proposal"},
                "url": impact.url,
                "style": "primary"
            })
        
        if actions:
            blocks.append({
                "type": "actions",
                "elements": actions[:3]  # Max 3 buttons
            })
        
        # 8. Footer - confidence, source, timestamp (compact)
        source_domain = f"{impact.chain.lower()}.org" if impact.chain in ['Ethereum', 'Bitcoin'] else "github.com"
        footer_text = f"*Confidence: {impact.confidence}* • Source: {source_domain} • Checked {impact.last_checked_utc[:16]} UTC"
        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": footer_text}
            ]
        })
        
        return {"blocks": blocks}
    
    def _effort_to_description(self, effort: str) -> str:
        """Convert effort code to readable description"""
        effort_map = {
            'S': 'Small - 1-2 days',
            'M': 'Medium - 1-2 weeks', 
            'L': 'Large - 1+ months',
            'TBD': 'To be determined'
        }
        return effort_map.get(effort, 'Unknown')
    
    def _create_html_email_for_proposal(self, impact: ProposalImpact) -> str:
        """Create HTML email content for a single proposal"""
        
        # Format activation nicely
        activation = impact.deadline_or_activation
        if '2024-03-13' in activation:
            activation = "Activated with <em>Dencun</em> (2024-03-13)"
        elif '2021-08-05' in activation:
            activation = "Activated with <em>London</em> (2021-08-05)"
        elif activation == 'TBD':
            activation = "TBD"
        else:
            activation = activation
        
        # Get effort description
        effort_desc = self._effort_to_description(impact.estimated_effort)
        
        html_template = f"""
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:100%;background:#ffffff;border-radius:10px;border:1px solid #e8ebf3;margin-bottom:20px;">
          <!-- Header -->
          <tr><td style="padding:20px 24px 8px 24px;">
            <div style="font-size:20px;line-height:26px;font-weight:700;color:#111;">⚡ {impact.chain} {impact.proposal_id} — {impact.title}</div>
            <div style="margin-top:6px;font-size:12px;color:#5b6472;">
              {impact.stage} • Impact: <strong>{impact.impact_level}</strong> • {impact.type} • Breaking: <strong>{'Yes' if impact.breaking_changes else 'No'}</strong> • Compat: <strong>{impact.compatibility}</strong> • Mig: <strong>{impact.migration_complexity}</strong>
            </div>
          </td></tr>

          <!-- TLDR -->
          <tr><td style="padding:8px 24px 0 24px;">
            <div style="font-size:14px;color:#111;"><strong>TL;DR</strong> {impact.tl_dr}</div>
          </td></tr>

          <!-- Why it matters -->
          <tr><td style="padding:12px 24px 0 24px;">
            <div style="font-size:14px;font-weight:700;color:#111;margin-bottom:4px;">Why it matters</div>
            <ul style="margin:0;padding-left:18px;color:#1f2937;font-size:14px;line-height:20px;">
              {"".join(f"<li>{reason}</li>" for reason in impact.impact_reasons[:2])}
            </ul>
          </td></tr>

          <!-- Two-column fields -->
          <tr><td style="padding:16px 24px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td valign="top" style="width:50%;padding-right:12px;">
                  <div style="font-size:13px;font-weight:700;color:#111;">Impact reason</div>
                  <div style="font-size:14px;color:#1f2937;line-height:20px;">{impact.impact_reasons[0] if impact.impact_reasons else 'Assessment pending'}</div>
                  <div style="height:12px;"></div>
                  <div style="font-size:13px;font-weight:700;color:#111;">Effect on users</div>
                  <div style="font-size:14px;color:#1f2937;line-height:20px;">{impact.user_facing_effects[:80]}{'...' if len(impact.user_facing_effects) > 80 else ''}</div>
                </td>
                <td valign="top" style="width:50%;padding-left:12px;">
                  <div style="font-size:13px;font-weight:700;color:#111;">Activation</div>
                  <div style="font-size:14px;color:#1f2937;line-height:20px;">{activation}</div>
                  <div style="height:12px;"></div>
                  <div style="font-size:13px;font-weight:700;color:#111;">Effort</div>
                  <div style="font-size:14px;color:#1f2937;line-height:20px;">{impact.estimated_effort} ({effort_desc})</div>
                </td>
              </tr>
            </table>
          </td></tr>

          <!-- Actions section (only if needed) -->
          {"" if not impact.required_actions or (activation and "Activated" in activation) else f'''
          <tr><td style="padding:0px 24px 8px 24px;">
            <div style="font-size:13px;font-weight:700;color:#111;margin-bottom:4px;">Required actions</div>
            <ul style="margin:0;padding-left:18px;color:#1f2937;font-size:14px;line-height:20px;">
              {"".join(f"<li>{action}</li>" for action in impact.required_actions[:2])}
            </ul>
          </td></tr>
          '''}

          <!-- Buttons -->
          <tr><td align="left" style="padding:8px 24px 20px 24px;">
            <a href="{impact.url}" style="display:inline-block;background:#0ea5e9;color:#fff;text-decoration:none;padding:10px 14px;border-radius:8px;font-size:14px;">📋 View Proposal</a>
          </td></tr>

          <!-- Footer -->
          <tr><td style="padding:12px 24px 18px 24px;border-top:1px solid #eef1f6;">
            <div style="font-size:12px;color:#6b7280;">
              Confidence: {impact.confidence} • Source: {impact.chain.lower()}.org • Checked {impact.last_checked_utc[:16]} UTC
            </div>
          </td></tr>
        </table>
        """
        
        return html_template
    
    def _create_plaintext_email_for_proposal(self, impact: ProposalImpact) -> str:
        """Create plain text email content for a single proposal"""
        
        activation = impact.deadline_or_activation
        if '2024-03-13' in activation:
            activation = "Activated with Dencun (2024-03-13)"
        elif '2021-08-05' in activation:
            activation = "Activated with London (2021-08-05)"
            
        effort_desc = self._effort_to_description(impact.estimated_effort)
        
        lines = [
            f"[Impact Alert] {impact.chain} {impact.proposal_id} — {impact.title} ({impact.stage} | Impact: {impact.impact_level})",
            f"",
            f"TL;DR: {impact.tl_dr}",
            f"",
            f"Why it matters:",
        ]
        
        for reason in impact.impact_reasons[:2]:
            lines.append(f"- {reason}")
        
        lines.extend([
            f"",
            f"Impact reason: {impact.impact_reasons[0] if impact.impact_reasons else 'Assessment pending'}",
            f"Activation: {activation}",
            f"Effect on users: {impact.user_facing_effects[:100]}{'...' if len(impact.user_facing_effects) > 100 else ''}",
            f"Effort: {impact.estimated_effort} ({effort_desc})",
            f"",
            f"Confidence: {impact.confidence} | Source: {impact.chain.lower()}.org | Checked {impact.last_checked_utc[:16]} UTC",
            f"View Proposal: {impact.url}",
        ])
        
        return "\n".join(lines)
    
    def send_unified_email(self, impacts: List[ProposalImpact]) -> bool:
        """Send unified email notification"""
        
        email_config = self.load_config(self.email_config_file)
        if not email_config or not email_config.get('enabled'):
            print("  Email not configured")
            return False
        
        try:
            # Filter out low-confidence low-impact items
            filtered_impacts = [impact for impact in impacts if not (impact.impact_level == 'Low' and impact.confidence == 'Low')]
            
            # Create subject
            subject = f"Blockchain Impact Alert: {len(filtered_impacts)} Proposals"
            
            # Count by impact level
            impact_counts = {}
            for impact in filtered_impacts:
                impact_counts[impact.impact_level] = impact_counts.get(impact.impact_level, 0) + 1
            
            # Create HTML email body
            html_header = f"""
            <!doctype html>
            <html>
              <body style="margin:0;padding:0;background:#f6f7fb;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f6f7fb;">
                  <tr><td align="center" style="padding:24px;">
                    <!-- Email Header -->
                    <div style="max-width:600px;margin:0 auto;padding:20px;background:#ffffff;border-radius:10px;border:1px solid #e8ebf3;margin-bottom:20px;">
                      <h1 style="margin:0;font-size:24px;font-weight:700;color:#111;">📊 Blockchain Proposal Impact Summary</h1>
                      <p style="margin:8px 0 0 0;font-size:14px;color:#5b6472;">{len(filtered_impacts)} proposals analyzed with AI-enhanced impact assessment</p>
                      <div style="margin-top:12px;font-size:14px;color:#1f2937;">
            """
            
            # Add impact counts
            count_parts = []
            for level in ['Critical', 'High', 'Medium', 'Low']:
                if impact_counts.get(level, 0) > 0:
                    count_parts.append(f"<strong>{level}</strong>: {impact_counts[level]}")
            
            html_header += " • ".join(count_parts) + "</div></div>"
            
            # Add each proposal as HTML
            html_proposals = ""
            for impact in filtered_impacts:
                html_proposals += self._create_html_email_for_proposal(impact)
            
            # HTML footer
            html_footer = f"""
                    <div style="max-width:600px;margin:0 auto;padding:16px;background:#f8fafc;border-radius:8px;text-align:center;">
                      <p style="margin:0;font-size:12px;color:#6b7280;">
                        Generated by Unified Blockchain Impact Analyzer at {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC<br>
                        This analysis uses AI-enhanced impact assessment for actionable insights.
                      </p>
                    </div>
                  </td></tr>
                </table>
              </body>
            </html>
            """
            
            html_body = html_header + html_proposals + html_footer
            
            # Create plain text version
            plaintext_body = f"Blockchain Impact Alert: {len(filtered_impacts)} Proposals\n\n"
            
            for level in ['Critical', 'High', 'Medium', 'Low']:
                if impact_counts.get(level, 0) > 0:
                    plaintext_body += f"{level}: {impact_counts[level]} proposals\n"
            
            plaintext_body += "\n" + "="*50 + "\n\n"
            
            for impact in filtered_impacts:
                plaintext_body += self._create_plaintext_email_for_proposal(impact) + "\n\n" + "="*50 + "\n\n"
            
            plaintext_body += f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC"
            
            # Create multipart message with HTML and plain text
            msg = MIMEMultipart('alternative')
            msg['From'] = email_config['sender_email']
            msg['To'] = ', '.join(email_config['recipient_emails'])
            msg['Subject'] = subject
            
            # Attach both versions
            text_part = MIMEText(plaintext_body, 'plain', 'utf-8')
            html_part = MIMEText(html_body, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            server.sendmail(email_config['sender_email'], email_config['recipient_emails'], msg.as_string())
            server.quit()
            
            print(f"  HTML email sent with {len(filtered_impacts)} impact analyses")
            return True
            
        except Exception as e:
            print(f"  Email failed: {e}")
            return False
    
    def save_impact_data(self, impacts: List[ProposalImpact], filename: str = None) -> str:
        """Save impact data as JSON for storage/transmission"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/impact_analysis_{timestamp}.json"
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Convert to JSON
        impact_data = {
            'generated_at': datetime.utcnow().isoformat(),
            'total_proposals': len(impacts),
            'impact_summary': {},
            'proposals': [impact.to_dict() for impact in impacts]
        }
        
        # Add impact summary
        for impact in impacts:
            level = impact.impact_level
            impact_data['impact_summary'][level] = impact_data['impact_summary'].get(level, 0) + 1
        
        with open(filename, 'w') as f:
            json.dump(impact_data, f, indent=2)
        
        print(f"  Impact data saved to {filename}")
        return filename