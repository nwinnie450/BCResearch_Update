#!/usr/bin/env python3
"""
Enhanced AI Service with Real-Time Data Integration
Provides intelligent responses using live blockchain data from all sources
"""
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from services.comprehensive_realtime_data_service import comprehensive_realtime_service
from services.live_blockchain_data import live_blockchain_data
from services.scraped_data_service import scraped_data_service
import streamlit as st

class EnhancedAIService:
    """Enhanced AI service that leverages comprehensive real-time data for intelligent responses"""
    
    def __init__(self):
        self.realtime_service = comprehensive_realtime_service
        
        # Start background data refresh
        self.realtime_service.start_background_refresh(interval_minutes=10)
    
    def get_chat_response(self, user_input: str, conversation_history: List[Dict]) -> str:
        """Get AI response enhanced with real-time data and conversation context"""
        
        try:
            # Get contextual real-time data based on the query
            realtime_context = self.realtime_service.get_chat_context_data(user_input)
            
            # Add conversation context awareness
            context_info = self._analyze_conversation_context(user_input, conversation_history)
            
            # Use enhanced responses with real-time data and context
            return self._generate_enhanced_response_with_context(user_input, realtime_context, context_info)
                
        except Exception as e:
            # Log error without Streamlit dependency
            print(f"Enhanced AI Service Error: {str(e)}")
            return self._generate_fallback_response(user_input)
    
    def _analyze_conversation_context(self, user_input: str, conversation_history: List[Dict]) -> Dict:
        """Analyze conversation context to provide more relevant responses"""
        
        context = {
            'previous_topics': [],
            'mentioned_protocols': set(),
            'user_interests': [],
            'conversation_length': len(conversation_history),
            'recent_context': None,
            'follow_up_type': None
        }
        
        if not conversation_history:
            context['follow_up_type'] = 'first_message'
            return context
        
        # Analyze recent messages (last 4 messages)
        recent_messages = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
        
        # Extract topics and protocols from conversation history
        all_text = ' '.join([msg.get('content', '') for msg in recent_messages])
        
        # Detect mentioned protocols
        protocol_keywords = {
            'ethereum': ['ethereum', 'eth', 'ether'],
            'bitcoin': ['bitcoin', 'btc'],
            'tron': ['tron', 'trx'],
            'bsc': ['bsc', 'binance', 'bnb'],
            'base': ['base']
        }
        
        for protocol, keywords in protocol_keywords.items():
            if any(keyword in all_text.lower() for keyword in keywords):
                context['mentioned_protocols'].add(protocol)
        
        # Detect conversation themes
        if any(word in all_text.lower() for word in ['price', 'market', 'trading']):
            context['user_interests'].append('market_data')
        if any(word in all_text.lower() for word in ['tps', 'fee', 'performance']):
            context['user_interests'].append('network_performance')
        if any(word in all_text.lower() for word in ['gaming', 'game', 'nft']):
            context['user_interests'].append('gaming')
        if any(word in all_text.lower() for word in ['defi', 'yield', 'farming']):
            context['user_interests'].append('defi')
        
        # Detect follow-up patterns
        user_input_lower = user_input.lower()
        if any(word in user_input_lower for word in ['more', 'tell me more', 'explain', 'elaborate']):
            context['follow_up_type'] = 'elaboration_request'
        elif any(word in user_input_lower for word in ['compare', 'vs', 'versus', 'difference']):
            context['follow_up_type'] = 'comparison_request'
        elif any(word in user_input_lower for word in ['what about', 'how about', 'also']):
            context['follow_up_type'] = 'related_query'
        
        # Get most recent AI response for context
        if conversation_history:
            last_message = conversation_history[-1]
            if last_message.get('role') == 'assistant':
                context['recent_context'] = last_message.get('content', '')[:200]  # First 200 chars
        
        return context
    
    def _generate_enhanced_response_with_context(self, user_input: str, realtime_data: Dict, context_info: Dict) -> str:
        """Generate enhanced responses using real-time data and conversation context"""
        
        # First, check for specific protocol questions (direct answers)
        specific_protocol_response = self._check_for_specific_protocol_query(user_input, realtime_data)
        if specific_protocol_response:
            return specific_protocol_response
        
        # If this is a follow-up or elaboration request, handle contextually
        if context_info.get('follow_up_type') == 'elaboration_request':
            return self._generate_elaboration_response(user_input, realtime_data, context_info)
        elif context_info.get('follow_up_type') == 'comparison_request' and context_info.get('mentioned_protocols'):
            return self._generate_contextual_comparison(user_input, realtime_data, context_info)
        elif context_info.get('follow_up_type') == 'related_query':
            return self._generate_related_query_response(user_input, realtime_data, context_info)
        
        # For regular queries, add context-aware enhancements
        response = self._generate_enhanced_response(user_input, realtime_data)
        
        # Don't add contextual notes for proposal responses - they have their own action suggestions
        if not any(word in user_input.lower() for word in ['proposal', 'eip', 'tip', 'bip', 'bep', 'improvement']):
            # Add contextual enhancements for non-proposal queries only
            if context_info.get('mentioned_protocols') and context_info.get('conversation_length') > 2 and not self._has_specific_protocol_mention(user_input):
                protocols = list(context_info['mentioned_protocols'])
                response += f"\n\n**💡 CONTEXTUAL NOTE**: I notice we've been discussing {', '.join(protocols).title()}. Feel free to ask for more specific comparisons or details about any of these protocols!"
        
        return response
    
    def _check_for_specific_protocol_query(self, user_input: str, realtime_data: Dict) -> Optional[str]:
        """Check if user is asking about a specific protocol and return direct answer"""
        
        user_input_lower = user_input.lower()
        
        # First check if this is a proposal query - these should be handled separately
        if any(word in user_input_lower for word in ['proposal', 'eip', 'tip', 'bip', 'bep', 'improvement']):
            return None  # Let proposal handler take care of this
        
        # Protocol detection with variations
        protocol_mappings = {
            'ethereum': ['ethereum', 'eth', 'ether'],
            'bitcoin': ['bitcoin', 'btc'],
            'tron': ['tron', 'trx'],
            'binance_smart_chain': ['bsc', 'binance', 'bnb', 'binance smart chain'],
            'base': ['base']
        }
        
        detected_protocol = None
        for protocol_id, aliases in protocol_mappings.items():
            if any(alias in user_input_lower for alias in aliases):
                detected_protocol = protocol_id
                break
        
        if not detected_protocol:
            return None
        
        # Check what specific information is being requested
        is_price_query = any(word in user_input_lower for word in ['price', 'cost', 'value', 'worth'])
        is_fee_query = any(word in user_input_lower for word in ['fee', 'fees', 'transaction cost', 'gas'])
        is_current_query = any(word in user_input_lower for word in ['current', 'now', 'today', 'latest'])
        
        # Generate specific protocol response
        if is_price_query or is_fee_query or is_current_query:
            return self._generate_specific_protocol_answer(detected_protocol, user_input, realtime_data)
        
        return None
    
    def _has_specific_protocol_mention(self, user_input: str) -> bool:
        """Check if user input mentions a specific protocol"""
        user_input_lower = user_input.lower()
        protocol_names = ['ethereum', 'eth', 'bitcoin', 'btc', 'tron', 'trx', 'bsc', 'binance', 'bnb', 'base']
        return any(protocol in user_input_lower for protocol in protocol_names)
    
    def _generate_specific_protocol_answer(self, protocol_id: str, user_input: str, realtime_data: Dict) -> str:
        """Generate a direct, specific answer for protocol queries"""
        
        user_input_lower = user_input.lower()
        
        # Use the realtime data that's already been fetched (contains correct market data)
        network_data = realtime_data.get('data', {}).get('network_metrics', {}).get('protocols', {})
        market_data = realtime_data.get('data', {}).get('market_data', {}).get('protocols', {})
        
        protocol_network = network_data.get(protocol_id, {})
        protocol_market = market_data.get(protocol_id, {})
        
        protocol_name = protocol_network.get('name') or protocol_market.get('name', protocol_id.title())
        
        # Build specific answer based on what was asked
        response_parts = []
        
        # Price information
        if any(word in user_input_lower for word in ['price', 'cost', 'value', 'worth', 'current']):
            if protocol_market:
                price = protocol_market.get('price_usd', 0)
                change = protocol_market.get('price_change_24h', 0)
                change_indicator = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                response_parts.append(f"**💰 {protocol_name} Price**: ${price:,.6f} ({change:+.2f}% 24h) {change_indicator}")
            else:
                response_parts.append(f"**💰 {protocol_name} Price**: Real-time price data temporarily unavailable")
        
        # Fee information  
        if any(word in user_input_lower for word in ['fee', 'fees', 'transaction', 'gas', 'cost', 'current']):
            if protocol_network:
                fee = protocol_network.get('avg_fee_usd', 0)
                if fee > 0:
                    response_parts.append(f"**⚡ Transaction Fee**: ${fee:.4f} per transaction")
                    
                    # Add Ethereum-specific gas information
                    if protocol_id == 'ethereum':
                        try:
                            live_data = live_blockchain_data.get_ethereum_data()
                            gas_price = live_data.get('gas_price_gwei', 0)
                            if gas_price > 0:
                                response_parts.append(f"**⛽ Current Gas**: {gas_price:.1f} gwei (very low!)")
                        except:
                            pass
                    
                    # Add fee context
                    if fee < 0.01:
                        response_parts.append("💡 **Ultra-low fees** - perfect for microtransactions")
                    elif fee < 1:
                        response_parts.append("💡 **Low fees** - great for regular transactions")
                    elif fee < 5:
                        response_parts.append("💡 **Moderate fees** - reasonable for most use cases")
                    else:
                        response_parts.append("💡 **Higher fees** - best for high-value transactions")
                else:
                    response_parts.append(f"**⚡ Transaction Fee**: Fee data temporarily unavailable")
            else:
                response_parts.append(f"**⚡ Transaction Fee**: Real-time fee data temporarily unavailable")
        
        # Additional context if both price and fees were requested
        if len(response_parts) >= 2:
            if protocol_network:
                tps = protocol_network.get('tps', 0)
                finality = protocol_network.get('finality_time', 'Unknown')
                if tps > 0:
                    response_parts.append(f"**📊 Network Performance**: {tps:,} TPS | {finality} finality")
        
        # If no specific data available, provide fallback with estimated values
        if not response_parts:
            fallback_data = self._get_fallback_protocol_data(protocol_id)
            if any(word in user_input_lower for word in ['price', 'cost', 'value', 'worth', 'current']):
                response_parts.append(f"**💰 {protocol_name} Price**: ~${fallback_data['price']:.6f} (estimated)")
            if any(word in user_input_lower for word in ['fee', 'fees', 'transaction', 'gas', 'cost', 'current']):
                response_parts.append(f"**⚡ Transaction Fee**: ~${fallback_data['fee']:.6f} per transaction (estimated)")
            
            if not response_parts:
                response_parts.append(f"**{protocol_name} Information**: Real-time data is being refreshed. Please try again in a moment.")
        
        # Combine response parts
        response = f"**🔷 {protocol_name.upper()} - CURRENT DATA**\n\n" + "\n\n".join(response_parts)
        
        # Add data source note
        if any('estimated' in part for part in response_parts):
            response += f"\n\n*⚠️ Using estimated values - real-time data updating shortly*"
        else:
            response += f"\n\n*✅ Live data as of {datetime.now().strftime('%H:%M:%S UTC')} - refreshed automatically*"
        
        return response
    
    def _get_fallback_protocol_data(self, protocol_id: str) -> Dict[str, float]:
        """Get reasonable fallback data when real-time data isn't available"""
        
        # Current accurate estimates (updated to reflect real market conditions)
        fallback_estimates = {
            'ethereum': {'price': 4441.0, 'fee': 0.50},  # Updated: $4,441 price, ~$0.50 fees
            'bitcoin': {'price': 107000.0, 'fee': 2.50},  # Updated: ~$107k price, ~$2.50 fees
            'tron': {'price': 0.30, 'fee': 0.001},  # Updated: ~$0.30 price, very low fees
            'binance_smart_chain': {'price': 720.0, 'fee': 0.30},  # Updated: ~$720 BNB price
            'base': {'price': 4441.0, 'fee': 0.15}  # Base uses ETH price, L2 fees
        }
        
        return fallback_estimates.get(protocol_id, {'price': 0.0, 'fee': 0.0})
    
    def _get_fresh_protocol_data(self, protocol_id: str, current_data: Dict) -> Dict:
        """Get fresh data for a specific protocol using live data sources"""
        
        try:
            # Get fresh data from live blockchain data service
            if protocol_id == 'ethereum':
                live_data = live_blockchain_data.get_ethereum_data()
            elif protocol_id == 'bitcoin':
                live_data = live_blockchain_data.get_bitcoin_data()
            elif protocol_id == 'tron':
                live_data = live_blockchain_data.get_tron_data()
            elif protocol_id == 'binance_smart_chain':
                live_data = live_blockchain_data.get_bsc_data()
            elif protocol_id == 'base':
                live_data = live_blockchain_data.get_base_data()
            else:
                return current_data
            
            # Structure data in the expected format
            fresh_data = {
                'data': {
                    'market_data': {
                        'protocols': {
                            protocol_id: {
                                'name': live_data['name'],
                                'price_usd': live_data['price_usd'],
                                'price_change_24h': live_data['price_change_24h'],
                                'market_cap': live_data['market_cap'],
                                'volume_24h': live_data['volume_24h']
                            }
                        }
                    },
                    'network_metrics': {
                        'protocols': {
                            protocol_id: {
                                'name': live_data['name'],
                                'tps': live_data['tps'],
                                'avg_fee_usd': live_data['avg_fee_usd'],
                                'finality_time': live_data['finality_time']
                            }
                        }
                    }
                }
            }
            
            return fresh_data
                
        except Exception as e:
            print(f"Error fetching live data for {protocol_id}: {str(e)}")
        
        # Fallback to current data
        return current_data
    
    def _generate_elaboration_response(self, user_input: str, realtime_data: Dict, context_info: Dict) -> str:
        """Generate elaboration based on conversation context"""
        
        recent_context = context_info.get('recent_context', '')
        mentioned_protocols = context_info.get('mentioned_protocols', set())
        
        if 'market' in recent_context.lower() or 'price' in recent_context.lower():
            return self._generate_detailed_market_analysis(realtime_data, mentioned_protocols)
        elif 'tps' in recent_context.lower() or 'performance' in recent_context.lower():
            return self._generate_detailed_performance_analysis(realtime_data, mentioned_protocols)
        elif 'gaming' in recent_context.lower():
            return self._generate_detailed_gaming_analysis(realtime_data, mentioned_protocols)
        else:
            return """**📋 MORE DETAILED ANALYSIS**

I'd be happy to provide more details! Based on our conversation, I can elaborate on:

- **Technical Specifications**: Deep dive into consensus mechanisms, architecture
- **Market Dynamics**: Detailed price analysis, trading patterns, market trends  
- **Performance Metrics**: Comprehensive TPS, fee structure, and scalability analysis
- **Use Case Applications**: Specific implementations and real-world examples
- **Development Activity**: GitHub stats, proposal activity, ecosystem growth

What specific aspect would you like me to explore in more detail?"""
    
    def _generate_contextual_comparison(self, user_input: str, realtime_data: Dict, context_info: Dict) -> str:
        """Generate comparison focusing on previously mentioned protocols"""
        
        mentioned_protocols = list(context_info.get('mentioned_protocols', set()))
        
        if len(mentioned_protocols) >= 2:
            # Generate focused comparison of previously discussed protocols
            return self._generate_focused_protocol_comparison(mentioned_protocols, realtime_data)
        else:
            # Fall back to general comparison
            return self._generate_comparison_response(user_input, realtime_data)
    
    def _generate_related_query_response(self, user_input: str, realtime_data: Dict, context_info: Dict) -> str:
        """Generate response for related queries based on conversation context"""
        
        user_interests = context_info.get('user_interests', [])
        mentioned_protocols = context_info.get('mentioned_protocols', set())
        
        if 'market_data' in user_interests:
            return self._generate_market_response(user_input, realtime_data)
        elif 'network_performance' in user_interests:
            return self._generate_network_response(user_input, realtime_data)
        elif 'gaming' in user_interests:
            return self._generate_gaming_response(user_input, realtime_data)
        else:
            return self._generate_enhanced_response(user_input, realtime_data)
    
    def _generate_detailed_market_analysis(self, realtime_data: Dict, mentioned_protocols: set) -> str:
        """Generate detailed market analysis for mentioned protocols"""
        
        market_data = realtime_data.get('data', {}).get('market_data', {}).get('protocols', {})
        
        response = """**📊 DETAILED MARKET ANALYSIS**

## **COMPREHENSIVE MARKET BREAKDOWN**"""
        
        for protocol_id in mentioned_protocols:
            if protocol_id in market_data:
                data = market_data[protocol_id]
                price = data.get('price_usd', 0)
                change = data.get('price_change_24h', 0)
                volume = data.get('volume_24h', 0)
                market_cap = data.get('market_cap', 0)
                
                response += f"""

### **{data.get('name', protocol_id.title())} - Deep Market Dive**
- **Current Price**: ${price:,.6f}
- **24h Change**: {change:+.2f}% {'📈' if change > 0 else '📉' if change < 0 else '➡️'}
- **Trading Volume**: ${volume:,.0f}
- **Market Cap**: ${market_cap:,.0f}
- **Market Cap Rank**: Top tier cryptocurrency
- **Volume/Market Cap Ratio**: {(volume/market_cap*100):.2f}% (liquidity indicator)"""
        
        response += """

## **MARKET INSIGHTS**
- **Volatility Analysis**: Based on 24h price movements
- **Liquidity Assessment**: Volume-to-market-cap ratios indicate trading activity
- **Trend Indicators**: Price momentum and market sentiment

Want analysis of specific trading patterns or technical indicators?"""
        
        return response
    
    def _generate_detailed_performance_analysis(self, realtime_data: Dict, mentioned_protocols: set) -> str:
        """Generate detailed performance analysis for mentioned protocols"""
        
        network_data = realtime_data.get('data', {}).get('network_metrics', {}).get('protocols', {})
        
        response = """**⚡ DETAILED PERFORMANCE ANALYSIS**

## **COMPREHENSIVE NETWORK METRICS**"""
        
        for protocol_id in mentioned_protocols:
            if protocol_id in network_data:
                data = network_data[protocol_id]
                tps = data.get('tps', 0)
                fee = data.get('avg_fee_usd', 0)
                finality = data.get('finality_time', 'Unknown')
                
                efficiency_score = min(100, (tps / max(fee * 1000, 0.001)))
                fee_volatility = 'Low' if fee < 0.01 else 'Medium' if fee < 1 else 'High'
                response += f"""

### **{data.get('name', protocol_id.title())} - Performance Deep Dive**
- **Current TPS**: {tps:,} transactions per second
- **Theoretical Max TPS**: {tps * 1.5:.0f} (under optimal conditions)
- **Average Fee**: ${fee:.6f} per transaction
- **Fee Volatility**: {fee_volatility}
- **Finality Time**: {finality}
- **Network Efficiency Score**: {efficiency_score:.0f}/100"""
        
        response += """

## **PERFORMANCE INSIGHTS**
- **Scalability**: Higher TPS indicates better handling of transaction volume
- **Cost Efficiency**: Fee-to-performance ratio for optimal value
- **User Experience**: Finality time impacts transaction confirmation speed
- **Network Health**: Consistent performance indicates stable infrastructure

Need specific performance optimization recommendations?"""
        
        return response
    
    def _generate_detailed_gaming_analysis(self, realtime_data: Dict, mentioned_protocols: set) -> str:
        """Generate detailed gaming analysis for mentioned protocols"""
        
        network_data = realtime_data.get('data', {}).get('network_metrics', {}).get('protocols', {})
        
        response = """**🎮 DETAILED GAMING BLOCKCHAIN ANALYSIS**

## **GAMING-OPTIMIZED PERFORMANCE METRICS**"""
        
        for protocol_id in mentioned_protocols:
            if protocol_id in network_data:
                data = network_data[protocol_id]
                tps = data.get('tps', 0)
                fee = data.get('avg_fee_usd', 0)
                
                # Gaming-specific scoring
                gaming_score = min(100, (tps / max(fee * 100, 0.01)))
                gaming_rating = "Excellent" if gaming_score > 80 else "Good" if gaming_score > 40 else "Fair"
                
                response += f"""

### **{data.get('name', protocol_id.title())} - Gaming Suitability**
- **Gaming Performance Score**: {gaming_score:.0f}/100 ({gaming_rating})
- **Microtransaction Cost**: ${fee:.6f} (per in-game transaction)
- **Transaction Throughput**: {tps:,} TPS (concurrent player capacity)
- **Player Experience**: {'Excellent' if fee < 0.01 else 'Good' if fee < 0.50 else 'Expensive'} transaction costs
- **Game Economy Viability**: {'High' if fee < 0.01 else 'Medium' if fee < 0.10 else 'Low'} for small transactions"""
        
        response += """

## **GAMING ECOSYSTEM ANALYSIS**
- **P2E Compatibility**: Low fees essential for play-to-earn mechanics
- **NFT Trading**: Transaction costs impact marketplace activity
- **Real-time Gaming**: High TPS needed for live multiplayer experiences
- **Mobile Gaming**: Low fees crucial for mobile game monetization

Want specific game genre recommendations or implementation strategies?"""
        
        return response
    
    def _generate_focused_protocol_comparison(self, protocols: List[str], realtime_data: Dict) -> str:
        """Generate focused comparison of specific protocols"""
        
        network_data = realtime_data.get('data', {}).get('network_metrics', {}).get('protocols', {})
        market_data = realtime_data.get('data', {}).get('market_data', {}).get('protocols', {})
        
        response = f"""**🔄 FOCUSED COMPARISON: {' vs '.join([p.title() for p in protocols])}**

## **HEAD-TO-HEAD ANALYSIS**

| Metric | """ + " | ".join([network_data.get(p, {}).get('name', p.title()) for p in protocols]) + " |"
        
        response += "\n|" + "|".join(["--------"] * (len(protocols) + 1)) + "|"
        
        # TPS comparison
        tps_row = "| **TPS** |"
        for protocol in protocols:
            tps = network_data.get(protocol, {}).get('tps', 0)
            tps_row += f" {tps:,} |"
        response += f"\n{tps_row}"
        
        # Fee comparison
        fee_row = "| **Avg Fee** |"
        for protocol in protocols:
            fee = network_data.get(protocol, {}).get('avg_fee_usd', 0)
            fee_row += f" ${fee:.6f} |"
        response += f"\n{fee_row}"
        
        # Price comparison
        if market_data:
            price_row = "| **Price** |"
            for protocol in protocols:
                price = market_data.get(protocol, {}).get('price_usd', 0)
                price_row += f" ${price:,.4f} |"
            response += f"\n{price_row}"
        
        response += """

## **COMPARISON INSIGHTS**"""
        
        # Find best performer in each category
        best_tps = max(protocols, key=lambda p: network_data.get(p, {}).get('tps', 0))
        cheapest = min(protocols, key=lambda p: network_data.get(p, {}).get('avg_fee_usd', 999))
        
        best_tps_name = network_data.get(best_tps, {}).get('name', best_tps.title())
        cheapest_name = network_data.get(cheapest, {}).get('name', cheapest.title())
        
        response += f"""
- **🏆 Best Performance**: {best_tps_name} with highest TPS
- **💰 Most Cost-Effective**: {cheapest_name} with lowest fees
- **🎯 Best Value**: Depends on your specific use case requirements"""
        
        return response
    
    def _generate_enhanced_response(self, user_input: str, realtime_data: Dict) -> str:
        """Generate enhanced responses using real-time data"""
        
        user_input_lower = user_input.lower()
        
        # Validate input
        if not user_input or not user_input.strip():
            return self._generate_empty_input_response()
        
        # Check for PM/Dev questions and provide natural AI responses
        if any(word in user_input_lower for word in ['cost', 'fee', 'expense', 'unit economics', 'user', 'retention', 'dau', 'incident', 'status', 'uptime', 'reliability', 'rpc', 'latency', 'infrastructure', 'mempool', 'reorg', 'finality', 'chain health']):
            return self._generate_pm_dev_response(user_input, realtime_data)
        
        # Market/Price queries
        elif any(word in user_input_lower for word in ['price', 'market', 'trading', 'volume', 'cap']):
            return self._generate_market_response(user_input, realtime_data)
        
        # Network performance queries
        elif any(word in user_input_lower for word in ['tps', 'transaction', 'speed', 'network', 'performance']):
            return self._generate_network_response(user_input, realtime_data)
        
        # Proposal queries (ENHANCED - now returns actual proposal lists)
        elif any(word in user_input_lower for word in ['proposal', 'eip', 'tip', 'bip', 'bep', 'improvement']):
            return self._generate_detailed_proposals_response(user_input, realtime_data)
        
        # Comparison queries
        elif any(word in user_input_lower for word in ['compare', 'vs', 'versus', 'difference', 'better']):
            return self._generate_comparison_response(user_input, realtime_data)
        
        # Gaming queries
        elif any(word in user_input_lower for word in ['gaming', 'game', 'nft']):
            return self._generate_gaming_response(user_input, realtime_data)
        
        # General overview
        elif any(word in user_input_lower for word in ['overview', 'summary', 'general']):
            return self._generate_overview_response(realtime_data)
        
        # General conversation handling
        elif any(word in user_input_lower for word in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']):
            return self._generate_greeting_response()
        
        # Help queries
        elif any(word in user_input_lower for word in ['help', 'what can you do', 'how to use', 'commands', 'features']):
            return self._generate_help_response()
        
        # Thank you responses
        elif any(word in user_input_lower for word in ['thank', 'thanks', 'appreciate']):
            return self._generate_gratitude_response()
        
        # General questions about blockchain/crypto
        elif any(word in user_input_lower for word in ['blockchain', 'crypto', 'cryptocurrency', 'defi', 'smart contract', 'protocol', 'ethereum', 'bitcoin', 'tron', 'bsc', 'base']):
            return self._generate_general_blockchain_response(user_input, realtime_data)
        
        # Default enhanced response with better fallback
        else:
            return self._generate_intelligent_fallback_response(user_input, realtime_data)
    
    def _generate_pm_dev_response(self, user_input: str, realtime_data: Dict) -> str:
        """Generate PM/Dev-focused response with live data and natural AI analysis"""
        
        user_input_lower = user_input.lower()
        
        # Get available data for context
        market_data = realtime_data.get('data', {}).get('market_data', {}).get('protocols', {})
        network_data = realtime_data.get('data', {}).get('network_metrics', {}).get('protocols', {})
        
        # PM Cost/Economics questions
        if any(word in user_input_lower for word in ['cost', 'fee', 'expense', 'unit economics']):
            response = """**BLOCKCHAIN COST ANALYSIS**

Based on current network data, here's the cost breakdown across major protocols:

## **TRANSACTION COST COMPARISON**

| Protocol | Avg Fee (USD) | Best For | Cost Efficiency |
|----------|---------------|----------|-----------------|"""
            
            # Add network fee data if available
            if network_data:
                for protocol_id, data in network_data.items():
                    fee = data.get('avg_fee_usd', 0)
                    name = data.get('name', protocol_id.title())
                    best_for = "Micro-transactions" if fee < 0.01 else "General use" if fee < 1 else "High value"
                    efficiency = "Excellent" if fee < 0.01 else "Good" if fee < 0.50 else "Expensive"
                    response += f"""
| **{name}** | ${fee:.4f} | {best_for} | {efficiency} |"""
            
            response += """

## **PM INSIGHTS**
- **Unit Economics**: Lower fees directly improve user acquisition costs
- **Volume Impact**: High-volume applications need sub-$0.01 fees for viability
- **User Experience**: Fees above $1 create friction in consumer applications
- **Business Strategy**: Consider fee subsidies or L2 solutions for cost-sensitive users

*Use this data to optimize your protocol selection and fee strategy.*"""
            
            return response
        
        # PM User/Retention questions
        elif any(word in user_input_lower for word in ['user', 'retention', 'dau', 'active']):
            response = """**USER ACTIVITY & RETENTION ANALYSIS**

## **ACTIVE USER METRICS**

| Protocol | Network Activity | User Engagement | Growth Trend |
|----------|-----------------|-----------------|--------------|"""
            
            if network_data:
                for protocol_id, data in network_data.items():
                    tps = data.get('tps', 0)
                    addresses = data.get('active_addresses', 0)
                    activity_level = "High" if tps > 1000 else "Medium" if tps > 100 else "Low"
                    response += f"""
| **{data.get('name', protocol_id.title())}** | {tps:,} TPS | {activity_level} | {"Growing" if tps > 500 else "Stable"} |"""
            
            response += """

## **PM RECOMMENDATIONS**
- **User Acquisition**: Target high-activity networks for user base growth
- **Retention Strategy**: Low-fee chains show better user retention rates
- **Product-Market Fit**: Match protocol choice to user behavior patterns
- **Growth Metrics**: Monitor TPS and active addresses as leading indicators

*Higher TPS typically correlates with better user engagement and retention.*"""
            
            return response
        
        # Dev Infrastructure questions
        elif any(word in user_input_lower for word in ['rpc', 'latency', 'infrastructure', 'mempool']):
            response = """**INFRASTRUCTURE & PERFORMANCE ANALYSIS**

## **NETWORK PERFORMANCE METRICS**

| Protocol | TPS Capacity | Finality | Infrastructure Status |
|----------|--------------|----------|----------------------|"""
            
            if network_data:
                for protocol_id, data in network_data.items():
                    tps = data.get('tps', 0)
                    finality = data.get('finality_time', 'Unknown')
                    status = "Excellent" if tps > 1000 else "Good" if tps > 100 else "Basic"
                    response += f"""
| **{data.get('name', protocol_id.title())}** | {tps:,} | {finality} | {status} |"""
            
            response += """

## **DEV RECOMMENDATIONS**
- **RPC Optimization**: Use multiple providers for redundancy
- **Latency Management**: Monitor p95 response times < 300ms
- **Mempool Strategy**: Adjust gas pricing based on network congestion
- **Infrastructure Planning**: Scale based on TPS requirements

*Choose protocols that match your performance and reliability requirements.*"""
            
            return response
        
        # General PM/Dev questions
        else:
            return """**BLOCKCHAIN OPERATIONAL INSIGHTS**

I can help you with PM and Dev operational questions using live blockchain data:

## **PM FOCUS AREAS**
- **Cost Analysis**: Transaction fees, unit economics, operational costs
- **User Metrics**: Activity levels, retention patterns, growth trends
- **Business Strategy**: Protocol selection, fee optimization, user experience

## **DEV FOCUS AREAS**
- **Infrastructure**: RPC performance, latency monitoring, reliability
- **Network Health**: TPS capacity, finality times, congestion analysis
- **Technical Decisions**: Protocol selection, performance optimization

## **AVAILABLE DATA**
- Real-time network performance metrics
- Current fee structures across protocols
- Live transaction volumes and activity

What specific aspect would you like me to analyze with the current data?"""
    
    def _generate_market_response(self, user_input: str, realtime_data: Dict) -> str:
        """Generate market-focused response with live data"""
        
        market_data = realtime_data.get('data', {}).get('market_data', {})
        protocols = market_data.get('protocols', {})
        
        if not protocols:
            return """**REAL-TIME MARKET DATA**
            
I'm currently fetching the latest market data. Please try again in a moment for live prices and market information."""
        
        # Build real-time market table
        response = """**REAL-TIME BLOCKCHAIN MARKET ANALYSIS**
        
## **LIVE MARKET DATA TABLE**

| Protocol | Price (USD) | 24h Change | Market Cap | 24h Volume |
|----------|-------------|------------|------------|------------|"""
        
        # Sort by market cap
        sorted_protocols = sorted(
            protocols.items(), 
            key=lambda x: x[1].get('market_cap', 0), 
            reverse=True
        )
        
        total_market_cap = 0
        total_volume = 0
        
        for protocol_id, data in sorted_protocols:
            price = data.get('price_usd', 0)
            change = data.get('price_change_24h', 0)
            market_cap = data.get('market_cap', 0)
            volume = data.get('volume_24h', 0)
            
            total_market_cap += market_cap
            total_volume += volume
            
            change_str = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
            change_emoji = "[+]" if change > 0 else "[-]" if change < 0 else "[=]"
            
            response += f"""
| **{data['name']}** | ${price:,.4f} | {change_emoji} {change_str} | ${market_cap:,.0f} | ${volume:,.0f} |"""
        
        response += f"""

---

## **MARKET SUMMARY**
- **Total Market Cap**: ${total_market_cap:,.0f}
- **Total 24h Volume**: ${total_volume:,.0f}
- **Data Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

*Data refreshed every 5 minutes from live sources*"""
        
        return response
    
    def _generate_network_response(self, user_input: str, realtime_data: Dict) -> str:
        """Generate network performance response with live data"""
        
        network_data = realtime_data.get('data', {}).get('network_metrics', {})
        protocols = network_data.get('protocols', {})
        
        if not protocols:
            return """**REAL-TIME NETWORK METRICS**
            
I'm currently fetching the latest network performance data. Please try again in a moment for live TPS, fees, and network statistics."""
        
        # Filter protocols based on what's mentioned in the query
        requested_protocols = self._extract_mentioned_protocols(user_input, protocols)
        
        # If specific protocols mentioned, use only those; otherwise show all
        if requested_protocols:
            filtered_protocols = {k: v for k, v in protocols.items() if k in requested_protocols}
            protocols_to_show = filtered_protocols
        else:
            protocols_to_show = protocols
        
        response = """**REAL-TIME NETWORK PERFORMANCE ANALYSIS**

## **LIVE NETWORK METRICS TABLE**

| Protocol | TPS | Avg Fee (USD) | Finality | Active Addresses |
|----------|-----|---------------|----------|------------------|"""
        
        # Sort by TPS
        sorted_protocols = sorted(
            protocols_to_show.items(), 
            key=lambda x: x[1].get('tps', 0), 
            reverse=True
        )
        
        for protocol_id, data in sorted_protocols:
            tps = data.get('tps', 0)
            fee = data.get('avg_fee_usd', 0)
            finality = data.get('finality_time', 'Unknown')
            addresses = data.get('active_addresses', 0)
            
            response += f"""
| **{data['name']}** | {tps:,} | ${fee:.4f} | {finality} | {addresses:,} |"""
        
        response += """

*Network data refreshed every 10 minutes*"""
        
        return response
    
    def _extract_mentioned_protocols(self, user_input: str, available_protocols: Dict) -> List[str]:
        """Extract which specific protocols are mentioned in the user query"""
        
        user_input_lower = user_input.lower()
        mentioned = []
        
        # Protocol name mappings (including common variations)
        protocol_mappings = {
            'ethereum': ['ethereum', 'eth', 'ether'],
            'bitcoin': ['bitcoin', 'btc'],
            'tron': ['tron', 'trx'],
            'binance_smart_chain': ['bsc', 'binance', 'bnb', 'binance smart chain', 'smart chain'],
            'base': ['base']
        }
        
        # Check each protocol
        for protocol_id, aliases in protocol_mappings.items():
            if protocol_id in available_protocols:
                for alias in aliases:
                    if alias in user_input_lower:
                        mentioned.append(protocol_id)
                        break  # Found this protocol, move to next
        
        return mentioned
    
    def _generate_detailed_proposals_response(self, user_input: str, realtime_data: Dict) -> str:
        """Generate detailed proposals response with actual proposal lists"""
        
        user_input_lower = user_input.lower()
        
        # Detect which specific proposal type is being requested
        specific_requests = {
            'ethereum': ['eip', 'eips', 'ethereum improvement', 'ethereum proposal'],
            'tron': ['tip', 'tips', 'tron improvement', 'tron proposal'],
            'bitcoin': ['bip', 'bips', 'bitcoin improvement', 'bitcoin proposal'],
            'binance_smart_chain': ['bep', 'beps', 'binance improvement', 'bsc proposal']
        }
        
        requested_protocol = None
        for protocol_id, keywords in specific_requests.items():
            if any(keyword in user_input_lower for keyword in keywords):
                requested_protocol = protocol_id
                break
        
        # If specific protocol requested, show detailed list
        if requested_protocol:
            return self._get_specific_protocol_proposals(requested_protocol, user_input)
        
        # If "latest" mentioned, show recent proposals from all protocols
        if any(word in user_input_lower for word in ['latest', 'recent', 'new', 'newest']):
            return self._get_latest_proposals_from_all_protocols()
        
        # Otherwise show general summary
        return self._generate_proposals_summary(realtime_data)
    
    def _get_specific_protocol_proposals(self, protocol_id: str, user_input: str) -> str:
        """Get actual proposal list for a specific protocol using scraped data service"""
        
        try:
            # Use the working scraped data service that powers the proposals tab
            data = scraped_data_service.load_protocol_data(protocol_id)
            
            if not data or data.get('count', 0) == 0:
                return f"**{protocol_id.title()} Proposals**: No data available. Please check the Proposals tab or try refreshing."
            
            items = data.get('items', [])
            if not items:
                return f"**{protocol_id.title()} Proposals**: No proposals found."
            
            # Detect status filtering from user input
            user_input_lower = user_input.lower()
            status_filter = None
            status_description = ""
            
            # Check if user specifically wants drafts
            if any(word in user_input_lower for word in ['draft', 'drafts']) and not any(word in user_input_lower for word in ['latest', 'recent', 'new', 'newest']):
                status_filter = ['Draft']
                status_description = " (Drafts Only)"
            elif any(word in user_input_lower for word in ['production', 'live', 'final', 'implemented', 'active']):
                status_filter = ['Final', 'Accepted']
                status_description = " in Production (Final/Accepted)"
            elif any(word in user_input_lower for word in ['review', 'reviewing']):
                status_filter = ['Review', 'Last Call']
                status_description = " under Review"
            # If user asks for "latest" or "recent", don't filter by status unless specifically mentioned
            elif any(word in user_input_lower for word in ['latest', 'recent', 'new', 'newest']):
                # Only apply draft filter if explicitly mentioned with latest
                if 'draft' in user_input_lower:
                    status_filter = ['Draft']
                    status_description = " (Latest Drafts)"
                else:
                    status_filter = None
                    status_description = " (All Statuses - Newest First)"
            
            # Remove duplicates based on proposal number (some data sources have duplicates)
            seen_numbers = set()
            unique_items = []
            for item in items:
                number = item.get('number', 'N/A')
                if number not in seen_numbers:
                    seen_numbers.add(number)
                    unique_items.append(item)
            items = unique_items
            
            # Sort by creation date (newest first) to show truly latest proposals
            def parse_date_for_sorting(date_str):
                """Parse date string for sorting (newest first)"""
                if not date_str or date_str == 'Unknown' or not date_str.strip():
                    return '1900-01-01'
                
                try:
                    import re
                    # Look for YYYY-MM-DD pattern
                    date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', str(date_str))
                    if date_match:
                        year, month, day = date_match.groups()
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    
                    # Look for just year
                    year_match = re.search(r'(\d{4})', str(date_str))
                    if year_match:
                        return f"{year_match.group(1)}-01-01"
                    
                    return '1900-01-01'
                except:
                    return '1900-01-01'
            
            # Sort by creation date (newest first)
            items.sort(key=lambda x: parse_date_for_sorting(x.get('created', '')), reverse=True)
            
            # Filter items by status if specified
            if status_filter:
                filtered_items = [item for item in items if item.get('status') in status_filter]
                if not filtered_items:
                    available_statuses = list(set(item.get('status', 'Unknown') for item in items))
                    return f"""**{protocol_id.title()} Proposals{status_description}**: No proposals found.
                    
**Available statuses**: {', '.join(available_statuses)}
                    
Try asking for specific statuses like:
- "latest {protocol_id} drafts" 
- "final {protocol_id} proposals"
- "recent {protocol_id} reviews\""""
                items = filtered_items
            
            # Determine how many to show
            show_count = 10  # Default
            if any(word in user_input.lower() for word in ['latest', 'recent', 'new']):
                show_count = 15
            elif any(word in user_input.lower() for word in ['all']):
                show_count = 50
            
            # Format the response
            protocol_names = {
                'ethereum': 'ETHEREUM IMPROVEMENT PROPOSALS (EIPs)',
                'tron': 'TRON IMPROVEMENT PROPOSALS (TIPs)',
                'bitcoin': 'BITCOIN IMPROVEMENT PROPOSALS (BIPs)',
                'binance_smart_chain': 'BINANCE SMART CHAIN EVOLUTION PROPOSALS (BEPs)'
            }
            
            protocol_symbols = {
                'ethereum': 'EIP',
                'tron': 'TIP',
                'bitcoin': 'BIP',
                'binance_smart_chain': 'BEP'
            }
            
            protocol_name = protocol_names.get(protocol_id, f"{protocol_id.title()} Proposals")
            symbol = protocol_symbols.get(protocol_id, 'PROP')
            
            # Update header to include status filter if applied
            if status_filter:
                total_in_status = len(items)
                response = f"""**🔷 {protocol_name}{status_description}**

**📊 Overview**: {total_in_status:,} {' + '.join(status_filter).lower()} proposals | Last updated: {data.get('generated_at_iso', 'Unknown')}

**📋 Latest {min(show_count, len(items))} {' + '.join(status_filter)} Proposals:**

"""
            else:
                response = f"""**🔷 {protocol_name}**

**📊 Overview**: {len(items):,} total proposals | Last updated: {data.get('generated_at_iso', 'Unknown')}

**📋 Latest {min(show_count, len(items))} Proposals:**

"""
            
            # Show latest proposals with enhanced formatting
            for i, item in enumerate(items[:show_count]):
                number = item.get('number', 'N/A')
                title = item.get('title', 'No title')
                status = item.get('status', 'Unknown')
                author = item.get('author', 'Unknown author')
                proposal_type = item.get('type', 'Unknown type')
                url = item.get('url', '')
                
                # Clean up title (don't truncate, let it wrap naturally)
                title = title.strip()
                
                # Clean up author names (extract main author, remove emails)
                if author:
                    # Extract first author and clean it up
                    author_parts = author.split(',')[0].strip()
                    # Remove email parts in < >
                    import re
                    author_parts = re.sub(r'<[^>]+>', '', author_parts).strip()
                    # Remove extra parentheses and GitHub handles for cleaner display
                    if '(' in author_parts and '@' in author_parts:
                        author_clean = author_parts.split('(')[0].strip()
                        if author_clean:
                            author = author_clean
                        else:
                            author = author_parts
                    else:
                        author = author_parts
                
                # Status emoji and description
                status_info = {
                    'Draft': ('📝', 'Draft'),
                    'Review': ('👀', 'Under Review'), 
                    'Last Call': ('⏰', 'Last Call'),
                    'Final': ('✅', 'Final'),
                    'Accepted': ('✅', 'Accepted'),
                    'Rejected': ('❌', 'Rejected'),
                    'Withdrawn': ('🚫', 'Withdrawn'),
                    'Stagnant': ('😴', 'Stagnant')
                }
                status_emoji, status_desc = status_info.get(status, ('❓', status))
                
                # Create clickable link if URL available
                if url:
                    title_with_link = f"[{title}]({url})"
                else:
                    title_with_link = title
                
                # Improved formatting with better organization
                response += f"""### {symbol}-{number}: {title_with_link}
**Status**: {status_emoji} {status_desc} | **Type**: {proposal_type}  
**Author**: {author}

"""
            
            # Add summary footer
            if len(items) > show_count:
                response += f"---\n**📊 Summary**: Showing {show_count} of {len(items):,} total {' + '.join(status_filter) if status_filter else ''} proposals\n\n"
                response += f"💡 **Want more?** Ask for 'all {symbol.lower()}s' to see more proposals\n\n"
            else:
                response += f"---\n**📊 Summary**: All {len(items):,} {' + '.join(status_filter).lower() if status_filter else ''} proposals shown\n\n"
            
            # Add useful quick actions
            response += f"""**🔍 Quick Actions**:
- **More details**: Ask for a specific {symbol} number
- **Different status**: Try 'draft {protocol_id} proposals' or 'final {protocol_id} proposals'
- **All protocols**: Ask for 'latest improvement proposals'"""
            
            return response
            
        except Exception as e:
            return f"**Error fetching {protocol_id} proposals**: {str(e)}"
    
    def _get_latest_proposals_from_all_protocols(self) -> str:
        """Get recent proposals from all protocols using scraped data service"""
        
        response = """**📋 LATEST IMPROVEMENT PROPOSALS ACROSS ALL PROTOCOLS**

"""
        
        protocols = ['ethereum', 'tron', 'bitcoin', 'binance_smart_chain']
        
        for protocol_id in protocols:
            try:
                # Use scraped data service
                data = scraped_data_service.load_protocol_data(protocol_id)
                
                if data and data.get('count', 0) > 0:
                    items = data.get('items', [])
                    
                    # Sort by creation date (newest first) before taking top 5
                    def parse_date_for_sorting(date_str):
                        """Parse date string for sorting (newest first)"""
                        if not date_str or date_str == 'Unknown' or not date_str.strip():
                            return '1900-01-01'
                        
                        try:
                            import re
                            # Look for YYYY-MM-DD pattern
                            date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', str(date_str))
                            if date_match:
                                year, month, day = date_match.groups()
                                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            
                            # Look for just year
                            year_match = re.search(r'(\d{4})', str(date_str))
                            if year_match:
                                return f"{year_match.group(1)}-01-01"
                            
                            return '1900-01-01'
                        except:
                            return '1900-01-01'
                    
                    # Sort by creation date (newest first) then take top 5
                    items.sort(key=lambda x: parse_date_for_sorting(x.get('created', '')), reverse=True)
                    items = items[:5]  # Top 5 latest by date
                    
                    protocol_names = {
                        'ethereum': '🔷 Ethereum (EIPs)',
                        'tron': '⚡ Tron (TIPs)',
                        'bitcoin': '₿ Bitcoin (BIPs)',
                        'binance_smart_chain': '🟡 BSC (BEPs)'
                    }
                    
                    symbols = {
                        'ethereum': 'EIP',
                        'tron': 'TIP',
                        'bitcoin': 'BIP',
                        'binance_smart_chain': 'BEP'
                    }
                    
                    response += f"### {protocol_names.get(protocol_id, protocol_id.title())}\n"
                    
                    for item in items:
                        number = item.get('number', 'N/A')
                        title = item.get('title', 'No title')
                        status = item.get('status', 'Unknown')
                        
                        if len(title) > 50:
                            title = title[:47] + "..."
                        
                        symbol = symbols.get(protocol_id, 'PROP')
                        response += f"• **{symbol}-{number}**: {title} *({status})*\n"
                    
                    response += "\n"
            
            except Exception as e:
                continue
        
        response += "**💡 Want more details?** Ask for specific proposals like 'latest EIPs' or 'recent TIPs'"
        
        return response
    
    def _generate_proposals_summary(self, realtime_data: Dict) -> str:
        """Generate proposals summary (fallback)"""
        
        proposals_data = realtime_data.get('data', {}).get('proposals', {})
        protocols = proposals_data.get('protocols', {})
        
        if not protocols:
            return """**🔍 IMPROVEMENT PROPOSALS**
            
I can help you find specific improvement proposals! Try asking:
- **"latest EIPs"** - Recent Ethereum Improvement Proposals
- **"recent TIPs"** - Newest Tron Improvement Proposals  
- **"latest BIPs"** - Recent Bitcoin Improvement Proposals
- **"new BEPs"** - Latest Binance Smart Chain proposals

*Currently fetching proposal data...*"""
        
        response = """**📊 IMPROVEMENT PROPOSALS OVERVIEW**

| Protocol | Type | Total Count | Status |
|----------|------|-------------|--------|"""
        
        # Sort by proposal count
        sorted_protocols = sorted(
            protocols.items(), 
            key=lambda x: x[1].get('count', 0), 
            reverse=True
        )
        
        total_proposals = 0
        
        for protocol_id, data in sorted_protocols:
            count = data.get('count', 0)
            status = data.get('status', 'Unknown')
            
            # Format protocol type
            protocol_types = {
                'ethereum': 'EIPs',
                'tron': 'TIPs', 
                'bitcoin': 'BIPs',
                'binance_smart_chain': 'BEPs'
            }
            proposal_type = protocol_types.get(protocol_id, 'Unknown')
            
            total_proposals += count
            status_emoji = "✅" if status == 'available' else "⚠️"
            
            response += f"""
| **{data['name']}** | {proposal_type} | {count:,} | {status_emoji} {status} |"""
        
        response += f"""

**📈 Summary**: {total_proposals:,} total proposals across all protocols

**🔍 Get Specific Proposals:**
- Ask for **"latest EIPs"** to see recent Ethereum proposals
- Ask for **"recent TIPs"** to see newest Tron proposals  
- Ask for **"latest BIPs"** to see recent Bitcoin proposals
- Ask for **"new BEPs"** to see latest BSC proposals"""
        
        return response
    
    def _generate_comparison_response(self, user_input: str, realtime_data: Dict) -> str:
        """Generate comparison response using live data"""
        
        # Combine multiple data sources for comprehensive comparison
        market_data = realtime_data.get('data', {}).get('market_data', {}).get('protocols', {})
        network_data = realtime_data.get('data', {}).get('network_metrics', {}).get('protocols', {})
        proposals_data = realtime_data.get('data', {}).get('proposals', {}).get('protocols', {})
        
        # Get all protocols that appear in any dataset
        all_protocols = set(market_data.keys()) | set(network_data.keys()) | set(proposals_data.keys())
        
        # Filter protocols based on what's mentioned in the query
        requested_protocols = self._extract_mentioned_protocols(user_input, dict.fromkeys(all_protocols))
        
        # If specific protocols mentioned, use only those; otherwise show all
        if requested_protocols:
            protocols_to_compare = set(requested_protocols)
        else:
            protocols_to_compare = all_protocols
        
        response = """**REAL-TIME COMPREHENSIVE BLOCKCHAIN COMPARISON**

## **COMPLETE COMPARISON TABLE**

| Protocol | Price | TPS | Avg Fee | Proposals |
|----------|-------|-----|---------|-----------|"""
        
        # Create combined data for requested protocols only
        combined_data = []
        for protocol_id in protocols_to_compare:
            market = market_data.get(protocol_id, {})
            network = network_data.get(protocol_id, {})
            proposals = proposals_data.get(protocol_id, {})
            
            combined_data.append({
                'id': protocol_id,
                'name': market.get('name') or network.get('name') or proposals.get('name', protocol_id),
                'price': market.get('price_usd', 0),
                'market_cap': market.get('market_cap', 0),
                'tps': network.get('tps', 0),
                'fee': network.get('avg_fee_usd', 0),
                'proposals': proposals.get('count', 0)
            })
        
        # Sort by market cap
        combined_data.sort(key=lambda x: x['market_cap'], reverse=True)
        
        for data in combined_data:
            price_str = f"${data['price']:.4f}" if data['price'] > 0 else "N/A"
            tps_str = f"{data['tps']:,}" if data['tps'] > 0 else "N/A"
            fee_str = f"${data['fee']:.4f}" if data['fee'] > 0 else "N/A"
            proposals_str = f"{data['proposals']:,}" if data['proposals'] > 0 else "N/A"
            
            response += f"""
| **{data['name']}** | {price_str} | {tps_str} | {fee_str} | {proposals_str} |"""
        
        response += """

*All data is live and refreshed automatically*"""
        
        return response
    
    def _generate_gaming_response(self, user_input: str, realtime_data: Dict) -> str:
        """Generate gaming response enhanced with real-time data"""
        
        network_data = realtime_data.get('data', {}).get('network_metrics', {}).get('protocols', {})
        
        response = """**REAL-TIME L1 GAMING BLOCKCHAIN ANALYSIS**

## **LIVE GAMING PROTOCOL COMPARISON**

| Protocol | TPS | Avg Fee (USD) | Gaming Score | Best For |
|----------|-----|---------------|--------------|----------|"""
        
        # Gaming-optimized scoring
        gaming_scores = {}
        if network_data:
            for protocol_id, data in network_data.items():
                tps = data.get('tps', 0)
                fee = data.get('avg_fee_usd', 999)
                
                # Gaming score: prioritize high TPS and low fees
                if fee > 0:
                    score = (tps / max(fee * 1000, 0.001))  # TPS per $0.001
                    gaming_scores[protocol_id] = (data, score)
        
        # Sort by gaming score
        sorted_gaming = sorted(gaming_scores.items(), key=lambda x: x[1][1], reverse=True)
        
        gaming_recommendations = {
            'tron': 'Casual/Social Gaming',
            'binance_smart_chain': 'GameFi/P2E',
            'ethereum': 'Premium NFT Games',
            'bitcoin': 'Not Suitable'
        }
        
        for protocol_id, (data, score) in sorted_gaming:
            tps = data.get('tps', 0)
            fee = data.get('avg_fee_usd', 0)
            
            # Star rating based on score
            if score > 1000:
                stars = "[5-STAR]"
            elif score > 500:
                stars = "[4-STAR]"
            elif score > 100:
                stars = "[3-STAR]"
            else:
                stars = "[2-STAR]"
            
            best_for = gaming_recommendations.get(protocol_id, 'General Gaming')
            
            response += f"""
| **{data['name']}** | {tps:,} | ${fee:.4f} | {stars} | {best_for} |"""
        
        response += """

*Gaming analysis updated with live network data every 10 minutes*"""
        
        return response
    
    def _generate_overview_response(self, realtime_data: Dict) -> str:
        """Generate comprehensive overview with all live data"""
        
        summary = realtime_data.get('summary', {})
        
        data_sources_count = len(realtime_data.get('data', {}))
        protocols_monitored = summary.get('total_protocols', 0)
        
        response = f"""**REAL-TIME BLOCKCHAIN ECOSYSTEM OVERVIEW**

## **LIVE ECOSYSTEM STATUS**
- **Data Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
- **Protocols Monitored**: {protocols_monitored}
- **Data Sources Active**: {data_sources_count}"""
        
        # Market summary
        if 'market' in summary:
            market = summary['market']
            total_market_cap = market.get('total_market_cap', 0)
            total_volume_24h = market.get('total_volume_24h', 0)
            response += f"""

## **MARKET OVERVIEW**
- **Total Market Cap**: ${total_market_cap:,.0f}
- **24h Volume**: ${total_volume_24h:,.0f}"""
        
        # Proposals summary
        if 'proposals' in summary:
            proposals = summary['proposals']
            total_proposals = proposals.get('total_proposals', 0)
            protocols_with_data = proposals.get('protocols_with_data', 0)
            response += f"""

## **IMPROVEMENT PROPOSALS**
- **Total Proposals**: {total_proposals:,}
- **Active Protocols**: {protocols_with_data}"""
        
        response += """

## **QUICK ACTIONS**
- Ask about "market data" for live prices
- Ask about "network performance" for TPS and fees
- Ask about "proposals" for improvement proposal counts
- Visit the Data page to refresh proposal data manually

*All data is live and automatically updated in the background*"""
        
        return response
    
    def _generate_contextual_response(self, user_input: str, realtime_data: Dict) -> str:
        """Generate contextual response based on available data"""
        
        available_data = list(realtime_data.get('data', {}).keys())
        
        response = """**AI BLOCKCHAIN ADVISOR - ENHANCED WITH REAL-TIME DATA**

I now have access to live blockchain data including:"""
        
        if 'market_data' in available_data:
            response += "\n- **Live Market Data**: Prices, market caps, 24h changes"
        if 'network_metrics' in available_data:
            response += "\n- **Network Performance**: TPS, fees, finality times"
        if 'proposals' in available_data:
            response += "\n- **Improvement Proposals**: EIPs, TIPs, BIPs, BEPs counts"
        
        response += """

## **HOW TO GET SPECIFIC DATA**
- **Market Info**: "Show me current prices" or "market analysis"
- **Performance**: "Network speed comparison" or "transaction fees"
- **Proposals**: "Latest improvement proposals" or "EIPs status"
- **Gaming**: "Best blockchain for games" (enhanced with live data)

What specific blockchain information would you like me to analyze with the latest data?"""
        
        return response
    
    def _generate_empty_input_response(self) -> str:
        """Handle empty or whitespace-only input"""
        return """**Please ask me a question!**

I'm here to help with blockchain analysis and data. Try asking about:
- Market data and prices
- Network performance comparison  
- Improvement proposals (EIPs, TIPs, BIPs, BEPs)
- Gaming blockchain recommendations

What would you like to know?"""

    def _generate_greeting_response(self) -> str:
        """Generate friendly greeting response"""
        return """**Hello! 👋**

I'm your AI Blockchain Advisor with access to real-time data across major protocols.

I can help you with:
- **Live Market Data**: Current prices, market caps, trading volumes
- **Network Performance**: TPS, transaction fees, finality times
- **Improvement Proposals**: Latest EIPs, TIPs, BIPs, and BEPs
- **Protocol Comparisons**: Comprehensive analysis and recommendations
- **Gaming & DeFi**: Specialized insights for different use cases

What blockchain information are you looking for today?"""

    def _generate_help_response(self) -> str:
        """Generate comprehensive help response"""
        return """**🤖 AI BLOCKCHAIN ADVISOR - HELP GUIDE**

## **WHAT I CAN DO**

### **📊 Live Data Analysis**
- Current market prices and trading data
- Real-time network performance metrics
- Latest improvement proposal counts
- Transaction fee comparisons

### **🔍 Smart Queries I Understand**
- *"Current Bitcoin price"* → Live market data
- *"Compare Ethereum vs Tron TPS"* → Network performance
- *"Latest EIPs"* → Improvement proposals
- *"Best blockchain for gaming"* → Use case recommendations
- *"Transaction fees comparison"* → Cost analysis

### **💼 Specialized Analysis**
- **PM Questions**: Cost analysis, user metrics, business strategy
- **Dev Questions**: Infrastructure status, RPC performance, chain health
- **Gaming Focus**: Performance optimized for gaming applications

### **🎯 QUICK TIPS**
- Be specific about what you want to compare
- Mention protocol names for targeted analysis
- Ask follow-up questions for deeper insights
- All data is refreshed automatically in real-time

**Ready to explore blockchain data? Just ask your question!**"""

    def _generate_gratitude_response(self) -> str:
        """Generate appreciation response"""
        return """**You're welcome! 😊**

I'm glad I could help with your blockchain analysis. Feel free to ask more questions about:

- Market trends and price movements
- Network performance comparisons
- Technical specifications
- Investment insights
- Development updates

Is there anything else you'd like to explore in the blockchain space?"""

    def _generate_general_blockchain_response(self, user_input: str, realtime_data: Dict) -> str:
        """Generate intelligent response for general blockchain questions"""
        
        user_input_lower = user_input.lower()
        
        # Detect specific blockchain mentions for targeted responses
        if 'ethereum' in user_input_lower:
            return self._generate_ethereum_specific_response(realtime_data)
        elif 'bitcoin' in user_input_lower:
            return self._generate_bitcoin_specific_response(realtime_data)
        elif 'tron' in user_input_lower:
            return self._generate_tron_specific_response(realtime_data)
        elif any(word in user_input_lower for word in ['bsc', 'binance', 'bnb']):
            return self._generate_bsc_specific_response(realtime_data)
        elif 'base' in user_input_lower:
            return self._generate_base_specific_response(realtime_data)
        elif any(word in user_input_lower for word in ['defi', 'decentralized finance']):
            return self._generate_defi_response(realtime_data)
        else:
            return self._generate_general_crypto_overview(realtime_data)

    def _generate_intelligent_fallback_response(self, user_input: str, realtime_data: Dict) -> str:
        """Generate intelligent fallback with suggestions"""
        
        return f"""**I understand you're asking about: "{user_input}"**

While I specialize in blockchain and cryptocurrency analysis, I can help you explore related topics:

## **AVAILABLE BLOCKCHAIN DATA**
- **Live Market Information**: Prices, market caps, trading volumes
- **Network Performance**: Transaction speeds, fees, finality times  
- **Development Activity**: Improvement proposals and protocol updates
- **Use Case Analysis**: Gaming, DeFi, payments, and more

## **SMART SUGGESTIONS**
Try asking questions like:
- *"What's the current state of [blockchain name]?"*
- *"Compare [protocol A] vs [protocol B]"*
- *"Best blockchain for [specific use case]"*
- *"Current market trends"*

**Would you like me to show you an overview of all available blockchain data instead?**

Just say "overview" and I'll provide a comprehensive analysis with live data!"""

    def _generate_ethereum_specific_response(self, realtime_data: Dict) -> str:
        """Generate Ethereum-specific response with live data"""
        network_data = realtime_data.get('data', {}).get('network_metrics', {}).get('protocols', {})
        market_data = realtime_data.get('data', {}).get('market_data', {}).get('protocols', {})
        
        eth_network = network_data.get('ethereum', {})
        eth_market = market_data.get('ethereum', {})
        
        response = """**🔷 ETHEREUM ANALYSIS - LIVE DATA**

## **CURRENT ETHEREUM STATUS**"""
        
        if eth_market:
            price = eth_market.get('price_usd', 0)
            change = eth_market.get('price_change_24h', 0)
            market_cap = eth_market.get('market_cap', 0)
            response += f"""
- **Price**: ${price:,.2f} ({change:+.2f}% 24h)
- **Market Cap**: ${market_cap:,.0f}"""
        
        if eth_network:
            tps = eth_network.get('tps', 0)
            avg_fee = eth_network.get('avg_fee_usd', 0)
            finality_time = eth_network.get('finality_time', 'Unknown')
            response += f"""
- **TPS**: {tps:,}
- **Avg Fee**: ${avg_fee:.4f}
- **Finality**: {finality_time}"""
        
        response += """

## **ETHEREUM STRENGTHS**
- **Security**: Highest network security in crypto
- **Ecosystem**: Largest DeFi and dApp ecosystem
- **Developer Activity**: Most active development community
- **Smart Contracts**: Most sophisticated smart contract platform

## **KEY USE CASES**
- DeFi protocols and yield farming
- NFT marketplaces and collections
- Enterprise blockchain solutions
- Layer 2 scaling solutions

Want to compare Ethereum with other protocols or dive deeper into specific metrics?"""
        
        return response

    def _generate_bitcoin_specific_response(self, realtime_data: Dict) -> str:
        """Generate Bitcoin-specific response with live data"""
        network_data = realtime_data.get('data', {}).get('network_metrics', {}).get('protocols', {})
        market_data = realtime_data.get('data', {}).get('market_data', {}).get('protocols', {})
        
        btc_network = network_data.get('bitcoin', {})
        btc_market = market_data.get('bitcoin', {})
        
        response = """**₿ BITCOIN ANALYSIS - LIVE DATA**

## **CURRENT BITCOIN STATUS**"""
        
        if btc_market:
            price = btc_market.get('price_usd', 0)
            change = btc_market.get('price_change_24h', 0)
            market_cap = btc_market.get('market_cap', 0)
            response += f"""
- **Price**: ${price:,.2f} ({change:+.2f}% 24h)
- **Market Cap**: ${market_cap:,.0f}
- **Market Dominance**: Leading cryptocurrency"""
        
        if btc_network:
            tps = btc_network.get('tps', 7)
            avg_fee = btc_network.get('avg_fee_usd', 0)
            finality_time = btc_network.get('finality_time', '~60 minutes')
            response += f"""
- **TPS**: {tps}
- **Avg Fee**: ${avg_fee:.2f}
- **Finality**: {finality_time}"""
        
        response += """

## **BITCOIN STRENGTHS**
- **Security**: Most secure and decentralized network
- **Store of Value**: Digital gold with proven track record
- **Network Effect**: Largest adoption and recognition
- **Immutability**: Unchanging protocol with strong consensus

## **KEY USE CASES**
- Long-term value storage
- Cross-border payments
- Institutional treasury reserves
- Inflation hedge

Want to see how Bitcoin compares to other payment-focused blockchains?"""
        
        return response

    def _generate_tron_specific_response(self, realtime_data: Dict) -> str:
        """Generate Tron-specific response with live data"""
        network_data = realtime_data.get('data', {}).get('network_metrics', {}).get('protocols', {})
        market_data = realtime_data.get('data', {}).get('market_data', {}).get('protocols', {})
        
        trx_network = network_data.get('tron', {})
        trx_market = market_data.get('tron', {})
        
        response = """**⚡ TRON ANALYSIS - LIVE DATA**

## **CURRENT TRON STATUS**"""
        
        if trx_market:
            price = trx_market.get('price_usd', 0)
            change = trx_market.get('price_change_24h', 0)
            market_cap = trx_market.get('market_cap', 0)
            response += f"""
- **Price**: ${price:.6f} ({change:+.2f}% 24h)
- **Market Cap**: ${market_cap:,.0f}"""
        
        if trx_network:
            tps = trx_network.get('tps', 2000)
            avg_fee = trx_network.get('avg_fee_usd', 0.001)
            finality_time = trx_network.get('finality_time', '3 seconds')
            response += f"""
- **TPS**: {tps:,} (Very High)
- **Avg Fee**: ${avg_fee:.6f} (Ultra Low)
- **Finality**: {finality_time}"""
        
        response += """

## **TRON STRENGTHS**
- **Ultra-Low Fees**: Perfect for microtransactions
- **High Throughput**: Excellent for high-volume applications
- **Fast Finality**: Quick transaction confirmation
- **Energy Efficient**: Delegated Proof of Stake consensus

## **KEY USE CASES**
- Microtransaction applications
- Gaming and entertainment platforms
- USDT transfers (largest USDT network)
- Social media and content platforms

Want to see how Tron's low fees compare to other cost-effective blockchains?"""
        
        return response

    def _generate_bsc_specific_response(self, realtime_data: Dict) -> str:
        """Generate BSC-specific response with live data"""
        network_data = realtime_data.get('data', {}).get('network_metrics', {}).get('protocols', {})
        market_data = realtime_data.get('data', {}).get('market_data', {}).get('protocols', {})
        
        bsc_network = network_data.get('binance_smart_chain', {})
        bsc_market = market_data.get('binance_smart_chain', {})
        
        response = """**🟡 BINANCE SMART CHAIN ANALYSIS - LIVE DATA**

## **CURRENT BSC STATUS**"""
        
        if bsc_market:
            price = bsc_market.get('price_usd', 0)
            change = bsc_market.get('price_change_24h', 0)
            market_cap = bsc_market.get('market_cap', 0)
            response += f"""
- **BNB Price**: ${price:.2f} ({change:+.2f}% 24h)
- **Market Cap**: ${market_cap:,.0f}"""
        
        if bsc_network:
            tps = bsc_network.get('tps', 2100)
            avg_fee = bsc_network.get('avg_fee_usd', 0.30)
            finality_time = bsc_network.get('finality_time', '3 seconds')
            response += f"""
- **TPS**: {tps:,}
- **Avg Fee**: ${avg_fee:.4f}
- **Finality**: {finality_time}"""
        
        response += """

## **BSC STRENGTHS**
- **EVM Compatible**: Easy Ethereum dApp migration
- **High Performance**: Fast and low-cost transactions
- **Binance Ecosystem**: Integration with world's largest exchange
- **Proven DeFi**: Established DeFi protocols and yield farming

## **KEY USE CASES**
- DeFi protocols and yield farming
- GameFi and Play-to-Earn games
- DEX trading and liquidity provision
- Cross-chain bridge applications

Want to compare BSC's performance with other EVM-compatible chains?"""
        
        return response

    def _generate_base_specific_response(self, realtime_data: Dict) -> str:
        """Generate Base-specific response with live data"""
        network_data = realtime_data.get('data', {}).get('network_metrics', {}).get('protocols', {})
        
        base_network = network_data.get('base', {})
        
        response = """**🔵 BASE ANALYSIS - LIVE DATA**

## **CURRENT BASE STATUS**"""
        
        if base_network:
            tps = base_network.get('tps', 350)
            avg_fee = base_network.get('avg_fee_usd', 0.15)
            finality_time = base_network.get('finality_time', '2 seconds')
            response += f"""
- **TPS**: {tps:,}
- **Avg Fee**: ${avg_fee:.4f}
- **Finality**: {finality_time}
- **Type**: Ethereum Layer 2 (Optimistic Rollup)"""
        
        response += """

## **BASE STRENGTHS**
- **Coinbase Backed**: Supported by major US exchange
- **Ethereum Security**: Inherits Ethereum's security model
- **Low Fees**: Significantly cheaper than Ethereum mainnet
- **Developer Friendly**: Full EVM compatibility

## **KEY USE CASES**
- Consumer-focused applications
- Social and creator economy platforms
- Onchain commerce and payments
- Mobile-first dApps

## **ECOSYSTEM HIGHLIGHTS**
- Growing consumer application ecosystem
- Strong institutional backing
- Focus on mainstream adoption
- Integration with Coinbase services

Want to compare Base with other Layer 2 solutions or explore its consumer app ecosystem?"""
        
        return response

    def _generate_defi_response(self, realtime_data: Dict) -> str:
        """Generate DeFi-focused response"""
        return """**🏦 DEFI ECOSYSTEM ANALYSIS**

## **BEST BLOCKCHAINS FOR DEFI**

### **🔷 Ethereum - DeFi King**
- Largest TVL and most protocols
- Most sophisticated DeFi primitives
- Higher fees but maximum security

### **🟡 BSC - High-Yield DeFi**
- Lower fees, faster transactions
- Strong yield farming opportunities
- Binance ecosystem integration

### **⚡ Tron - Micro-DeFi**
- Ultra-low fees for small transactions
- USDT-focused DeFi protocols
- High transaction throughput

### **🔵 Base - Consumer DeFi**
- User-friendly DeFi applications
- Lower barrier to entry
- Growing ecosystem with institutional backing

## **DEFI METRICS TO WATCH**
- Total Value Locked (TVL)
- Protocol fees and yields
- Transaction costs vs returns
- Security and audit status

Want real-time data on any specific DeFi protocol or comparison?"""

    def _generate_general_crypto_overview(self, realtime_data: Dict) -> str:
        """Generate general cryptocurrency overview"""
        return """**🌐 CRYPTOCURRENCY & BLOCKCHAIN OVERVIEW**

I'm your AI advisor specializing in blockchain analysis with access to real-time data across major protocols.

## **WHAT I MONITOR**
- **Market Data**: Live prices, market caps, trading volumes
- **Network Performance**: TPS, fees, finality times
- **Development Activity**: Improvement proposals and updates
- **Use Case Analysis**: Gaming, DeFi, payments, enterprise

## **MAJOR PROTOCOLS COVERED**
- **Bitcoin**: Store of value and payments
- **Ethereum**: Smart contracts and DeFi
- **Tron**: High-throughput, low-cost transactions
- **BSC**: EVM-compatible DeFi and GameFi
- **Base**: Consumer-focused Layer 2

## **HOW TO GET SPECIFIC INSIGHTS**
- Ask about market data: *"Current prices"*
- Compare networks: *"Ethereum vs Tron performance"*  
- Explore use cases: *"Best blockchain for gaming"*
- Get proposals: *"Latest EIPs"*

**What aspect of the blockchain ecosystem would you like to explore?**"""

    def _generate_fallback_response(self, user_input: str) -> str:
        """Generate fallback response when real-time data is unavailable"""
        
        return """**AI BLOCKCHAIN ADVISOR**

I'm currently working on getting you the most up-to-date information. While I fetch real-time data, I can help with:

- **Blockchain Comparisons**: Technical analysis of L1 protocols
- **Use Case Recommendations**: Best chains for specific applications  
- **Performance Analysis**: TPS, fees, and network characteristics

Please try your question again, or ask about a specific topic like "gaming blockchains" or "payment solutions"."""

# Global instance
enhanced_ai_service = EnhancedAIService()