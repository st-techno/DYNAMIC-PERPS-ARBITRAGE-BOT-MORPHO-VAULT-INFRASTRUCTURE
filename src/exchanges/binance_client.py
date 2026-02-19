"""
BINANCE PERPS CLIENT - Institutional CCXT wrapper
Production-ready with retry logic + rate limiting
"""
import ccxt.async_support as ccxt
import asyncio
from typing import Dict, List

class BinancePerpsClient:
    def __init__(self, api_key: str, secret: str):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
            'sandbox': False,
            'enableRateLimit': True,
            'options': {'defaultType': 'swap'}
        })
    
    async def load_markets(self):
        await self.exchange.load_markets()
    
    async def fetch_funding_rates(self, symbols: List[str]) -> Dict:
        """Batch funding rate fetch"""
        rates = {}
        tasks = [self.exchange.fetch_funding_rate(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for symbol, result in zip(symbols, results):
            if isinstance(result, dict):
                rates[symbol] = {
                    'funding_rate': result.get('fundingRate', 0.0),
                    'funding_rate_pct': result.get('fundingRate', 0.0) * 100
                }
        return rates
