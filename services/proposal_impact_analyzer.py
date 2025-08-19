"""
Proposal Impact Analyzer
Analyzes blockchain proposals for development and product impact
"""
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class ProposalImpactAnalyzer:
    """Analyzes proposals for development and product impact"""
    
    def __init__(self):
        # Transaction impact keywords
        self.transaction_impact_keywords = {
            'gas_fees': [
                'gas', 'fee', 'cost', 'price', 'optimization', 'efficiency',
                'cheaper', 'expensive', 'reduction', 'increase'
            ],
            'transaction_format': [
                'transaction', 'tx', 'format', 'structure', 'encoding',
                'serialization', 'signature', 'hash'
            ],
            'confirmation_time': [
                'confirmation', 'finality', 'block time', 'latency',
                'speed', 'faster', 'slower', 'delay'
            ],
            'wallet_compatibility': [
                'wallet', 'metamask', 'hardware wallet', 'signing',
                'interface', 'compatibility', 'breaking change'
            ],
            'network_capacity': [
                'throughput', 'tps', 'scaling', 'capacity', 'congestion',
                'bandwidth', 'performance'
            ]
        }
        
        # Keywords that indicate different types of impact
        self.impact_keywords = {
            'development': [
                'api', 'interface', 'sdk', 'library', 'tool', 'framework',
                'compiler', 'testing', 'debug', 'development', 'code',
                'smart contract', 'solidity', 'vyper', 'runtime', 'vm'
            ],
            'performance': [
                'gas', 'fee', 'optimization', 'efficiency', 'speed', 'throughput',
                'latency', 'performance', 'scaling', 'tps', 'bandwidth'
            ],
            'security': [
                'security', 'vulnerability', 'attack', 'protection', 'encryption',
                'cryptography', 'audit', 'verification', 'proof', 'validation'
            ],
            'compatibility': [
                'backwards compatible', 'breaking change', 'migration', 'upgrade',
                'compatibility', 'legacy', 'version', 'deprecated'
            ],
            'user_experience': [
                'ux', 'ui', 'user', 'interface', 'wallet', 'transaction', 'dapp',
                'frontend', 'usability', 'experience', 'interaction'
            ],
            'protocol': [
                'consensus', 'fork', 'block', 'mining', 'staking', 'validator',
                'network', 'protocol', 'chain', 'node', 'peer'
            ],
            'defi': [
                'defi', 'lending', 'borrowing', 'yield', 'liquidity', 'swap',
                'exchange', 'trading', 'market', 'token', 'erc20', 'erc721'
            ],
            'governance': [
                'governance', 'voting', 'proposal', 'dao', 'community',
                'decision', 'upgrade', 'parameter', 'treasury'
            ]
        }
        
        # Impact severity levels
        self.severity_indicators = {
            'critical': [
                'breaking change', 'hard fork', 'critical', 'urgent', 'security',
                'vulnerability', 'exploit', 'emergency'
            ],
            'major': [
                'significant', 'major', 'important', 'substantial', 'enhancement',
                'improvement', 'optimization', 'upgrade'
            ],
            'minor': [
                'minor', 'small', 'fix', 'patch', 'cleanup', 'documentation',
                'clarification', 'typo'
            ]
        }

    def analyze_proposal(self, proposal: Dict) -> Dict:
        """Analyze a single proposal for impact"""
        
        proposal_id = proposal.get('id', 'Unknown')
        title = proposal.get('title', '').lower()
        description = proposal.get('description', '').lower()
        status = proposal.get('status', 'Unknown')
        
        # Combine text for analysis
        full_text = f"{title} {description}"
        
        # Determine proposal type and impact areas
        impact_areas = self._identify_impact_areas(full_text)
        severity = self._determine_severity(full_text)
        development_impact = self._analyze_development_impact(full_text, proposal_id)
        product_impact = self._analyze_product_impact(full_text, proposal_id)
        timeline_impact = self._estimate_timeline_impact(status, severity)
        
        # Add transaction impact analysis
        transaction_impact = self._analyze_transaction_impact(full_text, proposal_id, status)
        
        return {
            'proposal_id': proposal_id,
            'title': proposal.get('title', 'No title'),
            'status': status,
            'impact_areas': impact_areas,
            'severity': severity,
            'development_impact': development_impact,
            'product_impact': product_impact,
            'transaction_impact': transaction_impact,
            'timeline_impact': timeline_impact,
            'priority_score': self._calculate_priority_score(impact_areas, severity),
            'recommended_actions': self._generate_recommendations(impact_areas, severity, status)
        }

    def _identify_impact_areas(self, text: str) -> List[str]:
        """Identify which areas this proposal impacts"""
        identified_areas = []
        
        for area, keywords in self.impact_keywords.items():
            if any(keyword in text for keyword in keywords):
                identified_areas.append(area)
        
        return identified_areas or ['general']

    def _determine_severity(self, text: str) -> str:
        """Determine the severity level of the proposal"""
        
        for severity, indicators in self.severity_indicators.items():
            if any(indicator in text for indicator in indicators):
                return severity
        
        return 'minor'

    def _analyze_development_impact(self, text: str, proposal_id: str) -> Dict:
        """Analyze impact on development processes"""
        
        impact = {
            'breaking_changes': 'breaking change' in text or 'breaking' in text,
            'api_changes': any(word in text for word in ['api', 'interface', 'method']),
            'tooling_updates': any(word in text for word in ['tool', 'compiler', 'framework']),
            'testing_required': any(word in text for word in ['test', 'testing', 'validation']),
            'migration_needed': any(word in text for word in ['migration', 'upgrade', 'migrate']),
            'documentation_updates': any(word in text for word in ['documentation', 'spec', 'standard']),
            'estimated_effort': self._estimate_development_effort(text),
            'affected_components': self._identify_affected_components(text)
        }
        
        # Generate actionable insights
        impact['action_items'] = []
        
        if impact['breaking_changes']:
            impact['action_items'].append("🚨 Review for breaking changes - plan migration strategy")
        
        if impact['api_changes']:
            impact['action_items'].append("🔧 Update API documentation and client libraries")
        
        if impact['testing_required']:
            impact['action_items'].append("🧪 Develop comprehensive test cases")
        
        if impact['migration_needed']:
            impact['action_items'].append("📋 Create migration guide and timeline")
        
        return impact

    def _analyze_product_impact(self, text: str, proposal_id: str) -> Dict:
        """Analyze impact on product features and user experience"""
        
        impact = {
            'user_facing_changes': any(word in text for word in ['user', 'ux', 'ui', 'interface']),
            'performance_improvement': any(word in text for word in ['performance', 'gas', 'efficiency', 'optimization']),
            'new_features': any(word in text for word in ['new', 'feature', 'functionality', 'capability']),
            'security_enhancement': any(word in text for word in ['security', 'protection', 'vulnerability']),
            'cost_impact': any(word in text for word in ['cost', 'fee', 'gas', 'price']),
            'compatibility_impact': any(word in text for word in ['compatible', 'compatibility', 'support']),
            'market_opportunity': self._assess_market_opportunity(text),
            'competitive_advantage': self._assess_competitive_impact(text)
        }
        
        # Generate business insights
        impact['business_implications'] = []
        
        if impact['performance_improvement']:
            impact['business_implications'].append("💰 Potential cost savings from improved efficiency")
        
        if impact['new_features']:
            impact['business_implications'].append("🚀 New product capabilities - assess market demand")
        
        if impact['security_enhancement']:
            impact['business_implications'].append("🛡️ Enhanced security posture - reduces risk")
        
        if impact['user_facing_changes']:
            impact['business_implications'].append("👥 User experience changes - plan communication strategy")
        
        return impact

    def _analyze_transaction_impact(self, text: str, proposal_id: str, status: str) -> Dict:
        """Analyze how this proposal affects blockchain transactions"""
        
        impact = {
            'affects_transactions': False,
            'gas_fee_impact': 'none',  # 'increase', 'decrease', 'none'
            'confirmation_time_impact': 'none',  # 'faster', 'slower', 'none'
            'wallet_compatibility_impact': 'none',  # 'breaking', 'compatible', 'none'
            'transaction_format_changes': False,
            'network_capacity_impact': 'none',  # 'increase', 'decrease', 'none'
            'user_action_required': False,
            'summary': '',
            'user_impact_level': 'low'  # 'critical', 'high', 'medium', 'low', 'none'
        }
        
        # Check each transaction impact area
        transaction_affected = False
        
        # Gas fee impact
        if any(keyword in text for keyword in self.transaction_impact_keywords['gas_fees']):
            transaction_affected = True
            if any(word in text for word in ['reduction', 'reduces', 'cheaper', 'optimization', 'efficiency', 'lower', 'decrease', 'save', 'saving', 'less']):
                impact['gas_fee_impact'] = 'decrease'
            elif any(word in text for word in ['increase', 'expensive', 'higher', 'more', 'raise', 'raising']):
                impact['gas_fee_impact'] = 'increase'
        
        # Confirmation time impact
        if any(keyword in text for keyword in self.transaction_impact_keywords['confirmation_time']):
            transaction_affected = True
            if any(word in text for word in ['faster', 'speed', 'quick', 'immediate']):
                impact['confirmation_time_impact'] = 'faster'
            elif any(word in text for word in ['slower', 'delay', 'longer']):
                impact['confirmation_time_impact'] = 'slower'
        
        # Wallet compatibility
        if any(keyword in text for keyword in self.transaction_impact_keywords['wallet_compatibility']):
            transaction_affected = True
            if any(word in text for word in ['breaking change', 'incompatible', 'breaking']):
                impact['wallet_compatibility_impact'] = 'breaking'
                impact['user_action_required'] = True
            else:
                impact['wallet_compatibility_impact'] = 'compatible'
        
        # Transaction format changes
        if any(keyword in text for keyword in self.transaction_impact_keywords['transaction_format']):
            transaction_affected = True
            impact['transaction_format_changes'] = True
            if any(word in text for word in ['breaking', 'incompatible', 'new format']):
                impact['user_action_required'] = True
        
        # Network capacity impact
        if any(keyword in text for keyword in self.transaction_impact_keywords['network_capacity']):
            transaction_affected = True
            if any(word in text for word in ['scaling', 'increase', 'more', 'higher', 'improvement']):
                impact['network_capacity_impact'] = 'increase'
            elif any(word in text for word in ['decrease', 'less', 'lower', 'reduction']):
                impact['network_capacity_impact'] = 'decrease'
        
        impact['affects_transactions'] = transaction_affected
        
        # Generate user-friendly summary and impact level
        if transaction_affected:
            impact['summary'], impact['user_impact_level'] = self._generate_transaction_summary(impact, status)
        else:
            impact['summary'] = "No direct impact on blockchain transactions"
            impact['user_impact_level'] = 'none'
        
        return impact

    def _generate_transaction_summary(self, impact: Dict, status: str) -> Tuple[str, str]:
        """Generate a user-friendly transaction impact summary"""
        
        summary_parts = []
        impact_level = 'low'
        
        # Gas fee impact
        if impact['gas_fee_impact'] == 'decrease':
            summary_parts.append("💰 Lower transaction fees")
            impact_level = 'medium'
        elif impact['gas_fee_impact'] == 'increase':
            summary_parts.append("💸 Higher transaction fees")
            impact_level = 'high'
        
        # Confirmation time impact
        if impact['confirmation_time_impact'] == 'faster':
            summary_parts.append("⚡ Faster transaction confirmations")
            impact_level = max(impact_level, 'medium', key=['none', 'low', 'medium', 'high', 'critical'].index)
        elif impact['confirmation_time_impact'] == 'slower':
            summary_parts.append("🐌 Slower transaction confirmations")
            impact_level = 'high'
        
        # Wallet compatibility
        if impact['wallet_compatibility_impact'] == 'breaking':
            summary_parts.append("⚠️ Wallet updates required")
            impact_level = 'critical'
        elif impact['wallet_compatibility_impact'] == 'compatible':
            summary_parts.append("✅ Wallet compatible")
        
        # Transaction format changes
        if impact['transaction_format_changes']:
            if impact['user_action_required']:
                summary_parts.append("🔄 Transaction format changes - action required")
                impact_level = 'critical'
            else:
                summary_parts.append("📝 Transaction format updates")
                impact_level = max(impact_level, 'medium', key=['none', 'low', 'medium', 'high', 'critical'].index)
        
        # Network capacity
        if impact['network_capacity_impact'] == 'increase':
            summary_parts.append("📈 Network can handle more transactions")
            impact_level = max(impact_level, 'medium', key=['none', 'low', 'medium', 'high', 'critical'].index)
        elif impact['network_capacity_impact'] == 'decrease':
            summary_parts.append("📉 Network capacity may be reduced")
            impact_level = 'high'
        
        # User action required
        if impact['user_action_required']:
            summary_parts.append("👤 User action required")
            impact_level = 'critical'
        
        # Create final summary
        if not summary_parts:
            summary = "Minor technical changes with minimal transaction impact"
        else:
            summary = " | ".join(summary_parts)
        
        # Add status context
        if status == 'Final':
            summary += " (Implemented - take action now)"
            impact_level = max(impact_level, 'high', key=['none', 'low', 'medium', 'high', 'critical'].index)
        elif status == 'Last Call':
            summary += " (Finalizing soon - prepare for changes)"
            impact_level = max(impact_level, 'medium', key=['none', 'low', 'medium', 'high', 'critical'].index)
        
        return summary, impact_level

    def _estimate_development_effort(self, text: str) -> str:
        """Estimate development effort required"""
        
        high_effort_indicators = ['major', 'significant', 'breaking', 'rewrite', 'overhaul']
        medium_effort_indicators = ['moderate', 'update', 'enhance', 'improve']
        
        if any(indicator in text for indicator in high_effort_indicators):
            return "High (2-4 weeks)"
        elif any(indicator in text for indicator in medium_effort_indicators):
            return "Medium (3-7 days)"
        else:
            return "Low (1-2 days)"

    def _identify_affected_components(self, text: str) -> List[str]:
        """Identify which system components are affected"""
        
        components = []
        component_keywords = {
            'Smart Contracts': ['contract', 'solidity', 'vyper', 'evm'],
            'API Layer': ['api', 'endpoint', 'interface', 'service'],
            'Frontend': ['ui', 'frontend', 'web', 'dapp'],
            'Backend': ['backend', 'server', 'database', 'node'],
            'Infrastructure': ['network', 'protocol', 'consensus', 'node'],
            'SDK/Libraries': ['sdk', 'library', 'framework', 'tool'],
            'Documentation': ['docs', 'documentation', 'guide', 'spec']
        }
        
        for component, keywords in component_keywords.items():
            if any(keyword in text for keyword in keywords):
                components.append(component)
        
        return components or ['General']

    def _assess_market_opportunity(self, text: str) -> str:
        """Assess market opportunity from this proposal"""
        
        high_opportunity = ['defi', 'scaling', 'efficiency', 'new market', 'innovation']
        medium_opportunity = ['improvement', 'enhancement', 'optimization']
        
        if any(keyword in text for keyword in high_opportunity):
            return "High - significant market potential"
        elif any(keyword in text for keyword in medium_opportunity):
            return "Medium - incremental improvement"
        else:
            return "Low - maintenance/technical change"

    def _assess_competitive_impact(self, text: str) -> str:
        """Assess competitive advantage potential"""
        
        if any(word in text for word in ['first', 'innovative', 'breakthrough', 'revolutionary']):
            return "High - potential first-mover advantage"
        elif any(word in text for word in ['improvement', 'better', 'faster', 'cheaper']):
            return "Medium - competitive improvement"
        else:
            return "Low - parity/maintenance"

    def _estimate_timeline_impact(self, status: str, severity: str) -> Dict:
        """Estimate timeline for implementation"""
        
        urgency_map = {
            'critical': 'Immediate action required',
            'major': 'Plan for next sprint/quarter',
            'minor': 'Include in regular roadmap'
        }
        
        status_timeline = {
            'Draft': 'Monitor - may change significantly',
            'Review': 'Plan ahead - likely to be finalized',
            'Last Call': 'Prepare for implementation - finalizing soon',
            'Final': 'Implement now - standard is finalized',
            'Withdrawn': 'No action needed'
        }
        
        return {
            'urgency': urgency_map.get(severity, 'Low priority'),
            'status_guidance': status_timeline.get(status, 'Monitor for updates'),
            'recommended_timeline': self._get_recommended_timeline(severity, status)
        }

    def _get_recommended_timeline(self, severity: str, status: str) -> str:
        """Get recommended implementation timeline"""
        
        if status in ['Final', 'Last Call'] and severity == 'critical':
            return "Start immediately - within 1 week"
        elif status == 'Final' and severity == 'major':
            return "Plan for next sprint - within 2-4 weeks"
        elif status in ['Review', 'Last Call']:
            return "Prepare for implementation - 1-2 months"
        elif status == 'Draft':
            return "Monitor and plan - 3-6 months"
        else:
            return "Standard roadmap timeline"

    def _calculate_priority_score(self, impact_areas: List[str], severity: str) -> int:
        """Calculate a priority score (1-10)"""
        
        base_score = {
            'critical': 8,
            'major': 5,
            'minor': 2
        }.get(severity, 2)
        
        # Add points for important impact areas
        high_impact_areas = ['security', 'performance', 'development', 'defi']
        area_bonus = len([area for area in impact_areas if area in high_impact_areas])
        
        return min(10, base_score + area_bonus)

    def _generate_recommendations(self, impact_areas: List[str], severity: str, status: str) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        if severity == 'critical':
            recommendations.append("🚨 High priority - assign dedicated team")
        
        if 'security' in impact_areas:
            recommendations.append("🔒 Conduct security review and audit")
        
        if 'development' in impact_areas:
            recommendations.append("👨‍💻 Involve development team in planning")
        
        if 'compatibility' in impact_areas:
            recommendations.append("🔄 Test backwards compatibility thoroughly")
        
        if 'defi' in impact_areas:
            recommendations.append("💱 Assess impact on DeFi integrations")
        
        if status == 'Draft':
            recommendations.append("👀 Monitor for changes - still in development")
        elif status == 'Final':
            recommendations.append("✅ Begin implementation planning")
        
        return recommendations or ["📋 Monitor for updates and assess impact"]

    def analyze_multiple_proposals(self, proposals: List[Dict]) -> Dict:
        """Analyze multiple proposals and provide summary insights"""
        
        analyses = [self.analyze_proposal(proposal) for proposal in proposals]
        
        # Group by priority and impact
        high_priority = [a for a in analyses if a['priority_score'] >= 7]
        medium_priority = [a for a in analyses if 4 <= a['priority_score'] < 7]
        low_priority = [a for a in analyses if a['priority_score'] < 4]
        
        # Identify common themes
        all_impact_areas = []
        for analysis in analyses:
            all_impact_areas.extend(analysis['impact_areas'])
        
        impact_summary = {}
        for area in set(all_impact_areas):
            impact_summary[area] = all_impact_areas.count(area)
        
        return {
            'total_proposals': len(proposals),
            'analyses': analyses,
            'priority_breakdown': {
                'high': len(high_priority),
                'medium': len(medium_priority),
                'low': len(low_priority)
            },
            'impact_areas_summary': impact_summary,
            'critical_proposals': [a for a in analyses if a['severity'] == 'critical'],
            'recommended_immediate_actions': self._get_immediate_actions(high_priority),
            'strategic_insights': self._generate_strategic_insights(analyses)
        }

    def _get_immediate_actions(self, high_priority_analyses: List[Dict]) -> List[str]:
        """Get immediate actions needed for high priority proposals"""
        
        actions = set()
        
        for analysis in high_priority_analyses:
            actions.update(analysis['development_impact']['action_items'])
            actions.update(analysis['recommended_actions'])
        
        return list(actions)

    def _generate_strategic_insights(self, analyses: List[Dict]) -> List[str]:
        """Generate strategic insights from all proposals"""
        
        insights = []
        
        # Count by impact area
        area_counts = {}
        for analysis in analyses:
            for area in analysis['impact_areas']:
                area_counts[area] = area_counts.get(area, 0) + 1
        
        # Generate insights based on patterns
        if area_counts.get('security', 0) > 1:
            insights.append("🔒 Multiple security-related proposals - consider comprehensive security review")
        
        if area_counts.get('performance', 0) > 1:
            insights.append("⚡ Performance theme emerging - opportunity for optimization initiative")
        
        if area_counts.get('defi', 0) > 1:
            insights.append("🏦 DeFi evolution accelerating - assess competitive positioning")
        
        if area_counts.get('development', 0) > 2:
            insights.append("👨‍💻 Developer tooling changes - plan developer experience improvements")
        
        return insights or ["📈 Regular proposal monitoring recommended"]