from core.supabase_client import db
from config import Config

async def can_add_product(telegram_id: int) -> tuple[bool, str]:
    """
    Prüft ob User noch Produkte hinzufügen darf
    Returns: (can_add: bool, reason: str)
    """
    user_response = db.table("profiles").select("is_pro").eq("id", telegram_id).execute()
    
    if not user_response.data:
        return False, "User nicht gefunden"
    
    user = user_response.data[0]
    
    # PRO: Unbegrenzt
    if user.get("is_pro"):
        return True, ""
    
    # FREE: Max 2 Produkte
    products_response = db.table("products").select("id", count="exact").eq("owner_id", telegram_id).execute()
    product_count = products_response.count if products_response.count is not None else 0
    
    if product_count >= Config.FREE_PRODUCT_LIMIT:
        return False, f"FREE-Limit erreicht ({Config.FREE_PRODUCT_LIMIT} Produkte)"
    
    return True, ""

async def can_use_categories(telegram_id: int) -> bool:
    """Prüft ob User Kategorien nutzen darf (PRO-Feature)"""
    user_response = db.table("profiles").select("is_pro").eq("id", telegram_id).execute()
    if not user_response.data:
        return False
    return user_response.data[0].get("is_pro", False)

async def can_upload_images(telegram_id: int) -> bool:
    """Prüft ob User Bilder hochladen darf (PRO-Feature)"""
    user_response = db.table("profiles").select("is_pro").eq("id", telegram_id).execute()
    if not user_response.data:
        return False
    return user_response.data[0].get("is_pro", False)

async def can_use_payment_method(telegram_id: int, method: str) -> bool:
    """
    Prüft ob User diese Zahlungsmethode nutzen darf
    FREE: Nur BTC & LTC
    PRO: Alle
    """
    user_response = db.table("profiles").select("is_pro").eq("id", telegram_id).execute()
    if not user_response.data:
        return False
    
    is_pro = user_response.data[0].get("is_pro", False)
    
    # FREE: Nur BTC & LTC
    if not is_pro:
        return method in Config.FREE_PAYMENT_METHODS
    
    # PRO: Alle
    return method in Config.PRO_PAYMENT_METHODS

def validate_price(price_str: str) -> tuple[bool, float]:
    """
    Validiert Preis-Eingabe
    Returns: (is_valid: bool, price: float)
    """
    try:
        price = float(price_str.replace(",", "."))
        if price <= 0:
            return False, 0.0
        if price > 999999.99:
            return False, 0.0
        return True, round(price, 2)
    except ValueError:
        return False, 0.0
