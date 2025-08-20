"""
Settings Page Component for Streamlit UI
Secure configuration interface for API keys and system settings
"""
import streamlit as st
import os
import json
import requests
from pathlib import Path
import getpass
from datetime import datetime

def mask_api_key(api_key: str, reveal_chars: int = 4) -> str:
    """Mask API key for secure display - shows first N and last N digits"""
    if not api_key:
        return "Not Set"
    if len(api_key) <= reveal_chars * 2:
        return "*" * len(api_key)
    # Show first N and last N characters with stars in between
    return api_key[:reveal_chars] + "*" * (len(api_key) - reveal_chars * 2) + api_key[-reveal_chars:]

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



def render_settings_page():
    """Render the settings page"""
    
    # Load current environment variables
    load_env_variables()
    
    st.title("⚙️ System Settings")
    st.markdown("Configure your API keys and system settings securely")
    
    # Create tabs for different setting categories
    tab1, tab2, tab3 = st.tabs(["🤖 OpenAI", "📧 Email", "💬 Slack"])
    
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
            # Email provider selection
            email_provider = st.selectbox(
                "Email Provider",
                ["Gmail", "Outlook/Hotmail", "Yahoo", "Custom"],
                index=0 if not current_email or 'gmail' in current_email else 
                      1 if 'outlook' in current_email or 'hotmail' in current_email else
                      2 if 'yahoo' in current_email else 3,
                help="Select your email provider for automatic configuration"
            )
            
            # Show provider-specific instructions
            if email_provider == "Gmail":
                st.info("📝 Gmail: Use App Password (not regular password)")
            elif email_provider == "Outlook/Hotmail":
                st.info("📝 Outlook: Use App Password from Microsoft Account settings")
            elif email_provider == "Yahoo":
                st.info("📝 Yahoo: Use App Password from Yahoo Account settings")
            else:
                st.info("📝 Custom: Configure SMTP settings manually")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_email = st.text_input(
                    "Sender Email",
                    value=current_email,
                    placeholder="your-email@domain.com"
                )
                
            with col2:
                new_password = st.text_input(
                    "Email Password",
                    type="password",
                    placeholder="Your app password"
                )
            
            # SMTP configuration (auto-filled for known providers)
            if email_provider == "Custom":
                st.subheader("🔧 SMTP Configuration")
                col1, col2 = st.columns(2)
                
                with col1:
                    smtp_server = st.text_input(
                        "SMTP Server",
                        value=os.getenv('SMTP_SERVER', ''),
                        placeholder="smtp.yourdomain.com"
                    )
                    
                with col2:
                    smtp_port = st.number_input(
                        "SMTP Port",
                        value=int(os.getenv('SMTP_PORT', '587')),
                        min_value=1,
                        max_value=65535
                    )
            else:
                # Auto-configure SMTP based on provider
                if email_provider == "Gmail":
                    smtp_server = "smtp.gmail.com"
                    smtp_port = 587
                elif email_provider == "Outlook/Hotmail":
                    smtp_server = "smtp-mail.outlook.com"
                    smtp_port = 587
                elif email_provider == "Yahoo":
                    smtp_server = "smtp.mail.yahoo.com" 
                    smtp_port = 587
                
                st.info(f"SMTP: {smtp_server}:{smtp_port} (auto-configured)")
            
            # Recipient emails
            st.subheader("📬 Email Recipients")
            
            # Load current recipients
            try:
                with open("data/email_config.json", 'r') as f:
                    email_config = json.load(f)
                current_recipients = email_config.get('recipient_emails', [])
            except:
                current_recipients = []
            
            recipients_text = st.text_area(
                "Recipient Email Addresses",
                value="\n".join(current_recipients) if current_recipients else "",
                height=100,
                placeholder="Enter email addresses (one per line, or separated by commas/semicolons):\nexample1@domain.com\nexample2@domain.com",
                help="Supports multiple formats: newlines, commas, or semicolons"
            )
            
            # Preview recipients if provided
            if recipients_text.strip():
                import re
                
                raw_emails = re.split(r'[\n;,]+', recipients_text)
                preview_emails = []
                for email in raw_emails:
                    email = email.strip()
                    if email and '@' in email:
                        preview_emails.append(email)
                
                if preview_emails:
                    st.success(f"✅ {len(preview_emails)} recipients detected")
                    with st.expander("👀 Preview Recipients"):
                        for email in preview_emails:
                            st.write(f"📧 {email}")
            
            if st.form_submit_button("💾 Save Email Settings"):
                if new_email and new_password:
                    # Parse recipient emails
                    recipient_emails = []
                    if recipients_text.strip():
                        import re
                        raw_emails = re.split(r'[\n;,]+', recipients_text)
                        for email in raw_emails:
                            email = email.strip()
                            if email and '@' in email:
                                recipient_emails.append(email)
                    
                    if not recipient_emails:
                        st.warning("⚠️ No valid recipient emails found. Please add at least one recipient.")
                    else:
                        # Save to environment variables
                        env_settings = {
                            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
                            'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4o'),
                            'openai_max_tokens': os.getenv('OPENAI_MAX_TOKENS', '1000'),
                            'openai_temperature': os.getenv('OPENAI_TEMPERATURE', '0.3'),
                            'sender_email': new_email,
                            'sender_password': new_password,
                            'smtp_server': smtp_server,
                            'smtp_port': str(smtp_port),
                            'slack_webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
                            'slack_channel': os.getenv('SLACK_CHANNEL', '#faws_testing')
                        }
                        save_env_file(env_settings)
                        
                        # Save detailed email config to JSON file
                        email_config = {
                            'enabled': True,
                            'smtp_server': smtp_server,
                            'smtp_port': smtp_port,
                            'sender_email': new_email,
                            'sender_password': new_password,
                            'recipient_emails': recipient_emails,
                            'email_provider': email_provider
                        }
                        
                        try:
                            os.makedirs("data", exist_ok=True)
                            with open("data/email_config.json", 'w') as f:
                                json.dump(email_config, f, indent=2)
                            
                            st.success("✅ Email settings saved successfully!")
                            st.info(f"📬 {len(recipient_emails)} recipients configured")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Failed to save email config: {str(e)}")
                else:
                    st.error("❌ Please fill in both sender email and password")
        
        # Email test function
        st.divider()
        st.subheader("📧 Test Email Notification")
        
        # Load current email configuration
        try:
            with open("data/email_config.json", 'r') as f:
                email_config = json.load(f)
        except:
            email_config = {}
        
        current_recipients = email_config.get('recipient_emails', [])
        smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
        smtp_port = email_config.get('smtp_port', 587)
        
        if current_email and current_password and current_recipients:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Recipients:** {len(current_recipients)} configured")
                if len(current_recipients) <= 3:
                    for recipient in current_recipients:
                        st.write(f"📧 {recipient}")
                else:
                    for recipient in current_recipients[:2]:
                        st.write(f"📧 {recipient}")
                    st.write(f"📧 ... and {len(current_recipients) - 2} more")
                
            with col2:
                if st.button("🧪 Send Test Email", type="secondary"):
                    # Test email functionality to all recipients
                    try:
                        import smtplib
                        from email.mime.text import MIMEText
                        from email.mime.multipart import MIMEMultipart
                        
                        success_count = 0
                        failed_recipients = []
                        
                        with smtplib.SMTP(smtp_server, smtp_port) as server:
                            server.starttls()
                            server.login(current_email, current_password)
                            
                            for recipient in current_recipients:
                                try:
                                    msg = MIMEMultipart()
                                    msg['From'] = current_email
                                    msg['To'] = recipient
                                    msg['Subject'] = "🧪 Blockchain Monitor - Test Email"
                                    
                                    body = f"""
                                    <h2>✅ Email Test Successful!</h2>
                                    <p>This is a test email from your Blockchain Proposal Monitoring System.</p>
                                    
                                    <h3>📧 Configuration Details:</h3>
                                    <ul>
                                        <li><strong>Provider:</strong> {email_config.get('email_provider', 'Unknown')}</li>
                                        <li><strong>SMTP Server:</strong> {smtp_server}:{smtp_port}</li>
                                        <li><strong>Sender:</strong> {current_email}</li>
                                        <li><strong>Recipient:</strong> {recipient}</li>
                                        <li><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                                    </ul>
                                    
                                    <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                        <h4 style="color: #2c3e50;">✅ Configuration Status: Working Correctly</h4>
                                        <p>If you received this email, your blockchain proposal notification system is properly configured!</p>
                                    </div>
                                    
                                    <hr>
                                    <p style="color: #666; font-size: 12px;">
                                        This is an automated test message from your Blockchain Research & Monitoring System.
                                    </p>
                                    """
                                    
                                    msg.attach(MIMEText(body, 'html'))
                                    server.send_message(msg)
                                    success_count += 1
                                    
                                except Exception as e:
                                    failed_recipients.append(f"{recipient}: {str(e)}")
                        
                        # Show results
                        if success_count == len(current_recipients):
                            st.success(f"✅ Test emails sent successfully to all {success_count} recipients!")
                            st.info("Check your inbox for the test messages.")
                        elif success_count > 0:
                            st.warning(f"⚠️ {success_count}/{len(current_recipients)} emails sent successfully")
                            if failed_recipients:
                                with st.expander("❌ Failed Recipients"):
                                    for failure in failed_recipients:
                                        st.write(failure)
                        else:
                            st.error("❌ All email tests failed")
                            if failed_recipients:
                                with st.expander("❌ Error Details"):
                                    for failure in failed_recipients:
                                        st.write(failure)
                            
                    except Exception as e:
                        st.error(f"❌ Email test failed: {str(e)}")
                        
        elif not current_recipients:
            st.warning("⚠️ No recipient emails configured. Please add recipients in the Email Settings above.")
        else:
            st.warning("⚠️ Configure sender email and password first before testing")
    
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
            
            # Bot customization settings
            st.subheader("🤖 Bot Appearance")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Load current slack config for bot settings
                try:
                    with open("data/slack_config.json", 'r') as f:
                        slack_config = json.load(f)
                except:
                    slack_config = {}
                
                bot_username = st.text_input(
                    "Bot Username",
                    value=slack_config.get('username', 'Blockchain Research Agent'),
                    placeholder="Blockchain Monitor",
                    help="Name displayed for bot messages"
                )
                
            with col2:
                # Emoji selector for bot icon
                emoji_options = [
                    ":robot_face:", ":chart_with_upwards_trend:", ":bell:", 
                    ":chains:", ":diamond_shape_with_a_dot_inside:", ":gear:",
                    ":mag_right:", ":rocket:", ":zap:", ":warning:",
                    ":white_check_mark:", ":bangbang:", ":exclamation:",
                    ":computer:", ":link:", ":crystal_ball:"
                ]
                
                current_emoji = slack_config.get('icon_emoji', ':robot_face:')
                
                try:
                    emoji_index = emoji_options.index(current_emoji)
                except ValueError:
                    emoji_index = 0
                
                bot_icon_emoji = st.selectbox(
                    "Bot Icon",
                    emoji_options,
                    index=emoji_index,
                    help="Emoji icon for bot messages"
                )
            
            # Preview bot appearance
            if bot_username and bot_icon_emoji:
                st.markdown(f"**Preview:** {bot_icon_emoji} **{bot_username}** will send notifications to {new_channel}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save"):
                    if new_webhook:
                        if new_webhook.startswith('https://hooks.slack.com/'):
                            # Save to environment variables
                            env_settings = {
                                'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
                                'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4o'),
                                'openai_max_tokens': os.getenv('OPENAI_MAX_TOKENS', '1000'),
                                'openai_temperature': os.getenv('OPENAI_TEMPERATURE', '0.3'),
                                'sender_email': os.getenv('SENDER_EMAIL', ''),
                                'sender_password': os.getenv('SENDER_PASSWORD', ''),
                                'slack_webhook_url': new_webhook,
                                'slack_channel': new_channel
                            }
                            save_env_file(env_settings)
                            
                            # Save detailed Slack config to JSON file
                            detailed_slack_config = {
                                'enabled': True,
                                'webhook_url': new_webhook,
                                'channel': new_channel,
                                'username': bot_username,
                                'icon_emoji': bot_icon_emoji,
                                'setup_date': datetime.now().isoformat()
                            }
                            
                            try:
                                os.makedirs("data", exist_ok=True)
                                with open("data/slack_config.json", 'w') as f:
                                    json.dump(detailed_slack_config, f, indent=2)
                                
                                st.success("✅ Slack settings saved successfully!")
                                st.info(f"🤖 Bot: {bot_icon_emoji} {bot_username} → {new_channel}")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Failed to save Slack config: {str(e)}")
                                st.success("✅ Basic settings saved to environment!")
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
                        # Enhanced test with custom message and bot settings
                        try:
                            # Load current Slack config for bot appearance
                            try:
                                with open("data/slack_config.json", 'r') as f:
                                    slack_config = json.load(f)
                                bot_username = slack_config.get('username', 'Blockchain Research Agent')
                                bot_icon = slack_config.get('icon_emoji', ':robot_face:')
                            except:
                                bot_username = 'Blockchain Research Agent'
                                bot_icon = ':robot_face:'
                            
                            test_payload = {
                                "text": f"🔔 *Blockchain Monitor Test*",
                                "username": bot_username,
                                "icon_emoji": bot_icon,
                                "blocks": [
                                    {
                                        "type": "header",
                                        "text": {
                                            "type": "plain_text",
                                            "text": f"{bot_icon} Test Notification"
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
                                        "type": "section",
                                        "fields": [
                                            {
                                                "type": "mrkdwn",
                                                "text": f"*Bot:* {bot_icon} {bot_username}"
                                            },
                                            {
                                                "type": "mrkdwn",
                                                "text": f"*Channel:* {current_webhook.split('/')[-1] if current_webhook else 'Unknown'}"
                                            }
                                        ]
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

if __name__ == "__main__":
    render_settings_page()