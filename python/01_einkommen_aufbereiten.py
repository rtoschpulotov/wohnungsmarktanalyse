# ============================================================
# Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
# Datei: 01_einkommen_aufbereiten.py
# Zweck: Offizielle VGRdL-Einkommens-Excel (Blatt 2.4) in eine
#        schlanke CSV umwandeln, die das Import-Skript erwartet.
# Autor:  Rustam T. (Data Engineering)
# Eingabe : rohdaten/einkommen_kreise.xlsx  (Blatt "2.4", Jahr 2019)
# Ausgabe : clean/einkommen_kreise_clean.csv
# Start   : python 01_einkommen_aufbereiten.py
# ============================================================

import openpyxl
from pathlib import Path
import csv

# Bundesland aus den ersten zwei Ziffern des Kreisschlüssels (AGS)
BUNDESLAND = {
    '01': 'Schleswig-Holstein', '02': 'Hamburg', '03': 'Niedersachsen',
    '04': 'Bremen', '05': 'Nordrhein-Westfalen', '06': 'Hessen',
    '07': 'Rheinland-Pfalz', '08': 'Baden-Wuerttemberg', '09': 'Bayern',
    '10': 'Saarland', '11': 'Berlin', '12': 'Brandenburg',
    '13': 'Mecklenburg-Vorpommern', '14': 'Sachsen', '15': 'Sachsen-Anhalt',
    '16': 'Thueringen',
}

# Stadtstaaten stehen in der Excel als 2-stellige Landeszeile.
# Wir geben ihnen den amtlichen 5-stelligen Kreisschlüssel,
# damit der Join mit den Mietdaten später funktioniert.
STADTSTAATEN = {'11': '11000', '02': '02000'}   # Berlin, Hamburg

# --- Excel öffnen, nur das Datenblatt 2.4 (Einkommen je Einwohner) ---
wb = openpyxl.load_workbook(r"C:\Users\User\Desktop\DSI-Ordner\1-Abschlussprojekt-Wohnungsnot in Duetschland\rohdaten\einkommen_kreise.xlsx",
                            read_only=True, data_only=True)
ws = wb['2.4']
rows = list(ws.iter_rows(values_only=True))

# Die Kopfzeile mit den Jahreszahlen steht in Zeile mit Index 4.
# Daraus die Spaltennummer für 2019 holen (statt sie fest zu verdrahten).
header = rows[4]
idx_2019 = list(header).index(2019)

ergebnis = []
for r in rows[6:]:                       # ab Zeile 6 beginnen die Daten
    schluessel = str(r[2]).strip() if r[2] else ''   # Spalte Regionalschlüssel
    name = str(r[7]).strip() if r[7] else ''         # Spalte Gebietseinheit
    wert = r[idx_2019]                               # Einkommen 2019

    if wert is None:
        continue

    if len(schluessel) == 5 and schluessel.isdigit():
        kreis_schluessel = schluessel                # normaler Landkreis
    elif schluessel in STADTSTAATEN:
        kreis_schluessel = STADTSTAATEN[schluessel]  # Berlin / Hamburg
    else:
        continue                                     # Land/NUTS-Ebenen weg

    ergebnis.append({
        'kreis_schluessel': kreis_schluessel,
        'kreis_name': name,
        'bundesland': BUNDESLAND.get(kreis_schluessel[:2], 'unbekannt'),
        'einkommen_je_ew': wert,
        'berichtsjahr': 2019,
    })

# --- Als CSV speichern (Semikolon-getrennt, UTF-8) ---


projekt = Path(__file__).resolve().parent.parent
clean_dir = projekt / "clean"
clean_dir.mkdir(exist_ok=True)

with open(clean_dir / "einkommen_kreise_clean.csv",
          "w",
          newline="",
          encoding="utf-8") as f:


#with open('clean/einkommen_kreise_clean.csv', 'w', newline='', encoding='utf-8') as f:"""
    writer = csv.DictWriter(
        f,
        fieldnames=['kreis_schluessel', 'kreis_name', 'bundesland',
                    'einkommen_je_ew', 'berichtsjahr'],
        delimiter=';',
    )
    writer.writeheader()
    writer.writerows(ergebnis)

# --- Kurze Kontrollausgabe ---
print(f'Fertig: {len(ergebnis)} Kreise geschrieben.')
laender = set(r['bundesland'] for r in ergebnis)
print(f'Bundeslaender abgedeckt: {len(laender)} von 16')
werte = [r['einkommen_je_ew'] for r in ergebnis]
print(f'Einkommen je Einwohner 2019: {min(werte):,} bis {max(werte):,} EUR')