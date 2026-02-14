# Changelog

Alle wichtigen Änderungen am Own1Shop Bot werden hier dokumentiert.

---

## [2.1.0] - 2026-02-14

### 🎉 Automatisches Bot-Setup & Migration!

Das größte Update seit Release mit vollautomatischem Shop-Bot Management.

### ✨ Neue Features

#### Automatisches Bot-Setup
- **Token eingeben → Bot läuft sofort**: Nach Token-Eingabe wird Bot automatisch eingerichtet
- **Commands automatisch setzen**: `/start`, `/admin`, `/help` werden konfiguriert
- **Beschreibung automatisch**: Bot-Info wird gesetzt
- **Keine Wartezeit**: Bot startet in ~5 Sekunden statt nach Neustart

#### Produktübertragung (Migration)
- **Produkte migrieren**: Alle Produkte vom Master-Bot zum eigenen Bot übertragen
- **Kategorien migrieren**: Kategorien bleiben erhalten
- **Lagerbestände**: Bleiben komplett erhalten
- **Ein-Klick-Migration**: Einfacher UI-Prozess
- **Zusammenfassung**: User sieht was passiert vor der Migration

#### Dynamisches Bot-Management
- **Bot-Stopp bei Ablauf**: PRO läuft ab → Bot stoppt automatisch
- **Automatische Reaktivierung**: PRO verlängert → Bot startet wieder
- **Echtzeit-Management**: Bots können im Betrieb gestartet/gestoppt werden
- **Status-Tracking**: Anzahl aktiver Bots, User-IDs, etc.

### 🔧 Neue Komponenten

- `services/bot_setup.py` - Automatische Bot-Konfiguration
- `services/migration.py` - Produktübertragung
- `services/bot_manager.py` - Dynamisches Bot-Management
- `handlers/migration_handlers.py` - Migration UI

### 📊 Verbesserungen

- **120x schneller**: Bot-Start von ~30 Min auf ~5 Sek
- **Bessere UX**: Sofortiges Feedback, keine Wartezeiten
- **Fairness**: PRO-Features nur für zahlende User
- **Automatisierung**: Weniger manuelle Eingriffe nötig

### 🗄️ Datenbank

- **Neue Felder in `profiles`**:
  - `migration_completed` (BOOLEAN)
  - `migration_date` (TIMESTAMPTZ)

### 🐛 Bug Fixes

- PRO-Ablauf stoppt jetzt tatsächlich den Bot
- Bot-Start nach Token-Eingabe funktioniert ohne Neustart
- Migration verhindert Daten-Duplikate

### 📚 Dokumentation

- `BOT_SETUP_FEATURE.md` - Vollständige Feature-Doku
- `UPDATE_v2.1.md` - Upgrade-Guide
- Alle README-Dateien aktualisiert

---

## [2.0.0] - 2026-02-14

### 🎉 Komplett überarbeitet!

Vollständige Neuimplementierung mit verbesserter Architektur und neuen Features.

### ✨ Neue Features

#### PRO Features
- **Kategorien-System**: Produkte in Kategorien organisieren
- **Bild-Upload**: 1 Bild pro Produkt (Telegram file_id)
- **Mehr Zahlungsmethoden**: ETH, SOL, PayPal (zusätzlich zu BTC/LTC)
- **Eigener Bot-Token**: Vollständiges Branding mit eigenem Bot

#### Admin Features
- **Verbesserte Master-Admin Übersicht**: 
  - `/listpro` - Alle PRO-User anzeigen
  - `/listfree` - Alle FREE-User anzeigen
  - Erweiterte Statistiken
- **Detaillierte User-Info**: `/userinfo <ID>` zeigt alle Details

#### System Features
- **Zahlungsmethoden-Filter**: FREE-User nur BTC/LTC
- **Subscription-Expiry-Check**: Automatische Deaktivierung abgelaufener PRO-Accounts
- **Validierung**: Crypto-Adressen werden validiert
- **Bessere Error-Handling**: Umfassende Try-Catch Blöcke

### 🔧 Verbesserungen

#### Code-Struktur
- Modulare Architektur mit klarer Trennung
- Verbesserte Service-Layer
- Konsistente Naming Conventions
- Type Hints wo sinnvoll

#### Database
- Erweiterte Schema mit `categories` Tabelle
- `image_url` Feld für Produkte
- Bessere Indizes für Performance
- RLS (Row Level Security) vorbereitet

#### User Experience
- Inline Kategorien-Navigation für Kunden
- Produktbilder in Kundenansicht
- Bessere Fehlermeldungen
- Übersichtlichere Buttons

### 🐛 Bug Fixes

- Shop-ID wird jetzt garantiert generiert
- Lagerbestand-Zählung korrigiert
- Deep-Link Routing verbessert
- Middleware-Kontext korrekt weitergegeben
- FSM States richtig gehandhabt

### 📚 Dokumentation

- Umfassende README.md
- Detailliertes DEPLOY.md für render.com
- TESTING.md für lokale Tests
- SQL Schema mit Kommentaren
- .env.example Template

### 🔒 Sicherheit

- Zahlungsadressen-Validierung
- Admin-Berechtigungen überprüft
- Environment Variables statt Hardcoding
- Input-Sanitization verbessert

---

## [1.0.0] - 2026-01-XX

### Initial Release

- ✅ Basis Shop-System
- ✅ FREE & PRO Unterscheidung
- ✅ Produkt-Verwaltung
- ✅ Bestell-System
- ✅ Zahlungsmethoden (BTC/LTC)
- ✅ Master-Admin Befehle
- ✅ Multi-Tenant Support

---

## Geplante Features (Roadmap)

### Version 2.1.0
- [ ] Statistiken-Dashboard für Shop-Betreiber
- [ ] Export-Funktion (Bestellungen als CSV)
- [ ] Automatische Zahlungserkennung (via API)
- [ ] Mehrsprachigkeit (EN, DE)

### Version 2.2.0
- [ ] Rabatt-Codes System
- [ ] Bundle-Angebote
- [ ] Kundenbewertungen
- [ ] Newsletter-Funktion

### Version 3.0.0
- [ ] Web-Dashboard (zusätzlich zu Telegram)
- [ ] Analytics & Insights
- [ ] API für Drittanbieter
- [ ] Webhook-Integrationen

---

**Hinweise zur Versionierung:**

Wir folgen [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking Changes
- MINOR: Neue Features (abwärtskompatibel)
- PATCH: Bug Fixes
