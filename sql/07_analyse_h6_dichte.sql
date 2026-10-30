-- ============================================================
--  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
--  Datei:  07_analyse_h6_dichte.sql
--  Autor:  Rustam T. (Data Engineering)
--  Thema:  Analyse-Abfrage als Startpunkt für Person B
-- ============================================================
--
--  HYPOTHESE H6:
--  Die Bevölkerungsdichte erklärt einen Großteil der
--  Preisunterschiede zwischen den Kreisen. Anders gesagt:
--  Je dichter ein Kreis besiedelt ist, desto teurer ist
--  tendenziell die Miete pro Quadratmeter, weil Wohnraum
--  dort knapper ist.
--
--  WORUM GEHT ES IN DIESER ABFRAGE:
--  Wir wollen pro Kreis drei Zahlen nebeneinander sehen:
--   1) die Bevölkerungsdichte (Einwohner je Quadratkilometer)
--   2) die durchschnittliche Miete pro Quadratmeter
--   3) die Anzahl der Inserate, aus denen der Schnitt entsteht
--  So lässt sich erkennen, ob dicht besiedelte Kreise wirklich
--  teurer sind. Die Anzahl der Inserate zeigt dabei, wie
--  belastbar der Durchschnitt je Kreis ist (ein Schnitt aus
--  vielen Wohnungen ist verlässlicher als einer aus wenigen).
--
--  Diese Abfrage nutzt die Verbindung zwischen den Mietdaten
--  und den Dichtedaten über den Kreisschlüssel. Sie dient
--  Person B als Ausgangspunkt für H6.
-- ============================================================
 
SELECT
    d.kreis_name,                                  -- Name des Kreises
    d.dichte_ew_qkm,                               -- Einwohner je Quadratkilometer
    ROUND(AVG(m.miete_pro_qm), 2) AS schnitt_miete_qm,  -- Durchschnittsmiete je qm
    COUNT(*) AS anzahl_inserate                    -- Anzahl Wohnungen im Schnitt
 
-- Wir starten bei der Mieten-Tabelle (Kurzname: m) ...
FROM fakt_mietangebote AS m
 
-- ... und verbinden sie mit der Dichte-Tabelle (Kurzname: d).
-- Die Verbindung läuft über den Kreisschlüssel: Jede Wohnung
-- bekommt so die Bevölkerungsdichte ihres Kreises angehängt.
JOIN dim_dichte AS d
    ON m.kreis_schluessel = d.kreis_schluessel
 
-- GROUP BY fasst alle Wohnungen eines Kreises zusammen, damit
-- der Durchschnitt PRO KREIS berechnet wird und nicht über ganz
-- Deutschland. Name und Dichte gehören mit in die Gruppierung,
-- weil sie je Kreis eindeutig sind.
GROUP BY d.kreis_name, d.dichte_ew_qkm
 
-- Die am dichtesten besiedelten Kreise zuerst (DESC = absteigend) ...
ORDER BY d.dichte_ew_qkm DESC
 
-- ... und nur die obersten 15 anzeigen.
LIMIT 15;