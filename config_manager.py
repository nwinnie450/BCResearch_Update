#!/usr/bin/env python3
"""
Secure Configuration Manager
User-friendly interface to manage API keys and settings with masking
"""
import os
import json
import getpass
from pathlib import Path
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureConfigManager:
    """Secure configuration manager with API key masking"""
    
    def __init__(self):
        self.config_file = Path('data/secure_config.json')
        self.env_file = Path('.env')
        self.config_file.parent.mkdir(exist_ok=True)
        
    def _generate_key(self, password: str, salt: bytes) -> bytes:
        """Generate encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _encrypt_value(self, value: str, password: str) -> dict:
        """Encrypt a value with password"""
        salt = os.urandom(16)
        key = self._generate_key(password, salt)
        f = Fernet(key)
        encrypted = f.encrypt(value.encode())
        return {
            'encrypted': base64.b64encode(encrypted).decode(),
            'salt': base64.b64encode(salt).decode()
        }
    
    def _decrypt_value(self, encrypted_data: dict, password: str) -> str:
        """Decrypt a value with password"""
        salt = base64.b64decode(encrypted_data['salt'])
        key = self._generate_key(password, salt)
        f = Fernet(key)
        encrypted = base64.b64decode(encrypted_data['encrypted'])
        return f.decrypt(encrypted).decode()
    
    def mask_api_key(self, api_key: str) -> str:
        """Mask API key for display"""
        if not api_key:
            return "Not Set"
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
    
    def load_config(self) -> dict:
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_config(self, config: dict):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def update_env_file(self, settings: dict):
        """Update .env file with current settings"""
        env_lines = []
        env_lines.append("# Blockchain Notification System Configuration")
        env_lines.append(f"# Updated: {os.path.basename(__file__)}")
        env_lines.append("")
        
        env_lines.append("# OpenAI Configuration")
        env_lines.append(f"OPENAI_API_KEY={settings.get('openai_api_key', '')}")
        env_lines.append(f"OPENAI_MODEL={settings.get('openai_model', 'gpt-3.5-turbo')}")
        env_lines.append(f"OPENAI_MAX_TOKENS={settings.get('openai_max_tokens', '1000')}")
        env_lines.append(f"OPENAI_TEMPERATURE={settings.get('openai_temperature', '0.3')}")
        env_lines.append("")
        
        env_lines.append("# Email Configuration")
        env_lines.append(f"SENDER_EMAIL={settings.get('sender_email', '')}")
        env_lines.append(f"SENDER_PASSWORD={settings.get('sender_password', '')}")
        env_lines.append("SMTP_SERVER=smtp.gmail.com")
        env_lines.append("SMTP_PORT=587")
        env_lines.append("")
        
        env_lines.append("# Slack Configuration")
        env_lines.append(f"SLACK_WEBHOOK_URL={settings.get('slack_webhook_url', '')}")
        env_lines.append("SLACK_CHANNEL=#faws_testing")
        
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(env_lines))
    
    def display_current_settings(self):
        """Display current settings with masked sensitive data"""
        print("\n🔧 Current Configuration:")
        print("-" * 50)
        
        # Load from environment or config
        openai_key = os.getenv('OPENAI_API_KEY', '')
        sender_email = os.getenv('SENDER_EMAIL', '')
        sender_password = os.getenv('SENDER_PASSWORD', '')
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        
        print(f"📱 OpenAI API Key:    {self.mask_api_key(openai_key)}")
        print(f"📧 Sender Email:      {sender_email if sender_email else 'Not Set'}")
        print(f"🔑 Email Password:    {self.mask_api_key(sender_password)}")
        print(f"💬 Slack Webhook:     {self.mask_api_key(slack_webhook)}")
        print(f"🤖 OpenAI Model:      {os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')}")
        print(f"🎛️  Max Tokens:        {os.getenv('OPENAI_MAX_TOKENS', '1000')}")
        print(f"🌡️  Temperature:       {os.getenv('OPENAI_TEMPERATURE', '0.3')}")
        print()
    
    def configure_openai(self):
        """Configure OpenAI settings"""
        print("\n🤖 OpenAI Configuration:")
        print("-" * 30)
        
        current_key = os.getenv('OPENAI_API_KEY', '')
        print(f"Current API Key: {self.mask_api_key(current_key)}")
        
        change = input("Update OpenAI API Key? (y/N): ").strip().lower()
        if change == 'y':
            print("\n📝 Get your API key from: https://platform.openai.com/api-keys")
            new_key = getpass.getpass("Enter new OpenAI API Key (hidden): ").strip()
            
            if new_key:
                if not new_key.startswith('sk-'):
                    print("⚠️  Warning: OpenAI API keys usually start with 'sk-'")
                
                confirm = input(f"Confirm key: {self.mask_api_key(new_key)}? (y/N): ").strip().lower()
                if confirm == 'y':
                    os.environ['OPENAI_API_KEY'] = new_key
                    print("✅ OpenAI API Key updated")
                    return new_key
        
        return current_key
    
    def configure_email(self):
        """Configure email settings"""
        print("\n📧 Email Configuration:")
        print("-" * 25)
        
        current_email = os.getenv('SENDER_EMAIL', '')
        current_password = os.getenv('SENDER_PASSWORD', '')
        
        print(f"Current Email: {current_email if current_email else 'Not Set'}")
        print(f"Current Password: {self.mask_api_key(current_password)}")
        
        change = input("Update Email Configuration? (y/N): ").strip().lower()
        if change == 'y':
            new_email = input("Enter sender email: ").strip()
            if new_email:
                os.environ['SENDER_EMAIL'] = new_email
                print("✅ Email updated")
            
            print("\n🔑 For Gmail, use an App Password (not your regular password)")
            print("   Generate at: https://myaccount.google.com/apppasswords")
            new_password = getpass.getpass("Enter email app password (hidden): ").strip()
            if new_password:
                os.environ['SENDER_PASSWORD'] = new_password
                print("✅ Email password updated")
            
            return new_email, new_password
        
        return current_email, current_password
    
    def configure_slack(self):
        """Configure Slack settings"""
        print("\n💬 Slack Configuration:")
        print("-" * 25)
        
        current_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        print(f"Current Webhook: {self.mask_api_key(current_webhook)}")
        
        change = input("Update Slack Webhook? (y/N): ").strip().lower()
        if change == 'y':
            print("\n📝 Get webhook URL from your Slack app configuration")
            print("   Should start with: https://hooks.slack.com/services/...")
            new_webhook = input("Enter Slack webhook URL: ").strip()
            
            if new_webhook:
                if not new_webhook.startswith('https://hooks.slack.com/'):
                    print("⚠️  Warning: Slack webhooks usually start with 'https://hooks.slack.com/'")
                
                os.environ['SLACK_WEBHOOK_URL'] = new_webhook
                print("✅ Slack webhook updated")
                return new_webhook
        
        return current_webhook
    
    def test_configuration(self):
        """Test current configuration"""
        print("\n🧪 Testing Configuration:")
        print("-" * 30)
        
        try:
            # Test OpenAI
            from services.unified_impact_analyzer import UnifiedImpactAnalyzer
            analyzer = UnifiedImpactAnalyzer()
            
            if analyzer.ai_available:
                print("✅ OpenAI API: Connected")
            else:
                print("❌ OpenAI API: Not configured or invalid key")
            
            # Test notification services
            from services.unified_notification_service import UnifiedNotificationService
            service = UnifiedNotificationService()
            
            # Test email config
            email_config = service.load_config(service.email_config_file)
            if email_config.get('enabled') and os.getenv('SENDER_EMAIL'):
                print("✅ Email: Configured")
            else:
                print("⚠️  Email: Not fully configured")
            
            # Test Slack config
            slack_config = service.load_config(service.slack_config_file)
            if slack_config.get('enabled') and os.getenv('SLACK_WEBHOOK_URL'):
                print("✅ Slack: Configured")
            else:
                print("⚠️  Slack: Not fully configured")
            
        except Exception as e:
            print(f"❌ Configuration test error: {e}")
    
    def save_to_files(self):
        """Save current environment to .env file"""
        settings = {
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            'openai_model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            'openai_max_tokens': os.getenv('OPENAI_MAX_TOKENS', '1000'),
            'openai_temperature': os.getenv('OPENAI_TEMPERATURE', '0.3'),
            'sender_email': os.getenv('SENDER_EMAIL', ''),
            'sender_password': os.getenv('SENDER_PASSWORD', ''),
            'slack_webhook_url': os.getenv('SLACK_WEBHOOK_URL', '')
        }
        
        self.update_env_file(settings)
        print("✅ Configuration saved to .env file")
        
        # Ensure .env is in .gitignore
        gitignore_file = Path('.gitignore')
        if gitignore_file.exists():
            with open('.gitignore', 'r') as f:
                content = f.read()
            if '.env' not in content:
                with open('.gitignore', 'a') as f:
                    f.write('\n# Environment variables\n.env\n')
                print("✅ Added .env to .gitignore")
        else:
            with open('.gitignore', 'w') as f:
                f.write("# Environment variables\n.env\n")
            print("✅ Created .gitignore with .env")

def main():
    """Main configuration interface"""
    manager = SecureConfigManager()
    
    print("🔐 Secure Configuration Manager")
    print("=" * 40)
    print("Manage your API keys and settings securely")
    
    while True:
        manager.display_current_settings()
        
        print("Options:")
        print("1. Configure OpenAI API Key")
        print("2. Configure Email Settings")
        print("3. Configure Slack Settings")
        print("4. Test Configuration")
        print("5. Save Configuration")
        print("6. Exit")
        print()
        
        choice = input("Select option (1-6): ").strip()
        
        if choice == '1':
            manager.configure_openai()
        elif choice == '2':
            manager.configure_email()
        elif choice == '3':
            manager.configure_slack()
        elif choice == '4':
            manager.test_configuration()
        elif choice == '5':
            manager.save_to_files()
        elif choice == '6':
            print("\n👋 Configuration saved. Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()