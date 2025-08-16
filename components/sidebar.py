"""
Sidebar Navigation Component
"""
import streamlit as st

def render_sidebar():
    """Render the sidebar navigation menu - compact"""
    
    with st.sidebar:
        st.markdown("### 🎯 Navigation")
        
        # Simple radio button navigation (fallback if streamlit-option-menu not available)
        selected = st.radio(
            "Choose a page:",
            ["🏠 Home", "💬 Chat", "📊 Compare", "📈 Analytics", "📋 Proposals", "📅 Schedule Manager"],
            index=0,
            label_visibility="collapsed"
        )
        
        # Quick Actions section - compact with shorter labels
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("Latest TIPs", use_container_width=True):
            st.session_state.current_page = "📋 Proposals"
            selected = "📋 Proposals"
        
        if st.button("Latest EIPs", use_container_width=True):
            st.session_state.selected_use_case = "eips"
            st.session_state.current_page = "💬 Chat"
            selected = "💬 Chat"
        
        if st.button("L1 Performance", use_container_width=True):
            st.session_state.selected_use_case = "l1_performance"
            st.session_state.current_page = "💬 Chat"
            selected = "💬 Chat"
        
        # Settings section - compact
        st.markdown("### ⚙️ Settings")
        
        with st.expander("Preferences", expanded=False):
            st.slider("TPS Priority", 0.0, 1.0, 0.25, key="tps_weight")
            st.slider("Fee Priority", 0.0, 1.0, 0.25, key="fee_weight")
            st.slider("Security Priority", 0.0, 1.0, 0.25, key="security_weight")
            st.slider("Ecosystem Priority", 0.0, 1.0, 0.25, key="ecosystem_weight")
        
        # Information section - compact
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Top 5 L1 Protocol Research Hub** - Focused analysis of the leading blockchain protocols using AI-powered research and live data.
        
        **Protocols:**
        - 🟠 **Bitcoin** - Original blockchain
        - 🔵 **Ethereum** - Smart contract leader  
        - ⚡ **Base** - Coinbase L2 solution
        - 🟡 **Tron** - High-speed transactions
        - 🟨 **BSC** - Binance ecosystem
        
        **Features:**
        - 📋 Live improvement proposals
        - 📊 Real-time performance data
        - 🔗 Protocol comparisons
        """)
        
        # Update session state
        st.session_state.current_page = selected
        
        return selected