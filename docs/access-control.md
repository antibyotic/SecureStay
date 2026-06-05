# Access Control — SecureStay

## Rollen

| Rolle | Beschreibung |
|---|---|
| Besucher | Kein Account, nur schauen |
| Kunde | Sucht und bucht Immobilien |
| Mitarbeiter | Verwaltet die Plattform |
| Admin | Voller Zugriff |

## Zugriffsrechte

### Besucher
- Verfügbare Immobilien sehen

### Kunde
- Verfügbare Immobilien sehen
- Nur eigene Buchungen sehen
- Fremde Buchungen: kein Zugriff

### Mitarbeiter
- Alle Immobilien sehen inkl. extra Details
- Plattform verwalten
- ein mitarbeiter kann immobilien erstellen

### Admin
- Alles — innerhalb gesetzlicher Grenzen


## API Zugriffsrechte

| Endpoint | Methode | Berechtigung |
|---|---|---|
| /register | POST | Öffentlich |
| /login | POST | Öffentlich |
| /agencies | POST | Admin |
| /agencies | GET | Mitarbeiter, Admin |
| /agencies/{id} | GET | Mitarbeiter, Admin |
| /properties | POST | Mitarbeiter, Admin |
| /properties | GET | Alle eingeloggten User |
| /properties/{id} | GET | Alle eingeloggten User |