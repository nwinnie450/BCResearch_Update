"""
Conversational AI Chat Interface Component
"""
import streamlit as st
import time
import pandas as pd
import re
from typing import List, Dict
from services.enhanced_ai_service import enhanced_ai_service
from utils.session_manager import update_search_filter

def render_chat_interface():
    """Render the main chat interface for AI conversation - compact"""
    
    st.markdown("### 💬 Ask Your Blockchain AI Advisor")
    
    # Initialize enhanced AI service with real-time data
    ai_service = enhanced_ai_service
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        display_chat_history()
    
    # Chat input section
    render_chat_input(ai_service)
    
    # Suggested queries section
    render_suggested_queries()

def display_chat_history():
    """Display the conversation history"""
    
    if not st.session_state.chat_messages:
        # Welcome message
        st.markdown("""
        <div class="chat-message bot-message">
            <strong>🤖 Enhanced AI Advisor:</strong> Hello! I'm your blockchain research specialist with 
            <strong>Improvement Proposal Analysis</strong> covering all L1 protocol developments.
            <br><br>
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <strong>⚠️ Note:</strong> Live data integration is currently in development. 
                Analysis is based on cached proposal data and may not reflect the most recent submissions.
            </div>
            I specialize in improvement proposal analysis including:
            <ul>
                <li><strong>📋 Latest Proposals:</strong> "Recent EIPs", "New TIPs", "BIP updates", "Development activity"</li>
                <li><strong>📊 Proposal Analytics:</strong> "Proposal counts by status", "Protocol comparison", "Trending proposals"</li>
                <li><strong>🔍 Deep Analysis:</strong> "Technical impact assessment", "Implementation complexity", "Community consensus"</li>
                <li><strong>⚡ Protocol Updates:</strong> "Major network upgrades", "Protocol improvements", "Breaking changes"</li>
                <li><strong>🏗️ Development Insights:</strong> "Active proposals", "Author analysis", "Category trends"</li>
                <li><strong>🎯 Strategic Planning:</strong> "Roadmap analysis", "Feature comparison", "Adoption tracking"</li>
            </ul>
            What improvement proposals would you like me to analyze?
        </div>
        """, unsafe_allow_html=True)
    
    # Display conversation history
    for message in st.session_state.chat_messages:
        if message["role"] == "user":
            st.markdown("**👤 You:**")
            st.markdown(f"> {message['content']}")
            st.markdown("")  # Add spacing
        else:
            # Display AI response with proper table rendering
            st.markdown("**🤖 AI Advisor:**")
            render_ai_response_with_tables(message["content"])
            st.markdown("---")  # Add divider after AI response

def render_ai_response_with_tables(content: str):
    """Render AI response with proper table formatting"""
    
    # For better compatibility, use Streamlit's native markdown with table support
    # This handles emojis and formatting better than pandas DataFrames
    
    # Check if content has tables and use appropriate rendering
    if '|' in content and '---' in content:
        # Content has tables - render with Streamlit markdown
        st.markdown(content)
    else:
        # No tables - regular markdown
        st.markdown(content)

def render_fee_comparison_tables(content: str):
    """Render the fee comparison with dedicated table components"""
    
    # Display title
    st.markdown("💸 **LOWEST FEE L1 PROTOCOLS - COMPREHENSIVE ANALYSIS**")
    
    # Main comparison table
    st.markdown("🏆 **TRANSACTION FEE COMPARISON**")
    
    fee_data = [
        {"Rank": "🥇", "Protocol": "Tron (TRX)", "Avg Fee": "$0.001", "TPS": "2,000", "Finality": "3s", "Security": "78/100", "Type": "L1", "Best Use Case": "Microtransactions"},
        {"Rank": "🥈", "Protocol": "Base (ETH)", "Avg Fee": "$0.15", "TPS": "350", "Finality": "2s", "Security": "92/100", "Type": "L2", "Best Use Case": "Consumer Apps"},
        {"Rank": "🥉", "Protocol": "BSC (BNB)", "Avg Fee": "$0.30", "TPS": "2,100", "Finality": "3s", "Security": "82/100", "Type": "L1", "Best Use Case": "High Volume Apps"},
        {"Rank": "4️⃣", "Protocol": "Bitcoin (BTC)", "Avg Fee": "$8.50", "TPS": "7", "Finality": "1h", "Security": "100/100", "Type": "L1", "Best Use Case": "Store of Value"},
        {"Rank": "5️⃣", "Protocol": "Ethereum (ETH)", "Avg Fee": "$12.50", "TPS": "15", "Finality": "12.8m", "Security": "98/100", "Type": "L1", "Best Use Case": "Smart Contracts"}
    ]
    
    df_fees = pd.DataFrame(fee_data)
    st.dataframe(df_fees, use_container_width=True)
    
    # Optimization guide table
    st.markdown("💡 **FEE OPTIMIZATION GUIDE**")
    
    optimization_data = [
        {"Transaction Value": "<$10 (Micro)", "Recommended Protocol": "Tron", "Why Choose": "0.01% fee ratio, ultra-cheap"},
        {"Transaction Value": "$10-$1,000", "Recommended Protocol": "Base", "Why Choose": "Good security/cost balance"},
        {"Transaction Value": "$1,000-$10,000", "Recommended Protocol": "BSC", "Why Choose": "High performance, proven ecosystem"},
        {"Transaction Value": ">$10,000", "Recommended Protocol": "Ethereum", "Why Choose": "Maximum security justifies fee"},
        {"Transaction Value": "Store Value", "Recommended Protocol": "Bitcoin", "Why Choose": "Ultimate security, payment focus"}
    ]
    
    df_optimization = pd.DataFrame(optimization_data)
    st.dataframe(df_optimization, use_container_width=True)
    
    # Summary recommendations
    st.markdown("""
**🎯 QUICK RECOMMENDATIONS:**
• **For Maximum Savings**: Choose **Tron** (299x cheaper than Ethereum)
• **For Balance**: Choose **Base** (83x cheaper than Ethereum, good security)
• **For High Volume Apps**: Choose **BSC** (41x cheaper than Ethereum, proven)
• **For Large Holdings**: **Ethereum** or **Bitcoin** (security over cost)

Would you like a detailed breakdown for any specific protocol or use case?
    """)

def render_chat_input(ai_service):
    """Render chat input and handle user messages"""
    
    # Pre-fill with use case if selected
    placeholder_text = "Ask about blockchain protocols..."
    initial_query = ""
    
    if st.session_state.selected_use_case:
        use_case = st.session_state.selected_use_case
        if use_case == "eips":
            placeholder_text = "Fetching latest Ethereum Improvement Proposals..."
            initial_query = "Show me the latest EIPs with their status"
        elif use_case == "l1_performance":
            placeholder_text = "Comparing L1 protocol performance..."
            initial_query = "Compare the performance of major L1 protocols: Ethereum, Bitcoin, Tron, BSC, and Base"
        else:
            placeholder_text = f"Researching {use_case}..."
            initial_query = f"Tell me about {use_case}"
        
        # Reset the use case selection
        st.session_state.selected_use_case = None
    
    # Chat input with form for Enter key support
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Your question:",
                value=initial_query,
                placeholder=placeholder_text,
                label_visibility="collapsed",
                help="Type your question and press Enter or click Send"
            )
        
        with col2:
            send_button = st.form_submit_button("Send 🚀", type="primary", use_container_width=True)
    
    # Process user input when form is submitted (Enter key or Send button)
    if send_button:
        if user_input.strip():
            process_user_message(user_input, ai_service)
            st.rerun()
        else:
            st.warning("Please enter a question or message.")

def process_user_message(user_input: str, ai_service):
    """Process user message and generate AI response with enhanced validation and error handling"""
    
    # Input validation
    if not user_input or not isinstance(user_input, str):
        st.warning("Please enter a valid question.")
        return
        
    # Clean and validate input
    cleaned_input = user_input.strip()
    if not cleaned_input:
        st.warning("Please enter a question or message.")
        return
        
    # Check for extremely long inputs
    if len(cleaned_input) > 1000:
        st.warning("Your message is too long. Please keep it under 1000 characters.")
        return
        
    # Check for potentially harmful content (basic validation)
    suspicious_patterns = ['<script', 'javascript:', 'eval(', 'exec(', 'import os', 'import sys']
    if any(pattern in cleaned_input.lower() for pattern in suspicious_patterns):
        st.error("Invalid input detected. Please ask a legitimate question about blockchain technology.")
        return
    
    # Add user message to history
    st.session_state.chat_messages.append({
        "role": "user",
        "content": cleaned_input
    })
    
    # Show typing indicator
    with st.spinner("🤖 AI is thinking..."):
        try:
            # Get AI response with timeout handling
            ai_response = ai_service.get_chat_response(cleaned_input, st.session_state.chat_messages)
            
            # Validate AI response
            if not ai_response:
                ai_response = "I'm sorry, I couldn't generate a response at the moment. Please try again."
            elif not isinstance(ai_response, str):
                ai_response = "I encountered an issue processing your request. Please try rephrasing your question."
            elif ai_response.strip() == "":
                ai_response = "I'm sorry, I couldn't generate a meaningful response. Please try rephrasing your question."
            elif len(ai_response) > 10000:
                # Truncate overly long responses
                ai_response = ai_response[:9500] + "\n\n*Response truncated for better readability. Please ask for specific details if needed.*"
            
            # Add AI response to history
            st.session_state.chat_messages.append({
                "role": "assistant", 
                "content": ai_response
            })
                
        except ConnectionError as e:
            error_msg = "I'm having trouble connecting to data sources. Please check your internet connection and try again."
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": error_msg
            })
            st.error("Connection error occurred. Please try again.")
            
        except TimeoutError as e:
            error_msg = "The request took too long to process. Please try a simpler question or try again later."
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": error_msg
            })
            st.error("Request timed out. Please try again.")
            
        except ValueError as e:
            error_msg = "I encountered an issue understanding your request. Please rephrase your question more clearly."
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": error_msg
            })
            st.warning("Please rephrase your question.")
            
        except Exception as e:
            # Log the actual error for debugging while showing user-friendly message
            print(f"Chat Interface Error: {str(e)}")
            error_msg = "I apologize, but I encountered an unexpected error. Please try rephrasing your question or contact support if the issue persists."
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": error_msg
            })
            st.error("An unexpected error occurred. Please try again.")

def format_recommendations(recommendations: List[Dict]) -> str:
    """Format blockchain recommendations for display with comprehensive details"""
    
    if not recommendations:
        return "I couldn't find any blockchain protocols matching your criteria. Try adjusting your requirements."
    
    formatted = "\n**📋 BLOCKCHAIN RECOMMENDATIONS - DETAILED ANALYSIS**\n\n"
    
    for i, rec in enumerate(recommendations[:3], 1):
        rank_emoji = ["🏆", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
        
        formatted += f"{rank_emoji} **{rec['name']}** (Match Score: {rec['score']}/100)\n"
        
        # Core Performance Metrics
        formatted += f"   📊 **PERFORMANCE METRICS:**\n"
        formatted += f"      • Throughput: {rec.get('tps', 'N/A'):,} TPS\n"
        formatted += f"      • Finality: {format_finality_time(rec.get('finality_time', 'N/A'))}\n"
        formatted += f"      • Average Fee: ${rec.get('avg_fee', 0):.4f}\n"
        formatted += f"      • Consensus: {rec.get('consensus', 'N/A')}\n\n"
        
        # Economic & Market Data
        if rec.get('market_cap') or rec.get('tvl'):
            formatted += f"   💰 **MARKET POSITION:**\n"
            if rec.get('market_cap'):
                formatted += f"      • Market Cap: ${rec['market_cap']:,}\n"
            if rec.get('tvl'):
                formatted += f"      • Total Value Locked: ${rec['tvl']:,}\n"
            formatted += f"      • Type: {rec.get('type', 'N/A')}\n\n"
        
        # Ecosystem & Development
        formatted += f"   🌟 **ECOSYSTEM HEALTH:**\n"
        formatted += f"      • Security Score: {rec.get('security_score', 'N/A')}/100\n"
        formatted += f"      • Ecosystem Score: {rec.get('ecosystem_score', 'N/A')}/100\n"
        if rec.get('active_developers'):
            formatted += f"      • Active Developers: {rec['active_developers']:,}\n"
        if rec.get('dapp_count'):
            formatted += f"      • dApp Count: {rec['dapp_count']:,}\n"
        formatted += "\n"
        
        # Use Cases & Suitability
        if rec.get('suitable_for'):
            formatted += f"   🎯 **OPTIMAL USE CASES:** {', '.join(rec['suitable_for']).title()}\n\n"
        
        # Reasoning & Recommendation
        formatted += f"   ✅ **WHY RECOMMENDED:** {rec.get('reasoning', 'Good match for your requirements')}\n"
        
        # Website link if available
        if rec.get('website'):
            formatted += f"   🔗 **Learn More:** {rec['website']}\n"
        
        formatted += f"\n{'─' * 60}\n\n"
    
    # Summary and next steps
    formatted += "**🔍 DETAILED COMPARISON:**\n"
    formatted += "| Protocol | TPS | Fee | Finality | Security |\n"
    formatted += "|----------|-----|-----|----------|----------|\n"
    
    for rec in recommendations[:3]:
        formatted += f"| {rec['name']} | {rec.get('tps', 'N/A'):,} | ${rec.get('avg_fee', 0):.4f} | {format_finality_time(rec.get('finality_time', 'N/A'))} | {rec.get('security_score', 'N/A')}/100 |\n"
    
    formatted += "\n**💡 NEXT STEPS:**\n"
    formatted += "• Want detailed technical specifications for any protocol?\n"
    formatted += "• Need implementation guidance or integration support?\n" 
    formatted += "• Interested in risk analysis or security audit results?\n"
    formatted += "• Would you like me to compare with other specific protocols?\n\n"
    formatted += "**Just ask!** I can provide deeper analysis on any aspect that interests you."
    
    return formatted

def format_finality_time(finality_value) -> str:
    """Format finality time for better readability"""
    if isinstance(finality_value, (int, float)):
        if finality_value < 1:
            return f"{finality_value*1000:.0f}ms"
        elif finality_value < 60:
            return f"{finality_value:.1f}s"
        else:
            minutes = finality_value // 60
            seconds = finality_value % 60
            if seconds > 0:
                return f"{int(minutes)}m {int(seconds)}s"
            else:
                return f"{int(minutes)}m"
    else:
        return str(finality_value)

def render_suggested_queries():
    """Render suggested query buttons focused on improvement proposals"""
    
    st.markdown("### 💡 Suggested Questions - Improvement Proposals")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**📋 Latest Proposals**")
        
        if st.button("📋 Show Latest Proposals", use_container_width=True, key="latest_proposals"):
            query = "Show me the latest proposals from all protocols"
            st.session_state.chat_input_counter = getattr(st.session_state, 'chat_input_counter', 0) + 1
            process_user_message(query, enhanced_ai_service)
            st.rerun()
        
        if st.button("🆕 Recent EIPs", use_container_width=True, key="recent_eips"):
            query = "Show me the latest Ethereum Improvement Proposals"
            st.session_state.chat_input_counter = getattr(st.session_state, 'chat_input_counter', 0) + 1
            process_user_message(query, enhanced_ai_service)
            st.rerun()
    
    with col2:
        st.markdown("**📊 Proposals by Status**")
        
        if st.button("✅ Final Proposals", use_container_width=True, key="final_proposals"):
            query = "Show me all proposals with Final status"
            st.session_state.chat_input_counter = getattr(st.session_state, 'chat_input_counter', 0) + 1
            process_user_message(query, enhanced_ai_service)
            st.rerun()
        
        if st.button("📝 Draft Proposals", use_container_width=True, key="draft_proposals"):
            query = "Show me all proposals with Draft status"
            st.session_state.chat_input_counter = getattr(st.session_state, 'chat_input_counter', 0) + 1
            process_user_message(query, enhanced_ai_service)
            st.rerun()
    
    with col3:
        st.markdown("**🔍 Protocol Specific**")
        
        if st.button("🟡 TRON Proposals", use_container_width=True, key="tron_proposals"):
            query = "Show me TRON Improvement Proposals (TIPs)"
            st.session_state.chat_input_counter = getattr(st.session_state, 'chat_input_counter', 0) + 1
            process_user_message(query, enhanced_ai_service)
            st.rerun()
        
        if st.button("🟠 Bitcoin Proposals", use_container_width=True, key="bitcoin_proposals"):
            query = "Show me Bitcoin Improvement Proposals (BIPs)"
            st.session_state.chat_input_counter = getattr(st.session_state, 'chat_input_counter', 0) + 1
            process_user_message(query, enhanced_ai_service)
            st.rerun()
    
    with col4:
        st.markdown("**📈 Simple Analysis**")
        
        if st.button("📊 Count by Protocol", use_container_width=True, key="count_by_protocol"):
            query = "How many proposals does each protocol have?"
            st.session_state.chat_input_counter = getattr(st.session_state, 'chat_input_counter', 0) + 1
            process_user_message(query, enhanced_ai_service)
            st.rerun()
        
        if st.button("📈 Status Summary", use_container_width=True, key="status_summary"):
            query = "Show me a summary of proposal statuses across all protocols"
            st.session_state.chat_input_counter = getattr(st.session_state, 'chat_input_counter', 0) + 1
            process_user_message(query, enhanced_ai_service)
            st.rerun()
    
    # Clear chat button
    st.markdown("---")
    if st.button("🗑️ Clear Conversation", type="secondary"):
        st.session_state.chat_messages = []
        st.session_state.current_recommendations = []
        st.rerun()