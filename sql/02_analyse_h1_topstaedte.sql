-- ============================================================
--  Abschlussprojekt: Wohnungsmarkt & Mietpreise in Deutschland
--  Datei:  02_analyse_h1_topstaedte.sql
--  Autor:  Rustam T. (Data Engineering)
--  Thema:  Analyse-Abfrage
-- ============================================================
--
--  HYPOTHESE H1:Die teuersten Städte Deutschland
--  Die teuersten Großstädte (Top-10) liegen 
--  über dem bundesweiten Durchschnitt der Quadratmetermiete.
--
--  ZWeck DIESER ABFRAGE:
--  Um zu prüfen, ob eine Stadt "deutlich teurer" ist, brauchen
--  wir einen Vergleichsmaßstab: den bundesweiten Durchschnitt
--  der Miete pro Quadratmeter. Diesen rechne ich einmal aus
--  und stellen daneben für jeden Kreis, wie weit er prozentual
--  darüber oder darunter liegt. So sieht man auf einen Blick,
--  welche Städte wie stark über dem Schnitt liegen.
--
--  Diese Abfrage arbeitet nur mit den Mietdaten, sie braucht
--  keine Verknüpfung. Den Ortsnamen nehmen wir aus der
--  Zuordnungstabelle, damit ein sauberer Kreisname erscheint.
-- ============================================================

-- Ein "WITH"-Block berechnet vorab eine Hilfszahl:
-- den bundesweiten Durchschnitt der Miete pro qm² über
-- ALLE Inserate. Man kann sich das wie eine Zwischenrechnung
-- vorstellen, die wir gleich weiterverwenden.
WITH bundesschnitt AS (
    SELECT AVG(miete_pro_qm) AS schnitt_de
    FROM fakt_mietangebote
)

SELECT
    k.kreis_name,                                       -- Name des Kreises/der Stadt
    ROUND(AVG(m.miete_pro_qm), 2) AS schnitt_miete_qm,  -- Durchschnittsmiete je qm im Kreis
    -- Abweichung vom Bundesschnitt in Prozent:
    -- (Kreis-Schnitt geteilt durch Bundesschnitt minus 1) mal 100.
    ROUND(
        (AVG(m.miete_pro_qm) / (SELECT schnitt_de FROM bundesschnitt) - 1) * 100,
        1
    ) AS prozent_ueber_schnitt,
    COUNT(*) AS anzahl_inserate                         -- aus wie vielen Wohnungen der Schnitt besteht
FROM fakt_mietangebote AS m

-- Den Klarnamen des Kreises holen wir aus der Zuordnungstabelle.
-- Verbunden wird über den Ort: In map_ort_kreis gibt es pro Ort genau
-- eine Zeile, pro Kreis aber manchmal mehrere. Ein Join über den
-- Kreisschlüssel hätte Wohnungen doppelt gezählt (Korrektur 10/2026).
JOIN map_ort_kreis AS k
    ON m.ort = k.ort

-- Pro Kreis zusammenfassen. Der Schlüssel muss mit rein, weil z.B.
-- "Augsburg" als Stadt und als Landkreis gleich heißt.
GROUP BY k.kreis_schluessel, k.kreis_name

-- Nur Kreise mit genug Inseraten, damit der Schnitt belastbar ist
-- (mindestens 50 Wohnungen). HAVING filtert NACH dem Gruppieren.
HAVING COUNT(*) >= 50

-- Teuerste zuerst.
ORDER BY schnitt_miete_qm DESC

-- Die Top 10 anzeigen.
LIMIT 10;