"""
Bot Setup Service
Automatische Konfiguration von Shop-Bots für PRO-User
"""
import logging
from typing import Optional, Dict, Any
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault
from config import Config

logger = logging.getLogger(__name__)


async def setup_shop_bot(bot_token: str, owner_id: int, shop_id: str) -> Dict[str, Any]:
    """
    Richtet einen Shop-Bot automatisch ein:
    - Setzt Bot-Commands
    - Konfiguriert Bot-Info
    - Validiert Token
    
    Returns: {
        "success": bool,
        "bot_username": str,
        "bot_name": str,
        "error": str (optional)
    }
    """
    try:
        # Bot-Instanz erstellen
        bot = Bot(token=bot_token)
        
        # 1. Bot-Info holen
        bot_info = await bot.get_me()
        bot_username = bot_info.username
        bot_name = bot_info.first_name
        
        logger.info(f"Setup für Bot @{bot_username} (ID: {bot_info.id})")
        
        # 2. Commands setzen
        commands = [
            BotCommand(command="start", description="🏪 Shop öffnen"),
            BotCommand(command="admin", description="🛠 Shop verwalten (Besitzer)"),
            BotCommand(command="help", description="❓ Hilfe"),
        ]
        
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        logger.info(f"✅ Commands gesetzt für @{bot_username}")
        
        # 3. Bot-Beschreibung setzen
        shop_description = (
            f"🏪 Digitaler Shop von Shop-ID: {shop_id}\n\n"
            f"Powered by {Config.BRAND_NAME}"
        )
        
        try:
            await bot.set_my_description(shop_description)
            logger.info(f"✅ Beschreibung gesetzt für @{bot_username}")
        except Exception as e:
            logger.warning(f"Beschreibung setzen fehlgeschlagen: {e}")
        
        # 4. Short Description setzen
        try:
            await bot.set_my_short_description(
                f"🛒 Digitaler Shop - Powered by {Config.BRAND_NAME}"
            )
            logger.info(f"✅ Kurzbeschreibung gesetzt für @{bot_username}")
        except Exception as e:
            logger.warning(f"Kurzbeschreibung setzen fehlgeschlagen: {e}")
        
        # Bot-Session schließen
        await bot.session.close()
        
        return {
            "success": True,
            "bot_username": bot_username,
            "bot_name": bot_name,
            "bot_id": bot_info.id
        }
        
    except Exception as e:
        logger.error(f"❌ Bot-Setup fehlgeschlagen: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def validate_bot_token(bot_token: str) -> Dict[str, Any]:
    """
    Validiert einen Bot-Token
    
    Returns: {
        "valid": bool,
        "bot_username": str (optional),
        "bot_id": int (optional),
        "error": str (optional)
    }
    """
    try:
        bot = Bot(token=bot_token)
        bot_info = await bot.get_me()
        await bot.session.close()
        
        return {
            "valid": True,
            "bot_username": bot_info.username,
            "bot_id": bot_info.id,
            "bot_name": bot_info.first_name
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


async def send_setup_notification(bot: Bot, owner_id: int, bot_username: str, shop_id: str):
    """
    Sendet Benachrichtigung nach erfolgreichem Setup
    """
    message = (
        f"🎉 **Shop-Bot erfolgreich eingerichtet!**\n\n"
        f"🤖 Dein Bot: @{bot_username}\n"
        f"🆔 Shop-ID: `{shop_id}`\n\n"
        f"**Dein Bot ist jetzt aktiv und läuft 24/7!**\n\n"
        f"Teile diesen Link mit deinen Kunden:\n"
        f"`https://t.me/{bot_username}`\n\n"
        f"💡 **Nächste Schritte:**\n"
        f"• Produkte übertragen (falls vorhanden)\n"
        f"• Zahlungsdaten prüfen\n"
        f"• Shop-Link teilen!"
    )
    
    try:
        await bot.send_message(owner_id, message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Fehler beim Senden der Setup-Benachrichtigung: {e}")


async def configure_bot_privacy(bot_token: str):
    """
    Konfiguriert Privacy-Settings (optional)
    Hinweis: Privacy muss manuell bei @BotFather gesetzt werden
    """
    # Dies ist nur informativ - Privacy-Settings müssen manuell gesetzt werden
    # bei @BotFather mit /setprivacy
    pass
