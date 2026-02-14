from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject
from config import Config
from services.db_service import create_new_user, get_user_by_id, get_user_by_shop_id
from handlers.customer_handlers import show_shop_catalog
from core.strings import Buttons, Messages

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    """
    Start-Handler für Master-Bot
    1. Deep-Link Logik: Shop-Code in URL -> Shop anzeigen
    2. Normaler Start: User registrieren & Dashboard
    """
    args = command.args

    # ========================================
    # 1. DEEP-LINK: Shop-Code übergeben?
    # ========================================
    if args:
        shop_owner = await get_user_by_shop_id(args)
        
        if shop_owner:
            owner_name = shop_owner.get("username", "Unbekannt")
            
            # Keyboard für Navigation
            kb = [[types.KeyboardButton(text=Buttons.MAIN_MENU)]]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
            
            await message.answer(
                Messages.SHOP_WELCOME.format(owner_name=owner_name),
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            # Shop-Katalog anzeigen
            await show_shop_catalog(message, shop_owner['id'])
            return
        else:
            await message.answer(
                "❌ **Shop nicht gefunden**\n\n"
                "Dieser Shop-Code ist ungültig oder existiert nicht mehr.",
                parse_mode="Markdown"
            )
            return

    # ========================================
    # 2. USER REGISTRIEREN / LADEN
    # ========================================
    await create_new_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "User"
    )
    
    user = await get_user_by_id(message.from_user.id)
    is_pro = user.get("is_pro", False)
    shop_id = user.get("shop_id", "N/A")
    status_text = "💎 PRO" if is_pro else "🆓 FREE"

    # Shop-Link generieren
    bot_info = await message.bot.get_me()
    shop_link = f"https://t.me/{bot_info.username}?start={shop_id}"

    # Dashboard-Text
    welcome_text = (
        f"{Messages.WELCOME_BACK.format(status=status_text, shop_id=shop_id)}\n\n"
        f"🔗 **Dein Shop-Link:**\n"
        f"`{shop_link}`\n\n"
        f"Teile diesen Link mit deinen Kunden!"
    )
    
    # Keyboard
    kb = [
        [types.KeyboardButton(text=Buttons.ADMIN_MANAGE)],
        [types.KeyboardButton(text=Buttons.VIEW_SHOP)]
    ]
    
    if is_pro:
        kb.insert(1, [types.KeyboardButton(text=Buttons.CONF_BOT)])
    else:
        kb.insert(1, [types.KeyboardButton(text=Buttons.UPGRADE_PRO)])
        
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    
    await message.answer(
        welcome_text,
        reply_markup=keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


@router.message(F.text == Buttons.VIEW_SHOP)
async def view_own_shop(message: types.Message):
    """Eigenen Shop in Kundenansicht anzeigen"""
    user = await get_user_by_id(message.from_user.id)
    if user:
        await message.answer("👀 **Shop-Vorschau:**", parse_mode="Markdown")
        await show_shop_catalog(message, user['id'])


@router.message(F.text == Buttons.MAIN_MENU)
async def main_menu(message: types.Message):
    """Zurück zum Hauptmenü"""
    # Simuliert Start ohne Argumente
    await cmd_start(message, CommandObject(args=None))
