"""
Custom CSS Styles for Blockchain Research AI Agent
Based on design specifications from DESIGN_SPEC.md
"""
import streamlit as st
from config import COLORS

def load_custom_css():
    """Load Ethereum-style professional CSS with overflow prevention"""
    
    css = """<style>
    :root {
      --eth-blue: #627EEA;
      --eth-blue-dark: #3849D6;
      --border: #E5E7EB;
      --muted: #64748B;
      --surface: #FFFFFF;
      --surface-2: #F7F9FC;
    }
    
    /* Use full width with tight padding */
    [data-testid="stAppViewContainer"] > .main {
      padding: 10px 14px 16px 14px !important;
      max-width: 100% !important;
      font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji','Segoe UI Emoji', 'Segoe UI Symbol';
    }
    [data-testid="stHeader"] { 
      height: 0; 
      background: transparent; 
    }
    
    /* Eliminate gaps between elements */
    .main .block-container {
      padding-top: 0 !important;
      padding-bottom: 0 !important;
    }
    .element-container {
      margin-bottom: 0 !important;
    }
    [data-testid="stMarkdownContainer"] {
      margin-bottom: 0 !important;
    }

    /* Compact vertical rhythm */
    div[data-testid="stVerticalBlock"] > div { 
      margin-bottom: 8px !important; 
    }
    [data-testid="column"] { 
      padding-left: 8px !important; 
      padding-right: 8px !important; 
    }

    /* BANNER (centered, Ethereum gradient) */
    .banner {
      background: linear-gradient(135deg, var(--eth-blue-dark) 0%, var(--eth-blue) 60%, #8BA1FF 100%);
      color: white;
      border-radius: 16px;
      padding: 16px 18px;
      border: 1px solid rgba(255,255,255,.22);
      box-shadow: 0 6px 18px rgba(17,24,39,.12);
    }
    .banner .inner {
      max-width: 1080px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      text-align: center;
    }
    .banner h2 {
      margin: 0;
      font-weight: 700;
      font-size: 22px;
      letter-spacing: .2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    @media (max-width: 900px) {
      .banner h2 { 
        white-space: normal; 
      }
    }
    .banner .protocols {
      color: rgba(255,255,255,0.95);
      font-size: 14px;
      margin: 4px 0;
      font-weight: 500;
    }
    .banner .sub {
      opacity: .95;
      font-size: 12.5px;
    }
    .banner {
      margin-bottom: 10px !important;
    }
    
    /* Collapse any empty header action containers */
    .header-actions:empty { 
      display: none !important; 
    }
    
    /* HORIZONTAL NAVIGATION TABS */
    .nav-tabs {
      margin: 8px 0 12px 0;
      padding: 0;
    }
    .nav-container {
      background: rgba(98, 126, 234, 0.1);
      border-radius: 12px;
      padding: 8px;
      border: 1px solid rgba(98, 126, 234, 0.2);
    }
    
    /* Debug: highlight any containers that might be creating empty space */
    [data-testid="stVerticalBlock"]:empty {
      display: none !important;
    }
    [data-testid="column"]:empty {
      display: none !important;
    }
    .element-container:empty {
      display: none !important;
    }
    
    .nav-tabs .stButton > button {
      background: transparent !important;
      color: var(--eth-blue) !important;
      border: 1px solid transparent !important;
      font-weight: 500 !important;
      font-size: 14px !important;
      padding: 10px 16px !important;
    }
    .nav-tabs .stButton > button:hover {
      background: rgba(98, 126, 234, 0.15) !important;
      border: 1px solid rgba(98, 126, 234, 0.3) !important;
      color: var(--eth-blue-dark) !important;
    }

    /* CARDS / SECTIONS */
    .card { 
      background: var(--surface); 
      border: 1px solid var(--border); 
      border-radius: 14px; 
      padding: 14px; 
    }
    .muted { 
      color: var(--muted); 
    }

    /* TABLES */
    [data-testid="stTable"] table { 
      width: 100% !important; 
    }
    [data-testid="stTable"] th, [data-testid="stTable"] td { 
      padding: 8px 10px !important; 
    }
    [data-testid="stTable"] thead { 
      position: sticky; 
      top: 70px; 
      z-index: 3; 
      background: #fff; 
    }
    [data-testid="stTable"] tbody tr:nth-child(even) { 
      background: var(--surface-2); 
    }

    /* BUTTONS (Ethereum-style blue) */
    .stButton > button {
      display: inline-flex; 
      align-items: center; 
      justify-content: center;
      gap: 6px;
      padding: 8px 12px !important;
      border-radius: 10px !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
      min-width: 0;
      background: linear-gradient(135deg, var(--eth-blue-dark), var(--eth-blue)) !important;
      color: white !important;
      border: none !important;
      font-weight: 500 !important;
      transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
      background: linear-gradient(135deg, var(--eth-blue), #8BA1FF) !important;
      box-shadow: 0 4px 12px rgba(98, 126, 234, 0.3) !important;
      transform: translateY(-1px) !important;
    }
    [data-testid="stSidebar"] .stButton > button {
      width: 100% !important; 
      font-size: 12px !important; 
      line-height: 1.1 !important;
      background: rgba(255,255,255,0.15) !important;
      color: white !important;
      border: 1px solid rgba(255,255,255,0.2) !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
      background: rgba(255,255,255,0.25) !important;
      border: 1px solid rgba(255,255,255,0.4) !important;
      transform: translateY(-1px) !important;
    }

    /* HIDE SIDEBAR (using horizontal tabs instead) */
    [data-testid="stSidebar"] { 
      display: none !important;
    }

    /* Small stat cards */
    .kpi { 
      background: var(--surface); 
      border: 1px solid var(--border); 
      border-radius: 14px; 
      padding: 16px; 
      text-align: center; 
    }
    .kpi .label { 
      color: var(--muted); 
      font-size: 12px; 
      margin-bottom: 6px; 
    }
    .kpi .value { 
      font-weight: 600; 
      font-size: 28px; 
    }

    /* Ellipsis utility classes */
    .ellipsis { 
      white-space: nowrap; 
      overflow: hidden; 
      text-overflow: ellipsis; 
      max-width: 100%; 
      display: inline-block; 
      vertical-align: bottom; 
    }
    .inline { 
      display: inline-flex; 
      align-items: center; 
      gap: 6px; 
      min-width: 0; 
    }

    </style>"""
    
    st.markdown(css, unsafe_allow_html=True)
