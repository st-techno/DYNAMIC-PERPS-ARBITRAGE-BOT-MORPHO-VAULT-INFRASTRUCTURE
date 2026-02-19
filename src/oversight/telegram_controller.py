"""
INSTITUTIONAL TELEGRAM CONTROL PANEL
11 commands: /status /emergency /approve OPP_ID etc.
"""
import asyncio
from telegram.ext import Application, CommandHandler
from typing import Dict

class InstitutionalHumanOversight:
    def __init__(self, bot_token: str, chat_id: str, bot):
        self.app = Application.builder().token(bot_token).build()
        self.chat_id = chat_id
        self.bot = bot
        self.pending_opportunities = {}
        self.setup_handlers()
    
    def setup_handlers(self):
        handlers = [
            CommandHandler("status", self.status),
            CommandHandler("emergency", self.emergency),
            CommandHandler("approve", self.approve),
            CommandHandler("positions", self.positions),
            CommandHandler("events", self.events),
        ]
        for handler in handlers:
            self.app.add_handler(handler)
    
    async def status(self, update, context):
        pnl = await self.bot.calculate_pnl()
        msg = f"""
🤖 *BOT STATUS*
State: `{self.bot.state}`
Capital: ${self.bot.config['capital_base']:,.0f}
PnL: ${pnl:.0f}
Positions: {len(self.bot.positions)}
Events: {len(self.bot.active_events)}
        """
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    async def approve(self, update, context):
        if context.args:
            opp_id = context.args[0]
            if opp_id in self.pending_opportunities:
                opp = self.pending_opportunities.pop(opp_id)
                asyncio.create_task(self.bot.execute_trade(opp))
                await update.message.reply_text(f"✅ {opp_id} EXECUTED")
