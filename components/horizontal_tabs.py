"""
Horizontal Navigation Tabs Component
"""
import streamlit as st

def render_horizontal_tabs():
    """Render horizontal navigation tabs under the banner"""
    
    # Define navigation options
    nav_options = [
        ("🏠", "Home"),
        ("💬", "Chat"), 
        ("📊", "Compare"),
        ("📈", "Analytics"),
        ("📋", "Proposals"),
        ("📅", "Schedule")
    ]
    
    # Create horizontal tabs layout
    st.markdown("""
    <div class="nav-tabs">
        <div class="nav-container">
    """, unsafe_allow_html=True)
    
    # Create columns for tabs
    cols = st.columns(len(nav_options))
    
    selected_page = None
    
    for i, (col, (icon, label)) in enumerate(zip(cols, nav_options)):
        with col:
            full_label = f"{icon} {label}"
            if st.button(full_label, key=f"nav_{label.lower()}", use_container_width=True):
                selected_page = full_label
                st.session_state.current_page = full_label
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Return current selection or default
    if selected_page:
        return selected_page
    elif hasattr(st.session_state, 'current_page'):
        return st.session_state.current_page
    else:
        return "🏠 Home"