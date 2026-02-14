# 🚀 Deployment auf render.com

Detaillierte Schritt-für-Schritt Anleitung für das Deployment des Own1Shop Bots auf render.com.

---

## 📋 Voraussetzungen

Bevor du startest, benötigst du:

1. ✅ **Supabase Account** mit konfigurierter Datenbank
2. ✅ **Telegram Bot Token** (von @BotFather)
3. ✅ **Deine Telegram User ID** (z.B. via @userinfobot)
4. ✅ **GitHub Account** (für Code-Repository)
5. ✅ **render.com Account** (kostenlos anmelden)

---

## 1️⃣ Supabase Datenbank einrichten

### 1.1 Projekt erstellen

1. Gehe zu [supabase.com](https://supabase.com)
2. Klicke auf "Start your project"
3. Erstelle ein neues Projekt:
   - **Name:** `own1shop` (oder beliebig)
   - **Database Password:** Sicheres Passwort wählen
   - **Region:** Nächstgelegene auswählen
4. Warte ca. 2 Minuten bis das Projekt bereit ist

### 1.2 Datenbank-Schema anlegen

1. In deinem Supabase-Projekt → **SQL Editor** (linkes Menü)
2. Klicke auf "New query"
3. Kopiere den kompletten Inhalt von `database_schema.sql`
4. Füge ihn in den Editor ein
5. Klicke auf "Run" (oder Strg+Enter)
6. ✅ Du solltest sehen: "Success. No rows returned"

### 1.3 API-Credentials holen

1. Gehe zu **Settings** → **API**
2. Kopiere:
   - **Project URL** (z.B. `https://abcdefgh.supabase.co`)
   - **Project API keys** → `anon` `public` (der lange Schlüssel)

⚠️ **Wichtig:** Speichere diese Werte sicher, du brauchst sie später!

---

## 2️⃣ Telegram Bot erstellen

### 2.1 Bot bei BotFather erstellen

1. Öffne [@BotFather](https://t.me/BotFather) in Telegram
2. Sende `/newbot`
3. Folge den Anweisungen:
   - **Name:** `Own1Shop Master Bot` (oder beliebig)
   - **Username:** `Own1Shop_Bot` (muss auf `_bot` enden)
4. ✅ Du erhältst den **Bot Token** - speichere ihn!

Beispiel-Token:
```
5678901234:AAFsxxx-xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2.2 Deine Telegram User ID holen

1. Öffne [@userinfobot](https://t.me/userinfobot) in Telegram
2. Sende `/start`
3. ✅ Du erhältst deine **User ID** (z.B. `123456789`)

---

## 3️⃣ Code auf GitHub hochladen

### 3.1 Repository erstellen

1. Gehe zu [github.com](https://github.com)
2. Klicke auf "New repository"
3. **Name:** `own1shop-bot`
4. **Visibility:** Private (empfohlen)
5. Klicke "Create repository"

### 3.2 Code hochladen

**Option A: Via GitHub Web-Interface**
1. Klicke auf "uploading an existing file"
2. Ziehe alle Dateien aus `updated_bot/` in das Fenster
3. Commit mit "Initial commit"

**Option B: Via Git CLI**
```bash
cd updated_bot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/DEIN_USERNAME/own1shop-bot.git
git push -u origin main
```

---

## 4️⃣ render.com einrichten

### 4.1 Account erstellen

1. Gehe zu [render.com](https://render.com)
2. Klicke "Get Started for Free"
3. Registriere mit GitHub-Account

### 4.2 Web Service erstellen

1. Nach dem Login → **Dashboard**
2. Klicke "New +" → **Web Service**
3. Verbinde dein GitHub-Repository:
   - Klicke "Connect account" (falls nötig)
   - Wähle `own1shop-bot` Repository
   - Klicke "Connect"

### 4.3 Service konfigurieren

**Basic Settings:**
- **Name:** `own1shop-bot` (oder beliebig)
- **Region:** Nächstgelegene auswählen
- **Branch:** `main`
- **Runtime:** Python 3

**Build Settings:**
- **Build Command:**
  ```bash
  pip install -r requirements.txt
  ```

- **Start Command:**
  ```bash
  python main.py
  ```

**Instance Type:**
- Wähle "Free" (für Anfang ausreichend)

### 4.4 Environment Variables setzen

Scrolle zu "Environment Variables" und füge hinzu:

| Key | Value | Beispiel |
|-----|-------|----------|
| `MASTER_BOT_TOKEN` | Dein Bot Token | `5678901234:AAFsxxx...` |
| `SUPABASE_URL` | Deine Supabase URL | `https://abcdefgh.supabase.co` |
| `SUPABASE_KEY` | Dein Supabase Key | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` |
| `ADMIN_IDS` | Deine Telegram User ID | `123456789` |
| `PORT` | Port für render.com | `10000` |

⚠️ **Wichtig:** Keine Leerzeichen oder Anführungszeichen!

**Mehrere Admins:**
```
ADMIN_IDS = 123456789,987654321,555666777
```

### 4.5 Deploy starten

1. Klicke unten auf "Create Web Service"
2. ⏳ Warte ca. 2-5 Minuten
3. ✅ Status sollte "Live" werden

---

## 5️⃣ Bot testen

### 5.1 Bot in Telegram öffnen

1. Suche deinen Bot in Telegram (z.B. `@Own1Shop_Bot`)
2. Klicke "Start"
3. ✅ Du solltest eine Willkommensnachricht erhalten

### 5.2 Admin-Befehle testen

Sende:
```
/master
```

✅ Du solltest das Admin-Dashboard sehen mit Statistiken.

### 5.3 Test-Shop erstellen

1. Klicke "🛒 Shop verwalten"
2. Klicke "➕ Produkt hinzufügen"
3. Folge den Schritten
4. ✅ Produkt sollte erfolgreich erstellt werden

---

## 6️⃣ Troubleshooting

### Bot antwortet nicht

**Logs checken:**
1. In render.com → Dein Service
2. Klicke auf "Logs" (oben)
3. Suche nach Fehlern

**Häufige Probleme:**

❌ **"MASTER_BOT_TOKEN nicht gefunden"**
- Lösung: Environment Variable korrekt gesetzt?

❌ **"Supabase URL oder Key fehlen"**
- Lösung: SUPABASE_URL und SUPABASE_KEY prüfen

❌ **"Unauthorized" oder "401"**
- Lösung: Bot Token von @BotFather neu generieren
- `/token` bei @BotFather → Token kopieren

### Datenbank-Fehler

❌ **"relation 'profiles' does not exist"**
- Lösung: `database_schema.sql` wurde nicht ausgeführt
- Gehe zu Supabase SQL Editor und führe es aus

❌ **"SSL connection required"**
- Lösung: Supabase Projekt aktiv? Region korrekt?

### render.com Probleme

❌ **"Build failed"**
- Prüfe `requirements.txt` ist vorhanden
- Prüfe Python-Syntax in allen Files

❌ **"Deploy failed"**
- Prüfe Start Command: `python main.py`
- Prüfe Logs auf Fehler

---

## 7️⃣ Nach dem Deployment

### Auto-Sleep verhindern (Free Plan)

Render.com schläft nach 15 Minuten Inaktivität ein. Optionen:

**Option 1: Upgrade auf Paid Plan**
- 7$/Monat für "always-on"

**Option 2: Uptimerobot (Kostenlos)**
1. Gehe zu [uptimerobot.com](https://uptimerobot.com)
2. Erstelle Account
3. Füge Monitor hinzu:
   - **Type:** HTTP(s)
   - **URL:** Deine render.com URL (z.B. `https://own1shop-bot.onrender.com`)
   - **Interval:** 5 Minuten
4. ✅ Dein Bot wird alle 5 Minuten "geweckt"

### Logs überwachen

Regelmäßig Logs prüfen:
```
render.com → Dein Service → Logs
```

Achte auf:
- ✅ "Master-Bot Polling aktiv"
- ✅ "Shop-Bot für User X gestartet"
- ❌ Fehler oder Warnings

### Backups

**Supabase Datenbank:**
1. Supabase → Settings → Database
2. "Database backups" aktivieren
3. Empfohlen: Tägliches Backup

---

## 8️⃣ Updates deployen

### Code aktualisieren

1. Ändere Code lokal
2. Push zu GitHub:
   ```bash
   git add .
   git commit -m "Update: Beschreibung"
   git push
   ```
3. ✅ render.com deployt automatisch!

### Manual Redeploy

Falls nötig:
1. render.com → Dein Service
2. Klicke "Manual Deploy" → "Deploy latest commit"

---

## 🎉 Fertig!

Dein Own1Shop Bot läuft jetzt 24/7 auf render.com!

**Nächste Schritte:**
- ✅ Zahlungsadressen in Settings hinterlegen
- ✅ Test-Produkte anlegen
- ✅ Shop-Link mit Freunden teilen
- ✅ Auf PRO upgraden für alle Features

Bei Problemen:
- 📖 README.md lesen
- 🐛 Logs checken
- 💬 Support kontaktieren

---

**Viel Erfolg! 🚀**
