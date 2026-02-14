import asyncio
import logging
from datetime import datetime, timezone
from core.supabase_client import db

logger = logging.getLogger(__name__)


async def check_subscription_expiry():
    """
    Prüft alle PRO-User auf abgelaufene Subscriptions
    Stoppt automatisch Bots bei Ablauf
    Läuft im Hintergrund alle 24 Stunden
    """
    from services.bot_manager import bot_manager
    
    while True:
        try:
            # Alle PRO-User mit Ablaufdatum holen
            response = db.table("profiles").select("*").eq("is_pro", True).execute()
            
            if response.data:
                now = datetime.now(timezone.utc)
                expired_count = 0
                
                for user in response.data:
                    if user.get("expiry_date"):
                        try:
                            expiry = datetime.fromisoformat(
                                user["expiry_date"].replace('Z', '+00:00')
                            )
                            
                            # Abgelaufen?
                            if now > expiry:
                                # PRO deaktivieren
                                db.table("profiles").update({
                                    "is_pro": False
                                }).eq("id", user["id"]).execute()
                                
                                # Bot stoppen (falls läuft)
                                if bot_manager.is_bot_running(user["id"]):
                                    await bot_manager.stop_shop_bot(user["id"])
                                    logger.info(
                                        f"🛑 Shop-Bot für User {user['id']} "
                                        f"gestoppt (PRO abgelaufen)"
                                    )
                                
                                expired_count += 1
                                logger.info(f"⏰ User {user['id']} PRO-Status abgelaufen")
                        
                        except Exception as e:
                            logger.error(f"Fehler bei User {user['id']}: {e}")
                
                if expired_count > 0:
                    logger.info(
                        f"✅ {expired_count} abgelaufene PRO-Subscriptions "
                        f"deaktiviert und Bots gestoppt"
                    )
        
        except Exception as e:
            logger.error(f"Fehler beim Expiry-Check: {e}")
        
        # 24 Stunden warten
        await asyncio.sleep(86400)
