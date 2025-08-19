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
from components.header import render_header, render_banner, render_banner_with_nav
from components.horizontal_tabs import render_horizontal_tabs
from components.chat_interface import render_chat_interface
from components.dashboard import render_dashboard
# Unified analytics replaces separate comparison and analytics components
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
    
    # Render header with fully integrated navigation (no separate containers)
    selected_page = render_banner_with_nav()
    
    
    # Main content area - full width
    if selected_page == "🏠 Home":
        render_home_page()
    elif selected_page == "💬 Chat":
        render_chat_interface()
    elif selected_page == "📊 Analytics":
        from components.unified_analytics import render_unified_analytics
        render_unified_analytics()
    elif selected_page == "📋 Proposals":
        render_proposals_interface()
    elif selected_page == "📅 Schedule":
        from components.simple_schedule_manager import render_simple_schedule_manager
        render_simple_schedule_manager()
    elif selected_page == "⚙️ Settings":
        from components.settings_page import render_settings_page
        render_settings_page()
    else:
        render_home_page()

def render_home_page():
    """Render the main home/dashboard page"""
    
    # Compact top toolbar with no overflow buttons  
    st.markdown("### 🚀 Quick Start - Proposals, Analytics & Research")
    
    c1, c2, c3 = st.columns([0.33, 0.33, 0.34])
    
    with c1:
        if st.button("📚 Browse TIPs", use_container_width=True):
            st.session_state.current_page = "📋 Proposals"
            st.rerun()
    
    with c2:
        if st.button("🔗 Latest EIPs", use_container_width=True):
            st.session_state.selected_use_case = "eips"
            st.session_state.current_page = "💬 Chat"
            st.rerun()
    
    with c3:
        if st.button("📊 Analytics Hub", use_container_width=True):
            st.session_state.current_page = "📊 Analytics"
            st.rerun()
    
    # Main dashboard content
    render_dashboard()

if __name__ == "__main__":
    main()