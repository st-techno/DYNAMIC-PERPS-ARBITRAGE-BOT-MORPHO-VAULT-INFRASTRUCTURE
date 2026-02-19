"""INSTITUTIONAL CIRCUIT BREAKERS + RISK MANAGEMENT"""
import time
from typing import Dict

class InstitutionalCircuitBreaker:
    def __init__(self, config: Dict):
        self.config = config
        self.daily_pnl = 0.0
        self.consecutive_losses = 0
        self.last_reset = time.time()
    
    def is_healthy(self) -> bool:
        """Multi-layered institutional risk checks"""
        # Daily PnL reset
        if time.time() - self.last_reset > 86400:
            self.daily_pnl = 0.0
            self.last_reset = time.time()
        
        # Volatility breaker (mock)
        btc_vol = 0.02  # From real-time feed
        if abs(btc_vol) > 0.06:
            return False
        
        # Daily loss limit
        if self.daily_pnl < -self.config['capital_base'] * 0.10:
            return False
        
        return True
