"""
Migration Service
Übertragung von Produkten, Kategorien und Einstellungen
vom Master-Bot zum eigenen Shop-Bot
"""
import logging
from typing import List, Dict, Any
from services.db_service import (
    get_user_products, get_user_categories,
    get_user_by_id, update_product
)
from core.supabase_client import db

logger = logging.getLogger(__name__)


async def migrate_products_to_custom_bot(user_id: int) -> Dict[str, Any]:
    """
    Migriert alle Produkte vom Master-Bot zum eigenen Bot
    
    Hinweis: In der Datenbank bleiben Produkte gleich,
    nur die Zuordnung ändert sich (welcher Bot bedient sie)
    
    Returns: {
        "success": bool,
        "migrated_count": int,
        "categories_migrated": int,
        "error": str (optional)
    }
    """
    try:
        user = await get_user_by_id(user_id)
        
        if not user:
            return {"success": False, "error": "User nicht gefunden"}
        
        if not user.get("is_pro"):
            return {"success": False, "error": "PRO-Status erforderlich"}
        
        if not user.get("custom_bot_token"):
            return {"success": False, "error": "Kein Bot-Token hinterlegt"}
        
        # Produkte holen
        products = await get_user_products(user_id)
        
        # Kategorien holen
        categories = await get_user_categories(user_id)
        
        # Migration-Flag in der DB setzen
        # Dies markiert, dass Produkte nun über den Custom-Bot verfügbar sind
        db.table("profiles").update({
            "migration_completed": True,
            "migration_date": "NOW()"
        }).eq("id", user_id).execute()
        
        logger.info(
            f"✅ Migration abgeschlossen für User {user_id}: "
            f"{len(products)} Produkte, {len(categories)} Kategorien"
        )
        
        return {
            "success": True,
            "migrated_count": len(products),
            "categories_migrated": len(categories),
            "custom_bot_active": True
        }
        
    except Exception as e:
        logger.error(f"❌ Migration fehlgeschlagen für User {user_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def check_migration_status(user_id: int) -> Dict[str, Any]:
    """
    Prüft ob User bereits migriert hat
    
    Returns: {
        "migrated": bool,
        "has_custom_bot": bool,
        "product_count": int,
        "can_migrate": bool
    }
    """
    try:
        user = await get_user_by_id(user_id)
        
        if not user:
            return {
                "migrated": False,
                "has_custom_bot": False,
                "product_count": 0,
                "can_migrate": False
            }
        
        products = await get_user_products(user_id)
        has_custom_bot = bool(user.get("custom_bot_token"))
        is_pro = user.get("is_pro", False)
        migrated = user.get("migration_completed", False)
        
        can_migrate = (
            is_pro and 
            has_custom_bot and 
            not migrated and 
            len(products) > 0
        )
        
        return {
            "migrated": migrated,
            "has_custom_bot": has_custom_bot,
            "product_count": len(products),
            "can_migrate": can_migrate,
            "is_pro": is_pro
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Migration-Status-Check: {e}")
        return {
            "migrated": False,
            "has_custom_bot": False,
            "product_count": 0,
            "can_migrate": False
        }


async def rollback_migration(user_id: int) -> bool:
    """
    Macht Migration rückgängig (falls nötig)
    """
    try:
        db.table("profiles").update({
            "migration_completed": False,
            "migration_date": None
        }).eq("id", user_id).execute()
        
        logger.info(f"Migration für User {user_id} zurückgesetzt")
        return True
        
    except Exception as e:
        logger.error(f"Rollback fehlgeschlagen: {e}")
        return False


async def get_migration_summary(user_id: int) -> str:
    """
    Erstellt eine Zusammenfassung für die Migration
    """
    user = await get_user_by_id(user_id)
    products = await get_user_products(user_id)
    categories = await get_user_categories(user_id)
    
    summary = (
        f"📦 **Migration-Übersicht**\n\n"
        f"**Deine Produkte:**\n"
        f"├─ Anzahl: {len(products)}\n"
    )
    
    if categories:
        summary += f"├─ Kategorien: {len(categories)}\n"
    
    # Produkte auflisten
    if products:
        summary += f"\n**Produkte die übertragen werden:**\n"
        for i, p in enumerate(products[:10], 1):  # Max 10 anzeigen
            summary += f"{i}. {p['name']} ({p['price']}€)\n"
        
        if len(products) > 10:
            summary += f"...und {len(products) - 10} weitere\n"
    
    summary += (
        f"\n**Was passiert:**\n"
        f"✅ Alle Produkte werden auf deinen Bot übertragen\n"
        f"✅ Kategorien bleiben erhalten\n"
        f"✅ Zahlungsdaten bleiben gleich\n"
        f"✅ Lagerbestände bleiben erhalten\n\n"
        f"⚠️ **Wichtig:**\n"
        f"Nach der Migration sind deine Produkte nur noch über\n"
        f"deinen eigenen Bot verfügbar, nicht mehr über den Master-Bot."
    )
    
    return summary
