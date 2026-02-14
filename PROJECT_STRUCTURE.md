# 📁 Projektstruktur

Übersicht über alle Dateien und deren Funktion.

---

## 📂 Verzeichnis-Struktur

```
own1shop-bot/
├── 📄 main.py                      # Entry Point - Bot-Orchestrierung
├── 📄 config.py                    # Konfiguration & Limits
├── 📄 requirements.txt             # Python Dependencies
├── 📄 version.txt                  # Version (2.0.0)
│
├── 📁 core/                        # Core Funktionalität
│   ├── __init__.py
│   ├── supabase_client.py          # Datenbank-Verbindung
│   ├── strings.py                  # Texte & Buttons
│   ├── utils.py                    # Hilfsfunktionen
│   ├── validator.py                # Feature-Validierung (FREE/PRO)
│   └── middlewares.py              # Shop-Kontext Middleware
│
├── 📁 handlers/                    # Request Handler (MVC: Controller)
│   ├── __init__.py
│   ├── master_admin_handlers.py    # System-Admin Befehle (/master)
│   ├── admin_handlers.py           # Shop-Verwaltung (Produkte, Kategorien)
│   ├── customer_handlers.py        # Kundenansicht (Shop-Katalog, Kauf)
│   ├── shop_settings.py            # Einstellungen (Wallets, Bot-Token)
│   └── payment_handlers.py         # Upgrade & Zahlungen
│
├── 📁 services/                    # Business Logic (MVC: Model)
│   ├── __init__.py
│   ├── db_service.py               # Datenbank-Operationen (CRUD)
│   └── subscription.py             # PRO-Subscription Management
│
├── 📁 bots/                        # Bot Router
│   ├── __init__.py
│   ├── master_bot.py               # Master-Bot Commands & Deep-Links
│   └── shop_logic.py               # Shop-Bots (PRO Feature)
│
├── 📁 tasks/                       # Background Tasks
│   ├── __init__.py
│   └── expiry_check.py             # Subscription-Ablauf prüfen (24h)
│
├── 📄 database_schema.sql          # Supabase SQL Schema
├── 📄 .env.example                 # Environment Variables Template
├── 📄 .gitignore                   # Git Ignore Rules
│
└── 📚 Dokumentation/
    ├── README.md                   # Hauptdokumentation
    ├── QUICKSTART.md               # Schnelleinstieg (10 Min)
    ├── DEPLOY.md                   # Deployment-Guide (render.com)
    ├── TESTING.md                  # Testing-Guide (Lokal)
    └── CHANGELOG.md                # Versions-Historie
```

---

## 🔍 Datei-Details

### 🎯 Entry Points

#### `main.py` (273 Zeilen)
**Funktion:** Bot-Orchestrierung
- Startet Master-Bot
- Startet PRO-User Shop-Bots
- Registriert Handler & Middleware
- Flask Health-Check für render.com
- Background-Tasks (Expiry-Check)

**Key Functions:**
- `main()` - Hauptfunktion
- `start_customer_bots()` - PRO-Bots starten

---

### ⚙️ Konfiguration

#### `config.py` (36 Zeilen)
**Funktion:** Zentrale Konfiguration
- Environment Variables laden
- Limits definieren (FREE: 2 Produkte)
- Pricing (PRO: 10€)
- Admin IDs
- Feature-Listen (Zahlungsmethoden)

**Key Classes:**
- `Config` - Statische Konfiguration

---

### 🧱 Core Module

#### `core/supabase_client.py` (11 Zeilen)
**Funktion:** Datenbank-Verbindung
- Supabase Client initialisieren
- Singleton Pattern

**Exports:**
- `db` - Globaler Supabase Client

#### `core/strings.py` (202 Zeilen)
**Funktion:** Texte & Buttons
- Alle UI-Texte zentral
- Buttons (Haupt- & Inline)
- Nachrichten-Templates

**Key Classes:**
- `Buttons` - Button-Texte
- `Messages` - Nachricht-Templates

#### `core/utils.py` (75 Zeilen)
**Funktion:** Hilfsfunktionen
- Zahlungsadressen-Validierung
- Crypto-Kurs-Abfrage (LTC)
- Bild-Upload Helper
- Text-Formatierung

**Key Functions:**
- `validate_crypto_address()` - Wallet validieren
- `format_payment_methods()` - Zahlungen formatieren

#### `core/validator.py` (67 Zeilen)
**Funktion:** Feature-Validierung
- Prüft FREE vs PRO Limits
- Zahlungsmethoden-Check
- Preis-Validierung

**Key Functions:**
- `can_add_product()` - Produkt-Limit prüfen
- `can_use_categories()` - PRO-Feature prüfen
- `can_upload_images()` - PRO-Feature prüfen

#### `core/middlewares.py` (38 Zeilen)
**Funktion:** Request-Middleware
- Lädt Shop-Kontext
- Prüft ob User = Shop-Besitzer
- Für Multi-Tenant Support

**Key Classes:**
- `ShopMiddleware` - Shop-Kontext laden

---

### 🎮 Handler (Controller)

#### `handlers/master_admin_handlers.py` (196 Zeilen)
**Funktion:** System-Admin Befehle
- Dashboard mit Statistiken
- PRO aktivieren/deaktivieren
- User-Verwaltung

**Key Commands:**
- `/master` - Dashboard
- `/grantpro <ID>` - PRO aktivieren
- `/revokepro <ID>` - PRO deaktivieren
- `/userinfo <ID>` - User-Details
- `/listpro` - PRO-User Liste
- `/listfree` - FREE-User Liste

#### `handlers/admin_handlers.py` (389 Zeilen)
**Funktion:** Shop-Verwaltung
- Produkte anlegen (mit Kategorien & Bildern)
- Lagerbestand verwalten
- Kategorien erstellen (PRO)
- Bestellungen bestätigen

**Key Features:**
- FSM für Produkt-Erstellung
- Kategorien-Auswahl (PRO)
- Bild-Upload (PRO)
- Lager-Nachfüllung

#### `handlers/customer_handlers.py` (185 Zeilen)
**Funktion:** Kundenansicht
- Shop-Katalog anzeigen
- Kategorien-Navigation (PRO)
- Produktbilder anzeigen (PRO)
- Kaufprozess starten

**Key Functions:**
- `show_shop_catalog()` - Katalog anzeigen
- `start_purchase()` - Kauf initiieren

#### `handlers/shop_settings.py` (126 Zeilen)
**Funktion:** Shop-Einstellungen
- Zahlungsmethoden verwalten
- Wallet-Adressen hinterlegen
- Bot-Token konfigurieren (PRO)
- Validierung

**Key Features:**
- Zahlungsmethoden-Filter (FREE/PRO)
- Adress-Validierung
- FSM für Settings

#### `handlers/payment_handlers.py` (107 Zeilen)
**Funktion:** Upgrade & Zahlungen
- PRO-Upgrade Optionen
- Zahlungsinfo (LTC)
- Admin-Bestätigung
- User-Benachrichtigung

**Key Functions:**
- `show_upgrade_options()` - Upgrade anbieten
- `pay_ltc_info()` - LTC-Zahlung
- `process_admin_confirm_pro()` - PRO aktivieren

---

### 💾 Services (Model)

#### `services/db_service.py` (328 Zeilen)
**Funktion:** Datenbank-Operationen
- User-Verwaltung (CRUD)
- Produkt-Verwaltung (mit Kategorien & Bildern)
- Kategorien-Verwaltung (PRO)
- Bestell-Verwaltung
- Statistiken

**Key Functions:**
- `get_user_by_id()` - User laden
- `add_product()` - Produkt erstellen
- `create_category()` - Kategorie erstellen (PRO)
- `confirm_order()` - Bestellung abschließen
- `get_all_users_stats()` - System-Statistiken

#### `services/subscription.py` (79 Zeilen)
**Funktion:** PRO-Verwaltung
- Subscription aktivieren
- Ablauf prüfen
- Verlängern
- Kündigen

**Key Functions:**
- `activate_pro_subscription()` - PRO aktivieren
- `check_subscription_status()` - Status prüfen
- `cancel_subscription()` - PRO deaktivieren

---

### 🤖 Bot Router

#### `bots/master_bot.py` (92 Zeilen)
**Funktion:** Master-Bot Commands
- `/start` Handler
- Deep-Link Routing (Shop-Code)
- User Registrierung
- Dashboard

#### `bots/shop_logic.py` (28 Zeilen)
**Funktion:** Shop-Bots (PRO)
- `/start` für eigene Bots
- Besitzer vs Kunde unterscheiden
- Shop-Katalog anzeigen

---

### ⏱️ Background Tasks

#### `tasks/expiry_check.py` (43 Zeilen)
**Funktion:** Subscription-Prüfung
- Läuft alle 24 Stunden
- Prüft abgelaufene PRO-Accounts
- Deaktiviert automatisch

---

### 🗄️ Datenbank

#### `database_schema.sql` (177 Zeilen)
**Funktion:** Supabase Schema
- Tabellen: profiles, products, orders, categories
- Indizes für Performance
- RLS Policies
- Triggers für updated_at

**Tabellen:**
- `profiles` - User & Shop-Betreiber
- `products` - Produkte (mit category, image_url)
- `orders` - Bestellungen
- `categories` - Kategorien (PRO)

---

## 📊 Code-Metriken

**Gesamt:** ~2.500 Zeilen Code

| Modul | Zeilen | Dateien |
|-------|--------|---------|
| Handlers | ~1.000 | 5 |
| Services | ~400 | 2 |
| Core | ~400 | 5 |
| Bots | ~120 | 2 |
| Main | ~90 | 1 |
| Tasks | ~43 | 1 |
| Config | ~36 | 1 |

**Dokumentation:** ~1.500 Zeilen

---

## 🔄 Request Flow

### User startet Bot (`/start`)

```
1. Master-Bot empfängt Message
   ↓
2. Middleware: Shop-Kontext laden
   ↓
3. master_bot.py: cmd_start()
   ├─ Deep-Link? → Shop anzeigen
   └─ Normaler Start → Dashboard
   ↓
4. db_service: User laden/erstellen
   ↓
5. Template rendern (strings.py)
   ↓
6. Response an User
```

### Produkt anlegen (PRO mit Bild & Kategorie)

```
1. User: "➕ Produkt hinzufügen"
   ↓
2. admin_handlers: start_add_product()
   ↓
3. validator: can_add_product() → ✅
   ↓
4. FSM: ProductForm.name
   ├─ Name → description
   ├─ Description → price
   ├─ Price → category (PRO)
   ├─ Category → image (PRO)
   ├─ Image → content
   └─ Content → add_product()
   ↓
5. db_service: add_product(category, image_url)
   ↓
6. Supabase: INSERT INTO products
   ↓
7. Response: "✅ Produkt erstellt!"
```

### Kaufprozess

```
1. Kunde: Shop-Link öffnen
   ↓
2. master_bot: Deep-Link → show_shop_catalog()
   ↓
3. customer_handlers: Produkte laden
   ↓
4. Kunde: "🛒 Jetzt kaufen"
   ↓
5. customer_handlers: start_purchase()
   ├─ Stock prüfen
   ├─ Order erstellen
   ├─ Zahlungsinfo anzeigen
   └─ Verkäufer benachrichtigen
   ↓
6. Verkäufer: "✅ Zahlung erhalten"
   ↓
7. admin_handlers: process_confirm_sale()
   ├─ Item aus Lager nehmen
   ├─ Order auf completed setzen
   └─ Ware an Käufer senden
   ↓
8. ✅ Verkauf abgeschlossen
```

---

## 🎯 Wichtigste Module zum Verstehen

**Für Entwickler:**
1. `main.py` - Start hier
2. `handlers/admin_handlers.py` - Haupt-Logik
3. `services/db_service.py` - Datenbank-Layer
4. `core/validator.py` - Feature-Limits

**Für Anpassungen:**
1. `core/strings.py` - Texte ändern
2. `config.py` - Limits/Preise ändern
3. `database_schema.sql` - Schema erweitern

---

**Viel Erfolg beim Entwickeln! 🚀**
