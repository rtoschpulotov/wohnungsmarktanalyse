-- ============================================================
--  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
--  Datei:  06_analyse_h5_wohnungsbestand.sql
--  Autor:  Rustam T. (Data Engineering)
--  Thema:  Analyse-Abfrage als Startpunkt für Person B
-- ============================================================
--
--  HYPOTHESE H5: Wohnungsbestand
--  Der Wohnungsbestand wächst langsamer als die Bevölkerung.
--  Dadurch wird Wohnraum pro Kopf knapper, was den Druck auf
--  die Mieten erklärt.
--
--  WORUM GEHT ES IN DIESER ABFRAGE:
--  Wir betrachten die Zeitreihe von 2015 bis 2024. Die Tabelle
--  enthält die fertige Kennzahl "Wohnungen je 1000 Einwohner".
--  Diese Zahl ist der Schlüssel zu H5:
--   - STEIGT sie, gibt es mehr Wohnungen pro Kopf (Bestand
--     wächst schneller als die Bevölkerung).
--   - FÄLLT sie, gibt es weniger Wohnungen pro Kopf (Bevölkerung
--     wächst schneller, dann wäre H5 bestätigt).
--  Zusätzlich berechnen wir die Veränderung gegenüber dem
--  Vorjahr, um die Entwicklung Jahr für Jahr sichtbar zu machen.
--
--  Diese Abfrage arbeitet nur mit der Wohnungsbestand-Tabelle.
-- ============================================================

SELECT
    stichtag_jahr,                                 -- das Jahr
    wohnungen,                                     -- Anzahl Wohnungen gesamt
    wohnungen_je_1000_ew,                          -- die Schlüsselkennzahl für H5

    -- Veränderung der Kennzahl gegenüber dem Vorjahr.
    -- LAG(...) holt den Wert der jeweils vorherigen Zeile (also
    -- das Vorjahr). Wir ziehen ihn vom aktuellen Wert ab und
    -- sehen so, ob die Kennzahl gestiegen oder gefallen ist.
    wohnungen_je_1000_ew - LAG(wohnungen_je_1000_ew) OVER (ORDER BY stichtag_jahr)
        AS veraenderung_vorjahr

FROM dim_wohnungsbestand

-- Chronologisch sortieren, vom ältesten zum neuesten Jahr.
ORDER BY stichtag_jahr;