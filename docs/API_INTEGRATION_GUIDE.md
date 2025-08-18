# API Integration Guide
## BlockChain Research & Advisory AI Agent - Real-Time Data APIs

**Last Updated**: August 17, 2025  
**Version**: 2.0 (Enhanced API Integration)  
**Technical Lead**: Data Engineering Team  
**Status**: Production Ready

---

## 🎯 **API Integration Overview**

The BlockChain Research & Advisory AI Agent features a sophisticated API integration system that seamlessly scales from free APIs to premium institutional-grade data sources. The system provides intelligent fallbacks, cost optimization, and enhanced accuracy through multiple API providers.

### **Integration Architecture**
- **Multi-Tier API Support**: Free → Basic → Professional → Enterprise
- **Intelligent Fallback**: Automatic degradation to available APIs
- **Smart Cost Management**: Optimized API usage to minimize costs
- **Enhanced Accuracy**: Premium APIs provide real-time data with ±0.1% accuracy

---

## 🔧 **Supported API Providers**

### **Market Data APIs**

#### **1. CoinGecko Pro API** ⭐⭐⭐⭐⭐
**Best for**: Real-time market data with highest accuracy

```python
# Configuration
COINGECKO_API_KEY=your_coingecko_pro_key_here

# Features
- Real-time price data (30-second updates)
- Comprehensive market metrics
- 10,000 requests/month
- ±0.1% price accuracy
- Historical data access
```

**Endpoints Used**:
```python
# Premium real-time prices
GET https://pro-api.coingecko.com/api/v3/simple/price
Headers: {"x-cg-pro-api-key": "your_key"}

# Market data with volume
GET https://pro-api.coingecko.com/api/v3/coins/{id}
```

**Integration Code**:
```python
def _fetch_coingecko_pro_data(self) -> Dict[str, Any]:
    headers = {'x-cg-pro-api-key': self.api_keys['coingecko_pro']}
    url = f"{self.premium_apis['coingecko_pro']['base_url']}/simple/price"
    
    params = {
        'ids': 'ethereum,bitcoin,tron,binancecoin',
        'vs_currencies': 'usd',
        'include_24hr_change': 'true',
        'include_market_cap': 'true',
        'include_24hr_vol': 'true',
        'include_last_updated_at': 'true'
    }
    
    response = self.session.get(url, headers=headers, params=params)
    return response.json()
```

#### **2. CoinMarketCap Pro API** ⭐⭐⭐⭐
**Best for**: Institutional-grade market data

```python
# Configuration
COINMARKETCAP_API_KEY=your_cmc_api_key_here

# Features
- Professional market data
- Real-time cryptocurrency listings
- 10,000 requests/month (Basic plan)
- Institutional data quality
- Advanced market metrics
```

**Endpoints Used**:
```python
# Latest cryptocurrency quotes
GET https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest
Headers: {"X-CMC_PRO_API_KEY": "your_key"}

# Market cap rankings
GET https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest
```

### **Network Data APIs**

#### **1. Etherscan Pro API** ⭐⭐⭐⭐⭐
**Best for**: Real-time Ethereum network data

```python
# Configuration
ETHERSCAN_API_KEY=your_etherscan_api_key_here

# Features
- Live gas price tracking
- Real-time network statistics
- 100,000 requests/day
- Official Ethereum data
- Transaction analysis
```

**Critical Endpoints**:
```python
# Real-time gas oracle
GET https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={key}

# Network statistics  
GET https://api.etherscan.io/api?module=stats&action=ethsupply&apikey={key}

# Block information
GET https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey={key}
```

**Live Gas Price Integration**:
```python
def _fetch_etherscan_pro_data(self) -> Dict[str, Any]:
    api_key = self.api_keys['etherscan']
    base_url = self.premium_apis['etherscan']['base_url']
    
    # Get current gas prices
    gas_response = self.session.get(
        f"{base_url}?module=gastracker&action=gasoracle&apikey={api_key}"
    )
    
    if gas_response.status_code == 200:
        gas_data = gas_response.json()
        gas_price = float(gas_data['result']['ProposeGasPrice'])
        
        # Calculate USD fee (21000 gas * gas price * ETH price)
        eth_price = self._get_current_eth_price()
        fee_usd = (gas_price * 1e-9 * 21000) * eth_price
        
        return {
            'name': 'Ethereum',
            'tps': 15.0,
            'avg_fee_usd': fee_usd,
            'gas_price_gwei': gas_price,
            'finality_time': '12.8 minutes',
            'data_source': 'etherscan_pro'
        }
```

#### **2. BSCScan Pro API** ⭐⭐⭐⭐
**Best for**: Real-time BSC network data

```python
# Configuration
BSCSCAN_API_KEY=your_bscscan_api_key_here

# Features
- BNB Smart Chain network data
- Real-time transaction monitoring
- 100,000 requests/day
- Official BSC statistics
- DeFi protocol tracking
```

#### **3. Moralis API** ⭐⭐⭐⭐
**Best for**: Multi-chain data aggregation

```python
# Configuration
MORALIS_API_KEY=your_moralis_api_key_here

# Features
- Multi-chain support
- DeFi protocol data
- NFT market data
- 40,000 requests/month
- Real-time webhooks
```

**Multi-Chain Integration**:
```python
# Moralis multi-chain data
headers = {"X-API-Key": self.api_keys['moralis']}
base_url = "https://deep-index.moralis.io/api/v2"

# Get chain statistics
chains = ['eth', 'bsc', 'polygon']
for chain in chains:
    response = self.session.get(f"{base_url}/stats/{chain}", headers=headers)
```

### **Infrastructure APIs**

#### **1. Alchemy API** ⭐⭐⭐⭐⭐
**Best for**: Enterprise blockchain infrastructure

```python
# Configuration
ALCHEMY_API_KEY=your_alchemy_api_key_here

# Features
- Enhanced blockchain APIs
- Real-time network access
- 300M compute units/month
- Webhook notifications
- Advanced filtering
```

#### **2. Infura API** ⭐⭐⭐⭐
**Best for**: Reliable blockchain access

```python
# Configuration
INFURA_API_KEY=your_infura_api_key_here

# Features
- Reliable blockchain infrastructure
- Multi-chain support
- 100,000 requests/day
- IPFS integration
- Global CDN
```

---

## 🛠️ **Implementation Guide**

### **Environment Setup**

#### **Method 1: Environment Variables (.env)**
```bash
# Create .env file in project root
# Market Data APIs
COINGECKO_API_KEY=cg-pro-12345678901234567890
COINMARKETCAP_API_KEY=12345678-1234-1234-1234-123456789012

# Network Data APIs
ETHERSCAN_API_KEY=YourEtherscanAPIKeyToken
BSCSCAN_API_KEY=YourBSCScanAPIKeyToken
MORALIS_API_KEY=12345678901234567890123456789012

# Infrastructure APIs
ALCHEMY_API_KEY=12345678901234567890123456789012
INFURA_API_KEY=12345678901234567890123456789012
```

#### **Method 2: Streamlit Secrets (.streamlit/secrets.toml)**
```toml
# For Streamlit Cloud deployment
[api_keys]
COINGECKO_API_KEY = "cg-pro-12345678901234567890"
ETHERSCAN_API_KEY = "YourEtherscanAPIKeyToken"
BSCSCAN_API_KEY = "YourBSCScanAPIKeyToken"
MORALIS_API_KEY = "12345678901234567890123456789012"
```

#### **Method 3: System Environment Variables**
```bash
# Windows
setx COINGECKO_API_KEY "cg-pro-12345678901234567890"
setx ETHERSCAN_API_KEY "YourEtherscanAPIKeyToken"

# Linux/macOS
export COINGECKO_API_KEY="cg-pro-12345678901234567890"
export ETHERSCAN_API_KEY="YourEtherscanAPIKeyToken"
```

### **API Service Integration**

#### **Enhanced API Service Class**
```python
# services/enhanced_api_service.py
class EnhancedAPIService:
    def __init__(self):
        self.session = requests.Session()
        self.api_keys = self._load_api_keys()
        
        # API endpoint configuration
        self.premium_apis = {
            'coingecko_pro': {
                'base_url': 'https://pro-api.coingecko.com/api/v3',
                'rate_limit': 10000,
                'features': ['real_time_prices', 'historical_data']
            },
            'etherscan': {
                'base_url': 'https://api.etherscan.io/api',
                'rate_limit': 100000,
                'features': ['gas_prices', 'network_stats']
            }
        }
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment or Streamlit secrets"""
        api_keys = {}
        
        key_mappings = {
            'COINGECKO_API_KEY': 'coingecko_pro',
            'ETHERSCAN_API_KEY': 'etherscan',
            'BSCSCAN_API_KEY': 'bscscan',
            'MORALIS_API_KEY': 'moralis'
        }
        
        for env_var, service in key_mappings.items():
            # Try environment variable first
            key = os.getenv(env_var)
            
            # Try Streamlit secrets if available
            if not key and hasattr(st, 'secrets'):
                try:
                    key = st.secrets.get(env_var)
                except:
                    pass
            
            if key:
                api_keys[service] = key
        
        return api_keys
```

#### **Intelligent API Selection**
```python
def get_enhanced_market_data(self) -> Dict[str, Any]:
    """Smart API selection with fallback strategy"""
    
    # Priority 1: CoinGecko Pro (highest accuracy)
    if 'coingecko_pro' in self.api_keys:
        try:
            return self._fetch_coingecko_pro_data()
        except Exception as e:
            logger.warning(f"CoinGecko Pro failed: {e}")
    
    # Priority 2: CoinMarketCap Pro
    if 'coinmarketcap' in self.api_keys:
        try:
            return self._fetch_coinmarketcap_data()
        except Exception as e:
            logger.warning(f"CoinMarketCap failed: {e}")
    
    # Priority 3: Free APIs (fallback)
    return self._fetch_free_market_data()
```

### **Rate Limiting & Cost Management**

#### **Smart Rate Limiting**
```python
class APIRateLimiter:
    def __init__(self):
        self.request_counts = {}
        self.last_reset = {}
        self.limits = {
            'coingecko_pro': {'limit': 10000, 'window': 2592000},  # monthly
            'etherscan': {'limit': 100000, 'window': 86400},       # daily
            'free_apis': {'limit': 100, 'window': 86400}           # daily
        }
    
    def can_make_request(self, api_name: str) -> bool:
        """Check if API request is within rate limits"""
        now = time.time()
        limit_config = self.limits.get(api_name, {})
        
        if api_name not in self.request_counts:
            self.request_counts[api_name] = 0
            self.last_reset[api_name] = now
        
        # Reset counter if window expired
        if now - self.last_reset[api_name] > limit_config.get('window', 86400):
            self.request_counts[api_name] = 0
            self.last_reset[api_name] = now
        
        return self.request_counts[api_name] < limit_config.get('limit', 100)
    
    def record_request(self, api_name: str):
        """Record an API request"""
        self.request_counts[api_name] = self.request_counts.get(api_name, 0) + 1
```

#### **Cost Optimization**
```python
def optimize_api_usage(self):
    """Optimize API usage to minimize costs"""
    
    # Use caching to reduce API calls
    cache_ttl_by_data_type = {
        'market_data': 300,      # 5 minutes (high frequency)
        'network_stats': 600,    # 10 minutes (medium frequency)
        'proposals': 3600,       # 1 hour (low frequency)
    }
    
    # Batch requests when possible
    def batch_market_requests(coin_ids: List[str]):
        """Batch multiple coin requests into single API call"""
        batched_ids = ','.join(coin_ids)
        return self._fetch_multiple_coins(batched_ids)
    
    # Use cheaper APIs for less critical data
    def get_data_with_cost_optimization(data_type: str):
        if data_type == 'basic_prices':
            return self._use_free_api()  # Good enough for basic needs
        elif data_type == 'trading_decisions':
            return self._use_premium_api()  # Critical accuracy needed
```

---

## 📊 **API Monitoring & Analytics**

### **Real-Time API Status Dashboard**

#### **API Health Monitoring**
```python
class APIHealthMonitor:
    def __init__(self):
        self.health_status = {}
        self.response_times = {}
        self.error_rates = {}
    
    def check_api_health(self, api_name: str) -> Dict[str, Any]:
        """Check API endpoint health"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.api_endpoints[api_name]}/ping")
            response_time = time.time() - start_time
            
            self.health_status[api_name] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response_time,
                'last_check': datetime.now().isoformat(),
                'status_code': response.status_code
            }
            
        except Exception as e:
            self.health_status[api_name] = {
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
        
        return self.health_status[api_name]
```

#### **Usage Analytics**
```python
def get_api_usage_analytics(self) -> Dict[str, Any]:
    """Get comprehensive API usage analytics"""
    
    return {
        'daily_usage': self._get_daily_usage_stats(),
        'cost_analysis': self._calculate_monthly_costs(),
        'performance_metrics': self._get_performance_stats(),
        'rate_limit_status': self._get_rate_limit_status(),
        'recommendations': self._get_optimization_recommendations()
    }

def _calculate_monthly_costs(self) -> Dict[str, float]:
    """Calculate estimated monthly API costs"""
    usage_stats = self._get_usage_stats()
    
    cost_per_request = {
        'coingecko_pro': 99.0 / 10000,     # $99/10K requests
        'coinmarketcap': 333.0 / 10000,    # $333/10K requests
        'etherscan': 99.0 / 100000,        # $99/100K requests
        'free_apis': 0.0                   # Free
    }
    
    monthly_costs = {}
    for api_name, requests in usage_stats.items():
        cost_per = cost_per_request.get(api_name, 0)
        monthly_costs[api_name] = requests * cost_per
    
    return monthly_costs
```

### **Performance Optimization**

#### **Caching Strategy**
```python
class IntelligentCaching:
    def __init__(self):
        self.cache = {}
        self.cache_stats = {'hits': 0, 'misses': 0}
    
    def get_cached_data(self, cache_key: str, ttl: int) -> Optional[Any]:
        """Get data from cache if still valid"""
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < ttl:
                self.cache_stats['hits'] += 1
                return data
        
        self.cache_stats['misses'] += 1
        return None
    
    def cache_data(self, cache_key: str, data: Any):
        """Store data in cache with timestamp"""
        self.cache[cache_key] = (data, time.time())
    
    def get_cache_efficiency(self) -> float:
        """Calculate cache hit rate"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        return self.cache_stats['hits'] / total_requests if total_requests > 0 else 0
```

---

## 🔐 **Security & Best Practices**

### **API Key Security**

#### **Secure Storage**
```python
# Environment variable validation
def validate_api_key_format(api_key: str, provider: str) -> bool:
    """Validate API key format for security"""
    patterns = {
        'coingecko_pro': r'^cg-pro-[a-f0-9]{32}$',
        'etherscan': r'^[A-Z0-9]{34}$',
        'coinmarketcap': r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
    }
    
    pattern = patterns.get(provider)
    return bool(re.match(pattern, api_key)) if pattern else True

# Secure key loading
def load_api_keys_securely():
    """Load API keys with validation and error handling"""
    api_keys = {}
    
    for env_var, provider in key_mappings.items():
        key = os.getenv(env_var)
        if key:
            if validate_api_key_format(key, provider):
                api_keys[provider] = key
            else:
                logger.warning(f"Invalid API key format for {provider}")
    
    return api_keys
```

#### **Error Handling**
```python
def secure_api_request(self, url: str, **kwargs) -> Optional[Dict]:
    """Make API request with security measures"""
    try:
        # Add timeout and retry logic
        response = self.session.get(url, timeout=30, **kwargs)
        response.raise_for_status()
        
        # Validate response data
        data = response.json()
        if not self._validate_response_data(data):
            raise ValueError("Invalid response data structure")
        
        return data
        
    except requests.exceptions.Timeout:
        logger.error("API request timeout")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            logger.error("API authentication failed - check key")
        elif e.response.status_code == 429:
            logger.warning("API rate limit exceeded")
        return None
    except Exception as e:
        logger.error(f"Unexpected API error: {str(e)}")
        return None
```

### **Production Security Checklist**

#### **API Key Management**
- [ ] API keys stored in environment variables, not code
- [ ] API key format validation implemented
- [ ] Separate keys for development/staging/production
- [ ] Key rotation schedule established (quarterly)
- [ ] Access logs monitored for unusual activity

#### **Network Security**
- [ ] HTTPS/TLS encryption for all API calls
- [ ] Request timeouts configured (30 seconds max)
- [ ] Rate limiting implemented to prevent abuse
- [ ] Error messages sanitized (no key exposure)
- [ ] API endpoint validation and whitelisting

#### **Data Security**
- [ ] Response data validation and sanitization
- [ ] No sensitive data logged or cached
- [ ] Secure cache storage with encryption
- [ ] Regular security audits of API usage
- [ ] Incident response plan for key compromise

---

## 🚀 **Advanced Features**

### **Webhook Integration**

#### **Real-Time Notifications**
```python
class WebhookManager:
    def __init__(self):
        self.webhook_endpoints = {}
        self.active_subscriptions = {}
    
    def setup_price_alerts(self, thresholds: Dict[str, float]):
        """Setup price movement alerts via webhooks"""
        for coin, threshold in thresholds.items():
            webhook_url = f"https://api.moralis.io/streams/evm"
            webhook_config = {
                'chains': ['eth', 'bsc'],
                'description': f'Price alert for {coin}',
                'tag': f'price_alert_{coin}',
                'includeContractLogs': True,
                'webhookUrl': 'https://your-app.com/webhook/price-alert'
            }
            
            response = requests.post(
                webhook_url,
                headers={'X-API-Key': self.api_keys['moralis']},
                json=webhook_config
            )
```

### **Historical Data Analysis**

#### **Trend Analysis**
```python
def get_historical_trends(self, coin_id: str, days: int = 30) -> Dict[str, Any]:
    """Get historical price and volume trends"""
    
    if 'coingecko_pro' in self.api_keys:
        url = f"{self.premium_apis['coingecko_pro']['base_url']}/coins/{coin_id}/market_chart"
        params = {'vs_currency': 'usd', 'days': days}
        headers = {'x-cg-pro-api-key': self.api_keys['coingecko_pro']}
        
        response = self.session.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            
            # Calculate trends
            prices = [point[1] for point in data['prices']]
            volumes = [point[1] for point in data['total_volumes']]
            
            return {
                'price_trend': self._calculate_trend(prices),
                'volume_trend': self._calculate_trend(volumes),
                'volatility': self._calculate_volatility(prices),
                'support_resistance': self._find_support_resistance(prices)
            }
```

### **Custom Analytics**

#### **Protocol Performance Scoring**
```python
def calculate_protocol_score(self, protocol_data: Dict[str, Any]) -> float:
    """Calculate comprehensive protocol performance score"""
    
    # Weight different metrics
    weights = {
        'tps': 0.25,           # Transaction throughput
        'fees': 0.25,          # Cost efficiency (inverse)
        'finality': 0.15,      # Speed (inverse)
        'market_cap': 0.15,    # Market adoption
        'proposals': 0.10,     # Development activity
        'tvl': 0.10           # DeFi ecosystem
    }
    
    # Normalize metrics (0-100 scale)
    normalized_scores = {
        'tps': min(protocol_data.get('tps', 0) / 2000 * 100, 100),
        'fees': max(100 - (protocol_data.get('avg_fee_usd', 100) * 10), 0),
        'finality': self._normalize_finality_score(protocol_data.get('finality_time')),
        'market_cap': self._normalize_market_cap(protocol_data.get('market_cap', 0)),
        'proposals': self._normalize_proposal_activity(protocol_data.get('proposal_count', 0)),
        'tvl': self._normalize_tvl(protocol_data.get('tvl', 0))
    }
    
    # Calculate weighted score
    total_score = sum(normalized_scores[metric] * weights[metric] 
                     for metric in weights.keys())
    
    return round(total_score, 2)
```

---

## 📋 **API Integration Checklist**

### **Setup Phase**
- [ ] API keys obtained from all required providers
- [ ] Environment variables configured correctly
- [ ] API key format validation implemented
- [ ] Rate limiting configured for each provider
- [ ] Fallback strategy implemented for API failures

### **Testing Phase**
- [ ] All API endpoints tested successfully
- [ ] Rate limiting tested with burst requests
- [ ] Error handling tested with invalid keys
- [ ] Fallback mechanisms tested with API outages
- [ ] Performance benchmarks established

### **Production Phase**
- [ ] Monitoring and alerting configured
- [ ] Cost tracking and budgets established
- [ ] Security audit completed
- [ ] Documentation updated with all configurations
- [ ] Team training completed on API management

### **Maintenance Phase**
- [ ] Regular API health checks scheduled
- [ ] Cost optimization reviews (monthly)
- [ ] API key rotation schedule (quarterly)
- [ ] Performance monitoring and tuning
- [ ] New API provider evaluation (annually)

---

## 📞 **Support & Troubleshooting**

### **Common Issues**

#### **API Authentication Failures**
```bash
# Test API key validity
curl -H "x-cg-pro-api-key: YOUR_KEY" \
  "https://pro-api.coingecko.com/api/v3/ping"

# Expected response: {"gecko_says":"(V3) To the Moon!"}
```

#### **Rate Limit Exceeded**
```python
# Monitor rate limit status
def check_rate_limits():
    for api_name, limit_info in self.limits.items():
        current_usage = self.request_counts.get(api_name, 0)
        limit = limit_info['limit']
        percentage = (current_usage / limit) * 100
        
        if percentage > 80:
            logger.warning(f"{api_name} at {percentage}% of rate limit")
```

#### **API Endpoint Downtime**
```python
# Health check with automated fallback
def health_check_with_fallback():
    for api_name in ['coingecko_pro', 'coinmarketcap', 'free_apis']:
        if self._test_api_health(api_name):
            return api_name
    
    raise Exception("All API providers unavailable")
```

### **Performance Optimization**
- **Caching**: Implement intelligent caching with appropriate TTLs
- **Batching**: Combine multiple requests where possible
- **Async Requests**: Use asyncio for concurrent API calls
- **Connection Pooling**: Reuse HTTP connections

### **Cost Management**
- **Usage Monitoring**: Track API calls and costs daily
- **Budget Alerts**: Set up alerts at 80% of monthly budget
- **Provider Comparison**: Regularly evaluate cost/performance ratios
- **Optimization Reviews**: Monthly reviews of API usage patterns

---

*This comprehensive API integration guide provides everything needed to implement, monitor, and optimize the enhanced real-time data capabilities of the BlockChain Research & Advisory AI Agent.*