# ============================================================
#  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
#  Datei:  07_verbraucherpreise_aufbereiten.py
#  Autor:  Rustam T. (Data Engineering)
#  Zweck:  Die Verbraucherpreise als Vergleichsreihe für H7
#          aufbereiten (Baupreise gegen allgemeine Inflation).
#
#  Eingabe:  rohdaten/61111-0001_de_flat.csv  (GENESIS Flat-File)
#  Ausgabe:  clean/verbraucherpreise_clean.csv
#  Aufruf:   python python/07_verbraucherpreise_aufbereiten.py
# ============================================================

import csv
import os

# --- Arbeitsverzeichnis festnageln (wie in den anderen Skripten) ---
# Egal von wo das Skript gestartet wird, wir setzen das
# Arbeitsverzeichnis auf den Projektordner.
projekt_ordner = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(projekt_ordner)
os.makedirs("clean", exist_ok=True)


# ------------------------------------------------------------
#  1. Die GENESIS-Datei einlesen
# ------------------------------------------------------------
# Die Datei ist ein "Flat-File": eine Zeile pro Wert. Sie hat ein
# unsichtbares BOM-Zeichen am Anfang, deshalb encoding="utf-8-sig".
# Das Trennzeichen ist das Semikolon.
#
# Wichtig: Pro Jahr gibt es ZWEI Zeilen. Eine enthält den Index
# (Einheit "2020=100"), die andere die Veränderung in Prozent
# (Einheit "%"). Uns interessiert nur die Index-Zeile.
#
# Die Spalten, die wir brauchen (von 0 an gezählt):
#   Spalte 4  = das Jahr
#   Spalte 9  = der Wert
#   Spalte 10 = die Einheit ("2020=100" oder "%")

vpi_2020_basis = {}   # Jahr -> Indexwert (amtliche Basis 2020 = 100)

with open("rohdaten/61111-0001_de_flat.csv", encoding="utf-8-sig") as f:
    reader = csv.reader(f, delimiter=";")
    next(reader)   # die Kopfzeile überspringen

    for zeile in reader:
        # Sehr kurze Zeilen (z.B. der Fußzeilen-Block) überspringen.
        if len(zeile) < 11:
            continue

        jahr = zeile[4].strip()
        wert = zeile[9].strip()
        einheit = zeile[10].strip()

        # Nur die Index-Zeilen nehmen (Einheit "2020=100"),
        # nicht die Prozent-Zeilen.
        if einheit != "2020=100":
            continue

        # Nur echte Jahreszahlen verarbeiten.
        if not jahr.isdigit():
            continue

        # Deutsches Komma in einen Punkt umwandeln, dann als Zahl.
        wert_zahl = float(wert.replace(",", "."))
        vpi_2020_basis[int(jahr)] = wert_zahl


# ------------------------------------------------------------
#  2. Nur die Jahre 2021 bis 2025 behalten
# ------------------------------------------------------------
# Die Baupreise beginnen bei 2021. Damit beide Reihen exakt
# denselben Zeitraum abdecken, beschränken wir uns auf 2021 bis 2025.
jahre = [j for j in sorted(vpi_2020_basis) if 2021 <= j <= 2025]


# ------------------------------------------------------------
#  3. Umbasieren auf 2021 = 100
# ------------------------------------------------------------
# Die Baupreise haben das Basisjahr 2021 = 100, der Verbraucher-
# preisindex amtlich 2020 = 100. Damit man beide fair vergleichen
# kann, rechnen wir den Verbraucherpreisindex so um, dass auch er
# 2021 bei 100 startet. Formel: Wert geteilt durch den Wert von
# 2021, mal 100.
wert_2021 = vpi_2020_basis[2021]

ergebnis = []
for jahr in jahre:
    umbasiert = round(vpi_2020_basis[jahr] / wert_2021 * 100, 1)
    ergebnis.append({
        "berichtsjahr": jahr,
        "verbraucherpreisindex": umbasiert,
    })


# ------------------------------------------------------------
#  4. Als saubere CSV speichern
# ------------------------------------------------------------
with open("clean/verbraucherpreise_clean.csv", "w",
          newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f, fieldnames=["berichtsjahr", "verbraucherpreisindex"], delimiter=";")
    writer.writeheader()
    writer.writerows(ergebnis)


# --- Kontrollausgabe ---
print("Eingelesene Jahre (amtliche Basis 2020 = 100):")
for j in sorted(vpi_2020_basis):
    print(f"  {j}: {vpi_2020_basis[j]}")
print()
print("Gespeichert, umbasiert auf 2021 = 100:")
for r in ergebnis:
    print(f"  {r['berichtsjahr']}: {r['verbraucherpreisindex']}")