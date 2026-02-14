import asyncio
import logging
import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config import Config

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

app = Flask(__name__)
_main_dispatcher: Dispatcher = None

def get_main_dispatcher() -> Dispatcher:
    return _main_dispatcher

@app.route('/')
def health():
    return f"{Config.BRAND_NAME} v{Config.VERSION} is running", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def start_customer_bots(main_dispatcher: Dispatcher):
    active_shops = await get_active_pro_users()
    logger.info(f"Prüfe {len(active_shops)} PRO-User auf eigene Bot-Tokens...")
    
    started_count = 0
    for shop in active_shops:
        token = shop.get("custom_bot_token")
        if token:
            try:
                # WICHTIG: Webhook für Custom-Bot löschen, bevor Polling via BotManager startet
                temp_bot = Bot(token=token)
                await temp_bot.delete_webhook(drop_pending_updates=True)
                await temp_bot.session.close()

                success = await bot_manager.start_shop_bot(
                    user_id=shop['id'],
                    bot_token=token,
                    dispatcher=main_dispatcher
                )
                
                if success:
                    started_count += 1
                    logger.info(f"✅ Shop-Bot für User {shop['id']} gestartet")
            except Exception as e:
                logger.error(f"❌ Fehler bei User {shop['id']}: {e}")
    
    logger.info(f"📊 {started_count} eigene Shop-Bots aktiv")

async def main():
    global _main_dispatcher
    
    if not Config.MASTER_BOT_TOKEN:
        logger.error("❌ MASTER_BOT_TOKEN fehlt!")
        return

    logger.info(f"🚀 {Config.BRAND_NAME} wird gestartet...")
    storage = MemoryStorage()

    master_bot = Bot(
        token=Config.MASTER_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    
    dp = Dispatcher(storage=storage)
    _main_dispatcher = dp

    # Middleware registrieren
    dp.message.middleware(ShopMiddleware())
    dp.callback_query.middleware(ShopMiddleware())

    # --- ROUTER REIHENFOLGE (BERICHTIGT) ---
    # 1. Höchste Priorität: System-Level
    dp.include_router(master_admin_router)
    
    # 2. Mittlere Priorität: Administrative Handler für den Besitzer
    dp.include_router(admin_router)
    dp.include_router(settings_router)
    dp.include_router(payment_router)
    dp.include_router(migration_router)
    
    # 3. Master-Logic (Dashboard Buttons wie "Meinen Shop verwalten")
    # Muss VOR dem customer_router stehen!
    dp.include_router(master_router)
    
    # 4. Spezifische Shop-Logik für externe Bots
    dp.include_router(shop_logic_router)
    
    # 5. Niedrigste Priorität: Allgemeine Kundenansicht / Katalog
    dp.include_router(customer_router)
    # ---------------------------------------

    await master_bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(1)

    # Custom Bots via BotManager
    await start_customer_bots(dp)

    # Hintergrund-Tasks
    asyncio.create_task(check_subscription_expiry())

    logger.info(f"✅ Master-Bot Polling aktiv!")
    await dp.start_polling(master_bot, skip_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 System beendet")
