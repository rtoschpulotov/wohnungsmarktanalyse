-- ============================================================
--  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
--  Datei:  04_analyse_h3_ost_west.sql
--  Autor:  Rustam T. (Data Engineering)
--  Thema:  Analyse-Abfrage
-- ============================================================
--
--  HYPOTHESE H3:
--  Es gibt weiterhin Mietunterschiede zwischen Ost und West. 
--  Im Westen sind die Mieten höher als im Osten. 
--  Berlin, Leipzig und Dresden sind eine Ausnahme, 
--  denn obwohl sie im Osten liegen, sind diese Städte sehr teuer.
--
--  ZWECK DIESER ABFRAGE:
--  Der Vergleich der durchschnittlichen Miete pro qm² erfolgt 
--  zwischen den Regionen Ost, West und Berlin. Dafür nutze ich 
--  die Spalte region_ost_west.Diese Spalte habe ich bei der 
--  Datenaufbereitung mit PySpark gebildet.Berlin führte ich dort bewusst 
--  als eigene Kategorie, weil es als Boom-Stadt weder klar Ost noch West ist.

--  Diese Abfrage arbeitet nur mit den Mietdaten, sie braucht
--  keine Verknüpfung.
-- ============================================================

SELECT
    region_ost_west,                                  -- Ost, West oder Berlin
    ROUND(AVG(miete_pro_qm), 2) AS schnitt_miete_qm,  -- Durchschnittsmiete je qm
    COUNT(*) AS anzahl_inserate                       -- Wohnungen je Region

FROM fakt_mietangebote

-- Nach der Region gruppieren, damit pro Region ein Durchschnitt
-- entsteht (ein Wert für Ost, einer für West, einer für Berlin).
GROUP BY region_ost_west

-- Teuerste Region zuerst.
ORDER BY schnitt_miete_qm DESC;


-- ============================================================
--  ZUSATZ: Die Boom-Städte einzeln betrachten
--  Um den zweiten Teil von H3 zu prüfen (Leipzig und Dresden
--  als Ausnahmen im Osten), schauen wir uns diese Städte
--  genau an. So sieht man, ob sie über dem Ost-Schnitt liegen.
-- ============================================================

SELECT
    k.kreis_name,
    ROUND(AVG(m.miete_pro_qm), 2) AS schnitt_miete_qm,
    COUNT(*) AS anzahl_inserate
FROM fakt_mietangebote AS m
-- Join über den Ort, nicht über den Kreisschlüssel (sonst Doppelzählung)
JOIN map_ort_kreis AS k
    ON m.ort = k.ort
-- Wir filtern gezielt auf die drei Boom-Städte. ILIKE sucht
-- unabhängig von Groß- und Kleinschreibung nach dem Namen.
WHERE k.kreis_name ILIKE '%Leipzig%'
   OR k.kreis_name ILIKE '%Dresden%'
   OR k.kreis_name ILIKE '%Berlin%'
GROUP BY k.kreis_schluessel, k.kreis_name
ORDER BY schnitt_miete_qm DESC;