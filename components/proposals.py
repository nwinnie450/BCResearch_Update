"""
Blockchain Proposals Component - Web Scraping Based
Displays improvement proposals using pre-scraped data
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from services.scraped_data_service import scraped_data_service

def render_proposals_interface():
    """Render proposals interface using web-scraped data"""
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📋 Blockchain Proposals")
        st.markdown("Comprehensive improvement proposals from web scraping")
    
    with col2:
        if st.button("🔄 Refresh", help="Refresh proposal data"):
            st.rerun()
        st.success("🚀 Scrapped Data")
    
    st.markdown("---")
    
    # Proposal type and status filter section
    with st.expander("⚙️ Filter Options", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Proposal Types")
            proposal_types = st.multiselect(
                "Select proposal types:",
                options=['EIP', 'TIP', 'BIP', 'BEP'],
                default=['TIP'],
                help="Choose which types of blockchain improvement proposals to display"
            )
        
        with col2:
            st.markdown("#### Sort & Filter")
            
            # Status filter
            status_options = {
                'All Statuses': None,
                'Draft': 'draft',
                'Final/Production': 'final',
                'Proposed': 'proposed',
                'Review': 'review',
                'Withdrawn': 'withdrawn',
                'Living': 'living',
                'Stagnant': 'stagnant'
            }
            
            selected_status = st.selectbox(
                "Filter by status:",
                options=list(status_options.keys()),
                index=0,
                help="Filter proposals by their current status"
            )
            
            status_filter = status_options[selected_status]
            
            limit_results = st.number_input(
                "Maximum results per type:",
                min_value=5,
                max_value=100,
                value=20,
                step=5,
                help="Limit the number of proposals shown for each type"
            )
    
    # Fetch and display button
    if st.button("🔍 Fetch Proposals", type="primary", use_container_width=True):
        if not proposal_types:
            st.warning("Please select at least one proposal type.")
        else:
            with st.spinner(f"Loading {', '.join(proposal_types)} proposals{' with ' + selected_status.lower() + ' status' if status_filter else ''}..."):
                try:
                    all_proposals = []
                    
                    # Map proposal types to protocols
                    protocol_map = {
                        'EIP': 'ethereum',
                        'BIP': 'bitcoin', 
                        'TIP': 'tron',
                        'BEP': 'binance_smart_chain'
                    }
                    
                    standards_data = []
                    
                    for proposal_type in proposal_types:
                        if proposal_type in protocol_map:
                            protocol = protocol_map[proposal_type]
                            
                            # Get proposals using scraped data service
                            proposals = scraped_data_service.get_latest_proposals(
                                protocol, 
                                limit=limit_results,
                                status_filter=status_filter
                            )
                            
                            # Add type information
                            for proposal in proposals:
                                proposal['type'] = proposal_type
                                proposal['protocol'] = protocol
                            
                            all_proposals.extend(proposals)
                            
                            # Add to standards data for display
                            standards_data.append({
                                'standard': proposal_type,
                                'source': f"Web Scraped - {protocol_map.get(proposal_type, 'Unknown')} repository",
                                'items': proposals
                            })
                    
                    st.session_state.proposals_result = {
                        'success': True,
                        'standards': standards_data,
                        'total_count': len(all_proposals),
                        'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Store filter info
                    st.session_state.proposals_filter = {
                        'types': proposal_types,
                        'status': status_filter,
                        'selected_status_text': selected_status,
                        'limit': limit_results
                    }
                    
                    st.success(f"✅ Successfully loaded {len(all_proposals)} proposals!")
                    
                except Exception as e:
                    st.error(f"❌ Error loading proposals: {str(e)}")
    
    # Display fetched results
    if hasattr(st.session_state, 'proposals_result') and st.session_state.proposals_result:
        render_proposals_results(st.session_state.proposals_result, st.session_state.proposals_filter)
    
    # Quick action buttons
    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Draft TIPs", use_container_width=True):
            quick_fetch_and_display(['TIP'], 'draft', "Draft TIPs")
    
    with col2:
        if st.button("🔥 Final TIPs", use_container_width=True):
            quick_fetch_and_display(['TIP'], 'final', "Final TIPs")
    
    with col3:
        if st.button("⚡ All EIPs", use_container_width=True):
            quick_fetch_and_display(['EIP'], None, "All EIPs")
    
    with col4:
        if st.button("💎 Draft BIPs", use_container_width=True):
            quick_fetch_and_display(['BIP'], 'draft', "Draft BIPs")

def render_proposals_results(result: Dict, filter_config: Dict):
    """Render the fetched proposals results"""
    
    st.markdown("---")
    st.markdown("### 📊 Results")
    
    # Show filter summary
    filter_summary = f"**Showing:** {', '.join(filter_config['types'])}"
    if filter_config['status']:
        filter_summary += f" | **Status:** {filter_config['selected_status_text']}"
    
    st.markdown(filter_summary)
    st.markdown(f"**Loaded at:** {result.get('fetched_at', 'Unknown')}")
    
    standards_data = result.get('standards', [])
    
    if not standards_data:
        st.warning("No proposals found matching the selected criteria.")
        return
    
    # Create tabs for different proposal types
    if len(standards_data) > 1:
        tab_names = [f"{std.get('standard', 'Unknown')} ({len(std.get('items', []))})" for std in standards_data]
        tabs = st.tabs(tab_names)
        
        for i, (tab, standard_data) in enumerate(zip(tabs, standards_data)):
            with tab:
                render_standard_proposals(standard_data, filter_config)
    else:
        # Single proposal type - no tabs needed
        render_standard_proposals(standards_data[0], filter_config)

def render_standard_proposals(standard_data: Dict, filter_config: Dict):
    """Render proposals for a specific standard (e.g., TIP, EIP)"""
    
    standard = standard_data.get('standard', 'Unknown')
    source = standard_data.get('source', '')
    items = standard_data.get('items', [])
    
    if not items:
        st.info(f"No {standard} proposals found with the current filters.")
        return
    
    st.markdown(f"**Source:** {source}")
    st.markdown(f"**Found:** {len(items)} proposals")
    
    # Create a table for better display
    table_data = []
    for item in items:
        created_date = item.get('created')
        # Better handling for empty creation dates
        if not created_date or created_date.strip() == "":
            created_display = 'Not available'
        else:
            created_display = created_date
            
        table_data.append({
            'ID': f"{standard}-{item.get('number', 'N/A')}",
            'Title': item.get('title', 'No title available')[:80] + ('...' if len(item.get('title', '')) > 80 else ''),
            'Status': item.get('status', 'Unknown'),
            'Author': item.get('author', 'Unknown')[:30] + ('...' if len(item.get('author', '')) > 30 else ''),
            'Created': created_display
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        # Reset index to start from 1 instead of 0
        df.index = range(1, len(df) + 1)
        st.dataframe(df, use_container_width=True, height=400)
        
        # Show detailed view option
        if st.checkbox(f"Show detailed {standard} information", key=f"details_{standard}"):
            render_detailed_proposals(items, standard)
    
    # Export option
    if st.button(f"📥 Export {standard} Data", key=f"export_{standard}", use_container_width=True):
        export_proposals_data(items, standard)

def render_detailed_proposals(items: List[Dict], standard: str):
    """Render detailed view of proposals with pagination"""
    
    st.markdown(f"#### Detailed {standard} Information")
    st.markdown(f"**Total Proposals:** {len(items)}")
    
    # Add pagination for better performance and UX
    items_per_page = 10
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        page = st.selectbox(
            f"Select page (showing {items_per_page} items per page):",
            options=list(range(1, total_pages + 1)),
            format_func=lambda x: f"Page {x} of {total_pages}",
            key=f"page_selector_{standard}"
        )
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_items = items[start_idx:end_idx]
        
        st.markdown(f"*Showing items {start_idx + 1}-{min(end_idx, len(items))} of {len(items)}*")
    else:
        page_items = items
    
    # Display all items for the current page
    for i, item in enumerate(page_items, start=(0 if total_pages <= 1 else (page - 1) * items_per_page)):
        item_number = i + 1
        with st.expander(f"#{item_number} - {standard}-{item.get('number', 'N/A')}: {item.get('title', 'No title')}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Basic Information:**")
                st.markdown(f"- **Number:** {item.get('number', 'N/A')}")
                
                # Enhanced status display with color coding
                status = item.get('status', 'Unknown')
                status_color = get_status_color(status)
                st.markdown(f"- **Status:** :{status_color}[{status}]")
                
                st.markdown(f"- **Type:** {item.get('type', 'Not specified')}")
                st.markdown(f"- **Category:** {item.get('category', 'Not specified')}")
                
                # Timeline information
                if item.get('created'):
                    st.markdown(f"- **Created:** {item.get('created')}")
            
            with col2:
                st.markdown("**Links & Author:**")
                if item.get('url'):
                    st.markdown(f"[📖 View Proposal]({item['url']})")
                if item.get('author'):
                    st.markdown(f"- **Author:** {item['author']}")
                
                # Additional metadata
                if item.get('summary'):
                    st.markdown(f"- **Summary Available:** ✅")
            
            if item.get('description'):
                st.markdown("**Description:**")
                st.markdown(item['description'][:300] + ('...' if len(item.get('description', '')) > 300 else ''))
            elif item.get('summary'):
                st.markdown("**Summary:**")
                st.markdown(item['summary'][:300] + ('...' if len(item.get('summary', '')) > 300 else ''))

def get_status_color(status: str) -> str:
    """Get color for status display"""
    status_lower = status.lower()
    
    color_map = {
        'draft': 'blue',
        'review': 'orange', 
        'proposed': 'orange',
        'final': 'green',
        'active': 'green',
        'living': 'green',
        'stagnant': 'gray',
        'withdrawn': 'red',
        'rejected': 'red'
    }
    
    return color_map.get(status_lower, 'gray')

def export_proposals_data(items: List[Dict], standard: str):
    """Export proposals data as downloadable file"""
    
    if not items:
        st.warning("No data to export.")
        return
    
    try:
        df = pd.DataFrame(items)
        csv_data = df.to_csv(index=False)
        
        st.download_button(
            label=f"📥 Download {standard} data as CSV",
            data=csv_data,
            file_name=f"{standard}_proposals_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key=f"download_{standard}"
        )
        
        st.success(f"✅ {standard} data prepared for download!")
        
    except Exception as e:
        st.error(f"❌ Error preparing export: {str(e)}")

def quick_fetch_and_display(proposal_types: List[str], status_filter: Optional[str], title: str):
    """Quick fetch and display for action buttons"""
    
    with st.spinner(f"Loading {title.lower()}..."):
        try:
            all_proposals = []
            protocol_map = {
                'TIP': 'tron',
                'EIP': 'ethereum',
                'BIP': 'bitcoin', 
                'BEP': 'binance_smart_chain'
            }
            
            standards_data = []
            
            for proposal_type in proposal_types:
                if proposal_type in protocol_map:
                    protocol = protocol_map[proposal_type]
                    proposals = scraped_data_service.get_latest_proposals(
                        protocol, 
                        limit=10,
                        status_filter=status_filter
                    )
                    
                    for proposal in proposals:
                        proposal['type'] = proposal_type
                        proposal['protocol'] = protocol
                    
                    all_proposals.extend(proposals)
                    
                    standards_data.append({
                        'standard': proposal_type,
                        'source': f"Web Scraped - {protocol_map.get(proposal_type, 'Unknown')} repository",
                        'items': proposals
                    })
            
            # Store in session state
            st.session_state.proposals_result = {
                'success': True,
                'standards': standards_data,
                'total_count': len(all_proposals),
                'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            st.session_state.proposals_filter = {
                'types': proposal_types,
                'status': status_filter,
                'selected_status_text': title,
                'limit': 10
            }
            
            st.success(f"✅ {title} loaded!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")