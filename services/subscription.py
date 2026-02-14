from datetime import datetime, timedelta, timezone
from core.supabase_client import db

async def check_subscription_status(telegram_id: int) -> bool:
    """
    Prüft ob PRO-Subscription noch aktiv ist
    Returns: True wenn aktiv, False wenn abgelaufen
    """
    response = db.table("profiles").select("is_pro, expiry_date").eq("id", telegram_id).execute()
    if not response.data:
        return False
    
    user = response.data[0]
    if not user["is_pro"]:
        return False
    
    # Wenn expiry_date gesetzt ist, prüfen
    if user["expiry_date"]:
        try:
            expiry = datetime.fromisoformat(user["expiry_date"].replace('Z', '+00:00'))
            if datetime.now(timezone.utc) > expiry:
                # Subscription abgelaufen -> auf FREE zurücksetzen
                db.table("profiles").update({"is_pro": False}).eq("id", telegram_id).execute()
                return False
        except Exception as e:
            print(f"Error parsing expiry_date: {e}")
    
    return True


async def activate_pro_subscription(telegram_id: int, months: int = 1):
    """
    Aktiviert PRO-Subscription für X Monate
    """
    now = datetime.now(timezone.utc)
    new_expiry = now + timedelta(days=30 * months)
    
    data = {
        "is_pro": True,
        "expiry_date": new_expiry.isoformat()
    }
    
    db.table("profiles").update(data).eq("id", telegram_id).execute()


async def cancel_subscription(telegram_id: int):
    """
    Deaktiviert PRO-Subscription sofort und stoppt eigenen Bot
    """
    from services.bot_manager import bot_manager
    
    # PRO deaktivieren
    db.table("profiles").update({
        "is_pro": False,
        "expiry_date": None
    }).eq("id", telegram_id).execute()
    
    # Eigenen Bot stoppen (falls läuft)
    if bot_manager.is_bot_running(telegram_id):
        await bot_manager.stop_shop_bot(telegram_id)
        logger.info(f"Shop-Bot für User {telegram_id} gestoppt (PRO abgelaufen)")


async def reactivate_subscription(telegram_id: int, months: int = 1):
    """
    Reaktiviert PRO-Subscription und startet Bot neu
    """
    from services.bot_manager import bot_manager
    
    # PRO aktivieren
    await activate_pro_subscription(telegram_id, months)
    
    # Bot neu starten (falls Token vorhanden)
    response = db.table("profiles").select("custom_bot_token").eq("id", telegram_id).execute()
    
    if response.data and response.data[0].get("custom_bot_token"):
        token = response.data[0]["custom_bot_token"]
        
        # Bot neu starten
        from main import get_main_dispatcher
        dispatcher = get_main_dispatcher()
        
        if dispatcher:
            bot_started = await bot_manager.start_shop_bot(
                user_id=telegram_id,
                bot_token=token,
                dispatcher=dispatcher
            )
            
            if bot_started:
                logger.info(f"Shop-Bot für User {telegram_id} reaktiviert")
            else:
                logger.error(f"Fehler beim Reaktivieren von Bot für User {telegram_id}")
        else:
            logger.warning(f"Dispatcher nicht verfügbar für User {telegram_id}")


async def extend_subscription(telegram_id: int, months: int = 1):
    """
    Verlängert bestehende Subscription um X Monate
    """
    response = db.table("profiles").select("expiry_date").eq("id", telegram_id).execute()
    
    if not response.data:
        return
    
    current_expiry = response.data[0].get("expiry_date")
    
    if current_expiry:
        try:
            expiry_dt = datetime.fromisoformat(current_expiry.replace('Z', '+00:00'))
            # Wenn noch nicht abgelaufen, ab aktuellem Datum verlängern
            if expiry_dt > datetime.now(timezone.utc):
                new_expiry = expiry_dt + timedelta(days=30 * months)
            else:
                # Sonst ab jetzt
                new_expiry = datetime.now(timezone.utc) + timedelta(days=30 * months)
        except:
            new_expiry = datetime.now(timezone.utc) + timedelta(days=30 * months)
    else:
        new_expiry = datetime.now(timezone.utc) + timedelta(days=30 * months)
    
    db.table("profiles").update({
        "is_pro": True,
        "expiry_date": new_expiry.isoformat()
    }).eq("id", telegram_id).execute()
