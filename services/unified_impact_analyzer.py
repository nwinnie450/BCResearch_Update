"""
Unified Proposal Impact Analyzer
Single impact-focused analysis for all blockchain improvement proposals
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ProposalImpact:
    """Unified proposal impact data structure"""
    chain: str
    proposal_id: str
    title: str
    url: str
    stage: str  # Draft | Review | Last Call | Final | Withdrawn
    type: str   # Core | Consensus | Networking | Interface | Meta | Informational
    tl_dr: str
    impact_level: str  # Low | Medium | High | Critical
    impact_reasons: List[str]
    breaking_changes: bool
    compatibility: str  # Full | Partial | None | TBD
    migration_complexity: str  # Low | Medium | High | TBD
    affected_areas: List[str]  # fees, opcodes, consensus, rpc, wallets, bridges
    user_facing_effects: str
    required_actions: List[str]
    deadline_or_activation: str  # YYYY-MM-DD or Block # or TBD
    risk_notes: List[str]
    estimated_effort: str  # S | M | L
    dependencies: List[str]  # EIP-xxxx
    confidence: str  # High | Medium | Low
    references: Dict[str, str]
    last_checked_utc: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'chain': self.chain,
            'proposal_id': self.proposal_id,
            'title': self.title,
            'url': self.url,
            'stage': self.stage,
            'type': self.type,
            'tl_dr': self.tl_dr,
            'impact_level': self.impact_level,
            'impact_reasons': self.impact_reasons,
            'breaking_changes': self.breaking_changes,
            'compatibility': self.compatibility,
            'migration_complexity': self.migration_complexity,
            'affected_areas': self.affected_areas,
            'user_facing_effects': self.user_facing_effects,
            'required_actions': self.required_actions,
            'deadline_or_activation': self.deadline_or_activation,
            'risk_notes': self.risk_notes,
            'estimated_effort': self.estimated_effort,
            'dependencies': self.dependencies,
            'confidence': self.confidence,
            'references': self.references,
            'last_checked_utc': self.last_checked_utc
        }

class UnifiedImpactAnalyzer:
    """Unified analyzer for proposal impact using severity scoring"""
    
    def __init__(self):
        self._load_env_file()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.ai_available = bool(self.openai_api_key)
        
        print(f"Unified Impact Analyzer initialized (AI: {'enabled' if self.ai_available else 'disabled'})")
    
    def _load_env_file(self):
        """Load environment variables from .env file"""
        env_file = '.env'
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key and value:
                                os.environ[key] = value
            except Exception as e:
                print(f"Error loading .env file: {e}")
    
    def analyze_proposal(self, proposal: Dict) -> ProposalImpact:
        """Analyze a proposal and return unified impact data"""
        
        # Extract basic info
        proposal_id = proposal.get('id', 'Unknown')
        title = proposal.get('title', '')
        url = proposal.get('link', '')
        status = proposal.get('status', 'TBD')
        description = proposal.get('description', '')
        
        # Determine chain from proposal ID
        chain = self._determine_chain(proposal_id)
        
        # Use AI analysis if available, otherwise use rule-based analysis
        if self.ai_available:
            impact_data = self._analyze_with_ai(proposal_id, title, description, url, status)
        else:
            impact_data = self._analyze_with_rules(proposal_id, title, description, status)
        
        # Calculate severity score and impact level
        severity_score = self._calculate_severity_score(impact_data)
        impact_level = self._score_to_impact_level(severity_score)
        
        # Create unified impact object
        return ProposalImpact(
            chain=chain,
            proposal_id=proposal_id,
            title=title[:100],  # Truncate if too long
            url=url,
            stage=self._normalize_stage(status),
            type=impact_data.get('type', 'TBD'),
            tl_dr=impact_data.get('tl_dr', '')[:220],  # Max 220 chars
            impact_level=impact_level,
            impact_reasons=impact_data.get('impact_reasons', []),
            breaking_changes=impact_data.get('breaking_changes', False),
            compatibility=impact_data.get('compatibility', 'TBD'),
            migration_complexity=impact_data.get('migration_complexity', 'TBD'),
            affected_areas=impact_data.get('affected_areas', []),
            user_facing_effects=impact_data.get('user_facing_effects', ''),
            required_actions=impact_data.get('required_actions', []),
            deadline_or_activation=impact_data.get('deadline_or_activation', 'TBD'),
            risk_notes=impact_data.get('risk_notes', []),
            estimated_effort=impact_data.get('estimated_effort', 'TBD'),
            dependencies=impact_data.get('dependencies', []),
            confidence=impact_data.get('confidence', 'Medium'),
            references={
                'spec': url,
                'discussion': impact_data.get('discussion_url', ''),
                'client_releases': impact_data.get('client_releases', [])
            },
            last_checked_utc=datetime.utcnow().isoformat()
        )
    
    def _determine_chain(self, proposal_id: str) -> str:
        """Determine blockchain from proposal ID"""
        if proposal_id.upper().startswith('EIP'):
            return 'Ethereum'
        elif proposal_id.upper().startswith('BIP'):
            return 'Bitcoin'
        elif proposal_id.upper().startswith('TIP'):
            return 'Tron'
        elif proposal_id.upper().startswith('BEP'):
            return 'BNB Chain'
        elif proposal_id.upper().startswith('SUP'):
            return 'Solana'
        else:
            return 'Unknown'
    
    def _normalize_stage(self, status: str) -> str:
        """Normalize status to standard stages"""
        status_lower = status.lower()
        if status_lower in ['draft', 'idea']:
            return 'Draft'
        elif status_lower in ['review', 'proposed']:
            return 'Review'
        elif status_lower in ['last call', 'lastcall']:
            return 'Last Call'
        elif status_lower in ['final', 'accepted', 'active']:
            return 'Final'
        elif status_lower in ['withdrawn', 'rejected']:
            return 'Withdrawn'
        else:
            return status or 'TBD'
    
    def _analyze_with_ai(self, proposal_id: str, title: str, description: str, url: str, status: str) -> Dict:
        """Use OpenAI to analyze proposal impact"""
        
        system_prompt = """You are a blockchain release manager. Read a blockchain improvement proposal and output a STRICT JSON object matching this schema exactly:

{
  "type": "Core | Consensus | Networking | Interface | Meta | Informational",
  "tl_dr": "One sentence ≤120 chars - focus on what changes and who must act",
  "impact_reasons": ["reason1", "reason2"],
  "breaking_changes": false,
  "compatibility": "Full | Partial | None | TBD",
  "migration_complexity": "Low | Medium | High | TBD",
  "affected_areas": ["fees","opcodes","consensus","rpc","wallets","bridges"],
  "user_facing_effects": "How this affects end users",
  "required_actions": ["action1", "action2"],
  "deadline_or_activation": "YYYY-MM-DD or Block # or TBD",
  "risk_notes": ["risk1", "risk2"],
  "estimated_effort": "S | M | L",
  "dependencies": ["EIP-xxxx"],
  "confidence": "High | Medium | Low",
  "discussion_url": "",
  "client_releases": []
}

If info is missing, use "TBD"/[] and lower confidence. Keep tl_dr ≤ 220 chars. Avoid speculation. Focus on practical impact."""

        user_prompt = f"""Summarize this proposal for a one-page impact alert.

Proposal ID: {proposal_id}
Title: {title}
Status: {status}
URL: {url}
Description: {description[:2000]}

IMPORTANT: For deadline_or_activation, look for:
- Specific dates (YYYY-MM-DD)
- Block numbers (Block #12965000)
- Network upgrade names with dates (London 2021-08-05)
- Mainnet activation dates
- Hard fork schedules

Return only valid JSON matching the schema."""

        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'gpt-4o',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'temperature': 0.2,
                'max_tokens': 1500
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_content = result['choices'][0]['message']['content']
                
                # Extract JSON from response
                start_idx = ai_content.find('{')
                end_idx = ai_content.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_content = ai_content[start_idx:end_idx]
                    parsed_data = json.loads(json_content)
                    print(f"AI analysis completed for {proposal_id}")
                    return parsed_data
                else:
                    print(f"AI response not in JSON format for {proposal_id}")
                    return self._analyze_with_rules(proposal_id, title, description, status)
            else:
                print(f"OpenAI API error {response.status_code} for {proposal_id}")
                return self._analyze_with_rules(proposal_id, title, description, status)
                
        except Exception as e:
            print(f"AI analysis failed for {proposal_id}: {e}")
            return self._analyze_with_rules(proposal_id, title, description, status)
    
    def _analyze_with_rules(self, proposal_id: str, title: str, description: str, status: str) -> Dict:
        """Fallback rule-based analysis"""
        
        text = f"{title} {description}".lower()
        
        # Determine type based on keywords
        if any(word in text for word in ['consensus', 'fork', 'block', 'mining']):
            prop_type = 'Core'
        elif any(word in text for word in ['rpc', 'api', 'interface']):
            prop_type = 'Interface'
        elif any(word in text for word in ['network', 'p2p', 'peer']):
            prop_type = 'Networking'
        else:
            prop_type = 'TBD'
        
        # Detect breaking changes
        breaking = any(word in text for word in ['breaking', 'incompatible', 'fork'])
        
        # Determine affected areas
        areas = []
        if any(word in text for word in ['gas', 'fee', 'cost']):
            areas.append('fees')
        if any(word in text for word in ['opcode', 'instruction']):
            areas.append('opcodes')
        if any(word in text for word in ['consensus', 'mining', 'validator']):
            areas.append('consensus')
        if any(word in text for word in ['rpc', 'api']):
            areas.append('rpc')
        if any(word in text for word in ['wallet', 'signing']):
            areas.append('wallets')
        if any(word in text for word in ['bridge', 'layer']):
            areas.append('bridges')
        
        return {
            'type': prop_type,
            'tl_dr': f"{title[:180]}..." if len(title) > 180 else title,
            'impact_reasons': ['Technical change detected', 'Further analysis needed'],
            'breaking_changes': breaking,
            'compatibility': 'Partial' if breaking else 'TBD',
            'migration_complexity': 'High' if breaking else 'Low',
            'affected_areas': areas or ['TBD'],
            'user_facing_effects': 'Impact assessment pending',
            'required_actions': ['Review proposal details', 'Monitor for updates'],
            'deadline_or_activation': 'TBD',
            'risk_notes': ['Requires technical review'],
            'estimated_effort': 'M',
            'dependencies': [],
            'confidence': 'Low',
            'discussion_url': '',
            'client_releases': []
        }
    
    def _calculate_severity_score(self, impact_data: Dict) -> int:
        """Calculate severity score based on defined criteria"""
        
        score = 0
        
        # Breaking change (compat=None): +40
        if impact_data.get('compatibility') == 'None' or impact_data.get('breaking_changes'):
            score += 40
        
        # Consensus/hard-fork/activation block set: +30
        if impact_data.get('type') == 'Core' or 'consensus' in impact_data.get('affected_areas', []):
            score += 30
        
        # Security patch/vuln class: +25
        if any(word in str(impact_data.get('impact_reasons', [])).lower() for word in ['security', 'vulnerability', 'exploit']):
            score += 25
        
        # Economic/fee model or gas limits: +20
        if 'fees' in impact_data.get('affected_areas', []):
            score += 20
        
        # Migration complexity: 0/+10/+20
        complexity = impact_data.get('migration_complexity', 'Low')
        if complexity == 'High':
            score += 20
        elif complexity == 'Medium':
            score += 10
        
        # RPC/wallet API change: +10
        if any(area in impact_data.get('affected_areas', []) for area in ['rpc', 'wallets']):
            score += 10
        
        # Low information quality: -10
        if impact_data.get('confidence') == 'Low':
            score -= 10
        
        return max(0, score)
    
    def _score_to_impact_level(self, score: int) -> str:
        """Convert severity score to impact level"""
        if score >= 75:
            return 'Critical'
        elif score >= 50:
            return 'High'
        elif score >= 30:
            return 'Medium'
        else:
            return 'Low'

    def format_slack_message(self, impact: ProposalImpact) -> str:
        """Format as compact Slack message (max 1200 chars)"""
        
        # Title line
        emoji = {'Critical': '🚨', 'High': '⚡', 'Medium': '⚠️', 'Low': '📝'}.get(impact.impact_level, '📝')
        title = f"{emoji} {impact.chain} {impact.proposal_id} — {impact.title[:50]} · {impact.stage} · Impact: {impact.impact_level}"
        
        # Body lines
        lines = [
            f"**TL;DR:** {impact.tl_dr}",
            f"**Why it matters:** {', '.join(impact.impact_reasons[:2])}",
            f"**Changes:** {impact.type} · Breaking: {'Yes' if impact.breaking_changes else 'No'} · Compat: {impact.compatibility} · Migration: {impact.migration_complexity}",
            f"**Effect on users:** {impact.user_facing_effects[:100]}",
            f"**Do now:** 1) {impact.required_actions[0] if impact.required_actions else 'Monitor'}"
        ]
        
        if len(impact.required_actions) > 1:
            lines[-1] += f"  2) {impact.required_actions[1]}"
        
        lines.append(f"**Timeline:** {impact.deadline_or_activation} · Effort: {impact.estimated_effort} · Confidence: {impact.confidence}")
        
        # Links
        links = []
        if impact.references.get('spec'):
            links.append(f"[Spec]({impact.references['spec']})")
        if impact.references.get('discussion'):
            links.append(f"[Discussion]({impact.references['discussion']})")
        
        if links:
            lines.append(f"**Links:** {' · '.join(links)}")
        
        lines.append(f"`Checked {impact.last_checked_utc[:16]}`")
        
        # Combine and truncate if needed
        message = f"{title}\n\n" + "\n".join(lines)
        
        if len(message) > 1200:
            # Truncate and add ellipsis
            message = message[:1197] + "..."
        
        return message
    
    def format_email_subject_and_opening(self, impact: ProposalImpact) -> Tuple[str, str]:
        """Format email subject and opening line"""
        
        subject = f"[Impact: {impact.impact_level}] {impact.chain} {impact.proposal_id} — {impact.title[:50]} ({impact.stage})"
        
        top_reason = impact.impact_reasons[0] if impact.impact_reasons else "updates detected"
        
        opening = (f"{impact.proposal_id} moved to **{impact.stage}**. **{impact.impact_level}** impact due to {top_reason}. "
                  f"Breaking: {'Yes' if impact.breaking_changes else 'No'}. "
                  f"Target: {impact.deadline_or_activation}. "
                  f"Actions: {impact.required_actions[0] if impact.required_actions else 'Monitor'}")
        
        if len(impact.required_actions) > 1:
            opening += f" / {impact.required_actions[1]}"
        
        opening += "."
        
        return subject, opening