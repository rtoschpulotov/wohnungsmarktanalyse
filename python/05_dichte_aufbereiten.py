# ============================================================
#  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
#  Datei:  05_dichte_aufbereiten.py
#  Autor:  Rustam T. (Data Engineering)
#  Zweck:  Aus dem Gemeindeverzeichnis (04-kreise.xlsx) je Kreis
#          die Fläche, Bevölkerung und Bevölkerungsdichte
#          herausziehen. Liefert die Daten für Hypothese H6
#          (erklärt die Dichte die Mietpreisunterschiede).
#
#  Eingabe:  rohdaten/04-kreise.xlsx
#  Ausgabe:  clean/dichte_kreise_clean.csv
#  Aufruf:   python python/05_dichte_aufbereiten.py
# ============================================================

import openpyxl
import csv
import os

# --- Arbeitsverzeichnis festnageln (wie in den anderen Skripten) ---
projekt_ordner = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(projekt_ordner)
os.makedirs("clean", exist_ok=True)


# --- Die Excel öffnen, nur das Datenblatt mit den Kreisen ---
wb = openpyxl.load_workbook("rohdaten/dichte_kreise.xlsx",
                            read_only=True, data_only=True)
ws = wb["Kreisfreie Städte u. Landkreise"]
rows = list(ws.iter_rows(values_only=True))


# --- Die Kreise herausfiltern ---
# In der Datei stehen auch Zwischenzeilen (Bundesland-Ueberschriften,
# "Insgesamt"-Summen, statistische Regionen). Die haben keinen oder
# einen zu kurzen Schlüssel. Wir behalten nur echte Kreise, die wir
# am 5-stelligen Kreisschlüssel erkennen.
ergebnis = []
for r in rows:
    schluessel = str(r[0]).strip() if r[0] else ''

    # Nur echte Kreise (5-stelliger Schlüssel aus Ziffern).
    if len(schluessel) == 5 and schluessel.isdigit():
        name = str(r[2]).strip() if r[2] else ''
        flaeche = r[4]          # Fläche in km2 (Spalte 4)
        bevoelkerung = r[5]     # Bevölkerung insgesamt (Spalte 5)
        dichte = r[8]           # Einwohner je km2 (Spalte 8, schon fertig)

        # Sicherheitscheck: nur übernehmen, wenn die Dichte da ist.
        if dichte is not None:
            ergebnis.append({
                "kreis_schluessel": schluessel,
                "kreis_name": name,
                "flaeche_qkm": flaeche,
                "bevoelkerung": bevoelkerung,
                "dichte_ew_qkm": dichte,
            })


# --- Als saubere CSV speichern ---
with open("clean/dichte_kreise_clean.csv", "w",
          newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["kreis_schluessel", "kreis_name",
                    "flaeche_qkm", "bevoelkerung", "dichte_ew_qkm"],
        delimiter=";",
    )
    writer.writeheader()
    writer.writerows(ergebnis)


# --- Kontrollausgabe ---
print(f"Fertig: {len(ergebnis)} Kreise geschrieben.")
dichten = [float(r["dichte_ew_qkm"]) for r in ergebnis]
print(f"Bevoelkerungsdichte: {min(dichten):.0f} bis {max(dichten):.0f} Einwohner je km2")
