from aiogram import Router, types, F
from aiogram.filters import Command
from handlers.customer_handlers import show_shop_catalog

router = Router()


@router.message(Command("start"))
async def handle_shop_start(message: types.Message, is_owner: bool = False, shop_owner_id: int = None):
    """
    Start-Handler für eigene Shop-Bots (PRO)
    
    is_owner: True wenn Bot-Besitzer den Bot startet
    shop_owner_id: ID des Shop-Besitzers
    """
    if is_owner:
        # Besitzer -> Admin-Panel
        from handlers.admin_handlers import admin_menu
        await admin_menu(message, is_owner=True)
        return

    if shop_owner_id:
        # Kunde -> Shop anzeigen
        await message.answer("🏪 **Willkommen im Shop!**\nHier sind die verfügbaren Produkte:")
        await show_shop_catalog(message, shop_owner_id)
    else:
        await message.answer(
            "👋 Willkommen!\n\n"
            "Dies ist ein Shop-Bot. Nutze die Menü-Buttons zur Navigation.",
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "refresh_shop")
async def refresh_shop_view(callback: types.CallbackQuery):
    """Shop-Ansicht aktualisieren"""
    await callback.answer("🔄 Ansicht aktualisiert.")
