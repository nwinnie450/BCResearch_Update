"""
Simple Schedule Manager Component
Step-by-step flow: Frequency → Day → Time → Save
Same styling as other pages but simple functionality
"""
import streamlit as st
import json
import os
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional

# Simple storage functions
def load_simple_schedules():
    """Load schedules from simple JSON file"""
    schedules_file = "data/simple_schedules.json"
    if os.path.exists(schedules_file):
        try:
            with open(schedules_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_simple_schedules(schedules):
    """Save schedules to simple JSON file"""
    os.makedirs("data", exist_ok=True)
    schedules_file = "data/simple_schedules.json"
    try:
        with open(schedules_file, 'w') as f:
            json.dump(schedules, f, indent=2)
        return True
    except:
        return False

def calculate_next_run_time(schedule):
    """Calculate the next run time for a given schedule"""
    try:
        frequency = schedule.get('frequency', '')
        days = schedule.get('days', [])
        time_24h = schedule.get('time_24h', '09:00')
        
        # Parse the time
        hour, minute = map(int, time_24h.split(':'))
        
        # Get current time
        now = datetime.now()
        today = now.date()
        
        # Calculate next run date based on frequency
        if "Daily" in frequency:
            # Daily - next run is today if time hasn't passed, otherwise tomorrow
            run_time = datetime.combine(today, time(hour, minute))
            if run_time <= now:
                run_time = datetime.combine(today + timedelta(days=1), time(hour, minute))
            return run_time
            
        elif "Weekdays" in frequency:
            # Weekdays - next weekday
            for i in range(8):  # Check next 7 days
                check_date = today + timedelta(days=i)
                if check_date.weekday() < 5:  # Monday=0 to Friday=4
                    run_time = datetime.combine(check_date, time(hour, minute))
                    if run_time > now:
                        return run_time
            return None
            
        elif "Weekly" in frequency or "Bi-weekly" in frequency:
            # Weekly or bi-weekly - find next occurrence of the specified day
            if not days:
                return None
                
            target_day = days[0]
            day_mapping = {
                'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                'Friday': 4, 'Saturday': 5, 'Sunday': 6
            }
            
            if target_day not in day_mapping:
                return None
                
            target_weekday = day_mapping[target_day]
            
            # Find next occurrence
            for i in range(8):  # Check next 7 days
                check_date = today + timedelta(days=i)
                if check_date.weekday() == target_weekday:
                    run_time = datetime.combine(check_date, time(hour, minute))
                    if run_time > now:
                        return run_time
            return None
            
        elif "Custom" in frequency:
            # Custom days - find next occurrence of any specified day
            if not days:
                return None
                
            day_mapping = {
                'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                'Friday': 4, 'Saturday': 5, 'Sunday': 6
            }
            
            target_weekdays = [day_mapping[day] for day in days if day in day_mapping]
            if not target_weekdays:
                return None
            
            # Find next occurrence of any target day
            for i in range(8):  # Check next 7 days
                check_date = today + timedelta(days=i)
                if check_date.weekday() in target_weekdays:
                    run_time = datetime.combine(check_date, time(hour, minute))
                    if run_time > now:
                        return run_time
            return None
            
        return None
        
    except Exception as e:
        print(f"Error calculating next run time: {e}")
        return None

def render_upcoming_schedules(schedules):
    """Render upcoming schedule notifications"""
    
    # Filter active schedules and calculate next run times
    upcoming_schedules = []
    
    for schedule in schedules:
        if not schedule.get('enabled', True):
            continue
            
        next_run = calculate_next_run_time(schedule)
        if next_run:
            upcoming_schedules.append({
                'schedule': schedule,
                'next_run': next_run,
                'name': schedule.get('name', 'Unnamed Schedule')
            })
    
    # Sort by next run time (soonest first)
    upcoming_schedules.sort(key=lambda x: x['next_run'])
    
    if upcoming_schedules:
        # Show only the next upcoming schedule
        next_item = upcoming_schedules[0]
        schedule = next_item['schedule']
        next_run = next_item['next_run']
        name = next_item['name']
        
        # Calculate time until next run
        time_until = next_run - datetime.now()
        
        if time_until.total_seconds() < 3600:  # Less than 1 hour
            time_str = f"in {int(time_until.total_seconds() / 60)} minutes"
            urgency_color = "🔴"
        elif time_until.total_seconds() < 86400:  # Less than 1 day
            time_str = f"in {int(time_until.total_seconds() / 3600)} hours"
            urgency_color = "🟡"
        else:
            days = time_until.days
            if days == 1:
                time_str = "tomorrow"
            else:
                time_str = f"in {days} days"
            urgency_color = "🟢"
        
        # Format the notification
        next_run_formatted = next_run.strftime('%A, %B %d at %I:%M %p')
        
        # Show the next schedule notification
        st.success(f"{urgency_color} **Next Schedule:** '{name}' will run **{time_str}** ({next_run_formatted})")
            
    else:
        st.warning("⚠️ No active schedules found. Enable some schedules to see the next run!")

def render_simple_schedule_manager():
    """Render the simple schedule manager with step-by-step flow"""
    
    # Header - match other pages exactly
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📅 Schedule Manager")
        st.markdown("Simple step-by-step schedule creation")
    
    with col2:
        if st.button("🔄 Refresh", help="Refresh schedules"):
            st.rerun()
    
    # Load existing schedules
    schedules = load_simple_schedules()
    
    # Show upcoming schedule notifications
    st.markdown("---")
    render_upcoming_schedules(schedules)
    
    # Show existing schedules table
    st.markdown("---")
    render_schedules_table(schedules)
    
    # Control panel for scheduler
    st.markdown("---")
    render_scheduler_controls()
    
    # Email configuration section
    st.markdown("---")
    render_email_configuration()
    
    # Create schedule section
    st.markdown("---")
    render_create_schedule_form()

def render_schedules_table(schedules):
    """Render existing schedules in a table"""
    
    st.markdown("#### 📊 Your Schedules")
    
    if not schedules:
        st.info("No schedules created yet. Click 'Create Schedule' to add one.")
        return
    
    # Sort schedules by created_at descending (newest first)
    schedules_sorted = sorted(schedules, key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Combined table with checkboxes and management
    st.markdown("**📊 Your Schedules**")
    st.markdown("Select schedules using checkboxes to manage them:")
    
    # Create checkboxes for each schedule
    selected_schedules = []
    
    # Use columns for integrated table layout
    table_cols = st.columns([0.4, 0.4, 2.5, 1, 1.2, 1, 1, 0.8])
    
    with table_cols[0]:
        # Select All checkbox
        select_all = st.checkbox("**All**", help="Select/deselect all schedules")
        
    with table_cols[1]:
        st.markdown("**#**")
    with table_cols[2]:
        st.markdown("**Schedule Name**") 
    with table_cols[3]:
        st.markdown("**Status**")
    with table_cols[4]:
        st.markdown("**Frequency**")
    with table_cols[5]:
        st.markdown("**Days**")
    with table_cols[6]:
        st.markdown("**Time**")
    with table_cols[7]:
        st.markdown("**Created**")
        
    st.markdown("---")
    
    # Display each schedule with checkbox in integrated table
    for i, schedule in enumerate(schedules_sorted):
        cols = st.columns([0.4, 0.4, 2.5, 1, 1.2, 1, 1, 0.8])
        
        with cols[0]:
            selected = st.checkbox(
                "",
                value=select_all,  # Follow the select_all checkbox
                key=f"schedule_checkbox_{schedule.get('id', i)}",
                help=f"Select {schedule.get('name', f'Schedule {i+1}')}"
            )
            if selected:
                selected_schedules.append(schedule)
        
        with cols[1]:
            st.write(f"**{i + 1}**")
        
        with cols[2]:
            st.write(schedule.get('name', f'Schedule {i+1}'))
        
        with cols[3]:
            status_color = "🟢" if schedule.get('enabled', True) else "🔴"
            status_text = "Active" if schedule.get('enabled', True) else "Disabled"
            st.write(f"{status_color} {status_text}")
        
        with cols[4]:
            freq_short = schedule.get('frequency', 'Unknown').split('(')[0].strip()
            st.write(freq_short)
        
        with cols[5]:
            st.write(schedule.get('days_display', 'Unknown'))
        
        with cols[6]:
            st.write(schedule.get('time', 'Unknown'))
        
        with cols[7]:
            st.write(schedule.get('created_date', 'Unknown'))
    
    # Action buttons for selected schedules
    st.markdown("---")
    
    if selected_schedules:
        st.markdown(f"**🎯 {len(selected_schedules)} schedule(s) selected**")
        
        action_cols = st.columns([1, 1, 1, 1])
        
        with action_cols[0]:
            if st.button("✅ Enable Selected", help=f"Enable {len(selected_schedules)} selected schedule(s)"):
                # Enable selected schedules
                for selected in selected_schedules:
                    for i, sched in enumerate(schedules):
                        if sched.get('id') == selected.get('id'):
                            schedules[i]['enabled'] = True
                            break
                
                if save_simple_schedules(schedules):
                    names = [s.get('name', 'Unnamed') for s in selected_schedules]
                    st.success(f"✅ Enabled: {', '.join(names)}")
                    st.rerun()
                else:
                    st.error("Failed to enable schedules")
        
        with action_cols[1]:
            if st.button("❌ Disable Selected", help=f"Disable {len(selected_schedules)} selected schedule(s)"):
                # Disable selected schedules
                for selected in selected_schedules:
                    for i, sched in enumerate(schedules):
                        if sched.get('id') == selected.get('id'):
                            schedules[i]['enabled'] = False
                            break
                
                if save_simple_schedules(schedules):
                    names = [s.get('name', 'Unnamed') for s in selected_schedules]
                    st.success(f"❌ Disabled: {', '.join(names)}")
                    st.rerun()
                else:
                    st.error("Failed to disable schedules")
        
        with action_cols[2]:
            if st.button("🔄 Toggle Selected", help=f"Toggle status of {len(selected_schedules)} selected schedule(s)"):
                # Toggle selected schedules
                for selected in selected_schedules:
                    for i, sched in enumerate(schedules):
                        if sched.get('id') == selected.get('id'):
                            schedules[i]['enabled'] = not schedules[i].get('enabled', True)
                            break
                
                if save_simple_schedules(schedules):
                    names = [s.get('name', 'Unnamed') for s in selected_schedules]
                    st.success(f"🔄 Toggled: {', '.join(names)}")
                    st.rerun()
                else:
                    st.error("Failed to toggle schedules")
        
        with action_cols[3]:
            if st.button("🗑️ Delete Selected", help=f"Delete {len(selected_schedules)} selected schedule(s)", type="secondary"):
                # Confirm deletion
                selected_ids = [s.get('id') for s in selected_schedules]
                updated_schedules = [s for s in schedules if s.get('id') not in selected_ids]
                
                if save_simple_schedules(updated_schedules):
                    names = [s.get('name', 'Unnamed') for s in selected_schedules]
                    st.success(f"🗑️ Deleted: {', '.join(names)}")
                    st.rerun()
                else:
                    st.error("Failed to delete schedules")
    else:
        st.info("💡 **Tip:** Select schedules using the checkboxes above to manage them")
    
    # Summary info
    active_count = len([s for s in schedules if s.get('enabled', True)])
    st.info(f"📊 **Total:** {len(schedules)} schedules | **Active:** {active_count} | **Disabled:** {len(schedules) - active_count}")

def render_scheduler_controls():
    """Render scheduler control panel"""
    
    st.markdown("#### 🎛️ Scheduler Controls")
    st.markdown("Start the scheduler to automatically fetch proposals based on your schedules")
    
    # Import the schedule executor
    try:
        from services.schedule_executor import schedule_executor
        
        # Get current status
        status = schedule_executor.get_status()
        
        # Status display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if status['running']:
                st.success("🟢 Running")
            else:
                st.error("🔴 Stopped")
        
        with col2:
            st.info(f"📅 {status['active_schedules']} Active")
        
        with col3:
            if status['notifications_available']:
                st.success("🔔 Notifications OK")
            else:
                st.warning("🔔 No Notifications")
        
        with col4:
            st.metric("Total Schedules", status['total_schedules'])
        
        # Control buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start Scheduler", type="primary", use_container_width=True):
                try:
                    schedule_executor.start()
                    st.success("✅ Scheduler started!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        with col2:
            if st.button("🛑 Stop Scheduler", use_container_width=True):
                try:
                    schedule_executor.stop()
                    st.success("✅ Scheduler stopped!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        with col3:
            if st.button("🔍 Test Check", help="Run manual proposal check", use_container_width=True):
                try:
                    with st.spinner("Checking for new proposals..."):
                        success = schedule_executor.run_manual_check()
                        if success:
                            st.success("✅ Manual check completed!")
                        else:
                            st.error("❌ Check failed")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Show next scheduled jobs
        if status['running'] and status['next_jobs']:
            with st.expander("📋 Next Scheduled Jobs"):
                for i, job in enumerate(status['next_jobs'][:3], 1):
                    st.text(f"{i}. {job}")
        
        # Instructions
        if not status['running']:
            st.info("💡 **How it works:** Start the scheduler to automatically fetch proposals according to your saved schedules. You'll get desktop notifications when new proposals are found!")
        else:
            st.success("✅ **Scheduler is running!** Your schedules are active and will automatically check for new proposals.")
    
    except ImportError:
        st.error("❌ Schedule executor not available")
    except Exception as e:
        st.error(f"❌ Error loading scheduler: {str(e)}")

def render_email_configuration():
    """Render email configuration interface"""
    
    st.markdown("#### 🔔 Notification Settings")
    
    try:
        from services.schedule_executor import schedule_executor
        
        # Load current email configuration
        email_config = schedule_executor.load_email_config()
        
        # Desktop notifications info (always works)
        st.success("✅ **Desktop notifications are ALWAYS enabled** - no setup required!")
        st.info("💡 When new proposals are found, you'll see a popup notification on your computer. This works automatically!")
        
        # Email configuration form
        with st.expander("⚙️ Email Settings (Optional)", expanded=not email_config.get('enabled', False)):
            
            # Enable/disable email notifications
            email_enabled = st.checkbox(
                "Also send email notifications",
                value=email_config.get('enabled', False),
                help="Send email alerts in addition to desktop notifications"
            )
            
            if email_enabled:
                # Show warning about complexity
                st.warning("⚠️ **Email setup requires passwords and can be complex.** Desktop notifications work great without any setup!")
                
                with st.expander("📧 Advanced: Email Setup (Optional)", expanded=False):
                    st.markdown("**Only set this up if you really need email notifications.**")
                    st.info("💡 **Tip:** Desktop notifications are much simpler and work instantly without any configuration!")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        # Email provider selection
                        email_provider = st.selectbox(
                            "Choose your email provider:",
                            options=["Gmail", "Outlook/Hotmail", "Yahoo", "Other"],
                            index=0,
                            help="Select your email provider for automatic configuration"
                        )
                        
                        # Sender email
                        sender_email = st.text_input(
                            "Your email address:",
                            value=email_config.get('sender_email', ''),
                            placeholder="your-email@gmail.com",
                            help="The email address you want to send notifications from"
                        )
                        
                        # Password with helpful hints
                        if email_provider == "Gmail":
                            password_help = "⚠️ COMPLEX: Need Gmail App Password (not regular password)"
                            password_placeholder = "Gmail App Password (hard to get)"
                            st.error("🔴 Gmail requires special App Password setup - very complicated!")
                        elif email_provider == "Outlook/Hotmail":
                            password_help = "✅ SIMPLE: Use your normal Outlook password"
                            password_placeholder = "Your normal Outlook password"
                            st.success("🟢 Outlook is the easiest - just use your normal password!")
                        elif email_provider == "Yahoo":
                            password_help = "⚠️ COMPLEX: Need Yahoo App Password (not regular password)"
                            password_placeholder = "Yahoo App Password (hard to get)"
                            st.error("🔴 Yahoo requires special App Password setup - very complicated!")
                        else:
                            password_help = "Varies by provider - may be complex"
                            password_placeholder = "Your email password"
                        
                        sender_password = st.text_input(
                            "Password:",
                            value=email_config.get('sender_password', ''),
                            type="password",
                            placeholder=password_placeholder,
                            help=password_help
                        )
                
                with col2:
                    st.markdown("**Who should receive notifications?**")
                    
                    # Recipients with better explanation
                    recipients_text = st.text_area(
                        "Send notifications to:",
                        value="\\n".join(email_config.get('recipient_emails', [])),
                        placeholder="developer1@company.com\\ndeveloper2@company.com\\nmanager@company.com",
                        help="Enter email addresses, one per line",
                        height=120
                    )
                    
                    # Show helpful setup instructions
                    if email_provider == "Gmail":
                        st.info("💡 **Gmail Setup:** Go to Google Account settings → Security → 2-Step Verification → App passwords → Generate app password")
                    elif email_provider == "Yahoo":
                        st.info("💡 **Yahoo Setup:** Go to Account Security → Generate app password → Select 'Mail' → Use generated password")
                    else:
                        st.info("💡 **Tip:** If login fails, you may need to enable 'Less secure app access' or use an app password")
                
                # Auto-configure SMTP settings based on provider
                if email_provider == "Gmail":
                    smtp_server = "smtp.gmail.com"
                    smtp_port = 587
                elif email_provider == "Outlook/Hotmail":
                    smtp_server = "smtp-mail.outlook.com" 
                    smtp_port = 587
                elif email_provider == "Yahoo":
                    smtp_server = "smtp.mail.yahoo.com"
                    smtp_port = 587
                else:
                    # For "Other", show advanced settings
                    st.markdown("**Advanced Settings (for other providers):**")
                    smtp_server = st.text_input("SMTP Server:", value=email_config.get('smtp_server', ''))
                    smtp_port = st.number_input("SMTP Port:", value=email_config.get('smtp_port', 587), min_value=1, max_value=65535)
                
                # Save configuration
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    if st.button("💾 Save Email Config", type="primary", use_container_width=True):
                        try:
                            # Parse recipient emails
                            recipient_emails = [email.strip() for email in recipients_text.split('\\n') if email.strip()]
                            
                            # Validate required fields
                            if not all([smtp_server, sender_email, sender_password, recipient_emails]):
                                st.error("❌ Please fill in all required fields")
                            else:
                                # Save configuration
                                new_config = {
                                    'enabled': email_enabled,
                                    'smtp_server': smtp_server,
                                    'smtp_port': smtp_port,
                                    'sender_email': sender_email,
                                    'sender_password': sender_password,
                                    'recipient_emails': recipient_emails
                                }
                                
                                if schedule_executor.save_email_config(new_config):
                                    st.success("✅ Email configuration saved!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to save configuration")
                                    
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                
                with col2:
                    if st.button("📧 Test Email", help="Send test email", use_container_width=True):
                        try:
                            # Create test notification data
                            test_proposals = {
                                'ethereum': [7001, 7002],
                                'tron': [7003]
                            }
                            
                            with st.spinner("Sending test email..."):
                                schedule_executor.send_email_notification(test_proposals, 3)
                                st.success("✅ Test email sent! Check your inbox.")
                                
                        except Exception as e:
                            st.error(f"❌ Test email failed: {str(e)}")
                
                with col3:
                    if st.button("❌ Disable Email", use_container_width=True):
                        try:
                            config = email_config.copy()
                            config['enabled'] = False
                            if schedule_executor.save_email_config(config):
                                st.success("✅ Email notifications disabled")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            
            else:
                st.info("📧 Email notifications are disabled. Enable above to configure email settings.")
        
        # Show current email status
        status = schedule_executor.get_status()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if status['email_enabled']:
                st.success("✅ Email Enabled")
            else:
                st.error("❌ Email Disabled")
        
        with col2:
            if status['email_configured']:
                st.success("✅ Email Configured")
            else:
                st.warning("⚠️ Email Not Configured")
        
        with col3:
            if status['email_available']:
                st.success("✅ Email Available")
            else:
                st.error("❌ Email Not Available")
        
        # Show recipient count
        if email_config.get('recipient_emails'):
            st.info(f"📬 {len(email_config['recipient_emails'])} email recipients configured")
        
    except ImportError:
        st.error("❌ Email system not available")
    except Exception as e:
        st.error(f"❌ Error loading email configuration: {str(e)}")

def render_create_schedule_form():
    """Render the step-by-step create schedule form"""
    
    st.markdown("#### ➕ Create New Schedule")
    
    # Initialize session state for the form
    if 'show_create_form' not in st.session_state:
        st.session_state.show_create_form = False
    if 'schedule_step' not in st.session_state:
        st.session_state.schedule_step = 1
    if 'schedule_data' not in st.session_state:
        st.session_state.schedule_data = {}
    
    # Show/hide create form
    if not st.session_state.show_create_form:
        if st.button("📝 Create Schedule", type="primary", use_container_width=True):
            st.session_state.show_create_form = True
            st.session_state.schedule_step = 1
            st.session_state.schedule_data = {}
            st.rerun()
        return
    
    # Show form steps
    st.markdown("**Step-by-step schedule creation:**")
    
    # Progress indicator
    progress_text = ""
    if st.session_state.schedule_step >= 1:
        progress_text += "✅ Frequency"
    else:
        progress_text += "1️⃣ Frequency"
    
    if st.session_state.schedule_step >= 2:
        progress_text += " → ✅ Days"
    elif st.session_state.schedule_step == 2:
        progress_text += " → 2️⃣ Days"
    else:
        progress_text += " → ⏸️ Days"
    
    if st.session_state.schedule_step >= 3:
        progress_text += " → ✅ Time"
    elif st.session_state.schedule_step == 3:
        progress_text += " → 3️⃣ Time"
    else:
        progress_text += " → ⏸️ Time"
    
    if st.session_state.schedule_step >= 4:
        progress_text += " → ✅ Name"
    elif st.session_state.schedule_step == 4:
        progress_text += " → 4️⃣ Name"
    else:
        progress_text += " → ⏸️ Name"
    
    st.markdown(f"**Progress:** {progress_text}")
    st.markdown("---")
    
    # Step 1: Select Frequency
    if st.session_state.schedule_step >= 1:
        render_frequency_step()
    
    # Step 2: Select Days (only if frequency is selected)
    if st.session_state.schedule_step >= 2:
        render_days_step()
    
    # Step 3: Select Time (only if days are selected)
    if st.session_state.schedule_step >= 3:
        render_time_step()
    
    # Step 4: Schedule Name (only if time is selected)
    if st.session_state.schedule_step >= 4:
        render_name_step()
    
    # Cancel button
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.show_create_form = False
            st.session_state.schedule_step = 1
            st.session_state.schedule_data = {}
            st.rerun()
    
    with col2:
        if st.session_state.schedule_step >= 4 and st.session_state.schedule_data.get('name'):
            if st.button("💾 Save Schedule", type="primary", use_container_width=True):
                save_new_schedule()

def render_frequency_step():
    """Step 1: Select frequency"""
    
    st.markdown("##### 1️⃣ Select Frequency")
    
    frequency_options = [
        "Daily (Every day)",
        "Weekdays (Monday-Friday)", 
        "Weekly (Once per week)",
        "Bi-weekly (Every 2 weeks)",
        "Custom (Select specific days)"
    ]
    
    selected_frequency = st.selectbox(
        "How often should this run?",
        options=frequency_options,
        key="frequency_select"
    )
    
    if selected_frequency:
        st.session_state.schedule_data['frequency'] = selected_frequency
        
        if st.button("Next: Select Days →", type="primary"):
            st.session_state.schedule_step = 2
            st.rerun()
        
        # Show current selection
        st.success(f"✅ Selected: {selected_frequency}")

def render_days_step():
    """Step 2: Select days based on frequency"""
    
    st.markdown("##### 2️⃣ Select Days")
    
    frequency = st.session_state.schedule_data.get('frequency', '')
    
    if "Daily" in frequency:
        # Daily - all days
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        st.info("📅 Daily schedule will run every day")
        st.session_state.schedule_data['days'] = days
        st.session_state.schedule_data['days_display'] = "Every day"
        
    elif "Weekdays" in frequency:
        # Weekdays only
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        st.info("📅 Weekdays schedule will run Monday through Friday")
        st.session_state.schedule_data['days'] = days
        st.session_state.schedule_data['days_display'] = "Monday-Friday"
        
    elif "Weekly" in frequency:
        # Weekly - select one day
        day_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        selected_day = st.selectbox("Select which day of the week:", options=day_options)
        
        if selected_day:
            st.session_state.schedule_data['days'] = [selected_day]
            st.session_state.schedule_data['days_display'] = f"Every {selected_day}"
            
    elif "Bi-weekly" in frequency:
        # Bi-weekly - select one day
        day_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        selected_day = st.selectbox("Select which day (every 2 weeks):", options=day_options)
        
        if selected_day:
            st.session_state.schedule_data['days'] = [selected_day]
            st.session_state.schedule_data['days_display'] = f"Every other {selected_day}"
            
    elif "Custom" in frequency:
        # Custom - select multiple days
        day_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        selected_days = st.multiselect("Select specific days:", options=day_options)
        
        if selected_days:
            st.session_state.schedule_data['days'] = selected_days
            st.session_state.schedule_data['days_display'] = ", ".join(selected_days)
    
    # Show buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Back: Change Frequency"):
            st.session_state.schedule_step = 1
            st.rerun()
    
    with col2:
        if st.session_state.schedule_data.get('days'):
            if st.button("Next: Select Time →", type="primary"):
                st.session_state.schedule_step = 3
                st.rerun()
    
    # Show current selection
    if st.session_state.schedule_data.get('days_display'):
        st.success(f"✅ Selected: {st.session_state.schedule_data['days_display']}")

def render_time_step():
    """Step 3: Select time"""
    
    st.markdown("##### 3️⃣ Select Time")
    
    # Time selection
    selected_time = st.time_input(
        "What time should it run?",
        value=time(9, 0),  # Default 9:00 AM
        step=1800  # 30 minute steps
    )
    
    if selected_time:
        st.session_state.schedule_data['time'] = selected_time.strftime('%H:%M')
        st.session_state.schedule_data['time_display'] = selected_time.strftime('%I:%M %p')
    
    # Show buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Back: Change Days"):
            st.session_state.schedule_step = 2
            st.rerun()
    
    with col2:
        if st.session_state.schedule_data.get('time'):
            if st.button("Next: Schedule Name →", type="primary"):
                st.session_state.schedule_step = 4
                st.rerun()
    
    # Show current selection
    if st.session_state.schedule_data.get('time_display'):
        st.success(f"✅ Selected: {st.session_state.schedule_data['time_display']}")

def render_name_step():
    """Step 4: Enter schedule name"""
    
    st.markdown("##### 4️⃣ Schedule Name")
    st.markdown("**Please enter a name for your schedule:**")
    
    # Auto-generate a suggested name
    freq = st.session_state.schedule_data.get('frequency', 'Schedule')
    time_str = st.session_state.schedule_data.get('time_display', '')
    days_str = st.session_state.schedule_data.get('days_display', '')
    
    # Create suggested name
    freq_short = freq.split('(')[0].strip()
    suggested_name = f"{freq_short} at {time_str}"
    
    # Show suggested name
    st.markdown(f"**Suggested name:** `{suggested_name}`")
    
    # Schedule name input
    schedule_name = st.text_input(
        "Enter a name for this schedule:",
        placeholder=suggested_name, 
        help="Give your schedule a descriptive name",
        key="schedule_name_input"
    )
    
    # Use suggested name if nothing entered
    if not schedule_name:
        schedule_name = suggested_name
    
    # Always store the name (even if it's the suggested name)
    st.session_state.schedule_data['name'] = schedule_name
    
    # Show buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Back: Change Time"):
            st.session_state.schedule_step = 3
            st.rerun()
    
    with col2:
        # This button is handled in the main form
        pass
    
    # Show current selection
    if st.session_state.schedule_data.get('name'):
        st.success(f"✅ Name: {st.session_state.schedule_data['name']}")
        
        # Show complete summary
        st.markdown("**📋 Final Schedule Summary:**")
        st.info(f"""
        **Name:** {st.session_state.schedule_data.get('name', 'Unnamed')}
        **Frequency:** {st.session_state.schedule_data.get('frequency', 'Unknown')}
        **Days:** {st.session_state.schedule_data.get('days_display', 'Unknown')}
        **Time:** {st.session_state.schedule_data.get('time_display', 'Unknown')}
        """)

def save_new_schedule():
    """Save the new schedule"""
    
    try:
        # Load existing schedules
        schedules = load_simple_schedules()
        
        # Create new schedule
        new_schedule = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "name": st.session_state.schedule_data.get('name', 'Unnamed Schedule'),
            "frequency": st.session_state.schedule_data.get('frequency', ''),
            "days": st.session_state.schedule_data.get('days', []),
            "days_display": st.session_state.schedule_data.get('days_display', ''),
            "time": st.session_state.schedule_data.get('time_display', ''),
            "time_24h": st.session_state.schedule_data.get('time', ''),
            "enabled": True,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat()
        }
        
        # Add to schedules
        schedules.append(new_schedule)
        
        # Save
        if save_simple_schedules(schedules):
            st.success(f"✅ Schedule '{new_schedule['name']}' created successfully!")
            
            # Reset form
            st.session_state.show_create_form = False
            st.session_state.schedule_step = 1
            st.session_state.schedule_data = {}
            
            st.rerun()
        else:
            st.error("❌ Failed to save schedule")
            
    except Exception as e:
        st.error(f"❌ Error saving schedule: {str(e)}")