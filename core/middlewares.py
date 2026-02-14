from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from services.db_service import db

class ShopMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        bot_info = data.get("bot")
        user = data.get("event_from_user")
        
        # Sicherheitscheck für technische Events
        if not bot_info or not user:
            return await handler(event, data)

        bot_token = bot_info.token
        
        # 1. Prüfe, ob es sich um einen Custom-Shop-Bot (Pro-User) handelt
        shop_res = db.table("profiles").select("*").eq("custom_bot_token", bot_token).execute()
        
        if shop_res.data:
            # KONTEXT: Dies ist ein spezifischer Shop-Bot eines Pro-Users
            shop_owner = shop_res.data[0]
            
            # Hier ist man nur der Chef (Owner), wenn die eigene ID dem Shop-Besitzer gehört
            data["is_owner"] = (user.id == shop_owner["id"])
            data["shop_owner_id"] = shop_owner["id"]
            data["shop_data"] = shop_owner
        else:
            # KONTEXT: Dies ist der Master-Bot (Own1Shop Hauptbot)
            # Im Master-Bot veraltet jeder User sein eigenes "Universum"
            user_res = db.table("profiles").select("*").eq("id", user.id).execute()
            
            data["is_owner"] = True  # Erlaubt den Zugriff auf das persönliche Dashboard
            data["shop_owner_id"] = user.id
            
            if user_res.data:
                data["shop_data"] = user_res.data[0]
            else:
                data["shop_data"] = None

        return await handler(event, data)
