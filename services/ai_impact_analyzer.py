"""
AI-Powered Transaction Impact Analyzer
Uses AI to generate comprehensive transaction impact summaries
"""
import json
import requests
import os
from typing import Dict, List, Optional
from datetime import datetime

class AITransactionImpactAnalyzer:
    """AI-powered analyzer for detailed transaction impact analysis"""
    
    def __init__(self):
        # Try to load from .env file first
        self._load_env_file()
        
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.ai_api_available = bool(self.openai_api_key)
        self.fallback_templates = self._load_fallback_templates()
        
        if self.ai_api_available:
            print("AI-powered impact analysis enabled with OpenAI")
        else:
            print("Using fallback templates (set OPENAI_API_KEY for AI analysis)")
    
    def _load_env_file(self):
        """Load environment variables from .env file if it exists"""
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
                print("Loaded configuration from .env file")
            except Exception as e:
                print(f"Error loading .env file: {e}")
    
    def _load_fallback_templates(self) -> Dict:
        """Load fallback templates when AI is not available"""
        return {
            'gas_fee_increase': {
                'summary': 'This proposal may increase transaction costs',
                'details': [
                    'Users will pay higher gas fees per transaction',
                    'DeFi operations become more expensive',
                    'Small transactions may become uneconomical',
                    'Consider batching transactions to reduce costs'
                ],
                'user_actions': [
                    'Monitor gas prices before transacting',
                    'Use gas optimization tools',
                    'Consider Layer 2 solutions for cheaper transactions'
                ]
            },
            'gas_fee_decrease': {
                'summary': 'This proposal reduces transaction costs for users',
                'details': [
                    'Lower gas fees make transactions more affordable',
                    'Enables more frequent DeFi interactions',
                    'Makes micro-transactions economically viable',
                    'Improves overall network accessibility'
                ],
                'user_actions': [
                    'Take advantage of lower fees for regular transactions',
                    'Consider increasing DeFi activity frequency',
                    'Explore previously expensive operations'
                ]
            },
            'wallet_breaking': {
                'summary': 'This proposal requires wallet software updates',
                'details': [
                    'Existing wallets may not support new transaction format',
                    'Users must update wallet software to continue transacting',
                    'Hardware wallets may need firmware updates',
                    'Temporary service disruptions possible during transition'
                ],
                'user_actions': [
                    'Update wallet software immediately',
                    'Check hardware wallet firmware compatibility',
                    'Test transactions on testnet first',
                    'Keep backup access methods ready'
                ]
            },
            'confirmation_faster': {
                'summary': 'Transactions will confirm faster with this proposal',
                'details': [
                    'Reduced waiting time for transaction finality',
                    'Improved user experience for time-sensitive operations',
                    'Better performance for DeFi arbitrage and MEV',
                    'Enhanced scalability for high-frequency use cases'
                ],
                'user_actions': [
                    'Adjust transaction timeout settings',
                    'Update applications expecting longer confirmation times',
                    'Consider faster transaction strategies'
                ]
            },
            'network_capacity': {
                'summary': 'This proposal affects network transaction capacity',
                'details': [
                    'Changes to how many transactions the network can process',
                    'May affect congestion during high-demand periods',
                    'Could influence optimal transaction timing',
                    'Impacts overall network performance characteristics'
                ],
                'user_actions': [
                    'Monitor network congestion patterns',
                    'Adjust transaction timing strategies',
                    'Consider alternative scaling solutions'
                ]
            }
        }
    
    def generate_ai_impact_summary(self, proposal: Dict, basic_impact: Dict) -> Dict:
        """Generate AI-powered comprehensive impact summary"""
        
        proposal_id = proposal.get('id', 'Unknown')
        title = proposal.get('title', '')
        description = proposal.get('description', '')
        status = proposal.get('status', 'Unknown')
        
        # Create comprehensive prompt for AI analysis
        prompt = self._create_analysis_prompt(proposal_id, title, description, status, basic_impact)
        
        # Try AI analysis first, fallback to templates
        ai_summary = self._try_ai_analysis(prompt)
        
        if ai_summary:
            return ai_summary
        else:
            return self._generate_fallback_summary(basic_impact)
    
    def _create_analysis_prompt(self, proposal_id: str, title: str, description: str, status: str, basic_impact: Dict) -> str:
        """Create detailed prompt for AI analysis"""
        
        prompt = f"""
        Analyze the blockchain transaction impact of this proposal and provide a comprehensive summary:

        **Proposal Details:**
        - ID: {proposal_id}
        - Title: {title}
        - Description: {description}
        - Status: {status}

        **Detected Basic Impacts:**
        - Affects Transactions: {basic_impact.get('affects_transactions', False)}
        - Gas Fee Impact: {basic_impact.get('gas_fee_impact', 'none')}
        - Confirmation Time Impact: {basic_impact.get('confirmation_time_impact', 'none')}
        - Wallet Compatibility: {basic_impact.get('wallet_compatibility_impact', 'none')}
        - Transaction Format Changes: {basic_impact.get('transaction_format_changes', False)}
        - Network Capacity Impact: {basic_impact.get('network_capacity_impact', 'none')}
        - User Action Required: {basic_impact.get('user_action_required', False)}

        Please provide a detailed analysis in this JSON format:
        {{
            "executive_summary": "Brief 1-2 sentence overview of the main transaction impact",
            "detailed_impact": {{
                "cost_impact": "How this affects transaction costs for users",
                "speed_impact": "How this affects transaction speed and confirmation times", 
                "compatibility_impact": "How this affects wallet and application compatibility",
                "user_experience_impact": "How this changes the user transaction experience"
            }},
            "real_world_scenarios": [
                "Specific example of how this affects DeFi users",
                "How this impacts NFT trading",
                "Effect on regular ETH/BTC transfers",
                "Impact on enterprise blockchain usage"
            ],
            "user_action_items": [
                "Specific steps users should take",
                "Timeline for required actions",
                "Risk mitigation strategies"
            ],
            "business_implications": [
                "Impact on DApps and protocols",
                "Effect on exchange operations", 
                "Implications for wallet providers",
                "Impact on blockchain infrastructure"
            ],
            "technical_depth": {{
                "mechanism": "Technical explanation of how the change works",
                "backward_compatibility": "Compatibility with existing systems",
                "migration_complexity": "How complex is the transition"
            }},
            "timeline_considerations": {{
                "immediate_effects": "What happens immediately when implemented",
                "short_term_effects": "Effects over next 1-3 months",
                "long_term_effects": "Effects over 6-12 months"
            }},
            "risk_assessment": {{
                "high_risks": ["Critical risks users should know about"],
                "medium_risks": ["Moderate risks to consider"],
                "mitigation_strategies": ["How to reduce risks"]
            }}
        }}

        Focus on practical, actionable insights that help users understand exactly how this will affect their blockchain transactions.
        """
        
        return prompt
    
    def _try_ai_analysis(self, prompt: str) -> Optional[Dict]:
        """Try to get AI analysis using OpenAI API"""
        
        if not self.ai_api_available:
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'gpt-4o',  # Using GPT-4o for better analysis
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a blockchain expert specializing in transaction impact analysis. Provide detailed, practical insights about how blockchain proposals affect real users and businesses. Focus on actionable information and real-world implications.'
                    },
                    {
                        'role': 'user', 
                        'content': prompt
                    }
                ],
                'temperature': 0.3,  # Lower temperature for more consistent analysis
                'max_tokens': 2000
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
                
                # Try to parse as JSON
                try:
                    # Find JSON content in the response
                    start_idx = ai_content.find('{')
                    end_idx = ai_content.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx != -1:
                        json_content = ai_content[start_idx:end_idx]
                        parsed_analysis = json.loads(json_content)
                        
                        print(f"AI analysis generated successfully")
                        return parsed_analysis
                    else:
                        print(f"AI response not in JSON format, using fallback")
                        return None
                        
                except json.JSONDecodeError as e:
                    print(f"Failed to parse AI response as JSON: {e}")
                    return None
            else:
                print(f"OpenAI API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return None
    
    def _generate_fallback_summary(self, basic_impact: Dict) -> Dict:
        """Generate comprehensive summary using fallback templates"""
        
        summary = {
            "executive_summary": "",
            "detailed_impact": {
                "cost_impact": "No significant cost changes detected",
                "speed_impact": "No significant speed changes detected", 
                "compatibility_impact": "No compatibility issues detected",
                "user_experience_impact": "Minimal user experience changes"
            },
            "real_world_scenarios": [],
            "user_action_items": [],
            "business_implications": [],
            "technical_depth": {
                "mechanism": "Technical details require further analysis",
                "backward_compatibility": "Compatibility assessment pending",
                "migration_complexity": "Migration requirements to be determined"
            },
            "timeline_considerations": {
                "immediate_effects": "No immediate action required",
                "short_term_effects": "Monitor for updates",
                "long_term_effects": "Long-term impact assessment ongoing"
            },
            "risk_assessment": {
                "high_risks": [],
                "medium_risks": [],
                "mitigation_strategies": ["Stay informed about proposal updates"]
            }
        }
        
        # Build summary based on detected impacts
        impact_parts = []
        
        if basic_impact.get('gas_fee_impact') == 'decrease':
            template = self.fallback_templates['gas_fee_decrease']
            impact_parts.append("reduced transaction costs")
            summary["detailed_impact"]["cost_impact"] = template['summary']
            summary["real_world_scenarios"].extend(template['details'])
            summary["user_action_items"].extend(template['user_actions'])
            
        elif basic_impact.get('gas_fee_impact') == 'increase':
            template = self.fallback_templates['gas_fee_increase']
            impact_parts.append("increased transaction costs")
            summary["detailed_impact"]["cost_impact"] = template['summary']
            summary["real_world_scenarios"].extend(template['details'])
            summary["user_action_items"].extend(template['user_actions'])
            summary["risk_assessment"]["medium_risks"].append("Higher transaction costs may affect usage patterns")
        
        if basic_impact.get('wallet_compatibility_impact') == 'breaking':
            template = self.fallback_templates['wallet_breaking']
            impact_parts.append("wallet compatibility changes")
            summary["detailed_impact"]["compatibility_impact"] = template['summary']
            summary["real_world_scenarios"].extend(template['details'])
            summary["user_action_items"].extend(template['user_actions'])
            summary["risk_assessment"]["high_risks"].append("Wallet software must be updated to continue transacting")
            summary["business_implications"].extend([
                "Wallet providers must release updates",
                "DApps may need to update integrations",
                "Exchange systems require compatibility testing"
            ])
        
        if basic_impact.get('confirmation_time_impact') == 'faster':
            template = self.fallback_templates['confirmation_faster']
            impact_parts.append("faster transaction confirmations")
            summary["detailed_impact"]["speed_impact"] = template['summary']
            summary["real_world_scenarios"].extend(template['details'])
            summary["user_action_items"].extend(template['user_actions'])
        
        if basic_impact.get('network_capacity_impact') in ['increase', 'decrease']:
            template = self.fallback_templates['network_capacity']
            impact_parts.append("network capacity changes")
            summary["detailed_impact"]["user_experience_impact"] = template['summary']
            summary["real_world_scenarios"].extend(template['details'])
            summary["user_action_items"].extend(template['user_actions'])
        
        # Create executive summary
        if impact_parts:
            summary["executive_summary"] = f"This proposal introduces {', '.join(impact_parts)} that will affect how users interact with blockchain transactions."
        else:
            summary["executive_summary"] = "This proposal has minimal direct impact on transaction processing and user experience."
        
        # Add timeline based on status
        if basic_impact.get('user_action_required'):
            summary["timeline_considerations"]["immediate_effects"] = "Users should prepare for required wallet/software updates"
            summary["timeline_considerations"]["short_term_effects"] = "Update software and test compatibility within 1-2 weeks"
        
        # Add general business implications if not already added
        if not summary["business_implications"]:
            summary["business_implications"] = [
                "Monitor implementation progress",
                "Assess impact on existing operations",
                "Plan for any necessary updates"
            ]
        
        return summary
    
    def enhance_multiple_proposals(self, proposals_with_impact: List[Dict]) -> Dict:
        """Enhance multiple proposals with AI analysis"""
        
        enhanced_analyses = []
        
        for item in proposals_with_impact:
            basic_impact = item.get('transaction_impact', {})
            
            # Generate AI-enhanced summary
            ai_summary = self.generate_ai_impact_summary(item, basic_impact)
            
            # Add to the analysis
            enhanced_item = item.copy()
            enhanced_item['ai_transaction_analysis'] = ai_summary
            enhanced_analyses.append(enhanced_item)
        
        # Generate cross-proposal insights
        cross_proposal_insights = self._generate_cross_proposal_insights(enhanced_analyses)
        
        return {
            'enhanced_analyses': enhanced_analyses,
            'cross_proposal_insights': cross_proposal_insights,
            'summary_statistics': self._calculate_enhanced_statistics(enhanced_analyses)
        }
    
    def _generate_cross_proposal_insights(self, enhanced_analyses: List[Dict]) -> Dict:
        """Generate insights across multiple proposals"""
        
        insights = {
            'common_themes': [],
            'conflicting_changes': [],
            'cumulative_impact': '',
            'strategic_considerations': []
        }
        
        # Analyze common themes
        gas_decreases = sum(1 for a in enhanced_analyses if a.get('transaction_impact', {}).get('gas_fee_impact') == 'decrease')
        gas_increases = sum(1 for a in enhanced_analyses if a.get('transaction_impact', {}).get('gas_fee_impact') == 'increase')
        wallet_changes = sum(1 for a in enhanced_analyses if a.get('transaction_impact', {}).get('wallet_compatibility_impact') == 'breaking')
        
        if gas_decreases > 1:
            insights['common_themes'].append(f"Multiple proposals ({gas_decreases}) focus on reducing transaction costs")
        
        if wallet_changes > 1:
            insights['common_themes'].append(f"Multiple proposals ({wallet_changes}) require wallet compatibility updates")
        
        if gas_decreases > 0 and gas_increases > 0:
            insights['conflicting_changes'].append("Some proposals reduce costs while others may increase them")
        
        # Cumulative impact assessment
        if gas_decreases > gas_increases:
            insights['cumulative_impact'] = "Overall trend toward lower transaction costs"
        elif gas_increases > gas_decreases:
            insights['cumulative_impact'] = "Overall trend toward higher transaction costs"
        else:
            insights['cumulative_impact'] = "Mixed impact on transaction costs"
        
        # Strategic considerations
        if wallet_changes > 0:
            insights['strategic_considerations'].append("Coordinate wallet update rollout to minimize user disruption")
        
        if gas_decreases > 0:
            insights['strategic_considerations'].append("Leverage cost reductions for user acquisition and retention")
        
        return insights
    
    def _calculate_enhanced_statistics(self, enhanced_analyses: List[Dict]) -> Dict:
        """Calculate statistics from enhanced analyses"""
        
        total = len(enhanced_analyses)
        
        stats = {
            'total_proposals': total,
            'high_user_impact': 0,
            'wallet_updates_required': 0,
            'cost_reducing': 0,
            'cost_increasing': 0,
            'immediate_action_required': 0
        }
        
        for analysis in enhanced_analyses:
            tx_impact = analysis.get('transaction_impact', {})
            ai_analysis = analysis.get('ai_transaction_analysis', {})
            
            if tx_impact.get('user_impact_level') in ['high', 'critical']:
                stats['high_user_impact'] += 1
            
            if tx_impact.get('wallet_compatibility_impact') == 'breaking':
                stats['wallet_updates_required'] += 1
            
            if tx_impact.get('gas_fee_impact') == 'decrease':
                stats['cost_reducing'] += 1
            elif tx_impact.get('gas_fee_impact') == 'increase':
                stats['cost_increasing'] += 1
            
            if tx_impact.get('user_action_required'):
                stats['immediate_action_required'] += 1
        
        return stats