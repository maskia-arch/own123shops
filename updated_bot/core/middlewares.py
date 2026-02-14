from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from services.db_service import db

class ShopMiddleware(BaseMiddleware):
    """
    Middleware um Shop-Kontext zu laden:
    - Bei eigenem Bot: Lädt Shop-Besitzer Daten
    - Prüft ob User = Besitzer
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        bot_info = data.get("bot")
        user = data.get("event_from_user")
        
        if not bot_info or not user:
            return await handler(event, data)

        bot_token = bot_info.token
        
        # Prüfe ob dieser Bot einem Shop gehört
        shop_res = db.table("profiles").select("*").eq("custom_bot_token", bot_token).execute()
        
        if shop_res.data:
            # Dies ist ein Shop-Bot
            shop_owner = shop_res.data[0]
            is_owner = user.id == shop_owner["id"]
            
            data["is_owner"] = is_owner
            data["shop_owner_id"] = shop_owner["id"]
            data["shop_data"] = shop_owner
        else:
            # Master Bot oder unbekannt
            data["is_owner"] = False
            data["shop_owner_id"] = None

        return await handler(event, data)
