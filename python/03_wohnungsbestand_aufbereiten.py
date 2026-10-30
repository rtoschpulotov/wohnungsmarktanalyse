# ============================================================
#  Abschlussprojekt: Wohnungsmarkt & Mietpreise
#  Datei:  03_wohnungsbestand_aufbereiten.py
#  Autor:  Rustam T. (Data Engineering)
#  Zweck:  Die GENESIS-Datei zum Wohnungsbestand (Deutschland,
#          2015 bis 2024) in eine saubere CSV umwandeln.
#          Liefert die Daten für Hypothese H5.
# ============================================================

import csv
import os

# --- Arbeitsverzeichnis festnageln (wie in den anderen Skripten) ---
projekt_ordner = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(projekt_ordner)
os.makedirs("clean", exist_ok=True)

# --- Die Rohdatei einlesen ---
# encoding="utf-8-sig" entfernt ein unsichtbares Sonderzeichen,
# das GENESIS-Dateien am Anfang haben (das sogenannte BOM).
with open("rohdaten/31231-0001_flat.csv", encoding="utf-8-sig") as f:
    zeilen = f.readlines()

ergebnis = []
for zeile in zeilen:
    # Uns interessieren nur die echten Datenzeilen. Die erkennen
    # wir daran, dass sie mit einem Datum wie "31.12.2015" beginnen.
    # Prüfung: Stelle 3 und 6 sind ein Punkt (TT.MM.JJJJ).
    if len(zeile) > 10 and zeile[2] == "." and zeile[5] == ".":

        # Die Zeile am Semikolon in einzelne Felder zerlegen.
        teile = zeile.strip().split(";")

        # Aus "31.12.2015" nur das Jahr herausnehmen (die letzten 4 Zeichen
        # des ersten Feldes). int(...) macht daraus eine echte Zahl.
        jahr = int(teile[0][-4:])

        # Anzahl Wohnungen steht im Feld mit Index 1.
        wohnungen = int(teile[1])

        # Wohnungen je 1000 Einwohner steht im Feld mit Index 3.
        wohnungen_je_1000 = int(teile[3])

        # Wohnfläche je Einwohner steht im Feld mit Index 9.
        # Hier das deutsche Komma durch einen Punkt ersetzen,
        # damit Python die Kommazahl versteht.
        wohnflaeche_je_ew = float(teile[9].replace(",", "."))

        ergebnis.append({
            "stichtag_jahr": jahr,
            "wohnungen": wohnungen,
            "wohnungen_je_1000_ew": wohnungen_je_1000,
            "wohnflaeche_je_ew": wohnflaeche_je_ew,
        })

# --- Als saubere CSV speichern ---
with open("clean/wohnungsbestand_clean.csv", "w",
          newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["stichtag_jahr", "wohnungen",
                    "wohnungen_je_1000_ew", "wohnflaeche_je_ew"],
        delimiter=";",
    )
    writer.writeheader()
    writer.writerows(ergebnis)

# --- Kontrollausgabe ---
print(f"Fertig: {len(ergebnis)} Jahre geschrieben.")
print(f"Zeitraum: {ergebnis[0]['stichtag_jahr']} bis {ergebnis[-1]['stichtag_jahr']}")
print(f"Wohnungen 2024: {ergebnis[-1]['wohnungen']:,}")