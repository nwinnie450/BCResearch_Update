"""
Advanced Analytics Component for Deep Protocol Analysis
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
# from services.blockchain_service import BlockchainService  # Removed - service deleted
from typing import Dict, List
import time
from datetime import datetime, timedelta
from config import BLOCKCHAIN_PROTOCOLS

# Use comprehensive realtime data service
try:
    from services.comprehensive_realtime_data_service import comprehensive_realtime_service
    REALTIME_AVAILABLE = True
except ImportError:
    comprehensive_realtime_service = None
    REALTIME_AVAILABLE = False

def render_analytics():
    """Render advanced analytics dashboard with real-time data"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if REALTIME_AVAILABLE:
            st.markdown("### 📈 Real-Time Analytics")
        else:
            st.markdown("### 📈 Analytics Dashboard")
    
    with col2:
        if REALTIME_AVAILABLE and st.button("🔄 Refresh Data", help="Refresh live data"):
            # Clear cache to force refresh
            realtime_service.cache.clear()
            st.rerun()
    
    # Load protocol data (real-time if available, mock otherwise)
    if REALTIME_AVAILABLE:
        protocols = get_realtime_protocol_data()
    else:
        protocols = get_mock_protocol_data()
        st.info("📊 **Demo Mode**: Showing mock data for analytics demonstration. Real-time features will be available in production.")
    
    if not protocols:
        st.error("❌ **Unable to load analytics data. Please check your connection.**")
        return
    
    # Status and controls
    if REALTIME_AVAILABLE:
        # Auto-refresh and update time
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        with col2:
            auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False, help="Automatically refresh data every 30 seconds")
        
        # Real-time status indicator
        status_col1, status_col2, status_col3 = st.columns([1, 1, 2])
        
        with status_col1:
            st.markdown("🟢 **Live Data**")
        
        with status_col2:
            data_age = 60 - (time.time() % 60)  # Time until next minute
            st.markdown(f"⏱️ Next update: {int(data_age)}s")
        
        with status_col3:
            if st.button("📊 Market Overview", help="Quick market overview for all protocols"):
                render_market_overview(protocols)
        
        # Auto-refresh functionality
        if auto_refresh:
            time.sleep(30)
            st.rerun()
    else:
        st.caption(f"📅 Demo data generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    # Protocol selector
    protocol_names = [p['name'] for p in protocols]
    
    selected_protocol_name = st.selectbox(
        "Select protocol for detailed analysis:",
        options=protocol_names,
        index=0 if not hasattr(st.session_state, 'selected_protocol') else 
              next((i for i, p in enumerate(protocols) if p['id'] == st.session_state.get('selected_protocol')), 0)
    )
    
    selected_protocol = next(p for p in protocols if p['name'] == selected_protocol_name)
    
    # Render analytics sections
    render_protocol_overview(selected_protocol)
    render_performance_analysis(selected_protocol)
    render_ecosystem_analysis(selected_protocol)
    render_risk_analysis(selected_protocol)
    render_competitive_positioning(selected_protocol, protocols)

def render_protocol_overview(protocol: Dict):
    """Render detailed protocol overview with live or mock data"""
    
    if REALTIME_AVAILABLE:
        st.markdown(f"### 🔍 {protocol['name']} Live Overview")
        # Get live market data
        market_data = realtime_service.get_live_market_data()
        protocol_market = market_data.get(protocol['id'], {})
    else:
        st.markdown(f"### 🔍 {protocol['name']} Overview (Demo)")
        # Use mock market data
        protocol_market = {
            'market_cap': protocol.get('market_cap', 0),
            'change_24h': np.random.uniform(-5, 15)
        }
    
    # Key metrics cards with live data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_tps = protocol.get('tps', 0)
        st.metric(
            "Current TPS",
            f"{current_tps:.1f}",
            delta=f"{np.random.uniform(-5, 15):.1f}%",
            help="Current transactions per second"
        )
    
    with col2:
        market_cap = protocol_market.get('market_cap', protocol.get('market_cap', 0))
        change_24h = protocol_market.get('change_24h', 0)
        st.metric(
            "Market Cap",
            f"${market_cap/1e9:.1f}B",
            delta=f"{change_24h:.1f}%" if change_24h else None,
            help="Current market capitalization"
        )
    
    with col3:
        tvl = protocol.get('tvl', 0)
        st.metric(
            "Total Value Locked",
            f"${tvl/1e9:.1f}B",
            delta=f"{np.random.uniform(-10, 25):.1f}%",
            help="Total value locked in DeFi protocols"
        )
    
    with col4:
        active_addresses = protocol.get('active_addresses', 0)
        st.metric(
            "Active Addresses",
            f"{active_addresses:,}",
            delta=f"{np.random.uniform(-5, 20):.1f}%",
            help="24-hour active addresses"
        )
    
    # Protocol details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Technical Specifications")
        
        specs_data = {
            "Consensus Mechanism": protocol.get('consensus', 'Unknown'),
            "Block Time": f"{np.random.uniform(0.1, 15):.1f} seconds",
            "Block Size": f"{np.random.randint(1, 32)} MB",
            "Programming Language": get_programming_language(protocol['id']),
            "Virtual Machine": get_virtual_machine(protocol['id']),
            "Staking Required": "Yes" if protocol.get('consensus') != 'Proof of Work' else "No"
        }
        
        for key, value in specs_data.items():
            st.markdown(f"**{key}:** {value}")
    
    with col2:
        st.markdown("#### 🌟 Ecosystem Health")
        
        # Create ecosystem health chart
        render_ecosystem_health_chart(protocol)

def render_performance_analysis(protocol: Dict):
    """Render performance analysis with time series data"""
    
    st.markdown("---")
    st.markdown("### ⚡ Performance Analysis")
    
    # Generate mock time series data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    
    # Mock performance data
    base_tps = protocol.get('tps', 1000)
    tps_data = base_tps + np.random.normal(0, base_tps * 0.1, len(dates))
    
    base_fee = protocol.get('avg_fee', 0.01)
    fee_data = base_fee + np.random.normal(0, base_fee * 0.2, len(dates))
    fee_data = np.maximum(fee_data, 0.0001)  # Ensure positive fees
    
    latency_data = np.random.uniform(0.1, 5, len(dates))
    
    df = pd.DataFrame({
        'Date': dates,
        'TPS': tps_data,
        'Fee': fee_data,
        'Latency': latency_data
    })
    
    # Render performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        render_tps_trend(protocol)
    
    with col2:
        render_fee_trend(protocol)
    
    # Network utilization
    render_network_utilization(protocol)

def render_tps_trend(protocol: Dict):
    """Render TPS trend chart (live or mock data)"""
    
    if REALTIME_AVAILABLE:
        st.markdown("#### 📊 Live TPS Trend (24 Hours)")
        # Get live TPS data
        df = realtime_service.get_live_tps_data(protocol['id'], hours=24)
        title = f"{protocol['name']} - Real-Time Transaction Throughput"
    else:
        st.markdown("#### 📊 TPS Trend (Demo Data)")
        # Generate mock TPS data
        df = generate_mock_tps_data(protocol, hours=24)
        title = f"{protocol['name']} - Transaction Throughput (Demo)"
    
    fig = px.line(
        df, 
        x='timestamp' if REALTIME_AVAILABLE else 'time', 
        y='tps',
        title=title
    )
    
    fig.update_layout(
        height=300,
        font=dict(family="Inter, sans-serif"),
        xaxis_title="Time (UTC)",
        yaxis_title="Transactions per Second",
        showlegend=False
    )
    
    # Add current TPS as annotation
    current_tps = protocol.get('tps', 0)
    fig.add_annotation(
        text=f"Current: {current_tps:.1f} TPS",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_fee_trend(protocol: Dict):
    """Render fee trend chart (live or mock data)"""
    
    if REALTIME_AVAILABLE:
        st.markdown("#### 💰 Live Fee Trend (24 Hours)")
        # Get live fee data
        df = realtime_service.get_live_fee_data(protocol['id'], hours=24)
        title = f"{protocol['name']} - Real-Time Transaction Fees"
    else:
        st.markdown("#### 💰 Fee Trend (Demo Data)")
        # Generate mock fee data
        df = generate_mock_fee_data(protocol, hours=24)
        title = f"{protocol['name']} - Transaction Fees (Demo)"
    
    fig = px.line(
        df,
        x='timestamp' if REALTIME_AVAILABLE else 'time',
        y='fee', 
        title=title
    )
    
    fig.update_layout(
        height=300,
        font=dict(family="Inter, sans-serif"),
        xaxis_title="Time (UTC)",
        yaxis_title="Average Fee (USD)",
        showlegend=False
    )
    
    fig.update_layout(yaxis=dict(tickformat="$.4f"))
    
    # Add current fee as annotation
    current_fee = protocol.get('avg_fee', 0)
    fig.add_annotation(
        text=f"Current: ${current_fee:.4f}",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_network_utilization(protocol: Dict):
    """Render network utilization analysis"""
    
    st.markdown("#### 🌐 Network Utilization")
    
    # Mock utilization data
    hours = list(range(24))
    utilization = [np.random.uniform(20, 95) for _ in hours]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hours,
        y=utilization,
        mode='lines+markers',
        name='Network Utilization %',
        line=dict(color='#3B82F6', width=3),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title="Network Utilization by Hour (24h)",
        xaxis_title="Hour of Day",
        yaxis_title="Utilization %",
        height=300,
        font=dict(family="Inter, sans-serif")
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_ecosystem_analysis(protocol: Dict):
    """Render ecosystem and adoption analysis"""
    
    st.markdown("---")
    st.markdown("### 🌟 Ecosystem Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_dapp_categories(protocol)
    
    with col2:
        render_developer_activity(protocol)
    
    # Partnership and integration analysis
    render_partnerships_analysis(protocol)

def render_dapp_categories(protocol: Dict):
    """Render dApp ecosystem breakdown"""
    
    st.markdown("#### 🏗️ dApp Categories")
    
    # Mock dApp data
    categories = ['DeFi', 'Gaming', 'NFT', 'Social', 'Infrastructure', 'Other']
    values = np.random.randint(10, 200, len(categories))
    
    fig = px.pie(
        values=values,
        names=categories,
        title=f"dApp Distribution on {protocol['name']}"
    )
    
    fig.update_layout(
        height=400,
        font=dict(family="Inter, sans-serif")
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_developer_activity(protocol: Dict):
    """Render developer activity metrics"""
    
    st.markdown("#### 👨‍💻 Developer Activity")
    
    # Mock developer data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    commits = np.random.randint(500, 2000, len(months))
    active_devs = np.random.randint(100, 800, len(months))
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(x=months, y=commits, name="Commits", marker_color="#3B82F6"),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=months, y=active_devs, mode='lines+markers', name="Active Developers", 
                  line=dict(color="#DC2626", width=3)),
        secondary_y=True,
    )
    
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Commits", secondary_y=False)
    fig.update_yaxes(title_text="Active Developers", secondary_y=True)
    
    fig.update_layout(
        height=400,
        font=dict(family="Inter, sans-serif")
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_partnerships_analysis(protocol: Dict):
    """Render partnerships and integrations"""
    
    st.markdown("#### 🤝 Key Partnerships & Integrations")
    
    # Mock partnership data
    partnerships = [
        {"Partner": "Major Exchange A", "Type": "Trading", "Status": "Active", "Impact": "High"},
        {"Partner": "DeFi Protocol B", "Type": "Integration", "Status": "Active", "Impact": "Medium"},
        {"Partner": "Enterprise C", "Type": "Adoption", "Status": "Planned", "Impact": "High"},
        {"Partner": "Infrastructure D", "Type": "Technical", "Status": "Active", "Impact": "Low"}
    ]
    
    df = pd.DataFrame(partnerships)
    
    # Add status colors
    def get_status_color(status):
        colors = {"Active": "🟢", "Planned": "🟡", "Inactive": "🔴"}
        return colors.get(status, "⚪")
    
    df['Status Icon'] = df['Status'].apply(get_status_color)
    
    st.dataframe(
        df[['Status Icon', 'Partner', 'Type', 'Impact']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status Icon": "Status",
            "Partner": "Partner Organization",
            "Type": "Partnership Type",
            "Impact": "Business Impact"
        }
    )

def render_risk_analysis(protocol: Dict):
    """Render risk analysis dashboard"""
    
    st.markdown("---")
    st.markdown("### ⚠️ Risk Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_security_score_breakdown(protocol)
    
    with col2:
        render_risk_factors(protocol)

def render_security_score_breakdown(protocol: Dict):
    """Render detailed security score breakdown"""
    
    st.markdown("#### 🛡️ Security Score Breakdown")
    
    # Mock security metrics
    security_factors = {
        'Consensus Security': np.random.randint(80, 95),
        'Smart Contract Audits': np.random.randint(70, 90),
        'Network Decentralization': np.random.randint(75, 92),
        'Historical Incidents': np.random.randint(85, 98),
        'Bug Bounty Program': np.random.randint(80, 95)
    }
    
    categories = list(security_factors.keys())
    values = list(security_factors.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Security Score',
        line=dict(color='#059669', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        height=400,
        font=dict(family="Inter, sans-serif")
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_risk_factors(protocol: Dict):
    """Render key risk factors analysis"""
    
    st.markdown("#### ⚠️ Key Risk Factors")
    
    risk_factors = [
        {"Risk": "Centralization", "Level": "Medium", "Score": 6},
        {"Risk": "Smart Contract Bugs", "Level": "Low", "Score": 3},
        {"Risk": "Regulatory Compliance", "Level": "Medium", "Score": 5},
        {"Risk": "Market Volatility", "Level": "High", "Score": 8},
        {"Risk": "Technical Scalability", "Level": "Low", "Score": 2}
    ]
    
    df = pd.DataFrame(risk_factors)
    
    # Create risk level chart
    fig = px.bar(
        df,
        x='Risk',
        y='Score',
        color='Level',
        color_discrete_map={
            'Low': '#059669',
            'Medium': '#D97706', 
            'High': '#DC2626'
        },
        title="Risk Assessment"
    )
    
    fig.update_layout(
        height=300,
        font=dict(family="Inter, sans-serif"),
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_competitive_positioning(protocol: Dict, all_protocols: List[Dict]):
    """Render competitive positioning analysis"""
    
    st.markdown("---")
    st.markdown("### 🏆 Competitive Positioning")
    
    # Create competitive landscape
    render_competitive_landscape(protocol, all_protocols)
    
    # Strengths and weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        render_strengths_analysis(protocol)
    
    with col2:
        render_weaknesses_analysis(protocol)

def render_competitive_landscape(protocol: Dict, all_protocols: List[Dict]):
    """Render competitive landscape bubble chart"""
    
    st.markdown("#### 🗺️ Competitive Landscape")
    
    # Prepare competitive data
    df = pd.DataFrame([
        {
            "Protocol": p['name'],
            "TPS": p.get('tps', 0),
            "Security Score": p.get('security_score', 0),
            "Market Cap": p.get('market_cap', 0),
            "Selected": p['name'] == protocol['name']
        }
        for p in all_protocols
    ])
    
    # Create bubble chart
    fig = px.scatter(
        df,
        x="TPS",
        y="Security Score",
        size="Market Cap",
        color="Selected",
        hover_name="Protocol",
        color_discrete_map={True: "#DC2626", False: "#3B82F6"},
        title="Performance vs Security vs Market Cap"
    )
    
    fig.update_layout(
        height=500,
        font=dict(family="Inter, sans-serif"),
        xaxis_title="Transactions Per Second (TPS)",
        yaxis_title="Security Score"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_strengths_analysis(protocol: Dict):
    """Render protocol strengths"""
    
    st.markdown("#### ✅ Key Strengths")
    
    # Mock strengths based on protocol characteristics
    strengths = get_protocol_strengths(protocol)
    
    for strength in strengths:
        st.markdown(f"**{strength['title']}**")
        st.progress(strength['score'] / 100)
        st.markdown(f"*{strength['description']}*")
        st.markdown("")

def render_weaknesses_analysis(protocol: Dict):
    """Render protocol weaknesses"""
    
    st.markdown("#### ⚠️ Areas for Improvement")
    
    # Mock weaknesses based on protocol characteristics  
    weaknesses = get_protocol_weaknesses(protocol)
    
    for weakness in weaknesses:
        st.markdown(f"**{weakness['title']}**")
        st.progress(weakness['severity'] / 100)
        st.markdown(f"*{weakness['description']}*")
        st.markdown("")

# Helper functions
def get_programming_language(protocol_id: str) -> str:
    """Get programming language for protocol"""
    languages = {
        'ethereum': 'Solidity',
        'solana': 'Rust', 
        'polygon': 'Solidity',
        'binance': 'Solidity',
        'avalanche': 'Solidity'
    }
    return languages.get(protocol_id, 'Various')

def get_virtual_machine(protocol_id: str) -> str:
    """Get virtual machine for protocol"""
    vms = {
        'ethereum': 'EVM',
        'solana': 'Sealevel VM',
        'polygon': 'EVM',
        'binance': 'EVM', 
        'avalanche': 'EVM'
    }
    return vms.get(protocol_id, 'Custom VM')

def render_ecosystem_health_chart(protocol: Dict):
    """Render ecosystem health gauge"""
    
    ecosystem_score = protocol.get('ecosystem_score', 75)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = ecosystem_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Ecosystem Health"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#3B82F6"},
            'steps': [
                {'range': [0, 50], 'color': "#FEE2E2"},
                {'range': [50, 80], 'color': "#FEF3C7"},
                {'range': [80, 100], 'color': "#D1FAE5"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    st.plotly_chart(fig, use_container_width=True)

def get_protocol_strengths(protocol: Dict) -> List[Dict]:
    """Get protocol strengths based on metrics"""
    
    strengths = []
    
    if protocol.get('tps', 0) > 10000:
        strengths.append({
            'title': 'High Throughput',
            'score': 90,
            'description': 'Excellent transaction processing capability'
        })
    
    if protocol.get('avg_fee', 1) < 0.01:
        strengths.append({
            'title': 'Low Transaction Costs',
            'score': 95,
            'description': 'Very affordable for users and applications'
        })
    
    if protocol.get('security_score', 0) > 85:
        strengths.append({
            'title': 'Strong Security',
            'score': protocol.get('security_score', 85),
            'description': 'Robust security track record and design'
        })
    
    return strengths[:3]  # Return top 3 strengths

def get_protocol_weaknesses(protocol: Dict) -> List[Dict]:
    """Get protocol weaknesses based on metrics"""
    
    weaknesses = []
    
    if protocol.get('tps', 0) < 1000:
        weaknesses.append({
            'title': 'Limited Throughput',
            'severity': 70,
            'description': 'May face scalability challenges during high demand'
        })
    
    if protocol.get('avg_fee', 0) > 1.0:
        weaknesses.append({
            'title': 'High Transaction Costs',
            'severity': 80,
            'description': 'Expensive for frequent transactions and micro-payments'
        })
    
    if protocol.get('ecosystem_score', 100) < 70:
        weaknesses.append({
            'title': 'Limited Ecosystem',
            'severity': 60,
            'description': 'Smaller developer and application ecosystem'
        })
    
    return weaknesses[:3]  # Return top 3 weaknesses

def get_realtime_protocol_data() -> List[Dict]:
    """Get real-time protocol data for analytics"""
    
    protocols = []
    
    with st.spinner("🔄 Fetching live blockchain data..."):
        for protocol_id in BLOCKCHAIN_PROTOCOLS.keys():
            try:
                protocol_data = realtime_service.get_live_protocol_data(protocol_id)
                protocols.append(protocol_data)
            except Exception as e:
                st.warning(f"⚠️ Error fetching data for {protocol_id}: {str(e)}")
                continue
    
    return protocols

def generate_mock_tps_data(protocol: Dict, hours: int) -> pd.DataFrame:
    """Generate mock TPS data for charts"""
    
    timestamps = pd.date_range(
        start=datetime.now() - timedelta(hours=hours),
        end=datetime.now(),
        freq='H'
    )
    
    base_tps = protocol.get('tps', 100)
    tps_values = base_tps + np.random.normal(0, base_tps * 0.1, len(timestamps))
    tps_values = np.maximum(tps_values, base_tps * 0.5)
    
    return pd.DataFrame({
        'time': timestamps,
        'tps': tps_values
    })

def generate_mock_fee_data(protocol: Dict, hours: int) -> pd.DataFrame:
    """Generate mock fee data for charts"""
    
    timestamps = pd.date_range(
        start=datetime.now() - timedelta(hours=hours),
        end=datetime.now(),
        freq='H'
    )
    
    base_fee = protocol.get('avg_fee', 1.0)
    fee_values = base_fee + np.random.normal(0, base_fee * 0.2, len(timestamps))
    fee_values = np.maximum(fee_values, base_fee * 0.1)
    
    return pd.DataFrame({
        'time': timestamps,
        'fee': fee_values
    })

def render_market_overview(protocols: List[Dict]):
    """Render quick market overview for all protocols"""
    
    st.markdown("### 📊 Live Market Overview")
    
    # Create overview dataframe
    overview_data = []
    
    for protocol in protocols:
        overview_data.append({
            'Protocol': protocol['name'],
            'TPS': f"{protocol.get('tps', 0):.1f}",
            'Avg Fee': f"${protocol.get('avg_fee', 0):.4f}",
            'Market Cap': f"${protocol.get('market_cap', 0)/1e9:.1f}B",
            'Security Score': f"{protocol.get('security_score', 0)}/100",
            'Utilization': f"{protocol.get('network_utilization', 0):.1f}%"
        })
    
    df = pd.DataFrame(overview_data)
    
    # Display as a nice table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Protocol": st.column_config.TextColumn("Protocol", width="medium"),
            "TPS": st.column_config.TextColumn("TPS", width="small"),
            "Avg Fee": st.column_config.TextColumn("Fee", width="small"),
            "Market Cap": st.column_config.TextColumn("Market Cap", width="medium"),
            "Security Score": st.column_config.TextColumn("Security", width="small"),
            "Utilization": st.column_config.TextColumn("Usage", width="small")
        }
    )
    
    # Quick comparison chart
    col1, col2 = st.columns(2)
    
    with col1:
        tps_fig = px.bar(
            df, 
            x='Protocol', 
            y=[float(x) for x in df['TPS']],
            title="TPS Comparison",
            color='Protocol'
        )
        tps_fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(tps_fig, use_container_width=True)
    
    with col2:
        # Extract numeric values for fee comparison
        fee_values = [float(x.replace('$', '')) for x in df['Avg Fee']]
        fee_fig = px.bar(
            x=df['Protocol'], 
            y=fee_values,
            title="Fee Comparison (USD)",
            color=df['Protocol']
        )
        fee_fig.update_layout(height=300, showlegend=False, yaxis=dict(tickformat="$.4f"))
        st.plotly_chart(fee_fig, use_container_width=True)

def get_mock_protocol_data() -> List[Dict]:
    """Generate mock protocol data for analytics"""
    
    mock_data = []
    
    for protocol_id, protocol_info in BLOCKCHAIN_PROTOCOLS.items():
        # Generate realistic mock data based on known characteristics
        if protocol_id == 'ethereum':
            mock_protocol = {
                'id': protocol_id,
                'name': protocol_info['name'],
                'symbol': protocol_info['symbol'],
                'tps': 15,
                'avg_fee': 15.0,
                'market_cap': 240000000000,
                'tvl': 35000000000,
                'security_score': 95,
                'ecosystem_score': 98,
                'consensus': protocol_info['consensus']
            }
        elif protocol_id == 'bitcoin':
            mock_protocol = {
                'id': protocol_id,
                'name': protocol_info['name'],
                'symbol': protocol_info['symbol'],
                'tps': 7,
                'avg_fee': 8.0,
                'market_cap': 580000000000,
                'tvl': 1000000000,
                'security_score': 98,
                'ecosystem_score': 85,
                'consensus': protocol_info['consensus']
            }
        elif protocol_id == 'binance_smart_chain':
            mock_protocol = {
                'id': protocol_id,
                'name': protocol_info['name'],
                'symbol': protocol_info['symbol'],
                'tps': 160,
                'avg_fee': 0.35,
                'market_cap': 45000000000,
                'tvl': 4500000000,
                'security_score': 78,
                'ecosystem_score': 88,
                'consensus': protocol_info['consensus']
            }
        elif protocol_id == 'tron':
            mock_protocol = {
                'id': protocol_id,
                'name': protocol_info['name'],
                'symbol': protocol_info['symbol'],
                'tps': 1500,
                'avg_fee': 0.001,
                'market_cap': 12000000000,
                'tvl': 1800000000,
                'security_score': 82,
                'ecosystem_score': 75,
                'consensus': protocol_info['consensus']
            }
        elif protocol_id == 'base':
            mock_protocol = {
                'id': protocol_id,
                'name': protocol_info['name'],
                'symbol': protocol_info['symbol'],
                'tps': 350,
                'avg_fee': 0.15,
                'market_cap': 8500000000,
                'tvl': 2200000000,
                'security_score': 88,
                'ecosystem_score': 82,
                'consensus': protocol_info['consensus']
            }
        else:
            continue
            
        mock_data.append(mock_protocol)
    
    return mock_data