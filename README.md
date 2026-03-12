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
| `schwarm_polarisierung.py` | Experiment zu Polarisierung, Konsensbildung und Lagerdynamik |
| `schwarm_parameterstudie.py` | Vergleichsstudie zu Netzwerkparametern gegen Polarisierung |
| `schwarm_adaptive_netzwerke.py` | Vergleichsstudie zu adaptivem Rewiring auf Basis von Reputation und Meinungsnähe |
| `schwarm_invasive_netzwerke.py` | Vergleichsstudie zu adaptiven Netzwerken unter Invasions- und Stoerungsszenarien |
| `schwarm_commitment_resilienz.py` | Vergleichsstudie zu adaptiven Netzwerken unter Manipulations- und Commitment-Angriffen |
| `schwarm_vertrauens_benchmark.py` | Benchmark fuer Vertrauensstrategien wie Reputation, Commitment, Meinung und hybride Mischungen |
| `schwarm_grossstudie.py` | Kombinierte Grossstudie ueber Polarisierung, Invasion und Commitment-Angriffe auf gemeinsamer Agenten-Grund-DNA |
| `schwarm_anti_polarisierung.py` | Vergleichsstudie fuer Brueckenagenten, Mittelzonen-Moderation und hybride Anti-Polarisierungsstrategien |
| `schwarm_gekoppelte_abwehr.py` | Architekturvergleich fuer gekoppelte Anti-Polarisierungs-, Invasions- und Commitment-Abwehr |
| `schwarm_rollenspezialisierung.py` | Rollenstudie fuer gemeinsame Agenten-DNA mit Brueckenbauern, Waechtern und Rollenmix |
| `schwarm_rollenlernen.py` | Verfeinerte Lernprofilstudie fuer Vermittler, Analytiker und adaptive Rollenprofile |
| `schwarm_rollenwechsel.py` | Studie fuer dynamische Rollenwechsel und adaptive Aufgabenverteilung im Schwarm |
| `schwarm_missionsziele.py` | Studie fuer explizite Teamaufgaben wie Konsensbildung, Wissensaustausch und Abwehr |
| `schwarm_missionskonflikte.py` | Studie fuer Arbitration und Zielkonflikte zwischen konkurrierenden Missionen |
| `schwarm_arbeitsketten.py` | Studie fuer mehrstufige Teamaufgaben und Aufgabenabhaengigkeiten im Schwarm |
| `schwarm_arbeitszellen.py` | Studie fuer spezialisierte Workflow-Zellen und Uebergabemechanismen im Schwarm |
| `schwarm_arbeitszellen_parallel.py` | Studie fuer parallele Workflow-Zellen und koordinierte Ressourcenteilung im Schwarm |
| `schwarm_faehigkeitscluster.py` | Studie fuer heterogene Faehigkeitscluster und asymmetrische Ressourcenbudgets im Schwarm |
| `schwarm_engpassmanagement.py` | Studie fuer Bottleneck-Management und prioritaetsbasierte Ressourcen-Umlenkung zwischen Zellclustern |
| `schwarm_meta_koordination.py` | Studie fuer hierarchische Meta-Koordination zwischen Zellclustern und Missionslagen |
| `commitment_protokoll.py` | Commit-Reveal-Verify-Protokoll gegen Manipulation |

## Features

- iterierte Multi-Agenten-Simulationen in Python
- Lernregeln für Kooperation, Defektion und Intelligenzentwicklung
- Visualisierung mit `matplotlib`
- Experimente mit Schwarmverhalten, Reputation und Netzwerkstrukturen
- adaptive Netzwerkumbauten durch Rewiring auf Basis von Reputation und Meinungsnähe
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

## Reproduzierbare Seeds

Alle Simulationsskripte unterstützen reproduzierbare Zufallszahlen über die Umgebungsvariable `KKI_SEED`.

```bash
KKI_SEED=42 python3 schwarm_simulation.py
KKI_SEED=42 python3 commitment_protokoll.py
```

Ohne gesetzte Variable verwenden die Skripte standardmäßig den Seed `42` und geben den aktiven Seed beim Start aus.

Für reproduzierbare PNG-Ausgaben kann zusätzlich ein separates Zielverzeichnis gesetzt werden:

```bash
KKI_SEED=42 KKI_OUTPUT_DIR=artefakte python3 schwarm_simulation.py
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
python3 schwarm_polarisierung.py
python3 schwarm_parameterstudie.py
python3 schwarm_adaptive_netzwerke.py
python3 schwarm_invasive_netzwerke.py
python3 schwarm_commitment_resilienz.py
python3 schwarm_vertrauens_benchmark.py
python3 schwarm_grossstudie.py
python3 schwarm_anti_polarisierung.py
python3 schwarm_gekoppelte_abwehr.py
python3 schwarm_rollenspezialisierung.py
python3 schwarm_rollenlernen.py
python3 schwarm_rollenwechsel.py
python3 schwarm_missionsziele.py
python3 schwarm_missionskonflikte.py
python3 schwarm_arbeitsketten.py
python3 schwarm_arbeitszellen.py
python3 schwarm_arbeitszellen_parallel.py
python3 schwarm_faehigkeitscluster.py
python3 schwarm_engpassmanagement.py
python3 schwarm_meta_koordination.py
python3 commitment_protokoll.py
```

Für das neue Polarisierungs-Experiment kann das Szenario zusätzlich per Umgebungsvariable gewählt werden:

```bash
KKI_POLARIZATION_SCENARIO=polarization python3 schwarm_polarisierung.py
KKI_POLARIZATION_SCENARIO=consensus python3 schwarm_polarisierung.py
```

Für die Netzwerk-Parameterstudie kann zusätzlich ein Grid über Umgebungsvariablen gesetzt werden:

```bash
KKI_STUDY_DEGREES=4,6,8 KKI_STUDY_CROSS_GROUPS=0.05,0.15,0.25 python3 schwarm_parameterstudie.py
```

Für adaptive Netzwerke kann Rewiring im Polarisierungsmodell direkt aktiviert werden:

```bash
KKI_REWIRING_ENABLED=true \
KKI_REWIRE_REP_THRESHOLD=0.30 \
KKI_REWIRE_PROXIMITY_WEIGHT=0.35 \
python3 schwarm_polarisierung.py
```

Die neue Adaptive-Netzwerk-Studie vergleicht mehrere Rewiring-Konfigurationen gegen ein statisches Basisnetz:

```bash
python3 schwarm_adaptive_netzwerke.py
```

Optional kann das Rewiring-Grid angepasst werden:

```bash
KKI_ADAPTIVE_REP_THRESHOLDS=0.25,0.35,0.45 \
KKI_ADAPTIVE_PROXIMITY_WEIGHTS=0.25,0.45,0.65 \
python3 schwarm_adaptive_netzwerke.py
```

Fuer adaptive Netzwerke unter Invasionsbedingungen gibt es eine eigene Vergleichsstudie:

```bash
python3 schwarm_invasive_netzwerke.py
```

Optional lassen sich Invasionsdruck und adaptive Parameter anpassen:

```bash
KKI_INVASION_AGENT_COUNT=12 \
KKI_INVASION_REP_THRESHOLDS=0.25,0.35,0.45 \
KKI_INVASION_PROXIMITY_WEIGHTS=0.25,0.45,0.65 \
python3 schwarm_invasive_netzwerke.py
```

Fuer adaptive Netzwerke unter Commitment-Angriffen gibt es eine eigene Vergleichsstudie:

```bash
python3 schwarm_commitment_resilienz.py
```

Optional lassen sich Angriffsstaerke und Commitment-Schwellen anpassen:

```bash
KKI_COMMITMENT_ATTACK_STRENGTH=0.45 \
KKI_COMMITMENT_REP_THRESHOLDS=0.25,0.35,0.45 \
KKI_COMMITMENT_TRUST_THRESHOLDS=0.55,0.75,0.95 \
python3 schwarm_commitment_resilienz.py
```

Der neue Vertrauens-Benchmark vergleicht mehrere adaptive Strategien direkt gegeneinander:

```bash
python3 schwarm_vertrauens_benchmark.py
```

Die kombinierte Grossstudie fuehrt Polarisierung, Invasion und Commitment-Angriffe unter einer gemeinsamen Agenten-Grundkonfiguration zusammen:

```bash
python3 schwarm_grossstudie.py
```

Die neue Anti-Polarisierungsstudie vergleicht Baseline, Brueckenagenten, Mittelzonen-Moderation und einen hybriden Ansatz direkt miteinander:

```bash
python3 schwarm_anti_polarisierung.py
```

Optional lassen sich Wiederholungen und Kernparameter fuer schnelle Reproduktionen anpassen:

```bash
KKI_ANTI_POL_REPETITIONS=2 \
KKI_ANTI_POL_AGENT_COUNT=60 \
KKI_NETWORK_DEGREE=6 \
python3 schwarm_anti_polarisierung.py
```

Die gekoppelte Abwehrstudie vergleicht, ob die neue Anti-Polarisierung auch als Teil einer uebergreifenden Resilienzarchitektur neben Invasions- und Commitment-Abwehr traegt:

```bash
python3 schwarm_gekoppelte_abwehr.py
```

Die Rollenspezialisierungsstudie prueft den naechsten Schritt zur Bauphase: gemeinsame Agenten-Grund-DNA, aber unterschiedliche Funktionsrollen im Schwarm:

```bash
python3 schwarm_rollenspezialisierung.py
```

Optional lassen sich Wiederholungen und Rollenanteile anpassen:

```bash
KKI_ROLLENSPEZ_REPETITIONS=2 \
KKI_GENERALIST_SHARE=0.55 \
KKI_CONNECTOR_SHARE=0.25 \
KKI_SENTINEL_SHARE=0.20 \
python3 schwarm_rollenspezialisierung.py
```

Die Rollenlern-Studie verfeinert diese Rollen um neue Lernprofile wie Vermittler und Analytiker:

```bash
python3 schwarm_rollenlernen.py
```

Optional lassen sich Wiederholungen und Rollenanteile anpassen:

```bash
KKI_ROLLENLERNEN_REPETITIONS=2 \
KKI_MEDIATOR_SHARE=0.15 \
KKI_ANALYZER_SHARE=0.15 \
python3 schwarm_rollenlernen.py
```

Die Rollenwechsel-Studie prueft als naechsten Schritt, ob der Schwarm zwischen Rollen dynamisch wechseln sollte:

```bash
python3 schwarm_rollenwechsel.py
```

Optional lassen sich Wiederholungen und Wechselparameter anpassen:

```bash
KKI_ROLLENWECHSEL_REPETITIONS=2 \
KKI_ENABLE_ROLE_SWITCHING=true \
KKI_ROLE_SWITCH_INTERVAL=20 \
python3 schwarm_rollenwechsel.py
```

Die Missionsziel-Studie koppelt diese Rollen anschliessend an explizite Teamaufgaben wie Konsensbildung, Wissensaustausch und Reputationsabwehr:

```bash
python3 schwarm_missionsziele.py
```

Optional lassen sich Wiederholungen sowie Missionen- und Wechselintervalle anpassen:

```bash
KKI_MISSION_REPETITIONS=2 \
KKI_MISSIONS_ENABLED=true \
KKI_MISSION_SWITCH_INTERVAL=20 \
python3 schwarm_missionsziele.py
```

Die Missionskonflikt-Studie untersucht anschliessend, ob adaptive Missionen durch explizite Arbitration unter konkurrierenden Zielen besser werden:

```bash
python3 schwarm_missionskonflikte.py
```

Optional lassen sich Wiederholungen sowie Konflikt- und Arbitration-Parameter anpassen:

```bash
KKI_MISSION_ARBITRATION_REPETITIONS=2 \
KKI_MISSION_CONFLICT_THRESHOLD=0.45 \
KKI_MISSION_ARBITRATION_MARGIN=0.08 \
python3 schwarm_missionskonflikte.py
```

Die Arbeitsketten-Studie baut darauf auf und untersucht, ob daraus mehrstufige Teamaufgaben mit Voraussetzungen entstehen koennen:

```bash
python3 schwarm_arbeitsketten.py
```

Optional lassen sich Wiederholungen und Workflow-Stufenparameter anpassen:

```bash
KKI_WORKFLOW_REPETITIONS=2 \
KKI_WORKFLOW_STAGES_ENABLED=true \
KKI_WORKFLOW_STAGE_MIN_TENURE=2 \
python3 schwarm_arbeitsketten.py
```

Die Arbeitszellen-Studie erweitert diese Ketten um spezialisierte Teilteams und gezielte Uebergaben:

```bash
python3 schwarm_arbeitszellen.py
```

Optional lassen sich Wiederholungen und Handoff-Parameter anpassen:

```bash
KKI_WORKFLOW_CELL_REPETITIONS=2 \
KKI_WORKFLOW_CELLS_ENABLED=true \
KKI_HANDOFF_COORDINATION_ENABLED=true \
KKI_HANDOFF_PRIORITY_BONUS=0.12 \
python3 schwarm_arbeitszellen.py
```

Die Parallel-Arbeitszellen-Studie laesst mehrere Zellen gleichzeitig an gekoppelten Teilaufgaben arbeiten und verteilt gemeinsame Ressourcen nach Prioritaet:

```bash
python3 schwarm_arbeitszellen_parallel.py
```

Optional lassen sich Ressourcenbudget und Parallelitaet feinjustieren:

```bash
KKI_PARALLEL_CELLS_REPETITIONS=2 \
KKI_PARALLEL_WORKFLOW_CELLS_ENABLED=true \
KKI_RESOURCE_COORDINATION_ENABLED=true \
KKI_RESOURCE_BUDGET=1.0 \
KKI_RESOURCE_SHARE_FACTOR=0.20 \
python3 schwarm_arbeitszellen_parallel.py
```

Die Faehigkeitscluster-Studie erweitert diese Architektur um spezialisierte Clusterprofile und asymmetrische Budgets:

```bash
python3 schwarm_faehigkeitscluster.py
```

Optional lassen sich Wiederholungen und Cluster-Schaerfe anpassen:

```bash
KKI_CAPABILITY_CLUSTER_REPETITIONS=2 \
KKI_CAPABILITY_CLUSTERS_ENABLED=true \
KKI_ASYMMETRIC_CLUSTER_BUDGETS_ENABLED=true \
KKI_CLUSTER_BUDGET_SKEW=0.35 \
python3 schwarm_faehigkeitscluster.py
```

Die Engpassmanagement-Studie legt auf diese Clusterarchitektur knappe Budgets und adaptive Ressourcen-Triage:

```bash
python3 schwarm_engpassmanagement.py
```

Optional lassen sich Engpass-Schwelle und Triage-Intensitaet anpassen:

```bash
KKI_BOTTLENECK_REPETITIONS=2 \
KKI_BOTTLENECK_MANAGEMENT_ENABLED=true \
KKI_BOTTLENECK_THRESHOLD=1.05 \
KKI_BOTTLENECK_TRIAGE_INTENSITY=0.55 \
python3 schwarm_engpassmanagement.py
```

Die Meta-Koordinations-Studie erweitert diese lokale Triage um globale Prioritaeten zwischen Missionen und Zellclustern:

```bash
python3 schwarm_meta_koordination.py
```

Optional lassen sich Meta-Intervall und Prioritaetsstaerke anpassen:

```bash
KKI_META_REPETITIONS=2 \
KKI_META_COORDINATION_ENABLED=true \
KKI_META_UPDATE_INTERVAL=12 \
KKI_META_PRIORITY_STRENGTH=0.18 \
python3 schwarm_meta_koordination.py
```

Optional lassen sich Wiederholungen und gemeinsame Basisparameter anpassen:

```bash
KKI_COUPLED_REPETITIONS=2 \
KKI_COUPLED_AGENT_COUNT=60 \
KKI_COUPLED_STRESS_ROUND=90 \
python3 schwarm_gekoppelte_abwehr.py
```

Optional lassen sich Wiederholungen und gemeinsame Basisparameter anpassen:

```bash
KKI_MEGASTUDY_REPETITIONS=2 \
KKI_MEGASTUDY_AGENT_COUNT=60 \
KKI_MEGASTUDY_STRESS_ROUND=90 \
python3 schwarm_grossstudie.py
```

Optional lassen sich Wiederholungen und Angriffsdruck anpassen:

```bash
KKI_BENCHMARK_REPETITIONS=3 \
KKI_COMMITMENT_ATTACK_STRENGTH=0.45 \
python3 schwarm_vertrauens_benchmark.py
```

Die Visualisierungs-Skripte erzeugen PNG-Dateien direkt im Projektverzeichnis.
Da die Simulationen Zufallselemente enthalten, können konkrete Zahlenwerte zwischen einzelnen Läufen variieren.

## Reproduktion der Beispielgrafiken

Die folgenden Skripte erzeugen die im Repository abgelegten PNG-Dateien:

| Skript | Ausgabe | Beispiel |
| --- | --- | --- |
| `kooperation_visual.py` | `kki_kooperation_graph.png` | `KKI_SEED=42 python3 kooperation_visual.py` |
| `schwarm_simulation.py` | `kki_schwarm_simulation.png` | `KKI_SEED=42 python3 schwarm_simulation.py` |
| `schwarm_100.py` | `kki_100_agenten.png` | `KKI_SEED=42 python3 schwarm_100.py` |
| `schwarm_cluster.py` | `kki_cluster_simulation.png` | `KKI_SEED=42 python3 schwarm_cluster.py` |
| `schwarm_invasion.py` | `kki_invasion.png` | `KKI_SEED=42 python3 schwarm_invasion.py` |
| `schwarm_polarisierung.py` | `kki_polarisierung.png` | `KKI_SEED=42 KKI_POLARIZATION_SCENARIO=polarization python3 schwarm_polarisierung.py` |
| `schwarm_parameterstudie.py` | `kki_netzwerk_parameterstudie.png` | `KKI_SEED=42 python3 schwarm_parameterstudie.py` |
| `schwarm_adaptive_netzwerke.py` | `kki_adaptive_netzwerke.png` | `KKI_SEED=42 python3 schwarm_adaptive_netzwerke.py` |
| `schwarm_invasive_netzwerke.py` | `kki_invasive_netzwerke.png` | `KKI_SEED=42 python3 schwarm_invasive_netzwerke.py` |
| `schwarm_commitment_resilienz.py` | `kki_commitment_resilienz.png` | `KKI_SEED=42 python3 schwarm_commitment_resilienz.py` |
| `schwarm_vertrauens_benchmark.py` | `kki_vertrauens_benchmark.png` | `KKI_SEED=42 python3 schwarm_vertrauens_benchmark.py` |
| `schwarm_grossstudie.py` | `kki_grossstudie.png` | `KKI_SEED=42 python3 schwarm_grossstudie.py` |
| `schwarm_anti_polarisierung.py` | `kki_anti_polarisierung.png` | `KKI_SEED=42 python3 schwarm_anti_polarisierung.py` |
| `schwarm_gekoppelte_abwehr.py` | `kki_gekoppelte_abwehr.png` | `KKI_SEED=42 python3 schwarm_gekoppelte_abwehr.py` |
| `schwarm_rollenspezialisierung.py` | `kki_rollenspezialisierung.png` | `KKI_SEED=42 python3 schwarm_rollenspezialisierung.py` |
| `schwarm_rollenlernen.py` | `kki_rollenlernen.png` | `KKI_SEED=42 python3 schwarm_rollenlernen.py` |
| `schwarm_rollenwechsel.py` | `kki_rollenwechsel.png` | `KKI_SEED=42 python3 schwarm_rollenwechsel.py` |
| `schwarm_missionsziele.py` | `kki_missionsziele.png` | `KKI_SEED=42 python3 schwarm_missionsziele.py` |
| `schwarm_missionskonflikte.py` | `kki_missionskonflikte.png` | `KKI_SEED=42 python3 schwarm_missionskonflikte.py` |
| `schwarm_arbeitsketten.py` | `kki_arbeitsketten.png` | `KKI_SEED=42 python3 schwarm_arbeitsketten.py` |
| `schwarm_arbeitszellen.py` | `kki_arbeitszellen.png` | `KKI_SEED=42 python3 schwarm_arbeitszellen.py` |
| `schwarm_arbeitszellen_parallel.py` | `kki_arbeitszellen_parallel.png` | `KKI_SEED=42 python3 schwarm_arbeitszellen_parallel.py` |
| `schwarm_faehigkeitscluster.py` | `kki_faehigkeitscluster.png` | `KKI_SEED=42 python3 schwarm_faehigkeitscluster.py` |
| `schwarm_engpassmanagement.py` | `kki_engpassmanagement.png` | `KKI_SEED=42 python3 schwarm_engpassmanagement.py` |
| `schwarm_meta_koordination.py` | `kki_meta_koordination.png` | `KKI_SEED=42 python3 schwarm_meta_koordination.py` |
| `commitment_protokoll.py` | `kki_commitment_protokoll.png` | `KKI_SEED=42 python3 commitment_protokoll.py` |

Hinweise zur Reproduktion:

- `KKI_SEED=42` sorgt für denselben Zufallsstart bei wiederholten Läufen.
- `KKI_OUTPUT_DIR=artefakte` schreibt PNG-Dateien in ein separates Verzeichnis statt ins Projektwurzelverzeichnis.
- für schnelle technische Prüfungen ohne GUI kann zusätzlich `KKI_TEST_MODE=1` gesetzt werden
- adaptive Netzwerke lassen sich u. a. mit `KKI_REWIRING_ENABLED`, `KKI_REWIRE_REP_THRESHOLD` und `KKI_REWIRE_PROXIMITY_WEIGHT` steuern
- das Invasions-Experiment nutzt zusaetzlich `KKI_INVASION_AGENT_COUNT`, `KKI_INVASION_REP_THRESHOLDS` und `KKI_INVASION_PROXIMITY_WEIGHTS`
- das Commitment-Experiment nutzt zusaetzlich `KKI_COMMITMENT_ATTACK_STRENGTH`, `KKI_COMMITMENT_REP_THRESHOLDS` und `KKI_COMMITMENT_TRUST_THRESHOLDS`
- der Vertrauens-Benchmark nutzt zusaetzlich `KKI_BENCHMARK_REPETITIONS` und vergleicht statische, reputationsbasierte, commitment-basierte, meinungsbasierte und hybride Strategien
- die Grossstudie nutzt zusaetzlich `KKI_MEGASTUDY_REPETITIONS`, `KKI_MEGASTUDY_AGENT_COUNT` und `KKI_MEGASTUDY_STRESS_ROUND` fuer eine gemeinsame Grundlagenkonfiguration
- die Anti-Polarisierungsstudie nutzt zusaetzlich `KKI_ANTI_POL_REPETITIONS`, `KKI_ANTI_POL_AGENT_COUNT` und die optionalen Schalter `KKI_BRIDGE_MECHANISM`, `KKI_CENTRIST_MODERATION` und `KKI_MEDIATOR_MODE`
- die gekoppelte Abwehrstudie nutzt zusaetzlich `KKI_COUPLED_REPETITIONS`, `KKI_COUPLED_AGENT_COUNT` und `KKI_COUPLED_STRESS_ROUND` fuer den Architekturvergleich ueber mehrere Bedrohungen
- die Rollenspezialisierungsstudie nutzt zusaetzlich `KKI_ROLLENSPEZ_REPETITIONS`, `KKI_GENERALIST_SHARE`, `KKI_CONNECTOR_SHARE` und `KKI_SENTINEL_SHARE`
- die Rollenlern-Studie nutzt zusaetzlich `KKI_ROLLENLERNEN_REPETITIONS`, `KKI_MEDIATOR_SHARE`, `KKI_ANALYZER_SHARE` sowie die Lernparameter fuer Connector, Sentinel, Vermittler und Analytiker
- die Rollenwechsel-Studie nutzt zusaetzlich `KKI_ROLLENWECHSEL_REPETITIONS`, `KKI_ENABLE_ROLE_SWITCHING`, `KKI_ROLE_SWITCH_INTERVAL` und `KKI_ROLE_SWITCH_MIN_TENURE`
- die Missionsziel-Studie nutzt zusaetzlich `KKI_MISSION_REPETITIONS`, `KKI_MISSION_SWITCH_INTERVAL` und die Missionsschalter `KKI_MISSIONS_ENABLED` sowie `KKI_MISSION_ASSIGNMENT`
- die Missionskonflikt-Studie nutzt zusaetzlich `KKI_MISSION_ARBITRATION_REPETITIONS`, `KKI_MISSION_CONFLICT_THRESHOLD`, `KKI_MISSION_ARBITRATION_MARGIN` sowie `KKI_MISSION_ARBITRATION_ENABLED`
- die Arbeitsketten-Studie nutzt zusaetzlich `KKI_WORKFLOW_REPETITIONS`, `KKI_WORKFLOW_STAGE_MIN_TENURE` und `KKI_WORKFLOW_STAGES_ENABLED`
- die Arbeitszellen-Studie nutzt zusaetzlich `KKI_WORKFLOW_CELL_REPETITIONS`, `KKI_WORKFLOW_CELLS_ENABLED`, `KKI_HANDOFF_COORDINATION_ENABLED` und `KKI_HANDOFF_PRIORITY_BONUS`
- die Parallel-Arbeitszellen-Studie nutzt zusaetzlich `KKI_PARALLEL_CELLS_REPETITIONS`, `KKI_PARALLEL_WORKFLOW_CELLS_ENABLED`, `KKI_RESOURCE_COORDINATION_ENABLED`, `KKI_RESOURCE_BUDGET` und `KKI_RESOURCE_SHARE_FACTOR`
- die Faehigkeitscluster-Studie nutzt zusaetzlich `KKI_CAPABILITY_CLUSTER_REPETITIONS`, `KKI_CAPABILITY_CLUSTERS_ENABLED`, `KKI_ASYMMETRIC_CLUSTER_BUDGETS_ENABLED` und `KKI_CLUSTER_BUDGET_SKEW`
- die Engpassmanagement-Studie nutzt zusaetzlich `KKI_BOTTLENECK_REPETITIONS`, `KKI_BOTTLENECK_MANAGEMENT_ENABLED`, `KKI_BOTTLENECK_THRESHOLD` und `KKI_BOTTLENECK_TRIAGE_INTENSITY`
- die Meta-Koordinations-Studie nutzt zusaetzlich `KKI_META_REPETITIONS`, `KKI_META_COORDINATION_ENABLED`, `KKI_META_UPDATE_INTERVAL` und `KKI_META_PRIORITY_STRENGTH`

Beispiel für eine reproduzierbare, headless Erzeugung:

```bash
KKI_SEED=42 KKI_OUTPUT_DIR=artefakte MPLBACKEND=Agg python3 commitment_protokoll.py
```

## Smoke-Tests

Für schnelle technische Prüfungen gibt es `smoke_tests.py`.

```bash
python3 smoke_tests.py
```

Die Smoke-Tests starten ausgewählte Kernskripte im verkürzten headless Testmodus.

## Beispiel-Visualisierungen

### Zwei Agenten: Emergenz von Kooperation

![KKI Kooperationsgraph](kki_kooperation_graph.png)

### Schwarm-Simulation

![KKI Schwarm-Simulation](kki_schwarm_simulation.png)

### Polarisierung und Konsensbildung

![KKI Polarisierungs-Experiment](kki_polarisierung.png)

### Adaptive Netzwerke und soziale Brücken

![KKI Adaptive Netzwerk-Studie](kki_adaptive_netzwerke.png)

### Adaptive Netzwerke unter Invasion

![KKI Invasive Netzwerke](kki_invasive_netzwerke.png)

### Adaptive Netzwerke gegen Commitment-Angriffe

![KKI Commitment-Resilienz](kki_commitment_resilienz.png)

### Benchmark fuer Vertrauenssignale

![KKI Vertrauens-Benchmark](kki_vertrauens_benchmark.png)

### Kombinierte Grossstudie

![KKI Grossstudie](kki_grossstudie.png)

### Anti-Polarisierungsstudie

![KKI Anti-Polarisierung](kki_anti_polarisierung.png)

### Gekoppelte Abwehrstudie

![KKI Gekoppelte Abwehr](kki_gekoppelte_abwehr.png)

### Rollenspezialisierungsstudie

![KKI Rollenspezialisierung](kki_rollenspezialisierung.png)

### Rollenlern-Studie

![KKI Rollenlernen](kki_rollenlernen.png)

### Rollenwechsel-Studie

![KKI Rollenwechsel](kki_rollenwechsel.png)

### Missionsziel-Studie

![KKI Missionsziele](kki_missionsziele.png)

### Missionskonflikt-Studie

![KKI Missionskonflikte](kki_missionskonflikte.png)

### Arbeitsketten-Studie

![KKI Arbeitsketten](kki_arbeitsketten.png)

### Arbeitszellen-Studie

![KKI Arbeitszellen](kki_arbeitszellen.png)

### Parallele Arbeitszellen-Studie

![KKI Parallele Arbeitszellen](kki_arbeitszellen_parallel.png)

### Faehigkeitscluster-Studie

![KKI Faehigkeitscluster](kki_faehigkeitscluster.png)

### Engpassmanagement-Studie

![KKI Engpassmanagement](kki_engpassmanagement.png)

### Meta-Koordinations-Studie

![KKI Meta-Koordination](kki_meta_koordination.png)

## Zentrale Beobachtungen

Die bisherigen Simulationen illustrieren wiederkehrende Muster:

- kooperative Agenten stabilisieren und steigern ihre Intelligenz häufiger
- Defektoren verlieren auf Dauer Anschluss an die leistungsfähigen Teile des Systems
- Schwarmstrukturen können Kooperation auch gegen Störungen oder Invasionsversuche absichern
- spezialisierte Teilteams profitieren zusaetzlich, wenn mehrere Zellen parallel arbeiten und knappe Ressourcen koordiniert teilen
- adaptive Rewiring-Regeln zeigen, wie stark soziale Brücken und Vertrauenssignale die Lagerbildung beeinflussen
- unter Invasion wirkt adaptives Rewiring als Resilienzmechanismus, wenn schlechte Partner schnell isoliert und kooperative Kerne erhalten werden
- Commitment-Mechanismen erschweren oder verhindern strategische Täuschung
- adaptive Netzwerke koennen Commitment-Brueche zusaetzlich in schnelle soziale Isolation manipulativer Agenten uebersetzen
- unterschiedliche Vertrauenssignale lassen sich nun direkt benchmarken, statt nur einzeln in getrennten Experimenten zu betrachten
- die neue Grossstudie verbindet diese Einzelbefunde zu einer gemeinsamen Grundlage fuer spaetere Agenten mit einheitlicher DNA und gruppenspezifischen Zusatzfaehigkeiten
- reine Polarisierung braucht zusaetzlich soziale Bruecken und eine stabile Mittelzone; genau diese Mechanismen vergleicht nun die Anti-Polarisierungsstudie explizit
- die gekoppelte Abwehrstudie prueft nun, ob Anti-Polarisierung nur lokal wirkt oder als Teil einer breiteren Schutzarchitektur neben Invasions- und Commitment-Abwehr bestehen kann
- die Rollenspezialisierungsstudie untersucht nun, ob dieselbe Grund-DNA bereits durch Brueckenbauer- und Waechterrollen robuster wird als ein homogener Schwarm
- die Rollenlern-Studie untersucht nun, ob aus diesen Rollen auch verfeinerte Lernprofile wie Vermittler und Analytiker mit eigenstaendigen Staerken ableitbar sind
- die Rollenwechsel-Studie untersucht nun, ob stabile Spezialrollen bereits genuegen oder ob ein dynamischer Wechsel zwischen Aufgaben im Schwarm zusaetzliche Vorteile bringt
- die Missionsziel-Studie untersucht nun, ob dieselben Rollen durch explizite Teamaufgaben noch fokussierter auf Konsens, Wissensaustausch und Abwehr ausgerichtet werden koennen
- die Missionskonflikt-Studie untersucht nun, ob adaptive Missionen besser werden, wenn der Schwarm Zielkonflikte explizit erkennt und konkurrierende Aufgaben arbitriert
- die Arbeitsketten-Studie untersucht nun, ob aus diesen Missionen mehrstufige Arbeitsablaeufe mit Abhaengigkeiten entstehen koennen, statt nur einzelne Aufgaben zu optimieren
- die Arbeitszellen-Studie untersucht nun, ob spezialisierte Teilteams mit expliziten Uebergaben die Arbeitsketten nochmals koordinierter und skalierbarer machen

## Projektstruktur und Ausrichtung

Das Repository ist experimentell aufgebaut: von einem kleinen Zwei-Agenten-Modell bis hin zu größeren Simulationen mit 50 bis 100 Agenten. Dadurch eignet es sich sowohl für konzeptionelle Demonstrationen als auch für die schrittweise Weiterentwicklung der zugrunde liegenden Theorie.

Die Dateien `kki_*.png` dokumentieren Beispielausgaben der Simulationen. Zusätzlich enthält das Repository mit `sektion_viii_empirische_validierung.docx` begleitendes Arbeitsmaterial zur theoretischen Einbettung.

## Lizenz

Dieses Projekt steht unter der `MIT License`. Details findest du in der Datei [`LICENSE`](LICENSE).

## Autor

Jan Niklas ([@janniklas123jnz-beep](https://github.com/janniklas123jnz-beep))
