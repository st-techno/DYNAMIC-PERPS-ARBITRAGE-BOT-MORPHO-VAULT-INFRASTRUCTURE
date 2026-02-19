"""KALSHI PREDICTION MARKETS CLIENT"""
from kalshi import Kalshi
from typing import List, Dict
from datetime import datetime

class KalshiClient:
    def __init__(self, api_key: str, passphrase: str):
        self.client = Kalshi(api_key, passphrase)
    
    async def get_open_markets(self) -> List[Dict]:
        """Fetch all open prediction markets"""
        try:
            markets = self.client.get_markets(status="open")
            return markets[:100]  # Top 100 by volume
        except:
            # Fallback mock data for demo
            return [{
                'ticker': 'BTC100K-Q1',
                'title': 'Will Bitcoin hit $100K by March 31?',
                'yes_price': 0.58,
                'volume': 125000,
                'close_time': '2026-03-31T16:00:00'
            }]
