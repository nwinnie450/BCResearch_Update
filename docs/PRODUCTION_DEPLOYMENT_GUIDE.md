# Production Deployment Guide
## BlockChain Research & Advisory AI Agent - Real-Time Data Enhanced

**Last Updated**: August 17, 2025  
**Version**: 2.0 (Real-Time Data Production)  
**DevOps Lead**: Infrastructure Team  
**Status**: Production Ready

---

## 🚀 **Deployment Overview**

### **System Requirements**
- **Python**: 3.9+ (Recommended: 3.11)
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: 1GB for application, 5GB+ for data caching
- **Network**: Stable internet connection for API calls
- **CPU**: 2+ cores recommended for concurrent users

### **Supported Platforms**
- ✅ **Streamlit Cloud** (Recommended for quick deployment)
- ✅ **Heroku** (Easy scaling, good for MVP)
- ✅ **AWS EC2** (Full control, enterprise-grade)
- ✅ **Google Cloud Run** (Serverless, cost-effective)
- ✅ **Digital Ocean Droplets** (Simple, affordable)
- ✅ **Local Development** (Windows, macOS, Linux)

---

## 📦 **Pre-Deployment Checklist**

### **1. Code Repository Setup**
```bash
# Clone repository
git clone https://github.com/your-org/blockchain-research-ai
cd blockchain-research-ai

# Verify all files present
ls -la
# Should include: app.py, requirements.txt, components/, services/, data/
```

### **2. Dependencies Verification**
```bash
# Install dependencies
pip install -r requirements.txt

# Verify core imports
python -c "
import streamlit as st
from services.comprehensive_realtime_data_service import comprehensive_realtime_service
from services.enhanced_ai_service import enhanced_ai_service
print('✅ All core dependencies verified')
"
```

### **3. Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### **4. Initial Data Setup**
```bash
# Ensure data directory exists
mkdir -p data

# Verify proposal data files (optional - will be created by scrapers)
ls data/
# Should include: eips.json, tips.json, bips.json, beps.json (if available)
```

---

## 🔧 **Configuration Management**

### **Required Environment Variables**
```bash
# Basic Configuration
STREAMLIT_ENV=production
PYTHONPATH=.

# API Keys (Optional - system works without them)
COINGECKO_API_KEY=your_coingecko_pro_key_here
ETHERSCAN_API_KEY=your_etherscan_api_key_here
BSCSCAN_API_KEY=your_bscscan_api_key_here
MORALIS_API_KEY=your_moralis_api_key_here
COINMARKETCAP_API_KEY=your_cmc_api_key_here
ALCHEMY_API_KEY=your_alchemy_api_key_here
INFURA_API_KEY=your_infura_api_key_here

# Optional: Custom Configuration
DATA_REFRESH_INTERVAL=300    # 5 minutes
CACHE_TTL=3600              # 1 hour
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30          # seconds
```

### **Streamlit Configuration (.streamlit/config.toml)**
```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#627EEA"
backgroundColor = "#FAFAFA"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#111827"

[client]
caching = true
```

### **Secrets Management (.streamlit/secrets.toml)**
```toml
# Production secrets (DO NOT commit to repository)
COINGECKO_API_KEY = "your_production_key_here"
ETHERSCAN_API_KEY = "your_production_key_here"
BSCSCAN_API_KEY = "your_production_key_here"
MORALIS_API_KEY = "your_production_key_here"
```

---

## 🌐 **Platform-Specific Deployments**

### **1. Streamlit Cloud Deployment** ⭐ (Recommended)

#### **Setup Steps**
1. **Repository Setup**
   ```bash
   # Push to GitHub
   git add .
   git commit -m "Production ready - Real-time data enhanced"
   git push origin main
   ```

2. **Streamlit Cloud Configuration**
   - Visit: https://share.streamlit.io/
   - Connect GitHub repository
   - Select branch: `main`
   - Main file: `app.py`
   - Python version: `3.11`

3. **Environment Variables**
   ```
   # In Streamlit Cloud dashboard > App settings > Secrets
   COINGECKO_API_KEY = "your_key_here"
   ETHERSCAN_API_KEY = "your_key_here"
   # Add other API keys as needed
   ```

4. **Advanced Settings**
   ```toml
   # Advanced settings in Streamlit Cloud
   [server]
   maxUploadSize = 200
   enableStaticServing = true
   ```

#### **Monitoring**
- **App URL**: https://your-app-name.streamlit.app/
- **Logs**: Available in Streamlit Cloud dashboard
- **Metrics**: Built-in usage analytics

### **2. Heroku Deployment**

#### **Setup Files**
```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Create runtime.txt
echo "python-3.11.5" > runtime.txt

# Create app.json for easy deployment
cat > app.json << 'EOF'
{
  "name": "Blockchain Research AI Agent",
  "description": "Real-time blockchain data analysis with AI",
  "keywords": ["blockchain", "ai", "streamlit", "real-time"],
  "website": "https://github.com/your-org/blockchain-research-ai",
  "repository": "https://github.com/your-org/blockchain-research-ai",
  "env": {
    "COINGECKO_API_KEY": {
      "description": "CoinGecko Pro API key for enhanced market data",
      "required": false
    },
    "ETHERSCAN_API_KEY": {
      "description": "Etherscan Pro API key for Ethereum data",
      "required": false
    }
  },
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
EOF
```

#### **Deployment Commands**
```bash
# Install Heroku CLI and login
heroku login

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set COINGECKO_API_KEY=your_key_here
heroku config:set ETHERSCAN_API_KEY=your_key_here

# Deploy
git add .
git commit -m "Heroku deployment ready"
git push heroku main

# Open app
heroku open
```

#### **Scaling**
```bash
# Scale dynos
heroku ps:scale web=1

# Upgrade to hobby dyno (for always-on)
heroku dyno:type web=hobby
```

### **3. AWS EC2 Deployment**

#### **EC2 Instance Setup**
```bash
# Launch EC2 instance (Ubuntu 22.04 LTS)
# Instance type: t3.medium (2 vCPU, 4GB RAM)
# Security group: Allow HTTP (80), HTTPS (443), SSH (22)

# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Install Nginx (for reverse proxy)
sudo apt install nginx -y
```

#### **Application Setup**
```bash
# Clone repository
git clone https://github.com/your-org/blockchain-research-ai
cd blockchain-research-ai

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export COINGECKO_API_KEY="your_key_here"
export ETHERSCAN_API_KEY="your_key_here"

# Test application
streamlit run app.py --server.port 8501
```

#### **Production Configuration**
```bash
# Create systemd service
sudo tee /etc/systemd/system/blockchain-ai.service > /dev/null << 'EOF'
[Unit]
Description=Blockchain Research AI Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/blockchain-research-ai
Environment=PATH=/home/ubuntu/blockchain-research-ai/venv/bin
Environment=COINGECKO_API_KEY=your_key_here
Environment=ETHERSCAN_API_KEY=your_key_here
ExecStart=/home/ubuntu/blockchain-research-ai/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable blockchain-ai
sudo systemctl start blockchain-ai
sudo systemctl status blockchain-ai
```

#### **Nginx Configuration**
```bash
# Create Nginx config
sudo tee /etc/nginx/sites-available/blockchain-ai > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/blockchain-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **4. Docker Deployment**

#### **Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Start application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### **Docker Compose**
```yaml
version: '3.8'

services:
  blockchain-ai:
    build: .
    ports:
      - "8501:8501"
    environment:
      - COINGECKO_API_KEY=${COINGECKO_API_KEY}
      - ETHERSCAN_API_KEY=${ETHERSCAN_API_KEY}
      - BSCSCAN_API_KEY=${BSCSCAN_API_KEY}
      - MORALIS_API_KEY=${MORALIS_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - blockchain-ai
    restart: unless-stopped
```

#### **Deployment Commands**
```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f blockchain-ai

# Scale if needed
docker-compose up --scale blockchain-ai=3 -d
```

---

## 🔒 **Security Configuration**

### **SSL/HTTPS Setup**
```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **Environment Security**
```bash
# Secure environment file permissions
chmod 600 .env
chmod 600 .streamlit/secrets.toml

# Never commit secrets to repository
echo ".env" >> .gitignore
echo ".streamlit/secrets.toml" >> .gitignore
```

### **API Rate Limiting**
```python
# In app configuration
MAX_REQUESTS_PER_MINUTE = 60
MAX_CONCURRENT_USERS = 100
API_TIMEOUT = 30
```

---

## 📊 **Monitoring & Logging**

### **Application Monitoring**
```python
# Health check endpoint (built into Streamlit)
# Available at: /_stcore/health

# Custom monitoring
import psutil
import time

def get_system_metrics():
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'timestamp': time.time()
    }
```

### **Log Configuration**
```python
# In app.py
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
```

### **External Monitoring Tools**
- **Uptime Monitoring**: UptimeRobot, Pingdom
- **Performance**: New Relic, DataDog
- **Error Tracking**: Sentry
- **Analytics**: Google Analytics, Mixpanel

---

## 🔄 **Backup & Recovery**

### **Data Backup Strategy**
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/blockchain-ai-$DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup data files
cp -r data/ $BACKUP_DIR/
cp -r .streamlit/ $BACKUP_DIR/
cp .env $BACKUP_DIR/

# Compress backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR/
rm -rf $BACKUP_DIR/

# Upload to cloud storage (optional)
# aws s3 cp $BACKUP_DIR.tar.gz s3://your-backup-bucket/
```

### **Recovery Procedures**
```bash
# Restore from backup
tar -xzf backup-20250817.tar.gz
cp -r blockchain-ai-20250817/data/ ./
cp -r blockchain-ai-20250817/.streamlit/ ./
cp blockchain-ai-20250817/.env ./

# Restart application
sudo systemctl restart blockchain-ai
```

---

## 🚀 **Performance Optimization**

### **Caching Strategy**
```python
# Streamlit caching
@st.cache_data(ttl=300)  # 5 minutes
def get_market_data():
    return comprehensive_realtime_service.get_comprehensive_data(['market_data'])

@st.cache_resource
def load_ai_service():
    return enhanced_ai_service
```

### **API Optimization**
```python
# Request pooling and optimization
import asyncio
import aiohttp

# Concurrent API requests
async def fetch_all_data():
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_market_data(session),
            fetch_network_data(session),
            fetch_proposals_data(session)
        ]
        return await asyncio.gather(*tasks)
```

### **Resource Management**
```bash
# Memory optimization
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# CPU optimization
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=50

# Network optimization
export STREAMLIT_SERVER_ENABLE_STATIC_SERVING=true
```

---

## 📋 **Deployment Checklist**

### **Pre-Deployment**
- [ ] All dependencies installed and tested
- [ ] Environment variables configured
- [ ] API keys tested (if available)
- [ ] SSL certificates configured
- [ ] Backup strategy implemented
- [ ] Monitoring tools configured

### **Deployment**
- [ ] Application successfully deployed
- [ ] Health checks passing
- [ ] All features functional without API keys
- [ ] Enhanced features working with API keys
- [ ] Performance within acceptable limits
- [ ] Logs showing no critical errors

### **Post-Deployment**
- [ ] User acceptance testing completed
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Monitoring alerts configured
- [ ] Backup verification completed
- [ ] Disaster recovery plan tested

---

## 🆘 **Troubleshooting Guide**

### **Common Issues**

#### **Application Won't Start**
```bash
# Check Python version
python --version

# Check dependencies
pip list | grep streamlit

# Check logs
journalctl -u blockchain-ai -f
```

#### **API Keys Not Working**
```python
# Test API key configuration
from services.enhanced_api_service import enhanced_api_service
status = enhanced_api_service.get_api_status()
print(f"Configured APIs: {status['configured_apis']}")
```

#### **Memory Issues**
```bash
# Check memory usage
free -h
ps aux | grep streamlit

# Restart application
sudo systemctl restart blockchain-ai
```

#### **Network Connectivity**
```bash
# Test API endpoints
curl -I "https://api.coingecko.com/api/v3/ping"
curl -I "https://api.etherscan.io/api"
```

### **Performance Issues**
```bash
# Monitor resource usage
htop
iotop
netstat -an | grep 8501

# Check Streamlit performance
streamlit run app.py --server.enableStaticServing=true
```

---

## 📞 **Support & Maintenance**

### **Regular Maintenance Tasks**
- **Weekly**: Check logs for errors, monitor API usage
- **Monthly**: Update dependencies, security patches
- **Quarterly**: Performance review, capacity planning
- **Annually**: Security audit, disaster recovery testing

### **Support Contacts**
- **Technical Issues**: DevOps Team
- **API Questions**: Data Engineering Team  
- **Performance Issues**: Infrastructure Team
- **Security Concerns**: Security Team

---

*This deployment guide provides comprehensive instructions for deploying the BlockChain Research & Advisory AI Agent with enhanced real-time data capabilities across multiple platforms. The system is production-ready and optimized for reliability, performance, and security.*