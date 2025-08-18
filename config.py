"""
Configuration settings for Blockchain Research AI Agent
"""
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

# API Configuration
ANKR_API_KEY = os.getenv("ANKR_API_KEY", "")
ANKR_API_URL = "https://rpc.ankr.com/multichain"

# Application Settings
APP_TITLE = "Top 5 L1 Protocol Research Hub"
APP_DESCRIPTION = "AI-powered analysis of Ethereum, Base, Tron, BSC & Bitcoin"
VERSION = "2.0.0"

# Streamlit Configuration - Optimized for compact display
PAGE_CONFIG = {
    "page_title": APP_TITLE,
    "page_icon": "🔗",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        'Get Help': None,
        'Report a bug': None,
        'About': f"# {APP_TITLE}\n{APP_DESCRIPTION}"
    }
}

# Color Palette (from design spec)
COLORS = {
    "primary_blue": "#1E3A8A",
    "secondary_blue": "#3B82F6", 
    "light_blue": "#EFF6FF",
    "success_green": "#059669",
    "danger_red": "#DC2626",
    "warning_orange": "#D97706",
    "purple": "#7C3AED",
    "dark_gray": "#111827",
    "medium_gray": "#6B7280",
    "light_gray": "#F3F4F6",
    "white": "#FFFFFF"
}

# Focused Top 5 L1 Blockchain Protocols
BLOCKCHAIN_PROTOCOLS = {
    "ethereum": {
        "name": "Ethereum",
        "symbol": "ETH",
        "type": "Layer 1",
        "consensus": "Proof of Stake",
        "website": "https://ethereum.org",
        "description": "Leading smart contract platform"
    },
    "bitcoin": {
        "name": "Bitcoin",
        "symbol": "BTC",
        "type": "Layer 1",
        "consensus": "Proof of Work",
        "website": "https://bitcoin.org",
        "description": "Original digital currency"
    },
    "binance_smart_chain": {
        "name": "BNB Smart Chain",
        "symbol": "BNB",
        "type": "Layer 1", 
        "consensus": "Proof of Stake Authority",
        "website": "https://www.bnbchain.org",
        "description": "High-performance Binance ecosystem"
    },
    "tron": {
        "name": "Tron",
        "symbol": "TRX",
        "type": "Layer 1",
        "consensus": "Delegated Proof of Stake",
        "website": "https://tron.network",
        "description": "High-speed, low-cost transactions"
    },
    "base": {
        "name": "Base",
        "symbol": "ETH",
        "type": "Layer 2",
        "consensus": "Optimistic Rollup",
        "website": "https://base.org",
        "description": "Coinbase's Ethereum L2 solution"
    }
}

# Use Case Templates
USE_CASES = {
    "gaming": {
        "name": "Gaming & NFTs",
        "description": "High throughput, low latency, affordable transactions",
        "priorities": {"tps": 0.3, "latency": 0.25, "fees": 0.25, "security": 0.2},
        "min_requirements": {"tps": 1000, "max_fee": 0.1}
    },
    "smart_contracts": {
        "name": "Smart Contract Applications", 
        "description": "Security-first with mature tooling",
        "priorities": {"security": 0.4, "ecosystem": 0.3, "tools": 0.2, "fees": 0.1},
        "min_requirements": {"security_score": 8, "ecosystem_score": 80}
    },
    "enterprise": {
        "name": "Enterprise Solutions",
        "description": "Compliance, governance, and scalability",
        "priorities": {"governance": 0.3, "compliance": 0.25, "scalability": 0.25, "security": 0.2},
        "min_requirements": {"governance_score": 7, "compliance_rating": "B+"}
    },
    "payments": {
        "name": "Payments & Transfers",
        "description": "Fast, cheap, and reliable transactions", 
        "priorities": {"speed": 0.35, "fees": 0.35, "stability": 0.2, "adoption": 0.1},
        "min_requirements": {"finality_time": 10, "max_fee": 0.01}
    },
    "nft": {
        "name": "NFT Marketplace",
        "description": "Creator-friendly with rich ecosystem",
        "priorities": {"fees": 0.3, "ecosystem": 0.25, "tools": 0.25, "community": 0.2},
        "min_requirements": {"max_fee": 0.05, "nft_support": True}
    }
}

# Evaluation Parameters
EVALUATION_PARAMS = {
    "technical": [
        "tps", "latency", "finality_time", "block_size", 
        "smart_contracts", "programming_languages"
    ],
    "economic": [
        "transaction_fees", "gas_price", "staking_yield", 
        "inflation_rate", "market_cap", "trading_volume"
    ],
    "security": [
        "consensus_mechanism", "validator_count", "attack_resistance",
        "audit_history", "bug_bounty", "incident_history"  
    ],
    "ecosystem": [
        "dapp_count", "developer_activity", "tvl", "user_count",
        "community_size", "institutional_support"
    ],
    "governance": [
        "governance_model", "voting_mechanism", "proposal_process",
        "upgrade_mechanism", "decentralization_score"
    ]
}

# API Timeouts and Limits
API_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1,
    "cache_ttl": 300  # 5 minutes
}