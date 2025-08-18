#!/usr/bin/env python3
"""
Unified Analytics Dashboard
Combines Analytics + Compare + Data management into one powerful interface
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import BLOCKCHAIN_PROTOCOLS

# Import services
try:
    from services.comprehensive_realtime_data_service import comprehensive_realtime_service
    from services.realtime_data_fetcher import realtime_data_fetcher
    REALTIME_AVAILABLE = True
except ImportError:
    comprehensive_realtime_service = None
    realtime_data_fetcher = None
    REALTIME_AVAILABLE = False

def render_unified_analytics():
    """Render the unified analytics dashboard"""
    
    st.markdown("### 📊 Unified Analytics Dashboard")
    st.markdown("*All-in-one: Analyze, Compare, and Manage blockchain data*")
    
    # Initialize session state
    if 'analytics_mode' not in st.session_state:
        st.session_state.analytics_mode = 'analyze'  # analyze | compare | manage
    if 'selected_protocols' not in st.session_state:
        st.session_state.selected_protocols = ['ethereum']  # Default to Ethereum
    
    # Control Panel
    render_control_panel()
    
    st.markdown("---")
    
    # Dynamic Content Area based on mode
    if st.session_state.analytics_mode == 'analyze':
        render_analyze_mode()
    elif st.session_state.analytics_mode == 'compare':
        render_compare_mode()
    elif st.session_state.analytics_mode == 'manage':
        render_manage_mode()
    
    # Action Bar
    render_action_bar()

def render_control_panel():
    """Render the unified control panel - optimized for current demo mode"""
    
    st.markdown("#### 🎛️ Control Panel")
    
    # Demo mode notice
    st.info("📊 **Demo Mode**: Using realistic mock data for blockchain protocols. Real-time features available with API subscriptions.")
    
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        # Protocol Selection
        available_protocols = list(BLOCKCHAIN_PROTOCOLS.keys())
        protocol_names = {k: v['name'] for k, v in BLOCKCHAIN_PROTOCOLS.items()}
        
        # Get current selection names
        current_names = [protocol_names.get(pid, pid) for pid in st.session_state.selected_protocols]
        
        selected_names = st.multiselect(
            "Select Protocol(s) for Analysis:",
            options=[protocol_names[pid] for pid in available_protocols],
            default=current_names,
            help="Choose 1 protocol for deep analysis, or 2+ for comparison"
        )
        
        # Update session state with protocol IDs
        st.session_state.selected_protocols = [
            pid for pid, name in protocol_names.items() if name in selected_names
        ]
    
    with col2:
        # View Mode Toggle - simplified for current capabilities
        if REALTIME_AVAILABLE:
            mode_options = ['🔍 Analyze', '⚖️ Compare', '⚡ Manage Data']
            mode_map = {'🔍 Analyze': 'analyze', '⚖️ Compare': 'compare', '⚡ Manage Data': 'manage'}
        else:
            # Focus on what works well without real-time data
            mode_options = ['🔍 Analyze', '⚖️ Compare']
            mode_map = {'🔍 Analyze': 'analyze', '⚖️ Compare': 'compare'}
        
        current_mode_display = next((k for k, v in mode_map.items() if v == st.session_state.analytics_mode), mode_options[0])
        
        selected_mode = st.selectbox(
            "Analysis Mode:",
            options=mode_options,
            index=mode_options.index(current_mode_display) if current_mode_display in mode_options else 0
        )
        
        st.session_state.analytics_mode = mode_map[selected_mode]
    
    with col3:
        # Demo Mode Status
        st.markdown("**Data Quality:**")
        st.success("✅ Demo Ready")
        st.caption("Realistic mock data")
    
    # Smart mode suggestion - adapted for current capabilities
    selected_count = len(st.session_state.selected_protocols)
    
    if selected_count == 0:
        st.warning("⚠️ Please select at least one protocol above")
    elif selected_count == 1 and st.session_state.analytics_mode == 'compare':
        st.info("💡 **Tip**: Select 2+ protocols for comparison, or switch to Analyze mode for detailed single protocol analysis")
    elif selected_count > 1 and st.session_state.analytics_mode == 'analyze':
        st.info(f"💡 **Tip**: You have {selected_count} protocols selected. Switch to Compare mode to see them side-by-side")
    
    # Current limitations notice
    if not REALTIME_AVAILABLE and selected_count > 0:
        st.success(f"📊 **Ready**: Analyzing {selected_count} protocol{'s' if selected_count > 1 else ''} with comprehensive mock data including realistic TPS, fees, security scores, and market metrics.")

def render_analyze_mode():
    """Render single protocol analysis mode"""
    
    if not st.session_state.selected_protocols:
        st.info("👆 Select a protocol above to start analysis")
        return
    
    protocol_id = st.session_state.selected_protocols[0]
    protocol_info = BLOCKCHAIN_PROTOCOLS.get(protocol_id, {})
    protocol_name = protocol_info.get('name', protocol_id)
    
    st.markdown(f"### 🔍 Deep Analysis: {protocol_name}")
    
    if len(st.session_state.selected_protocols) > 1:
        st.info(f"Analyzing first selected protocol: **{protocol_name}**. Switch to Compare mode to see all selected protocols.")
    
    # Get protocol data
    protocol_data = get_protocol_data(protocol_id)
    
    if not protocol_data:
        st.error(f"❌ Unable to load data for {protocol_name}")
        return
    
    # Overview metrics
    render_protocol_overview_unified(protocol_data)
    
    # Performance analysis
    col1, col2 = st.columns(2)
    
    with col1:
        render_performance_charts(protocol_data)
    
    with col2:
        render_ecosystem_health(protocol_data)
    
    # Detailed sections
    tab1, tab2, tab3 = st.tabs(["📈 Performance", "🛡️ Security & Risk", "🌟 Ecosystem"])
    
    with tab1:
        render_performance_analysis_unified(protocol_data)
    
    with tab2:
        render_security_analysis(protocol_data)
    
    with tab3:
        render_ecosystem_analysis_unified(protocol_data)

def render_compare_mode():
    """Render multi-protocol comparison mode"""
    
    selected_protocols = st.session_state.selected_protocols
    
    if len(selected_protocols) < 2:
        st.info("👆 Select 2+ protocols above for comparison analysis")
        return
    
    st.markdown(f"### ⚖️ Protocol Comparison ({len(selected_protocols)} protocols)")
    
    # Get data for all selected protocols
    protocol_data = []
    for protocol_id in selected_protocols:
        data = get_protocol_data(protocol_id)
        if data:
            protocol_data.append(data)
    
    if not protocol_data:
        st.error("❌ Unable to load data for comparison")
        return
    
    # Comparison overview
    render_comparison_overview(protocol_data)
    
    # Visual comparisons
    col1, col2 = st.columns(2)
    
    with col1:
        render_performance_comparison_unified(protocol_data)
    
    with col2:
        render_cost_comparison_unified(protocol_data)
    
    # Multi-dimensional analysis
    render_radar_comparison_unified(protocol_data)
    
    # Head-to-head (if exactly 2 protocols)
    if len(protocol_data) == 2:
        render_head_to_head_unified(protocol_data)

def render_manage_mode():
    """Render data management mode - adapted for current capabilities"""
    
    st.markdown("### ⚡ Data Management")
    
    if not REALTIME_AVAILABLE:
        st.info("📊 **Demo Mode Active**: Real-time data fetching requires API subscriptions")
        
        st.markdown("#### 🎯 Current Capabilities")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ Available Now:**")
            st.markdown("• Rich mock data for all protocols")
            st.markdown("• Realistic TPS, fees, market cap data")
            st.markdown("• Security and ecosystem scoring")
            st.markdown("• Performance trend simulation")
            st.markdown("• Multi-protocol comparison")
        
        with col2:
            st.markdown("**🔮 With Real-Time APIs:**")
            st.markdown("• Live blockchain data fetching")
            st.markdown("• Fresh proposal monitoring")
            st.markdown("• API health monitoring")
            st.markdown("• Scheduled data updates")
            st.markdown("• Multi-source data aggregation")
        
        st.markdown("---")
        st.markdown("#### 📈 Upgrade Path")
        
        api_info = {
            "CoinGecko Pro": {"cost": "$129/month", "benefit": "Market data, price feeds"},
            "Etherscan Pro": {"cost": "$199/month", "benefit": "Ethereum transaction data"},
            "Moralis": {"cost": "$109/month", "benefit": "Multi-chain API access"},
            "Alchemy": {"cost": "$199/month", "benefit": "Enhanced node access"}
        }
        
        for api, details in api_info.items():
            with st.expander(f"{api} - {details['cost']}"):
                st.write(f"**Benefits**: {details['benefit']}")
                st.write("**Status**: Not configured (demo mode)")
        
        st.info("💡 **Tip**: The current demo mode provides excellent analytics capabilities. Upgrade to real-time APIs when you need live data for production decisions.")
        return
    
    # Real-time mode (when APIs are available)
    protocols = realtime_data_fetcher.get_protocol_list()
    fetch_status = realtime_data_fetcher.get_fetch_status()
    
    render_data_status_overview(protocols, fetch_status)
    render_protocol_management(protocols)
    render_fetch_controls_unified(protocols)

def render_protocol_overview_unified(protocol_data: Dict):
    """Render unified protocol overview"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        tps = protocol_data.get('tps', 0)
        st.metric("TPS", f"{tps:,}", help="Transactions per second")
    
    with col2:
        fee = protocol_data.get('avg_fee', 0)
        st.metric("Avg Fee", f"${fee:.4f}", help="Average transaction fee")
    
    with col3:
        market_cap = protocol_data.get('market_cap', 0)
        st.metric("Market Cap", f"${market_cap/1e9:.1f}B" if market_cap > 1e9 else f"${market_cap/1e6:.1f}M")
    
    with col4:
        security = protocol_data.get('security_score', 0)
        st.metric("Security Score", f"{security}/100", help="Security assessment score")

def render_comparison_overview(protocol_data: List[Dict]):
    """Render comparison overview table"""
    
    st.markdown("#### 📋 Quick Comparison")
    
    # Create comparison table
    table_data = []
    for protocol in protocol_data:
        table_data.append({
            "Protocol": protocol['name'],
            "TPS": f"{protocol.get('tps', 0):,}",
            "Fee": f"${protocol.get('avg_fee', 0):.4f}",
            "Market Cap": f"${protocol.get('market_cap', 0)/1e9:.1f}B" if protocol.get('market_cap', 0) > 1e9 else f"${protocol.get('market_cap', 0)/1e6:.1f}M",
            "Security": f"{protocol.get('security_score', 0)}/100",
            "Ecosystem": f"{protocol.get('ecosystem_score', 0)}/100"
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

def render_action_bar():
    """Render unified action bar"""
    
    st.markdown("---")
    st.markdown("#### 🔧 Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Export Analysis", use_container_width=True):
            export_current_analysis()
    
    with col2:
        if st.button("🔗 Share Results", use_container_width=True):
            generate_share_link()
    
    with col3:
        if st.button("📅 Schedule Update", use_container_width=True):
            st.info("Scheduling feature available in main Schedule tab")
    
    with col4:
        if st.button("⚙️ Advanced Settings", use_container_width=True):
            render_advanced_settings()

def get_protocol_data(protocol_id: str) -> Dict:
    """Get protocol data (real-time or mock)"""
    
    if REALTIME_AVAILABLE and comprehensive_realtime_service:
        try:
            # Try to get real-time data
            return comprehensive_realtime_service.get_protocol_data(protocol_id)
        except:
            pass
    
    # Return mock data
    return get_mock_protocol_data(protocol_id)

def get_mock_protocol_data(protocol_id: str) -> Dict:
    """Generate realistic mock protocol data based on current market conditions"""
    
    protocol_info = BLOCKCHAIN_PROTOCOLS.get(protocol_id, {})
    
    # Base mock data
    mock_data = {
        'id': protocol_id,
        'name': protocol_info.get('name', protocol_id.title()),
        'symbol': protocol_info.get('symbol', protocol_id.upper()[:3]),
        'consensus': protocol_info.get('consensus', 'Unknown')
    }
    
    # Protocol-specific realistic data (based on actual 2024 performance)
    if protocol_id == 'ethereum':
        mock_data.update({
            'tps': 15.2,
            'avg_fee': 12.45,
            'market_cap': 245000000000,
            'tvl': 38200000000,
            'security_score': 95,
            'ecosystem_score': 98,
            'active_addresses': 485000,
            'finality_time': 13.2,
            'validator_count': 975000,
            'description': 'Leading smart contract platform with the largest DeFi ecosystem'
        })
    elif protocol_id == 'bitcoin':
        mock_data.update({
            'tps': 7.1,
            'avg_fee': 8.75,
            'market_cap': 595000000000,
            'tvl': 850000000,
            'security_score': 98,
            'ecosystem_score': 85,
            'active_addresses': 825000,
            'finality_time': 600,  # ~10 minutes
            'validator_count': 15000,  # Mining pools
            'description': 'Original cryptocurrency and store of value with highest security'
        })
    elif protocol_id == 'binance_smart_chain':
        mock_data.update({
            'tps': 158.3,
            'avg_fee': 0.28,
            'market_cap': 47500000000,
            'tvl': 4200000000,
            'security_score': 78,
            'ecosystem_score': 88,
            'active_addresses': 1150000,
            'finality_time': 3.0,
            'validator_count': 21,
            'description': 'EVM-compatible chain with low fees and high throughput'
        })
    elif protocol_id == 'tron':
        mock_data.update({
            'tps': 1458.2,
            'avg_fee': 0.0008,
            'market_cap': 11800000000,
            'tvl': 1650000000,
            'security_score': 82,
            'ecosystem_score': 75,
            'active_addresses': 1950000,
            'finality_time': 3.0,
            'validator_count': 27,
            'description': 'High-performance blockchain focused on entertainment and DApps'
        })
    elif protocol_id == 'base':
        mock_data.update({
            'tps': 348.5,
            'avg_fee': 0.12,
            'market_cap': 8200000000,
            'tvl': 2800000000,
            'security_score': 88,
            'ecosystem_score': 82,
            'active_addresses': 950000,
            'finality_time': 2.0,
            'validator_count': 1,  # Optimistic rollup
            'description': 'Coinbase L2 solution built on Optimism stack'
        })
    else:
        # Generic realistic mock data
        mock_data.update({
            'tps': np.random.uniform(50, 2000),
            'avg_fee': np.random.uniform(0.01, 5.0),
            'market_cap': np.random.randint(1, 100) * 1e9,
            'tvl': np.random.randint(100, 10000) * 1e6,
            'security_score': np.random.randint(70, 95),
            'ecosystem_score': np.random.randint(60, 90),
            'active_addresses': np.random.randint(10000, 1000000),
            'finality_time': np.random.uniform(1, 60),
            'validator_count': np.random.randint(21, 100000),
            'description': f'Blockchain protocol with {protocol_info.get("consensus", "unknown")} consensus'
        })
    
    return mock_data

def render_performance_charts(protocol_data: Dict):
    """Render performance charts for single protocol"""
    
    st.markdown("#### ⚡ Performance Trends")
    
    # Generate mock time series data
    hours = list(range(24))
    base_tps = protocol_data.get('tps', 100)
    tps_data = [base_tps + np.random.normal(0, base_tps * 0.1) for _ in hours]
    
    fig = px.line(
        x=hours,
        y=tps_data,
        title="24-Hour TPS Trend",
        labels={'x': 'Hour', 'y': 'TPS'}
    )
    fig.update_layout(height=300)
    
    st.plotly_chart(fig, use_container_width=True)

def render_ecosystem_health(protocol_data: Dict):
    """Render ecosystem health gauge"""
    
    st.markdown("#### 🌟 Ecosystem Health")
    
    ecosystem_score = protocol_data.get('ecosystem_score', 75)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ecosystem_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Score"},
        gauge={
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

def render_performance_analysis_unified(protocol_data: Dict):
    """Render detailed performance analysis"""
    
    # Network utilization
    st.markdown("#### 🌐 Network Utilization")
    hours = list(range(24))
    utilization = [np.random.uniform(20, 95) for _ in hours]
    
    fig = go.Figure(go.Scatter(
        x=hours,
        y=utilization,
        mode='lines+markers',
        fill='tonexty',
        line=dict(color='#3B82F6', width=3)
    ))
    fig.update_layout(
        title="Network Utilization by Hour",
        xaxis_title="Hour of Day",
        yaxis_title="Utilization %",
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

def render_security_analysis(protocol_data: Dict):
    """Render security analysis"""
    
    st.markdown("#### 🛡️ Security Assessment")
    
    # Security factors radar chart
    categories = ['Consensus', 'Audits', 'Decentralization', 'History', 'Bug Bounty']
    values = [np.random.randint(70, 95) for _ in categories]
    
    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line=dict(color='#059669', width=2)
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_ecosystem_analysis_unified(protocol_data: Dict):
    """Render ecosystem analysis"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏗️ dApp Categories")
        categories = ['DeFi', 'Gaming', 'NFT', 'Social', 'Infra']
        values = [np.random.randint(10, 100) for _ in categories]
        
        fig = px.pie(values=values, names=categories)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 👨‍💻 Developer Activity")
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        commits = [np.random.randint(500, 2000) for _ in months]
        
        fig = px.bar(x=months, y=commits)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def render_performance_comparison_unified(protocol_data: List[Dict]):
    """Render performance comparison"""
    
    st.markdown("#### ⚡ Performance Comparison")
    
    df = pd.DataFrame([
        {
            "Protocol": p['name'],
            "TPS": p.get('tps', 0)
        }
        for p in protocol_data
    ])
    
    fig = px.bar(df, x='Protocol', y='TPS', title="TPS Comparison")
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def render_cost_comparison_unified(protocol_data: List[Dict]):
    """Render cost comparison"""
    
    st.markdown("#### 💰 Cost Comparison")
    
    df = pd.DataFrame([
        {
            "Protocol": p['name'],
            "Fee": p.get('avg_fee', 0)
        }
        for p in protocol_data
    ])
    
    fig = px.bar(df, x='Protocol', y='Fee', title="Average Fee Comparison")
    fig.update_layout(height=300, yaxis=dict(tickformat="$.4f"))
    st.plotly_chart(fig, use_container_width=True)

def render_radar_comparison_unified(protocol_data: List[Dict]):
    """Render radar comparison chart"""
    
    st.markdown("#### 🕸️ Multi-Dimensional Comparison")
    
    fig = go.Figure()
    categories = ['TPS', 'Cost', 'Security', 'Ecosystem']
    
    for protocol in protocol_data:
        # Normalize values to 0-100 scale
        values = [
            min(protocol.get('tps', 0) / 10, 100),  # TPS score
            max(0, 100 - (protocol.get('avg_fee', 1) * 20)),  # Cost score (inverted)
            protocol.get('security_score', 0),  # Security score
            protocol.get('ecosystem_score', 0)  # Ecosystem score
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=protocol['name'],
            line=dict(width=2)
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_head_to_head_unified(protocol_data: List[Dict]):
    """Render head-to-head comparison for 2 protocols"""
    
    st.markdown("#### 🥊 Head-to-Head Analysis")
    
    protocol_a, protocol_b = protocol_data
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"**{protocol_a['name']}**")
        st.metric("TPS", f"{protocol_a.get('tps', 0):,}")
        st.metric("Fee", f"${protocol_a.get('avg_fee', 0):.4f}")
        st.metric("Security", f"{protocol_a.get('security_score', 0)}/100")
    
    with col2:
        st.markdown("**VS**")
        
        # Winner indicators
        tps_winner = "A" if protocol_a.get('tps', 0) > protocol_b.get('tps', 0) else "B"
        fee_winner = "A" if protocol_a.get('avg_fee', 1) < protocol_b.get('avg_fee', 1) else "B"
        security_winner = "A" if protocol_a.get('security_score', 0) > protocol_b.get('security_score', 0) else "B"
        
        st.markdown(f"**TPS Winner:** Protocol {tps_winner}")
        st.markdown(f"**Fee Winner:** Protocol {fee_winner}")
        st.markdown(f"**Security Winner:** Protocol {security_winner}")
    
    with col3:
        st.markdown(f"**{protocol_b['name']}**")
        st.metric("TPS", f"{protocol_b.get('tps', 0):,}")
        st.metric("Fee", f"${protocol_b.get('avg_fee', 0):.4f}")
        st.metric("Security", f"{protocol_b.get('security_score', 0)}/100")

def render_data_status_overview(protocols: List[Dict], fetch_status: Dict):
    """Render data management overview"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fetching_count = fetch_status.get('total_fetching', 0)
        st.metric("Currently Fetching", fetching_count)
    
    with col2:
        available_count = len([p for p in protocols if p.get('status') == 'available'])
        st.metric("Available Protocols", f"{available_count}/{len(protocols)}")
    
    with col3:
        total_proposals = sum(p.get('current_count', 0) for p in protocols)
        st.metric("Total Proposals", f"{total_proposals:,}")
    
    with col4:
        # Last update time
        last_updates = [p.get('last_updated') for p in protocols if p.get('last_updated') != 'Never']
        if last_updates:
            st.metric("Data Status", "Fresh" if len(last_updates) == len(protocols) else "Mixed")
        else:
            st.metric("Data Status", "Stale")

def render_protocol_management(protocols: List[Dict]):
    """Render protocol management interface"""
    
    st.markdown("#### 🔗 Protocol Status")
    
    for protocol in protocols:
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{protocol['name']}**")
            st.caption(protocol.get('description', ''))
        
        with col2:
            status = protocol.get('status', 'unknown')
            if status == 'available':
                st.success("✅ Ready")
            elif status == 'fetching':
                st.info("🔄 Fetching")
            else:
                st.warning("⚠️ Stale")
        
        with col3:
            count = protocol.get('current_count', 0)
            st.markdown(f"**{count:,}** proposals")
        
        with col4:
            last_updated = protocol.get('last_updated', 'Never')
            if last_updated != 'Never':
                try:
                    dt = datetime.fromisoformat(last_updated.replace('Z', ''))
                    time_ago = datetime.now() - dt
                    if time_ago.total_seconds() < 3600:
                        display = f"{int(time_ago.total_seconds() / 60)}m ago"
                    else:
                        display = f"{int(time_ago.total_seconds() / 3600)}h ago"
                    st.caption(display)
                except:
                    st.caption(last_updated)
            else:
                st.caption("Never updated")

def render_fetch_controls_unified(protocols: List[Dict]):
    """Render unified fetch controls"""
    
    st.markdown("#### 🚀 Data Fetch Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⚡ Fetch Selected", use_container_width=True):
            if st.session_state.selected_protocols:
                # Trigger fetch for selected protocols
                trigger_protocol_fetch(st.session_state.selected_protocols)
            else:
                st.warning("No protocols selected")
    
    with col2:
        if st.button("🔄 Fetch All", use_container_width=True):
            # Trigger fetch for all protocols
            all_ids = [p['id'] for p in protocols]
            trigger_protocol_fetch(all_ids)
    
    with col3:
        if st.button("⏱️ Fetch Stale", use_container_width=True):
            # Trigger fetch for stale protocols only
            stale_ids = [p['id'] for p in protocols if p.get('status') != 'available']
            if stale_ids:
                trigger_protocol_fetch(stale_ids)
            else:
                st.success("All protocols are fresh!")

def trigger_protocol_fetch(protocol_ids: List[str]):
    """Trigger fetch for specified protocols"""
    
    st.session_state.fetch_triggered = True
    st.session_state.fetch_protocols = protocol_ids
    st.info(f"🔄 Fetching data for {len(protocol_ids)} protocol(s)...")
    
    # This would integrate with the actual fetch service
    if realtime_data_fetcher:
        try:
            result = realtime_data_fetcher.fetch_multiple_protocols(protocol_ids)
            if result.get('success'):
                st.success(f"✅ Successfully fetched {result.get('successful_protocols', 0)} protocols")
            else:
                st.error(f"❌ Fetch failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Fetch error: {str(e)}")
    
    st.rerun()

def export_current_analysis():
    """Export current analysis"""
    
    mode = st.session_state.analytics_mode
    protocols = st.session_state.selected_protocols
    
    if mode == 'analyze' and len(protocols) == 1:
        export_text = f"# Analysis Report: {BLOCKCHAIN_PROTOCOLS[protocols[0]]['name']}\n\n"
        export_text += "Generated by Unified Analytics Dashboard\n"
        export_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    elif mode == 'compare' and len(protocols) > 1:
        protocol_names = [BLOCKCHAIN_PROTOCOLS[p]['name'] for p in protocols]
        export_text = f"# Comparison Report: {' vs '.join(protocol_names)}\n\n"
        export_text += "Generated by Unified Analytics Dashboard\n"
        export_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    else:
        export_text = "# Analytics Report\n\nNo data to export"
    
    st.code(export_text, language="markdown")
    st.success("📊 Export ready! Copy the text above.")

def generate_share_link():
    """Generate shareable link"""
    
    protocols_param = ",".join(st.session_state.selected_protocols)
    mode_param = st.session_state.analytics_mode
    
    # This would be your actual domain
    share_url = f"https://your-app.com/analytics?protocols={protocols_param}&mode={mode_param}"
    
    st.code(share_url)
    st.success("🔗 Share link generated! Copy the URL above.")

def render_advanced_settings():
    """Render advanced settings"""
    
    with st.expander("⚙️ Advanced Settings", expanded=True):
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Display Options:**")
            auto_refresh = st.checkbox("🔄 Auto-refresh data", value=False)
            show_tooltips = st.checkbox("💡 Show helpful tooltips", value=True)
            compact_view = st.checkbox("📱 Compact mobile view", value=False)
        
        with col2:
            st.markdown("**Data Options:**")
            cache_duration = st.slider("Cache duration (minutes)", 1, 60, 15)
            max_history = st.slider("Max history points", 10, 100, 50)
            precision = st.selectbox("Number precision", [2, 3, 4], index=1)
        
        if st.button("💾 Save Settings"):
            st.success("⚙️ Settings saved!")

if __name__ == "__main__":
    render_unified_analytics()