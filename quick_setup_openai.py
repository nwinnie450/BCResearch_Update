#!/usr/bin/env python3
"""
Quick OpenAI API Key Setup
One-command setup for OpenAI configuration
"""
import os
import getpass
from pathlib import Path

def quick_openai_setup():
    """Quick setup for OpenAI API key only"""
    print("🔑 Quick OpenAI API Key Setup")
    print("=" * 40)
    
    # Check current status
    current_key = os.getenv('OPENAI_API_KEY', '')
    if current_key:
        masked = current_key[:4] + "*" * (len(current_key) - 8) + current_key[-4:] if len(current_key) > 8 else "*" * len(current_key)
        print(f"Current API Key: {masked}")
        
        update = input("Update existing API key? (y/N): ").strip().lower()
        if update != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📝 Get your API key from: https://platform.openai.com/api-keys")
    print("💡 API keys start with 'sk-' and are about 51 characters long")
    
    # Get API key
    while True:
        api_key = getpass.getpass("\n🔐 Enter your OpenAI API Key (hidden): ").strip()
        
        if not api_key:
            print("❌ No key entered. Please try again.")
            continue
            
        if not api_key.startswith('sk-'):
            confirm = input("⚠️  Key doesn't start with 'sk-'. Continue anyway? (y/N): ").strip().lower()
            if confirm != 'y':
                continue
        
        # Show masked version for confirmation
        masked = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "*" * len(api_key)
        print(f"\n✅ API Key: {masked}")
        
        confirm = input("Save this API key? (y/N): ").strip().lower()
        if confirm == 'y':
            break
    
    # Save to .env file
    env_file = Path('.env')
    env_content = []
    
    # Read existing .env if it exists
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if not line.strip().startswith('OPENAI_API_KEY='):
                    env_content.append(line.rstrip())
    else:
        env_content.append("# Blockchain Notification System Configuration")
        env_content.append("")
    
    # Add/update OpenAI key
    env_content.append(f"OPENAI_API_KEY={api_key}")
    
    # Add default OpenAI settings if not present
    has_model = any('OPENAI_MODEL=' in line for line in env_content)
    if not has_model:
        env_content.extend([
            "OPENAI_MODEL=gpt-3.5-turbo",
            "OPENAI_MAX_TOKENS=1000",
            "OPENAI_TEMPERATURE=0.3"
        ])
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write('\n'.join(env_content))
    
    print(f"✅ API key saved to {env_file}")
    
    # Update .gitignore
    gitignore_file = Path('.gitignore')
    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            content = f.read()
        if '.env' not in content:
            with open(gitignore_file, 'a') as f:
                f.write('\n# Environment variables\n.env\n')
            print("✅ Added .env to .gitignore")
    else:
        with open(gitignore_file, 'w') as f:
            f.write("# Environment variables\n.env\n")
        print("✅ Created .gitignore with .env")
    
    # Test the configuration
    print("\n🧪 Testing OpenAI connection...")
    try:
        os.environ['OPENAI_API_KEY'] = api_key
        from services.unified_impact_analyzer import UnifiedImpactAnalyzer
        
        analyzer = UnifiedImpactAnalyzer()
        if analyzer.ai_available:
            print("✅ OpenAI API: Connected and ready!")
            print("\n🎉 Setup complete! Your OpenAI API is configured.")
            print("🚀 Run the notification system with: python start_scheduler.py")
        else:
            print("❌ OpenAI API: Connection failed")
            print("   Please check your API key and try again")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("   The key was saved but couldn't be tested")

if __name__ == "__main__":
    quick_openai_setup()