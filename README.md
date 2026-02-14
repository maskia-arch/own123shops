# Own1Shop - Telegram Multi-Shop Bot System

🚀 **Version 2.0.0** - Vollständig überarbeitetes System

Ein professionelles Telegram-Bot-System für digitale Shops mit FREE- und PRO-Features.

---

## 📋 Features

### 🆓 FREE Version
- ✅ Max. **2 Produkte** anlegen
- ✅ Digitale Güter verkaufen (mit Lagerbestand)
- ✅ Zahlungsmethoden: **BTC & LTC**
- ✅ Eigene Shop-ID & Link
- ✅ Bestellverwaltung
- ✅ Automatische Warenauslieferung

### 💎 PRO Version (10€/Monat)
- ✅ **Unbegrenzt Produkte**
- ✅ **Kategorien** für bessere Organisation
- ✅ **Bilder** für Produkte (1 pro Produkt)
- ✅ Mehr Zahlungsmethoden: **ETH, SOL, PayPal**
- ✅ **Eigener Bot-Token** (Branding)
- ✅ Prioritäts-Support

### 👑 Master-Admin Features
- ✅ User-Übersicht (FREE & PRO)
- ✅ PRO-Status verwalten
- ✅ System-Statistiken
- ✅ User-Details einsehen

---

## 🛠 Setup-Anleitung

### 1. Supabase Datenbank einrichten

1. Account erstellen auf [supabase.com](https://supabase.com)
2. Neues Projekt erstellen
3. Im **SQL Editor** die Datei `database_schema.sql` ausführen
4. **URL** und **API Key** kopieren (Settings → API)

### 2. Telegram Bot erstellen

1. Mit [@BotFather](https://t.me/BotFather) einen Bot erstellen (`/newbot`)
2. **Bot Token** kopieren
3. Deine **Telegram User ID** holen (z.B. via [@userinfobot](https://t.me/userinfobot))

### 3. Umgebungsvariablen konfigurieren

Erstelle eine `.env` Datei (siehe `.env.example`):

```env
MASTER_BOT_TOKEN=dein_bot_token_hier
SUPABASE_URL=https://dein-projekt.supabase.co
SUPABASE_KEY=dein_supabase_key_hier
ADMIN_IDS=deine_telegram_id_hier
PORT=10000
```

### 4. Installation

```bash
# Dependencies installieren
pip install -r requirements.txt

# Bot starten
python main.py
```

---

## 🚀 Deployment auf render.com

### Schritt-für-Schritt

1. **GitHub Repository** erstellen und Code pushen

2. Auf [render.com](https://render.com) anmelden

3. **New → Web Service** erstellen

4. Repository verbinden

5. **Konfiguration:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   
6. **Environment Variables** setzen:
   ```
   MASTER_BOT_TOKEN = dein_token
   SUPABASE_URL = deine_url
   SUPABASE_KEY = dein_key
   ADMIN_IDS = deine_id
   PORT = 10000
   ```

7. **Deploy** starten

---

## 📖 Nutzung

### Als Master-Admin

Befehle:
- `/master` - Dashboard mit Statistiken
- `/grantpro <ID> [Monate]` - PRO aktivieren
- `/revokepro <ID>` - PRO deaktivieren
- `/userinfo <ID>` - User-Details
- `/listpro` - Alle PRO-User
- `/listfree` - Alle FREE-User

### Als Shop-Betreiber (FREE)

1. Bot starten mit `/start`
2. "🛒 Shop verwalten" → Produkte anlegen
3. "⚙️ Shop-Einstellungen" → BTC/LTC Adressen hinterlegen
4. Shop-Link mit Kunden teilen

**Shop-Link Format:**
```
https://t.me/dein_bot?start=SHOP_ID
```

### Als Shop-Betreiber (PRO)

Zusätzlich:
- "📁 Kategorien verwalten" → Kategorien erstellen
- Beim Produkt anlegen: Kategorie & Bild hochladen
- "🤖 Eigener Bot-Token" → Eigenen Bot konfigurieren

### Als Kunde

1. Shop-Link öffnen
2. Produkte durchstöbern
3. "🛒 Jetzt kaufen" klicken
4. An angegebene Wallet-Adresse zahlen
5. Verkäufer bestätigt Zahlung
6. Ware wird automatisch gesendet

---

## 🔧 Technische Details

### Architektur

```
main.py                    # Entry Point + Bot Orchestration
├── config.py              # Konfiguration & Limits
├── core/                  # Core Funktionalität
│   ├── supabase_client.py # Datenbankverbindung
│   ├── strings.py         # Texte & Buttons
│   ├── utils.py           # Hilfsfunktionen
│   ├── validator.py       # Feature-Validierung
│   └── middlewares.py     # Shop-Kontext Middleware
├── handlers/              # Request Handler
│   ├── master_admin_handlers.py
│   ├── admin_handlers.py
│   ├── customer_handlers.py
│   ├── shop_settings.py
│   └── payment_handlers.py
├── services/              # Business Logic
│   ├── db_service.py      # Datenbank-Operationen
│   └── subscription.py    # PRO-Verwaltung
├── bots/                  # Bot Router
│   ├── master_bot.py      # Master-Bot
│   └── shop_logic.py      # Shop-Bots (PRO)
└── tasks/                 # Background Tasks
    └── expiry_check.py    # Subscription-Prüfung
```

### Datenbank-Schema

**profiles** - User/Shop-Betreiber
- `id` (BIGINT) - Telegram User ID
- `username` (TEXT)
- `is_pro` (BOOLEAN)
- `shop_id` (TEXT)
- `wallet_btc, wallet_ltc, wallet_eth, wallet_sol, paypal_email`
- `custom_bot_token` (TEXT) - Für PRO
- `expiry_date` (TIMESTAMPTZ)

**products** - Produkte
- `id` (BIGSERIAL)
- `owner_id` (BIGINT)
- `name, description, price`
- `content` (TEXT) - Lagerbestand
- `category` (TEXT) - PRO
- `image_url` (TEXT) - PRO

**orders** - Bestellungen
- `id` (UUID)
- `buyer_id, product_id, seller_id`
- `status` (pending/completed)

**categories** - Kategorien (PRO)
- `id` (SERIAL)
- `owner_id, name, description`

---

## 🎯 Workflow

### Produktanlage (PRO mit Kategorien & Bild)

```
1. /admin
2. "➕ Produkt hinzufügen"
3. Name eingeben
4. Beschreibung eingeben
5. Preis eingeben
6. Kategorie wählen (oder überspringen)
7. Bild hochladen (oder überspringen)
8. Lagerbestand hinzufügen (oder überspringen)
✅ Produkt erstellt!
```

### Kaufprozess

```
1. Kunde: Shop-Link öffnen
2. Kunde: Produkt auswählen → "🛒 Jetzt kaufen"
3. System: Bestellung erstellen
4. Kunde: Zahlung an BTC/LTC/etc. senden
5. Verkäufer: "✅ Zahlung erhalten" klicken
6. System: Item aus Lager nehmen & an Käufer senden
✅ Verkauf abgeschlossen!
```

---

## 🔐 Sicherheit

- ✅ Alle sensiblen Daten in Umgebungsvariablen
- ✅ Supabase RLS (Row Level Security) aktiviert
- ✅ Zahlungsadressen-Validierung
- ✅ Admin-Berechtigungen per User ID
- ✅ Feature-Limits pro User-Typ (FREE/PRO)

---

## 📊 Limits & Preise

| Feature | FREE | PRO |
|---------|------|-----|
| Produkte | Max. 2 | Unbegrenzt |
| Kategorien | ❌ | ✅ |
| Produktbilder | ❌ | ✅ |
| Zahlungen | BTC, LTC | BTC, LTC, ETH, SOL, PayPal |
| Eigener Bot | ❌ | ✅ |
| **Preis** | Kostenlos | **10€/Monat** |

---

## 🐛 Troubleshooting

### Bot startet nicht
- ✅ Prüfe `.env` Konfiguration
- ✅ Prüfe Bot Token (@BotFather)
- ✅ Prüfe Supabase URL & Key
- ✅ Logs checken: `python main.py`

### Datenbank-Fehler
- ✅ SQL Schema korrekt ausgeführt?
- ✅ Supabase Projekt aktiv?
- ✅ API Key korrekt?

### Shop-Bots starten nicht (PRO)
- ✅ Bot-Token korrekt hinterlegt?
- ✅ Token von @BotFather?
- ✅ Logs prüfen

---

## 📞 Support

Bei Fragen oder Problemen:
1. Issues auf GitHub erstellen
2. Admin kontaktieren (in Bot)

---

## 📝 Lizenz

Dieses Projekt ist für den persönlichen und kommerziellen Gebrauch freigegeben.

---

## ✨ Changelog

### Version 2.0.0 (Aktuell)
- ✅ Komplett überarbeitet & optimiert
- ✅ Kategorien-System (PRO)
- ✅ Bild-Upload (PRO)
- ✅ Verbesserte Admin-Übersicht
- ✅ Zahlungsmethoden-Filter (FREE: nur BTC/LTC)
- ✅ Bessere Code-Struktur
- ✅ Umfassende Validierung
- ✅ Subscription-Expiry-Check

### Version 1.0.0
- ✅ Basis-Funktionalität
- ✅ FREE & PRO Unterscheidung
- ✅ Produkte & Bestellungen
- ✅ Master-Admin System

---

**Viel Erfolg mit deinem Shop! 🚀**
