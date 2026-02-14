import httpx
from services.db_service import db

async def get_user_id_by_shop_id(shop_id: str):
    """Shop-ID zu Telegram-User-ID auflösen"""
    try:
        response = db.table("profiles").select("id").eq("shop_id", shop_id.upper()).single().execute()
        return response.data["id"] if response.data else None
    except:
        return None

async def get_ltc_price(eur_amount: float):
    """EUR zu LTC Kurs holen"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.coinbase.com/v2/prices/LTC-EUR/spot")
            data = response.json()
            price = float(data["data"]["amount"])
            return round(eur_amount / price, 8)
    except:
        return None

def validate_crypto_address(address: str, method: str) -> bool:
    """Validiert Krypto-Adressen und PayPal E-Mail"""
    address = address.strip()
    
    if method == "paypal_email":
        return "@" in address and "." in address
    
    if method == "wallet_btc":
        # BTC: Legacy (1...), SegWit (3...), Native SegWit (bc1...)
        return address.startswith(("1", "3", "bc1")) and 26 <= len(address) <= 62
    
    if method == "wallet_ltc":
        # LTC: L..., M..., ltc1...
        return address.startswith(("L", "M", "ltc1")) and 26 <= len(address) <= 62
    
    if method == "wallet_eth":
        # ETH: 0x... (42 Zeichen)
        return address.startswith("0x") and len(address) == 42
    
    if method == "wallet_sol":
        # SOL: Base58 (32-44 Zeichen)
        return 32 <= len(address) <= 44
    
    return True

def format_stock_display(content: str) -> int:
    """Anzahl verfügbarer Items aus content berechnen"""
    if not content:
        return 0
    items = [i for i in content.split("\n") if i.strip()]
    return len(items)

def format_payment_methods(user_data: dict, is_pro: bool) -> str:
    """Formatiert Zahlungsmethoden für Anzeige"""
    from config import Config
    
    methods = []
    
    # BTC & LTC (immer verfügbar)
    if user_data.get("wallet_btc"):
        methods.append(f"₿ **BTC:** `{user_data['wallet_btc']}`")
    if user_data.get("wallet_ltc"):
        methods.append(f"Ł **LTC:** `{user_data['wallet_ltc']}`")
    
    # Nur PRO: ETH, SOL, PayPal
    if is_pro:
        if user_data.get("wallet_eth"):
            methods.append(f"Ξ **ETH:** `{user_data['wallet_eth']}`")
        if user_data.get("wallet_sol"):
            methods.append(f"◎ **SOL:** `{user_data['wallet_sol']}`")
        if user_data.get("paypal_email"):
            methods.append(f"🅿️ **PayPal (F&F):** `{user_data['paypal_email']}`")
    
    return "\n".join(methods) if methods else "Keine Zahlungsmethoden hinterlegt"

async def upload_image_to_telegram(bot, file_id: str) -> str:
    """
    Speichert Telegram File ID für spätere Verwendung
    (Alternative: Upload zu S3/CDN für externe Verfügbarkeit)
    """
    # Für jetzt: Einfach file_id speichern
    # Telegram File IDs sind permanent und können wiederverwendet werden
    return file_id

def truncate_text(text: str, max_length: int = 100) -> str:
    """Text auf max_length kürzen"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
