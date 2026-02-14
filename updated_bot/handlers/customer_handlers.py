from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.db_service import (
    get_user_products, create_order, get_stock_count,
    get_user_by_id, get_user_categories, get_product_by_id
)
from core.utils import format_payment_methods
from core.strings import Buttons, Messages

router = Router()


async def show_shop_catalog(message: types.Message, owner_id: int, category: str = None):
    """
    Zeigt Shop-Katalog (Kundenansicht)
    Optional gefiltert nach Kategorie
    """
    user = await get_user_by_id(owner_id)
    if not user:
        await message.answer("❌ Shop nicht gefunden.")
        return
    
    is_pro = user.get("is_pro", False)
    
    # Produkte holen (optional nach Kategorie gefiltert)
    products = await get_user_products(owner_id, category=category)
    
    if not products:
        await message.answer(Messages.CATALOG_EMPTY)
        return
    
    # Bei PRO: Kategorien-Navigation anbieten
    if is_pro and not category:
        categories = await get_user_categories(owner_id)
        if categories:
            kb = []
            for cat in categories:
                # Zähle Produkte in Kategorie
                cat_products = await get_user_products(owner_id, category=cat['name'])
                count = len(cat_products)
                kb.append([types.InlineKeyboardButton(
                    text=f"📁 {cat['name']} ({count})",
                    callback_data=f"viewcat_{owner_id}_{cat['name']}"
                )])
            
            kb.append([types.InlineKeyboardButton(
                text=Buttons.VIEW_ALL,
                callback_data=f"viewall_{owner_id}"
            )])
            
            await message.answer(
                "📁 **Kategorien:**\nWähle eine Kategorie oder zeige alle an:",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                parse_mode="Markdown"
            )
    
    # Produkte anzeigen
    for product in products:
        stock_count = await get_stock_count(product['id'])
        stock_text = f"✅ Auf Lager: `{stock_count}`" if stock_count > 0 else "❌ Ausverkauft"
        
        # Text mit oder ohne Kategorie
        if is_pro and product.get('category'):
            caption = Messages.PRODUCT_DETAILS_WITH_CATEGORY.format(
                name=product['name'],
                category=product['category'],
                desc=product.get('description', 'Keine Beschreibung'),
                price=product['price'],
                stock=stock_text
            )
        else:
            caption = Messages.PRODUCT_DETAILS.format(
                name=product['name'],
                desc=product.get('description', 'Keine Beschreibung'),
                price=product['price'],
                stock=stock_text
            )
        
        # Buttons
        builder = InlineKeyboardBuilder()
        if stock_count > 0:
            builder.row(types.InlineKeyboardButton(
                text=Buttons.BUY_NOW.format(price=product['price']),
                callback_data=f"buy_{product['id']}_{owner_id}"
            ))
        else:
            builder.row(types.InlineKeyboardButton(
                text=Buttons.CONTACT_SELLER,
                url=f"tg://user?id={owner_id}"
            ))
        
        # Mit oder ohne Bild senden
        if is_pro and product.get('image_url'):
            try:
                await message.answer_photo(
                    photo=product['image_url'],
                    caption=caption,
                    reply_markup=builder.as_markup(),
                    parse_mode="Markdown"
                )
            except:
                # Fallback ohne Bild
                await message.answer(
                    caption,
                    reply_markup=builder.as_markup(),
                    parse_mode="Markdown"
                )
        else:
            await message.answer(
                caption,
                reply_markup=builder.as_markup(),
                parse_mode="Markdown"
            )


@router.callback_query(F.data.startswith("viewcat_"))
async def view_category(callback: types.CallbackQuery):
    """Produkte einer Kategorie anzeigen"""
    parts = callback.data.split("_", 2)
    owner_id = int(parts[1])
    category = parts[2]
    
    await callback.message.answer(f"📁 **Kategorie: {category}**", parse_mode="Markdown")
    await show_shop_catalog(callback.message, owner_id, category=category)
    await callback.answer()


@router.callback_query(F.data.startswith("viewall_"))
async def view_all_products(callback: types.CallbackQuery):
    """Alle Produkte anzeigen"""
    owner_id = int(callback.data.split("_")[1])
    
    await callback.message.answer("📋 **Alle Produkte:**", parse_mode="Markdown")
    await show_shop_catalog(callback.message, owner_id)
    await callback.answer()


@router.message(F.text == Buttons.VIEW_SHOP)
async def browse_own_shop(message: types.Message):
    """Eigenen Shop in Kundenansicht zeigen"""
    await message.answer("👀 **Vorschau deines Shops:**", parse_mode="Markdown")
    await show_shop_catalog(message, message.from_user.id)


@router.callback_query(F.data.startswith("buy_"))
async def start_purchase(callback: types.CallbackQuery):
    """Kauf-Prozess starten"""
    data = callback.data.split("_")
    product_id = data[1]
    seller_id = int(data[2])
    
    # Stock prüfen
    stock_count = await get_stock_count(product_id)
    if stock_count <= 0:
        await callback.answer("⚠️ Leider ausverkauft!", show_alert=True)
        return
    
    # Bestellung erstellen
    order = await create_order(
        buyer_id=callback.from_user.id,
        product_id=product_id,
        seller_id=seller_id
    )
    
    if not order:
        await callback.answer("❌ Fehler beim Erstellen der Bestellung.", show_alert=True)
        return
    
    # Verkäufer-Daten holen
    seller = await get_user_by_id(seller_id)
    is_pro = seller.get("is_pro", False)
    
    # Zahlungsmethoden zusammenstellen
    payment_methods = []
    
    # BTC & LTC (immer)
    if seller.get("wallet_btc"):
        payment_methods.append(f"₿ **BTC:** `{seller['wallet_btc']}`")
    if seller.get("wallet_ltc"):
        payment_methods.append(f"Ł **LTC:** `{seller['wallet_ltc']}`")
    
    # PRO: ETH, SOL, PayPal
    if is_pro:
        if seller.get("wallet_eth"):
            payment_methods.append(f"Ξ **ETH:** `{seller['wallet_eth']}`")
        if seller.get("wallet_sol"):
            payment_methods.append(f"◎ **SOL:** `{seller['wallet_sol']}`")
        if seller.get("paypal_email"):
            payment_methods.append(f"🅿️ **PayPal (F&F):** `{seller['paypal_email']}`")
    
    # Text für Käufer
    if payment_methods:
        payment_text = Messages.ORDER_INITIATED.format(
            payment_methods="\n".join(payment_methods)
        )
    else:
        payment_text = Messages.NO_PAYMENT_METHODS
    
    await callback.message.answer(payment_text, parse_mode="Markdown")
    
    # Verkäufer benachrichtigen
    product = await get_product_by_id(product_id)
    
    confirm_kb = [[types.InlineKeyboardButton(
        text=Buttons.CONFIRM_PAYMENT,
        callback_data=f"confirm_{order['id']}"
    )]]
    
    try:
        await callback.bot.send_message(
            chat_id=seller_id,
            text=Messages.NEW_ORDER_SELLER.format(
                username=callback.from_user.username or 'Unbekannt',
                user_id=callback.from_user.id,
                product_name=product['name'] if product else 'Unbekannt',
                price=product['price'] if product else 0,
                order_id=order['id']
            ),
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=confirm_kb),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Fehler beim Senden an Verkäufer: {e}")
    
    await callback.answer("✅ Bestellung aufgenommen!")
