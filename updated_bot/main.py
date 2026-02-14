import asyncio
import logging
import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config import Config

# Router importieren
from bots.master_bot import router as master_router
from bots.shop_logic import router as shop_logic_router
from handlers import (
    admin_router,
    customer_router,
    payment_router,
    settings_router,
    master_admin_router,
    migration_router
)

from services.db_service import get_active_pro_users
from services.bot_manager import bot_manager
from core.middlewares import ShopMiddleware
from tasks.expiry_check import check_subscription_expiry

# Flask für Health-Check (render.com)
app = Flask(__name__)

# Globaler Dispatcher (für dynamisches Bot-Management)
_main_dispatcher: Dispatcher = None

def get_main_dispatcher() -> Dispatcher:
    """Gibt den Haupt-Dispatcher zurück"""
    return _main_dispatcher

@app.route('/')
def health():
    return f"{Config.BRAND_NAME} v{Config.VERSION} is running", 200

def run_flask():
    """Flask in separatem Thread starten"""
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def start_customer_bots(main_dispatcher: Dispatcher):
    """
    Startet separate Bots für alle PRO-User mit eigenem Token
    Nutzt jetzt den BotManager für dynamisches Management
    """
    active_shops = await get_active_pro_users()
    
    logger.info(f"Prüfe {len(active_shops)} PRO-User auf eigene Bot-Tokens...")
    
    started_count = 0
    for shop in active_shops:
        token = shop.get("custom_bot_token")
        if token:
            try:
                # Bot via BotManager starten
                success = await bot_manager.start_shop_bot(
                    user_id=shop['id'],
                    bot_token=token,
                    dispatcher=main_dispatcher
                )
                
                if success:
                    started_count += 1
                    logger.info(
                        f"✅ Shop-Bot für User {shop['id']} "
                        f"(@{shop.get('username', 'N/A')}) gestartet"
                    )
                else:
                    logger.error(f"❌ Fehler beim Starten von Bot für User {shop['id']}")
                
            except Exception as e:
                logger.error(f"❌ Fehler bei User {shop['id']}: {e}")
    
    if started_count > 0:
        logger.info(f"🎉 {started_count} eigene Shop-Bots gestartet!")
    else:
        logger.info("ℹ️ Keine eigenen Shop-Bots konfiguriert")


async def main():
    """
    Hauptfunktion - Startet Master-Bot und alle PRO-Bots
    """
    global _main_dispatcher
    
    # Master-Bot Token prüfen
    if not Config.MASTER_BOT_TOKEN:
        logger.error("❌ MASTER_BOT_TOKEN nicht gefunden! Bot kann nicht starten.")
        return

    logger.info(f"🚀 {Config.BRAND_NAME} v{Config.VERSION} wird gestartet...")
    
    # Storage für FSM States
    storage = MemoryStorage()

    # Master-Bot erstellen
    master_bot = Bot(
        token=Config.MASTER_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    
    # Dispatcher erstellen
    dp = Dispatcher(storage=storage)
    _main_dispatcher = dp  # Global verfügbar machen

    # Middleware registrieren
    dp.message.middleware(ShopMiddleware())
    dp.callback_query.middleware(ShopMiddleware())

    # Router registrieren (Reihenfolge ist wichtig!)
    dp.include_router(master_admin_router)  # Master-Admin Befehle
    dp.include_router(admin_router)         # Shop-Verwaltung
    dp.include_router(settings_router)      # Einstellungen
    dp.include_router(payment_router)       # Zahlungen / Upgrade
    dp.include_router(migration_router)     # Produktübertragung (NEU)
    dp.include_router(customer_router)      # Kundenansicht
    dp.include_router(master_router)        # Master-Bot Commands
    dp.include_router(shop_logic_router)    # Shop-Logic für Custom Bots

    logger.info("📡 Master-Bot: Webhook wird gelöscht...")
    await master_bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(2)

    # PRO-User Bots starten (mit BotManager)
    await start_customer_bots(dp)

    # Expiry-Check Task im Hintergrund starten
    asyncio.create_task(check_subscription_expiry())
    logger.info("⏰ Subscription-Expiry-Check aktiviert")

    # Master-Bot Polling starten
    logger.info(f"✅ Master-Bot Polling aktiv - System läuft!")
    logger.info(f"📊 Aktive Shop-Bots: {bot_manager.get_active_bot_count()}")
    await dp.start_polling(master_bot, skip_updates=True)


if __name__ == "__main__":
    # Flask in separatem Thread starten (für render.com Health-Check)
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info(f"🌐 Flask Health-Check auf Port {os.environ.get('PORT', 10000)}")
    
    # Bot-System starten
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 System wurde manuell beendet")
