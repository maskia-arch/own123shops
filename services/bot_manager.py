"""
Bot Manager Service
Dynamisches Starten und Stoppen von Shop-Bots
"""
import asyncio
import logging
from typing import Dict, Optional
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

logger = logging.getLogger(__name__)


class BotManager:
    """
    Verwaltet alle laufenden Shop-Bots
    """
    
    def __init__(self):
        self.active_bots: Dict[int, Bot] = {}  # user_id -> Bot instance
        self.polling_tasks: Dict[int, asyncio.Task] = {}  # user_id -> Task
    
    async def start_shop_bot(
        self, 
        user_id: int, 
        bot_token: str, 
        dispatcher: Dispatcher
    ) -> bool:
        """
        Startet einen Shop-Bot
        
        Args:
            user_id: Telegram User ID des Besitzers
            bot_token: Bot API Token
            dispatcher: Hauptdispatcher (Router werden geteilt)
        
        Returns:
            True wenn erfolgreich gestartet
        """
        # Prüfe ob Bot bereits läuft
        if user_id in self.active_bots:
            logger.warning(f"Bot für User {user_id} läuft bereits")
            return True
        
        try:
            # Bot-Instanz erstellen
            bot = Bot(
                token=bot_token,
                default=DefaultBotProperties(parse_mode="HTML")
            )
            
            # Webhook löschen
            await bot.delete_webhook(drop_pending_updates=True)
            await asyncio.sleep(0.5)
            
            # Polling starten (als Background-Task)
            task = asyncio.create_task(
                dispatcher.start_polling(bot, skip_updates=True)
            )
            
            # In Registry speichern
            self.active_bots[user_id] = bot
            self.polling_tasks[user_id] = task
            
            bot_info = await bot.get_me()
            logger.info(f"✅ Shop-Bot gestartet: @{bot_info.username} (User: {user_id})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Starten von Bot für User {user_id}: {e}")
            return False
    
    async def stop_shop_bot(self, user_id: int) -> bool:
        """
        Stoppt einen Shop-Bot
        
        Args:
            user_id: Telegram User ID des Besitzers
        
        Returns:
            True wenn erfolgreich gestoppt
        """
        if user_id not in self.active_bots:
            logger.warning(f"Kein aktiver Bot für User {user_id} gefunden")
            return False
        
        try:
            bot = self.active_bots[user_id]
            task = self.polling_tasks.get(user_id)
            
            # Bot-Info vor dem Schließen holen
            try:
                bot_info = await bot.get_me()
                bot_username = bot_info.username
            except:
                bot_username = "Unknown"
            
            # Polling-Task stoppen
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Bot-Session schließen
            await bot.session.close()
            
            # Aus Registry entfernen
            del self.active_bots[user_id]
            if user_id in self.polling_tasks:
                del self.polling_tasks[user_id]
            
            logger.info(f"🛑 Shop-Bot gestoppt: @{bot_username} (User: {user_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Stoppen von Bot für User {user_id}: {e}")
            return False
    
    async def restart_shop_bot(
        self,
        user_id: int,
        bot_token: str,
        dispatcher: Dispatcher
    ) -> bool:
        """
        Startet einen Bot neu
        """
        await self.stop_shop_bot(user_id)
        await asyncio.sleep(1)
        return await self.start_shop_bot(user_id, bot_token, dispatcher)
    
    def is_bot_running(self, user_id: int) -> bool:
        """
        Prüft ob Bot läuft
        """
        return user_id in self.active_bots
    
    def get_active_bot_count(self) -> int:
        """
        Anzahl aktiver Bots
        """
        return len(self.active_bots)
    
    def get_active_user_ids(self) -> list:
        """
        Liste aller User-IDs mit aktiven Bots
        """
        return list(self.active_bots.keys())
    
    async def stop_all_bots(self):
        """
        Stoppt alle Bots (z.B. beim Shutdown)
        """
        logger.info(f"Stoppe alle {len(self.active_bots)} Shop-Bots...")
        
        user_ids = list(self.active_bots.keys())
        for user_id in user_ids:
            await self.stop_shop_bot(user_id)
        
        logger.info("✅ Alle Shop-Bots gestoppt")
    
    async def get_bot_status(self, user_id: int) -> Dict:
        """
        Status eines Bots abrufen
        """
        if user_id not in self.active_bots:
            return {
                "running": False,
                "bot_username": None
            }
        
        try:
            bot = self.active_bots[user_id]
            bot_info = await bot.get_me()
            
            return {
                "running": True,
                "bot_username": bot_info.username,
                "bot_id": bot_info.id,
                "bot_name": bot_info.first_name
            }
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Bot-Status: {e}")
            return {
                "running": False,
                "error": str(e)
            }


# Globale Instanz
bot_manager = BotManager()
