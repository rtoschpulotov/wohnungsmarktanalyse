-- ============================================================
--  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
--  Datei:  11_korrektur_kreiszuordnung.sql
--  Autor:  Rustam T. (Data Engineering)
--  Zweck:  Korrektur 10/2026 für eine schon bestehende Datenbank.
--
--  Was war falsch: 21 kreisfreie Städte waren dem gleichnamigen
--  Landkreis zugeordnet (z.B. München 09184 statt 09162), rund 24.900
--  Inserate. Ursache in python/06_ort_kreis_mapping.py, dort korrigiert.
--  Wer die Datenbank neu aufbaut, braucht dieses Skript nicht.
--
--  Läuft als Transaktion: entweder alles oder nichts.
-- ============================================================

BEGIN;

-- 1. Brücke korrigieren
UPDATE map_ort_kreis AS k
SET    kreis_schluessel = n.kreis_schluessel,
       kreis_name       = n.kreis_name
FROM (VALUES
    ('Ansbach', '09561', 'Ansbach'),
    ('Aschaffenburg', '09661', 'Aschaffenburg'),
    ('Augsburg', '09761', 'Augsburg'),
    ('Bamberg', '09461', 'Bamberg'),
    ('Bayreuth', '09462', 'Bayreuth'),
    ('Coburg', '09463', 'Coburg'),
    ('Fürth', '09563', 'Fürth'),
    ('Heilbronn', '08121', 'Heilbronn, Stadtkreis'),
    ('Hof', '09464', 'Hof'),
    ('Kaiserslautern', '07312', 'Kaiserslautern, kreisfreie Stadt'),
    ('Karlsruhe', '08212', 'Karlsruhe, Stadtkreis'),
    ('Kassel', '06611', 'Kassel, documenta-Stadt'),
    ('Landshut', '09261', 'Landshut'),
    ('Leipzig', '14713', 'Leipzig, Stadt'),
    ('München', '09162', 'München, Landeshauptstadt'),
    ('Osnabrück', '03404', 'Osnabrück, Stadt'),
    ('Passau', '09262', 'Passau'),
    ('Regensburg', '09362', 'Regensburg'),
    ('Rosenheim', '09163', 'Rosenheim'),
    ('Schweinfurt', '09662', 'Schweinfurt'),
    ('Würzburg', '09663', 'Würzburg')
) AS n(ort, kreis_schluessel, kreis_name)
WHERE k.ort = n.ort;

-- 2. Die Wohnungen dieser Orte bekommen den richtigen Kreis
UPDATE fakt_mietangebote AS m
SET    kreis_schluessel = k.kreis_schluessel
FROM   map_ort_kreis AS k
WHERE  m.ort = k.ort
  AND  m.kreis_schluessel IS DISTINCT FROM k.kreis_schluessel;

-- 3. Kontrolle: alle 400 Kreise sollten jetzt Inserate haben
SELECT COUNT(DISTINCT kreis_schluessel) AS kreise_mit_inseraten
FROM fakt_mietangebote;

COMMIT;
