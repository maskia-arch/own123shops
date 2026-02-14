import random
import string
from typing import List, Optional, Dict, Any
from core.supabase_client import db

# ========================================
# HELPER FUNCTIONS
# ========================================

def generate_unique_shop_id(length=6) -> str:
    """Generiert eine einzigartige Shop-ID"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# ========================================
# USER / PROFILE MANAGEMENT
# ========================================

async def get_active_pro_users() -> List[Dict]:
    """Holt alle aktiven PRO-User für Bot-Starts"""
    response = db.table("profiles").select("*").eq("is_pro", True).execute()
    return response.data


async def get_user_by_id(telegram_id: int) -> Optional[Dict]:
    """Holt User-Profil anhand Telegram ID"""
    response = db.table("profiles").select("*").eq("id", telegram_id).execute()
    if response.data:
        user = response.data[0]
        # Auto-Generiere Shop-ID falls nicht vorhanden
        if not user.get("shop_id"):
            new_id = generate_unique_shop_id()
            db.table("profiles").update({"shop_id": new_id}).eq("id", telegram_id).execute()
            user["shop_id"] = new_id
        return user
    return None


async def get_user_by_shop_id(shop_id: str) -> Optional[Dict]:
    """Holt User anhand Shop-ID"""
    response = db.table("profiles").select("*").eq("shop_id", shop_id.upper()).execute()
    return response.data[0] if response.data else None


async def get_shop_by_token(token: str) -> Optional[Dict]:
    """Holt Shop anhand Bot-Token"""
    response = db.table("profiles").select("*").eq("custom_bot_token", token).execute()
    return response.data[0] if response.data else None


async def create_new_user(telegram_id: int, username: str) -> bool:
    """Erstellt neuen User (falls noch nicht vorhanden)"""
    user = await get_user_by_id(telegram_id)
    if not user:
        shop_id = generate_unique_shop_id()
        data = {
            "id": telegram_id,
            "username": username,
            "is_pro": False,
            "shop_id": shop_id
        }
        db.table("profiles").insert(data).execute()
        return True
    return False


async def update_user_token(telegram_id: int, token: str):
    """Speichert Bot-Token für PRO-User"""
    db.table("profiles").update({"custom_bot_token": token}).eq("id", telegram_id).execute()


async def update_payment_methods(telegram_id: int, payment_data: dict):
    """Aktualisiert Zahlungsmethoden"""
    db.table("profiles").update(payment_data).eq("id", telegram_id).execute()


# ========================================
# PRODUCT MANAGEMENT
# ========================================

async def get_user_products(owner_id: int, category: Optional[str] = None) -> List[Dict]:
    """
    Holt alle Produkte eines Users
    Optiona Filter nach Kategorie
    """
    try:
        query = db.table("products").select("*").eq("owner_id", int(owner_id))
        
        if category:
            query = query.eq("category", category)
        
        response = query.order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error getting products: {e}")
        return []


async def add_product(
    owner_id: int, 
    name: str, 
    price: float, 
    content: str, 
    description: str = "",
    category: Optional[str] = None,
    image_url: Optional[str] = None
) -> Optional[Dict]:
    """Erstellt neues Produkt"""
    # Content formatieren (eine Zeile pro Item)
    clean_content = ""
    if content:
        items = [i.strip() for i in content.replace(",", "\n").split("\n") if i.strip()]
        clean_content = "\n".join(items)
    
    data = {
        "owner_id": int(owner_id),
        "name": name,
        "price": price,
        "content": clean_content,
        "description": description,
        "category": category,
        "image_url": image_url
    }
    
    response = db.table("products").insert(data).execute()
    return response.data[0] if response.data else None


async def update_product(
    product_id: int,
    owner_id: int,
    **kwargs
) -> bool:
    """Aktualisiert Produkt-Felder"""
    try:
        query_id = int(product_id) if str(product_id).isdigit() else product_id
        
        # Nur erlaubte Felder
        allowed_fields = ["name", "description", "price", "category", "image_url"]
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_data:
            return False
        
        db.table("products").update(update_data).eq("id", query_id).eq("owner_id", int(owner_id)).execute()
        return True
    except Exception as e:
        print(f"Error updating product: {e}")
        return False


async def refill_stock(product_id, owner_id: int, new_content: str) -> int:
    """Fügt Lagerbestand hinzu"""
    try:
        query_id = int(product_id) if str(product_id).isdigit() else product_id
        product = db.table("products").select("content").eq("id", query_id).eq("owner_id", int(owner_id)).single().execute()
        
        if product.data:
            old_content = product.data.get("content", "")
            items = [i.strip() for i in new_content.replace(",", "\n").split("\n") if i.strip()]
            updated_content = (old_content + ("\n" if old_content else "") + "\n".join(items)).strip()
            
            db.table("products").update({"content": updated_content}).eq("id", query_id).execute()
            return len(items)
    except Exception as e:
        print(f"Error refilling stock: {e}")
    return 0


async def get_stock_count(product_id) -> int:
    """Zählt verfügbare Items im Lager"""
    try:
        query_id = int(product_id) if str(product_id).isdigit() else product_id
        product = db.table("products").select("content").eq("id", query_id).single().execute()
        
        if not product.data or not product.data.get("content"):
            return 0
        
        return len([i for i in product.data["content"].split("\n") if i.strip()])
    except:
        return 0


async def delete_product(product_id, owner_id: int) -> bool:
    """Löscht Produkt und zugehörige Bestellungen"""
    query_id = int(product_id) if str(product_id).isdigit() else product_id
    try:
        # Erst Bestellungen löschen
        db.table("orders").delete().eq("product_id", query_id).execute()
        # Dann Produkt
        db.table("products").delete().eq("id", query_id).eq("owner_id", int(owner_id)).execute()
        return True
    except Exception as e:
        print(f"Error deleting product: {e}")
        return False


# ========================================
# CATEGORY MANAGEMENT (PRO)
# ========================================

async def get_user_categories(owner_id: int) -> List[Dict]:
    """Holt alle Kategorien eines Users"""
    try:
        response = db.table("categories").select("*").eq("owner_id", int(owner_id)).execute()
        return response.data
    except:
        return []


async def create_category(owner_id: int, name: str, description: str = "") -> Optional[Dict]:
    """Erstellt neue Kategorie"""
    try:
        data = {
            "owner_id": int(owner_id),
            "name": name,
            "description": description
        }
        response = db.table("categories").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating category: {e}")
        return None


async def delete_category(category_id: int, owner_id: int) -> bool:
    """Löscht Kategorie"""
    try:
        db.table("categories").delete().eq("id", category_id).eq("owner_id", int(owner_id)).execute()
        # Produkte in dieser Kategorie auf NULL setzen
        db.table("products").update({"category": None}).eq("category_id", category_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting category: {e}")
        return False


async def get_product_by_id(product_id) -> Optional[Dict]:
    """Holt einzelnes Produkt"""
    try:
        query_id = int(product_id) if str(product_id).isdigit() else product_id
        response = db.table("products").select("*").eq("id", query_id).single().execute()
        return response.data if response.data else None
    except:
        return None


# ========================================
# ORDER MANAGEMENT
# ========================================

async def create_order(buyer_id: int, product_id, seller_id: int) -> Optional[Dict]:
    """Erstellt neue Bestellung"""
    query_id = int(product_id) if str(product_id).isdigit() else product_id
    data = {
        "buyer_id": buyer_id,
        "product_id": query_id,
        "seller_id": int(seller_id),
        "status": "pending"
    }
    response = db.table("orders").insert(data).execute()
    return response.data[0] if response.data else None


async def confirm_order(order_id: str) -> Optional[str]:
    """
    Bestätigt Bestellung und sendet Item
    Returns: Item content oder "sold_out" oder None
    """
    order_res = db.table("orders").select("*").eq("id", order_id).single().execute()
    if not order_res.data:
        return None
    
    order = order_res.data
    p_id = order["product_id"]
    query_id = int(p_id) if str(p_id).isdigit() else p_id
    
    product_res = db.table("products").select("content").eq("id", query_id).single().execute()
    if not product_res.data:
        return None
    
    content = product_res.data.get("content", "")
    items = [i for i in content.split("\n") if i.strip()]
    
    if not items:
        return "sold_out"
    
    # Erstes Item entnehmen
    item_to_send = items[0]
    remaining_content = "\n".join(items[1:])
    
    # Update Produkt & Order
    db.table("products").update({"content": remaining_content}).eq("id", query_id).execute()
    db.table("orders").update({"status": "completed"}).eq("id", order_id).execute()
    
    return item_to_send


async def get_shop_customers(seller_id: int) -> List[int]:
    """Holt alle Kunden eines Shops"""
    response = db.table("orders").select("buyer_id").eq("seller_id", int(seller_id)).execute()
    if response.data:
        return list(set(item['buyer_id'] for item in response.data))
    return []


async def get_order_stats(seller_id: int) -> Dict[str, int]:
    """Holt Bestellungs-Statistiken für einen Seller"""
    response = db.table("orders").select("status", count="exact").eq("seller_id", int(seller_id)).execute()
    
    stats = {
        "total": response.count or 0,
        "pending": 0,
        "completed": 0
    }
    
    if response.data:
        for order in response.data:
            status = order.get("status", "pending")
            if status in stats:
                stats[status] += 1
    
    return stats


# ========================================
# ADMIN / STATISTICS
# ========================================

async def get_all_users_stats() -> Dict[str, Any]:
    """Holt System-weite Statistiken für Master Admin"""
    profiles = db.table("profiles").select("*", count="exact").execute()
    products = db.table("products").select("*", count="exact").execute()
    orders = db.table("orders").select("*", count="exact").execute()
    
    pro_count = len([u for u in profiles.data if u.get("is_pro")])
    free_count = profiles.count - pro_count
    
    return {
        "total_users": profiles.count or 0,
        "free_users": free_count,
        "pro_users": pro_count,
        "total_products": products.count or 0,
        "total_orders": orders.count or 0,
        "users_data": profiles.data
    }


async def get_pro_users_list() -> List[Dict]:
    """Holt Liste aller PRO-User"""
    response = db.table("profiles").select("*").eq("is_pro", True).execute()
    return response.data


async def get_free_users_list() -> List[Dict]:
    """Holt Liste aller FREE-User"""
    response = db.table("profiles").select("*").eq("is_pro", False).execute()
    return response.data
