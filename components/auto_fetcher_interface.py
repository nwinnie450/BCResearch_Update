"""
Auto Proposal Fetcher Interface Component
Simplified interface for automatic proposal fetching with table-based schedule management
"""
import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, time
from typing import Dict, List, Optional
from services.auto_proposal_fetcher import AutoProposalFetcher

def render_auto_fetcher_interface():
    """Render the simplified auto proposal fetcher interface"""
    
    st.markdown("### 🤖 Auto Proposal Fetcher")
    st.markdown("**Simple schedule management for blockchain proposal monitoring**")
    
    # Initialize auto fetcher
    auto_fetcher = AutoProposalFetcher()
    
    # Main interface sections
    render_basic_settings(auto_fetcher)
    st.markdown("---")
    render_schedule_table(auto_fetcher)
    st.markdown("---")
    render_control_panel(auto_fetcher)

def render_basic_settings(auto_fetcher: AutoProposalFetcher):
    """Render simplified basic settings"""
    
    st.markdown("#### ⚙️ Basic Settings")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Enable/disable auto fetcher
        enabled = st.checkbox(
            "✅ Enable Auto Fetcher",
            value=auto_fetcher.config.get('enabled', True),
            help="Turn on/off automatic checking"
        )
    
    with col2:
        # Desktop notifications
        notifications_enabled = st.checkbox(
            "🔔 Desktop Notifications",
            value=auto_fetcher.config.get('notifications', {}).get('desktop', {}).get('enabled', True),
            help="Show popup notifications when new proposals found"
        )
    
    # Protocol selection (simplified)
    st.markdown("**Blockchains to monitor:**")
    protocol_options = {
        "Ethereum": "ethereum",
        "Tron": "tron", 
        "Bitcoin": "bitcoin",
        "Binance Smart Chain": "binance_smart_chain"
    }
    
    current_protocols = auto_fetcher.config.get('protocols', list(protocol_options.values()))
    
    cols = st.columns(4)
    selected_protocols = []
    for i, (display_name, protocol_id) in enumerate(protocol_options.items()):
        with cols[i]:
            if st.checkbox(display_name, value=protocol_id in current_protocols, key=f"protocol_{protocol_id}"):
                selected_protocols.append(protocol_id)
    
    # Save basic settings
    if st.button("💾 Save Settings"):
        try:
            auto_fetcher.config.update({
                'enabled': enabled,
                'protocols': selected_protocols if selected_protocols else list(protocol_options.values()),
                'notifications': {
                    'enabled': notifications_enabled,
                    'desktop': {'enabled': notifications_enabled, 'show_popup': True, 'play_sound': False}
                }
            })
            auto_fetcher.save_config()
            st.success("✅ Settings saved!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def render_schedule_table(auto_fetcher: AutoProposalFetcher):
    """Render simple schedule table for editing"""
    
    st.markdown("#### 📅 Schedule Management")
    
    # Add preset schedule options
    st.markdown("**Quick Presets:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📅 Once per day", help="Check once daily at 9am"):
            apply_preset_schedule("daily", st.session_state)
            st.rerun()
    
    with col2:
        if st.button("📅 Twice per week", help="Check Monday and Friday at 9am"):
            apply_preset_schedule("twice_weekly", st.session_state)
            st.rerun()
    
    with col3:
        if st.button("📅 Weekdays only", help="Check Mon-Fri at 9am"):
            apply_preset_schedule("weekdays", st.session_state)
            st.rerun()
    
    with col4:
        if st.button("📅 Business hours", help="Check Mon-Fri at 9am, 1pm, 5pm"):
            apply_preset_schedule("business", st.session_state)
            st.rerun()
    
    st.markdown("---")
    st.markdown("**Custom Schedule Table:**")
    st.markdown("*Click Time cells to open time picker*")
    
    # Initialize session state for schedule data - exactly 7 rows (one per day)
    if 'schedule_data' not in st.session_state:
        # Create exactly 7 rows, one for each day of the week - using strings for compatibility
        st.session_state.schedule_data = [
            {"Day": "Monday", "Time": "09:00", "Active": True},
            {"Day": "Tuesday", "Time": "09:00", "Active": False},
            {"Day": "Wednesday", "Time": "13:00", "Active": True},
            {"Day": "Thursday", "Time": "09:00", "Active": False},
            {"Day": "Friday", "Time": "17:00", "Active": True},
            {"Day": "Saturday", "Time": "09:00", "Active": False},
            {"Day": "Sunday", "Time": "09:00", "Active": False}
        ]
        # Load existing schedules if available
        existing_schedules = get_existing_schedules(auto_fetcher)
        if existing_schedules:
            # Merge existing schedules into the 7-day structure
            merge_existing_schedules(st.session_state.schedule_data, existing_schedules)
    
    # Create editable data editor with fixed 7 rows
    edited_df = st.data_editor(
        st.session_state.schedule_data,
        column_config={
            "Day": st.column_config.TextColumn(
                "Day",
                help="Day of the week (fixed)",
                width="medium",
                disabled=True  # Make day column read-only
            ),
            "Time": st.column_config.TextColumn(
                "Time (SGT)",
                help="Time in HH:MM format (e.g., 09:00, 13:30)",
                width="medium",
                validate=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"  # Validate HH:MM format
            ),
            "Active": st.column_config.CheckboxColumn(
                "Active",
                help="Enable/disable this schedule",
                width="small",
                default=True
            )
        },
        num_rows="fixed",  # Fixed number of rows
        use_container_width=True,
        key="schedule_editor"
    )
    
    # Update session state
    st.session_state.schedule_data = edited_df
    
    # Helper text for time format
    st.caption("💡 **Time format:** Use 24-hour format like 09:00, 13:30, 18:45. Click cells to edit Time and Active columns.")
    
    # Time picker helper
    st.markdown("**⏰ Quick Time Picker:**")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Day selector for time picker
        selected_day = st.selectbox(
            "Select day to change time:",
            options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            key="time_picker_day"
        )
    
    with col2:
        # Time picker
        from datetime import time
        current_time_str = next((s["Time"] for s in st.session_state.schedule_data if s["Day"] == selected_day), "09:00")
        try:
            hour, minute = map(int, current_time_str.split(':'))
            current_time = time(hour, minute)
        except:
            current_time = time(9, 0)
            
        new_time = st.time_input(
            "Pick new time:",
            value=current_time,
            step=1800,  # 30 minute steps
            key="time_picker_input"
        )
    
    with col3:
        if st.button("✅ Apply", help="Apply selected time to selected day"):
            # Update the selected day's time
            for i, schedule in enumerate(st.session_state.schedule_data):
                if schedule["Day"] == selected_day:
                    st.session_state.schedule_data[i]["Time"] = new_time.strftime('%H:%M')
                    st.success(f"✅ Updated {selected_day} to {new_time.strftime('%H:%M')}")
                    st.rerun()
                    break
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("💾 Save Schedule", type="primary", use_container_width=True):
            save_schedule_table(auto_fetcher, st.session_state.schedule_data)
            st.success("✅ Schedule saved!")
    
    with col2:
        if st.button("🔄 Reset to Default", use_container_width=True):
            st.session_state.schedule_data = [
                {"Day": "Monday", "Time": "09:00", "Active": True},
                {"Day": "Tuesday", "Time": "09:00", "Active": False},
                {"Day": "Wednesday", "Time": "13:00", "Active": True},
                {"Day": "Thursday", "Time": "09:00", "Active": False},
                {"Day": "Friday", "Time": "17:00", "Active": True},
                {"Day": "Saturday", "Time": "09:00", "Active": False},
                {"Day": "Sunday", "Time": "09:00", "Active": False}
            ]
            st.rerun()
    
    # Show schedule preview
    active_schedules = [s for s in st.session_state.schedule_data if s.get("Active", True)]
    if active_schedules:
        st.info(f"📊 **Active schedules:** {len(active_schedules)} checks per week")
        preview_items = []
        for s in active_schedules[:3]:
            time_str = s['Time']  # Already a string
            preview_items.append(f"{s['Day']} {time_str}")
        
        preview_text = ", ".join(preview_items)
        if len(active_schedules) > 3:
            preview_text += f" +{len(active_schedules)-3} more"
        st.caption(f"Next checks: {preview_text}")

def get_existing_schedules(auto_fetcher):
    """Convert existing configuration to table format"""
    try:
        scheduling_config = auto_fetcher.config.get('scheduling', {})
        if scheduling_config.get('type') == 'specific_times':
            times = scheduling_config.get('specific_times', ['09:00'])
            enabled_days = scheduling_config.get('enabled_days', [1, 3, 5])
            
            day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 
                        5: "Friday", 6: "Saturday", 7: "Sunday"}
            
            schedules = []
            for day_num in enabled_days:
                # Use first time for each enabled day
                schedules.append({
                    "Day": day_names.get(day_num, "Monday"),
                    "Time": times[0] if times else "09:00",
                    "Active": True
                })
            return schedules
    except:
        pass
    return None

def merge_existing_schedules(weekly_schedule, existing_schedules):
    """Merge existing schedules into the 7-day weekly structure"""
    if not existing_schedules:
        return
    
    # Create a map of existing schedules by day
    existing_by_day = {}
    for schedule in existing_schedules:
        day = schedule.get("Day")
        if day:
            existing_by_day[day] = schedule
    
    # Update the weekly schedule with existing data
    for i, day_schedule in enumerate(weekly_schedule):
        day = day_schedule["Day"]
        if day in existing_by_day:
            existing = existing_by_day[day]
            time_str = existing.get("Time", "09:00")
            # Keep as string for compatibility
            weekly_schedule[i]["Time"] = time_str
            weekly_schedule[i]["Active"] = existing.get("Active", True)

def apply_preset_schedule(preset_type, session_state):
    """Apply a preset schedule pattern"""
    
    presets = {
        "daily": {
            "active_days": ["Monday"],
            "time": "09:00",
            "description": "Once per day"
        },
        "twice_weekly": {
            "active_days": ["Monday", "Friday"],
            "time": "09:00",
            "description": "Twice per week"
        },
        "weekdays": {
            "active_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "time": "09:00",
            "description": "Weekdays only"
        },
        "business": {
            "active_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "time": "09:00",  # We'll show multiple times in future
            "description": "Business hours"
        }
    }
    
    if preset_type not in presets:
        return
        
    preset = presets[preset_type]
    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Create new schedule data
    new_schedule = []
    for day in all_days:
        is_active = day in preset["active_days"]
        new_schedule.append({
            "Day": day,
            "Time": preset["time"],
            "Active": is_active
        })
    
    session_state.schedule_data = new_schedule

def save_schedule_table(auto_fetcher, schedule_data):
    """Save table data back to configuration"""
    try:
        # Validate time format
        import re
        time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
        
        # Group by day
        day_mapping = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
                      "Friday": 5, "Saturday": 6, "Sunday": 7}
        
        # Get active schedules and validate
        active_schedules = []
        for s in schedule_data:
            if s.get("Active", True):
                # Time is already a string
                time_str = s.get("Time", "09:00")
                    
                # Validate time format
                if not re.match(time_pattern, time_str):
                    st.error(f"❌ Invalid time format: {time_str}. Use HH:MM format (e.g., 09:00, 13:30)")
                    return
                    
                active_schedules.append(s)
        
        if not active_schedules:
            st.warning("⚠️ No active schedules found")
            return
        
        # Extract enabled days and their times
        enabled_days = []
        day_times = {}
        
        for s in active_schedules:
            day_num = day_mapping[s["Day"]]
            time_str = s["Time"]
            enabled_days.append(day_num)
            day_times[day_num] = time_str
        
        # For now, use the first time as the main time (since each day has one time)
        # In future versions, we could support multiple times per day
        specific_times = list(set([s["Time"] for s in active_schedules]))
        
        # Update configuration
        new_config = {
            'type': 'specific_times',
            'specific_times': specific_times,
            'enabled_days': enabled_days,
            'timezone': 'Asia/Singapore',
            'auto_start': auto_fetcher.config.get('scheduling', {}).get('auto_start', True),
            'max_runs_per_day': 24,
            'retry_on_failure': True,
            'retry_max_attempts': 3,
            'retry_delay_minutes': 5
        }
        
        if 'scheduling' not in auto_fetcher.config:
            auto_fetcher.config['scheduling'] = {}
        
        auto_fetcher.config['scheduling'].update(new_config)
        auto_fetcher.save_config()
        
        # Update scheduler
        auto_fetcher.scheduler = auto_fetcher.scheduler.__class__(auto_fetcher.config['scheduling'])
        
    except Exception as e:
        st.error(f"❌ Error saving schedule: {str(e)}")

def render_control_panel(auto_fetcher: AutoProposalFetcher):
    """Render simple control panel"""
    
    st.markdown("#### 🎛️ Control Panel")
    
    # Get current status
    status = auto_fetcher.get_status()
    
    # Status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if status['enabled']:
            st.success("✅ Enabled")
        else:
            st.error("❌ Disabled")
    
    with col2:
        if status['running']:
            st.success("🟢 Running")
        else:
            st.warning("🟡 Stopped")
    
    with col3:
        # Show simple schedule info
        scheduling_config = auto_fetcher.config.get('scheduling', {})
        if scheduling_config.get('type') == 'specific_times':
            times = scheduling_config.get('specific_times', [])
            st.info(f"📅 {len(times)} times/day")
        else:
            st.info("📅 Schedule set")
    
    with col4:
        if status.get('last_check'):
            last_check = status['last_check']
            new_count = last_check.get('new_proposals_count', 0)
            st.metric("New Proposals", new_count)
        else:
            st.info("🔍 No checks yet")
    
    # Control buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Start", type="primary", use_container_width=True):
            try:
                auto_fetcher.run_in_background()
                st.success("✅ Started!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.button("🛑 Stop", use_container_width=True):
            try:
                auto_fetcher.stop_scheduler()
                st.success("✅ Stopped!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col3:
        if st.button("🔄 Check Now", use_container_width=True):
            try:
                with st.spinner("Checking..."):
                    new_proposals = auto_fetcher.fetch_new_proposals()
                    
                    if new_proposals:
                        total_new = sum(len(proposals) for proposals in new_proposals.values())
                        st.success(f"🎉 Found {total_new} new proposals!")
                    else:
                        st.info("✅ No new proposals")
                        
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Show next scheduled runs (simplified)
    scheduler_status = status.get('scheduler', {})
    if scheduler_status.get('next_run_times'):
        with st.expander("📋 Next 3 Scheduled Runs"):
            for i, run_time in enumerate(scheduler_status['next_run_times'][:3], 1):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(run_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%a %b %d, %I:%M %p')
                    st.text(f"{i}. {formatted_time}")
                except:
                    st.text(f"{i}. {run_time}")