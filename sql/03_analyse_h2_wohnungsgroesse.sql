-- ============================================================
--  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
--  Datei:  03_analyse_h2_wohnungsgroesse.sql
--  Autor:  Rustam T. (Data Engineering)
--  Thema:  Analyse-Abfrage 
-- ============================================================
--
--  HYPOTHESE H2:
--  Für kleine Wohnungen zahlt man mehr pro qm²
--  als für größere Wohnungen.

--
--  WORUM GEHT ES IN DIESER ABFRAGE:
--  Wir teilen alle Wohnungen in Größenklassen ein (z.B. bis
--  40 qm, 40 bis 60 qm usw.) und berechnen für jede Klasse die
--  durchschnittliche Miete pro qm². Wenn die Hypothese
--  stimmt, sinkt der Quadratmeterpreis mit steigender Größe:
--  kleine Klassen oben teuer, große Klassen unten günstiger.

--  Die Abfrage braucht nur die Mietdaten, eine Verknüpfung
--  mit anderen Tabellen ist nicht nötig.
-- ============================================================

SELECT
    -- Mit CASE ordnen wir Wohnflächen in unterschiedliche Größenklassen ein.
    -- Eine Wenn-Dann-Einteilung wird bei CASE angewendet.
    -- Die Wohnung bekommt das passende Etikett je nach Fläche.
    CASE
        WHEN wohnflaeche_qm < 40  THEN '1: unter 40 qm'
        WHEN wohnflaeche_qm < 60  THEN '2: 40 bis 60 qm'
        WHEN wohnflaeche_qm < 80  THEN '3: 60 bis 80 qm'
        WHEN wohnflaeche_qm < 100 THEN '4: 80 bis 100 qm'
        ELSE                           '5: 100 qm und mehr'
    END AS groessenklasse,

    ROUND(AVG(miete_pro_qm), 2) AS schnitt_miete_qm,  -- Durchschnitt je Klasse
    COUNT(*) AS anzahl_inserate                       -- Wohnungen in der Klasse

FROM fakt_mietangebote

--    Die Gruppierung nach Größenklasse dient dazu, einen Durchschnitt 
--    pro Klasse zu ermitteln. Wir wiederholen die CASE-Einteilung,
--    da GROUP BY den fertigen Spaltennamen noch nicht kennt.
GROUP BY
    CASE
        WHEN wohnflaeche_qm < 40  THEN '1: unter 40 qm'
        WHEN wohnflaeche_qm < 60  THEN '2: 40 bis 60 qm'
        WHEN wohnflaeche_qm < 80  THEN '3: 60 bis 80 qm'
        WHEN wohnflaeche_qm < 100 THEN '4: 80 bis 100 qm'
        ELSE                           '5: 100 qm und mehr'
    END

-- Nach der Klasse sortieren (die Ziffer am Anfang sorgt für die
-- richtige Reihenfolge von klein nach groß).
ORDER BY groessenklasse;