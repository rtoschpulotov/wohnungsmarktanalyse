# ============================================================
#  Abschlussprojekt: Wohnungsmarkt & Mietpreise
#  Datei:  04_baupreise_aufbereiten.py
#  Autor:  Rustam T. (Data Engineering)
# ============================================================


# Wir holen uns die Werkzeuge von Spark, die wir brauchen.
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import os

# --- Arbeitsverzeichnis festnageln --------------------------------
# Relative Pfade hängen davon ab, von wo man das Skript startet.
# Damit das Skript von überall funktioniert, ermitteln wir, wo
# diese Datei liegt (im Ordner python/), gehen eine Ebene hoch
# (in den Projektordner) und machen das zum Arbeitsverzeichnis.
projekt_ordner = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(projekt_ordner)
os.makedirs("clean", exist_ok=True)


# Datei einlesen. encoding="utf-8-sig" entfernt das unsichtbare
# Sonderzeichen am Anfang, das GENESIS-Dateien immer haben.

with open("rohdaten/61261-0001_flat.csv", encoding="utf-8-sig") as f:
    zeilen = f.readlines()

# Wir brauchen zwei bestimmte Zeilen aus der Datei:
kopfzeile_jahre = None    # die Zeile mit den Jahreszahlen
daten_zeile = None        # die Zeile "Bauleistungen am Bauwerk"

# Alle Zeilen durchgehen und die zwei gesuchten herausfischen.
for zeile in zeilen:

    # Die Kopfzeile mit den Jahren erkennen wir daran, dass darin
    # eine "2021" vorkommt und sie mit Semikolons beginnt (also
    # keine normale Textzeile ist).
    if ";;2021" in zeile:
        kopfzeile_jahre = zeile

    # Die Datenzeile, die wir wollen, beginnt mit genau diesem Text.
    # "Bauleistungen am Bauwerk" ist die Gesamtsumme aller Bauarbeiten.
    if zeile.startswith("Wohngebäude;Bauleistungen am Bauwerk"): # zeile.startswith("...") prüft, ob die Zeile mit genau diesem Text beginnt
        daten_zeile = zeile

# Kurze Kontrolle, ob wir beide Zeilen gefunden haben.
print("Kopfzeile gefunden:", kopfzeile_jahre is not None)
print("Datenzeile gefunden:", daten_zeile is not None)

# Beide Zeilen in einzelne Felder zerlegen (am Semikolon trennen).
jahre_felder = kopfzeile_jahre.strip().split(";")
daten_felder = daten_zeile.strip().split(";")

# In dieses Dictionary sammeln wir pro Jahr einen Wert.
# Ein Dictionary merkt sich Paare, hier: Jahr -> Indexwert.
baupreise_pro_jahr = {}

# Wir gehen alle Felder gemeinsam durch. enumerate gibt uns
# zu jedem Feld auch seine Position (i), die brauchen wir, um
# im Daten-Feld an derselben Stelle nachzuschauen.
for i, feld in enumerate(jahre_felder):
    feld = feld.strip()

    # Uns interessieren nur Felder, die eine Jahreszahl enthalten.
    # isdigit() prüft, ob das Feld nur aus Ziffern besteht,
    # und len == 4 stellt sicher, dass es ein Jahr wie "2021" ist.
    if feld.isdigit() and len(feld) == 4:
        jahr = int(feld)

        # Dieses Jahr haben wir vielleicht schon (es kommt mehrfach
        # vor). Nur wenn es noch NICHT drin ist, holen wir den Wert.
        # So nehmen wir automatisch den ersten Wert pro Jahr.
        if jahr not in baupreise_pro_jahr:

            # Der Wert steht an derselben Position in der Datenzeile.
            wert_text = daten_felder[i].strip()

            # Manche Werte sind "-" (kein Wert). Die überspringen wir.
            if wert_text and wert_text != "-":
                # Deutsches Komma in Punkt umwandeln, dann in Zahl.
                wert = float(wert_text.replace(",", "."))
                baupreise_pro_jahr[jahr] = wert

# Zur Kontrolle ausgeben, was wir gesammelt haben.
print("Gesammelte Baupreise je Jahr:")
for jahr in sorted(baupreise_pro_jahr):
    print(f"  {jahr}: {baupreise_pro_jahr[jahr]}")

# ------------------------------------------------------------
#  Teil 3: Ergebnis als saubere CSV speichern
# ------------------------------------------------------------
import csv

with open("clean/baupreise_clean.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["berichtsjahr", "baupreisindex"],
        delimiter=";",
    )
    writer.writeheader()
    # Jahre der Reihe nach (sortiert) in die Datei schreiben.
    for jahr in sorted(baupreise_pro_jahr):
        writer.writerow({
            "berichtsjahr": jahr,
            "baupreisindex": baupreise_pro_jahr[jahr],
        })

print(f"Gespeichert: clean/baupreise_clean.csv mit {len(baupreise_pro_jahr)} Jahren.")