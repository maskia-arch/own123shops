from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.db_service import get_user_by_id, update_user_token, update_payment_methods
from core.validator import can_use_payment_method
from core.utils import validate_crypto_address
from core.strings import Buttons, Messages

router = Router()


class ShopSettingsForm(StatesGroup):
    waiting_for_token = State()
    waiting_for_wallet = State()


@router.message(F.text == Buttons.SETTINGS)
@router.message(F.text == Buttons.CONF_BOT)
async def show_settings_menu(message: types.Message):
    """Shop-Einstellungen anzeigen"""
    user = await get_user_by_id(message.from_user.id)
    if not user:
        return

    is_pro = user.get("is_pro", False)
    
    # Keyboard erstellen
    builder = InlineKeyboardBuilder()
    
    # BTC & LTC (immer verfügbar)
    builder.row(types.InlineKeyboardButton(
        text=Buttons.CHANGE_BTC,
        callback_data="set_pay_wallet_btc"
    ))
    builder.row(types.InlineKeyboardButton(
        text=Buttons.CHANGE_LTC,
        callback_data="set_pay_wallet_ltc"
    ))
    
    # PRO: Weitere Zahlungsmethoden
    if is_pro:
        text = Messages.SETTINGS_MENU_PRO.format(
            btc=user.get('wallet_btc') or 'Nicht hinterlegt',
            ltc=user.get('wallet_ltc') or 'Nicht hinterlegt',
            eth=user.get('wallet_eth') or 'Nicht hinterlegt',
            sol=user.get('wallet_sol') or 'Nicht hinterlegt',
            paypal=user.get('paypal_email') or 'Nicht hinterlegt',
            token_status='✅ Konfiguriert' if user.get('custom_bot_token') else '❌ Nicht gesetzt'
        )
        
        builder.row(types.InlineKeyboardButton(
            text=Buttons.CHANGE_ETH,
            callback_data="set_pay_wallet_eth"
        ))
        builder.row(types.InlineKeyboardButton(
            text=Buttons.CHANGE_SOL,
            callback_data="set_pay_wallet_sol"
        ))
        builder.row(types.InlineKeyboardButton(
            text=Buttons.CHANGE_PAYPAL,
            callback_data="set_pay_paypal_email"
        ))
        builder.row(types.InlineKeyboardButton(
            text=Buttons.OWN_BOT_TOKEN,
            callback_data="start_token_config"
        ))
    else:
        # FREE
        text = Messages.SETTINGS_MENU_FREE.format(
            btc=user.get('wallet_btc') or 'Nicht hinterlegt',
            ltc=user.get('wallet_ltc') or 'Nicht hinterlegt'
        )
    
    await message.answer(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("set_pay_"))
async def start_wallet_update(callback: types.CallbackQuery, state: FSMContext):
    """Zahlungsmethode ändern"""
    field = callback.data.replace("set_pay_", "")
    
    # Prüfen ob User diese Methode nutzen darf
    if not await can_use_payment_method(callback.from_user.id, field):
        await callback.answer(
            "⚠️ Diese Zahlungsmethode ist nur in der PRO-Version verfügbar!",
            show_alert=True
        )
        return
    
    names = {
        "wallet_btc": "Bitcoin (BTC)",
        "wallet_ltc": "Litecoin (LTC)",
        "wallet_eth": "Ethereum (ETH)",
        "wallet_sol": "Solana (SOL)",
        "paypal_email": "PayPal (F&F) Email"
    }
    
    await state.update_data(current_field=field)
    await state.set_state(ShopSettingsForm.waiting_for_wallet)
    
    await callback.message.answer(
        Messages.ASK_WALLET_ADDRESS.format(method=names.get(field, field)),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(ShopSettingsForm.waiting_for_wallet)
async def process_wallet_input(message: types.Message, state: FSMContext):
    """Zahlungsadresse speichern"""
    if message.text == Buttons.MAIN_MENU:
        await state.clear()
        return

    data = await state.get_data()
    field = data.get("current_field")
    value = message.text.strip()

    # Validierung
    if not validate_crypto_address(value, field):
        await message.answer(Messages.WALLET_INVALID)
        return

    try:
        await update_payment_methods(message.from_user.id, {field: value})
        await state.clear()
        await message.answer(Messages.WALLET_SUCCESS)
    except Exception as e:
        await message.answer(f"❌ Fehler beim Speichern: {e}")


@router.callback_query(F.data == "start_token_config")
async def start_token_config(callback: types.CallbackQuery, state: FSMContext):
    """Bot-Token konfigurieren (PRO)"""
    user = await get_user_by_id(callback.from_user.id)
    
    if not user.get("is_pro"):
        await callback.answer(
            "⚠️ Eigener Bot-Token ist nur in der PRO-Version verfügbar!",
            show_alert=True
        )
        return
    
    await state.set_state(ShopSettingsForm.waiting_for_token)
    await callback.message.answer(Messages.TOKEN_PROMPT, parse_mode="Markdown")
    await callback.answer()


@router.message(ShopSettingsForm.waiting_for_token)
async def process_token(message: types.Message, state: FSMContext):
    """Bot-Token speichern und automatisch einrichten"""
    if message.text == Buttons.MAIN_MENU:
        await state.clear()
        return

    token = message.text.strip()
    
    # Basis-Validierung
    if ":" not in token or len(token) < 30:
        await message.answer(
            "❌ **Ungültiges Token-Format**\n\n"
            "Ein Bot-Token sieht etwa so aus:\n"
            "`123456789:ABCdefGHIjklMNOpqrSTUvwxYZ`",
            parse_mode="Markdown"
        )
        return

    # Status-Nachricht
    status_msg = await message.answer(
        "⏳ **Bot wird eingerichtet...**\n\n"
        "├─ Token validieren\n"
        "├─ Bot konfigurieren\n"
        "├─ Commands setzen\n"
        "└─ Bot starten\n\n"
        "Dies kann einen Moment dauern...",
        parse_mode="Markdown"
    )

    try:
        from services.bot_setup import setup_shop_bot, validate_bot_token, send_setup_notification
        from services.bot_manager import bot_manager
        
        # 1. Token validieren
        validation = await validate_bot_token(token)
        if not validation["valid"]:
            await status_msg.edit_text(
                f"❌ **Token ungültig**\n\n"
                f"Fehler: {validation.get('error', 'Unbekannt')}\n\n"
                f"Bitte prüfe den Token und versuche es erneut.",
                parse_mode="Markdown"
            )
            return
        
        # 2. User-Daten holen
        user = await get_user_by_id(message.from_user.id)
        shop_id = user.get("shop_id", "N/A")
        
        # 3. Token speichern
        await update_user_token(message.from_user.id, token)
        
        # 4. Bot automatisch einrichten
        setup_result = await setup_shop_bot(token, message.from_user.id, shop_id)
        
        if not setup_result["success"]:
            await status_msg.edit_text(
                f"⚠️ **Token gespeichert, aber Setup fehlgeschlagen**\n\n"
                f"Fehler: {setup_result.get('error', 'Unbekannt')}\n\n"
                f"Der Bot wird beim nächsten System-Neustart aktiviert.",
                parse_mode="Markdown"
            )
            await state.clear()
            return
        
        bot_username = setup_result["bot_username"]
        
        # 5. Bot dynamisch starten
        from main import get_main_dispatcher
        dispatcher = get_main_dispatcher()
        
        if dispatcher:
            bot_started = await bot_manager.start_shop_bot(
                user_id=message.from_user.id,
                bot_token=token,
                dispatcher=dispatcher
            )
            
            if bot_started:
                start_status = "✅ Läuft jetzt"
            else:
                start_status = "⚠️ Wird beim Neustart gestartet"
        else:
            start_status = "⚠️ Wird beim Neustart gestartet"
        
        # 6. Erfolgs-Nachricht
        await status_msg.edit_text(
            f"🎉 **Bot erfolgreich eingerichtet!**\n\n"
            f"🤖 Dein Bot: @{bot_username}\n"
            f"🆔 Shop-ID: `{shop_id}`\n"
            f"📡 Status: {start_status}\n\n"
            f"**Shop-Link:**\n"
            f"`https://t.me/{bot_username}`\n\n"
            f"💡 **Nächster Schritt:**\n"
            f"Möchtest du deine bestehenden Produkte auf diesen Bot übertragen?",
            parse_mode="Markdown"
        )
        
        # 7. Migration anbieten
        from services.migration import check_migration_status
        migration_status = await check_migration_status(message.from_user.id)
        
        if migration_status["can_migrate"]:
            kb = [[types.InlineKeyboardButton(
                text=f"📦 Produkte übertragen ({migration_status['product_count']})",
                callback_data="start_migration"
            )]]
            await message.answer(
                "Du hast Produkte im Master-Bot. Möchtest du sie auf deinen eigenen Bot übertragen?",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb)
            )
        
        # 8. Setup-Benachrichtigung
        await send_setup_notification(message.bot, message.from_user.id, bot_username, shop_id)
        
        await state.clear()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Fehler: {e}")
        await state.clear()
