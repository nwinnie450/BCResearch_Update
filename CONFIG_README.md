# 🔐 Secure Configuration Setup

## Quick Start

### 🎯 Option 1: Interactive Configuration Manager (Recommended)
```bash
python simple_config_manager.py
```

This launches a user-friendly interface where you can:
- ✅ **Set OpenAI API Key** (with secure masking)
- ✅ **Configure Email Settings** (Gmail app passwords)
- ✅ **Set up Slack Webhooks** (for notifications)
- ✅ **Test All Configurations** (verify everything works)
- ✅ **Save Settings Securely** (to .env file)

### 🔧 Option 2: Manual .env Setup
```bash
# Copy the example file
cp .env.example .env

# Edit with your actual values
nano .env
```

## 🔑 API Key Sources

### OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Create new secret key
3. Copy the key (starts with `sk-`)
4. Paste in configuration manager

### Gmail App Password
1. Enable 2-Factor Authentication on Gmail
2. Go to: https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"
4. Use this password (NOT your regular Gmail password)

### Slack Webhook URL
1. Go to: https://api.slack.com/apps
2. Create new app or select existing
3. Enable "Incoming Webhooks"
4. Add webhook to workspace
5. Copy webhook URL

## 🛡️ Security Features

### ✅ API Key Masking
All sensitive data is masked when displayed:
```
OpenAI API Key: [SET] sk-1*****************************************abcd
Email Password: [SET] abcd********efgh
Slack Webhook:  [SET] hook*********************************3456
```

### ✅ Environment Variables
- API keys stored in `.env` file (never committed)
- `.env` automatically added to `.gitignore`
- Environment variables loaded at runtime

### ✅ Secure Testing
- Test connections without exposing keys
- Validate configuration before production
- Safe error handling for invalid keys

## 🚀 Production Deployment

### Step 1: Configure
```bash
python simple_config_manager.py
```

### Step 2: Test
```bash
# Test configuration
python simple_config_manager.py
# Choose option 4: "Test All Configurations"
```

### Step 3: Deploy
```bash
# Start the notification system
python start_scheduler.py
```

## 🔍 Configuration Status

Run the configuration manager to see current status:

```
BLOCKCHAIN NOTIFICATION SYSTEM CONFIGURATION
============================================================

OpenAI Configuration:
   API Key:       [SET] sk-1*****************************************abcd
   Model:         gpt-3.5-turbo
   Max Tokens:    1000
   Temperature:   0.3

Email Configuration:
   Sender Email:  your-email@gmail.com
   App Password:  [SET] abcd********efgh

Slack Configuration:
   Webhook URL:   [SET] hook*********************************3456
   Channel:       #faws_testing

System Status:
   OpenAI Ready:  [YES]
   Email Ready:   [YES]
   Slack Ready:   [YES]
```

## 🐛 Troubleshooting

### "OpenAI API: Not configured"
- Check if API key starts with `sk-`
- Verify key is active in OpenAI dashboard
- Check for any extra spaces or characters

### "Email: Missing configuration"
- Use Gmail App Password, not regular password
- Enable 2-Factor Authentication first
- Check sender email format

### "Slack: Missing webhook"
- Ensure webhook URL starts with `https://hooks.slack.com/`
- Verify webhook is active in Slack app settings
- Test webhook with a simple message

## 🎯 Best Practices

1. **Never commit .env files** to version control
2. **Use app passwords** for Gmail (not regular passwords)
3. **Test configurations** before production deployment
4. **Rotate API keys** regularly (every 90 days)
5. **Monitor usage** in OpenAI dashboard
6. **Set spending limits** to avoid unexpected costs

## 💰 Cost Management

### OpenAI Usage Optimization
- Using `gpt-3.5-turbo` (cost-effective)
- Limited to 1000 tokens per request
- Cached results to avoid duplicate calls
- Expected cost: ~$2-5/month for typical usage

### Monitor Costs
- OpenAI Dashboard: https://platform.openai.com/usage
- Set spending limits in account settings
- Review usage patterns monthly

---

✅ **Your blockchain notification system is ready for secure production deployment!**