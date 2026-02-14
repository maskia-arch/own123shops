from aiogram import Router, types, F
from services.db_service import get_user_by_id
from services.subscription import activate_pro_subscription
from config import Config
from core.strings import Buttons, Messages

router = Router()


@router.message(F.text == Buttons.UPGRADE_PRO)
async def show_upgrade_options(message: types.Message):
    """PRO-Upgrade Optionen anzeigen"""
    user = await get_user_by_id(message.from_user.id)
    
    if user and user.get("is_pro"):
        await message.answer(
            f"✨ Du nutzt bereits **{Config.BRAND_NAME} PRO**!",
            parse_mode="Markdown"
        )
        return

    kb = [
        [types.InlineKeyboardButton(
            text="Litecoin (LTC)",
            callback_data="pay_ltc"
        )],
        [types.InlineKeyboardButton(
            text="Andere Methoden (Support)",
            callback_data="pay_fiat"
        )]
    ]
    
    await message.answer(
        Messages.UPGRADE_INFO,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "pay_ltc")
async def pay_ltc_info(callback: types.CallbackQuery):
    """LTC-Zahlung anzeigen"""
    # Hier deine LTC-Wallet Adresse eintragen
    wallet = "ltc1q73t84vd9mj4yt2pkgmtx8cfmductgf8ds87dm5"
    
    # Admin-Buttons für schnelle Freischaltung
    confirm_kb = [[types.InlineKeyboardButton(
        text=f"✅ Zahlung bestätigen (ID: {callback.from_user.id})",
        callback_data=f"admin_confirm_pro_{callback.from_user.id}"
    )]]
    
    # Benachrichtigung an alle Admins senden
    for admin_id in Config.ADMIN_IDS:
        try:
            await callback.bot.send_message(
                chat_id=admin_id,
                text=(
                    f"🔔 **Kaufinteresse PRO-Version**\n\n"
                    f"👤 User: @{callback.from_user.username or 'Kein Username'}\n"
                    f"🆔 ID: `{callback.from_user.id}`\n\n"
                    f"Hat soeben die LTC-Zahlungsdaten angefordert."
                ),
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=confirm_kb),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Fehler beim Senden an Admin {admin_id}: {e}")
            continue

    # Info an User
    await callback.message.answer(
        f"📥 **Zahlung via Litecoin (LTC)**\n\n"
        f"Sende LTC im Wert von **{Config.PRO_SUBSCRIPTION_PRICE}€** an:\n\n"
        f"`{wallet}`\n\n"
        f"⚠️ **Wichtig:**\n"
        f"Sende nach der Transaktion bitte einen Screenshot als Beleg.\n"
        f"Sobald die Zahlung bestätigt ist, wird dein Account aktiviert.",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_confirm_pro_"))
async def process_admin_confirm_pro(callback: types.CallbackQuery):
    """Admin bestätigt PRO-Zahlung"""
    if callback.from_user.id not in Config.ADMIN_IDS:
        await callback.answer("❌ Keine Berechtigung.", show_alert=True)
        return

    target_id = int(callback.data.split("_")[-1])
    
    try:
        # PRO aktivieren (1 Monat)
        await activate_pro_subscription(target_id, months=1)
        
        # Nachricht updaten
        await callback.message.edit_text(
            f"{callback.message.text}\n\n"
            f"✅ **Bestätigt!** User `{target_id}` ist jetzt **PRO**.",
            parse_mode="Markdown"
        )
        
        # User benachrichtigen
        await callback.bot.send_message(
            target_id,
            f"🎉 **{Config.BRAND_NAME} PRO aktiviert!**\n\n"
            f"Dein Upgrade wurde soeben aktiviert.\n\n"
            f"Du kannst jetzt:\n"
            f"✅ Unbegrenzt Produkte anlegen\n"
            f"✅ Kategorien & Bilder nutzen\n"
            f"✅ Mehr Zahlungsmethoden verwenden\n"
            f"✅ Eigenen Bot-Token einrichten",
            parse_mode="Markdown"
        )
        
        await callback.answer("✅ User erfolgreich freigeschaltet!")
        
    except Exception as e:
        await callback.answer(f"❌ Fehler: {e}", show_alert=True)


@router.callback_query(F.data == "pay_fiat")
async def pay_fiat_info(callback: types.CallbackQuery):
    """Alternative Zahlungsmethoden"""
    await callback.message.answer(
        "💳 **Alternative Zahlungsmethoden**\n\n"
        "Für PayPal, Kreditkarte oder andere Methoden kontaktiere bitte den Support.\n\n"
        "Schreibe einfach dem Admin eine Nachricht.",
        parse_mode="Markdown"
    )
    await callback.answer()
