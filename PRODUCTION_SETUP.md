# 🚀 Production Deployment Guide

## 🔐 Secure API Key Configuration

### Option 1: Environment Variables (Recommended)

#### **Step 1: Create Production .env File**
```bash
# Copy the example and edit with your actual keys
cp .env.example .env

# Edit .env with your actual values
nano .env
```

#### **Step 2: Set Environment Variables**

**On Linux/MacOS:**
```bash
export OPENAI_API_KEY="sk-your-actual-openai-key-here"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**On Windows:**
```cmd
set OPENAI_API_KEY=sk-your-actual-openai-key-here
set SENDER_EMAIL=your-email@gmail.com
set SENDER_PASSWORD=your-app-password
set SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**On Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY = "sk-your-actual-openai-key-here"
$env:SENDER_EMAIL = "your-email@gmail.com"
$env:SENDER_PASSWORD = "your-app-password"
$env:SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Option 2: Docker Deployment

#### **Docker Compose with Secrets**
```yaml
version: '3.8'
services:
  blockchain-notifier:
    build: .
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key
      - SENDER_EMAIL_FILE=/run/secrets/sender_email
      - SENDER_PASSWORD_FILE=/run/secrets/sender_password
      - SLACK_WEBHOOK_URL_FILE=/run/secrets/slack_webhook
    secrets:
      - openai_api_key
      - sender_email
      - sender_password
      - slack_webhook
    restart: unless-stopped

secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt
  sender_email:
    file: ./secrets/sender_email.txt
  sender_password:
    file: ./secrets/sender_password.txt
  slack_webhook:
    file: ./secrets/slack_webhook.txt
```

### Option 3: Cloud Platform Deployment

#### **AWS (Using Parameter Store)**
```python
import boto3

def get_openai_key():
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name='/blockchain-notifier/openai-api-key',
        WithDecryption=True
    )
    return response['Parameter']['Value']
```

#### **Azure (Using Key Vault)**
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def get_openai_key():
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
    secret = client.get_secret("openai-api-key")
    return secret.value
```

#### **Google Cloud (Using Secret Manager)**
```python
from google.cloud import secretmanager

def get_openai_key():
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/your-project/secrets/openai-api-key/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

## 🎯 Current System Configuration

The system already supports environment variables! Check `services/unified_impact_analyzer.py`:

```python
def _load_env_file(self):
    """Load environment variables from .env file"""
    env_file = '.env'
    if os.path.exists(env_file):
        # Load from .env file
    
    # Also checks os.environ for OPENAI_API_KEY
    self.openai_api_key = os.getenv('OPENAI_API_KEY')
```

## 🔧 Production Deployment Steps

### **1. Secure Your API Keys**
```bash
# Create .env file (never commit this!)
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo ".env" >> .gitignore  # Ensure it's gitignored
```

### **2. Set Up System Service (Linux)**
```bash
# Create systemd service
sudo nano /etc/systemd/system/blockchain-notifier.service
```

```ini
[Unit]
Description=Blockchain Proposal Notifier
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/BlockChainResearch-Update
Environment=OPENAI_API_KEY=your-key-here
Environment=SENDER_EMAIL=your-email@gmail.com
Environment=SENDER_PASSWORD=your-app-password
Environment=SLACK_WEBHOOK_URL=your-webhook-url
ExecStart=/usr/bin/python3 start_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable blockchain-notifier
sudo systemctl start blockchain-notifier
sudo systemctl status blockchain-notifier
```

### **3. Monitor & Logs**
```bash
# View logs
sudo journalctl -u blockchain-notifier -f

# Check service status
sudo systemctl status blockchain-notifier
```

## 🛡️ Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** or cloud secret management
3. **Rotate keys regularly** (every 90 days)
4. **Monitor usage** in OpenAI dashboard
5. **Set spending limits** in OpenAI account
6. **Use least privilege access** for cloud deployments

## 📊 Cost Management

### **OpenAI API Usage Optimization**
- Current model: `gpt-3.5-turbo` (cost-effective)
- Token limits: 1000 max tokens per request
- Rate limiting: Built into the system
- Caching: AI results cached to avoid duplicate calls

### **Expected Costs**
- ~1000 proposals/day × $0.002/1K tokens ≈ $2-5/month
- Monitor via: https://platform.openai.com/usage

## 🚨 Troubleshooting

### **Common Issues:**
1. **"No API key found"** → Check environment variables
2. **"Rate limit exceeded"** → Implement exponential backoff
3. **"Invalid API key"** → Verify key is active in OpenAI dashboard

### **Debug Commands:**
```bash
# Test environment variables
python -c "import os; print('OpenAI Key:', os.getenv('OPENAI_API_KEY', 'NOT_SET')[:10] + '...')"

# Test notification system
python -c "from services.unified_impact_analyzer import UnifiedImpactAnalyzer; print('AI Available:', UnifiedImpactAnalyzer().ai_available)"
```

---

✅ **Your system is production-ready with secure API key management!**