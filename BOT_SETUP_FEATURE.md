# 🤖 Automatisches Bot-Setup & Migration

Neue Features in v2.1 für vollautomatisches Shop-Bot Management!

---

## 🎯 Übersicht

PRO-User können jetzt:
1. ✅ **Bot-Token eingeben** → Bot wird automatisch eingerichtet
2. ✅ **Produkte übertragen** → Migration vom Master-Bot zum eigenen Bot
3. ✅ **Bei PRO-Ablauf** → Bot wird automatisch gestoppt
4. ✅ **Bei Reaktivierung** → Bot wird automatisch reaktiviert

---

## 🚀 Workflow

### Schritt 1: Bot-Token eingeben

**User (PRO):**
```
→ "⚙️ Shop-Einstellungen"
→ "🤖 Eigener Bot-Token"
→ Token eingeben (von @BotFather)
```

**System macht automatisch:**
1. ✅ Token validieren
2. ✅ Bot-Info holen
3. ✅ Commands setzen (`/start`, `/admin`, `/help`)
4. ✅ Bot-Beschreibung setzen
5. ✅ Bot starten (Polling)
6. ✅ User benachrichtigen

**User erhält:**
```
🎉 Bot erfolgreich eingerichtet!

🤖 Dein Bot: @MeinShop_Bot
🆔 Shop-ID: ABC123
📡 Status: ✅ Läuft jetzt

Shop-Link:
https://t.me/MeinShop_Bot

💡 Nächster Schritt:
Möchtest du deine bestehenden Produkte übertragen?
```

### Schritt 2: Produkte übertragen (Optional)

**User kann wählen:**
- ✅ Produkte auf eigenen Bot übertragen
- ❌ Später machen
- ℹ️ Neue Produkte direkt im eigenen Bot anlegen

**Migration-Prozess:**
```
1. Zusammenfassung anzeigen
   ├─ Anzahl Produkte
   ├─ Kategorien
   └─ Was passiert

2. User bestätigt

3. System migriert:
   ├─ Alle Produkte
   ├─ Kategorien
   ├─ Lagerbestände
   └─ Zuordnung zum eigenen Bot

4. ✅ Fertig!
```

**Wichtig nach Migration:**
- Produkte sind NUR über eigenen Bot verfügbar
- Master-Bot zeigt Produkte nicht mehr
- Zahlungsdaten bleiben gleich
- Shop-Link ändert sich zu eigenem Bot

### Schritt 3: PRO läuft ab

**System macht automatisch:**
1. ⏰ Täglicher Check auf Ablauf
2. 🛑 Bei Ablauf: Bot stoppen
3. 📧 User benachrichtigen (TODO)
4. 💾 Alle Daten bleiben erhalten

**User kann:**
- ❌ Bot nicht mehr nutzen
- ✅ Produkte bleiben gespeichert
- ✅ Bei Reaktivierung: alles wie vorher

### Schritt 4: PRO reaktivieren

**Admin aktiviert PRO:**
```
/grantpro 123456789 1
```

**System macht automatisch:**
1. ✅ PRO-Status aktivieren
2. 🤖 Bot neu starten (falls Token vorhanden)
3. 📧 User benachrichtigen

**User kann:**
- ✅ Sofort weitermachen
- ✅ Alle Produkte verfügbar
- ✅ Bot läuft wieder

---

## 💡 Technische Details

### Bot-Setup Service

**Datei:** `services/bot_setup.py`

**Funktionen:**
```python
async def setup_shop_bot(bot_token, owner_id, shop_id):
    """
    Richtet Bot automatisch ein:
    - Bot-Info holen
    - Commands setzen
    - Beschreibung setzen
    - Validierung
    """

async def validate_bot_token(bot_token):
    """Token validieren"""

async def send_setup_notification(bot, owner_id, bot_username, shop_id):
    """Erfolgs-Benachrichtigung"""
```

### Migration Service

**Datei:** `services/migration.py`

**Funktionen:**
```python
async def migrate_products_to_custom_bot(user_id):
    """
    Migriert Produkte zum eigenen Bot
    Returns: {success, migrated_count, categories_migrated}
    """

async def check_migration_status(user_id):
    """Migration-Status prüfen"""

async def get_migration_summary(user_id):
    """Zusammenfassung für User"""
```

### Bot Manager

**Datei:** `services/bot_manager.py`

**Class:** `BotManager`
```python
async def start_shop_bot(user_id, bot_token, dispatcher):
    """Bot starten"""

async def stop_shop_bot(user_id):
    """Bot stoppen"""

async def restart_shop_bot(user_id, bot_token, dispatcher):
    """Bot neu starten"""

def is_bot_running(user_id):
    """Prüfen ob Bot läuft"""

def get_active_bot_count():
    """Anzahl aktiver Bots"""
```

### Datenbank

**Neue Felder in `profiles`:**
```sql
migration_completed BOOLEAN DEFAULT FALSE,
migration_date TIMESTAMPTZ
```

---

## 🔧 Konfiguration

### Commands die gesetzt werden

```python
commands = [
    BotCommand(command="start", description="🏪 Shop öffnen"),
    BotCommand(command="admin", description="🛠 Shop verwalten (Besitzer)"),
    BotCommand(command="help", description="❓ Hilfe"),
]
```

### Bot-Beschreibung

```
🏪 Digitaler Shop von Shop-ID: {shop_id}

Powered by Own1Shop
```

---

## ⚙️ Admin-Funktionen

### Bot-Status prüfen

```python
# In Master-Admin Handlers
from services.bot_manager import bot_manager

# Bot läuft?
is_running = bot_manager.is_bot_running(user_id)

# Anzahl aktiver Bots
count = bot_manager.get_active_bot_count()

# Liste aller aktiven User
user_ids = bot_manager.get_active_user_ids()
```

### Bot manuell stoppen/starten

```python
# Bot stoppen
await bot_manager.stop_shop_bot(user_id)

# Bot starten
await bot_manager.start_shop_bot(user_id, token, dispatcher)

# Bot neu starten
await bot_manager.restart_shop_bot(user_id, token, dispatcher)
```

---

## 🐛 Error Handling

### Token ungültig

```
❌ Token ungültig

Fehler: [API Error]

Bitte prüfe den Token und versuche es erneut.
```

### Bot-Setup fehlgeschlagen

```
⚠️ Token gespeichert, aber Setup fehlgeschlagen

Fehler: [Fehler]

Der Bot wird beim nächsten System-Neustart aktiviert.
```

### Migration fehlgeschlagen

```
❌ Migration fehlgeschlagen

Fehler: [Fehler]

Bitte kontaktiere den Support.
```

---

## 📊 Logs

**Bot gestartet:**
```
INFO - ✅ Shop-Bot gestartet: @MeinShop_Bot (User: 123456789)
```

**Bot gestoppt:**
```
INFO - 🛑 Shop-Bot gestoppt: @MeinShop_Bot (User: 123456789)
INFO - 🛑 Shop-Bot für User 123456789 gestoppt (PRO abgelaufen)
```

**Migration:**
```
INFO - ✅ Migration abgeschlossen für User 123456789: 15 Produkte, 3 Kategorien
```

**Expiry-Check:**
```
INFO - ⏰ User 123456789 PRO-Status abgelaufen
INFO - ✅ 5 abgelaufene PRO-Subscriptions deaktiviert und Bots gestoppt
```

---

## 🎯 Best Practices

### Für User

1. **Bot-Token sicher aufbewahren**
   - Token niemals teilen
   - Bei @BotFather generiert

2. **Migration durchführen**
   - Nach Bot-Setup sofort migrieren
   - Oder neue Produkte direkt im eigenen Bot anlegen

3. **PRO rechtzeitig verlängern**
   - Sonst wird Bot gestoppt
   - Daten bleiben erhalten

### Für Admins

1. **Bot-Status überwachen**
   - Regelmäßig Logs prüfen
   - Anzahl aktiver Bots checken

2. **Bei Ablauf**
   - User proaktiv kontaktieren
   - Verlängerung anbieten

3. **Backup**
   - Supabase Backups aktiv
   - Bei Migration: alte Daten 7 Tage behalten

---

## 🔮 Zukünftige Erweiterungen

### v2.2
- [ ] E-Mail Benachrichtigung bei Ablauf
- [ ] Auto-Verlängerung (Stripe)
- [ ] Bot-Statistiken im Dashboard

### v2.3
- [ ] Mehrere Bots pro User
- [ ] Bot-Template-Auswahl
- [ ] Custom Commands

---

**Happy Bot Management! 🤖**
