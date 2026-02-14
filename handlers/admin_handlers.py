from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.db_service import (
    add_product, get_user_products, delete_product,
    confirm_order, refill_stock, get_stock_count, get_user_by_id,
    get_user_categories, create_category, delete_category,
    get_product_by_id, update_product
)
from core.validator import can_add_product, can_use_categories, can_upload_images
from core.utils import upload_image_to_telegram
from core.strings import Buttons, Messages

router = Router()

# ========================================
# FSM STATES
# ========================================

class ProductForm(StatesGroup):
    name = State()
    description = State()
    price = State()
    category = State()  # PRO
    image = State()  # PRO
    content = State()

class RefillForm(StatesGroup):
    product_id = State()
    content = State()

class CategoryForm(StatesGroup):
    name = State()


# ========================================
# ADMIN MENU
# ========================================

@router.message(Command("start"))
async def cmd_start_handler(message: types.Message, is_owner: bool = False, shop_owner_id: int = None):
    """Start-Handler für Shop-Bots"""
    if is_owner:
        await admin_menu(message, is_owner=True)
    elif shop_owner_id:
        # Kunde besucht Shop
        from handlers.customer_handlers import show_shop_catalog
        await message.answer("🏪 **Willkommen im Shop!**")
        await show_shop_catalog(message, shop_owner_id)
    else:
        await message.answer("👋 Willkommen! Nutze /admin um deinen Shop zu verwalten.")


@router.message(F.text == Buttons.ADMIN_MANAGE)
@router.message(Command("admin"))
async def admin_menu(message: types.Message, is_owner: bool = False):
    """Admin-Menü anzeigen"""
    user = await get_user_by_id(message.from_user.id)
    if not user:
        return

    is_pro = user.get("is_pro", False)
    shop_id = user.get("shop_id", "Wird generiert...")
    
    # Bot-Info holen
    bot_info = await message.bot.get_me()
    shop_link = f"https://t.me/{bot_info.username}?start={shop_id}"
    
    # Keyboard erstellen
    kb = [
        [types.KeyboardButton(text=Buttons.ADD_PRODUCT)],
        [types.KeyboardButton(text=Buttons.LIST_PRODUCTS)],
        [types.KeyboardButton(text=Buttons.SETTINGS)],
    ]
    
    # PRO: Kategorien-Verwaltung
    if is_pro:
        kb.insert(2, [types.KeyboardButton(text=Buttons.MANAGE_CATEGORIES)])
    
    kb.append([types.KeyboardButton(text=Buttons.MAIN_MENU)])
    
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    
    text = Messages.ADMIN_WELCOME.format(
        shop_id=shop_id,
        shop_link=shop_link
    )
    
    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


# ========================================
# PRODUKT HINZUFÜGEN
# ========================================

@router.message(F.text == Buttons.ADD_PRODUCT)
async def start_add_product(message: types.Message, state: FSMContext):
    """Produkt-Erstellung starten"""
    can_add, reason = await can_add_product(message.from_user.id)
    
    if not can_add:
        await message.answer(Messages.LIMIT_REACHED)
        return
    
    await state.set_state(ProductForm.name)
    await message.answer(Messages.ASK_PRODUCT_NAME)


@router.message(ProductForm.name)
async def process_product_name(message: types.Message, state: FSMContext):
    """Name speichern"""
    await state.update_data(name=message.text)
    await state.set_state(ProductForm.description)
    await message.answer(Messages.ASK_PRODUCT_DESC)


@router.message(ProductForm.description)
async def process_product_description(message: types.Message, state: FSMContext):
    """Beschreibung speichern"""
    await state.update_data(description=message.text)
    await state.set_state(ProductForm.price)
    await message.answer(Messages.ASK_PRODUCT_PRICE)


@router.message(ProductForm.price)
async def process_product_price(message: types.Message, state: FSMContext):
    """Preis speichern"""
    try:
        price = float(message.text.replace(",", "."))
        if price <= 0:
            raise ValueError("Preis muss positiv sein")
        
        await state.update_data(price=price)
        
        # Prüfe ob User PRO ist -> Kategorien & Bilder
        user = await get_user_by_id(message.from_user.id)
        is_pro = user.get("is_pro", False)
        
        if is_pro and await can_use_categories(message.from_user.id):
            # PRO: Kategorie auswählen
            categories = await get_user_categories(message.from_user.id)
            
            if categories:
                kb = []
                for cat in categories:
                    kb.append([types.InlineKeyboardButton(
                        text=cat['name'],
                        callback_data=f"cat_{cat['name']}"
                    )])
                kb.append([types.InlineKeyboardButton(
                    text=Buttons.SKIP_CATEGORY,
                    callback_data="skip_category"
                )])
                
                await state.set_state(ProductForm.category)
                await message.answer(
                    Messages.ASK_PRODUCT_CATEGORY,
                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                    parse_mode="Markdown"
                )
            else:
                # Keine Kategorien -> Skip zu Bild
                await state.set_state(ProductForm.image)
                await ask_for_image(message, state)
        else:
            # FREE: Direkt zu Lagerbestand
            await state.set_state(ProductForm.content)
            await ask_for_stock(message, state)
            
    except ValueError:
        await message.answer("❌ Bitte eine gültige Zahl eingeben (z.B. 12.50)")


@router.callback_query(F.data.startswith("cat_"))
async def process_category_selection(callback: types.CallbackQuery, state: FSMContext):
    """Kategorie ausgewählt"""
    category_name = callback.data.replace("cat_", "")
    await state.update_data(category=category_name)
    
    # Weiter zu Bild
    await state.set_state(ProductForm.image)
    await callback.message.edit_text(f"✅ Kategorie: **{category_name}**", parse_mode="Markdown")
    await ask_for_image(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "skip_category")
async def skip_category_selection(callback: types.CallbackQuery, state: FSMContext):
    """Kategorie überspringen"""
    await state.update_data(category=None)
    await state.set_state(ProductForm.image)
    await callback.message.edit_text("⏭ Kategorie übersprungen")
    await ask_for_image(callback.message, state)
    await callback.answer()


async def ask_for_image(message: types.Message, state: FSMContext):
    """Bild-Upload anfordern (PRO)"""
    kb = [[types.InlineKeyboardButton(
        text=Buttons.SKIP_IMAGE,
        callback_data="skip_image"
    )]]
    
    await message.answer(
        Messages.ASK_PRODUCT_IMAGE,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown"
    )


@router.message(ProductForm.image, F.photo)
async def process_product_image(message: types.Message, state: FSMContext):
    """Bild gespeichert"""
    # Größtes Bild nehmen
    photo = message.photo[-1]
    file_id = photo.file_id
    
    image_url = await upload_image_to_telegram(message.bot, file_id)
    await state.update_data(image_url=image_url)
    
    await message.answer("✅ Bild gespeichert!")
    await state.set_state(ProductForm.content)
    await ask_for_stock(message, state)


@router.callback_query(F.data == "skip_image")
async def skip_image_upload(callback: types.CallbackQuery, state: FSMContext):
    """Bild überspringen"""
    await state.update_data(image_url=None)
    await state.set_state(ProductForm.content)
    await callback.message.edit_text("⏭ Bild übersprungen")
    await ask_for_stock(callback.message, state)
    await callback.answer()


async def ask_for_stock(message: types.Message, state: FSMContext):
    """Lagerbestand anfordern"""
    kb = [[types.InlineKeyboardButton(
        text=Buttons.SKIP_STOCK,
        callback_data="skip_stock"
    )]]
    
    await message.answer(
        "📦 **Lagerbestand hinzufügen (Optional)**\n\n"
        "Sende die Daten (eine pro Zeile) oder überspringe.",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "skip_stock")
async def skip_stock_process(callback: types.CallbackQuery, state: FSMContext):
    """Lagerbestand überspringen - Produkt erstellen"""
    data = await state.get_data()
    
    product = await add_product(
        owner_id=callback.from_user.id,
        name=data['name'],
        price=data['price'],
        content="",
        description=data['description'],
        category=data.get('category'),
        image_url=data.get('image_url')
    )
    
    await state.clear()
    await callback.message.edit_text(
        Messages.PRODUCT_ADDED.format(name=data['name']),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(ProductForm.content)
async def process_product_content(message: types.Message, state: FSMContext):
    """Lagerbestand gespeichert - Produkt erstellen"""
    data = await state.get_data()
    
    product = await add_product(
        owner_id=message.from_user.id,
        name=data['name'],
        price=data['price'],
        content=message.text,
        description=data['description'],
        category=data.get('category'),
        image_url=data.get('image_url')
    )
    
    await state.clear()
    await message.answer(Messages.PRODUCT_ADDED.format(name=data['name']))


# ========================================
# PRODUKTE AUFLISTEN
# ========================================

@router.message(F.text == Buttons.LIST_PRODUCTS)
async def list_admin_products(message: types.Message):
    """Alle eigenen Produkte auflisten"""
    user = await get_user_by_id(message.from_user.id)
    is_pro = user.get("is_pro", False)
    
    products = await get_user_products(message.from_user.id)
    
    if not products:
        await message.answer("Du hast noch keine Produkte angelegt.")
        return
    
    for p in products:
        stock = await get_stock_count(p['id'])
        
        # Text zusammenstellen
        text = f"📦 **{p['name']}**\n"
        
        if is_pro and p.get('category'):
            text += f"📁 Kategorie: _{p['category']}_\n"
        
        text += f"\n{p.get('description', '')}\n"
        text += f"\n💰 Preis: {p['price']}€\n"
        text += f"🔢 Lager: `{stock}` Stück"
        
        # Buttons
        kb = [
            [types.InlineKeyboardButton(
                text=Buttons.REFILL_STOCK,
                callback_data=f"refill_{p['id']}"
            )],
            [types.InlineKeyboardButton(
                text=Buttons.DELETE_PRODUCT,
                callback_data=f"delete_{p['id']}"
            )]
        ]
        
        # Bild falls vorhanden (PRO)
        if is_pro and p.get('image_url'):
            try:
                await message.answer_photo(
                    photo=p['image_url'],
                    caption=text,
                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                    parse_mode="Markdown"
                )
            except:
                # Fallback ohne Bild
                await message.answer(
                    text,
                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                    parse_mode="Markdown"
                )
        else:
            await message.answer(
                text,
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
                parse_mode="Markdown"
            )


# ========================================
# LAGERBESTAND AUFFÜLLEN
# ========================================

@router.callback_query(F.data.startswith("refill_"))
async def start_refill(callback: types.CallbackQuery, state: FSMContext):
    """Lager-Nachfüllung starten"""
    pid = callback.data.split("_")[1]
    await state.update_data(refill_id=pid)
    await state.set_state(RefillForm.content)
    await callback.message.answer(Messages.STOCK_REFILL_PROMPT, parse_mode="Markdown")
    await callback.answer()


@router.message(RefillForm.content)
async def process_refill_content(message: types.Message, state: FSMContext):
    """Lagerbestand hinzufügen"""
    data = await state.get_data()
    pid = data.get('refill_id')
    
    if pid:
        added = await refill_stock(pid, message.from_user.id, message.text)
        await message.answer(Messages.REFILL_SUCCESS.format(count=added))
    
    await state.clear()


# ========================================
# PRODUKT LÖSCHEN
# ========================================

@router.callback_query(F.data.startswith("delete_"))
async def process_delete_product(callback: types.CallbackQuery):
    """Produkt löschen"""
    pid = callback.data.split("_")[1]
    success = await delete_product(pid, callback.from_user.id)
    
    if success:
        await callback.message.delete()
        await callback.answer("✅ Produkt gelöscht.", show_alert=True)
    else:
        await callback.answer("❌ Fehler beim Löschen.", show_alert=True)


# ========================================
# BESTELLUNG BESTÄTIGEN
# ========================================

@router.callback_query(F.data.startswith("confirm_"))
async def process_confirm_sale(callback: types.CallbackQuery):
    """Zahlung bestätigen & Ware senden"""
    order_id = callback.data.split("_")[1]
    
    # Order-Daten holen
    from core.supabase_client import db
    order = db.table("orders").select("*").eq("id", order_id).single().execute().data
    
    if not order:
        await callback.answer("❌ Bestellung nicht gefunden.", show_alert=True)
        return
    
    # Produkt-Info holen
    product = await get_product_by_id(order['product_id'])
    
    # Item aus Lager nehmen
    item = await confirm_order(order_id)
    
    if item == "sold_out":
        await callback.message.answer("❌ **Ausverkauft!**")
        await callback.answer()
        return
    
    if item:
        # Ware an Käufer senden
        await callback.bot.send_message(
            order['buyer_id'],
            Messages.SALE_CONFIRMED_BUYER.format(content=item),
            parse_mode="Markdown"
        )
        
        # Verkäufer benachrichtigen
        await callback.message.edit_text(
            Messages.SALE_CONFIRMED_SELLER.format(content=item),
            parse_mode="Markdown"
        )
        await callback.answer("✅ Ware gesendet!")
    else:
        await callback.answer("❌ Fehler", show_alert=True)


# ========================================
# KATEGORIEN VERWALTEN (PRO)
# ========================================

@router.message(F.text == Buttons.MANAGE_CATEGORIES)
async def manage_categories_menu(message: types.Message):
    """Kategorien-Verwaltung (PRO)"""
    if not await can_use_categories(message.from_user.id):
        await message.answer(Messages.CATEGORY_PRO_ONLY)
        return
    
    categories = await get_user_categories(message.from_user.id)
    
    text = Messages.CATEGORY_MENU.format(count=len(categories))
    
    kb = [[types.InlineKeyboardButton(
        text=Buttons.ADD_CATEGORY,
        callback_data="add_category"
    )]]
    
    # Bestehende Kategorien zum Löschen anzeigen
    for cat in categories:
        kb.append([types.InlineKeyboardButton(
            text=f"🗑 {cat['name']}",
            callback_data=f"delcat_{cat['id']}"
        )])
    
    await message.answer(
        text,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "add_category")
async def start_add_category(callback: types.CallbackQuery, state: FSMContext):
    """Kategorie hinzufügen"""
    await state.set_state(CategoryForm.name)
    await callback.message.answer(Messages.ASK_CATEGORY_NAME)
    await callback.answer()


@router.message(CategoryForm.name)
async def process_category_name(message: types.Message, state: FSMContext):
    """Kategorie erstellen"""
    category_name = message.text.strip()
    
    category = await create_category(
        owner_id=message.from_user.id,
        name=category_name
    )
    
    await state.clear()
    
    if category:
        await message.answer(Messages.CATEGORY_CREATED.format(name=category_name))
    else:
        await message.answer("❌ Fehler beim Erstellen (evtl. bereits vorhanden)")


@router.callback_query(F.data.startswith("delcat_"))
async def delete_category_handler(callback: types.CallbackQuery):
    """Kategorie löschen"""
    cat_id = int(callback.data.split("_")[1])
    
    success = await delete_category(cat_id, callback.from_user.id)
    
    if success:
        await callback.message.edit_text(Messages.CATEGORY_DELETED)
        await callback.answer("✅ Gelöscht!")
    else:
        await callback.answer("❌ Fehler", show_alert=True)

