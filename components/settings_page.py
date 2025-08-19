"""
Settings Page Component for Streamlit UI
Secure configuration interface for API keys and system settings
"""
import streamlit as st
import os
import json
from pathlib import Path
import getpass

def mask_api_key(api_key: str) -> str:
    """Mask API key for secure display - shows first 4 and last 4 digits"""
    if not api_key:
        return "Not Set"
    if len(api_key) <= 8:
        return "*" * len(api_key)
    # Show first 4 and last 4 characters with stars in between
    return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]

def load_env_variables():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value:
                        os.environ[key] = value

def save_env_file(settings: dict):
    """Save settings to .env file"""
    env_content = []
    env_content.append("# Blockchain Notification System Configuration")
    env_content.append("# Updated via Streamlit Settings UI")
    env_content.append("")
    
    env_content.append("# OpenAI Configuration")
    env_content.append(f"OPENAI_API_KEY={settings.get('openai_api_key', '')}")
    env_content.append(f"OPENAI_MODEL={settings.get('openai_model', 'gpt-4o')}")
    env_content.append(f"OPENAI_MAX_TOKENS={settings.get('openai_max_tokens', '1000')}")
    env_content.append(f"OPENAI_TEMPERATURE={settings.get('openai_temperature', '0.3')}")
    env_content.append("")
    
    env_content.append("# Email Configuration")
    env_content.append(f"SENDER_EMAIL={settings.get('sender_email', '')}")
    env_content.append(f"SENDER_PASSWORD={settings.get('sender_password', '')}")
    env_content.append("SMTP_SERVER=smtp.gmail.com")
    env_content.append("SMTP_PORT=587")
    env_content.append("")
    
    env_content.append("# Slack Configuration")
    env_content.append(f"SLACK_WEBHOOK_URL={settings.get('slack_webhook_url', '')}")
    env_content.append(f"SLACK_CHANNEL={settings.get('slack_channel', '#faws_testing')}")
    
    with open('.env', 'w') as f:
        f.write('\n'.join(env_content))
    
    # Update .gitignore
    gitignore_file = Path('.gitignore')
    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            content = f.read()
        if '.env' not in content:
            with open(gitignore_file, 'a') as f:
                f.write('\n# Environment variables\n.env\n')
    else:
        with open(gitignore_file, 'w') as f:
            f.write("# Environment variables\n.env\n")

def test_openai_connection(api_key: str) -> bool:
    """Test OpenAI API connection"""
    try:
        # Temporarily set the API key
        original_key = os.environ.get('OPENAI_API_KEY')
        os.environ['OPENAI_API_KEY'] = api_key
        
        from services.unified_impact_analyzer import UnifiedImpactAnalyzer
        analyzer = UnifiedImpactAnalyzer()
        
        # Restore original key
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        return analyzer.ai_available
    except Exception:
        return False

def test_slack_webhook(webhook_url: str) -> bool:
    """Test Slack webhook"""
    try:
        import requests
        test_payload = {
            "text": "🧪 Configuration test from Blockchain Notification System",
            "username": "Settings Test Bot"
        }
        response = requests.post(webhook_url, json=test_payload, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

def render_schedule_settings():
    """Render schedule management settings"""
    
    st.markdown("Configure automatic proposal monitoring schedules")
    
    # Load existing schedules
    schedules_file = "data/simple_schedules.json"
    if os.path.exists(schedules_file):
        try:
            with open(schedules_file, 'r') as f:
                schedules = json.load(f)
        except:
            schedules = []
    else:
        schedules = []
    
    # Schedule overview
    st.subheader("📋 Current Schedules")
    
    if schedules:
        for schedule in schedules:
            if schedule.get('enabled', True):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(f"**{schedule.get('name', 'Unnamed')}**")
                    
                with col2:
                    st.write(schedule.get('frequency', 'Unknown'))
                    
                with col3:
                    st.write(schedule.get('time', 'Unknown'))
                    
                with col4:
                    status = "🟢 Active" if schedule.get('enabled', True) else "🔴 Disabled"
                    st.write(status)
        
        st.divider()
    else:
        st.info("No schedules configured. Use the Schedule page to create schedules.")
    
    # Schedule settings
    st.subheader("⚙️ Schedule Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Execution Settings:**")
        
        default_timeout = st.number_input(
            "Default Timeout (minutes)",
            min_value=1,
            max_value=60,
            value=int(os.getenv('SCHEDULE_TIMEOUT', '10')),
            help="Maximum time allowed for each schedule execution"
        )
        
        retry_count = st.number_input(
            "Retry Attempts",
            min_value=0,
            max_value=5,
            value=int(os.getenv('SCHEDULE_RETRIES', '3')),
            help="Number of retry attempts on failure"
        )
        
    with col2:
        st.markdown("**Notification Settings:**")
        
        notify_on_success = st.checkbox(
            "Notify on Success",
            value=os.getenv('NOTIFY_SUCCESS', 'true').lower() == 'true',
            help="Send notifications when schedules complete successfully"
        )
        
        notify_on_failure = st.checkbox(
            "Notify on Failure", 
            value=os.getenv('NOTIFY_FAILURE', 'true').lower() == 'true',
            help="Send notifications when schedules fail"
        )
    
    # Data retention settings
    st.subheader("🗄️ History & Retention")
    
    col1, col2 = st.columns(2)
    
    with col1:
        history_days = st.number_input(
            "Keep History (days)",
            min_value=1,
            max_value=365,
            value=int(os.getenv('HISTORY_RETENTION_DAYS', '30')),
            help="How long to keep execution history"
        )
        
    with col2:
        max_log_entries = st.number_input(
            "Max Log Entries",
            min_value=10,
            max_value=1000,
            value=int(os.getenv('MAX_LOG_ENTRIES', '100')),
            help="Maximum number of log entries to keep"
        )
    
    # Save schedule settings
    if st.button("💾 Save Schedule Settings", use_container_width=True):
        schedule_settings = {
            'schedule_timeout': str(default_timeout),
            'schedule_retries': str(retry_count),
            'notify_success': str(notify_on_success).lower(),
            'notify_failure': str(notify_on_failure).lower(),
            'history_retention_days': str(history_days),
            'max_log_entries': str(max_log_entries)
        }
        
        if save_env_variables(schedule_settings):
            st.success("✅ Schedule settings saved successfully!")
            st.info("Restart the scheduler to apply new settings.")
        else:
            st.error("❌ Failed to save schedule settings")

def render_data_settings():
    """Render data source and proposal settings"""
    
    st.markdown("Configure blockchain data sources and proposal settings")
    
    # Data source settings
    st.subheader("🔗 Data Sources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Proposal Sources:**")
        
        # EIPs settings
        eips_enabled = st.checkbox(
            "Ethereum EIPs",
            value=os.getenv('EIPS_ENABLED', 'true').lower() == 'true',
            help="Monitor Ethereum Improvement Proposals"
        )
        
        tips_enabled = st.checkbox(
            "TRON TIPs",
            value=os.getenv('TIPS_ENABLED', 'true').lower() == 'true', 
            help="Monitor TRON Improvement Proposals"
        )
        
        bips_enabled = st.checkbox(
            "Bitcoin BIPs",
            value=os.getenv('BIPS_ENABLED', 'true').lower() == 'true',
            help="Monitor Bitcoin Improvement Proposals"  
        )
        
        beps_enabled = st.checkbox(
            "Binance BEPs",
            value=os.getenv('BEPS_ENABLED', 'true').lower() == 'true',
            help="Monitor Binance Evolution Proposals"
        )
        
    with col2:
        st.markdown("**Update Settings:**")
        
        update_interval = st.selectbox(
            "Update Frequency",
            ["Every 30 minutes", "Every hour", "Every 2 hours", "Every 4 hours", "Daily"],
            index=2 if os.getenv('UPDATE_INTERVAL', '2h') == '2h' else 0,
            help="How often to check for new proposals"
        )
        
        batch_size = st.number_input(
            "Batch Size",
            min_value=10,
            max_value=1000,
            value=int(os.getenv('BATCH_SIZE', '100')),
            help="Number of proposals to process per batch"
        )
        
        rate_limit = st.number_input(
            "Rate Limit (requests/min)",
            min_value=1,
            max_value=100,
            value=int(os.getenv('RATE_LIMIT', '60')),
            help="API request rate limit to avoid blocking"
        )
    
    st.divider()
    
    # Data quality settings
    st.subheader("🎯 Data Quality")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Filtering:**")
        
        min_proposal_length = st.number_input(
            "Min Proposal Length",
            min_value=10,
            max_value=1000,
            value=int(os.getenv('MIN_PROPOSAL_LENGTH', '50')),
            help="Minimum character length for proposals"
        )
        
        exclude_drafts = st.checkbox(
            "Exclude Draft Proposals",
            value=os.getenv('EXCLUDE_DRAFTS', 'false').lower() == 'true',
            help="Skip proposals in draft status"
        )
        
    with col2:
        st.markdown("**Processing:**")
        
        enable_deduplication = st.checkbox(
            "Enable Deduplication",
            value=os.getenv('ENABLE_DEDUPLICATION', 'true').lower() == 'true',
            help="Remove duplicate proposals automatically"
        )
        
        validate_links = st.checkbox(
            "Validate Links",
            value=os.getenv('VALIDATE_LINKS', 'false').lower() == 'true',
            help="Check if proposal links are accessible"
        )
    
    # Cache settings
    st.subheader("🗂️ Cache & Storage")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cache_duration = st.selectbox(
            "Cache Duration",
            ["1 hour", "6 hours", "12 hours", "24 hours"],
            index=1 if os.getenv('CACHE_DURATION', '6h') == '6h' else 0,
            help="How long to cache fetched data"
        )
        
    with col2:
        backup_enabled = st.checkbox(
            "Enable Backups",
            value=os.getenv('BACKUP_ENABLED', 'true').lower() == 'true',
            help="Create automatic backups of proposal data"
        )
    
    # Save data settings
    if st.button("💾 Save Data Settings", use_container_width=True):
        # Convert interval to standardized format
        interval_map = {
            "Every 30 minutes": "30m",
            "Every hour": "1h", 
            "Every 2 hours": "2h",
            "Every 4 hours": "4h",
            "Daily": "24h"
        }
        
        cache_map = {
            "1 hour": "1h",
            "6 hours": "6h",
            "12 hours": "12h", 
            "24 hours": "24h"
        }
        
        data_settings = {
            'eips_enabled': str(eips_enabled).lower(),
            'tips_enabled': str(tips_enabled).lower(),
            'bips_enabled': str(bips_enabled).lower(),
            'beps_enabled': str(beps_enabled).lower(),
            'update_interval': interval_map.get(update_interval, '2h'),
            'batch_size': str(batch_size),
            'rate_limit': str(rate_limit),
            'min_proposal_length': str(min_proposal_length),
            'exclude_drafts': str(exclude_drafts).lower(),
            'enable_deduplication': str(enable_deduplication).lower(),
            'validate_links': str(validate_links).lower(),
            'cache_duration': cache_map.get(cache_duration, '6h'),
            'backup_enabled': str(backup_enabled).lower()
        }
        
        if save_env_variables(data_settings):
            st.success("✅ Data settings saved successfully!")
            st.info("Changes will take effect on next data fetch.")
        else:
            st.error("❌ Failed to save data settings")

def render_settings_page():
    """Render the settings page"""
    
    # Load current environment variables
    load_env_variables()
    
    st.title("⚙️ System Settings")
    st.markdown("Configure your API keys and system settings securely")
    
    # Create tabs for different setting categories
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 OpenAI", "📧 Email", "💬 Slack", "📅 Schedule", "📊 Data"])
    
    # OpenAI Settings Tab
    with tab1:
        st.header("🤖 OpenAI Configuration")
        
        current_key = os.getenv('OPENAI_API_KEY', '')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("**Current Status:** " + ("✅ Configured" if current_key else "❌ Not Set"))
            if current_key:
                st.code(f"API Key: {mask_api_key(current_key)}")
        
        with col2:
            if current_key:
                if st.button("🔄 Update API Key", key="update_openai"):
                    st.session_state.show_openai_form = True
            else:
                if st.button("🔑 Set API Key", key="set_openai"):
                    st.session_state.show_openai_form = True
        
        # Show API key form
        if st.session_state.get('show_openai_form', False):
            with st.form("openai_form"):
                st.markdown("**Enter your OpenAI API Key:**")
                st.markdown("Get it from: https://platform.openai.com/api-keys")
                
                new_api_key = st.text_input(
                    "API Key",
                    type="password",
                    placeholder="sk-your-api-key-here",
                    help="Your API key will be stored securely and masked in the UI"
                )
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.form_submit_button("💾 Save"):
                        if new_api_key:
                            if new_api_key.startswith('sk-'):
                                # Test the key
                                if test_openai_connection(new_api_key):
                                    os.environ['OPENAI_API_KEY'] = new_api_key
                                    settings = {
                                        'openai_api_key': new_api_key,
                                        'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4o'),
                                        'openai_max_tokens': os.getenv('OPENAI_MAX_TOKENS', '1000'),
                                        'openai_temperature': os.getenv('OPENAI_TEMPERATURE', '0.3'),
                                        'sender_email': os.getenv('SENDER_EMAIL', ''),
                                        'sender_password': os.getenv('SENDER_PASSWORD', ''),
                                        'slack_webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
                                        'slack_channel': os.getenv('SLACK_CHANNEL', '#faws_testing')
                                    }
                                    save_env_file(settings)
                                    st.success("✅ OpenAI API Key saved and tested successfully!")
                                    st.session_state.show_openai_form = False
                                    st.rerun()
                                else:
                                    st.error("❌ Invalid API key or connection failed")
                            else:
                                st.warning("⚠️ API key should start with 'sk-'")
                        else:
                            st.error("❌ Please enter an API key")
                
                with col2:
                    if st.form_submit_button("🧪 Test Only"):
                        if new_api_key:
                            if test_openai_connection(new_api_key):
                                st.success("✅ API key is valid!")
                            else:
                                st.error("❌ Invalid API key or connection failed")
                        else:
                            st.error("❌ Please enter an API key")
                
                with col3:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.show_openai_form = False
                        st.rerun()
        
        # Advanced OpenAI Settings
        st.subheader("🎛️ Advanced Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            # Latest OpenAI models for blockchain analysis
            model_options = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
            current_model = os.getenv('OPENAI_MODEL', 'gpt-4o')
            
            # Find index of current model, default to gpt-4o
            try:
                model_index = model_options.index(current_model)
            except ValueError:
                model_index = 0  # Default to gpt-4o
                
            model = st.selectbox(
                "Model",
                model_options,
                index=model_index,
                help="Latest GPT models optimized for blockchain proposal analysis"
            )
            
        with col2:
            max_tokens = st.number_input(
                "Max Tokens",
                min_value=100,
                max_value=4000,
                value=int(os.getenv('OPENAI_MAX_TOKENS', '1000')),
                help="Maximum tokens per request"
            )
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=float(os.getenv('OPENAI_TEMPERATURE', '0.3')),
            step=0.1,
            help="Controls randomness in responses"
        )
        
        if st.button("💾 Save Advanced Settings"):
            settings = {
                'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
                'openai_model': model,
                'openai_max_tokens': str(max_tokens),
                'openai_temperature': str(temperature),
                'sender_email': os.getenv('SENDER_EMAIL', ''),
                'sender_password': os.getenv('SENDER_PASSWORD', ''),
                'slack_webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
                'slack_channel': os.getenv('SLACK_CHANNEL', '#faws_testing')
            }
            save_env_file(settings)
            st.success("✅ Advanced settings saved!")
    
    # Email Settings Tab
    with tab2:
        st.header("📧 Email Configuration")
        
        current_email = os.getenv('SENDER_EMAIL', '')
        current_password = os.getenv('SENDER_PASSWORD', '')
        
        st.info("**Current Status:** " + ("✅ Configured" if current_email and current_password else "❌ Not Set"))
        
        if current_email:
            st.code(f"Email: {current_email}")
            st.code(f"Password: {mask_api_key(current_password)}")
        
        st.markdown("**📝 Gmail Setup Instructions:**")
        st.markdown("""
        1. Enable 2-Factor Authentication on Gmail
        2. Go to: https://myaccount.google.com/apppasswords
        3. Generate App Password for "Mail"
        4. Use the App Password below (NOT your regular Gmail password)
        """)
        
        with st.form("email_form"):
            new_email = st.text_input(
                "Sender Email",
                value=current_email,
                placeholder="your-email@gmail.com"
            )
            
            new_password = st.text_input(
                "Gmail App Password",
                type="password",
                placeholder="Your Gmail app password"
            )
            
            if st.form_submit_button("💾 Save Email Settings"):
                if new_email and new_password:
                    settings = {
                        'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
                        'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4o'),
                        'openai_max_tokens': os.getenv('OPENAI_MAX_TOKENS', '1000'),
                        'openai_temperature': os.getenv('OPENAI_TEMPERATURE', '0.3'),
                        'sender_email': new_email,
                        'sender_password': new_password,
                        'slack_webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
                        'slack_channel': os.getenv('SLACK_CHANNEL', '#faws_testing')
                    }
                    save_env_file(settings)
                    st.success("✅ Email settings saved!")
                    st.rerun()
                else:
                    st.error("❌ Please fill in both email and password")
        
        # Email test function
        st.divider()
        st.subheader("📧 Test Email Notification")
        
        if current_email and current_password:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                test_recipient = st.text_input(
                    "Test Email Address",
                    value=current_email,
                    help="Email address to send test notification"
                )
                
            with col2:
                if st.button("🧪 Send Test Email", type="secondary"):
                    if test_recipient:
                        # Test email functionality
                        try:
                            import smtplib
                            from email.mime.text import MIMEText
                            from email.mime.multipart import MIMEMultipart
                            
                            msg = MIMEMultipart()
                            msg['From'] = current_email
                            msg['To'] = test_recipient
                            msg['Subject'] = "🧪 Blockchain Monitor - Test Email"
                            
                            body = """
                            <h2>✅ Email Test Successful!</h2>
                            <p>This is a test email from your Blockchain Proposal Monitoring System.</p>
                            <p><strong>Configuration Status:</strong> ✅ Working correctly</p>
                            <p><strong>Test Time:</strong> {}</p>
                            <hr>
                            <p><em>If you received this email, your notification system is properly configured!</em></p>
                            """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            
                            msg.attach(MIMEText(body, 'html'))
                            
                            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                                server.starttls()
                                server.login(current_email, current_password)
                                server.send_message(msg)
                            
                            st.success(f"✅ Test email sent successfully to {test_recipient}!")
                            st.info("Check your inbox for the test message.")
                            
                        except Exception as e:
                            st.error(f"❌ Email test failed: {str(e)}")
                    else:
                        st.warning("Please enter a test email address")
        else:
            st.warning("⚠️ Configure email settings first before testing")
    
    # Slack Settings Tab
    with tab3:
        st.header("💬 Slack Configuration")
        
        current_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        
        st.info("**Current Status:** " + ("✅ Configured" if current_webhook else "❌ Not Set"))
        
        if current_webhook:
            st.code(f"Webhook: {mask_api_key(current_webhook, 8)}")
        
        st.markdown("**📝 Slack Setup Instructions:**")
        st.markdown("""
        1. Go to: https://api.slack.com/apps
        2. Create new app or select existing
        3. Go to "Incoming Webhooks" and activate
        4. Add webhook to workspace
        5. Copy the webhook URL
        """)
        
        with st.form("slack_form"):
            new_webhook = st.text_input(
                "Slack Webhook URL",
                value=current_webhook,
                placeholder="https://hooks.slack.com/services/..."
            )
            
            new_channel = st.text_input(
                "Channel",
                value=os.getenv('SLACK_CHANNEL', '#faws_testing'),
                placeholder="#your-channel"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save"):
                    if new_webhook:
                        if new_webhook.startswith('https://hooks.slack.com/'):
                            settings = {
                                'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
                                'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4o'),
                                'openai_max_tokens': os.getenv('OPENAI_MAX_TOKENS', '1000'),
                                'openai_temperature': os.getenv('OPENAI_TEMPERATURE', '0.3'),
                                'sender_email': os.getenv('SENDER_EMAIL', ''),
                                'sender_password': os.getenv('SENDER_PASSWORD', ''),
                                'slack_webhook_url': new_webhook,
                                'slack_channel': new_channel
                            }
                            save_env_file(settings)
                            st.success("✅ Slack settings saved!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid webhook URL format")
                    else:
                        st.error("❌ Please enter a webhook URL")
            
            with col2:
                if st.form_submit_button("🧪 Test"):
                    if new_webhook:
                        if test_slack_webhook(new_webhook):
                            st.success("✅ Slack webhook test successful!")
                        else:
                            st.error("❌ Slack webhook test failed")
                    else:
                        st.error("❌ Please enter a webhook URL")
        
        # Enhanced Slack test function
        if current_webhook:
            st.divider()
            st.subheader("💬 Test Slack Notification")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                test_message = st.text_area(
                    "Test Message",
                    value="🧪 This is a test notification from your Blockchain Monitoring System!\n\n✅ Configuration is working correctly.",
                    help="Custom message to send for testing"
                )
                
            with col2:
                if st.button("🧪 Send Test Message", type="secondary"):
                    if test_message:
                        # Enhanced test with custom message
                        try:
                            test_payload = {
                                "text": f"🔔 *Blockchain Monitor Test*",
                                "blocks": [
                                    {
                                        "type": "header",
                                        "text": {
                                            "type": "plain_text",
                                            "text": "🧪 Test Notification"
                                        }
                                    },
                                    {
                                        "type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": test_message
                                        }
                                    },
                                    {
                                        "type": "context",
                                        "elements": [
                                            {
                                                "type": "mrkdwn",
                                                "text": f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                            }
                                        ]
                                    }
                                ]
                            }
                            
                            response = requests.post(current_webhook, json=test_payload, timeout=10)
                            
                            if response.status_code == 200:
                                st.success("✅ Test message sent successfully!")
                                st.info("Check your Slack channel for the test message.")
                            else:
                                st.error(f"❌ Test failed with status code: {response.status_code}")
                                
                        except Exception as e:
                            st.error(f"❌ Test failed: {str(e)}")
                    else:
                        st.warning("Please enter a test message")
        else:
            st.warning("⚠️ Configure Slack webhook first before testing")
    
    # Schedule Management Tab
    with tab4:
        st.header("📅 Schedule Management")
        render_schedule_settings()
    
    # Data Configuration Tab  
    with tab5:
        st.header("📊 Data Configuration")
        render_data_settings()

if __name__ == "__main__":
    render_settings_page()