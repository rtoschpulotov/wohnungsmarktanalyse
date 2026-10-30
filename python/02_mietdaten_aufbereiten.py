# ============================================================
#  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
#  Datei:  02_mietdaten_aufbereiten.py
#  Autor:  Rustam T. (Data Engineering)
#  Zweck:  Den großen Mietdatensatz (immo_data.csv) mit PySpark
#          bereinigen: unplausible Inserate entfernen, neue Spalten
#          berechnen, PLZ reparieren, Zustand übersetzen, fehlende
#          Werte sauber behandeln und das Ergebnis speichern.
#
#  Eingabe:  rohdaten/immo_data.csv      (ca. 269.000 Inserate)
#  Ausgabe:  clean/mietangebote_clean.csv
#  Aufruf:   python python/02_mietdaten_aufbereiten.py
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


# ------------------------------------------------------------
#  Teil 1: Spark starten und die Rohdaten laden
# ------------------------------------------------------------

# Spark starten. Man kann sich das wie das Anschalten einer
# großen Verarbeitungsmaschine vorstellen.
spark = SparkSession.builder \
    .appName("Mietdaten Cleaning") \
    .getOrCreate()

# Die Mietdaten-CSV in Spark laden.
#   header=True      -> erste Zeile enthält die Spaltennamen
#   inferSchema=True -> Spark erkennt selbst Zahl vs. Text
#   multiLine=True   -> Beschreibungstexte gehen über mehrere Zeilen
#   escape='"'       -> Anführungszeichen in Texten korrekt behandeln
mieten = spark.read \
    .option("header", True) \
    .option("inferSchema", True) \
    .option("multiLine", True) \
    .option("escape", '"') \
    .csv("rohdaten/immo_data.csv")

# Kontrollzahl: Startwert für das Cleaning-Protokoll.
anzahl_start = mieten.count()
print(f"Geladene Inserate: {anzahl_start}")


# ------------------------------------------------------------
#  Teil 2: Unbrauchbare Inserate herausfiltern
# ------------------------------------------------------------

# Durchgang 1: Nur plausible Kaltmieten behalten (100 bis 10.000 EUR).
mieten = mieten.filter(
    (F.col("baseRent") >= 100) & (F.col("baseRent") <= 10000)
)
anzahl_nach_miete = mieten.count()
print(f"Nach Mietpreis-Filter: {anzahl_nach_miete}")

# Durchgang 2: Nur plausible Wohnflächen behalten (10 bis 400 qm).
mieten = mieten.filter(
    (F.col("livingSpace") >= 10) & (F.col("livingSpace") <= 400)
)
anzahl_nach_flaeche = mieten.count()
print(f"Nach Flaechen-Filter: {anzahl_nach_flaeche}")


# ------------------------------------------------------------
#  Teil 3: Neue Spalten berechnen und Daten korrigieren
# ------------------------------------------------------------

# Neue Spalte "miete_pro_qm": Kaltmiete geteilt durch Wohnfläche.
# Das ist DIE Vergleichskennzahl, denn nur pro Quadratmeter kann
# man große und kleine Wohnungen fair vergleichen.
mieten = mieten.withColumn(
    "miete_pro_qm",
    F.round(F.col("baseRent") / F.col("livingSpace"), 2)
)

# Dritter Filter: unsinnige qm-Preise aussortieren (3 bis 60 EUR/qm).
mieten = mieten.filter(
    (F.col("miete_pro_qm") >= 3) & (F.col("miete_pro_qm") <= 60)
)
anzahl_nach_qm = mieten.count()
print(f"Nach qm-Preis-Filter: {anzahl_nach_qm}")

# --- KORREKTUR 1: PLZ reparieren ---
# In den Rohdaten fehlt bei ostdeutschen PLZ die führende Null
# (z.B. "8527" statt "08527" für Plauen), weil die PLZ als Zahl
# statt als Text behandelt wurde. lpad ("left pad") füllt von
# links mit Nullen auf, bis die PLZ genau 5 Stellen hat.
# cast("string") stellt sicher, dass die PLZ als Text behandelt wird.
mieten = mieten.withColumn(
    "plz",
    F.lpad(F.col("geo_plz").cast("string"), 5, "0")
)

# --- KORREKTUR 2: Zustand ins Deutsche übersetzen ---
# Die Originalwerte sind englisch. Wir übersetzen sie über eine
# Wenn-dann-Kette. Das ".otherwise" am Ende fängt automatisch alle
# "NA"- und Leerwerte ab und macht daraus "unbekannt".
mieten = mieten.withColumn(
    "zustand",
    F.when(F.col("condition") == "well_kept", "gepflegt")
     .when(F.col("condition") == "refurbished", "saniert")
     .when(F.col("condition") == "fully_renovated", "vollständig renoviert")
     .when(F.col("condition") == "first_time_use", "Erstbezug")
     .when(F.col("condition") == "mint_condition", "neuwertig")
     .when(F.col("condition") == "modernized", "modernisiert")
     .when(F.col("condition") == "first_time_use_after_refurbishment", "Erstbezug nach Sanierung")
     .when(F.col("condition") == "negotiable", "verhandelbar")
     .when(F.col("condition") == "need_of_renovation", "renovierungsbedürftig")
     .when(F.col("condition") == "ripe_for_demolition", "abrissreif")
     .otherwise("unbekannt")
)

# --- KORREKTUR 3: Baujahr bereinigen ---
# "NA"-Texte und unplausible Jahre (vor 1850 oder nach 2025) in
# echte Leerwerte (NULL) umwandeln, damit man später damit rechnen
# kann. Plausible Jahre werden als ganze Zahl übernommen.
mieten = mieten.withColumn(
    "baujahr",
    F.when(
        (F.col("yearConstructed") >= 1850) & (F.col("yearConstructed") <= 2025),
        F.col("yearConstructed").cast("int")
    ).otherwise(None)
)


# --- KORREKTUR 4: Nebenkosten bereinigen ---
# In den Rohdaten steht bei fehlenden Nebenkosten der Text "NA".
# Spark kann diese Spalte deshalb nicht als Zahl lesen. Wir wandeln
# sie ausdrücklich in eine Zahl um (cast als double). Alles, was
# keine gültige Zahl ist (also "NA"), wird dabei automatisch zu NULL.
# So wird aus "nicht angegeben" ein ehrlicher Leerwert, keine 0.
mieten = mieten.withColumn(
    "serviceCharge",
    F.col("serviceCharge").cast("double")
)

# Neue Spalte "region_ost_west": Ost, West oder Berlin.
# Berlin wird bewusst getrennt geführt (siehe Hypothese H3).
ost_bundeslaender = [
    "Brandenburg", "Mecklenburg_Vorpommern", "Sachsen",
    "Sachsen_Anhalt", "Thüringen"
]
mieten = mieten.withColumn(
    "region_ost_west",
    F.when(F.col("regio1") == "Berlin", "Berlin")
     .when(F.col("regio1").isin(ost_bundeslaender), "Ost")
     .otherwise("West")
)

# ------------------------------------------------------------
#  Teil 4: Spalten aufräumen, speichern, Protokoll
# ------------------------------------------------------------

# Sicherheitsnetz: doppelte Inserate über die scoutId entfernen.
mieten = mieten.dropDuplicates(["scoutId"])

# Nur die benötigten Spalten behalten und auf deutsche Namen
# umbenennen. Achtung: plz, zustand, baujahr und region_ost_west
# sind bereits unsere neuen, korrigierten Spalten von oben.
mieten_fertig = mieten.select(
    F.col("scoutId").alias("angebot_id"),
    F.col("regio1").alias("bundesland"),
    F.col("plz"),
    F.col("regio2").alias("ort"),
    F.col("baseRent").alias("kaltmiete"),
    F.col("serviceCharge").alias("nebenkosten"),
    F.col("livingSpace").alias("wohnflaeche_qm"),
    F.col("miete_pro_qm"),
    F.col("noRooms").alias("zimmer"),
    F.col("baujahr"),
    F.col("zustand"),
    F.col("balcony").alias("balkon"),
    F.col("hasKitchen").alias("einbaukueche"),
    F.col("lift").alias("aufzug"),
    F.col("date").alias("scrape_datum"),
    F.col("region_ost_west"),
)

# Das saubere Ergebnis speichern.
# Wichtig für Windows: Sparks eigener Schreiber braucht winutils.exe,
# das hier fehlt. Deshalb wandeln wir das Ergebnis in einen Pandas-
# DataFrame um und lassen Pandas speichern (braucht kein Hadoop).
anzahl_final = mieten_fertig.count()
mieten_pandas = mieten_fertig.toPandas()

# encoding="utf-8-sig" setzt einen unsichtbaren Stempel, damit das
# deutsche Excel die Datei auch beim Doppelklick mit korrekten
# Umlauten öffnet.
mieten_pandas.to_csv(
    "clean/mietangebote_clean.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig",
)

# Das komplette Cleaning-Protokoll auf einen Blick.
# Diese Zahlen kommen 1:1 auf die Daten-Folie der Präsentation!
print("=" * 55)
print("CLEANING-PROTOKOLL")
print("=" * 55)
print(f"  Start (Rohdaten):        {anzahl_start}")
print(f"  Nach Mietpreis-Filter:   {anzahl_nach_miete}")
print(f"  Nach Flaechen-Filter:    {anzahl_nach_flaeche}")
print(f"  Nach qm-Preis-Filter:    {anzahl_nach_qm}")
print(f"  Final gespeichert:       {anzahl_final}")
print(f"  Insgesamt entfernt:      {anzahl_start - anzahl_final}")
print("=" * 55)

# Spark sauber herunterfahren.
spark.stop()