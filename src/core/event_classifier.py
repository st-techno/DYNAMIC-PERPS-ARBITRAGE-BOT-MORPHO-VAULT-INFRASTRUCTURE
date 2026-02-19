"""
AI-POWERED EVENT CLASSIFICATION ENGINE
Maps ANY event to BTC/ETH/SOL relevance dynamically
"""
from typing import Dict
from datetime import datetime, timedelta

class EventRelevanceClassifier:
    def __init__(self):
        self.btc_keywords = {
            'bitcoin', 'btc', 'crypto', 'fed', 'election', 'inflation', 'recession'
        }
        self.eth_keywords = {
            'ethereum', 'eth', 'defi', 'nft', 'staking', 'rollup'
        }
        self.sol_keywords = {
            'solana', 'sol', 'pump', 'memecoin', 'raydium'
        }
    
    def classify_event(self, title: str, expiry_days: int = 30) -> Dict[str, float]:
        """Dynamic relevance scoring 0.0-1.0"""
        title_lower = title.lower()
        scores = {'BTC': 0.0, 'ETH': 0.0, 'SOL': 0.0}
        
        time_weight = min(1.0, expiry_days / 30)
        
        btc_hits = sum(1 for kw in self.btc_keywords if kw in title_lower)
        eth_hits = sum(1 for kw in self.eth_keywords if kw in title_lower)
        sol_hits = sum(1 for kw in self.sol_keywords if kw in title_lower)
        
        scores['BTC'] = min(1.0, btc_hits * 0.25 * time_weight)
        scores['ETH'] = min(1.0, eth_hits * 0.25 * time_weight)
        scores['SOL'] = min(1.0, sol_hits * 0.25 * time_weight)
        
        return scores
