"""
CORE ARBITRAGE ENGINE - All trading decisions here
Dynamic event discovery → Perps arbitrage → Execution
"""
import asyncio
import json
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import redis
import numpy as np

from ..exchanges.binance_client import BinancePerpsClient
from ..exchanges.kalshi_client import KalshiClient
from ..defi.morpho_vaults import MorphoVaultInfrastructure
from .event_classifier import EventRelevanceClassifier
from .risk_manager import InstitutionalCircuitBreaker
from ..oversight.telegram_controller import InstitutionalHumanOversight

logger = logging.getLogger(__name__)

@dataclass
class DynamicEvent:
    event_id: str
    title: str
    category: str
    expiry: datetime
    kalshi_prob: float
    avg_prob: float
    volume_usd: float
    relevance_score: float
    perps_symbol: str

@dataclass
class ArbOpportunity:
    event: DynamicEvent
    perps_symbol: str
    divergence_pct: float
    expected_profit_usd: float
    position_size_usd: float
    confidence_score: float
    opp_id: str

class CompleteInstitutionalArbitrageBot:
    def __init__(self, config: Dict):
        self.config = config
        self.state = "STOPPED"
        self.positions = {}
        self.active_events = {}
        self.perps_cache = {}
        
        # Initialize components
        self.event_classifier = EventRelevanceClassifier()
        self.circuit_breaker = InstitutionalCircuitBreaker(config)
        self.vault_manager = MorphoVaultInfrastructure()
        self.redis_client = redis.from_url(config['redis_url'])
        
        # Exchange clients
        self.binance = None
        self.kalshi_client = None
        self.human_oversight = None
        
    async def initialize_trading_infrastructure(self):
        """Bootstrap all institutional infrastructure"""
        self.binance = BinancePerpsClient(
            self.config['binance_api_key'],
            self.config['binance_secret']
        )
        self.kalshi_client = KalshiClient(
            self.config['kalshi_api_key'],
            self.config['kalshi_passphrase']
        )
        
        self.human_oversight = InstitutionalHumanOversight(
            self.config['telegram_token'],
            self.config['telegram_chat_id'],
            self
        )
        
        self.vaults = await self.vault_manager.deploy_vaults(self.config['capital_base'])
        
        await self.binance.load_markets()
        logger.info("✅ COMPLETE INSTITUTIONAL INFRASTRUCTURE READY")
    
    async def discover_live_events(self) -> List[DynamicEvent]:
        """DYNAMIC EVENT DISCOVERY ENGINE"""
        events = []
        try:
            markets = await self.kalshi_client.get_open_markets()
            
            for market in markets[:50]:  # Top 50 by volume
                expiry = datetime.fromisoformat(market['close_time'])
                if expiry < datetime.now() + timedelta(days=90):
                    continue
                    
                scores = self.event_classifier.classify_event(market['title'])
                max_score = max(scores.values())
                
                if max_score >= self.config['min_relevance_score']:
                    event = DynamicEvent(
                        event_id=market['ticker'],
                        title=market['title'],
                        category=self._classify_category(market['title']),
                        expiry=expiry,
                        kalshi_prob=float(market['yes_price']),
                        avg_prob=float(market['yes_price']),
                        volume_usd=float(market['volume']),
                        relevance_score=max_score,
                        perps_symbol=self._map_event_to_perps(scores)
                    )
                    events.append(event)
            
            events.sort(key=lambda e: e.relevance_score * e.volume_usd, reverse=True)
            return events[:15]
            
        except Exception as e:
            logger.error(f"Event discovery failed: {e}")
            return []
    
    async def main_trading_cycle(self):
        """30-SECOND INSTITUTIONAL CYCLE"""
        cycle_start = time.time()
        
        # Circuit breaker check
        if not self.circuit_breaker.is_healthy():
            return
        
        # 1. Discover events
        events = await self.discover_live_events()
        
        # 2. Fetch perps data
        symbols = list(set(e.perps_symbol for e in events))
        self.perps_cache = await self.binance.fetch_funding_rates(symbols)
        
        # 3. Detect opportunities
        opportunities = self._detect_arbitrage_opportunities(events)
        
        # 4. Human review (top 3)
        for opp in opportunities[:3]:
            self.human_oversight.pending_opportunities[opp.opp_id] = opp
        
        cycle_time = time.time() - cycle_start
        logger.info(f"Cycle: {len(events)} events → {len(opportunities)} opps ({cycle_time:.1f}s)")
    
    async def institutional_main_loop(self):
        """24/7 PRODUCTION LOOP"""
        self.state = "RUNNING"
        while self.state == "RUNNING":
            await self.main_trading_cycle()
            await asyncio.sleep(self.config['scan_interval'])
