"""
Custom CSS Styles for Blockchain Research AI Agent
Based on design specifications from DESIGN_SPEC.md
"""
import streamlit as st
from config import COLORS

def load_custom_css():
    """Load ultra-compact CSS styles for the application"""
    
    css = f"""
    <style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* ====== OPTIMIZED COMPACT LAYOUT FIXES ====== */
    /* Use full width & tight padding */
    [data-testid="stAppViewContainer"] > .main {{
      padding: 8px 12px 12px 12px !important;
      max-width: 100% !important;
    }}
    
    /* Remove Streamlit top spacer */
    [data-testid="stHeader"] {{ 
      height: 0; 
      background: transparent; 
    }}

    /* Single-line headings with compact margins */
    h1, h2, h3 {{ 
      white-space: nowrap; 
      margin: 6px 0 8px 0 !important; 
    }}

    /* Reduce vertical gaps between blocks */
    div[data-testid="stVerticalBlock"] > div {{ 
      margin-bottom: 6px !important; 
    }}

    /* Columns + tables tighter */
    [data-testid="column"] {{ 
      padding-left: 6px !important; 
      padding-right: 6px !important; 
    }}
    [data-testid="stTable"] table {{ 
      width: 100% !important; 
    }}
    [data-testid="stTable"] th, [data-testid="stTable"] td {{ 
      padding: 6px 8px !important; 
    }}

    /* Sidebar: slimmer rail + no overflow on buttons */
    [data-testid="stSidebar"] {{ 
      min-width: 168px !important; 
      max-width: 168px !important; 
    }}
    [data-testid="stSidebar"] > div:first-child {{ 
      padding: 8px 6px !important; 
    }}
    [data-testid="stSidebar"] .stButton > button {{
      width: 100% !important; 
      font-size: 12px !important; 
      line-height: 1.05 !important;
      padding: 6px 8px !important; 
      border-radius: 8px !important;
      white-space: nowrap !important; 
      overflow: hidden !important; 
      text-overflow: ellipsis !important;
    }}
    [data-testid="stSidebar"] .stButton {{ 
      margin-bottom: 6px !important; 
    }}

    /* Cards for sections (less "floating on white" look) */
    .card {{ 
      background: #fff; 
      border: 1px solid #E5E7EB; 
      border-radius: 14px; 
      padding: 14px; 
    }}
    .muted {{ 
      color: #64748B; 
    }}

    /* Table polish - zebra rows + sticky header */
    [data-testid="stTable"] thead {{ 
      position: sticky; 
      top: 62px; 
      z-index: 3; 
      background: #fff; 
    }}
    [data-testid="stTable"] tbody tr:nth-child(even) {{ 
      background: #FAFAFB; 
    }}
    
    /* ====== LEGACY FALLBACK STYLES ====== */
    main [data-testid="block-container"], .block-container {{
      padding-top: 8px !important;
      padding-bottom: 10px !important;
      padding-left: 12px !important;
      padding-right: 12px !important;
      max-width: 100% !important;   /* kill centered narrow layout */
    }}

    /* Headline spacing + single line */
    h1, h2, h3 {{ margin-top: .4rem !important; margin-bottom: .6rem !important; white-space: nowrap; }}

    /* Remove default vertical gaps between Streamlit blocks */
    div[data-testid="stVerticalBlock"] > div {{ margin-bottom: 6px !important; }}

    /* Columns tighter */
    [data-testid="column"] {{ padding-left: 6px !important; padding-right: 6px !important; }}

    /* Tables edge-to-edge + compact cells */
    [data-testid="stTable"] table {{ width: 100% !important; }}
    [data-testid="stTable"] th, [data-testid="stTable"] td {{ padding: 6px 8px !important; }}

    /* ====== SIDEBAR: MAKE IT SLIM + FIX BUTTON OVERFLOW ====== */
    [data-testid="stSidebar"] {{
      min-width: 190px !important;
      max-width: 190px !important;   /* adjust to taste */
    }}
    [data-testid="stSidebar"] > div:first-child {{ padding: 8px 6px !important; }}

    /* Sidebar section headers tighter */
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
      margin: 6px 0 6px 0 !important;
    }}

    /* Sidebar radio/checkbox rows tighter */
    [data-testid="stSidebar"] label {{ margin-bottom: 2px !important; }}

    /* Quick Actions buttons: smaller font, single line, no overflow */
    [data-testid="stSidebar"] .stButton > button {{
      width: 100% !important;
      font-size: 12px !important;
      line-height: 1.1 !important;
      padding: 6px 8px !important;
      border-radius: 8px !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
    }}

    /* Give the Quick Actions button row a fixed height so the blue box fits the text */
    [data-testid="stSidebar"] .stButton {{ margin-bottom: 6px !important; }}

    /* ====== HEADER ROW: REMOVE DEAD SPACE ON THE RIGHT ====== */
    .header-row {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
    .header-left  {{ display:flex; align-items:center; gap:10px; }}
    .header-right > * {{ margin-left: 8px; }}
    
    /* GRID SYSTEM - Compact layout */
    :root {{
        --grid-unit: 4px;
        --grid-2x: 8px;
        --grid-3x: 12px;
        --grid-4x: 16px;
        --grid-6x: 24px;
        --grid-8x: 32px;
        --section-gap: 24px;
        --content-gap: 12px;
        --line-height-base: 1.4;
        --line-height-tight: 1.2;
    }}
    
    /* Global Styles - Compact layout */
    .main {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        width: 100vw;
        max-width: 100vw;
        margin: 0;
        padding: 0;
        line-height: var(--line-height-base);
    }}
    
    /* Content container - Proper spacing to show header */
    .block-container {{
        padding: var(--grid-4x) var(--grid-3x) var(--grid-2x) var(--grid-3x) !important;
        max-width: 100% !important;
        margin: 0 !important;
        width: 100% !important;
        box-sizing: border-box;
    }}
    
    /* Main content - Proper spacing for header visibility */
    .main .block-container {{
        display: block;
        width: 100%;
        max-width: 100%;
        padding: var(--grid-3x) var(--grid-3x);
        box-sizing: border-box;
        margin: 0;
        padding-top: var(--grid-4x) !important;
    }}
    
    /* Override Streamlit's container restrictions */
    .stApp > div:first-child {{
        width: 100% !important;
        max-width: 100% !important;
    }}
    
    [data-testid="stAppViewContainer"] {{
        width: 100% !important;
        max-width: 100% !important;
    }}
    
    /* Section spacing system - Reduced */
    .section {{
        margin-bottom: var(--section-gap);
    }}
    
    .section:last-child {{
        margin-bottom: 0;
    }}
    
    /* COMPONENT ALIGNMENT SYSTEM - Compact */
    
    /* Content sections - compact spacing */
    .stMarkdown, .stDataFrame, .stPlotlyChart, .stMetric {{
        width: 100%;
        margin-bottom: var(--content-gap);
        box-sizing: border-box;
    }}
    
    /* Form elements - compact */
    .stForm {{
        max-width: 800px;
        margin: var(--content-gap) auto;
        padding: var(--grid-3x);
        width: 100%;
        box-sizing: border-box;
    }}
    
    /* BUTTON SYSTEM - Compact spacing */
    .button-group {{
        display: flex;
        justify-content: center;
        gap: var(--grid-3x);
        margin: var(--grid-2x) 0 var(--content-gap) 0;
        flex-wrap: wrap;
    }}
    
    .stButton {{
        margin: 0;
        flex: 0 0 auto;
    }}
    
    /* Equal width buttons in column layouts */
    .stColumns .stButton {{
        width: 100%;
        margin: var(--grid-unit) 0;
    }}
    
    /* COLUMN SYSTEM - Compact gaps */
    .stColumn {{
        padding: 0 calc(var(--grid-2x) / 2) !important;
        box-sizing: border-box;
    }}
    
    .stColumn > div {{
        height: 100%;
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
    }}
    
    /* Compact column spacing - no gaps */
    .stColumns {{
        gap: 0 !important;
        margin-bottom: var(--content-gap);
        margin: 0 !important;
        padding: 0 !important;
    }}
    
    .stColumns > div {{
        height: 100%;
        display: flex;
        flex-direction: column;
    }}
    
    /* Adjust default Streamlit spacing */
    .stApp {{
        margin-top: 0px;
        padding-top: var(--grid-2x);
    }}
    
    /* TYPOGRAPHY SYSTEM - Compact and prominent */
    
    /* Main title - compact */
    h1, .stMarkdown h1 {{
        font-size: 2.25rem !important;
        margin: 0 0 var(--grid-3x) 0 !important;
        line-height: var(--line-height-tight) !important;
        text-align: left !important;
        font-weight: 700 !important;
        width: 100%;
        display: flex;
        align-items: center;
        gap: var(--grid-3x);
    }}
    
    /* Section headings - compact */
    h2, .stMarkdown h2 {{
        font-size: 1.75rem !important;
        margin: var(--grid-4x) 0 var(--grid-2x) 0 !important;
        line-height: var(--line-height-tight) !important;
        text-align: left !important;
        font-weight: 600 !important;
        width: 100%;
        display: flex;
        align-items: center;
        gap: var(--grid-3x);
    }}
    
    h2:first-child {{
        margin-top: 0 !important;
    }}
    
    /* Subsection headings - compact */
    h3, .stMarkdown h3 {{
        font-size: 1.375rem !important;
        margin: var(--grid-3x) 0 var(--grid-2x) 0 !important;
        line-height: var(--line-height-tight) !important;
        text-align: left !important;
        font-weight: 600 !important;
        width: 100%;
        display: flex;
        align-items: center;
        gap: var(--grid-3x);
    }}
    
    /* Card titles - compact */
    h4, .stMarkdown h4 {{
        font-size: 1.125rem !important;
        margin: var(--grid-2x) 0 var(--grid-unit) 0 !important;
        line-height: var(--line-height-tight) !important;
        text-align: left !important;
        font-weight: 500 !important;
        width: 100%;
    }}
    
    /* Paragraph text - compact */
    p, .stMarkdown p {{
        font-size: 1rem !important;
        line-height: var(--line-height-base) !important;
        margin: 0 0 var(--grid-2x) 0 !important;
        width: 100%;
        text-align: left;
    }}
    
    /* Icon + text alignment in headings */
    h1 .icon, h2 .icon, h3 .icon {{
        display: inline-flex;
        align-items: center;
        font-size: 0.9em;
    }}
    
    /* Enhanced metrics - compact */
    .stMetric {{
        background: white;
        padding: var(--grid-3x) !important;
        border-radius: var(--grid-2x);
        border: 1px solid #e5e7eb;
        margin-bottom: var(--grid-2x) !important;
        min-height: 100px;
    }}
    
    .stMetric > div {{
        gap: var(--grid-unit) !important;
    }}
    
    .stMetric [data-testid="metric-container"] {{
        padding: var(--grid-2x) !important;
    }}
    
    .stMetric label {{
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }}
    
    .stMetric [data-testid="metric-container"] > div {{
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }}
    
    /* Metric values - compact */
    .stMetric [data-testid="metric-container"] > div:first-child {{
        font-size: 1.875rem !important;
        font-weight: 700 !important;
    }}
    
    /* Header Styles - Compact and Centered with proper spacing */
    .main-header {{
        background: linear-gradient(90deg, {COLORS['primary_blue']} 0%, {COLORS['secondary_blue']} 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin: var(--grid-2x) 0 1rem 0;
        text-align: center;
        width: 100%;
        box-sizing: border-box;
        position: relative;
        z-index: 1;
    }}
    
    .main-header h1 {{
        margin: 0 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        justify-content: center !important;
        width: 100% !important;
        line-height: 1.2 !important;
    }}
    
    .main-header p {{
        margin: 0.5rem 0 0 0 !important;
        font-size: 1.1rem !important;
        opacity: 0.9;
        text-align: center !important;
        width: 100% !important;
    }}
    
    /* Compact Hero Section - Centered and Full Width */
    .hero-section {{
        text-align: center;
        padding: 1rem;
        background: {COLORS['light_blue']};
        border-radius: 8px;
        margin-bottom: 0.75rem;
        border: 1px solid {COLORS['secondary_blue']}20;
        width: 100%;
        box-sizing: border-box;
        margin-left: 0;
        margin-right: 0;
    }}
    
    .hero-section h1 {{
        font-size: 1.375rem !important;
        margin-bottom: 0.25rem !important;
        line-height: 1.2 !important;
        text-align: center !important;
        width: 100%;
    }}
    
    .hero-section p {{
        font-size: 0.875rem !important;
        margin-bottom: 0.25rem !important;
        line-height: 1.3 !important;
        text-align: center !important;
        width: 100%;
    }}
    
    /* Fix left-hand side spacing issues */
    .main .block-container {{
        padding: var(--grid-2x) var(--grid-3x) !important;
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        box-sizing: border-box;
    }}
    
    /* Ensure content sections are properly aligned */
    .stMarkdown, .stDataFrame, .stPlotlyChart, .stMetric {{
        width: 100% !important;
        margin-bottom: var(--content-gap) !important;
        box-sizing: border-box;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }}
    
    /* Fix column alignment - eliminate gaps */
    .stColumn {{
        padding: 0 !important;
        box-sizing: border-box;
        margin: 0 !important;
        gap: 0 !important;
    }}
    
    /* Eliminate gaps between columns */
    .stColumns {{
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    
    /* Ensure no spacing between sidebar and main content */
    .stColumns > div:first-child {{
        padding-right: 0 !important;
        margin-right: 0 !important;
    }}
    
    .stColumns > div:last-child {{
        padding-left: 0 !important;
        margin-left: 0 !important;
    }}
    
    /* Ensure buttons are properly centered */
    .stButton {{
        margin: 0 !important;
        flex: 0 0 auto;
        width: 100% !important;
    }}
    
    .stButton > button {{
        width: 100% !important;
        margin: var(--grid-2x) 0 !important;
    }}
    
    /* Fix main content alignment */
    .main {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: var(--line-height-base);
        box-sizing: border-box;
    }}
    
    /* Override any Streamlit default margins */
    .stApp > div:first-child {{
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    
    [data-testid="stAppViewContainer"] {{
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    
    /* Fix container margins */
    .block-container {{
        padding: var(--grid-2x) var(--grid-3x) !important;
        max-width: 100% !important;
        margin: 0 !important;
        width: 100% !important;
        box-sizing: border-box;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }}
    
    /* Eliminate gap between sidebar and main content */
    .main .block-container {{
        padding-left: var(--grid-2x) !important;
        margin-left: 0 !important;
    }}
    
    /* Ensure sidebar and main content are connected */
    .stSidebar {{
        margin-right: 0 !important;
        padding-right: 0 !important;
    }}
    
    /* Main content area - no left margin */
    .main > div:last-child {{
        margin-left: 0 !important;
        padding-left: 0 !important;
    }}
    
    /* Additional fixes for dashboard content alignment */
    .stMarkdown h3, .stMarkdown h4 {{
        margin-left: 0 !important;
        margin-right: 0 !important;
        width: 100% !important;
    }}
    
    /* Target main layout columns specifically */
    .main .stColumns {{
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    
    /* Ensure main content starts immediately after sidebar */
    .main .stColumns > div:last-child {{
        padding-left: 0 !important;
        margin-left: 0 !important;
        border-left: none !important;
    }}
    
    /* Remove any Streamlit default spacing */
    .stApp [data-testid="stSidebar"] + div {{
        margin-left: 0 !important;
        padding-left: 0 !important;
    }}
    
    /* Container-specific gap elimination */
    .stContainer .stColumns {{
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    
    /* Ensure container columns have no gaps */
    .stContainer .stColumn {{
        padding: 0 !important;
        margin: 0 !important;
        gap: 0 !important;
    }}
    
    /* Fix any remaining left margin issues */
    .stMarkdown > div {{
        margin-left: 0 !important;
        margin-right: 0 !important;
        width: 100% !important;
    }}
    
    /* Ensure dashboard sections are properly aligned */
    .dashboard-section {{
        width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }}
    
    /* Fix column content alignment */
    .stColumn > div {{
        width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }}
    
    /* Card Styles - Compact */
    .recommendation-card {{
        background: {COLORS['white']};
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }}
    
    .recommendation-card:hover {{
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
        border-color: {COLORS['secondary_blue']};
    }}
    
    .protocol-card {{
        background: {COLORS['white']};
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 0.75rem;
        margin: 0.25rem 0;
        transition: all 0.2s ease;
    }}
    
    .protocol-card:hover {{
        border-color: {COLORS['secondary_blue']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    
    /* Ranking Badges - Compact */
    .rank-badge {{
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.8rem;
        margin-right: 0.4rem;
    }}
    
    .rank-1 {{
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #8B4513;
    }}
    
    .rank-2 {{
        background: linear-gradient(135deg, #C0C0C0, #A0A0A0);
        color: #4A4A4A;
    }}
    
    .rank-3 {{
        background: linear-gradient(135deg, #CD7F32, #B87333);
        color: #FFFFFF;
    }}
    
    .rank-other {{
        background: {COLORS['light_gray']};
        color: {COLORS['medium_gray']};
    }}
    
    /* Chat Interface Styles - Compact */
    .chat-container {{
        background: {COLORS['white']};
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}
    
    .chat-message {{
        padding: 0.5rem 0.75rem;
        margin: 0.25rem 0;
        border-radius: 6px;
        max-width: 85%;
    }}
    
    .user-message {{
        background: {COLORS['secondary_blue']};
        color: white;
        margin-left: auto;
        text-align: right;
    }}
    
    .bot-message {{
        background: {COLORS['light_gray']};
        color: {COLORS['dark_gray']};
        margin-right: auto;
    }}
    
    /* Metric Cards - Compact */
    .metric-card {{
        background: {COLORS['white']};
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 0.75rem;
        text-align: center;
        transition: all 0.2s ease;
    }}
    
    .metric-card:hover {{
        border-color: {COLORS['secondary_blue']};
        transform: translateY(-1px);
    }}
    
    .metric-value {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {COLORS['primary_blue']};
        margin-bottom: 0.2rem;
    }}
    
    .metric-label {{
        font-size: 0.8rem;
        color: {COLORS['medium_gray']};
        text-transform: uppercase;
        font-weight: 500;
        letter-spacing: 0.5px;
    }}
    
    /* Status Indicators */
    .status-high {{
        color: {COLORS['success_green']};
        font-weight: 600;
    }}
    
    .status-medium {{
        color: {COLORS['warning_orange']};
        font-weight: 600;
    }}
    
    .status-low {{
        color: {COLORS['danger_red']};
        font-weight: 600;
    }}
    
    /* Comparison Table Styles - Compact */
    .comparison-table {{
        background: {COLORS['white']};
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }}
    
    .comparison-table th {{
        background: {COLORS['primary_blue']};
        color: white;
        padding: 0.5rem 0.75rem;
        font-weight: 600;
    }}
    
    .comparison-table td {{
        padding: 0.5rem 0.75rem;
        border-bottom: 1px solid #f3f4f6;
    }}
    
    /* BUTTON SYSTEM - Compact buttons */
    .stButton > button {{
        background: {COLORS['secondary_blue']};
        color: white;
        border: none;
        border-radius: var(--grid-2x);
        padding: var(--grid-2x) var(--grid-3x) !important;
        font-weight: 500;
        font-size: 1rem !important;
        height: var(--grid-6x) !important;
        min-width: 140px;
        transition: all 0.2s ease;
        margin: var(--grid-2x) 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        box-sizing: border-box;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .stButton > button:hover {{
        background: {COLORS['primary_blue']};
        transform: translateY(-2px);
        box-shadow: 0 var(--grid-2x) var(--grid-3x) rgba(0,0,0,0.2);
    }}
    
    /* Button groups - equal width in rows */
    .stColumns .stButton {{
        width: 100%;
    }}
    
    .stColumns .stButton > button {{
        width: 100%;
        min-width: unset;
    }}
    
    /* Compact sidebar */
    .css-1d391kg, .css-1v3fvcr {{
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }}
    
    /* Sidebar content should remain left-aligned */
    .sidebar .stMarkdown, .sidebar .stRadio, .sidebar .stButton {{
        text-align: left !important;
    }}
    
    /* Override center alignment for sidebar */
    [data-testid="stSidebar"] * {{
        text-align: left !important;
    }}
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {{
        text-align: left !important;
    }}
    
    /* Compact radio buttons */
    .stRadio > div {{
        gap: 0.2rem !important;
    }}
    
    .stRadio label {{
        font-size: 0.85rem !important;
        padding: 0.2rem 0 !important;
    }}
    
    /* Compact selectbox */
    .stSelectbox > div > div {{
        font-size: 0.85rem !important;
    }}
    
    /* Compact text input */
    .stTextInput > div > div > input {{
        font-size: 0.85rem !important;
        padding: 0.3rem 0.5rem !important;
    }}
    
    /* Compact columns spacing */
    .stColumn {{
        padding: 0 0.4rem !important;
    }}
    
    /* DATA TABLE SYSTEM - Compact tables */
    .stDataFrame {{
        font-size: 1rem !important;
        margin: var(--grid-3x) auto !important;
        text-align: center !important;
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto;
        border-radius: var(--grid-2x);
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    
    .stDataFrame th {{
        font-size: 0.9rem !important;
        padding: var(--grid-2x) var(--grid-2x) !important;
        text-align: center !important;
        font-weight: 600 !important;
        background: {COLORS['light_gray']};
        height: var(--grid-6x);
        vertical-align: middle;
    }}
    
    .stDataFrame td {{
        padding: var(--grid-2x) var(--grid-2x) !important;
        text-align: center !important;
        height: var(--grid-4x);
        vertical-align: middle;
        border-bottom: 1px solid #f3f4f6;
        font-size: 0.95rem !important;
    }}
    
    /* CHART SYSTEM - Compact sizing */
    .stPlotlyChart {{
        width: 100% !important;
        max-width: 100% !important;
        margin: var(--grid-2x) auto !important;
        text-align: center !important;
        border-radius: var(--grid-unit);
        overflow: hidden;
    }}
    
    .stPlotlyChart > div {{
        width: 100% !important;
        margin: 0 auto !important;
        border-radius: var(--grid-unit);
    }}
    
    /* CARD GRID SYSTEM - Compact layout */
    .protocol-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--grid-3x);
        margin-bottom: var(--content-gap);
        width: 100%;
    }}
    
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: var(--grid-3x);
        margin-bottom: var(--content-gap);
        width: 100%;
    }}
    
    /* Compact cards */
    .protocol-card, .metric-card {{
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: var(--grid-3x);
        border-radius: var(--grid-2x);
        border: 1px solid #e5e7eb;
        background: white;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    
    /* Protocol spotlight layout fixes */
    .protocol-spotlight {{
        width: 100%;
        margin: 0;
        padding: 0;
    }}
    
    /* Ensure protocol cards in same row have equal heights */
    .stColumns .stColumn {{
        display: flex;
        flex-direction: column;
    }}
    
    /* Protocol card container styling */
    .stContainer {{
        min-height: 200px;
        display: flex;
        flex-direction: column;
    }}
    
    /* Ensure consistent card heights */
    .stContainer .stMarkdown {{
        margin-bottom: 0.5rem !important;
    }}
    
    /* Metrics row alignment */
    .stContainer .stColumns {{
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    /* Protocol description consistency */
    .stContainer .stCaption {{
        font-size: 0.8rem !important;
        line-height: 1.2 !important;
        margin-bottom: 0.5rem !important;
        min-height: 1.2rem !important;
    }}
    
    .protocol-card:hover, .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 var(--grid-2x) var(--grid-3x) rgba(0,0,0,0.15);
        border-color: {COLORS['secondary_blue']};
    }}
    
    /* Card content sizing - compact */
    .protocol-card h3, .metric-card h3 {{
        font-size: 1.25rem !important;
        margin-bottom: var(--grid-2x) !important;
    }}
    
    .protocol-card p, .metric-card p {{
        font-size: 1rem !important;
        line-height: 1.4 !important;
    }}
    
    .protocol-card .metric-value, .metric-card .metric-value {{
        font-size: 1.75rem !important;
        font-weight: 700 !important;
    }}
    
    /* Element containers - no extra spacing */
    .element-container {{
        margin: 0;
        width: 100%;
    }}
    
    /* Streamlit metrics - compact sizing */
    .stMetric {{
        min-height: 100px;
        padding: var(--grid-2x) !important;
        margin: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: var(--grid-2x);
        transition: all 0.2s ease;
    }}
    
    .stMetric:hover {{
        transform: translateY(-2px);
        box-shadow: 0 var(--grid-unit) var(--grid-3x) rgba(0,0,0,0.1);
    }}
    
    /* Compact expandable sections */
    .stExpander {{
        border-radius: 6px;
        margin-bottom: 0.25rem !important;
    }}
    
    .streamlit-expanderHeader {{
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }}
    
    /* Success/Error/Warning Messages - Compact */
    .success-message {{
        background: {COLORS['success_green']}15;
        border: 1px solid {COLORS['success_green']};
        color: {COLORS['success_green']};
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }}
    
    .error-message {{
        background: {COLORS['danger_red']}15;
        border: 1px solid {COLORS['danger_red']};
        color: {COLORS['danger_red']};
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }}
    
    .warning-message {{
        background: {COLORS['warning_orange']}15;
        border: 1px solid {COLORS['warning_orange']};
        color: {COLORS['warning_orange']};
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }}
    
    /* Loading Animation - Compact */
    .loading-spinner {{
        border: 3px solid {COLORS['light_gray']};
        border-top: 3px solid {COLORS['secondary_blue']};
        border-radius: 50%;
        width: 24px;
        height: 24px;
        animation: spin 1s linear infinite;
        margin: 0.5rem auto;
    }}
    
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    
    /* Sidebar Styles */
    .css-1d391kg {{
        background: {COLORS['light_blue']};
    }}
    
    /* Hide Streamlit Menu and Footer */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Custom Scrollbar - Compact */
    ::-webkit-scrollbar {{
        width: 4px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {COLORS['light_gray']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {COLORS['medium_gray']};
        border-radius: 2px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['primary_blue']};
    }}
    
    /* RESPONSIVE DESIGN - Compact across screen sizes */
    
    /* Mobile - Stack cards, minimal spacing */
    @media (max-width: 768px) {{
        :root {{
            --section-gap: 16px;
            --content-gap: 8px;
        }}
        
        .block-container {{
            padding: var(--grid-2x) !important;
            width: 100% !important;
            max-width: 100% !important;
        }}
        
        .main .block-container {{
            padding: var(--grid-2x);
            width: 100%;
            max-width: 100%;
        }}
        
        /* Single column grids on mobile */
        .protocol-grid, .metric-grid {{
            grid-template-columns: 1fr;
            gap: var(--grid-2x);
        }}
        
        /* Smaller cards on mobile */
        .protocol-card, .metric-card {{
            min-height: 120px;
            padding: var(--grid-2x);
        }}
        
        /* Adjust typography for mobile */
        h1, .stMarkdown h1 {{
            font-size: 1.5rem !important;
            text-align: center !important;
            justify-content: center;
        }}
        
        h2, .stMarkdown h2 {{
            font-size: 1.25rem !important;
            text-align: center !important;
            justify-content: center;
        }}
        
        h3, .stMarkdown h3 {{
            font-size: 1rem !important;
            text-align: center !important;
            justify-content: center;
        }}
        
        p, .stMarkdown p {{
            text-align: center !important;
        }}
        
        /* Button adjustments */
        .button-group {{
            flex-direction: column;
            align-items: center;
            gap: var(--grid-2x);
        }}
        
        .stButton > button {{
            font-size: 0.8rem !important;
            padding: var(--grid-2x) var(--grid-3x) !important;
            min-width: 180px;
        }}
    }}
    
    /* Tablet - 2 column grids */
    @media (min-width: 769px) and (max-width: 1024px) {{
        .block-container {{
            width: 100% !important;
            max-width: 100% !important;
        }}
        
        .protocol-grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
        
        .metric-grid {{
            grid-template-columns: repeat(3, 1fr);
        }}
    }}
    
    /* Desktop - 3+ column grids */
    @media (min-width: 1025px) {{
        .block-container {{
            width: 100% !important;
            max-width: 100% !important;
            padding: var(--grid-3x) var(--grid-4x) !important;
        }}
        
        .protocol-grid {{
            grid-template-columns: repeat(4, 1fr);
        }}
        
        .metric-grid {{
            grid-template-columns: repeat(5, 1fr);
        }}
    }}
    
    /* Large screens - Maximum columns */
    @media (min-width: 1400px) {{
        .block-container {{
            padding: var(--grid-4x) var(--grid-6x) !important;
        }}
        
        .protocol-grid {{
            grid-template-columns: repeat(5, 1fr);
        }}
        
        .metric-grid {{
            grid-template-columns: repeat(6, 1fr);
        }}
    }}
    
    /* Ultra-wide screens */
    @media (min-width: 1800px) {{
        .protocol-grid {{
            grid-template-columns: repeat(6, 1fr);
        }}
        
        .metric-grid {{
            grid-template-columns: repeat(8, 1fr);
        }}
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)