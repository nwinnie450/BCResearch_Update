#!/usr/bin/env python3
"""
Simple Configuration Manager
User-friendly interface to manage API keys and settings with masking
No external dependencies required
"""
import os
import json
import getpass
from pathlib import Path

class SimpleConfigManager:
    """Simple configuration manager with API key masking"""
    
    def __init__(self):
        self.env_file = Path('.env')
        # Load existing environment from .env if it exists
        self._load_env_file()
        
    def _load_env_file(self):
        """Load environment variables from .env file"""
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key and value:
                                os.environ[key] = value
            except Exception as e:
                print(f"Warning: Could not load .env file: {e}")
    
    def mask_sensitive_data(self, value: str, reveal_chars: int = 4) -> str:
        """Mask sensitive data for display - shows first 4 and last 4 characters"""
        if not value:
            return "[Not Set]"
        if len(value) <= reveal_chars * 2:
            return "[SET] " + "*" * len(value)
        # Show first 4 and last 4 characters with stars in between
        return "[SET] " + value[:reveal_chars] + "*" * (len(value) - reveal_chars * 2) + value[-reveal_chars:]
    
    def display_current_settings(self):
        """Display current settings with masked sensitive data"""
        print("\n" + "="*60)
        print("BLOCKCHAIN NOTIFICATION SYSTEM CONFIGURATION")
        print("="*60)
        
        # OpenAI Settings
        openai_key = os.getenv('OPENAI_API_KEY', '')
        openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        max_tokens = os.getenv('OPENAI_MAX_TOKENS', '1000')
        temperature = os.getenv('OPENAI_TEMPERATURE', '0.3')
        
        print(f"\nOpenAI Configuration:")
        print(f"   API Key:       {self.mask_sensitive_data(openai_key)}")
        print(f"   Model:         {openai_model}")
        print(f"   Max Tokens:    {max_tokens}")
        print(f"   Temperature:   {temperature}")
        
        # Email Settings
        sender_email = os.getenv('SENDER_EMAIL', '')
        sender_password = os.getenv('SENDER_PASSWORD', '')
        
        print(f"\nEmail Configuration:")
        print(f"   Sender Email:  {sender_email if sender_email else '[Not Set]'}")
        print(f"   App Password:  {self.mask_sensitive_data(sender_password)}")
        
        # Slack Settings
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        slack_channel = os.getenv('SLACK_CHANNEL', '#faws_testing')
        
        print(f"\nSlack Configuration:")
        print(f"   Webhook URL:   {self.mask_sensitive_data(slack_webhook, 8)}")
        print(f"   Channel:       {slack_channel}")
        
        # Status indicators
        print(f"\nSystem Status:")
        print(f"   OpenAI Ready:  {'[YES]' if openai_key else '[NO - Missing API Key]'}")
        print(f"   Email Ready:   {'[YES]' if sender_email and sender_password else '[NO - Missing Config]'}")
        print(f"   Slack Ready:   {'[YES]' if slack_webhook else '[NO - Missing Webhook]'}")
        print()
    
    def configure_openai(self):
        """Configure OpenAI settings"""
        print("\n" + "="*50)
        print("🤖 OPENAI CONFIGURATION")
        print("="*50)
        
        current_key = os.getenv('OPENAI_API_KEY', '')
        
        print(f"Current API Key: {self.mask_sensitive_data(current_key)}")
        print("\n📝 Get your API key from: https://platform.openai.com/api-keys")
        print("💡 Tip: API keys start with 'sk-' and are about 51 characters long")
        
        while True:
            choice = input("\n1. Update API Key\n2. Advanced Settings\n3. Back to Main Menu\nChoice (1-3): ").strip()
            
            if choice == '1':
                new_key = getpass.getpass("\n🔑 Enter new OpenAI API Key (hidden): ").strip()
                
                if not new_key:
                    print("❌ No key entered")
                    continue
                    
                if not new_key.startswith('sk-'):
                    confirm = input("⚠️  Key doesn't start with 'sk-'. Continue anyway? (y/N): ").strip().lower()
                    if confirm != 'y':
                        continue
                
                print(f"✅ New key: {self.mask_sensitive_data(new_key)}")
                confirm = input("Save this API key? (y/N): ").strip().lower()
                if confirm == 'y':
                    os.environ['OPENAI_API_KEY'] = new_key
                    print("✅ OpenAI API Key saved!")
                    break
                    
            elif choice == '2':
                print("\n🎛️  Advanced OpenAI Settings:")
                
                model = input(f"Model (current: {os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')}): ").strip()
                if model:
                    os.environ['OPENAI_MODEL'] = model
                
                tokens = input(f"Max Tokens (current: {os.getenv('OPENAI_MAX_TOKENS', '1000')}): ").strip()
                if tokens:
                    os.environ['OPENAI_MAX_TOKENS'] = tokens
                
                temp = input(f"Temperature (current: {os.getenv('OPENAI_TEMPERATURE', '0.3')}): ").strip()
                if temp:
                    os.environ['OPENAI_TEMPERATURE'] = temp
                
                print("✅ Advanced settings updated!")
                
            elif choice == '3':
                break
            else:
                print("❌ Invalid choice")
    
    def configure_email(self):
        """Configure email settings"""
        print("\n" + "="*50)
        print("📧 EMAIL CONFIGURATION")
        print("="*50)
        
        current_email = os.getenv('SENDER_EMAIL', '')
        current_password = os.getenv('SENDER_PASSWORD', '')
        
        print(f"Current Email: {current_email if current_email else '❌ Not Set'}")
        print(f"Current Password: {self.mask_sensitive_data(current_password)}")
        
        print("\n📝 For Gmail setup:")
        print("   1. Enable 2-Factor Authentication")
        print("   2. Generate App Password at: https://myaccount.google.com/apppasswords")
        print("   3. Use the App Password (not your regular password)")
        
        while True:
            choice = input("\n1. Update Email Address\n2. Update App Password\n3. Back to Main Menu\nChoice (1-3): ").strip()
            
            if choice == '1':
                new_email = input("\n📧 Enter sender email address: ").strip()
                if new_email:
                    if '@' not in new_email:
                        print("⚠️  Invalid email format")
                        continue
                    os.environ['SENDER_EMAIL'] = new_email
                    print("✅ Email address saved!")
                    
            elif choice == '2':
                print("\n🔑 Enter your Gmail App Password:")
                print("   (This is NOT your regular Gmail password)")
                new_password = getpass.getpass("App Password (hidden): ").strip()
                if new_password:
                    if len(new_password) < 8:
                        print("⚠️  App passwords are usually longer")
                    os.environ['SENDER_PASSWORD'] = new_password
                    print("✅ Email password saved!")
                    
            elif choice == '3':
                break
            else:
                print("❌ Invalid choice")
    
    def configure_slack(self):
        """Configure Slack settings"""
        print("\n" + "="*50)
        print("💬 SLACK CONFIGURATION")
        print("="*50)
        
        current_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        
        print(f"Current Webhook: {self.mask_sensitive_data(current_webhook, 8)}")
        
        print("\n📝 To get your Slack webhook URL:")
        print("   1. Go to: https://api.slack.com/apps")
        print("   2. Create a new app or select existing")
        print("   3. Go to 'Incoming Webhooks' and activate")
        print("   4. Add webhook to workspace")
        print("   5. Copy the webhook URL")
        
        change = input("\nUpdate Slack webhook URL? (y/N): ").strip().lower()
        if change == 'y':
            new_webhook = input("\n🔗 Enter Slack webhook URL: ").strip()
            
            if not new_webhook:
                print("❌ No URL entered")
                return
                
            if not new_webhook.startswith('https://hooks.slack.com/'):
                confirm = input("⚠️  URL doesn't look like a Slack webhook. Continue? (y/N): ").strip().lower()
                if confirm != 'y':
                    return
            
            print(f"✅ New webhook: {self.mask_sensitive_data(new_webhook, 8)}")
            confirm = input("Save this webhook URL? (y/N): ").strip().lower()
            if confirm == 'y':
                os.environ['SLACK_WEBHOOK_URL'] = new_webhook
                print("✅ Slack webhook saved!")
    
    def test_configuration(self):
        """Test current configuration"""
        print("\n" + "="*50)
        print("🧪 TESTING CONFIGURATION")
        print("="*50)
        
        success_count = 0
        total_tests = 3
        
        # Test OpenAI
        print("\n🤖 Testing OpenAI connection...")
        try:
            from services.unified_impact_analyzer import UnifiedImpactAnalyzer
            analyzer = UnifiedImpactAnalyzer()
            
            if analyzer.ai_available:
                print("✅ OpenAI API: Connected and ready")
                success_count += 1
            else:
                print("❌ OpenAI API: Not configured or invalid key")
                print("   Check your API key in OpenAI configuration")
        except Exception as e:
            print(f"❌ OpenAI test error: {e}")
        
        # Test Email
        print("\n📧 Testing Email configuration...")
        try:
            sender_email = os.getenv('SENDER_EMAIL', '')
            sender_password = os.getenv('SENDER_PASSWORD', '')
            
            if sender_email and sender_password:
                print("✅ Email: Configuration complete")
                print(f"   Sender: {sender_email}")
                success_count += 1
            else:
                print("❌ Email: Missing configuration")
                if not sender_email:
                    print("   Missing: Sender email address")
                if not sender_password:
                    print("   Missing: App password")
        except Exception as e:
            print(f"❌ Email test error: {e}")
        
        # Test Slack
        print("\n💬 Testing Slack configuration...")
        try:
            slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
            
            if slack_webhook:
                # Try a simple ping to Slack
                import requests
                test_payload = {
                    "text": "🧪 Configuration test from Blockchain Notification System",
                    "username": "Config Test Bot"
                }
                
                response = requests.post(slack_webhook, json=test_payload, timeout=10)
                if response.status_code == 200:
                    print("✅ Slack: Webhook tested successfully!")
                    print("   Check your Slack channel for test message")
                    success_count += 1
                else:
                    print(f"❌ Slack: Webhook test failed (HTTP {response.status_code})")
            else:
                print("❌ Slack: Missing webhook URL")
        except Exception as e:
            print(f"❌ Slack test error: {e}")
        
        # Summary
        print(f"\n📊 Test Results: {success_count}/{total_tests} components configured correctly")
        
        if success_count == total_tests:
            print("🎉 All systems ready! Your notification system is fully configured.")
        else:
            print("⚠️  Some components need configuration. Check the errors above.")
    
    def save_configuration(self):
        """Save current configuration to .env file"""
        print("\n💾 Saving configuration to .env file...")
        
        env_content = []
        env_content.append("# Blockchain Notification System Configuration")
        env_content.append(f"# Generated by {os.path.basename(__file__)}")
        env_content.append("")
        
        env_content.append("# OpenAI Configuration")
        env_content.append(f"OPENAI_API_KEY={os.getenv('OPENAI_API_KEY', '')}")
        env_content.append(f"OPENAI_MODEL={os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')}")
        env_content.append(f"OPENAI_MAX_TOKENS={os.getenv('OPENAI_MAX_TOKENS', '1000')}")
        env_content.append(f"OPENAI_TEMPERATURE={os.getenv('OPENAI_TEMPERATURE', '0.3')}")
        env_content.append("")
        
        env_content.append("# Email Configuration")
        env_content.append(f"SENDER_EMAIL={os.getenv('SENDER_EMAIL', '')}")
        env_content.append(f"SENDER_PASSWORD={os.getenv('SENDER_PASSWORD', '')}")
        env_content.append("SMTP_SERVER=smtp.gmail.com")
        env_content.append("SMTP_PORT=587")
        env_content.append("")
        
        env_content.append("# Slack Configuration")
        env_content.append(f"SLACK_WEBHOOK_URL={os.getenv('SLACK_WEBHOOK_URL', '')}")
        env_content.append(f"SLACK_CHANNEL={os.getenv('SLACK_CHANNEL', '#faws_testing')}")
        
        try:
            with open(self.env_file, 'w') as f:
                f.write('\n'.join(env_content))
            print("✅ Configuration saved to .env file")
            
            # Ensure .env is in .gitignore
            gitignore_file = Path('.gitignore')
            gitignore_content = ""
            
            if gitignore_file.exists():
                with open(gitignore_file, 'r') as f:
                    gitignore_content = f.read()
            
            if '.env' not in gitignore_content:
                with open(gitignore_file, 'a') as f:
                    f.write('\n# Environment variables\n.env\n')
                print("✅ Added .env to .gitignore for security")
                
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")

def main():
    """Main configuration interface"""
    manager = SimpleConfigManager()
    
    print("BLOCKCHAIN NOTIFICATION SYSTEM")
    print("Secure Configuration Manager")
    print("No external dependencies required")
    
    while True:
        manager.display_current_settings()
        
        print("Configuration Options:")
        print("   1. Configure OpenAI API")
        print("   2. Configure Email Settings")
        print("   3. Configure Slack Settings")
        print("   4. Test All Configurations")
        print("   5. Save Configuration")
        print("   6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            manager.configure_openai()
        elif choice == '2':
            manager.configure_email()
        elif choice == '3':
            manager.configure_slack()
        elif choice == '4':
            manager.test_configuration()
        elif choice == '5':
            manager.save_configuration()
        elif choice == '6':
            print("\nConfiguration complete. Your settings are ready!")
            print("Run the notification system with: python start_scheduler.py")
            break
        else:
            print("❌ Invalid option. Please choose 1-6.")
        
        if choice != '6':
            input("\n⏸️  Press Enter to continue...")

if __name__ == "__main__":
    main()