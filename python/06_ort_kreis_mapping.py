# ============================================================
#  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
#  Datei:  06_ort_kreis_mapping.py
#  Autor:  Rustam T. (Data Engineering)
#  Zweck:  Eine Zuordnungstabelle bauen, die jeden Ortsnamen aus
#          den Mietdaten seinem amtlichen Kreisschlüssel zuordnet.
#          Diese Brücke erlaubt es, die Mieten später mit Einkommen
#          und Dichte (beide auf Kreisebene) zu verbinden (H4, H6).
#
#  Eingabe:  clean/mietangebote_clean.csv  (für die Ortsnamen)
#            rohdaten/04-kreise.xlsx        (für die Kreisnamen)
#  Ausgabe:  clean/ort_kreis_mapping.csv
#  Aufruf:   python python/06_ort_kreis_mapping.py
# ============================================================

import openpyxl
import csv
import os
import re

# --- Arbeitsverzeichnis festnageln (wie in den anderen Skripten) ---
projekt_ordner = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(projekt_ordner)
os.makedirs("clean", exist_ok=True)


# ------------------------------------------------------------
#  1. Alle Kreise mit Schlüssel und Name aus 04-kreise.xlsx
# ------------------------------------------------------------
wb = openpyxl.load_workbook("rohdaten/dichte_kreise.xlsx", read_only=True, data_only=True)
ws = wb["Kreisfreie Städte u. Landkreise"]

kreise = {}   # kreis_schluessel -> kreis_name
kreistyp = {} # kreis_schluessel -> "Kreisfreie Stadt", "Stadtkreis", "Landkreis" ...
for r in ws.iter_rows(values_only=True):
    schluessel = str(r[0]).strip() if r[0] else ""
    if len(schluessel) == 5 and schluessel.isdigit():
        kreise[schluessel] = str(r[2]).strip()
        kreistyp[schluessel] = str(r[1]).strip()


# ------------------------------------------------------------
#  2. Eine Funktion, die Namen in eine vergleichbare Grundform bringt
# ------------------------------------------------------------
# Die Schreibweisen unterscheiden sich zwischen den Quellen. In den
# Mietdaten steht z.B. "Pinneberg_Kreis", in der Kreistabelle nur
# "Pinneberg". Diese Funktion entfernt solche Unterschiede, damit wir
# die Namen vergleichen können: Umlaute, Unterstriche, Bindestriche,
# Klammerzusätze und Worte wie "Stadt", "Kreis", "Landkreis".
def normalisiere(name):
    n = name.lower()
    n = n.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    n = n.replace("_", " ").replace("-", " ")
    n = re.sub(r"\([^)]*\)", "", n)          # Klammerzusätze entfernen
    # ", stadtkreis" muss VOR ", stadt" stehen, sonst bleibt "kreis" übrig
    for zusatz in [", stadtkreis", ", stadt", ", landeshauptstadt", ", hansestadt",
                   ", kreisfreie stadt", ", wissenschaftsstadt",
                   ", documenta-stadt", ", documenta stadt",
                   ", universitaetsstadt",
                   ", grosse kreisstadt", " landkreis", " kreisfreie stadt"]:
        n = n.replace(zusatz, "")
    n = re.sub(r"\bkreis\b", "", n)
    n = re.sub(r"\bstadt\b", "", n)
    n = re.sub(r"\bsaale\b", "", n)
    n = re.sub(r"\boder\b", "", n)
    n = re.sub(r"\bim\b", "", n)
    n = re.sub(r"\ban der\b", "", n)
    n = re.sub(r"\ba d\b", "", n)
    n = re.sub(r"\bder\b", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n

# Kreisnamen in Grundform -> Schlüssel (für den automatischen Abgleich)
#
# Korrektur 10/2026: Vorher stand hier ein einziges Wörterbuch. Weil
# normalisiere() "Stadt", "Landeshauptstadt" usw. entfernt, wurden z.B.
# "München, Landeshauptstadt" (09162) und der Landkreis "München" (09184)
# beide zu "muenchen", und der Landkreis hat die Stadt überschrieben.
# Betroffen waren München, Leipzig, Kassel, Kaiserslautern, Osnabrück,
# Karlsruhe und Heilbronn, zusammen rund 20.900 Inserate.
# Bei Karlsruhe und Heilbronn kam noch ein zweiter Fehler dazu, siehe
# Reihenfolge der Zusätze in normalisiere().
# Deshalb jetzt zwei getrennte Wörterbücher: kreisfreie Städte und Landkreise.
def ist_stadt(schluessel):
    # die Destatis-Tabelle hat eine eigene Spalte mit dem Kreistyp
    return kreistyp.get(schluessel) in ("Kreisfreie Stadt", "Stadtkreis")

stadt_grundform = {}
landkreis_grundform = {}
for schluessel, name in kreise.items():
    ziel = stadt_grundform if ist_stadt(schluessel) else landkreis_grundform
    ziel[normalisiere(name)] = schluessel


# ------------------------------------------------------------
#  3. Manuelle Zuordnung für Sonderfälle
# ------------------------------------------------------------
# Manche Orte lassen sich nicht automatisch zuordnen, aus zwei Gründen:
#  - Großstädte mit Namenszusätzen in der Kreistabelle
#  - alte Kreise, die es durch die Kreisreform (v.a. 2011 in MV) nicht
#    mehr gibt; diese ordnen wir ihrem heutigen Nachfolgekreis zu.
manuell = {
    "Aachen": "05334", "Aachen_Kreis": "05334",           # Staedteregion Aachen
    "Altenkirchen_Westerwald_Kreis": "07132",
    "Bad_Doberan_Kreis": "13072",                          # -> Landkreis Rostock
    "Baden_Baden": "08211",
    "Bitburg_Prüm_Kreis": "07232",                         # Eifelkreis Bitburg-Pruem
    "Demmin_Kreis": "13071",                               # -> Mecklenburgische Seenplatte
    "Dillingen_an_der_Donau_Kreis": "09773",
    "Eisenach": "16063",                                   # -> Wartburgkreis
    "Frankenthal_Pfalz": "07311",
    "Freiburg_im_Breisgau": "08311",
    "Greifswald": "13075",                                 # -> Vorpommern-Greifswald
    "Güstrow_Kreis": "13072",                              # -> Landkreis Rostock
    "Hagen": "05914",
    "Hamburg": "02000",
    "Hannover": "03241", "Hannover_Kreis": "03241",        # Region Hannover
    "Heidelberg": "08221",
    "Hoyerswerda": "14625",                                # -> Bautzen
    "Kempten_Allgäu": "09763",
    "Lindau_Bodensee_Kreis": "09776",
    "Ludwigslust_Kreis": "13076",                          # -> Ludwigslust-Parchim
    "Mannheim": "08222",
    "Mecklenburg_Strelitz_Kreis": "13071",                 # -> Mecklenburgische Seenplatte
    "Mühldorf_am_Inn_Kreis": "09183",
    "Müritz_Kreis": "13071",                               # -> Mecklenburgische Seenplatte
    "Neubrandenburg": "13071",                             # -> Mecklenburgische Seenplatte
    "Neumarkt_in_der_Oberpfalz_Kreis": "09373",
    "Neuss_Rhein_Kreis": "05162",                          # Rhein-Kreis Neuss
    "Neustadt_a.d._Aisch_Bad_Windsheim_Kreis": "09575",
    "Neustadt_a.d._Waldnaab_Kreis": "09374",
    "Nienburg_Weser_Kreis": "03256",
    "Nordvorpommern_Kreis": "13073",                       # -> Vorpommern-Ruegen
    "Oldenburg_Oldenburg": "03403",                        # Stadt Oldenburg
    "Osterode_am_Harz_Kreis": "03159",                     # -> Goettingen
    "Ostvorpommern_Kreis": "13075",                        # -> Vorpommern-Greifswald
    "Parchim_Kreis": "13076",                              # -> Ludwigslust-Parchim
    "Pfaffenhofen_an_der_Ilm_Kreis": "09186",
    "Pforzheim": "08231",
    "Plauen": "14523",                                     # -> Vogtlandkreis
    "Rotenburg_Wümme_Kreis": "03357",
    "Rügen_Kreis": "13073",                                # -> Vorpommern-Ruegen
    "Sankt_Wendel_Kreis": "10046",
    "Solingen": "05122",
    "Soltau_Fallingbostel_Kreis": "03358",                 # Heidekreis
    "Stadtverband_Saarbrücken_Kreis": "10041",             # Regionalverband Saarbruecken
    "Stralsund": "13073",                                  # -> Vorpommern-Ruegen
    "Stuttgart": "08111",
    "Uecker_Randow_Kreis": "13075",                        # -> Vorpommern-Greifswald
    "Ulm": "08421",
    "Weiden_in_der_Oberpfalz": "09363",
    "Wismar": "13074",                                     # -> Nordwestmecklenburg
    "Wunsiedel_im_Fichtelgebirge_Kreis": "09479",
}


# ------------------------------------------------------------
#  4. Alle Ortsnamen aus den Mietdaten sammeln und zuordnen
# ------------------------------------------------------------
orte = set()
with open("clean/mietangebote_clean.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f, delimiter=";"):
        orte.add(row["ort"])

ergebnis = []
nicht_zugeordnet = []
for ort in sorted(orte):
    # Erst die manuelle Liste, dann der automatische Abgleich.
    grundform = normalisiere(ort)
    # "_Kreis" im Ortsnamen = Landkreis, sonst zuerst bei den Städten suchen
    if ort.endswith("_Kreis"):
        reihenfolge = (landkreis_grundform, stadt_grundform)
    else:
        reihenfolge = (stadt_grundform, landkreis_grundform)
    automatisch = next((d[grundform] for d in reihenfolge if grundform in d), None)

    if ort in manuell:
        ks = manuell[ort]
    elif automatisch:
        ks = automatisch
    else:
        nicht_zugeordnet.append(ort)
        continue
    ergebnis.append({
        "ort": ort,
        "kreis_schluessel": ks,
        "kreis_name": kreise[ks],
    })


# ------------------------------------------------------------
#  5. Ergebnis als CSV speichern
# ------------------------------------------------------------
with open("clean/ort_kreis_mapping.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["ort", "kreis_schluessel", "kreis_name"], delimiter=";")
    writer.writeheader()
    writer.writerows(ergebnis)


# --- Kontrollausgabe ---
print(f"Zugeordnet: {len(ergebnis)} Orte")
print(f"Nicht zugeordnet: {len(nicht_zugeordnet)}")
if nicht_zugeordnet:
    print("  Offen:", nicht_zugeordnet)