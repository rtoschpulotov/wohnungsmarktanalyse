-- ============================================================
--  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
--  Datei:  01b_kreisschluessel_verknuepfen.sql
--  Autor:  Rustam T. (Data Engineering)
--  Zweck:  Jeder Wohnung ihren Kreisschlüssel geben, damit die
--          Mieten mit Einkommen und Dichte verbunden werden können.
--  Wann:   nach 01_tabellen_anlegen.sql und dem Import aller CSVs,
--          vor den Analysen und vor 10_fremdschlüssel_erd.sql
--
--  Diesen Schritt hatte ich damals direkt im Query Tool gemacht und
--  nicht als Datei gespeichert. Bei der Überarbeitung (10/2026) neu
--  aufgeschrieben, damit sich das Projekt nachbauen lässt.
-- ============================================================

-- neue Spalte in der Faktentabelle
ALTER TABLE fakt_mietangebote
    ADD COLUMN IF NOT EXISTS kreis_schluessel VARCHAR(5);

-- für jede Wohnung in der Brücke nachschlagen, zu welchem Kreis ihr Ort gehört
UPDATE fakt_mietangebote AS m
SET    kreis_schluessel = k.kreis_schluessel
FROM   map_ort_kreis AS k
WHERE  m.ort = k.ort;

-- Kontrolle: muss 0 ergeben, sonst fehlt ein Ort in der Brücke
SELECT COUNT(*) AS ohne_kreis
FROM fakt_mietangebote
WHERE kreis_schluessel IS NULL;
