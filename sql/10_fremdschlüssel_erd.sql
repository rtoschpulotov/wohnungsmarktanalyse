-- ============================================================
--  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
--  Datei:  10_fremdschlüssel_erd.sql
--  Autor:  Rustam T. (Data Engineering)
--
--  ZWECK:
--  Bis jetzt waren unsere Tabellen nur logisch über gleiche
--  Spaltennamen verbunden, beim JOIN. In der Datenbank selbst
--  stand aber nirgends offiziell geschrieben, dass eine Spalte
--  zu einer anderen Tabelle gehört. Mit diesem Skript legen wir
--  echte Fremdschlüssel an. Dadurch passieren zwei Dinge:
--    1. pgAdmin kann im ER-Diagramm automatisch Verbindungslinien
--       zeichnen (vorher hatte es nichts zu zeichnen).
--    2. Die Datenbank erzwingt ab jetzt die "referentielle
--       Integrität", dazu unten mehr.
--
--  WICHTIG:
--  Dieses Skript wird nur EINMAL ausgeführt. Sind die Regeln
--  schon angelegt, meldet PostgreSQL beim erneuten Lauf, dass
--  der Constraint bereits existiert. Das ist harmlos, aber dann
--  führst du nur die Zeilen aus, die noch fehlen.
-- ============================================================


-- ------------------------------------------------------------
--  Kurz erklärt: Was ist ein Fremdschlüssel?
-- ------------------------------------------------------------
-- Ein Fremdschlüssel ist eine Regel, die sagt: "Der Wert in
-- dieser Spalte muss auch in jener anderen Tabelle existieren."
-- Beispiel: Jede Wohnung hat einen kreis_schluessel. Der
-- Fremdschlüssel verlangt, dass dieser Kreis auch wirklich in
-- der Einkommens-Tabelle steht. So kann keine Wohnung auf einen
-- Kreis verweisen, den es gar nicht gibt.
--
-- Sprechweise: Die Tabelle mit dem Fremdschlüssel ist das "Kind"
-- (hier die Mieten, die viele Seite), die Zieltabelle ist der
-- "Elternteil" (hier die Dimension, die eine Seite).
--
-- Eine Bedingung muss immer erfüllt sein: Die Zielspalte muss
-- EINDEUTIG sein, also Primärschlüssel oder mit einer Unique-
-- Regel versehen. Sonst wüsste die Datenbank nicht, auf welche
-- Zeile sich der Fremdschlüssel bezieht.


-- ============================================================
--  TEIL 1: Die zwei einfachen Fremdschlüssel (über den Kreis)
-- ============================================================
-- kreis_schluessel ist in dim_einkommen und dim_dichte bereits
-- der Primärschlüssel, also schon eindeutig. Deshalb können
-- wir die Fremdschlüssel hier direkt anlegen, ohne Vorarbeit.
--
-- Aufbau des Befehls Stück für Stück:
--   ALTER TABLE fakt_mietangebote   -> wir ändern die Mieten-Tabelle
--   ADD CONSTRAINT fk_fakt_einkommen-> wir geben der neuen Regel
--                                       einen Namen (frei wählbar,
--                                       fk steht für foreign key)
--   FOREIGN KEY (kreis_schluessel)  -> DIESE Spalte bei uns
--   REFERENCES dim_einkommen (kreis_schluessel) -> zeigt auf JENE
--                                       Spalte in der Zieltabelle

ALTER TABLE fakt_mietangebote
    ADD CONSTRAINT fk_fakt_einkommen
    FOREIGN KEY (kreis_schluessel) REFERENCES dim_einkommen (kreis_schluessel);

ALTER TABLE fakt_mietangebote
    ADD CONSTRAINT fk_fakt_dichte
    FOREIGN KEY (kreis_schluessel) REFERENCES dim_dichte (kreis_schluessel);


-- ============================================================
--  TEIL 2: Der Fremdschlüssel zur Brücke (über den Ort)
-- ============================================================
-- Die Brücke map_ort_kreis verbinden wir über die Spalte "ort".
-- Hier brauchen wir etwas Vorarbeit, weil "ort" dort nicht der
-- Primärschlüssel war und deshalb noch nicht als eindeutig galt.


-- --- Schritt 2a: Prüfen, ob "ort" überhaupt eindeutig ist ---
-- Bevor wir "ort" zur eindeutigen Spalte machen, vergewissern wir
-- uns, dass es keine doppelten Ortsnamen gibt. Diese Abfrage
-- gruppiert nach Ort und zeigt nur die, die mehr als einmal
-- vorkommen. Kommt KEINE Zeile zurück, ist jeder Ort einmalig.
SELECT ort, COUNT(*)
FROM map_ort_kreis
GROUP BY ort
HAVING COUNT(*) > 1;


-- --- Schritt 2b: "ort" zur eindeutigen Spalte machen ---
-- Wir hängen eine Unique-Regel an "ort". Damit verspricht die
-- Tabelle, dass jeder Ortsname nur ein einziges Mal vorkommt.
-- Erst dadurch darf ein Fremdschlüssel auf "ort" zeigen.
--
-- Hinweis aus der Praxis: Wir wollten "ort" zuerst zum zweiten
-- Primärschlüssel machen, das ging aber nicht, weil eine Tabelle
-- nur EINEN Primärschlüssel haben darf (map_ort_kreis hatte
-- schon einen auf kreis_schluessel). Die Unique-Regel ist die
-- richtige Lösung und reicht völlig aus.
ALTER TABLE map_ort_kreis
    ADD CONSTRAINT uq_map_ort_kreis UNIQUE (ort);


-- --- Schritt 2c: Den Fremdschlüssel anlegen ---
-- Jetzt darf jede Wohnung über ihren Ortsnamen fest mit der
-- Brücke verbunden werden.
ALTER TABLE fakt_mietangebote
    ADD CONSTRAINT fk_fakt_ort
    FOREIGN KEY (ort) REFERENCES map_ort_kreis (ort);


-- ============================================================
--  OPTIONAL: Nur zur Information, nicht nötig
-- ============================================================
-- Diese Abfrage zeigt, welche Spalte der bestehende Primär-
-- schlüssel von map_ort_kreis ist. Das half uns zu verstehen,
-- warum ein zweiter Primärschlüssel abgelehnt wurde. Sie
-- verändert nichts, sie schaut nur in die Systemtabellen von
-- PostgreSQL. Du kannst sie laufen lassen oder weglassen.
SELECT a.attname AS spalte
FROM pg_index i
JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
WHERE i.indrelid = 'map_ort_kreis'::regclass AND i.indisprimary;


-- ============================================================
--  WIE ES WEITERGEHT: Das ER-Diagramm neu erzeugen
-- ============================================================
-- Die Verbindungslinien erscheinen NICHT von selbst in einem
-- bereits geöffneten Diagramm. Du musst es einmal frisch erzeugen
-- lassen: Rechtsklick auf die Datenbank wohnungsmarkt_db, dann
-- "Generate ERD". Danach zeigt das Diagramm drei Verbindungen:
-- von fakt_mietangebote zu dim_einkommen, zu dim_dichte und zur
-- Brücke map_ort_kreis.
--
-- Bewusst OHNE Linie bleiben die drei Zeitreihen dim_baupreise,
-- dim_verbraucherpreise und dim_wohnungsbestand. Sie sind nicht
-- über einen Schlüssel an die Mieten gekoppelt, sondern stehen
-- für sich und bedienen direkt ihre Hypothese (H5 und H7). Dass
-- sie unverbunden sind, ist also richtig und ehrlich.
--
-- Schöner Nebeneffekt für die Verteidigung: Durch die Fremd-
-- schlüssel erzwingt die Datenbank nun die referentielle
-- Integrität. Das heißt, es kann gar keine Wohnung mehr geben,
-- die auf einen nicht existierenden Kreis oder Ort verweist. Das
-- ist ein echtes Qualitätsmerkmal der Datenbank.
-- ============================================================