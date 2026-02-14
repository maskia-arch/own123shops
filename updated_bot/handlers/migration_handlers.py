from aiogram import Router, types, F
from services.migration import (
    migrate_products_to_custom_bot,
    check_migration_status,
    get_migration_summary
)
from services.db_service import get_user_by_id

router = Router()


@router.callback_query(F.data == "start_migration")
async def start_migration_process(callback: types.CallbackQuery):
    """Migration-Prozess starten"""
    user = await get_user_by_id(callback.from_user.id)
    
    if not user:
        await callback.answer("❌ User nicht gefunden", show_alert=True)
        return
    
    if not user.get("is_pro"):
        await callback.answer("⚠️ PRO-Status erforderlich", show_alert=True)
        return
    
    if not user.get("custom_bot_token"):
        await callback.answer("⚠️ Kein Bot-Token hinterlegt", show_alert=True)
        return
    
    # Status prüfen
    status = await check_migration_status(callback.from_user.id)
    
    if status["migrated"]:
        await callback.message.answer(
            "✅ **Migration bereits durchgeführt**\n\n"
            "Deine Produkte sind bereits auf deinen eigenen Bot übertragen.",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    if not status["can_migrate"]:
        await callback.message.answer(
            "⚠️ **Migration nicht möglich**\n\n"
            "Entweder hast du keine Produkte oder die Voraussetzungen sind nicht erfüllt.",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    # Zusammenfassung anzeigen
    summary = await get_migration_summary(callback.from_user.id)
    
    kb = [
        [types.InlineKeyboardButton(
            text="✅ Ja, jetzt übertragen",
            callback_data="confirm_migration"
        )],
        [types.InlineKeyboardButton(
            text="❌ Abbrechen",
            callback_data="cancel_migration"
        )]
    ]
    
    await callback.message.answer(
        summary,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_migration")
async def confirm_migration(callback: types.CallbackQuery):
    """Migration bestätigen und ausführen"""
    # Status-Nachricht
    status_msg = await callback.message.answer(
        "⏳ **Migration läuft...**\n\n"
        "├─ Produkte übertragen\n"
        "├─ Kategorien übertragen\n"
        "└─ Konfiguration anpassen\n\n"
        "Bitte warten...",
        parse_mode="Markdown"
    )
    
    # Migration durchführen
    result = await migrate_products_to_custom_bot(callback.from_user.id)
    
    if result["success"]:
        user = await get_user_by_id(callback.from_user.id)
        
        # Bot-Info holen
        from aiogram import Bot
        try:
            custom_bot = Bot(token=user["custom_bot_token"])
            bot_info = await custom_bot.get_me()
            bot_username = bot_info.username
            await custom_bot.session.close()
        except:
            bot_username = "dein_bot"
        
        await status_msg.edit_text(
            f"✅ **Migration erfolgreich!**\n\n"
            f"📦 Produkte: {result['migrated_count']}\n"
            f"📁 Kategorien: {result['categories_migrated']}\n\n"
            f"**Dein Shop ist jetzt über deinen eigenen Bot verfügbar:**\n"
            f"🔗 `https://t.me/{bot_username}`\n\n"
            f"💡 **Wichtig:**\n"
            f"• Deine Produkte sind jetzt NUR über @{bot_username} verfügbar\n"
            f"• Der Master-Bot zeigt deine Produkte nicht mehr an\n"
            f"• Alle Zahlungsdaten bleiben gleich\n"
            f"• Lagerbestände bleiben erhalten",
            parse_mode="Markdown"
        )
        
        # Original-Nachricht löschen
        try:
            await callback.message.delete()
        except:
            pass
    else:
        await status_msg.edit_text(
            f"❌ **Migration fehlgeschlagen**\n\n"
            f"Fehler: {result.get('error', 'Unbekannt')}\n\n"
            f"Bitte kontaktiere den Support.",
            parse_mode="Markdown"
        )
    
    await callback.answer()


@router.callback_query(F.data == "cancel_migration")
async def cancel_migration(callback: types.CallbackQuery):
    """Migration abbrechen"""
    await callback.message.edit_text(
        "❌ **Migration abgebrochen**\n\n"
        "Du kannst die Migration jederzeit in den Einstellungen starten.",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "check_migration_status")
async def check_migration_status_handler(callback: types.CallbackQuery):
    """Migration-Status anzeigen"""
    status = await check_migration_status(callback.from_user.id)
    user = await get_user_by_id(callback.from_user.id)
    
    if status["migrated"]:
        # Bot-Info holen
        try:
            from aiogram import Bot
            custom_bot = Bot(token=user["custom_bot_token"])
            bot_info = await custom_bot.get_me()
            bot_username = bot_info.username
            await custom_bot.session.close()
            
            text = (
                f"✅ **Migration abgeschlossen**\n\n"
                f"Dein Shop läuft über: @{bot_username}\n"
                f"Produkte: {status['product_count']}"
            )
        except:
            text = "✅ Migration abgeschlossen"
    else:
        text = (
            f"📊 **Migration-Status**\n\n"
            f"Produkte: {status['product_count']}\n"
            f"Eigener Bot: {'✅ Ja' if status['has_custom_bot'] else '❌ Nein'}\n"
            f"PRO: {'✅ Ja' if status['is_pro'] else '❌ Nein'}\n\n"
        )
        
        if status["can_migrate"]:
            text += "✅ Migration möglich!"
        else:
            text += "⚠️ Migration noch nicht möglich"
    
    await callback.answer(text, show_alert=True)
