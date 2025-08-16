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
        <h2>Top 5 L1 Blockchain Protocol Analysis</h2>
        <div class="protocols">
          <strong>Ethereum • Base • Tron • BSC • Bitcoin</strong>
        </div>
        <div class="sub">AI-powered research with live data & improvement proposals • v{VERSION}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)