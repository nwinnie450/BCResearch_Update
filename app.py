"""
Blockchain Research & Advisory AI Agent
Streamlit Application Main Entry Point
"""
import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import PAGE_CONFIG, APP_TITLE, APP_DESCRIPTION, VERSION, COLORS
from utils.session_manager import init_session_state
from components.sidebar import render_sidebar
from components.header import render_header
from components.chat_interface import render_chat_interface
from components.dashboard import render_dashboard
from components.comparison import render_comparison
from components.analytics import render_analytics
from components.proposals import render_proposals_interface
from styles.custom_css import load_custom_css

def main():
    """Main application entry point"""
    
    # Configure Streamlit page
    st.set_page_config(**PAGE_CONFIG)
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # Render header
    render_header()
    
    # Main layout - eliminate all gaps between sidebar and content
    with st.container():
        col1, col2 = st.columns([1, 5], gap="small")
        
        with col1:
            # Render sidebar navigation
            selected_page = render_sidebar()
        
        with col2:
            # Route to appropriate page based on selection
            if selected_page == "🏠 Home":
                render_home_page()
            elif selected_page == "💬 Chat":
                render_chat_interface()
            elif selected_page == "📊 Compare":
                render_comparison()
            elif selected_page == "📈 Analytics": 
                render_analytics()
            elif selected_page == "📋 Proposals":
                render_proposals_interface()
            else:
                render_home_page()

def render_home_page():
    """Render the main home/dashboard page"""
    
    # Hero section - compact
    st.markdown("""
    <div class="hero-section">
        <h1 style="text-align: center; color: #1E3A8A; margin-bottom: 0.25rem;">
            Top 5 L1 Blockchain Protocol Analysis
        </h1>
        <p style="text-align: center; color: #6B7280; font-size: 1rem; margin-bottom: 1rem;">
            <strong>Ethereum • Base • Tron • BSC • Bitcoin</strong><br>
            AI-powered research with live data & improvement proposals
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick action cards focused on Improvement Proposals and L1 protocols - compact
    st.markdown("### 🚀 Quick Start - Improvement Proposals & L1 Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Browse TIPs", use_container_width=True):
            st.session_state.current_page = "📋 Proposals"
            st.rerun()
    
    with col2:
        if st.button("🔗 Latest EIPs", use_container_width=True):
            st.session_state.selected_use_case = "eips"
            st.session_state.current_page = "💬 Chat"
            st.rerun()
    
    with col3:
        if st.button("⚡ L1 Performance", use_container_width=True):
            st.session_state.selected_use_case = "l1_performance"
            st.session_state.current_page = "💬 Chat"
            st.rerun()
    
    # Main dashboard content
    render_dashboard()

if __name__ == "__main__":
    main()