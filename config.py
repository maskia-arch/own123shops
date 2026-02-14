import os
from dotenv import load_dotenv

load_dotenv()

def get_version():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        version_path = os.path.join(base_dir, "version.txt")
        with open(version_path, "r") as f:
            return f.read().strip()
    except Exception:
        return "2.0.0"

class Config:
    # Branding
    BRAND_NAME = "Own1Shop"
    VERSION = get_version()
    
    # Bot Tokens
    MASTER_BOT_TOKEN = os.getenv("MASTER_BOT_TOKEN")
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Limits & Pricing
    FREE_PRODUCT_LIMIT = 2
    PRO_SUBSCRIPTION_PRICE = 10.00
    
    # Admin IDs (System Admins)
    ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
    
    # FREE vs PRO Features
    FREE_PAYMENT_METHODS = ["wallet_btc", "wallet_ltc"]  # Nur BTC & LTC für FREE
    PRO_PAYMENT_METHODS = ["wallet_btc", "wallet_ltc", "wallet_eth", "wallet_sol", "paypal_email"]
    
    # Telegram File Upload
    MAX_IMAGE_SIZE_MB = 5  # Max 5MB für Produkt-Bilder
