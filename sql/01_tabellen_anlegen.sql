-- ============================================================
--  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
--  Datei:  01_tabellen_anlegen.sql
--  Autor:  Rustam T. (Data Engineering)
--  Zweck:  Das Tabellenmodell (Sternschema) für die Analyse
--          anlegen. Eine Faktentabelle (Mieten), fünf Dimensions-
--          tabellen (Einkommen, Dichte, Bestand, Baupreise,
--          Verbraucherpreise) und die Brücke map_ort_kreis.
--  Danach: CSVs importieren, dann 01b_kreisschluessel_verknuepfen.sql
--  Ausführen in: pgAdmin, Query Tool auf Datenbank wohnungsmarkt_db
-- ============================================================


-- ------------------------------------------------------------
--  DIMENSIONSTABELLE 1: Einkommen je Kreis
--  Quelle: einkommen_kreise_clean.csv (400 Kreise)
--  Dient für: Hypothese H4 (Mietbelastung)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS dim_einkommen;
CREATE TABLE dim_einkommen (
    kreis_schluessel  VARCHAR(5) PRIMARY KEY,   -- 5-stelliger Kreisschlüssel
    kreis_name        VARCHAR(100),
    bundesland        VARCHAR(40),
    einkommen_je_ew   INTEGER,                  -- verfügbares Einkommen in EUR
    berichtsjahr      SMALLINT
);


-- ------------------------------------------------------------
--  DIMENSIONSTABELLE 2: Bevölkerungsdichte je Kreis
--  Quelle: dichte_kreise_clean.csv (400 Kreise)
--  Dient für: Hypothese H6 (Dichte erklärt Mietpreise)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS dim_dichte;
CREATE TABLE dim_dichte (
    kreis_schluessel  VARCHAR(5) PRIMARY KEY,
    kreis_name        VARCHAR(100),
    flaeche_qkm       NUMERIC(10,2),            -- Fläche in Quadratkilometern
    bevoelkerung      INTEGER,
    dichte_ew_qkm     INTEGER                   -- Einwohner je Quadratkilometer
);


-- ------------------------------------------------------------
--  DIMENSIONSTABELLE 3: Wohnungsbestand (Deutschland, Zeitreihe)
--  Quelle: wohnungsbestand_clean.csv (10 Jahre)
--  Dient für: Hypothese H5 (wächst der Bestand mit)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS dim_wohnungsbestand;
CREATE TABLE dim_wohnungsbestand (
    stichtag_jahr         SMALLINT PRIMARY KEY,
    wohnungen             INTEGER,
    wohnungen_je_1000_ew  SMALLINT,
    wohnflaeche_je_ew     NUMERIC(5,1)          -- qm je Einwohner
);


-- ------------------------------------------------------------
--  DIMENSIONSTABELLE 4: Baupreise (Deutschland, Zeitreihe)
--  Quelle: baupreise_clean.csv (5 Jahre)
--  Dient für: Hypothese H7 (Baupreise steigen schnell)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS dim_baupreise;
CREATE TABLE dim_baupreise (
    berichtsjahr   SMALLINT PRIMARY KEY,
    baupreisindex  NUMERIC(6,1)                 -- Index, Basisjahr 2021 = 100
);

-- ------------------------------------------------------------
--  BRÜCKENTABELLE: Ort -> Kreis
--  Quelle: ort_kreis_mapping.csv (419 Orte), erzeugt mit
--          python/06_ort_kreis_mapping.py
--  Dient für: Verknüpfung der Mieten mit Einkommen und Dichte
-- ------------------------------------------------------------

DROP TABLE IF EXISTS map_ort_kreis;
CREATE TABLE map_ort_kreis (
    ort               VARCHAR(120) PRIMARY KEY,   -- Ortsname wie in den Mietdaten
    kreis_schluessel  VARCHAR(5),                 -- zugehöriger Kreisschlüssel
    kreis_name        VARCHAR(100)                -- Klarname des Kreises
);



-- ------------------------------------------------------------
--  FAKTENTABELLE: Mietangebote (das Herzstück)
--  Quelle: mietangebote_clean.csv (268.176 Inserate)
--  Dient für: Hypothesen H1, H2, H3 (und Basis für H4, H6)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS fakt_mietangebote;
CREATE TABLE fakt_mietangebote (
    angebot_id        BIGINT PRIMARY KEY,
    bundesland        VARCHAR(40),
    plz               VARCHAR(5),
    ort               VARCHAR(120),
    kaltmiete         NUMERIC(10,2),
    nebenkosten       NUMERIC(10,2),
    wohnflaeche_qm    NUMERIC(7,2),
    miete_pro_qm      NUMERIC(7,2),
    zimmer            NUMERIC(5,1),
    baujahr           NUMERIC(6,1),
    zustand           VARCHAR(40),
    balkon            BOOLEAN,
    einbaukueche      BOOLEAN,
    aufzug            BOOLEAN,
    scrape_datum      VARCHAR(10),
    region_ost_west   VARCHAR(10)
);

-- ------------------------------------------------------------
--  DIMENSIONSTABELLE 5: Verbraucherpreise (Deutschland, Zeitreihe)
--  Quelle: verbraucherpreise_clean.csv (5 Jahre, 2021 = 100)
--  Dient für: Hypothese H7 (Vergleichsreihe zu den Baupreisen)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS dim_verbraucherpreise;
CREATE TABLE dim_verbraucherpreise (
    berichtsjahr           SMALLINT PRIMARY KEY,
    verbraucherpreisindex  NUMERIC(6,1)
);

-- ------------------------------------------------------------
--  Kontrolle: zeigt alle angelegten Tabellen
-- ------------------------------------------------------------
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;