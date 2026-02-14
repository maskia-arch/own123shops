# 🧪 Testing Guide

Anleitung zum lokalen Testen des Bots vor dem Deployment.

---

## 🔧 Lokale Entwicklung einrichten

### 1. Python Virtual Environment

```bash
# Virtual Environment erstellen
python -m venv venv

# Aktivieren (Linux/Mac)
source venv/bin/activate

# Aktivieren (Windows)
venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Environment Variables

Erstelle `.env` Datei:

```env
MASTER_BOT_TOKEN=dein_test_bot_token
SUPABASE_URL=https://dein-projekt.supabase.co
SUPABASE_KEY=dein_supabase_key
ADMIN_IDS=deine_telegram_id
PORT=10000
```

### 3. Bot starten

```bash
python main.py
```

**Erwartete Ausgabe:**
```
INFO - 🚀 Own1Shop v2.0.0 wird gestartet...
INFO - ✅ Master-Bot Polling aktiv - System läuft!
```

---

## ✅ Test-Szenarien

### Test 1: Master-Admin Dashboard
1. `/master` senden
2. ✅ Dashboard mit Statistiken erscheint

### Test 2: Produkt anlegen (FREE)
1. "🛒 Shop verwalten"
2. "➕ Produkt hinzufügen"
3. ✅ Produkt erstellt

### Test 3: Limit testen (FREE)
1. 2 Produkte anlegen
2. 3. Produkt versuchen
3. ✅ Limit-Warnung erscheint

### Test 4: PRO aktivieren
1. `/grantpro DEINE_ID 1`
2. ✅ PRO aktiviert

### Test 5: Kategorien (PRO)
1. "📁 Kategorien verwalten"
2. Kategorie erstellen
3. ✅ Kategorie funktioniert

### Test 6: Kaufprozess
1. Shop-Link öffnen
2. Produkt kaufen
3. ✅ Zahlungsinfo + Benachrichtigung

---

## 📝 Test Checkliste

Vor jedem Deployment:

- [ ] Bot startet ohne Fehler
- [ ] Master-Admin funktioniert
- [ ] FREE Limit funktioniert
- [ ] PRO Features funktionieren
- [ ] Kaufprozess funktioniert
- [ ] Logs zeigen keine Fehler

---

**Happy Testing! 🧪**
