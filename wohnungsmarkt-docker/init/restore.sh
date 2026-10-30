#!/bin/bash
# ============================================================
#  Restore-Skript
#
#  Dieses Skript liegt im Ordner init/ und wird vom PostgreSQL-
#  Container beim ALLERERSTEN Start automatisch ausgeführt, also
#  nur solange das Daten-Volume noch leer ist. Danach läuft es
#  nicht mehr.
#
#  Es sucht nach deiner Backup-Datei und spielt sie ein. Lege dazu
#  dein pgAdmin-Backup (custom format) in diesen init-Ordner und
#  nenne es genau:  wohnungsmarkt_db.backup
# ============================================================

set -e   # bei einem Fehler sofort abbrechen

BACKUP="/docker-entrypoint-initdb.d/wohnungsmarkt_db.backup"

if [ -f "$BACKUP" ]; then
    echo ">> Spiele Backup ein: $BACKUP"
    # pg_restore liest das custom-format Backup und schreibt es in die
    # bereits angelegte Datenbank. --no-owner und --no-privileges
    # ignorieren Besitzer- und Rechteangaben aus dem Backup, damit es
    # sauber in den frischen Container passt.
    pg_restore --no-owner --no-privileges \
        -U "$POSTGRES_USER" -d "$POSTGRES_DB" "$BACKUP"
    echo ">> Backup erfolgreich eingespielt."
else
    echo ">> Kein Backup gefunden unter $BACKUP."
    echo ">> Die Datenbank bleibt leer. Lege dein Backup in den init-Ordner."
fi
