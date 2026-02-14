from aiogram import Router, types, F
from aiogram.filters import Command
from config import Config
from services.db_service import (
    get_all_users_stats, 
    get_pro_users_list,
    get_free_users_list,
    get_user_by_id
)
from services.subscription import activate_pro_subscription, cancel_subscription
from core.strings import Messages

router = Router()

def is_master_admin(user_id: int) -> bool:
    """Prüft ob User Master-Admin ist"""
    return user_id in Config.ADMIN_IDS


@router.message(Command("master"))
async def master_admin_menu(message: types.Message):
    """Master-Admin Dashboard mit Statistiken"""
    if not is_master_admin(message.from_user.id):
        return

    stats = await get_all_users_stats()
    
    text = Messages.MASTER_DASHBOARD.format(
        total_users=stats["total_users"],
        free_users=stats["free_users"],
        pro_users=stats["pro_users"],
        total_products=stats["total_products"],
        total_orders=stats["total_orders"]
    )
    
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("grantpro"))
async def master_grant_pro(message: types.Message):
    """PRO-Status aktivieren für User"""
    if not is_master_admin(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ **Verwendung:**\n`/grantpro <Telegram_ID> [Monate]`\n\nBeispiel: `/grantpro 123456789 3`", parse_mode="Markdown")
        return

    try:
        target_id = int(args[1])
        months = int(args[2]) if len(args) > 2 else 1
        
        await activate_pro_subscription(target_id, months)
        
        await message.answer(
            f"✅ **PRO aktiviert!**\n\n"
            f"User: `{target_id}`\n"
            f"Dauer: `{months} Monat{'e' if months > 1 else ''}`",
            parse_mode="Markdown"
        )
        
        # Benachrichtigung an User senden
        try:
            await message.bot.send_message(
                target_id,
                f"🎉 **PRO aktiviert!**\n\n"
                f"Dein Account wurde für **{months} Monat{'e' if months > 1 else ''}** auf PRO gesetzt.\n\n"
                f"Du hast nun Zugriff auf:\n"
                f"✅ Unbegrenzt Produkte\n"
                f"✅ Kategorien & Bilder\n"
                f"✅ Mehr Zahlungsmethoden\n"
                f"✅ Eigener Bot-Token",
                parse_mode="Markdown"
            )
        except:
            pass
            
    except Exception as e:
        await message.answer(f"❌ Fehler: {e}")


@router.message(Command("revokepro"))
async def master_revoke_pro(message: types.Message):
    """PRO-Status entfernen"""
    if not is_master_admin(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ **Verwendung:** `/revokepro <Telegram_ID>`", parse_mode="Markdown")
        return

    try:
        target_id = int(args[1])
        await cancel_subscription(target_id)
        
        await message.answer(f"🚫 **PRO entfernt!**\nUser `{target_id}` ist jetzt FREE.", parse_mode="Markdown")
        
        # Benachrichtigung
        try:
            await message.bot.send_message(
                target_id,
                "⚠️ **PRO-Status beendet**\n\nDein PRO-Account wurde deaktiviert. Upgrade erneut für volle Features.",
                parse_mode="Markdown"
            )
        except:
            pass
            
    except Exception as e:
        await message.answer(f"❌ Fehler: {e}")


@router.message(Command("userinfo"))
async def master_user_info(message: types.Message):
    """Detaillierte User-Info anzeigen"""
    if not is_master_admin(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ **Verwendung:** `/userinfo <Telegram_ID>`", parse_mode="Markdown")
        return

    try:
        target_id = int(args[1])
        user = await get_user_by_id(target_id)
        
        if not user:
            await message.answer("❌ User nicht gefunden.")
            return
        
        # Zahlungsmethoden
        payment_methods = []
        if user.get("wallet_btc"):
            payment_methods.append("BTC")
        if user.get("wallet_ltc"):
            payment_methods.append("LTC")
        if user.get("wallet_eth"):
            payment_methods.append("ETH")
        if user.get("wallet_sol"):
            payment_methods.append("SOL")
        if user.get("paypal_email"):
            payment_methods.append("PayPal")
        
        payment_str = ", ".join(payment_methods) if payment_methods else "Keine"
        
        info = (
            f"👤 **User Info**\n\n"
            f"🆔 ID: `{user['id']}`\n"
            f"👤 Username: @{user.get('username', 'N/A')}\n"
            f"💎 Status: {'**PRO**' if user.get('is_pro') else 'FREE'}\n"
            f"🏪 Shop-ID: `{user.get('shop_id', 'N/A')}`\n"
            f"💳 Zahlungen: {payment_str}\n"
            f"🤖 Bot-Token: {'✅ Konfiguriert' if user.get('custom_bot_token') else '❌ Nicht gesetzt'}\n"
            f"📅 Erstellt: {user.get('created_at', 'N/A')[:10]}"
        )
        
        if user.get("expiry_date"):
            info += f"\n⏰ Ablauf: {user.get('expiry_date')[:10]}"
        
        await message.answer(info, parse_mode="Markdown")
        
    except Exception as e:
        await message.answer(f"❌ Fehler: {e}")


@router.message(Command("listpro"))
async def list_pro_users(message: types.Message):
    """Liste aller PRO-User"""
    if not is_master_admin(message.from_user.id):
        return
    
    pro_users = await get_pro_users_list()
    
    if not pro_users:
        await message.answer("Keine PRO-User vorhanden.")
        return
    
    text = "💎 **PRO-User Liste:**\n\n"
    for user in pro_users[:20]:  # Max 20 anzeigen
        username = user.get('username', 'N/A')
        user_id = user.get('id')
        expiry = user.get('expiry_date', 'N/A')[:10] if user.get('expiry_date') else 'Kein Ablauf'
        text += f"• @{username} (`{user_id}`) - {expiry}\n"
    
    if len(pro_users) > 20:
        text += f"\n_...und {len(pro_users) - 20} weitere_"
    
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("listfree"))
async def list_free_users(message: types.Message):
    """Liste aller FREE-User"""
    if not is_master_admin(message.from_user.id):
        return
    
    free_users = await get_free_users_list()
    
    if not free_users:
        await message.answer("Keine FREE-User vorhanden.")
        return
    
    text = "🆓 **FREE-User Liste:**\n\n"
    for user in free_users[:20]:  # Max 20 anzeigen
        username = user.get('username', 'N/A')
        user_id = user.get('id')
        text += f"• @{username} (`{user_id}`)\n"
    
    if len(free_users) > 20:
        text += f"\n_...und {len(free_users) - 20} weitere_"
    
    await message.answer(text, parse_mode="Markdown")
