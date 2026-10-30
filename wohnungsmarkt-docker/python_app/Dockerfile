# ============================================================
#  Image für die Python-Umgebung (seaborn-Skripte)
#
#  Baut auf einem schlanken Python 3.12 auf und installiert genau
#  die Pakete, die unsere Skripte brauchen. Dadurch läuft die
#  Auswertung auf jedem Rechner gleich, ohne lokale Installation.
# ============================================================

FROM python:3.12-slim

# Arbeitsordner im Container
WORKDIR /app

# Erst nur die Paketliste kopieren und installieren. So muss Docker
# die Pakete nur neu bauen, wenn sich die Liste ändert (schneller).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Die Skripte selbst werden über ein Volume eingebunden (siehe
# docker-compose.yml), nicht ins Image kopiert. So kannst du sie
# ändern, ohne das Image neu zu bauen.

# Standardbefehl, falls der Container ohne eigenen Befehl gestartet wird.
CMD ["python", "--version"]
