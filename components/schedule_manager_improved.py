"""
Improved Schedule Manager with step-by-step flow:
1. Pick frequency → 2. Select time → 3. Select day (based on frequency)
"""
import streamlit as st
from datetime import datetime, time
from services.schedules_store import (
    load_schedules, save_schedules, new_schedule_id,
    update_schedule, delete_schedule
)

def parse_schedule_details(sched):
    """Parse schedule details to extract human-readable info"""
    details = {
        "times": [],
        "days": []
    }
    
    mode = sched.get("mode", "")
    
    if mode == "specific_times":
        details["times"] = sched.get("times", [])
        # For specific times, days depend on weekdays_only setting
        
    elif mode == "interval":
        # Interval mode - no specific times or days
        pass
        
    elif mode == "cron":
        # Parse cron expression to extract days
        cron = sched.get("cron", "")
        if cron:
            try:
                # Cron format: minute hour day month weekday
                parts = cron.split()
                if len(parts) >= 5:
                    weekday_part = parts[4]  # Last part is weekdays
                    
                    # Map weekday numbers to names
                    weekday_map = {
                        "0": "Sunday", "1": "Monday", "2": "Tuesday", 
                        "3": "Wednesday", "4": "Thursday", "5": "Friday", "6": "Saturday"
                    }
                    
                    if "," in weekday_part:
                        # Multiple specific days
                        weekday_nums = weekday_part.split(",")
                        details["days"] = [weekday_map.get(num.strip(), num.strip()) for num in weekday_nums]
                    elif weekday_part != "*":
                        # Single specific day
                        details["days"] = [weekday_map.get(weekday_part, weekday_part)]
                    
                    # Extract time from cron
                    if len(parts) >= 2:
                        hour = parts[1]
                        minute = parts[0]
                        if hour != "*" and minute != "*":
                            details["times"] = [f"{hour.zfill(2)}:{minute.zfill(2)}"]
            except:
                pass
    
    return details

def render_improved_schedule_manager():
    """Ultra-compact schedule manager with professional layout"""
    
    # Ultra-compact CSS with full space optimization
    st.markdown("""
    <style>
    /* KILL WASTED SPACE - Container & Layout */
    .block-container {
        padding: 0.5rem 0.25rem !important;
        max-width: 100% !important;
    }
    .main > div.block-container {
        padding: 0.25rem !important;
        max-width: 100% !important;
    }
    section[data-testid="stSidebar"] + div {
        padding-left: 0 !important;
        margin-left: 0 !important;
    }
    div[data-testid="stAppViewContainer"] > div.main {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* ONE-LINE TITLES */
    h1, h2, h3 {
        white-space: nowrap !important;
        margin: 0.25rem 0 !important;
        font-size: 1.2rem !important;
        line-height: 1.2 !important;
    }
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    
    /* COMPACT FORMS - Two column grid */
    .form-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
        margin: 0.25rem 0;
    }
    .form-row {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    /* COMPACT CONTROLS */
    .stButton > button {
        height: 1.2rem !important;
        min-height: 1.2rem !important;
        font-size: 0.65rem !important;
        padding: 0.1rem 0.25rem !important;
        margin: 0 !important;
        line-height: 1 !important;
        border-radius: 0.2rem !important;
    }
    .stSelectbox > div > div {
        min-height: 1.5rem !important;
        font-size: 0.8rem !important;
    }
    .stTextInput > div > div > input {
        min-height: 1.5rem !important;
        font-size: 0.8rem !important;
        padding: 0.2rem 0.4rem !important;
    }
    .stMultiSelect > div > div {
        min-height: 1.5rem !important;
        font-size: 0.8rem !important;
    }
    
    /* FULL-WIDTH TABLES */
    .schedule-table {
        width: 100% !important;
        margin: 0 !important;
    }
    .table-header {
        position: sticky;
        top: 0;
        background: white;
        z-index: 10;
        border-bottom: 1px solid #e0e0e0;
    }
    
    /* ULTRA-COMPACT SPACING */
    .element-container {
        margin: 0.1rem 0 !important;
    }
    div[data-testid="column"] {
        padding: 0.05rem !important;
        margin: 0 !important;
    }
    .stMarkdown p {
        margin: 0.05rem 0 !important;
        font-size: 0.8rem !important;
        line-height: 1.1 !important;
    }
    
    /* HORIZONTAL QUICK ACTIONS */
    .action-toolbar {
        display: flex;
        gap: 0.25rem;
        align-items: center;
        margin: 0.25rem 0;
    }
    .action-toolbar .stButton {
        flex: none;
    }
    
    /* CHIP STYLES */
    .status-chip {
        display: inline-block;
        padding: 0.1rem 0.3rem;
        border-radius: 0.8rem;
        font-size: 0.65rem;
        font-weight: 500;
        white-space: nowrap;
    }
    .chip-active {
        background: #dcfce7;
        color: #166534;
    }
    .chip-disabled {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* CONSISTENT SPACING */
    .stExpander {
        margin: 0.25rem 0 !important;
    }
    .stExpander > div > div {
        padding: 0.5rem !important;
    }
    hr {
        margin: 0.2rem 0 !important;
        border: 0.5px solid #f0f0f0 !important;
    }
    
    /* REMOVE ALL EXCESS PADDING */
    .stContainer, .css-1d391kg, .css-1aumxhk {
        padding: 0 !important;
        margin: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with icon, title, and actions in 3 columns
    col1, col2, col3 = st.columns([0.5, 2, 1])
    with col1:
        st.markdown("# 📅")
    with col2:
        st.markdown("# Schedule Manager")
    with col3:
        # Quick action toolbar
        st.markdown('<div class="action-toolbar">', unsafe_allow_html=True)
        if st.button("🔄", help="Refresh", key="refresh_btn"):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Load schedules
    schedules = load_schedules()
    
    # Show existing schedules in table format
    if schedules:
        st.markdown("## 📊 Your Current Schedules")
        
        # Prepare data for table
        table_data = []
        for sched in schedules:
            frequency_info = parse_schedule_details(sched)
            
            # Status
            status = "🟢 Active" if sched.get("enabled", True) else "🔴 Disabled"
            
            # Frequency
            frequency_preset = sched.get("frequency_preset", "Custom")
            
            # Times - format nicely
            if frequency_info["times"]:
                time_display = []
                for time_str in frequency_info["times"]:
                    try:
                        time_obj = datetime.strptime(time_str, "%H:%M").time()
                        display_time = time_obj.strftime("%I:%M %p")
                        time_display.append(display_time)
                    except:
                        time_display.append(time_str)
                times_text = ", ".join(time_display)
            else:
                times_text = "Continuous"
            
            # Days
            if frequency_info["days"]:
                days_text = ", ".join(frequency_info["days"])
            elif "Every" in frequency_preset:
                days_text = "All days"
            else:
                weekdays_only = sched.get("weekdays_only", False)
                days_text = "Weekdays" if weekdays_only else "All days"
            
            # Chains
            chains = sched.get("chains", [])
            chain_names = {
                "ethereum": "Ethereum",
                "tron": "Tron", 
                "bitcoin": "Bitcoin",
                "binance_smart_chain": "BSC"
            }
            chain_display = [chain_names.get(chain, chain) for chain in chains]
            chains_text = ", ".join(chain_display)
            
            # Created date
            created = sched.get("created_at", "")
            if created:
                try:
                    created_date = datetime.fromisoformat(created).strftime("%m/%d/%Y")
                except:
                    created_date = "Unknown"
            else:
                created_date = "Unknown"
            
            table_data.append({
                "Name": sched["name"],
                "Status": status,
                "Frequency": frequency_preset, 
                "Time(s)": times_text,
                "Days": days_text,
                "Chains": chains_text,
                "Created": created_date,
                "ID": sched["id"][:8]  # Short ID for actions
            })
        
        # Compact table with sticky header and shorter names
        st.markdown('<div class="schedule-table">', unsafe_allow_html=True)
        
        # Table header with shorter column names
        st.markdown('<div class="table-header">', unsafe_allow_html=True)
        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([2.5, 1, 1.5, 1.2, 1.2, 1, 0.6, 0.6, 0.6])
        with col1:
            st.markdown("**Name**")
        with col2:
            st.markdown("**Status**")
        with col3:
            st.markdown("**Frequency**")
        with col4:
            st.markdown("**Time**")
        with col5:
            st.markdown("**Days**")
        with col6:
            st.markdown("**Chains**")
        with col7:
            st.markdown("**✏️**")
        with col8:
            st.markdown("**🔄**")
        with col9:
            st.markdown("**🗑️**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Compact table rows
        for i, sched in enumerate(schedules):
            frequency_info = parse_schedule_details(sched)
            
            # Create columns matching header layout
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([2.5, 1, 1.5, 1.2, 1.2, 1, 0.6, 0.6, 0.6])
            
            with col1:
                st.markdown(f"**{sched['name'][:25]}**" + ("..." if len(sched['name']) > 25 else ""))
            
            with col2:
                # Chip-style status
                enabled = sched.get("enabled", True)
                chip_class = "chip-active" if enabled else "chip-disabled"
                status_text = "Active" if enabled else "Disabled"
                st.markdown(f'<span class="status-chip {chip_class}">{status_text}</span>', unsafe_allow_html=True)
            
            with col3:
                frequency = sched.get("frequency_preset", "Custom")
                short_freq = frequency.replace("per ", "").replace("Every ", "").replace(" minutes", "m").replace(" hours", "h")
                st.markdown(f"`{short_freq}`")
            
            with col4:
                # Compact time display
                if frequency_info["times"]:
                    time_str = frequency_info["times"][0]  # Show first time only
                    try:
                        time_obj = datetime.strptime(time_str, "%H:%M").time()
                        display_time = time_obj.strftime("%H:%M")
                        if len(frequency_info["times"]) > 1:
                            display_time += f" +{len(frequency_info['times'])-1}"
                    except:
                        display_time = time_str
                    st.markdown(f"`{display_time}`")
                else:
                    st.markdown("`24/7`")
            
            with col5:
                # Compact days display
                if frequency_info["days"]:
                    if len(frequency_info["days"]) <= 2:
                        days_text = ", ".join([d[:3] for d in frequency_info["days"]])
                    else:
                        days_text = f"{len(frequency_info['days'])} days"
                elif "Every" in frequency:
                    days_text = "Daily"
                else:
                    weekdays_only = sched.get("weekdays_only", False)
                    days_text = "M-F" if weekdays_only else "Daily"
                st.markdown(f"`{days_text}`")
            
            with col6:
                # Compact chain display
                chains = sched.get("chains", [])
                chain_map = {"ethereum": "ETH", "tron": "TRX", "bitcoin": "BTC", "binance_smart_chain": "BSC"}
                if len(chains) <= 2:
                    chain_text = ", ".join([chain_map.get(c, c[:3].upper()) for c in chains])
                else:
                    chain_text = f"{len(chains)} chains"
                st.markdown(f"`{chain_text}`")
            
            with col7:
                # Edit button
                if st.button("✏️", key=f"edit_{sched['id'][:8]}", help=f"Edit {sched['name']}", use_container_width=True):
                    st.session_state[f"editing_{sched['id'][:8]}"] = True
                    st.rerun()
            
            with col8:
                # Toggle button - smaller with icons
                current_enabled = sched.get("enabled", True)
                if current_enabled:
                    button_icon = "⏸️"
                    button_help = f"Disable {sched['name']}"
                else:
                    button_icon = "▶️"
                    button_help = f"Enable {sched['name']}"
                
                if st.button(button_icon, key=f"toggle_{sched['id'][:8]}", help=button_help, use_container_width=True):
                    sched["enabled"] = not current_enabled
                    save_schedules(schedules)
                    st.rerun()
            
            with col9:
                # Delete button - smaller with icon
                if st.button("🗑️", key=f"del_{sched['id'][:8]}", help=f"Delete {sched['name']}", use_container_width=True):
                    delete_schedule(sched["id"])
                    st.success(f"Deleted: {sched['name']}")
                    st.rerun()
            
            # Add very thin separator line for all rows except last
            if i < len(schedules) - 1:
                st.markdown("<hr style='margin: 0.1rem 0; border: 0.3px solid #f0f0f0; opacity: 0.7;'>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close schedule-table div
    
    # Check if any schedule is being edited
    editing_schedule = None
    for sched in schedules:
        if st.session_state.get(f"editing_{sched['id'][:8]}", False):
            editing_schedule = sched
            break
    
    if editing_schedule:
        st.markdown("## ✏️ Edit Schedule")
        st.markdown(f"**Editing: {editing_schedule['name']}**")
        
        # Parse current schedule details for editing
        current_frequency = editing_schedule.get("frequency_preset", "Custom")
        current_mode = editing_schedule.get("mode", "interval")
        current_times = editing_schedule.get("times", [])
        current_cron = editing_schedule.get("cron", "")
        
        # Edit form
        col1, col2 = st.columns([2, 1])
        with col1:
            edit_name = st.text_input("📝 Schedule Name", value=editing_schedule.get("name", ""), key="edit_name")
        with col2:
            edit_chains = st.multiselect(
                "🔗 Blockchains",
                ["ethereum", "tron", "bitcoin", "binance_smart_chain"],
                default=editing_schedule.get("chains", []),
                format_func=lambda x: {
                    "ethereum": "Ethereum",
                    "tron": "Tron", 
                    "bitcoin": "Bitcoin",
                    "binance_smart_chain": "BSC"
                }.get(x, x),
                key="edit_chains"
            )
        
        # Frequency selection
        st.markdown("### Step 1: 📊 Pick Frequency")
        frequency_options = [
            "Once per day",
            "Twice per day", 
            "3 times per day",
            "Once per week",
            "Twice per week",
            "3 times per week",
            "Every hour",
            "Every 2 hours",
            "Every 30 minutes"
        ]
        
        edit_frequency = st.selectbox(
            "How often should it check?",
            frequency_options,
            index=frequency_options.index(current_frequency) if current_frequency in frequency_options else 0,
            key="edit_frequency"
        )
        
        # Time selection based on frequency
        st.markdown("### Step 2: 🕐 Select Time(s)")
        edit_times_list = []
        edit_selected_days = []
        edit_interval_mins = editing_schedule.get("interval_minutes", 60)
        edit_mode = current_mode
        edit_cron_expr = current_cron
        edit_check_time = time(9, 0)  # Default time
        
        if edit_frequency == "Once per day":
            default_time = time(9, 0)
            if current_times:
                try:
                    h, m = map(int, current_times[0].split(":"))
                    default_time = time(h, m)
                except:
                    pass
            edit_time1 = st.time_input("Pick time for daily check:", value=default_time, key="edit_time1")
            edit_times_list = [edit_time1.strftime("%H:%M")]
            edit_mode = "specific_times"
            st.success(f"✅ Will check daily at {edit_time1.strftime('%I:%M %p')}")
            
        elif edit_frequency == "Twice per day":
            default_time1, default_time2 = time(9, 0), time(17, 0)
            if len(current_times) >= 2:
                try:
                    h1, m1 = map(int, current_times[0].split(":"))
                    h2, m2 = map(int, current_times[1].split(":"))
                    default_time1, default_time2 = time(h1, m1), time(h2, m2)
                except:
                    pass
            col1, col2 = st.columns(2)
            with col1:
                edit_time1 = st.time_input("First check:", value=default_time1, key="edit_time1")
            with col2:
                edit_time2 = st.time_input("Second check:", value=default_time2, key="edit_time2")
            edit_times_list = [edit_time1.strftime("%H:%M"), edit_time2.strftime("%H:%M")]
            edit_mode = "specific_times"
            st.success(f"✅ Will check at {edit_time1.strftime('%I:%M %p')} and {edit_time2.strftime('%I:%M %p')}")
            
        elif edit_frequency == "3 times per day":
            default_time1, default_time2, default_time3 = time(9, 0), time(13, 0), time(17, 0)
            if len(current_times) >= 3:
                try:
                    h1, m1 = map(int, current_times[0].split(":"))
                    h2, m2 = map(int, current_times[1].split(":"))
                    h3, m3 = map(int, current_times[2].split(":"))
                    default_time1, default_time2, default_time3 = time(h1, m1), time(h2, m2), time(h3, m3)
                except:
                    pass
            col1, col2, col3 = st.columns(3)
            with col1:
                edit_time1 = st.time_input("Morning:", value=default_time1, key="edit_time1")
            with col2:
                edit_time2 = st.time_input("Afternoon:", value=default_time2, key="edit_time2")
            with col3:
                edit_time3 = st.time_input("Evening:", value=default_time3, key="edit_time3")
            edit_times_list = [edit_time1.strftime("%H:%M"), edit_time2.strftime("%H:%M"), edit_time3.strftime("%H:%M")]
            edit_mode = "specific_times"
            st.success(f"✅ Will check at {edit_time1.strftime('%I:%M %p')}, {edit_time2.strftime('%I:%M %p')}, {edit_time3.strftime('%I:%M %p')}")
            
        elif "per week" in edit_frequency:
            default_time = time(9, 0)
            if current_times:
                try:
                    h, m = map(int, current_times[0].split(":"))
                    default_time = time(h, m)
                except:
                    pass
            edit_check_time = st.time_input("What time for weekly checks?", value=default_time, key="edit_check_time")
            edit_times_list = [edit_check_time.strftime("%H:%M")]
            st.info(f"⏰ Selected time: {edit_check_time.strftime('%I:%M %p')} - now pick days below")
            
            # Extract current days from cron if available
            current_days = []
            if current_cron:
                try:
                    parts = current_cron.split()
                    if len(parts) >= 5:
                        weekday_part = parts[4]
                        weekday_map = {"0": "Sunday", "1": "Monday", "2": "Tuesday", "3": "Wednesday", "4": "Thursday", "5": "Friday", "6": "Saturday"}
                        if "," in weekday_part:
                            weekday_nums = weekday_part.split(",")
                            current_days = [weekday_map.get(num.strip(), num.strip()) for num in weekday_nums]
                        elif weekday_part != "*":
                            current_days = [weekday_map.get(weekday_part, weekday_part)]
                except:
                    pass
            
            st.markdown("**📅 Days**")
            day_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            if edit_frequency == "Once per week":
                edit_selected_day = st.selectbox("Pick one day:", day_options, 
                                                index=day_options.index(current_days[0]) if current_days else 0, key="edit_day")
                edit_selected_days = [edit_selected_day]
                st.success(f"✅ Will check every {edit_selected_day} at {edit_check_time.strftime('%I:%M %p')}")
            elif edit_frequency == "Twice per week":
                edit_selected_days = st.multiselect("Pick two days:", day_options, default=current_days[:2], max_selections=2, key="edit_days")
                if len(edit_selected_days) == 2:
                    st.success(f"✅ Will check every {' and '.join(edit_selected_days)} at {edit_check_time.strftime('%I:%M %p')}")
                elif len(edit_selected_days) < 2:
                    st.warning("Please select exactly 2 days")
            elif edit_frequency == "3 times per week":
                edit_selected_days = st.multiselect("Pick three days:", day_options, default=current_days[:3], max_selections=3, key="edit_days")
                if len(edit_selected_days) == 3:
                    st.success(f"✅ Will check every {', '.join(edit_selected_days)} at {edit_check_time.strftime('%I:%M %p')}")
                elif len(edit_selected_days) < 3:
                    st.warning("Please select exactly 3 days")
            
        elif "Every" in edit_frequency:
            if "2 hours" in edit_frequency:
                edit_interval_mins = 120
            elif "hour" in edit_frequency:
                edit_interval_mins = 60
            elif "30 minutes" in edit_frequency:
                edit_interval_mins = 30
            else:
                edit_interval_mins = 60
            edit_mode = "interval"
            edit_cron_expr = ""
            st.success(f"✅ Will check every {edit_interval_mins} minutes continuously")
        
        # Additional settings
        st.markdown("### ⚙️ Additional Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            edit_weekdays_only = st.checkbox("📅 Weekdays only (Mon-Fri)", 
                                           value=editing_schedule.get("weekdays_only", True), key="edit_weekdays")
        with col2:
            edit_timezone = st.selectbox(
                "🌍 Timezone:",
                ["Asia/Singapore", "UTC", "US/Eastern", "US/Pacific"],
                index=["Asia/Singapore", "UTC", "US/Eastern", "US/Pacific"].index(editing_schedule.get("timezone", "Asia/Singapore")),
                format_func=lambda x: {
                    "Asia/Singapore": "Singapore (SGT)",
                    "UTC": "UTC",
                    "US/Eastern": "US Eastern",
                    "US/Pacific": "US Pacific"
                }.get(x, x),
                key="edit_timezone"
            )
        
        # Save and Cancel buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Changes", type="primary", use_container_width=True, key="save_edit"):
                # Build updated schedule object based on frequency type
                if "per week" in edit_frequency and edit_selected_days:
                    weekday_map = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, 
                                  "Friday": 5, "Saturday": 6, "Sunday": 0}
                    weekday_nums = [str(weekday_map[day]) for day in edit_selected_days]
                    edit_mode = "cron"
                    edit_cron_expr = f"{edit_check_time.minute} {edit_check_time.hour} * * {','.join(weekday_nums)}"
                elif "Every" in edit_frequency:
                    edit_mode = "interval"
                    edit_cron_expr = ""
                else:
                    edit_mode = "specific_times"
                    edit_cron_expr = ""
                
                # Update the schedule
                updated_schedule = editing_schedule.copy()
                updated_schedule.update({
                    "name": edit_name,
                    "chains": edit_chains,
                    "mode": edit_mode,
                    "interval_minutes": edit_interval_mins if "Every" in edit_frequency else editing_schedule.get("interval_minutes", 60),
                    "times": edit_times_list,
                    "cron": edit_cron_expr,
                    "weekdays_only": edit_weekdays_only,
                    "timezone": edit_timezone,
                    "frequency_preset": edit_frequency
                })
                
                # Save to schedules
                update_schedule(editing_schedule["id"], updated_schedule)
                
                # Clear editing state
                del st.session_state[f"editing_{editing_schedule['id'][:8]}"]
                
                st.success(f"✅ Updated schedule: {edit_name}")
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True, key="cancel_edit"):
                del st.session_state[f"editing_{editing_schedule['id'][:8]}"]
                st.rerun()
        
        st.markdown("---")
        return  # Don't show the create form when editing
    
    # Create New Schedule button (collapsed by default)
    st.markdown("---")
    
    # Check if create form should be shown
    show_create_form = st.session_state.get("show_create_form", False)
    
    if not show_create_form:
        # Show only the button to reveal the form
        if st.button("➕ Create New Schedule", type="primary", use_container_width=True, key="show_create_btn"):
            st.session_state["show_create_form"] = True
            st.rerun()
        return  # Don't show the form yet
    
    # Compact form header with inline hide button
    st.markdown('<div class="form-row">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("## ➕ Create Schedule")
    with col2:
        if st.button("🔼", key="hide_create_btn", help="Hide form"):
            st.session_state["show_create_form"] = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Compact two-column form grid
    st.markdown('<div class="form-grid">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", placeholder="e.g., Daily ETH Check")
    with col2:
        chains = st.multiselect(
            "Blockchains",
            ["ethereum", "tron", "bitcoin", "binance_smart_chain"],
            default=["ethereum"],
            format_func=lambda x: {"ethereum": "ETH", "tron": "TRX", "bitcoin": "BTC", "binance_smart_chain": "BSC"}.get(x, x)
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("**📊 Frequency**")
    
    frequency_options = [
        "Once per day",
        "Twice per day", 
        "3 times per day",
        "Once per week",
        "Twice per week",
        "3 times per week",
        "Every hour",
        "Every 2 hours",
        "Every 30 minutes"
    ]
    
    frequency = st.selectbox(
        "How often should it check?",
        frequency_options,
        help="Choose how frequently you want to check for new proposals"
    )
    
    # Compact time selection
    st.markdown("**🕐 Time(s)**")
    
    times_list = []
    
    if frequency == "Once per day":
        time1 = st.time_input("Pick time for daily check:", value=time(9, 0))
        times_list = [time1.strftime("%H:%M")]
        st.success(f"✅ Will check daily at {time1.strftime('%I:%M %p')}")
        
    elif frequency == "Twice per day":
        col1, col2 = st.columns(2)
        with col1:
            time1 = st.time_input("First check:", value=time(9, 0))
        with col2:
            time2 = st.time_input("Second check:", value=time(17, 0))
        times_list = [time1.strftime("%H:%M"), time2.strftime("%H:%M")]
        st.success(f"✅ Will check at {time1.strftime('%I:%M %p')} and {time2.strftime('%I:%M %p')}")
        
    elif frequency == "3 times per day":
        col1, col2, col3 = st.columns(3)
        with col1:
            time1 = st.time_input("Morning:", value=time(9, 0))
        with col2:
            time2 = st.time_input("Afternoon:", value=time(13, 0))
        with col3:
            time3 = st.time_input("Evening:", value=time(17, 0))
        times_list = [time1.strftime("%H:%M"), time2.strftime("%H:%M"), time3.strftime("%H:%M")]
        st.success(f"✅ Will check at {time1.strftime('%I:%M %p')}, {time2.strftime('%I:%M %p')}, {time3.strftime('%I:%M %p')}")
        
    elif "per week" in frequency:
        check_time = st.time_input("What time for weekly checks?", value=time(9, 0))
        times_list = [check_time.strftime("%H:%M")]
        st.info(f"⏰ Selected time: {check_time.strftime('%I:%M %p')} - now pick days below")
        
    elif "Every" in frequency:
        # Handle interval-based frequencies
        if "hour" in frequency:
            if "2 hours" in frequency:
                interval_mins = 120
            else:
                interval_mins = 60
        elif "30 minutes" in frequency:
            interval_mins = 30
        else:
            interval_mins = 60
        
        st.success(f"✅ Will check every {interval_mins} minutes continuously")
        mode = "interval"
    
    # Step 3: Day selection (only for weekly frequencies)
    if "per week" in frequency:
        st.markdown("### Step 3: 📅 Select Days")
        
        day_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        if frequency == "Once per week":
            selected_day = st.selectbox("Pick one day:", day_options)
            selected_days = [selected_day]
            st.success(f"✅ Will check every {selected_day} at {check_time.strftime('%I:%M %p')}")
            
        elif frequency == "Twice per week":
            selected_days = st.multiselect("Pick two days:", day_options, max_selections=2)
            if len(selected_days) == 2:
                st.success(f"✅ Will check every {' and '.join(selected_days)} at {check_time.strftime('%I:%M %p')}")
            elif len(selected_days) < 2:
                st.warning("Please select exactly 2 days")
            
        elif frequency == "3 times per week":
            selected_days = st.multiselect("Pick three days:", day_options, max_selections=3)
            if len(selected_days) == 3:
                st.success(f"✅ Will check every {', '.join(selected_days)} at {check_time.strftime('%I:%M %p')}")
            elif len(selected_days) < 3:
                st.warning("Please select exactly 3 days")
        
        # Convert to cron expression for weekly schedules
        if len(selected_days) == int(frequency.split()[0].replace("Once", "1").replace("Twice", "2")):
            weekday_map = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, 
                          "Friday": 5, "Saturday": 6, "Sunday": 0}
            weekday_nums = [str(weekday_map[day]) for day in selected_days]
            mode = "cron"
            cron_expr = f"{check_time.minute} {check_time.hour} * * {','.join(weekday_nums)}"
        else:
            mode = "specific_times"  # fallback
            cron_expr = ""
    else:
        # Daily frequencies or intervals
        if "Every" in frequency:
            mode = "interval"
            cron_expr = ""
        else:
            mode = "specific_times"
            cron_expr = ""
    
    # Compact settings and inline save
    st.markdown("**⚙️ Settings & Save**")
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    
    with col1:
        weekdays_only = st.checkbox("Weekdays only", value=True)
        
    with col2:
        timezone = st.selectbox(
            "Timezone",
            ["Asia/Singapore", "UTC", "US/Eastern", "US/Pacific"],
            format_func=lambda x: {"Asia/Singapore": "SGT", "UTC": "UTC", "US/Eastern": "EST", "US/Pacific": "PST"}.get(x, x)
        )
    
    with col3:
        can_create = bool(name and chains)
        if "per week" in frequency:
            required_days = int(frequency.split()[0].replace("Once", "1").replace("Twice", "2"))
            can_create = can_create and len(selected_days) == required_days
        
        if st.button("🚀 Create", type="primary", disabled=not can_create, use_container_width=True):
            
            # Build schedule object
            schedule_data = {
                "id": new_schedule_id(),
                "name": name,
                "chains": chains,
                "mode": mode,
                "interval_minutes": interval_mins if mode == "interval" else 60,
                "times": times_list,
                "cron": cron_expr,
                "end_time": None,
                "weekdays_only": weekdays_only,
                "enabled": True,
                "timezone": timezone,
                "created_at": datetime.now().isoformat(),
                "last_run": None,
                "frequency_preset": frequency  # Store the original frequency selection
            }
            
            # Save schedule
            current_schedules = load_schedules()
            current_schedules.append(schedule_data)
            save_schedules(current_schedules)
            
            st.success(f"✅ Created schedule: {name}")
            st.balloons()
            
            # Hide the create form after successful creation
            st.session_state["show_create_form"] = False
            st.rerun()
    
    if not can_create:
        if not name:
            st.warning("⚠️ Please enter a schedule name")
        elif not chains:
            st.warning("⚠️ Please select at least one blockchain")
        elif "per week" in frequency and len(selected_days) != int(frequency.split()[0].replace("Once", "1").replace("Twice", "2")):
            st.warning(f"⚠️ Please select the correct number of days for '{frequency}'")

if __name__ == "__main__":
    # Standalone test
    st.set_page_config(page_title="Improved Schedule Manager", layout="wide")
    render_improved_schedule_manager()