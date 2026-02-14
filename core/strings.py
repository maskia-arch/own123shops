class Buttons:
    # Hauptmenü / Navigation
    MAIN_MENU = "🏠 Hauptmenü"
    ADMIN_MANAGE = "🛒 Shop verwalten"
    VIEW_SHOP = "🛍 Shop ansehen"
    UPGRADE_PRO = "💎 Upgrade auf Pro (10€/Monat)"
    
    # Admin Bereich
    ADD_PRODUCT = "➕ Produkt hinzufügen"
    LIST_PRODUCTS = "📋 Meine Produkte"
    MANAGE_CATEGORIES = "📁 Kategorien verwalten"  # PRO
    SETTINGS = "⚙️ Shop-Einstellungen"
    
    # Shop Einstellungen
    CONF_BOT = "⚙️ Shop-Bot konfigurieren"
    CHANGE_BTC = "Bitcoin (BTC) ändern"
    CHANGE_LTC = "Litecoin (LTC) ändern"
    CHANGE_ETH = "Ethereum (ETH) ändern [PRO]"
    CHANGE_SOL = "Solana (SOL) ändern [PRO]"
    CHANGE_PAYPAL = "PayPal (F&F) ändern [PRO]"
    OWN_BOT_TOKEN = "🤖 Eigener Bot-Token"
    
    # Inline Buttons
    SKIP_STOCK = "⏭ Lager leer lassen"
    SKIP_CATEGORY = "⏭ Keine Kategorie"
    SKIP_IMAGE = "⏭ Kein Bild"
    REFILL_STOCK = "➕ Lager auffüllen"
    DELETE_PRODUCT = "🗑 Löschen"
    EDIT_PRODUCT = "✏️ Bearbeiten"
    BUY_NOW = "🛒 Jetzt kaufen ({price}€)"
    CONTACT_SELLER = "📧 Verkäufer kontaktieren"
    CONFIRM_PAYMENT = "✅ Zahlung erhalten (Ware senden)"
    
    # Kategorien
    ADD_CATEGORY = "➕ Kategorie erstellen"
    DELETE_CATEGORY = "🗑 Kategorie löschen"
    VIEW_BY_CATEGORY = "📁 Nach Kategorie"
    VIEW_ALL = "📋 Alle anzeigen"


class Messages:
    # Dashboard & Admin
    WELCOME_BACK = (
        "🎉 **Willkommen bei Own1Shop!**\n\n"
        "📊 **Dein Status:** {status}\n"
        "🆔 **Shop-ID:** `{shop_id}`\n\n"
        "Verwalte deinen digitalen Shop direkt über Telegram!"
    )
    
    ADMIN_WELCOME = (
        "🛠 **Shop-Verwaltung**\n\n"
        "🆔 Shop-ID: `{shop_id}`\n"
        "🔗 Kunden-Link:\n`{shop_link}`\n\n"
        "💡 Teile diesen Link mit deinen Kunden, damit sie deinen Shop besuchen können!"
    )
    
    # Master Admin
    MASTER_DASHBOARD = (
        "👑 **System-Admin Dashboard**\n\n"
        "📊 **Statistiken:**\n"
        "├─ 👥 Gesamt-User: `{total_users}`\n"
        "├─ 🆓 FREE-User: `{free_users}`\n"
        "├─ 💎 PRO-User: `{pro_users}`\n"
        "├─ 📦 Produkte: `{total_products}`\n"
        "└─ 💳 Bestellungen: `{total_orders}`\n\n"
        "**Verfügbare Befehle:**\n"
        "• `/grantpro <ID>` - PRO aktivieren\n"
        "• `/revokepro <ID>` - PRO entfernen\n"
        "• `/userinfo <ID>` - User-Details\n"
        "• `/listpro` - Alle PRO-User anzeigen\n"
        "• `/listfree` - Alle FREE-User anzeigen"
    )
    
    # Produkt Management
    ASK_PRODUCT_NAME = "📝 Wie soll das Produkt heißen?"
    ASK_PRODUCT_DESC = "📄 Gib eine kurze Beschreibung ein:"
    ASK_PRODUCT_PRICE = "💰 Was soll es kosten? (z.B. 12.50)"
    ASK_PRODUCT_CATEGORY = "📁 In welche Kategorie soll das Produkt? (Kategorie-Name)"
    ASK_PRODUCT_IMAGE = "🖼 Sende jetzt ein Bild für dieses Produkt (oder überspringe):"
    STOCK_REFILL_PROMPT = "📥 Sende die neuen Daten (eine pro Zeile):\n\nBeispiel:\nkey1:value1\nkey2:value2"
    PRODUCT_ADDED = "✅ Produkt **{name}** wurde erfolgreich erstellt!"
    REFILL_SUCCESS = "✅ `{count}` Einheiten wurden hinzugefügt!"
    LIMIT_REACHED = (
        "⚠️ **Limit erreicht!**\n\n"
        "Im FREE-Modus kannst du maximal **2 Produkte** anlegen.\n"
        "Upgrade auf PRO für unbegrenzte Produkte! 💎"
    )
    
    # Kategorien (PRO)
    CATEGORY_MENU = (
        "📁 **Kategorien-Verwaltung**\n\n"
        "Organisiere deine Produkte in Kategorien.\n"
        "Aktuelle Kategorien: {count}"
    )
    ASK_CATEGORY_NAME = "📝 Wie soll die neue Kategorie heißen?"
    CATEGORY_CREATED = "✅ Kategorie **{name}** wurde erstellt!"
    CATEGORY_DELETED = "🗑 Kategorie löschen!"
    CATEGORY_PRO_ONLY = "⚠️ Kategorien sind nur in der PRO-Version verfügbar! 💎"
    
    # Shop Einstellungen & Wallets
    SETTINGS_MENU_FREE = (
        "⚙️ **Shop-Einstellungen**\n\n"
        "**Zahlungsmethoden (FREE):**\n"
        "├─ ₿ BTC: `{btc}`\n"
        "└─ Ł LTC: `{ltc}`\n\n"
        "💎 **Upgrade auf PRO für:**\n"
        "• ETH, SOL & PayPal\n"
        "• Eigener Bot-Token\n"
        "• Kategorien & Bilder"
    )
    
    SETTINGS_MENU_PRO = (
        "⚙️ **Shop-Einstellungen**\n\n"
        "**Zahlungsmethoden:**\n"
        "├─ ₿ BTC: `{btc}`\n"
        "├─ Ł LTC: `{ltc}`\n"
        "├─ Ξ ETH: `{eth}`\n"
        "├─ ◎ SOL: `{sol}`\n"
        "└─ 🅿️ PayPal: `{paypal}`\n\n"
        "🤖 Bot-Token: `{token_status}`"
    )
    
    ASK_WALLET_ADDRESS = "Bitte sende mir jetzt deine Adresse/Email für **{method}**:"
    WALLET_SUCCESS = "✅ **Gespeichert!** Deine Zahlungsdaten wurden aktualisiert."
    WALLET_INVALID = "❌ Ungültiges Format! Bitte überprüfe die Adresse."
    TOKEN_PROMPT = "Bitte sende mir den **API-Token** deines Bots (vom @BotFather):"
    TOKEN_SUCCESS = "✅ **Token gespeichert!** Dein eigener Bot wird beim nächsten Neustart aktiviert."
    
    # Zahlungen & Shop (Kundensicht)
    SHOP_WELCOME = "🏪 **Willkommen im Shop von {owner_name}**\n\nDurchstöbere die verfügbaren Produkte:"
    CATALOG_EMPTY = "📭 Dieser Shop hat aktuell keine Produkte im Angebot."
    
    PRODUCT_DETAILS = (
        "📦 **{name}**\n\n"
        "📝 {desc}\n\n"
        "💰 Preis: **{price}€**\n"
        "🔢 Status: {stock}"
    )
    
    PRODUCT_DETAILS_WITH_CATEGORY = (
        "📦 **{name}**\n"
        "📁 Kategorie: _{category}_\n\n"
        "📝 {desc}\n\n"
        "💰 Preis: **{price}€**\n"
        "🔢 Status: {stock}"
    )
    
    ORDER_INITIATED = (
        "✅ **Bestellung eingeleitet!**\n\n"
        "Bitte sende den Betrag an eine der folgenden Adressen:\n\n"
        "{payment_methods}\n\n"
        "Sobald der Verkäufer die Zahlung bestätigt, erhältst du die Ware automatisch."
    )
    
    NO_PAYMENT_METHODS = (
        "⚠️ **Keine Zahlungsmethoden hinterlegt**\n\n"
        "Der Verkäufer hat noch keine Zahlungsdaten eingetragen.\n"
        "Bitte kontaktiere ihn direkt."
    )
    
    # Benachrichtigungen
    NEW_ORDER_SELLER = (
        "🔔 **Neue Bestellung!**\n\n"
        "👤 Kunde: @{username} (`{user_id}`)\n"
        "📦 Produkt: **{product_name}**\n"
        "💰 Preis: **{price}€**\n"
        "🆔 Bestell-ID: `{order_id}`\n\n"
        "Bestätige die Zahlung, um die Ware auszuliefern."
    )
    
    SALE_CONFIRMED_SELLER = "✅ **Verkauf abgeschlossen!**\nWare gesendet:\n`{content}`"
    SALE_CONFIRMED_BUYER = "🎉 **Zahlung bestätigt!**\n\nDeine Ware:\n`{content}`"
    
    # Upgrade / Pro
    UPGRADE_INFO = (
        "🚀 **Upgrade auf Own1Shop PRO**\n\n"
        "**Deine Vorteile:**\n"
        "✅ Unbegrenzt Produkte\n"
        "✅ Kategorien & Produktbilder\n"
        "✅ Mehr Zahlungsmethoden (ETH, SOL, PayPal)\n"
        "✅ Eigener Bot-Token (Branding)\n"
        "✅ Prioritäts-Support\n\n"
        "💰 **Preis: 10€ / Monat**\n\n"
        "Wähle eine Zahlungsmethode:"
    )
