-- ============================================================
--  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
--  Datei:  05_analyse_h4_bezahlbarkeit.sql
--  Autor:  Rustam T. (Data Engineering)
--  Thema:  Erste Analyse-Abfrage als Startpunkt für die Auswertung im Team
-- ============================================================
--
--  HYPOTHESE H4: Bezahlbarkeit
--  In über der Hälfte der großen Städte sprengt eine
--  70-Quadratmeter-Wohnung die 30-Prozent-Einkommensgrenze.
--  Anders gesagt: Wohnen ist dort teuer im Verhältnis zum
--  Einkommen, die Mietbelastung ist hoch.
--
--  WORUM GEHT ES IN DIESER ABFRAGE:
--  Wir wollen pro Kreis zwei Zahlen nebeneinander sehen:
--   1) die durchschnittliche Miete pro Quadratmeter
--   2) das verfügbare Einkommen je Einwohner in diesem Kreis
--  Erst wenn man beides zusammen sieht, erkennt man, wo Wohnen
--  wirklich belastend ist. Eine hohe Miete in einem reichen
--  Kreis ist weniger schlimm als dieselbe Miete in einem
--  einkommensschwachen Kreis.
--
--  Diese Abfrage nutzt die Verbindung zwischen den Mietdaten
--  und den Einkommensdaten über den Kreisschlüssel. Sie ist
--  damit der erste echte Test, dass das Datenmodell zusammen-
--  spielt, und dient Person B als Ausgangspunkt für H4.
-- ============================================================

SELECT
    e.kreis_name,                                  -- Name des Kreises
    e.bundesland,                                  -- zugehöriges Bundesland
    ROUND(AVG(m.miete_pro_qm), 2) AS schnitt_miete_qm,  -- Durchschnittsmiete je qm
    e.einkommen_je_ew                              -- Einkommen je Einwohner (EUR)

-- Wir starten bei der Mieten-Tabelle (Kurzname: m) ...
FROM fakt_mietangebote AS m

-- ... und verbinden sie mit der Einkommens-Tabelle (Kurzname: e).
-- Die Verbindung läuft über den Kreisschlüssel: Jede Wohnung
-- bekommt so das Einkommen ihres Kreises angehängt.
JOIN dim_einkommen AS e
    ON m.kreis_schluessel = e.kreis_schluessel

-- GROUP BY fasst alle Wohnungen eines Kreises zusammen, damit der
-- Durchschnitt PRO KREIS berechnet wird und nicht über ganz
-- Deutschland. Einkommen und Name gehören mit in die Gruppierung,
-- weil sie je Kreis eindeutig sind.
GROUP BY e.kreis_name, e.bundesland, e.einkommen_je_ew

-- Die teuersten Kreise zuerst (DESC = absteigend) ...
ORDER BY schnitt_miete_qm DESC

-- ... und nur die obersten 25 anzeigen.
LIMIT 25;