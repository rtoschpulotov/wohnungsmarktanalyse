-- ============================================================
--  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
--  Datei:  09_kontrollabfrage_für_alle_tabellen.sql
--  Autor:  Rustam T. (Data Engineering)
--  Zweck: Wir wollen alle sechs Tabellen auf einen Blick sehen
-- ============================================================

--  Die Idee:
--  Wir wollen für alle sechs Tabellen auf einen Blick sehen, 
--  wie viele Zeilen drin sind.
--  Normalerweise müsste man sechs einzelne COUNT-Abfragen machen. 
--  Wir bauen sie stattdessen mit UNION ALL zu einer einzigen 
--  zusammen,sodass eine schöne Übersichtstabelle herauskommt.
-- ============================================================




SELECT 'fakt_mietangebote'    AS tabelle, COUNT(*) AS zeilen FROM fakt_mietangebote
UNION ALL       -- stapelt die Ergebnisse mehrerer Abfragen untereinander zu einer Liste
SELECT 'dim_einkommen',          COUNT(*) FROM dim_einkommen
UNION ALL
SELECT 'dim_dichte',             COUNT(*) FROM dim_dichte
UNION ALL
SELECT 'map_ort_kreis',             COUNT(*) FROM map_ort_kreis
UNION ALL
SELECT 'dim_wohnungsbestand',    COUNT(*) FROM dim_wohnungsbestand
UNION ALL
SELECT 'dim_baupreise',          COUNT(*) FROM dim_baupreise
UNION ALL
SELECT 'dim_verbraucherpreise',  COUNT(*) FROM dim_verbraucherpreise
ORDER BY tabelle;

SELECT COUNT(*) FROM fakt_mietangebote WHERE kreis_schluessel IS NULL;

SELECT scrape_datum, COUNT(*) AS anzahl
FROM fakt_mietangebote
GROUP BY scrape_datum
ORDER BY scrape_datum;


SELECT table_name, column_name
FROM information_schema.columns
WHERE table_name IN ('dim_einkommen', 'dim_dichte', 'dim_wohnungsbestand')
ORDER BY table_name, ordinal_position;

SELECT
    (SELECT COUNT(*) FROM fakt_mietangebote f
     LEFT JOIN dim_einkommen e ON f.kreis_schluessel = e.kreis_schluessel
     WHERE e.kreis_schluessel IS NULL) AS fehlt_in_einkommen,
    (SELECT COUNT(*) FROM fakt_mietangebote f
     LEFT JOIN dim_dichte d ON f.kreis_schluessel = d.kreis_schluessel
     WHERE d.kreis_schluessel IS NULL) AS fehlt_in_dichte;

	 