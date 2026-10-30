# ============================================================
#  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
#  Datei:  08_visualisierung_seaborn.py
#  Autor:  Rustam T. (Data Engineering)
#
#  Zweck:  Bonus. Alle sieben Hypothesen einmal mit seaborn
#          direkt aus der PostgreSQL-Datenbank visualisieren.
#          So wird sichtbar, dass die Datenbank nicht nur steht,
#          sondern sich direkt aus Python auswerten lässt.
#
#  Grundidee in einem Satz: Python verbindet sich mit der
#  Datenbank, holt sich mit einer SQL-Abfrage die Daten in eine
#  Tabelle im Arbeitsspeicher, und seaborn malt daraus ein Bild.
#
#  Vorher einmalig im Terminal installieren:
#     pip install sqlalchemy psycopg2-binary seaborn
#
#  Ausgabe:  visualisierungen/*.png
#  Aufruf:   python python/08_visualisierung_seaborn.py
# ============================================================

# --- Die Werkzeuge, die wir brauchen (die "imports") ---
# Mit "import" holen wir uns fertige Bausteine in unser Skript.
# Das "as" gibt ihnen einen kurzen Spitznamen, damit man weniger
# tippen muss.
import os                          # Datei- und Ordnerfunktionen des Systems
import pandas as pd               # Tabellen im Arbeitsspeicher (sog. DataFrames)
import seaborn as sns             # hübsche Diagramme, baut auf matplotlib auf
import matplotlib.pyplot as plt   # die Zeichen-Maschine darunter
from sqlalchemy import create_engine   # baut die Verbindung zur Datenbank


# ------------------------------------------------------------
#  Arbeitsverzeichnis festnageln (wie in den anderen Skripten)
# ------------------------------------------------------------
# Egal von wo aus das Skript gestartet wird, wir setzen den
# Arbeitsordner immer auf den Projektordner. So landen die Bilder
# verlässlich am richtigen Ort.
# __file__ ist der Pfad dieser Datei. Zweimal "dirname" geht zwei
# Ordner nach oben (von python/ in den Projektordner).
projekt_ordner = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(projekt_ordner)

# Den Ausgabeordner anlegen, falls es ihn noch nicht gibt.
# exist_ok=True heißt: meckere nicht, wenn er schon da ist.
os.makedirs("visualisierungen", exist_ok=True)


# ------------------------------------------------------------
#  Verbindung zur Datenbank aufbauen
# ------------------------------------------------------------
# Damit Python mit PostgreSQL reden kann, braucht es eine
# Verbindung. Diese beschreiben wir mit einer Adresse, die alle
# nötigen Angaben enthält: Benutzer, Passwort, Servername und
# Datenbankname.
#
# WICHTIG: Trage hier dein eigenes Passwort ein. Dieses Passwort
# gibst du nicht weiter und es gehört auch nicht in die Doku.
# Falls dein Benutzer nicht "postgres" heißt, hier ebenfalls anpassen.
#
# Neu: Die Werte können über Umgebungsvariablen gesetzt werden. Das
# brauchen wir für Docker, wo die Datenbank nicht unter "localhost",
# sondern unter dem Servicenamen "db" erreichbar ist. Ist keine
# Umgebungsvariable gesetzt, gelten die Standardwerte für den lokalen
# Betrieb. So läuft genau dasselbe Skript lokal und im Container.
DB_HOST     = os.environ.get("DB_HOST", "localhost")
DB_BENUTZER = os.environ.get("DB_USER", "postgres")
DB_PASSWORT = os.environ.get("DB_PASSWORT", "DEIN_PASSWORT_HIER")
DB_NAME     = os.environ.get("DB_NAME", "wohnungsmarkt_db")

# create_engine baut die Verbindung. Das "engine"-Objekt ist wie
# eine Telefonleitung zur Datenbank, die wir später immer wieder
# benutzen. Der Teil "postgresql+psycopg2" sagt, mit welcher Technik
# gesprochen wird. Lokal ist DB_HOST gleich localhost, im Container "db".
verbindung = create_engine(
    f"postgresql+psycopg2://{DB_BENUTZER}:{DB_PASSWORT}@{DB_HOST}:5432/{DB_NAME}"
)


# ------------------------------------------------------------
#  Einheitlicher Stil für alle Diagramme
# ------------------------------------------------------------
# set_theme stellt das Aussehen aller folgenden Diagramme auf einen
# Schlag ein. "whitegrid" gibt einen weißen Hintergrund mit feinen
# Gitterlinien. font_scale macht die Schrift etwas größer.
sns.set_theme(style="whitegrid", font_scale=1.05)

# Unsere zwei Farben als Hex-Codes (so schreibt man Farben am
# Computer). TERRA ist das Terrakotta-Rot der Präsentation,
# SCHIEFER ein ruhiges Blaugrau. So passen die Bilder zum Foliendesign.
TERRA = "#B85042"
SCHIEFER = "#4C6E81"


# ------------------------------------------------------------
#  Ein kleiner Helfer zum Speichern
# ------------------------------------------------------------
# Diese Funktion benutzen wir nach jedem Diagramm. Sie nimmt nur den
# Dateinamen entgegen und kümmert sich um den Rest. So müssen wir
# die Speicher-Schritte nicht sieben Mal wiederholen.
def speichern(dateiname):
    """Legt das aktuelle Diagramm sauber zugeschnitten als PNG ab."""
    pfad = os.path.join("visualisierungen", dateiname)  # Ordner + Dateiname
    plt.tight_layout()              # Ränder automatisch hübsch ausrichten
    plt.savefig(pfad, dpi=150)      # als Bild speichern, dpi = Auflösung
    plt.close()                     # das Diagramm schließen, Speicher freigeben
    print(f"  gespeichert: {pfad}")


# ------------------------------------------------------------
#  Noch ein kleiner Helfer (nur bei Bedarf)
# ------------------------------------------------------------
# Falls eine Abfrage einmal an einem Spaltennamen scheitert, kannst
# du mit dieser Funktion schnell die echten Spaltennamen einer
# Tabelle anzeigen lassen, z.B. zeige_spalten("dim_einkommen").
def zeige_spalten(tabelle):
    df = pd.read_sql(f"SELECT * FROM {tabelle} LIMIT 1", verbindung)
    print(f"  Spalten von {tabelle}: {list(df.columns)}")


# ============================================================
#  H1: Die teuersten Orte über dem Bundesschnitt
# ============================================================
# Idee: Zuerst den bundesweiten Durchschnittspreis berechnen, dann
# je Ort schauen, wie viel Prozent er darüber liegt. Wir zeigen die
# zehn teuersten Orte als waagerechte Balken.
def h1_topstaedte():
    # Die SQL-Abfrage steht zwischen drei Anführungszeichen, damit
    # sie über mehrere Zeilen gehen darf. WITH ... AS (...) ist eine
    # Zwischenrechnung: wir nennen den Bundesschnitt einmal und
    # benutzen ihn dann unten.
    abfrage = """
        WITH bundesschnitt AS (
            SELECT AVG(miete_pro_qm) AS schnitt
            FROM fakt_mietangebote
            WHERE miete_pro_qm IS NOT NULL
        )
        SELECT m.ort,
               ROUND((((AVG(m.miete_pro_qm) /
                       (SELECT schnitt FROM bundesschnitt)) - 1) * 100)::numeric, 1)
                   AS prozent_ueber_schnitt
        FROM fakt_mietangebote AS m
        WHERE m.miete_pro_qm IS NOT NULL
        GROUP BY m.ort
        HAVING COUNT(*) >= 50          -- nur Orte mit mind. 50 Inseraten
        ORDER BY prozent_ueber_schnitt DESC
        LIMIT 10;                      -- nur die Top 10
    """
    # read_sql schickt die Abfrage an die Datenbank und legt das
    # Ergebnis als Tabelle (DataFrame) im Arbeitsspeicher ab.
    df = pd.read_sql(abfrage, verbindung)
    # "Frankfurt_am_Main" -> "Frankfurt am Main", liest sich im Diagramm besser
    df["ort"] = df["ort"].str.replace("_", " ")

    # Eine neue, leere Zeichenfläche in einer bestimmten Größe
    # (Breite, Höhe in Zoll) anlegen.
    plt.figure(figsize=(9, 5.5))

    # barplot zeichnet Balken. data ist unsere Tabelle, x die Länge
    # der Balken, y die Beschriftung. Weil y der Text ist, liegen die
    # Balken waagerecht. color färbt sie einheitlich terrakotta.
    sns.barplot(data=df, x="prozent_ueber_schnitt", y="ort", color=TERRA)

    # Titel und Achsenbeschriftungen. Die y-Achse braucht keinen
    # Titel, weil dort schon die Ortsnamen stehen.
    plt.title("H1: Die teuersten Orte über dem Bundesschnitt", fontweight="bold")
    plt.xlabel("Prozent über dem bundesweiten Schnitt")
    plt.ylabel("")

    speichern("h1_topstaedte.png")


# ============================================================
#  H2: Quadratmeterpreis nach Wohnungsgröße
# ============================================================
# Idee: Die Wohnungen in fünf Größenklassen einteilen und je
# Klasse den Durchschnittspreis zeigen. So wird die U-Form sichtbar.
def h2_wohnungsgroesse():
    # Das CASE im SQL ist wie eine Wenn-dann-Einteilung: jede Wohnung
    # bekommt anhand ihrer Fläche eine Klasse zugewiesen.
    abfrage = """
        SELECT
            CASE
                WHEN wohnflaeche_qm < 40  THEN 'unter 40'
                WHEN wohnflaeche_qm < 60  THEN '40 bis 60'
                WHEN wohnflaeche_qm < 80  THEN '60 bis 80'
                WHEN wohnflaeche_qm < 100 THEN '80 bis 100'
                ELSE '100 und mehr'
            END AS groesse_klasse,
            ROUND(AVG(miete_pro_qm)::numeric, 2) AS miete_pro_qm
        FROM fakt_mietangebote
        WHERE wohnflaeche_qm IS NOT NULL AND miete_pro_qm IS NOT NULL
        GROUP BY groesse_klasse;
    """
    df = pd.read_sql(abfrage, verbindung)

    # Kleiner, aber wichtiger Schritt: Ohne Vorgabe sortiert seaborn
    # die Klassen alphabetisch, dann stünde "100 und mehr" ganz vorn.
    # Mit pd.Categorical legen wir die richtige Reihenfolge fest und
    # sortieren danach.
    reihenfolge = ["unter 40", "40 bis 60", "60 bis 80", "80 bis 100", "100 und mehr"]
    df["groesse_klasse"] = pd.Categorical(df["groesse_klasse"], categories=reihenfolge, ordered=True)
    df = df.sort_values("groesse_klasse")

    plt.figure(figsize=(9, 5.5))
    # Hier sind die Balken senkrecht, weil x der Text ist und y die Zahl.
    sns.barplot(data=df, x="groesse_klasse", y="miete_pro_qm", color=TERRA)
    plt.title("H2: Quadratmeterpreis nach Wohnungsgröße", fontweight="bold")
    plt.xlabel("Wohnfläche in Quadratmetern")
    plt.ylabel("Durchschnittlicher Preis je m² (Euro)")
    speichern("h2_wohnungsgroesse.png")


# ============================================================
#  H3: Ost, West und Berlin im Vergleich
# ============================================================
# Idee: Den Durchschnittspreis je Region zeigen. Die Spalte
# region_ost_west hatten wir schon bei der Aufbereitung gebildet.
def h3_ost_west():
    abfrage = """
        SELECT region_ost_west AS region,
               ROUND(AVG(miete_pro_qm)::numeric, 2) AS miete_pro_qm
        FROM fakt_mietangebote
        WHERE region_ost_west IS NOT NULL AND miete_pro_qm IS NOT NULL
        GROUP BY region_ost_west
        ORDER BY miete_pro_qm;          -- aufsteigend, damit Berlin rechts steht
    """
    df = pd.read_sql(abfrage, verbindung)

    plt.figure(figsize=(8, 5.5))
    # Diesmal in Schiefer-Blau, nur zur Abwechslung und Lesbarkeit.
    sns.barplot(data=df, x="region", y="miete_pro_qm", color=SCHIEFER)
    plt.title("H3: Mietpreis je m² nach Region", fontweight="bold")
    plt.xlabel("")
    plt.ylabel("Durchschnittlicher Preis je m² (Euro)")
    speichern("h3_ost_west.png")


# ============================================================
#  H4: Einkommen gegen Miete je Kreis
# ============================================================
# Idee: Jeder Punkt ist ein Kreis. Waagerecht das Einkommen,
# senkrecht die Durchschnittsmiete. So sieht man den Zusammenhang.
# Die Spalte heißt in deiner Tabelle "einkommen_je_ew", wir nennen
# sie in der Abfrage kurz "einkommen".
def h4_bezahlbarkeit():
    abfrage = """
        SELECT m.kreis_schluessel,
               MAX(e.einkommen_je_ew) AS einkommen,
               AVG(m.miete_pro_qm)    AS miete_pro_qm
        FROM fakt_mietangebote AS m
        JOIN dim_einkommen AS e ON m.kreis_schluessel = e.kreis_schluessel
        WHERE m.miete_pro_qm IS NOT NULL
        GROUP BY m.kreis_schluessel;
    """
    df = pd.read_sql(abfrage, verbindung)

    plt.figure(figsize=(8.5, 5.5))
    # regplot macht zwei Dinge auf einmal: es streut die Punkte und
    # legt eine Trendlinie hinein. Mit den "kws"-Angaben (kurz für
    # keyword arguments) steuern wir das Aussehen getrennt:
    #   scatter_kws  -> die Punkte (alpha = Durchsichtigkeit)
    #   line_kws     -> die Trendlinie
    sns.regplot(data=df, x="einkommen", y="miete_pro_qm",
                scatter_kws={"alpha": 0.5, "color": SCHIEFER},
                line_kws={"color": TERRA})
    plt.title("H4: Einkommen gegen Miete je Kreis", fontweight="bold")
    plt.xlabel("Verfügbares Einkommen je Einwohner (Euro)")
    plt.ylabel("Durchschnittlicher Preis je m² (Euro)")
    speichern("h4_bezahlbarkeit.png")


# ============================================================
#  H5: Wohnungsbestand je 1000 Einwohner über die Zeit
# ============================================================
# Idee: Eine Zeitreihe über die Jahre als Linie. In deiner Tabelle
# heißt das Jahr "stichtag_jahr", wir nennen es kurz "berichtsjahr".
def h5_wohnungsbestand():
    abfrage = """
        SELECT stichtag_jahr AS berichtsjahr, wohnungen_je_1000_ew
        FROM dim_wohnungsbestand
        ORDER BY stichtag_jahr;
    """
    df = pd.read_sql(abfrage, verbindung)

    plt.figure(figsize=(9, 5.5))
    # lineplot zeichnet eine Linie. marker="o" setzt an jeden Jahrespunkt
    # einen kleinen Kreis, linewidth macht die Linie etwas dicker.
    sns.lineplot(data=df, x="berichtsjahr", y="wohnungen_je_1000_ew",
                 marker="o", color=TERRA, linewidth=2.5)
    # Ohne diese Zeile würde die Achse "2020.5" anzeigen. Wir erzwingen
    # genau die echten Jahreszahlen als Beschriftung.
    plt.xticks(df["berichtsjahr"])
    plt.title("H5: Wohnungen je 1000 Einwohner", fontweight="bold")
    plt.xlabel("Jahr")
    plt.ylabel("Wohnungen je 1000 Einwohner")
    speichern("h5_wohnungsbestand.png")


# ============================================================
#  H6: Bevölkerungsdichte gegen Miete je Kreis
# ============================================================
# Idee: Wie H4, nur mit der Dichte statt dem Einkommen. In deiner
# Tabelle heißt die Spalte "dichte_ew_qkm", wir nennen sie "dichte".
def h6_dichte():
    abfrage = """
        SELECT m.kreis_schluessel,
               MAX(d.dichte_ew_qkm) AS dichte,
               AVG(m.miete_pro_qm)  AS miete_pro_qm
        FROM fakt_mietangebote AS m
        JOIN dim_dichte AS d ON m.kreis_schluessel = d.kreis_schluessel
        WHERE m.miete_pro_qm IS NOT NULL
        GROUP BY m.kreis_schluessel;
    """
    df = pd.read_sql(abfrage, verbindung)

    plt.figure(figsize=(8.5, 5.5))
    # Wieder Streupunkte plus Trendlinie. Die breite Streuung der
    # Punkte um die Linie ist hier die eigentliche Aussage: der
    # Zusammenhang ist da, aber nicht stark.
    sns.regplot(data=df, x="dichte", y="miete_pro_qm",
                scatter_kws={"alpha": 0.5, "color": SCHIEFER},
                line_kws={"color": TERRA})
    plt.title("H6: Bevölkerungsdichte gegen Miete je Kreis", fontweight="bold")
    plt.xlabel("Einwohner je Quadratkilometer")
    plt.ylabel("Durchschnittlicher Preis je m² (Euro)")
    speichern("h6_dichte.png")


# ============================================================
#  H7: Baupreise gegen Verbraucherpreise über die Jahre
# ============================================================
# Idee: Zwei Linien im selben Diagramm, damit man sie vergleichen kann.
def h7_baupreise():
    abfrage = """
        SELECT b.berichtsjahr,
               b.baupreisindex,
               v.verbraucherpreisindex
        FROM dim_baupreise AS b
        JOIN dim_verbraucherpreise AS v ON b.berichtsjahr = v.berichtsjahr
        ORDER BY b.berichtsjahr;
    """
    df = pd.read_sql(abfrage, verbindung)

    # Kurzer Zwischenschritt: Umformen vom "breiten" ins "lange" Format.
    # Vorher stehen Baupreise und Verbraucherpreise in zwei Spalten
    # nebeneinander. seaborn zeichnet zwei Linien aber am einfachsten,
    # wenn alle Werte in EINER Spalte stehen und eine zweite Spalte
    # sagt, zu welcher Reihe der Wert gehört. Genau das macht melt:
    #   id_vars    -> die Spalte, die bleibt (das Jahr)
    #   value_vars -> die Spalten, die zusammengefaltet werden
    #   var_name   -> Name der neuen "welche Reihe"-Spalte
    #   value_name -> Name der neuen Werte-Spalte
    lang = df.melt(id_vars="berichtsjahr",
                   value_vars=["baupreisindex", "verbraucherpreisindex"],
                   var_name="reihe", value_name="index")

    # Die technischen Spaltennamen durch lesbare Beschriftungen ersetzen.
    lang["reihe"] = lang["reihe"].map({
        "baupreisindex": "Baupreise",
        "verbraucherpreisindex": "Verbraucherpreise",
    })

    plt.figure(figsize=(9, 5.5))
    # hue="reihe" sagt seaborn: zeichne pro Wert in der Spalte "reihe"
    # eine eigene Linie. Dadurch entstehen die zwei Linien. palette
    # gibt die zwei Farben in der Reihenfolge der Linien.
    sns.lineplot(data=lang, x="berichtsjahr", y="index", hue="reihe",
                 marker="o", linewidth=2.5, palette=[TERRA, SCHIEFER])
    plt.xticks(sorted(lang["berichtsjahr"].unique()))   # nur ganze Jahre
    plt.title("H7: Baupreise gegen Verbraucherpreise (2021 = 100)", fontweight="bold")
    plt.xlabel("Jahr")
    plt.ylabel("Index (2021 = 100)")
    plt.legend(title="")     # die kleine Erklärbox, ohne Überschrift
    speichern("h7_baupreise.png")


# ============================================================
#  Alles der Reihe nach ausführen
# ============================================================
# Diese letzte Zeile bedeutet vereinfacht: "Führe den folgenden
# Block nur aus, wenn diese Datei direkt gestartet wird." Das ist
# eine gute Gewohnheit in Python.
if __name__ == "__main__":
    # Eine Liste von Paaren: Kürzel und die zugehörige Funktion.
    # So können wir sie bequem in einer Schleife abarbeiten.
    aufgaben = [
        ("H1", h1_topstaedte), ("H2", h2_wohnungsgroesse), ("H3", h3_ost_west),
        ("H4", h4_bezahlbarkeit), ("H5", h5_wohnungsbestand), ("H6", h6_dichte),
        ("H7", h7_baupreise),
    ]

    # Jede Visualisierung läuft in ihrem eigenen try-Block. Falls eine
    # einzelne scheitert (z.B. wegen eines falschen Spaltennamens),
    # bricht nicht das ganze Skript ab. Die anderen laufen weiter, und
    # wir bekommen eine klare Meldung, welche Hypothese das Problem hatte.
    for name, funktion in aufgaben:
        try:
            print(f"{name} wird gezeichnet ...")
            funktion()
        except Exception as fehler:
            print(f"  Problem bei {name}: {fehler}")
            print(f"  Tipp: prüfe die Spaltennamen der beteiligten Tabelle.")

    print("\nFertig. Alle Bilder liegen im Ordner 'visualisierungen'.")
