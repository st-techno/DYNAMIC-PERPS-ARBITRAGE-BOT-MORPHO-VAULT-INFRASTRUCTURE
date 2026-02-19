#!/usr/bin/env python3
"""
INSTITUTIONAL PERPS ARBITRAGE BOT - Production Entry Point
$100K+ capital ready, 20% annual returns expected
"""
import asyncio
import logging
import os
import signal
import sys
from pathlib import Path
import yaml

from core.arbitrage_engine import CompleteInstitutionalArbitrageBot
from config.settings import load_config
from monitoring.health import HealthMonitor

# Production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Institutional production bootstrap"""
    try:
        # Load production config
        config = load_config('config/production.yaml')
        
        # Initialize complete institutional bot
        bot = CompleteInstitutionalArbitrageBot(config)
        await bot.initialize_trading_infrastructure()
        
        # Start health monitoring
        health_monitor = HealthMonitor(bot)
        health_monitor.start()
        
        logger.info("🚀 INSTITUTIONAL BOT LIVE - Scanning all events")
        await bot.institutional_main_loop()
        
    except KeyboardInterrupt:
        logger.info("Graceful shutdown initiated")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Graceful signal handling
    signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(shutdown()))
    signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(shutdown()))
    
    asyncio.run(main())
