"""
Header Component for Blockchain Research AI Agent
"""
import streamlit as st
from config import APP_TITLE, APP_DESCRIPTION, VERSION

def render_header():
    """Render the main application header - compact single-row design"""
    
    st.markdown(f"""
      <div class="card" style="padding:12px 14px; position:sticky; top:0; z-index:5; backdrop-filter:saturate(180%) blur(6px);">
        <div style="display:flex;align-items:center;gap:10px;justify-content:space-between;">
          <div style="display:flex;align-items:center;gap:10px;">
            <span>🔗</span>
            <h2 style="margin:0;">{APP_TITLE}</h2>
          </div>
          <div style="display:flex;gap:8px;">
            <!-- Actions can be added here if needed -->
          </div>
        </div>
        <div class="muted" style="margin-top:2px;">{APP_DESCRIPTION} • v{VERSION}</div>
      </div>
    """, unsafe_allow_html=True)