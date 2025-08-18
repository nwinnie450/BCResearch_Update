#!/usr/bin/env python3
"""
Live Blockchain Data Service
Fetches real-time data from multiple reliable sources
"""
import requests
import time
from typing import Dict, Optional, Any
from datetime import datetime

class LiveBlockchainData:
    """Service to fetch live blockchain data from reliable APIs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 10
        
        # API endpoints
        self.apis = {
            'etherscan': 'https://api.etherscan.io/api',
            'coingecko': 'https://api.coingecko.com/api/v3',
            'coinmarketcap': 'https://pro-api.coinmarketcap.com/v1',
            'blockchain_info': 'https://api.blockchain.info',
            'trongrid': 'https://api.trongrid.io'
        }
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1.0  # seconds between requests
    
    def _rate_limit(self, api_key: str):
        """Simple rate limiting"""
        now = time.time()
        if api_key in self.last_request_time:
            time_since_last = now - self.last_request_time[api_key]
            if time_since_last < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time[api_key] = time.time()
    
    def get_ethereum_data(self) -> Dict[str, Any]:
        """Get comprehensive live Ethereum data"""
        try:
            # Get price from CoinGecko (free, reliable)
            price_data = self._get_coingecko_price('ethereum')
            
            # Get gas data from Etherscan (free with API key, or public endpoint)
            gas_data = self._get_etherscan_gas()
            
            # Combine data
            eth_data = {
                'name': 'Ethereum',
                'symbol': 'ETH',
                'price_usd': price_data.get('price_usd', 0),
                'price_change_24h': price_data.get('price_change_24h', 0),
                'market_cap': price_data.get('market_cap', 0),
                'volume_24h': price_data.get('volume_24h', 0),
                'avg_fee_usd': gas_data.get('avg_fee_usd', 0),
                'gas_price_gwei': gas_data.get('gas_price_gwei', 0),
                'tps': 15,  # Ethereum L1 actual TPS
                'finality_time': '12.8 minutes',  # Casper FFG finality
                'last_updated': datetime.now().isoformat()
            }
            
            return eth_data
            
        except Exception as e:
            print(f"Error fetching Ethereum data: {str(e)}")
            return self._get_ethereum_fallback()
    
    def _get_coingecko_price(self, coin_id: str) -> Dict[str, float]:
        """Get price data from CoinGecko"""
        try:
            self._rate_limit('coingecko')
            
            url = f"{self.apis['coingecko']}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if coin_id in data:
                    coin_data = data[coin_id]
                    return {
                        'price_usd': coin_data.get('usd', 0),
                        'price_change_24h': coin_data.get('usd_24h_change', 0),
                        'market_cap': coin_data.get('usd_market_cap', 0),
                        'volume_24h': coin_data.get('usd_24h_vol', 0)
                    }
        except Exception as e:
            print(f"Error fetching CoinGecko price for {coin_id}: {str(e)}")
        
        return {'price_usd': 0, 'price_change_24h': 0, 'market_cap': 0, 'volume_24h': 0}
    
    def _get_etherscan_gas(self) -> Dict[str, float]:
        """Get current Ethereum gas prices from Etherscan"""
        try:
            self._rate_limit('etherscan')
            
            # Try Etherscan gas oracle (free endpoint)
            url = self.apis['etherscan']
            params = {
                'module': 'gastracker',
                'action': 'gasoracle'
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1' and 'result' in data:
                    result = data['result']
                    
                    # Get standard gas price in gwei
                    gas_price_gwei = float(result.get('ProposeGasPrice', 0))
                    
                    # Calculate USD fee for standard transfer (21,000 gas)
                    # Current ETH price needed for conversion
                    eth_price = self._get_coingecko_price('ethereum')['price_usd']
                    
                    if gas_price_gwei > 0 and eth_price > 0:
                        # Gas cost in ETH = (gas_price_gwei * 1e-9) * 21000
                        gas_cost_eth = (gas_price_gwei * 1e-9) * 21000
                        fee_usd = gas_cost_eth * eth_price
                        
                        return {
                            'avg_fee_usd': fee_usd,
                            'gas_price_gwei': gas_price_gwei
                        }
        
        except Exception as e:
            print(f"Error fetching Etherscan gas data: {str(e)}")
        
        # Fallback: estimate based on current conditions
        return {
            'avg_fee_usd': 0.50,  # Current reasonable estimate
            'gas_price_gwei': 20   # Current reasonable estimate
        }
    
    def get_bitcoin_data(self) -> Dict[str, Any]:
        """Get live Bitcoin data"""
        try:
            # Get price from CoinGecko
            price_data = self._get_coingecko_price('bitcoin')
            
            # Bitcoin network data (these are relatively stable)
            btc_data = {
                'name': 'Bitcoin',
                'symbol': 'BTC',
                'price_usd': price_data.get('price_usd', 0),
                'price_change_24h': price_data.get('price_change_24h', 0),
                'market_cap': price_data.get('market_cap', 0),
                'volume_24h': price_data.get('volume_24h', 0),
                'avg_fee_usd': 2.50,  # Current typical fee
                'tps': 7,  # Bitcoin theoretical max
                'finality_time': '~60 minutes',
                'last_updated': datetime.now().isoformat()
            }
            
            return btc_data
            
        except Exception as e:
            print(f"Error fetching Bitcoin data: {str(e)}")
            return self._get_bitcoin_fallback()
    
    def get_tron_data(self) -> Dict[str, Any]:
        """Get live Tron data"""
        try:
            # Get price from CoinGecko
            price_data = self._get_coingecko_price('tron')
            
            trx_data = {
                'name': 'Tron',
                'symbol': 'TRX',
                'price_usd': price_data.get('price_usd', 0),
                'price_change_24h': price_data.get('price_change_24h', 0),
                'market_cap': price_data.get('market_cap', 0),
                'volume_24h': price_data.get('volume_24h', 0),
                'avg_fee_usd': 0.001,  # Tron's consistently low fees
                'tps': 2000,  # Tron's actual capacity
                'finality_time': '3 seconds',
                'last_updated': datetime.now().isoformat()
            }
            
            return trx_data
            
        except Exception as e:
            print(f"Error fetching Tron data: {str(e)}")
            return self._get_tron_fallback()
    
    def get_bsc_data(self) -> Dict[str, Any]:
        """Get live BSC data"""
        try:
            # Get BNB price from CoinGecko
            price_data = self._get_coingecko_price('binancecoin')
            
            bsc_data = {
                'name': 'Binance Smart Chain',
                'symbol': 'BNB',
                'price_usd': price_data.get('price_usd', 0),
                'price_change_24h': price_data.get('price_change_24h', 0),
                'market_cap': price_data.get('market_cap', 0),
                'volume_24h': price_data.get('volume_24h', 0),
                'avg_fee_usd': 0.30,  # Current BSC fees
                'tps': 2100,  # BSC capacity
                'finality_time': '3 seconds',
                'last_updated': datetime.now().isoformat()
            }
            
            return bsc_data
            
        except Exception as e:
            print(f"Error fetching BSC data: {str(e)}")
            return self._get_bsc_fallback()
    
    def get_base_data(self) -> Dict[str, Any]:
        """Get live Base data (uses ETH for price)"""
        try:
            # Base uses ETH, so get ETH price
            price_data = self._get_coingecko_price('ethereum')
            
            base_data = {
                'name': 'Base',
                'symbol': 'ETH',
                'price_usd': price_data.get('price_usd', 0),
                'price_change_24h': price_data.get('price_change_24h', 0),
                'market_cap': price_data.get('market_cap', 0),
                'volume_24h': price_data.get('volume_24h', 0),
                'avg_fee_usd': 0.15,  # Base L2 fees
                'tps': 350,  # Base capacity
                'finality_time': '2 seconds',
                'last_updated': datetime.now().isoformat()
            }
            
            return base_data
            
        except Exception as e:
            print(f"Error fetching Base data: {str(e)}")
            return self._get_base_fallback()
    
    def get_all_protocols_data(self) -> Dict[str, Dict[str, Any]]:
        """Get data for all supported protocols"""
        return {
            'ethereum': self.get_ethereum_data(),
            'bitcoin': self.get_bitcoin_data(),
            'tron': self.get_tron_data(),
            'binance_smart_chain': self.get_bsc_data(),
            'base': self.get_base_data()
        }
    
    def _get_ethereum_fallback(self) -> Dict[str, Any]:
        """Fallback Ethereum data with current estimates"""
        return {
            'name': 'Ethereum',
            'symbol': 'ETH',
            'price_usd': 4441.0,  # Updated to current price
            'price_change_24h': 0.0,
            'market_cap': 534000000000,
            'volume_24h': 15000000000,
            'avg_fee_usd': 0.50,  # Updated to current low fees
            'gas_price_gwei': 20,
            'tps': 15,
            'finality_time': '12.8 minutes',
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_bitcoin_fallback(self) -> Dict[str, Any]:
        """Fallback Bitcoin data"""
        return {
            'name': 'Bitcoin',
            'symbol': 'BTC',
            'price_usd': 107000.0,  # Updated estimate
            'price_change_24h': 0.0,
            'market_cap': 2100000000000,
            'volume_24h': 25000000000,
            'avg_fee_usd': 2.50,
            'tps': 7,
            'finality_time': '~60 minutes',
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_tron_fallback(self) -> Dict[str, Any]:
        """Fallback Tron data"""
        return {
            'name': 'Tron',
            'symbol': 'TRX',
            'price_usd': 0.30,  # Updated estimate
            'price_change_24h': 0.0,
            'market_cap': 26000000000,
            'volume_24h': 1500000000,
            'avg_fee_usd': 0.001,
            'tps': 2000,
            'finality_time': '3 seconds',
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_bsc_fallback(self) -> Dict[str, Any]:
        """Fallback BSC data"""
        return {
            'name': 'Binance Smart Chain',
            'symbol': 'BNB',
            'price_usd': 720.0,  # Updated estimate
            'price_change_24h': 0.0,
            'market_cap': 104000000000,
            'volume_24h': 2000000000,
            'avg_fee_usd': 0.30,
            'tps': 2100,
            'finality_time': '3 seconds',
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_base_fallback(self) -> Dict[str, Any]:
        """Fallback Base data"""
        return {
            'name': 'Base',
            'symbol': 'ETH',
            'price_usd': 4441.0,  # Same as ETH
            'price_change_24h': 0.0,
            'market_cap': 534000000000,
            'volume_24h': 500000000,
            'avg_fee_usd': 0.15,
            'tps': 350,
            'finality_time': '2 seconds',
            'last_updated': datetime.now().isoformat()
        }

# Global instance
live_blockchain_data = LiveBlockchainData()