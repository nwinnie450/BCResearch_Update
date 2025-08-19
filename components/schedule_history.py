"""
Schedule History Component
Shows execution history and logs for scheduled runs
"""
import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List

def render_schedule_history():
    """Render schedule execution history interface"""
    
    st.markdown("### 📊 Schedule Execution History")
    st.markdown("Track when schedules run and their results")
    
    # Load execution history
    history = load_execution_history()
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_runs = len(history)
        st.metric("Total Runs", total_runs)
    
    with col2:
        successful_runs = len([h for h in history if h.get('success', False)])
        st.metric("Successful", successful_runs)
    
    with col3:
        failed_runs = total_runs - successful_runs
        st.metric("Failed", failed_runs)
    
    with col4:
        if history:
            last_run = max(history, key=lambda x: x.get('timestamp', ''))
            last_run_time = last_run.get('timestamp', 'Never')
            if last_run_time != 'Never':
                try:
                    dt = datetime.fromisoformat(last_run_time.replace('Z', '+00:00'))
                    last_run_time = dt.strftime('%H:%M:%S')
                except:
                    pass
            st.metric("Last Run", last_run_time)
        else:
            st.metric("Last Run", "Never")
    
    # Filter controls
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_last_hours = st.selectbox(
            "Show last:",
            [6, 12, 24, 48, 168], # hours
            index=2,
            format_func=lambda x: f"{x} hours" if x < 168 else "1 week"
        )
    
    with col2:
        status_filter = st.selectbox(
            "Filter by status:",
            ["All", "Success", "Failed"],
            index=0
        )
    
    with col3:
        if st.button("🔄 Refresh History"):
            st.rerun()
    
    # Filter history
    filtered_history = filter_history(history, show_last_hours, status_filter)
    
    # Display history
    if filtered_history:
        render_history_table(filtered_history)
        
        # Detailed view
        st.markdown("---")
        st.markdown("#### 📋 Detailed Execution Logs")
        
        if st.checkbox("Show detailed logs"):
            render_detailed_logs(filtered_history)
    else:
        st.info("No execution history found. The scheduler hasn't run yet.")
        
        # Help section
        st.markdown("### 🚀 Getting Started")
        st.markdown("""
        To see schedule execution history:
        1. **Start the scheduler**: Run `python start_scheduler.py` 
        2. **Wait for scheduled time**: Schedules will trigger automatically
        3. **Check this page**: View execution results and logs
        
        **Manual Test**: Use the test button below to simulate a schedule run.
        """)
        
        if st.button("🧪 Test Schedule Execution"):
            test_schedule_execution()

def load_execution_history() -> List[Dict]:
    """Load schedule execution history from file"""
    history_file = "data/schedule_history.json"
    
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_execution_record(record: Dict):
    """Save a single execution record"""
    history_file = "data/schedule_history.json"
    os.makedirs("data", exist_ok=True)
    
    # Load existing history
    history = load_execution_history()
    
    # Add new record
    history.append(record)
    
    # Keep only last 100 records to prevent file from growing too large
    if len(history) > 100:
        history = history[-100:]
    
    # Save back to file
    try:
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        st.error(f"Error saving execution record: {e}")

def filter_history(history: List[Dict], last_hours: int, status_filter: str) -> List[Dict]:
    """Filter history based on time and status"""
    if not history:
        return []
    
    # Time filter
    cutoff_time = datetime.now() - timedelta(hours=last_hours)
    filtered = []
    
    for record in history:
        try:
            record_time = datetime.fromisoformat(record.get('timestamp', '').replace('Z', '+00:00'))
            if record_time >= cutoff_time:
                filtered.append(record)
        except:
            # If we can't parse the timestamp, include it anyway
            filtered.append(record)
    
    # Status filter
    if status_filter == "Success":
        filtered = [r for r in filtered if r.get('success', False)]
    elif status_filter == "Failed":
        filtered = [r for r in filtered if not r.get('success', False)]
    
    # Sort by timestamp (newest first)
    filtered.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return filtered

def render_history_table(history: List[Dict]):
    """Render history as a table"""
    
    if not history:
        st.info("No records match the current filters.")
        return
    
    # Convert to table data
    table_data = []
    for record in history:
        timestamp = record.get('timestamp', 'Unknown')
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_str = timestamp
        
        table_data.append({
            'Time': time_str,
            'Schedule': record.get('schedule_name', 'Unknown'),
            'Status': '✅ Success' if record.get('success', False) else '❌ Failed',
            'Duration': f"{record.get('duration_seconds', 0):.1f}s",
            'New Proposals': record.get('new_proposals_count', 0),
            'Details': (record.get('summary', 'No details')[:50] + '...') if len(record.get('summary', '')) > 50 else record.get('summary', 'No details')
        })
    
    # Display as dataframe with custom index starting from 1
    df = pd.DataFrame(table_data)
    df.index = range(1, len(df) + 1)  # Set index to start from 1
    
    # Configure column widths to ensure Details column is visible
    column_config = {
        'Time': st.column_config.DatetimeColumn(width="medium"),
        'Schedule': st.column_config.TextColumn(width="medium"),
        'Status': st.column_config.TextColumn(width="small"),
        'Duration': st.column_config.TextColumn(width="small"),
        'New Proposals': st.column_config.NumberColumn(width="small"),
        'Details': st.column_config.TextColumn(width="large")
    }
    
    st.dataframe(
        df, 
        use_container_width=True, 
        height=400,
        column_config=column_config
    )

def render_detailed_logs(history: List[Dict]):
    """Render detailed logs for each execution"""
    
    for i, record in enumerate(history[:5]):  # Show last 5 detailed
        timestamp = record.get('timestamp', 'Unknown')
        success = record.get('success', False)
        status_icon = '✅' if success else '❌'
        
        with st.expander(f"{status_icon} {record.get('schedule_name', 'Unknown')} - {timestamp}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Execution Details:**")
                st.markdown(f"- **Start Time**: {record.get('start_time', 'Unknown')}")
                st.markdown(f"- **Duration**: {record.get('duration_seconds', 0):.2f} seconds")
                st.markdown(f"- **Status**: {'Success' if success else 'Failed'}")
                st.markdown(f"- **New Proposals**: {record.get('new_proposals_count', 0)}")
            
            with col2:
                st.markdown("**Results:**")
                if record.get('error'):
                    st.error(f"Error: {record['error']}")
                
                if record.get('new_proposals'):
                    st.markdown("**New Proposals Found:**")
                    for protocol, proposals in record['new_proposals'].items():
                        st.markdown(f"- **{protocol.title()}**: {len(proposals)} proposals")
            
            if record.get('logs'):
                st.markdown("**Execution Logs:**")
                st.code(record['logs'])

def test_schedule_execution():
    """Test schedule execution and create a sample record"""
    
    with st.spinner("Running test schedule execution..."):
        try:
            from services.schedule_executor import ScheduleExecutor
            
            start_time = datetime.now()
            
            # Create executor and run test
            executor = ScheduleExecutor()
            result = executor.check_for_new_proposals()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Create execution record
            record = {
                'timestamp': end_time.isoformat() + 'Z',
                'start_time': start_time.isoformat() + 'Z',
                'schedule_name': 'Manual Test',
                'success': result,
                'duration_seconds': duration,
                'new_proposals_count': 0,  # Would be populated by actual execution
                'summary': 'Manual test execution from UI',
                'test_run': True
            }
            
            # Save the record
            save_execution_record(record)
            
            if result:
                st.success("✅ Test execution completed successfully!")
            else:
                st.warning("⚠️ Test execution completed with warnings")
                
            st.info("Refresh the page to see the test execution in the history.")
            
        except Exception as e:
            # Save failed record
            record = {
                'timestamp': datetime.now().isoformat() + 'Z',
                'schedule_name': 'Manual Test',
                'success': False,
                'error': str(e),
                'summary': f'Test execution failed: {str(e)[:100]}',
                'test_run': True
            }
            save_execution_record(record)
            
            st.error(f"❌ Test execution failed: {str(e)}")

# Utility function to be called by the actual scheduler
def log_schedule_execution(schedule_name: str, success: bool, start_time: datetime, 
                          new_proposals: Dict = None, error: str = None, 
                          logs: str = None) -> None:
    """Log a schedule execution (called by scheduler)"""
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    record = {
        'timestamp': end_time.isoformat() + 'Z',
        'start_time': start_time.isoformat() + 'Z',
        'schedule_name': schedule_name,
        'success': success,
        'duration_seconds': duration,
        'new_proposals': new_proposals or {},
        'new_proposals_count': sum(len(props) for props in (new_proposals or {}).values()),
        'error': error,
        'logs': logs,
        'summary': f"Executed {schedule_name}: {'Success' if success else 'Failed'}"
    }
    
    save_execution_record(record)

if __name__ == "__main__":
    render_schedule_history()