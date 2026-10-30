-- ============================================================
--  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
--  Datei:  08_analyse_h7_baupreise.sql
--  Autor:  Rustam T. (Data Engineering)
--  Thema:  Analyse-Abfrage als Startpunkt für Person B
-- ============================================================
--
--  HYPOTHESE H7:
--  Die Baupreise steigen schneller als die Verbraucherpreise.
--  Das verteuert den Neubau und bremst die Bautätigkeit, was
--  langfristig den Wohnungsmangel verschärft.
--
--  ZEITBASIS DES VERGLEICHS:
--  Beide Reihen laufen über die Jahre 2021 bis 2025 und sind
--  auf das gemeinsame Basisjahr 2021 = 100 gebracht. Nur so
--  ist der Vergleich fair, weil beide vom selben Startpunkt
--  aus messen.
-- ============================================================


-- ============================================================
--  ABFRAGE 1: Die Baupreise allein
--  Zeigt, wie kräftig die Baupreise seit 2021 gestiegen sind.
-- ============================================================
SELECT
    berichtsjahr,                                  -- das Jahr
    baupreisindex,                                 -- der Index (2021 = 100)
    baupreisindex - LAG(baupreisindex) OVER (ORDER BY berichtsjahr)
        AS veraenderung_vorjahr,                   -- Teuerung zum Vorjahr
    ROUND(baupreisindex - 100, 1) AS steigerung_seit_2021_prozent
FROM dim_baupreise
ORDER BY berichtsjahr;


-- ============================================================
--  ABFRAGE 2: Der eigentliche Vergleich (das Herzstück für H7)
--  Stellt Baupreise und Verbraucherpreise Jahr für Jahr
--  nebeneinander. Die letzte Spalte zeigt den Abstand: wie
--  viele Prozentpunkte die Baupreise den Verbraucherpreisen
--  davongelaufen sind.
-- ============================================================
SELECT
    b.berichtsjahr,                                       -- das Jahr
    b.baupreisindex          AS baupreise,                -- Baupreise (2021=100)
    v.verbraucherpreisindex  AS verbraucherpreise,        -- Verbraucherpreise (2021=100)

    -- Steigerung jeder Reihe seit 2021 in Prozent (Index minus 100).
    ROUND(b.baupreisindex - 100, 1)         AS baupreise_seit_2021,
    ROUND(v.verbraucherpreisindex - 100, 1) AS verbraucher_seit_2021,

    -- Der Abstand zwischen beiden in Prozentpunkten. Ein positiver
    -- Wert bedeutet: Bauen ist stärker gestiegen als das normale
    -- Leben. Genau das behauptet H7.
    ROUND(b.baupreisindex - v.verbraucherpreisindex, 1) AS abstand_punkte

FROM dim_baupreise AS b

-- Beide Tabellen über das gemeinsame Jahr verbinden.
JOIN dim_verbraucherpreise AS v
    ON b.berichtsjahr = v.berichtsjahr

ORDER BY b.berichtsjahr;