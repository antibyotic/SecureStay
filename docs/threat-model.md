# Threat Model - Securestay
## Methodik
Dieses Dokument analysiert Sicherheitsbedrohungen für die SecureStay API nach dem STRIDE Modell.

## 1. SQL Injection
**Bedrohung:** Ein Angreifer manipuliert SQL Queries durch bösartige Eingaben um Daten zu leaken oder zu zerstören.

**Beispiel:**
GET/properties?id='OR '1'='1

**Ursache:** Direkte String-Konkatenation von User-Input in SQL Queries.

**Gegenmaßnahme:** Prepared Statements mit psycopg2 — User-Input wird nie als SQL Code ausgeführt.

**Status:** ✓ Implementiert

## 2. Broken Authentication - Token Theft

**Bedrohung** Ein Angreifer stiehlt einen gültigen JWT Token und schicjt Anfragen im namen des echten Users.

**Was er tun kann:**
- Daten sehen die dem User gehörren
- Aktionen ausführen im Namen des Users

**Gegenmaßnahme:** 
- Token hat eine Ablaufzeit von 1 Stunde - gestohlener Token funktioniert nur kurz
- HTTPS verhindert Token-Abfangen im Netzwerk
- Token enthält keine sensiblen Daten wie Passwöter

**Status:** ✓ Teilweise implementiert - HTTPS fehlt noch (wird beim Cloud Deployment hinzugefügt)

## 3. Broken Access Control

**Bedrohung:** Ein eingeloggter User greift auf Daten oder Funktionen zu die seiner Rolle nicht erlaubt sind.

**Beispiele:**
- Kunde sieht Buchungen andere Kunden
- Kunde erstellt einen neue Agentur
- Mitarbeiter löscht einen Admin-Account

**Ursache:** Fehlende oder falsche Rollen-Prüfung in den Endpooints.

**Gegenmaßnahme:**
- Jeder Endpoint prüft die Rolle des eingeloggten Users via `require_admin` oder `require_staff`
- Kunden können nur ihre eigenen Buchungen sehen via `GET /bookings/me`
- User ID kommt aus dem JWT Token — nicht vom Client

## 4. Sensitive Data Exposure

**Bedrohung:** Ein Angreifer bekommt Zugriff auf die Datenbank und liest sensible Daten.

**Sensible Daten in SecureStay:**
- Passwörter
- Email Adressen
- Buchungshistorie

**Ursache:** Daten werden ungeschützt gespeichert.

**Gegenmaßnahme:**
- Passwörter werden nie im Klartext gespeichert — bcrypt Hashing mit Salt
- Datenbankpasswort liegt in `.env` — nie im Code oder auf GitHub
- JWT Secret liegt in `.env` — nie im Code oder auf GitHub

**Was noch fehlt:**
- Email Adressen sind unverschlüsselt — in Production sollte die Datenbank verschlüsselt sein (AWS RDS Encryption)

**Status:** ✓ Teilweise implementiert — volle Verschlüsselung beim Cloud Deployment

## 5. Brute Force Attack

**Bedrohung:** Ein Angreifer schickt tausende Login-Versuche mit verschiedenen Passwörtern um einen Account zu übernehmen.

**Ursache:** Kein Limit auf Login-Versuche — der Angreifer kann unbegrenzt versuchen.

**Gegenmaßnahme:**
- bcrypt ist bewusst langsam — jeder Hash-Vergleich dauert länger, das verlangsamt Brute Force
- Rate Limiting sollte auf `POST /login` implementiert werden — maximal 5 Versuche pro Minute pro IP

**Was noch fehlt:**
- Rate Limiting ist noch nicht implementiert
- Account Lockout nach X fehlgeschlagenen Versuchen fehlt noch

**Status:** ✗ Offen — wird beim Cloud Deployment mit AWS WAF implementierts