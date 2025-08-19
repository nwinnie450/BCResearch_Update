# 🔑 How to Set OpenAI API Key - Step by Step

## 🎯 Quick Steps to Configure OpenAI API Key

### Step 1: Launch the Configuration UI
```bash
python simple_config_manager.py
```

You'll see this screen:
```
============================================================
BLOCKCHAIN NOTIFICATION SYSTEM CONFIGURATION
============================================================

OpenAI Configuration:
   API Key:       [Not Set]  # <-- This shows if no key is set
   Model:         gpt-3.5-turbo
   Max Tokens:    1000
   Temperature:   0.3

Configuration Options:
   1. Configure OpenAI API      # <-- SELECT THIS OPTION
   2. Configure Email Settings
   3. Configure Slack Settings
   4. Test All Configurations
   5. Save Configuration
   6. Exit

Select option (1-6): 
```

### Step 2: Choose Option 1 (Configure OpenAI API)
```
Type: 1
Press Enter
```

You'll see:
```
==================================================
OPENAI CONFIGURATION
==================================================

Current API Key: [Not Set]

Get your API key from: https://platform.openai.com/api-keys
Tip: API keys start with 'sk-' and are about 51 characters long

1. Update API Key          # <-- SELECT THIS
2. Advanced Settings
3. Back to Main Menu
Choice (1-3): 
```

### Step 3: Choose Option 1 (Update API Key)
```
Type: 1
Press Enter
```

You'll see:
```
Enter new OpenAI API Key (hidden): 
```

**🔐 IMPORTANT**: Your API key will be hidden as you type (for security)

### Step 4: Enter Your OpenAI API Key
```
Paste your API key here: sk-your-actual-key-here
Press Enter
```

The system will show:
```
New key: [SET] sk-yo***************************here
Save this API key? (y/N): 
```

### Step 5: Confirm and Save
```
Type: y
Press Enter
```

You'll see:
```
✅ OpenAI API Key saved!
```

### Step 6: Test the Configuration
Go back to main menu and select option 4:
```
4. Test All Configurations
```

You should see:
```
🧪 TESTING CONFIGURATION
==================================================

🤖 Testing OpenAI connection...
✅ OpenAI API: Connected and ready
```

## 🌐 Where to Get Your OpenAI API Key

### Step-by-Step to Get API Key:

1. **Go to OpenAI Platform**: https://platform.openai.com/api-keys

2. **Sign in** to your OpenAI account

3. **Click "Create new secret key"**

4. **Give it a name** (e.g., "Blockchain Notification System")

5. **Copy the key** - it starts with `sk-` and looks like:
   ```
   sk-1234567890abcdef1234567890abcdef1234567890abcd
   ```

6. **Paste it in the configuration manager** when prompted

## 🔍 Visual Guide

### Before Setting API Key:
```
OpenAI Configuration:
   API Key:       [Not Set]     # ❌ Not configured
   
System Status:
   OpenAI Ready:  [NO - Missing API Key]  # ❌ Not ready
```

### After Setting API Key:
```
OpenAI Configuration:
   API Key:       [SET] sk-12***************************cd  # ✅ Configured & Masked
   
System Status:
   OpenAI Ready:  [YES]  # ✅ Ready to use
```

## 🚀 Complete Configuration Flow

```bash
# 1. Start configuration
python simple_config_manager.py

# 2. In the UI:
Select option (1-6): 1                    # Configure OpenAI API
Choice (1-3): 1                          # Update API Key
Enter new OpenAI API Key (hidden): sk-your-key-here
Save this API key? (y/N): y              # Confirm save

# 3. Test it works:
Select option (1-6): 4                    # Test All Configurations
# Should show: ✅ OpenAI API: Connected and ready

# 4. Save to file:
Select option (1-6): 5                    # Save Configuration
# Saves to .env file securely

# 5. Exit:
Select option (1-6): 6                    # Exit
```

## 🛡️ Security Features

- **🔐 Hidden Input**: Your API key is never shown while typing
- **🎭 Masked Display**: Shows `sk-12***************************cd` format
- **💾 Secure Storage**: Saved to `.env` file (never committed to git)
- **🧪 Safe Testing**: Tests connection without exposing the key

## ❗ Troubleshooting

### "Invalid API key" Error
- Check if key starts with `sk-`
- Ensure no extra spaces or characters
- Verify key is active in OpenAI dashboard

### "OpenAI API: Not configured"
- Make sure you selected option 1, then option 1 again
- Confirm you typed 'y' to save the key
- Try running the configuration manager again

---

## 🎯 Ready to Configure?

**Run this command to start:**
```bash
python simple_config_manager.py
```

**Then follow**: Option 1 → Option 1 → Enter your API key → Type 'y' → Done! ✅