"""
KKI Adaptive Netzwerke unter Invasion
=====================================
Vergleicht statische und adaptive Netzwerke unter gezielter Invasion durch
defektorische Stoeragenten.
"""

from __future__ import annotations

import os
import random
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_polarisierung import (
    DEFAULT_RANDOM_EDGE_CHANCE,
    aktualisiere_adaptives_netzwerk,
    berechne_netzwerkmetriken,
)

DEFAULT_NATIVE_AGENT_COUNT = 60
DEFAULT_INVASION_AGENT_COUNT = 12
DEFAULT_TOTAL_ROUNDS = 180
DEFAULT_INVASION_ROUND = 90
DEFAULT_CONNECTIONS_PER_AGENT = 8
DEFAULT_INTERACTIONS_PER_ROUND = 90


class Agent:
    """Agent fuer Invasions- und Resilienzexperimente."""

    def __init__(
        self,
        agent_id,
        gruppe,
        meinung,
        kooperations_neigung,
        *,
        ist_invasor=False,
        hartnaeckigkeit=0.0,
    ):
        self.id = agent_id
        self.gruppe = gruppe
        self.meinung = meinung
        self.kooperations_neigung = kooperations_neigung
        self.ist_invasor = ist_invasor
        self.hartnaeckigkeit = hartnaeckigkeit
        self.intelligenz = 1.0 if not ist_invasor else 0.82
        self.reputation = 0.5 if not ist_invasor else 0.25
        self.nachbarn = set()
        self.interaktions_history = defaultdict(list)
        self.geboren_runde = 0

    def verbinde(self, anderer):
        self.nachbarn.add(anderer.id)
        anderer.nachbarn.add(self.id)

    def trenne(self, anderer):
        self.nachbarn.discard(anderer.id)
        anderer.nachbarn.discard(self.id)

    def berechne_partner_reputation(self, partner_id):
        history = self.interaktions_history.get(partner_id, [])
        if not history:
            return 0.5
        return sum(1 for aktion in history[-10:] if aktion == 'C') / len(history[-10:])

    def waehle_aktion(self, partner_reputation, partner_meinung):
        meinungs_distanz = abs(self.meinung - partner_meinung)
        aehnlichkeit = 1.0 - meinungs_distanz

        effektive_neigung = self.kooperations_neigung
        effektive_neigung *= 0.55 + 0.45 * partner_reputation
        effektive_neigung *= 0.35 + 0.65 * aehnlichkeit
        if self.ist_invasor:
            effektive_neigung *= 0.45
        effektive_neigung = max(0.03, min(0.97, effektive_neigung))
        return 'C' if random.random() < effektive_neigung else 'D'

    def lerne(self, meine_aktion, andere_aktion, partner_id, partner_intelligenz, partner_meinung):
        self.interaktions_history[partner_id].append(andere_aktion)
        meinungs_distanz = abs(self.meinung - partner_meinung)
        aehnlichkeit = 1.0 - meinungs_distanz
        beweglichkeit = 1.0 - self.hartnaeckigkeit

        if meine_aktion == 'C' and andere_aktion == 'C':
            self.intelligenz *= 1.002 + 0.002 * aehnlichkeit + 0.001 * min(partner_intelligenz, 4.0)
            self.kooperations_neigung += 0.005
            self.reputation += 0.012
            self.meinung += (partner_meinung - self.meinung) * 0.08 * beweglichkeit
        elif meine_aktion == 'C' and andere_aktion == 'D':
            self.kooperations_neigung -= 0.005
            self.reputation += 0.003
            if meinungs_distanz > 0.25:
                self.meinung += (self.meinung - partner_meinung) * 0.02 * beweglichkeit
        elif meine_aktion == 'D' and andere_aktion == 'C':
            self.intelligenz *= 0.996
            self.reputation -= 0.025
            if meinungs_distanz > 0.2:
                self.meinung += (self.meinung - partner_meinung) * 0.025 * beweglichkeit
        else:
            self.intelligenz *= 0.990
            self.reputation -= 0.012
            self.kooperations_neigung += 0.002
            if meinungs_distanz > 0.2:
                self.meinung += (self.meinung - partner_meinung) * 0.018 * beweglichkeit

        self.kooperations_neigung = max(0.03, min(0.97, self.kooperations_neigung))
        self.intelligenz = max(0.1, min(8.0, self.intelligenz))
        self.reputation = max(0.0, min(1.0, self.reputation))
        self.meinung = max(0.0, min(1.0, self.meinung))


def parse_float_grid(name: str, default_values):
    raw = os.getenv(name)
    if not raw:
        return list(default_values)
    return [float(value.strip()) for value in raw.split(',') if value.strip()]


def studienparameter():
    if is_test_mode():
        rep_thresholds = parse_float_grid('KKI_INVASION_REP_THRESHOLDS', [0.25, 0.40])
        proximity_weights = parse_float_grid('KKI_INVASION_PROXIMITY_WEIGHTS', [0.25, 0.55])
        repetitions = int(os.getenv('KKI_INVASION_REPETITIONS', '2'))
        rounds = min(DEFAULT_TOTAL_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        invasion_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        rep_thresholds = parse_float_grid('KKI_INVASION_REP_THRESHOLDS', [0.25, 0.35, 0.45, 0.55])
        proximity_weights = parse_float_grid('KKI_INVASION_PROXIMITY_WEIGHTS', [0.25, 0.45, 0.65, 0.85])
        repetitions = int(os.getenv('KKI_INVASION_REPETITIONS', '3'))
        rounds = DEFAULT_TOTAL_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        invasion_round = int(os.getenv('KKI_INVASION_ROUND', str(DEFAULT_INVASION_ROUND)))

    return {
        'rep_thresholds': rep_thresholds,
        'proximity_weights': proximity_weights,
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'invasion_round': invasion_round,
        'native_count': int(os.getenv('KKI_NATIVE_AGENT_COUNT', str(DEFAULT_NATIVE_AGENT_COUNT))),
        'invasion_count': int(os.getenv('KKI_INVASION_AGENT_COUNT', str(DEFAULT_INVASION_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'cross_group': float(os.getenv('KKI_CROSS_GROUP_CHANCE', '0.35')),
        'random_edge_chance': float(os.getenv('KKI_RANDOM_EDGE_CHANCE', str(DEFAULT_RANDOM_EDGE_CHANCE))),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def erstelle_native_agenten(agent_count):
    agenten = []
    gruppengroesse = agent_count // 2
    for index in range(agent_count):
        gruppe = 0 if index < gruppengroesse else 1
        basis_meinung = 0.42 if gruppe == 0 else 0.58
        kooperation = 0.60 if gruppe == 0 else 0.58
        hartnaeckigkeit = 0.10 if index % 9 == 0 else 0.04
        meinung = max(0.0, min(1.0, random.gauss(basis_meinung, 0.05)))
        agenten.append(
            Agent(index, gruppe, meinung, kooperation, ist_invasor=False, hartnaeckigkeit=hartnaeckigkeit)
        )
    return agenten


def erstelle_basisnetz(agenten, degree, cross_group_chance, random_edge_chance):
    gruppen = {
        0: [agent for agent in agenten if agent.gruppe == 0],
        1: [agent for agent in agenten if agent.gruppe == 1],
    }

    for gruppen_agenten in gruppen.values():
        n = len(gruppen_agenten)
        for index in range(n):
            for offset in range(1, degree // 2 + 1):
                gruppen_agenten[index].verbinde(gruppen_agenten[(index + offset) % n])

    for agent in agenten:
        if random.random() < cross_group_chance:
            andere = [ziel for ziel in agenten if ziel.gruppe != agent.gruppe]
            if andere:
                agent.verbinde(random.choice(andere))

        if random.random() < random_edge_chance:
            moegliche = [ziel for ziel in agenten if ziel.id != agent.id and ziel.id not in agent.nachbarn]
            if moegliche:
                agent.verbinde(random.choice(moegliche))


def fuege_invasoren_hinzu(agenten, agenten_dict, config, runde):
    start_id = max(agent.id for agent in agenten) + 1
    invasoren = []
    for offset in range(int(config['invasion_count'])):
        meinung = max(0.0, min(1.0, random.gauss(0.86, 0.04)))
        invasor = Agent(
            start_id + offset,
            2,
            meinung,
            0.16,
            ist_invasor=True,
            hartnaeckigkeit=0.35,
        )
        invasor.geboren_runde = runde
        invasoren.append(invasor)
        agenten.append(invasor)
        agenten_dict[invasor.id] = invasor

    native_agenten = [agent for agent in agenten if not agent.ist_invasor]
    degree = int(config['degree'])
    for invasor in invasoren:
        ziele = random.sample(native_agenten, min(degree, len(native_agenten)))
        for ziel in ziele:
            invasor.verbinde(ziel)

    return invasoren


def waehle_partner(agent, aktive_agenten, agenten_dict):
    if agent.nachbarn and random.random() < 0.9:
        gueltige = [nachbar_id for nachbar_id in agent.nachbarn if nachbar_id in agenten_dict]
        if gueltige:
            return agenten_dict[random.choice(gueltige)]
    kandidaten = [anderer for anderer in aktive_agenten if anderer.id != agent.id]
    return random.choice(kandidaten)


def anteil_invader_kanten(agenten):
    kanten = set()
    invader_kanten = 0
    for agent in agenten:
        for nachbar_id in agent.nachbarn:
            kante = tuple(sorted((agent.id, nachbar_id)))
            if kante in kanten:
                continue
            kanten.add(kante)
            if agent.ist_invasor or any(a.id == nachbar_id and a.ist_invasor for a in agenten):
                invader_kanten += 1
    return invader_kanten / len(kanten) if kanten else 0.0


def run_invasion_experiment(config, *, adaptive_enabled, rep_threshold, proximity_weight):
    agenten = erstelle_native_agenten(int(config['native_count']))
    agenten_dict = {agent.id: agent for agent in agenten}
    erstelle_basisnetz(
        agenten,
        int(config['degree']),
        float(config['cross_group']),
        float(config['random_edge_chance']),
    )

    total_rounds = int(config['rounds'])
    invasion_round = int(config['invasion_round'])
    interactions_per_round = int(config['interactions'])

    native_phi_history = []
    invader_phi_history = []
    cooperation_history = []
    rewiring_history = []
    native_reputation_history = []
    invader_reputation_history = []
    invader_edge_history = []
    density_history = []
    response_round = None
    invasoren = []
    pre_invasion_native_phi = None

    adaptive_config = {
        'enable_dynamic_rewiring': adaptive_enabled,
        'rewire_min_interactions': 2,
        'rewire_reputation_threshold': rep_threshold,
        'rewire_opinion_distance_threshold': 0.60,
        'rewire_proximity_weight': proximity_weight,
        'rewire_removal_probability': 0.45,
        'rewire_addition_probability': 0.80,
        'rewire_cross_group_bonus': 0.0,
        'rewire_target_degree': int(config['degree']),
    }

    for runde in range(1, total_rounds + 1):
        if runde == invasion_round:
            invasoren = fuege_invasoren_hinzu(agenten, agenten_dict, config, runde)
            pre_invasion_native_phi = mittelwert([agent.intelligenz for agent in agenten if not agent.ist_invasor])

        aktive_agenten = [agent for agent in agenten if agent.geboren_runde <= runde]
        kooperative_interaktionen = 0

        for _ in range(interactions_per_round):
            if len(aktive_agenten) < 2:
                continue
            agent = random.choice(aktive_agenten)
            partner = waehle_partner(agent, aktive_agenten, agenten_dict)

            partner_rep = agent.berechne_partner_reputation(partner.id)
            agent_rep = partner.berechne_partner_reputation(agent.id)

            aktion_a = agent.waehle_aktion(partner_rep, partner.meinung)
            aktion_b = partner.waehle_aktion(agent_rep, agent.meinung)
            if aktion_a == 'C' and aktion_b == 'C':
                kooperative_interaktionen += 1

            agent.lerne(aktion_a, aktion_b, partner.id, partner.intelligenz, partner.meinung)
            partner.lerne(aktion_b, aktion_a, agent.id, agent.intelligenz, agent.meinung)

        rewiring_stats = {'rewired_edges': 0}
        if invasoren and adaptive_enabled and runde >= invasion_round:
            rewiring_stats = aktualisiere_adaptives_netzwerk(agenten, agenten_dict, adaptive_config)
            if rewiring_stats['rewired_edges'] > 0 and response_round is None:
                response_round = runde

        native_agents = [agent for agent in agenten if not agent.ist_invasor]
        active_invaders = [agent for agent in invasoren if agent.geboren_runde <= runde]
        metrics = berechne_netzwerkmetriken(agenten, agenten_dict)

        native_phi_history.append(mittelwert([agent.intelligenz for agent in native_agents]))
        invader_phi_history.append(mittelwert([agent.intelligenz for agent in active_invaders]))
        cooperation_history.append(kooperative_interaktionen / max(1, interactions_per_round))
        rewiring_history.append(rewiring_stats['rewired_edges'])
        native_reputation_history.append(mittelwert([agent.reputation for agent in native_agents]))
        invader_reputation_history.append(mittelwert([agent.reputation for agent in active_invaders]))
        invader_edge_history.append(anteil_invader_kanten(agenten))
        density_history.append(metrics['density'])

    native_final_phi = native_phi_history[-1]
    invader_final_phi = invader_phi_history[-1] if invader_phi_history else 0.0
    native_final_rep = native_reputation_history[-1]
    invader_final_rep = invader_reputation_history[-1] if invader_reputation_history else 0.0
    pre_invasion_native_phi = pre_invasion_native_phi if pre_invasion_native_phi is not None else native_phi_history[0]
    resilience_ratio = native_final_phi / pre_invasion_native_phi if pre_invasion_native_phi else 0.0
    repulsion_index = native_final_phi - invader_final_phi
    reputation_divergence = native_final_rep - invader_final_rep
    final_invader_edge_share = invader_edge_history[-1]
    average_rewiring = mittelwert(rewiring_history[invasion_round - 1 :]) if invasoren else 0.0
    response_delay = None if response_round is None else response_round - invasion_round
    resilience_score = resilience_ratio + repulsion_index + reputation_divergence - final_invader_edge_share

    return {
        'native_final_phi': native_final_phi,
        'invader_final_phi': invader_final_phi,
        'resilience_ratio': resilience_ratio,
        'repulsion_index': repulsion_index,
        'reputation_divergence': reputation_divergence,
        'final_invader_edge_share': final_invader_edge_share,
        'average_rewiring': average_rewiring,
        'response_delay': response_delay,
        'resilience_score': resilience_score,
        'cooperation_history': cooperation_history,
        'native_phi_history': native_phi_history,
        'invader_phi_history': invader_phi_history,
        'rewiring_history': rewiring_history,
        'density_history': density_history,
        'native_reputation_history': native_reputation_history,
        'invader_reputation_history': invader_reputation_history,
    }


def run_once(seed, params, *, adaptive_enabled, rep_threshold=None, proximity_weight=None):
    random.seed(seed)
    np.random.seed(seed)
    return run_invasion_experiment(
        params,
        adaptive_enabled=adaptive_enabled,
        rep_threshold=0.35 if rep_threshold is None else rep_threshold,
        proximity_weight=0.45 if proximity_weight is None else proximity_weight,
    )


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print("=" * 84)
    print("KKI INVASIONS-RESILIENZ IN ADAPTIVEN NETZWERKEN")
    print("=" * 84)
    print(
        f"Seed-Basis: {base_seed} | Runden: {params['rounds']} | "
        f"Invasion ab Runde {params['invasion_round']}"
    )
    print(
        f"Basisnetz: Agenten={params['native_count']} + Invasoren={params['invasion_count']}, "
        f"Grad={params['degree']}, Cross-Group={params['cross_group']:.2f}"
    )
    print(
        f"Rep-Schwellen: {params['rep_thresholds']} | "
        f"Proximity-Gewichte: {params['proximity_weights']} | "
        f"Wiederholungen: {params['repetitions']}"
    )
    print("\nStudie läuft...\n")

    baseline_runs = []
    for repetition in range(params['repetitions']):
        baseline_runs.append(run_once(base_seed + repetition, params, adaptive_enabled=False))

    baseline = {
        'resilience_score': mittelwert([run['resilience_score'] for run in baseline_runs]),
        'resilience_ratio': mittelwert([run['resilience_ratio'] for run in baseline_runs]),
        'repulsion_index': mittelwert([run['repulsion_index'] for run in baseline_runs]),
        'reputation_divergence': mittelwert([run['reputation_divergence'] for run in baseline_runs]),
        'final_invader_edge_share': mittelwert([run['final_invader_edge_share'] for run in baseline_runs]),
    }
    print(
        "Statisches Basisnetz:\n"
        f"  Resilienz-Score:        {baseline['resilience_score']:+.3f}\n"
        f"  Native-Retention:       {baseline['resilience_ratio']:.3f}\n"
        f"  Invasor-Repulsion:      {baseline['repulsion_index']:+.3f}\n"
        f"  Reputations-Divergenz:  {baseline['reputation_divergence']:+.3f}\n"
        f"  Invasor-Kantenanteil:   {baseline['final_invader_edge_share']:.1%}\n"
    )

    rep_thresholds = params['rep_thresholds']
    proximity_weights = params['proximity_weights']
    shape = (len(rep_thresholds), len(proximity_weights))
    resilience_matrix = np.zeros(shape)
    retention_matrix = np.zeros(shape)
    repulsion_matrix = np.zeros(shape)
    rewiring_matrix = np.zeros(shape)
    invader_edge_matrix = np.zeros(shape)
    divergence_matrix = np.zeros(shape)
    best_score = None
    best_setting = None

    for row, rep_threshold in enumerate(rep_thresholds):
        for col, proximity_weight in enumerate(proximity_weights):
            runs = []
            for repetition in range(params['repetitions']):
                seed = base_seed + row * 100 + col * 10 + repetition
                runs.append(
                    run_once(
                        seed,
                        params,
                        adaptive_enabled=True,
                        rep_threshold=rep_threshold,
                        proximity_weight=proximity_weight,
                    )
                )

            resilience_matrix[row, col] = mittelwert([run['resilience_score'] for run in runs])
            retention_matrix[row, col] = mittelwert([run['resilience_ratio'] for run in runs])
            repulsion_matrix[row, col] = mittelwert([run['repulsion_index'] for run in runs])
            rewiring_matrix[row, col] = mittelwert([run['average_rewiring'] for run in runs])
            invader_edge_matrix[row, col] = mittelwert([run['final_invader_edge_share'] for run in runs])
            divergence_matrix[row, col] = mittelwert([run['reputation_divergence'] for run in runs])

            print(
                f"Rep={rep_threshold:.2f}, Proximity={proximity_weight:.2f} -> "
                f"Score={resilience_matrix[row, col]:+.3f}, "
                f"Retention={retention_matrix[row, col]:.3f}, "
                f"Repulsion={repulsion_matrix[row, col]:+.3f}, "
                f"Invader-Kanten={invader_edge_matrix[row, col]:.1%}"
            )

            if best_score is None or resilience_matrix[row, col] > best_score:
                best_score = resilience_matrix[row, col]
                response_delays = [run['response_delay'] for run in runs if run['response_delay'] is not None]
                best_setting = {
                    'rep_threshold': rep_threshold,
                    'proximity_weight': proximity_weight,
                    'resilience_score': resilience_matrix[row, col],
                    'retention': retention_matrix[row, col],
                    'repulsion': repulsion_matrix[row, col],
                    'rewiring': rewiring_matrix[row, col],
                    'invader_edge_share': invader_edge_matrix[row, col],
                    'divergence': divergence_matrix[row, col],
                    'response_delay': mittelwert(response_delays) if response_delays else 0.0,
                }

    print("\n" + "=" * 84)
    print("ERGEBNISSE")
    print("=" * 84)
    print(
        "Beste adaptive Abwehr:\n"
        f"  Reputations-Schwelle: {best_setting['rep_threshold']:.2f}\n"
        f"  Proximity-Gewicht:    {best_setting['proximity_weight']:.2f}\n"
        f"  Resilienz-Score:      {best_setting['resilience_score']:+.3f}\n"
        f"  Native-Retention:     {best_setting['retention']:.3f}\n"
        f"  Invasor-Repulsion:    {best_setting['repulsion']:+.3f}\n"
        f"  Reputations-Divergenz:{best_setting['divergence']:+.3f}\n"
        f"  Invasor-Kantenanteil: {best_setting['invader_edge_share']:.1%}\n"
        f"  Ø Rewiring/Runde:     {best_setting['rewiring']:.2f}\n"
        f"  Ø Reaktionsverzug:    {best_setting['response_delay']:.2f} Runden"
    )
    print(
        "\nDelta zum statischen Basisnetz:\n"
        f"  Δ Resilienz:    {best_setting['resilience_score'] - baseline['resilience_score']:+.3f}\n"
        f"  Δ Retention:    {best_setting['retention'] - baseline['resilience_ratio']:+.3f}\n"
        f"  Δ Repulsion:    {best_setting['repulsion'] - baseline['repulsion_index']:+.3f}\n"
        f"  Δ InvaderShare: {best_setting['invader_edge_share'] - baseline['final_invader_edge_share']:+.3f}"
    )

    fig, axes = plt.subplots(2, 3, figsize=(17, 11))
    fig.suptitle(
        'KKI Adaptive Netzwerke unter Invasion: statisch vs. adaptiv',
        fontsize=14,
        fontweight='bold',
    )

    heatmaps = [
        (axes[0, 0], resilience_matrix, 'Resilienz-Score\n(größer ist besser)', 'viridis'),
        (axes[0, 1], retention_matrix, 'Native-Retention\n(Φ nach/vor Invasion)', 'Blues'),
        (axes[0, 2], repulsion_matrix, 'Invasor-Repulsion\n(größer ist besser)', 'magma'),
        (axes[1, 0], divergence_matrix, 'Reputations-Divergenz', 'PuBuGn'),
        (axes[1, 1], rewiring_matrix, 'Ø Rewiring pro Runde', 'Oranges'),
        (axes[1, 2], invader_edge_matrix, 'Invasor-Kantenanteil\n(kleiner ist besser)', 'magma_r'),
    ]

    for axis, matrix, title, cmap in heatmaps:
        image = axis.imshow(matrix, cmap=cmap, aspect='auto')
        axis.set_title(title)
        axis.set_xlabel('Proximity-Gewicht')
        axis.set_ylabel('Reputations-Schwelle')
        axis.set_xticks(range(len(proximity_weights)))
        axis.set_xticklabels([f'{value:.2f}' for value in proximity_weights])
        axis.set_yticks(range(len(rep_thresholds)))
        axis.set_yticklabels([f'{value:.2f}' for value in rep_thresholds])

        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                axis.text(col, row, f'{matrix[row, col]:.2f}', ha='center', va='center', fontsize=9)

        if title.startswith('Resilienz'):
            best_row = rep_thresholds.index(best_setting['rep_threshold'])
            best_col = proximity_weights.index(best_setting['proximity_weight'])
            axis.scatter(best_col, best_row, s=140, facecolors='none', edgecolors='white', linewidths=2)

        fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)

    fig.text(
        0.5,
        0.02,
        (
            f"Statisches Basisnetz: Score={baseline['resilience_score']:+.3f}, "
            f"Retention={baseline['resilience_ratio']:.3f}, "
            f"Repulsion={baseline['repulsion_index']:+.3f}, "
            f"Invader-Kanten={baseline['final_invader_edge_share']:.1%}"
        ),
        ha='center',
        fontsize=10,
    )
    plt.tight_layout(rect=(0, 0.04, 1, 0.98))
    save_and_maybe_show(plt, 'kki_invasive_netzwerke.png', dpi=150)


if __name__ == '__main__':
    main()
