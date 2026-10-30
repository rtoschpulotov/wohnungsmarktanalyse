# Wohnungsmarkt-Projekt im Docker-Container

Dieses Setup startet die komplette Datengrundlage des Projekts in
Containern: die PostgreSQL-Datenbank, die grafische Oberfläche pgAdmin
und eine Python-Umgebung, in der die seaborn-Skripte laufen. Damit kann
jeder im Team das Projekt mit wenigen Befehlen starten, ohne irgendetwas
lokal zu installieren.

## Warum das nützlich ist

Bisher musste PostgreSQL lokal installiert sein, und die Version musste
beim Einspielen des Backups genau passen. Mit Docker ist die Version im
Container festgelegt. Wer das Projekt übernimmt, startet einen Befehl
und hat exakt dieselbe Datenbank, unabhängig vom eigenen Rechner. Auch
die Python-Pakete sind fest verdrahtet, niemand muss pip-Befehle
nachbauen.

## Was du vorher brauchst

Docker Desktop muss installiert sein. Unter Windows wird dabei WSL2
mitverwendet, das richtet Docker Desktop bei der Installation ein.
Prüfen kannst du es im Terminal mit `docker --version`.

## Die Ordnerstruktur

    wohnungsmarkt-docker/
    │
    ├─ docker-compose.yml        zentrale Steuerdatei, beschreibt alle drei Bausteine
    ├─ .env.example              Vorlage für die Passwörter
    ├─ .gitignore                schützt Passwörter und Backup vor GitHub
    │
    ├─ init/                     wird beim ersten Start automatisch ausgeführt
    │   ├─ restore.sh            spielt das Backup ein
    │   └─ (hier dein wohnungsmarkt_db.backup ablegen)
    │
    ├─ pgadmin/
    │   └─ servers.json          meldet die DB-Verbindung in pgAdmin vor
    │
    ├─ python_app/               die Python-Umgebung
    │   ├─ Dockerfile            baut das Python-Image
    │   ├─ requirements.txt      die nötigen Pakete
    │   └─ scripts/              hier liegen die seaborn-Skripte
    │
    └─ visualisierungen/         hier landen die erzeugten Bilder

## So startest du, Schritt für Schritt

### Schritt 1: Passwörter setzen

Kopiere die Datei `.env.example` und nenne die Kopie `.env`. Trage darin
deine eigenen Passwörter ein. Die Datei `.env` bleibt auf deinem
Rechner und wird nicht weitergegeben.

### Schritt 2: Backup bereitlegen

Lege dein pgAdmin-Backup in den Ordner `init/` und nenne es genau
`wohnungsmarkt_db.backup`. Es muss von PostgreSQL 17 stammen, damit es
zur Version im Container passt. Wenn die Fremdschlüssel schon gesetzt
waren, als du das Backup erstellt hast, sind sie automatisch mit dabei.

### Schritt 3: Datenbank und pgAdmin starten

    docker compose up -d

Beim allerersten Start lädt PostgreSQL dein Backup automatisch ein, das
kann einen Moment dauern. Mit `docker compose logs -f db` kannst du
zusehen.

### Schritt 4: In pgAdmin schauen

Öffne im Browser `http://localhost:5050` und melde dich mit der E-Mail
und dem pgAdmin-Passwort aus deiner `.env` an. Die Verbindung
"Wohnungsmarkt (Docker)" ist schon vorgemeldet. Beim ersten Verbinden
fragt pgAdmin nach dem Datenbank-Passwort, das ist das `DB_PASSWORT` aus
deiner `.env`.

### Schritt 5: Die seaborn-Diagramme erzeugen

    docker compose run --rm python python scripts/08_visualisierung_seaborn.py

Dieser Befehl startet die Python-Umgebung, verbindet sich mit der
Datenbank und legt die sieben Diagramme im Ordner `visualisierungen/`
ab. Das `--rm` räumt den Container danach wieder auf.

### Schritt 6: Stoppen

    docker compose down

Die Daten bleiben dabei erhalten, weil sie im Volume `db_data` liegen.
Beim nächsten `up` ist alles wieder da. Das Backup wird dann NICHT
erneut eingespielt, weil die Datenbank ja schon gefüllt ist.

## Zwei Dinge, die man wissen muss

Erstens, das automatische Einspielen des Backups passiert nur beim
ersten Start, solange das Daten-Volume leer ist. Willst du wirklich bei
null anfangen und das Backup neu einspielen lassen, musst du das Volume
löschen:

    docker compose down -v

Das `-v` löscht das Volume und damit alle Daten. Danach spielt der
nächste Start das Backup wieder frisch ein.

Zweitens, falls du unter Windows arbeitest: Die Datei `restore.sh` muss
sogenannte Unix-Zeilenenden (LF) haben, nicht Windows-Zeilenenden
(CRLF). Falls das Restore mit einem seltsamen Fehler abbricht, öffne
`restore.sh` in einem Editor wie VS Code, stelle unten rechts von CRLF
auf LF um und speichere neu.

## Wie das Python-Skript beide Welten bedient

Das Skript `08_visualisierung_seaborn.py` liest die Verbindungsdaten aus
Umgebungsvariablen. Sind keine gesetzt, nimmt es die lokalen
Standardwerte (Host localhost). Im Container setzt die docker-compose.yml
den Host auf `db`, weil die Datenbank dort unter diesem Namen erreichbar
ist. So läuft genau dasselbe Skript lokal und im Container, ohne dass du
etwas ändern musst.
