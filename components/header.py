"""
Header Component for Blockchain Research AI Agent
"""
import streamlit as st
from config import APP_TITLE, APP_DESCRIPTION, VERSION

def render_banner_with_nav():
    """Render banner with integrated navigation buttons"""
    
    st.markdown(f"""
    <div class="banner">
      <div class="inner">
        <h2>Top 5 L1 Blockchain Protocol Analysis</h2>
        <div class="protocols">
          <strong>Ethereum • Base • Tron • BSC • Bitcoin</strong>
        </div>
        <div class="sub">AI-powered research with live data & improvement proposals • v{VERSION}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons immediately after banner with no container gap - unified analytics
    nav_cols = st.columns(5)
    nav_options = [
        ("🏠", "Home"),
        ("💬", "Chat"), 
        ("📊", "Analytics"),  # Unified: Analyze + Compare + Data Management
        ("📋", "Proposals"),
        ("📅", "Schedule")
    ]
    
    selected_page = None
    for i, (col, (icon, label)) in enumerate(zip(nav_cols, nav_options)):
        with col:
            full_label = f"{icon} {label}"
            if st.button(full_label, key=f"nav_{label.lower()}", use_container_width=True):
                selected_page = full_label
                st.session_state.current_page = full_label
    
    # Return current selection or default
    if selected_page:
        return selected_page
    elif hasattr(st.session_state, 'current_page'):
        return st.session_state.current_page
    else:
        return "🏠 Home"

def render_banner(actions_fn=None, include_tabs=True):
    """Render Ethereum-style centered banner with optional actions and tabs"""
    
    st.markdown(f"""
    <div class="banner">
      <div class="inner">
        <h2>Top 5 L1 Blockchain Protocol Analysis</h2>
        <div class="protocols">
          <strong>Ethereum • Base • Tron • BSC • Bitcoin</strong>
        </div>
        <div class="sub">AI-powered research with live data & improvement proposals • v{VERSION}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Include navigation tabs right after banner (no gap)
    if include_tabs:
        from components.horizontal_tabs import render_horizontal_tabs
        return render_horizontal_tabs()
    
    # Only render an actions column when actions exist
    if actions_fn:
        col_gap, col_actions = st.columns([0.80, 0.20])
        with col_actions:
            actions_fn()  # e.g., draw a real button/search here
    
    return None

def render_header(actions_fn=None):
    """Legacy function for backwards compatibility"""
    render_banner(actions_fn)