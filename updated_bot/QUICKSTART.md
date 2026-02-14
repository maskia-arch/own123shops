# ⚡ Quick Start Guide

Schnelleinstieg in 10 Minuten!

---

## 🎯 Ziel

Bot auf render.com deployen und erste Produkte verkaufen.

---

## 📋 Was du brauchst

- [ ] Telegram Account
- [ ] 10 Minuten Zeit
- [ ] E-Mail Adresse (für Supabase & render.com)

---

## 🚀 In 5 Schritten zum eigenen Shop

### 1️⃣ Supabase einrichten (3 Min)

1. Gehe zu [supabase.com](https://supabase.com) → "Start your project"
2. Erstelle ein Projekt (Name: `own1shop`)
3. **SQL Editor** → `database_schema.sql` einfügen → Run
4. **Settings → API** → Kopiere:
   - Project URL
   - anon public Key

### 2️⃣ Telegram Bot erstellen (2 Min)

1. [@BotFather](https://t.me/BotFather) öffnen → `/newbot`
2. Bot-Namen eingeben (z.B. `MeinShop_Bot`)
3. **Token kopieren**
4. [@userinfobot](https://t.me/userinfobot) → Deine **User ID** kopieren

### 3️⃣ Code auf GitHub (2 Min)

1. [github.com](https://github.com) → "New repository"
2. Name: `own1shop-bot` (Private)
3. Alle Dateien aus `updated_bot/` hochladen

### 4️⃣ render.com Deploy (2 Min)

1. [render.com](https://render.com) → "New Web Service"
2. GitHub-Repository verbinden
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `python main.py`
5. **Environment Variables** hinzufügen:
   ```
   MASTER_BOT_TOKEN = dein_bot_token
   SUPABASE_URL = deine_url
   SUPABASE_KEY = dein_key
   ADMIN_IDS = deine_user_id
   PORT = 10000
   ```
6. "Create Web Service"

### 5️⃣ Testen! (1 Min)

1. Deinen Bot in Telegram suchen
2. `/start` senden
3. ✅ Willkommen-Nachricht!

---

## 🎊 Fertig!

Dein Bot läuft jetzt 24/7!

**Nächste Schritte:**

### Erstes Produkt anlegen

```
→ "🛒 Shop verwalten"
→ "➕ Produkt hinzufügen"
→ Name: "Premium Account"
→ Beschreibung: "1 Monat Zugang"
→ Preis: 9.99
→ Lager: account1:pass1
→ ✅ Erstellt!
```

### Zahlungsmethode hinterlegen

```
→ "⚙️ Shop-Einstellungen"
→ "Bitcoin (BTC) ändern"
→ Deine BTC-Adresse eingeben
→ ✅ Gespeichert!
```

### Shop-Link teilen

```
Dein Shop-Link steht im Hauptmenü:
https://t.me/dein_bot?start=DEINE_SHOP_ID

Teile ihn mit deinen Kunden!
```

---

## 💡 Pro Tipps

**Tipp 1: Test-Kauf durchführen**
- Öffne Shop-Link in neuem Chat
- Teste Kaufprozess selbst

**Tipp 2: Uptimerobot einrichten**
- Verhindert Sleep auf Free Plan
- 5 Minuten Setup

**Tipp 3: PRO upgraden**
- Für unbegrenzte Produkte
- Kategorien & Bilder
- Mehr Zahlungsmethoden

---

## ❓ Probleme?

**Bot antwortet nicht?**
→ render.com Logs checken

**Datenbank-Fehler?**
→ SQL Schema korrekt ausgeführt?

**Mehr Hilfe?**
→ Siehe README.md oder DEPLOY.md

---

**Viel Erfolg! 🎉**
