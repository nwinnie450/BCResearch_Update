#!/usr/bin/env python3
"""
Real-Time Data Fetching Interface Component
Provides UI for selective, real-time blockchain proposal data fetching
"""
import streamlit as st
import time
from datetime import datetime, timedelta
from typing import Dict, List
from services.realtime_data_fetcher import realtime_data_fetcher

def render_realtime_data_interface():
    """Render the real-time data fetching interface"""
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### ⚡ Real-Time Data Fetcher")
        st.markdown("Fetch fresh blockchain proposal data for selected protocols")
    
    with col2:
        if st.button("🔄 Refresh Status", help="Refresh the interface"):
            st.rerun()
    
    # Get current protocol status
    protocols = realtime_data_fetcher.get_protocol_list()
    fetch_status = realtime_data_fetcher.get_fetch_status()
    
    # Show overall status
    render_overall_status(fetch_status)
    
    st.markdown("---")
    
    # Protocol selection and status
    render_protocol_selection(protocols)
    
    st.markdown("---")
    
    # Fetch controls
    render_fetch_controls(protocols)
    
    st.markdown("---")
    
    # Recent results
    render_recent_results()

def render_overall_status(fetch_status: Dict):
    """Render overall fetching status"""
    
    st.markdown("#### 📊 System Status")
    
    # API Enhancement Status
    try:
        from services.enhanced_api_service import enhanced_api_service
        api_status = enhanced_api_service.get_api_status()
        configured_apis = len(api_status['configured_apis'])
        accuracy_level = api_status['accuracy_level']
        
        if configured_apis > 0:
            st.success(f"🔑 **Enhanced APIs Active**: {configured_apis} API keys configured | {accuracy_level}")
        else:
            st.info("💡 **Using Free APIs**: Add API keys for higher accuracy ([Setup Guide](API_KEYS_SETUP.md))")
    except:
        pass
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if fetch_status['total_fetching'] > 0:
            st.metric("Currently Fetching", fetch_status['total_fetching'], delta="Active")
        else:
            st.metric("Currently Fetching", "0", delta="Idle")
    
    with col2:
        protocols = realtime_data_fetcher.get_protocol_list()
        available_count = len([p for p in protocols if p['status'] == 'available'])
        st.metric("Protocols Available", f"{available_count}/4")
    
    with col3:
        total_proposals = sum(p['current_count'] for p in protocols)
        st.metric("Total Proposals", f"{total_proposals:,}")
    
    with col4:
        # Show last fetch time
        last_fetches = [p['last_fetch'] for p in protocols if p['last_fetch']]
        if last_fetches:
            try:
                latest = max(last_fetches)
                latest_dt = datetime.fromisoformat(latest.replace('Z', ''))
                time_ago = datetime.now() - latest_dt
                
                if time_ago.total_seconds() < 3600:
                    time_display = f"{int(time_ago.total_seconds() / 60)}m ago"
                elif time_ago.total_seconds() < 86400:
                    time_display = f"{int(time_ago.total_seconds() / 3600)}h ago"
                else:
                    time_display = f"{time_ago.days}d ago"
                
                st.metric("Last Fetch", time_display)
            except:
                st.metric("Last Fetch", "Unknown")
        else:
            st.metric("Last Fetch", "Never")
    
    # Show active fetching
    if fetch_status['currently_fetching']:
        st.info(f"🔄 **Currently fetching:** {', '.join(fetch_status['currently_fetching'])}")

def render_protocol_selection(protocols: List[Dict]):
    """Render protocol selection interface"""
    
    st.markdown("#### 🔗 Protocol Selection")
    st.markdown("Select which blockchain protocols to fetch fresh data for:")
    
    # Create protocol cards
    col1, col2 = st.columns(2)
    
    selected_protocols = []
    
    for i, protocol in enumerate(protocols):
        with col1 if i % 2 == 0 else col2:
            # Create expandable card for each protocol
            with st.container():
                # Protocol header
                col_check, col_name, col_status = st.columns([0.3, 2, 1])
                
                with col_check:
                    if protocol['is_fetching']:
                        st.markdown("🔄")
                        is_selected = False
                    else:
                        is_selected = st.checkbox("", key=f"select_{protocol['id']}")
                        if is_selected:
                            selected_protocols.append(protocol['id'])
                
                with col_name:
                    st.markdown(f"**{protocol['name']}**")
                    st.caption(protocol['description'])
                
                with col_status:
                    if protocol['status'] == 'available':
                        st.success("✅ Ready")
                    elif protocol['status'] == 'fetching':
                        st.info("🔄 Fetching")
                    elif protocol['status'] == 'missing':
                        st.warning("⚠️ No Data")
                    else:
                        st.error("❌ Error")
                
                # Protocol details
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    st.markdown(f"**Current:** {protocol['current_count']:,} proposals")
                
                with detail_col2:
                    if protocol['last_updated'] != 'Never':
                        try:
                            last_update = datetime.fromisoformat(protocol['last_updated'].replace('Z', ''))
                            time_ago = datetime.now() - last_update
                            
                            if time_ago.total_seconds() < 3600:
                                time_display = f"{int(time_ago.total_seconds() / 60)}m ago"
                            elif time_ago.total_seconds() < 86400:
                                time_display = f"{int(time_ago.total_seconds() / 3600)}h ago"
                            else:
                                time_display = f"{time_ago.days}d ago"
                            
                            st.markdown(f"**Updated:** {time_display}")
                        except:
                            st.markdown(f"**Updated:** {protocol['last_updated']}")
                    else:
                        st.markdown("**Updated:** Never")
                
                st.markdown("---")
    
    # Store selected protocols in session state
    st.session_state.selected_protocols = selected_protocols
    
    # Quick selection buttons
    st.markdown("**🚀 Quick Actions:**")
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    
    with quick_col1:
        if st.button("Select All", use_container_width=True):
            for protocol in protocols:
                if not protocol['is_fetching']:
                    st.session_state[f"select_{protocol['id']}"] = True
            st.rerun()
    
    with quick_col2:
        if st.button("Select None", use_container_width=True):
            for protocol in protocols:
                st.session_state[f"select_{protocol['id']}"] = False
            st.rerun()
    
    with quick_col3:
        if st.button("Select Stale", use_container_width=True):
            for protocol in protocols:
                # Select if last updated more than 1 hour ago or never
                is_stale = False
                if protocol['last_updated'] == 'Never':
                    is_stale = True
                else:
                    try:
                        last_update = datetime.fromisoformat(protocol['last_updated'].replace('Z', ''))
                        time_ago = datetime.now() - last_update
                        is_stale = time_ago.total_seconds() > 3600  # More than 1 hour
                    except:
                        is_stale = True
                
                if is_stale and not protocol['is_fetching']:
                    st.session_state[f"select_{protocol['id']}"] = True
                else:
                    st.session_state[f"select_{protocol['id']}"] = False
            st.rerun()
    
    with quick_col4:
        # Show selection count
        selected_count = len(selected_protocols)
        if selected_count > 0:
            st.info(f"📋 {selected_count} selected")
        else:
            st.info("📋 None selected")

def render_fetch_controls(protocols: List[Dict]):
    """Render fetch control buttons"""
    
    st.markdown("#### 🚀 Fetch Controls")
    
    selected_protocols = getattr(st.session_state, 'selected_protocols', [])
    any_fetching = any(p['is_fetching'] for p in protocols)
    
    if not selected_protocols:
        st.info("💡 **Select protocols above to enable fetching**")
        return
    
    # Show what will be fetched
    selected_names = [p['name'] for p in protocols if p['id'] in selected_protocols]
    st.markdown(f"**Will fetch:** {', '.join(selected_names)}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(
            f"⚡ Fetch Selected ({len(selected_protocols)})",
            type="primary",
            use_container_width=True,
            disabled=any_fetching
        ):
            # Trigger fetch for selected protocols
            st.session_state.fetch_triggered = True
            st.session_state.fetch_protocols = selected_protocols.copy()
            st.rerun()
    
    with col2:
        if st.button(
            "🔄 Fetch All Protocols",
            use_container_width=True,
            disabled=any_fetching
        ):
            # Trigger fetch for all protocols
            all_protocol_ids = [p['id'] for p in protocols if not p['is_fetching']]
            st.session_state.fetch_triggered = True
            st.session_state.fetch_protocols = all_protocol_ids
            st.rerun()
    
    with col3:
        if st.button(
            "⏱️ Fetch Stale Only",
            use_container_width=True,
            disabled=any_fetching
        ):
            # Trigger fetch for stale protocols only
            stale_protocols = []
            for protocol in protocols:
                if protocol['is_fetching']:
                    continue
                
                is_stale = False
                if protocol['last_updated'] == 'Never':
                    is_stale = True
                else:
                    try:
                        last_update = datetime.fromisoformat(protocol['last_updated'].replace('Z', ''))
                        time_ago = datetime.now() - last_update
                        is_stale = time_ago.total_seconds() > 3600  # More than 1 hour
                    except:
                        is_stale = True
                
                if is_stale:
                    stale_protocols.append(protocol['id'])
            
            if stale_protocols:
                st.session_state.fetch_triggered = True
                st.session_state.fetch_protocols = stale_protocols
                st.rerun()
            else:
                st.info("✅ No stale protocols found")
    
    # Handle fetch execution
    if getattr(st.session_state, 'fetch_triggered', False):
        execute_fetch()

def execute_fetch():
    """Execute the triggered fetch operation"""
    
    fetch_protocols = getattr(st.session_state, 'fetch_protocols', [])
    
    if not fetch_protocols:
        st.session_state.fetch_triggered = False
        return
    
    st.markdown("### 🔄 Fetching Data...")
    
    # Create progress containers
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.empty()
    
    try:
        if len(fetch_protocols) == 1:
            # Single protocol fetch
            protocol_id = fetch_protocols[0]
            status_text.info(f"🔄 Fetching {protocol_id}...")
            
            with st.spinner(f"Fetching {protocol_id} data..."):
                result = realtime_data_fetcher.fetch_protocol_data(protocol_id)
            
            progress_bar.progress(1.0)
            
            if result['success']:
                status_text.success(f"✅ {result['message']}")
                results_container.json(result)
            else:
                status_text.error(f"❌ Error: {result['error']}")
                results_container.json(result)
        
        else:
            # Multiple protocol fetch
            status_text.info(f"🔄 Fetching {len(fetch_protocols)} protocols in parallel...")
            
            with st.spinner(f"Fetching {len(fetch_protocols)} protocols..."):
                def update_callback(result):
                    # This could be used for real-time updates if needed
                    pass
                
                summary = realtime_data_fetcher.fetch_multiple_protocols(
                    fetch_protocols, 
                    callback=update_callback
                )
            
            progress_bar.progress(1.0)
            
            if summary['success']:
                status_text.success(
                    f"✅ Completed! {summary['successful_protocols']}/{summary['total_protocols']} protocols fetched successfully. "
                    f"Total: {summary['total_proposals_fetched']:,} proposals in {summary['total_duration']}s"
                )
            else:
                status_text.error(f"❌ Fetch failed: {summary.get('error', 'Unknown error')}")
            
            # Show detailed results
            results_container.json(summary)
    
    except Exception as e:
        status_text.error(f"❌ Exception during fetch: {str(e)}")
        progress_bar.progress(1.0)
    
    finally:
        # Clear the trigger
        st.session_state.fetch_triggered = False
        st.session_state.fetch_protocols = []
        
        # Auto-refresh after 3 seconds
        time.sleep(1)
        st.rerun()

def render_recent_results():
    """Render recent fetch results"""
    
    st.markdown("#### 📋 Recent Results")
    
    fetch_status = realtime_data_fetcher.get_fetch_status()
    
    has_results = False
    
    for protocol_id, status in fetch_status['protocols'].items():
        last_result = status.get('last_result', {})
        
        if last_result:
            has_results = True
            
            # Get protocol info
            protocols = realtime_data_fetcher.get_protocol_list()
            protocol_info = next((p for p in protocols if p['id'] == protocol_id), None)
            
            if protocol_info:
                protocol_name = protocol_info['name']
            else:
                protocol_name = protocol_id
            
            with st.expander(f"{protocol_name} - Last Result", expanded=False):
                if last_result.get('success', False):
                    st.success(f"✅ {last_result.get('message', 'Success')}")
                    st.info(f"⏱️ Duration: {last_result.get('duration', 0)}s | 📊 Count: {last_result.get('count', 0):,}")
                else:
                    st.error(f"❌ {last_result.get('error', 'Unknown error')}")
                    if 'duration' in last_result:
                        st.info(f"⏱️ Duration: {last_result.get('duration', 0)}s")
                
                # Show full result data
                st.json(last_result)
    
    if not has_results:
        st.info("No recent fetch results available. Fetch some data to see results here!")