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
    env_content.append(f"OPENAI_MODEL={settings.get('openai_model', 'gpt-3.5-turbo')}")
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

def render_settings_page():
    """Render the settings page"""
    
    # Load current environment variables
    load_env_variables()
    
    st.title("⚙️ System Settings")
    st.markdown("Configure your API keys and system settings securely")
    
    # Create tabs for different setting categories
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 OpenAI", "📧 Email", "💬 Slack", "🧪 Testing"])
    
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
                                        'openai_model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
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
            model = st.selectbox(
                "Model",
                ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                index=0 if os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo') == 'gpt-3.5-turbo' else 1,
                help="GPT model to use for analysis"
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
                        'openai_model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
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
                                'openai_model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
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
    
    # Testing Tab
    with tab4:
        st.header("🧪 System Testing")
        
        st.markdown("Test all your configurations to ensure everything is working properly.")
        
        if st.button("🔬 Run All Tests", type="primary"):
            
            # Test OpenAI
            st.subheader("🤖 OpenAI Test")
            openai_key = os.getenv('OPENAI_API_KEY', '')
            if openai_key:
                if test_openai_connection(openai_key):
                    st.success("✅ OpenAI API: Connected and ready")
                else:
                    st.error("❌ OpenAI API: Connection failed")
            else:
                st.warning("⚠️ OpenAI API: Not configured")
            
            # Test Email
            st.subheader("📧 Email Test")
            email = os.getenv('SENDER_EMAIL', '')
            password = os.getenv('SENDER_PASSWORD', '')
            if email and password:
                st.success("✅ Email: Configuration complete")
                st.info(f"Sender: {email}")
            else:
                st.warning("⚠️ Email: Missing configuration")
            
            # Test Slack
            st.subheader("💬 Slack Test")
            webhook = os.getenv('SLACK_WEBHOOK_URL', '')
            if webhook:
                if test_slack_webhook(webhook):
                    st.success("✅ Slack: Webhook tested successfully!")
                    st.info("Check your Slack channel for test message")
                else:
                    st.error("❌ Slack: Webhook test failed")
            else:
                st.warning("⚠️ Slack: Not configured")
        
        # Configuration Status
        st.subheader("📊 Configuration Status")
        
        openai_status = "✅ Ready" if os.getenv('OPENAI_API_KEY') else "❌ Not Set"
        email_status = "✅ Ready" if (os.getenv('SENDER_EMAIL') and os.getenv('SENDER_PASSWORD')) else "❌ Not Set"
        slack_status = "✅ Ready" if os.getenv('SLACK_WEBHOOK_URL') else "❌ Not Set"
        
        status_data = {
            "Component": ["OpenAI API", "Email", "Slack"],
            "Status": [openai_status, email_status, slack_status]
        }
        
        st.table(status_data)
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start Scheduler"):
                st.info("Run: `python start_scheduler.py` in terminal")
        
        with col2:
            if st.button("📊 View Logs"):
                st.info("Check `logs/` directory for system logs")
        
        with col3:
            if st.button("🔄 Restart System"):
                st.info("Restart the Streamlit app to apply changes")

if __name__ == "__main__":
    render_settings_page()