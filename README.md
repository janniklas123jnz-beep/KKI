# KKI - Künstliche Kollektive Intelligenz

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Lizenz](https://img.shields.io/badge/Lizenz-MIT-green)
![Status](https://img.shields.io/badge/Status-Experimentell-orange)

Ein Python-Projekt zur Frage, wie **Kooperation, Vertrauen und kollektive Intelligenz** in Multi-Agenten-Systemen emergieren können.

## Auf einen Blick

- Python-Simulationen zu Kooperation, Schwarmverhalten und Manipulationsresistenz
- klare Leitthese: **Intelligenz = f(Kooperation)**
- direkt ausführbare Experimente mit Visualisierungen und Beispielgrafiken

Die Leitidee des Repositories lautet:

> **Intelligenz = f(Kooperation)**

Agenten, die kooperieren, gewinnen langfristig an Anpassungsfähigkeit und Systemleistung. Agenten, die defektieren oder manipulieren, erzielen kurzfristige Vorteile, verlieren aber strukturell an Intelligenz, Reputation oder Anschluss an den Schwarm.

## Projektidee

KKI untersucht eine einfache, aber starke Hypothese:

- Kooperation ist nicht nur moralisch wünschenswert, sondern **architektonisch vorteilhaft**
- Defektion erzeugt keine nachhaltige Überlegenheit, sondern **langfristige Entkopplung**
- Moral kann als **emergente Systemeigenschaft** statt als externe Regel modelliert werden

Die Simulationen basieren auf wiederholten Interaktionen im Stil des Gefangenendilemmas und erweitern dieses Grundmodell schrittweise um Schwarmdynamik, Reputation, Netzwerkstrukturen und kryptografische Verifikation.

## Inhalte des Repositories

| Datei | Zweck |
| --- | --- |
| `kooperation_test.py` | Minimaler Proof of Concept mit zwei Agenten |
| `kooperation_visual.py` | Visualisierte Zwei-Agenten-Simulation mit Graph-Ausgabe |
| `schwarm_simulation.py` | Zentrale Schwarm-Simulation mit mehreren Agenten und Defektoren |
| `schwarm_100.py` | Skalierung auf 100 Agenten |
| `schwarm_cluster.py` | Simulation mit Cluster- und Netzwerkdynamik |
| `schwarm_invasion.py` | Resilienz-Test gegen spätere Invasion durch Defektoren |
| `commitment_protokoll.py` | Commit-Reveal-Verify-Protokoll gegen Manipulation |

## Features

- iterierte Multi-Agenten-Simulationen in Python
- Lernregeln für Kooperation, Defektion und Intelligenzentwicklung
- Visualisierung mit `matplotlib`
- Experimente mit Schwarmverhalten, Reputation und Netzwerkstrukturen
- kryptografische Absicherung von Verhaltenszusagen über Commitments

## Voraussetzungen

- Python 3.10 oder neuer
- `pip`
- optional: eine grafische Umgebung für `matplotlib`, wenn Diagramme direkt angezeigt werden sollen

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Schnellstart

Kleinstes Beispiel:

```bash
python3 kooperation_test.py
```

Visualisierte Variante:

```bash
python3 kooperation_visual.py
```

Zentrales Schwarm-Experiment:

```bash
python3 schwarm_simulation.py
```

Weitere Experimente:

```bash
python3 schwarm_100.py
python3 schwarm_cluster.py
python3 schwarm_invasion.py
python3 commitment_protokoll.py
```

Die Visualisierungs-Skripte erzeugen PNG-Dateien direkt im Projektverzeichnis.
Da die Simulationen Zufallselemente enthalten, können konkrete Zahlenwerte zwischen einzelnen Läufen variieren.

## Beispiel-Visualisierungen

### Zwei Agenten: Emergenz von Kooperation

![KKI Kooperationsgraph](kki_kooperation_graph.png)

### Schwarm-Simulation

![KKI Schwarm-Simulation](kki_schwarm_simulation.png)

## Zentrale Beobachtungen

Die bisherigen Simulationen illustrieren wiederkehrende Muster:

- kooperative Agenten stabilisieren und steigern ihre Intelligenz häufiger
- Defektoren verlieren auf Dauer Anschluss an die leistungsfähigen Teile des Systems
- Schwarmstrukturen können Kooperation auch gegen Störungen oder Invasionsversuche absichern
- Commitment-Mechanismen erschweren oder verhindern strategische Täuschung

## Projektstruktur und Ausrichtung

Das Repository ist experimentell aufgebaut: von einem kleinen Zwei-Agenten-Modell bis hin zu größeren Simulationen mit 50 bis 100 Agenten. Dadurch eignet es sich sowohl für konzeptionelle Demonstrationen als auch für die schrittweise Weiterentwicklung der zugrunde liegenden Theorie.

Die Dateien `kki_*.png` dokumentieren Beispielausgaben der Simulationen. Zusätzlich enthält das Repository mit `sektion_viii_empirische_validierung.docx` begleitendes Arbeitsmaterial zur theoretischen Einbettung.

## Lizenz

Dieses Projekt steht unter der `MIT License`. Details findest du in der Datei [`LICENSE`](LICENSE).

## Autor

Jan Niklas ([@janniklas123jnz-beep](https://github.com/janniklas123jnz-beep))
