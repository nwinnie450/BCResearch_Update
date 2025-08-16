"""
Custom CSS Styles for Blockchain Research AI Agent
Based on design specifications from DESIGN_SPEC.md
"""
import streamlit as st
from config import COLORS

def load_custom_css():
    """Load Ethereum-style professional CSS with overflow prevention"""
    
    css = f"""
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    :root{{
      --eth-blue:#627EEA;          /* Ethereum blue */
      --eth-blue-dark:#3849D6;     /* deeper tone for gradient */
      --border:#E5E7EB;
      --muted:#64748B;
      --surface:#FFFFFF;
      --surface-2:#F7F9FC;
    }}
    
    /* Use full width with tight padding (remove big white bands) */
    [data-testid="stAppViewContainer"] > .main{{
      padding:10px 14px 16px 14px !important;
      max-width:100% !important;
      font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji','Segoe UI Emoji', 'Segoe UI Symbol';
    }}
    [data-testid="stHeader"]{{ height:0; background:transparent; }}

    /* Compact vertical rhythm */
    div[data-testid="stVerticalBlock"] > div{{ margin-bottom:8px !important; }}
    [data-testid="column"]{{ padding-left:8px !important; padding-right:8px !important; }}

    /* ---------- BANNER (centered, Ethereum gradient) ---------- */
    .banner{{
      background: linear-gradient(135deg, var(--eth-blue-dark) 0%, var(--eth-blue) 60%, #8BA1FF 100%);
      color: white;
      border-radius: 16px;
      padding: 16px 18px;
      border: 1px solid rgba(255,255,255,.22);
      box-shadow: 0 6px 18px rgba(17,24,39,.12);
    }}
    .banner .inner{{
      max-width: 1080px;          /* centers content and prevents super-wide stretch */
      margin: 0 auto;              /* <- center */
      display: flex;
      flex-direction: column;
      align-items: center;         /* <- center title/subtitle */
      gap: 6px;
      text-align: center;          /* <- ensure text is centered */
    }}
    .banner h2{{
      margin: 0;
      font-weight: 700;
      font-size: 22px;
      letter-spacing: .2px;
      white-space: nowrap;         /* keep on one row on desktop */
      overflow: hidden;
      text-overflow: ellipsis;     /* avoid wrap/overflow if window is narrower */
    }}
    @media (max-width: 900px){{
      .banner h2{{ white-space: normal; }}    /* allow wrap on small screens */
    }}
    .banner .sub{{
      opacity: .95;
      font-size: 12.5px;
    }}

    /* ---------- CARDS / SECTIONS ---------- */
    .card{{ background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:14px; }}
    .muted{{ color:var(--muted); }}

    /* ---------- TABLES ---------- */
    [data-testid="stTable"] table{{ width:100% !important; }}
    [data-testid="stTable"] th,[data-testid="stTable"] td{{ padding:8px 10px !important; }}
    [data-testid="stTable"] thead{{ position: sticky; top: 70px; z-index: 3; background: #fff; }}
    [data-testid="stTable"] tbody tr:nth-child(even){{ background: var(--surface-2); }}

    /* ---------- BUTTONS (no overflow) ---------- */
    .stButton > button{{
      display: inline-flex; align-items:center; justify-content:center;
      gap: 6px;
      padding: 8px 12px !important;
      border-radius: 10px !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
      min-width: 0;
    }}
    [data-testid="stSidebar"] .stButton > button{{
      width:100% !important; font-size:12px !important; line-height:1.1 !important;
    }}

    /* ---------- SIDEBAR (slim & tidy) ---------- */
    [data-testid="stSidebar"]{{ min-width: 180px !important; max-width: 180px !important; }}
    [data-testid="stSidebar"] > div:first-child{{ padding:10px 8px !important; }}
    [data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{{ margin:6px 0 6px 0 !important; }}

    /* Small stat cards */
    .kpi{{ background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:16px; text-align:center; }}
    .kpi .label{{ color:var(--muted); font-size:12px; margin-bottom:6px; }}
    .kpi .value{{ font-weight:600; font-size:28px; }}

    /* Ellipsis utility classes */
    .ellipsis{{ white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width: 100%; display:inline-block; vertical-align:bottom; }}
    .inline{{ display:inline-flex; align-items:center; gap:6px; min-width:0; }}

    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
