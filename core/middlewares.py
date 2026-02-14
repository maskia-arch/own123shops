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
        
        if not bot_info or not user:
            return await handler(event, data)

        # Standardwerte: Im Master-Bot ist jeder sein eigener Chef
        data["is_owner"] = True 
        data["shop_owner_id"] = user.id
        data["shop_data"] = None

        bot_token = bot_info.token
        
        # 1. Prüfe, ob es sich um einen Custom-Shop-Bot handelt
        # Wir suchen, ob der aktuelle Bot-Token jemandem gehört
        shop_res = db.table("profiles").select("*").eq("custom_bot_token", bot_token).execute()
        
        if shop_res.data:
            # KONTEXT: Dies ist ein externer PRO-Shop-Bot
            shop_owner = shop_res.data[0]
            # Hier ist man nur Owner, wenn die ID übereinstimmt
            data["is_owner"] = (user.id == shop_owner["id"])
            data["shop_owner_id"] = shop_owner["id"]
            data["shop_data"] = shop_owner
        else:
            # KONTEXT: Dies ist der Master-Bot
            # Wir laden die Profildaten des Users, damit die Handler darauf zugreifen können
            user_res = db.table("profiles").select("*").eq("id", user.id).execute()
            if user_res.data:
                data["shop_data"] = user_res.data[0]
            
            # is_owner bleibt True, damit jeder sein eigenes Dashboard sieht
            data["is_owner"] = True
            data["shop_owner_id"] = user.id

        return await handler(event, data)
