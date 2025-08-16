"""
Header Component for Blockchain Research AI Agent
"""
import streamlit as st
from config import APP_TITLE, APP_DESCRIPTION, VERSION

def render_header():
    """Render the main application header - Ethereum-style centered banner"""
    
    st.markdown(f"""
    <div class="banner">
      <div class="inner">
        <h2>{APP_TITLE}</h2>
        <div class="sub">{APP_DESCRIPTION} • v{VERSION}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)