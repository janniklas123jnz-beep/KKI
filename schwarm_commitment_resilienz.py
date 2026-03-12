"""
KKI Adaptive Netzwerke gegen Commitment-Angriffe
================================================
Vergleicht statische und adaptive Netzwerke unter gezielten Manipulations-
versuchen, die durch Commitment-Verifikation erkannt werden.
"""

from __future__ import annotations

import os
import random
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from kki_commitment import Commitment
from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_polarisierung import berechne_netzwerkmetriken

DEFAULT_NATIVE_AGENT_COUNT = 50
DEFAULT_ATTACKER_COUNT = 8
DEFAULT_TOTAL_ROUNDS = 180
DEFAULT_ATTACK_ROUND = 90
DEFAULT_CONNECTIONS_PER_AGENT = 8
DEFAULT_INTERACTIONS_PER_ROUND = 90


class Agent:
    """Agent fuer Commitment-Angriffs- und Abwehrszenarien."""

    def __init__(
        self,
        agent_id: int,
        gruppe: int,
        meinung: float,
        kooperations_neigung: float,
        *,
        ist_manipulator: bool = False,
        hartnaeckigkeit: float = 0.0,
    ):
        self.id = agent_id
        self.gruppe = gruppe
        self.meinung = meinung
        self.kooperations_neigung = kooperations_neigung
        self.ist_manipulator = ist_manipulator
        self.hartnaeckigkeit = hartnaeckigkeit
        self.intelligenz = 1.0 if not ist_manipulator else 0.88
        self.reputation = 0.5 if not ist_manipulator else 0.35
        self.commitment_integritaet = 1.0 if not ist_manipulator else 0.75
        self.nachbarn = set()
        self.interaktions_history = defaultdict(list)
        self.commitment_history = defaultdict(list)
        self.geboren_runde = 0
        self.manipulations_versuche = 0
        self.erkannte_brueche = 0
        self.erfolgreiche_manipulationen = 0

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

    def berechne_partner_commitment_trust(self, partner_id):
        history = self.commitment_history.get(partner_id, [])
        if not history:
            return 1.0
        return sum(1 for status in history[-10:] if status) / len(history[-10:])

    def plane_aktion(self, partner_vertrauen: float):
        effektive_neigung = self.kooperations_neigung * (0.55 + 0.45 * partner_vertrauen)
        effektive_neigung = max(0.03, min(0.97, effektive_neigung))
        aktion = 'C' if random.random() < effektive_neigung else 'D'
        return aktion, Commitment.erstelle(aktion)

    def fuehre_commitment_aus(self, geplante_aktion, commitment, attack_strength):
        manipulationsversuch = False
        finale_aktion = geplante_aktion

        if self.ist_manipulator and random.random() < attack_strength:
            manipulationsversuch = True
            self.manipulations_versuche += 1
            finale_aktion = 'D' if geplante_aktion == 'C' else 'C'

        commitment_ok = commitment.verifiziere(finale_aktion)
        if manipulationsversuch and commitment_ok:
            self.erfolgreiche_manipulationen += 1
        if manipulationsversuch and not commitment_ok:
            self.erkannte_brueche += 1
        return finale_aktion, commitment_ok, manipulationsversuch

    def lerne(
        self,
        meine_aktion,
        andere_aktion,
        partner_id,
        partner_intelligenz,
        partner_meinung,
        ich_wurde_erwischt,
        partner_wurde_erwischt,
    ):
        self.interaktions_history[partner_id].append(andere_aktion)
        self.commitment_history[partner_id].append(not partner_wurde_erwischt)
        meinungs_distanz = abs(self.meinung - partner_meinung)
        aehnlichkeit = 1.0 - meinungs_distanz
        beweglichkeit = 1.0 - self.hartnaeckigkeit

        if ich_wurde_erwischt:
            self.intelligenz *= 0.82
            self.reputation -= 0.18
            self.commitment_integritaet *= 0.55
            self.kooperations_neigung += 0.03

        if meine_aktion == 'C' and andere_aktion == 'C' and not ich_wurde_erwischt:
            self.intelligenz *= 1.003 + 0.002 * aehnlichkeit + 0.001 * min(partner_intelligenz, 4.0)
            self.kooperations_neigung += 0.004
            self.reputation += 0.010
            self.commitment_integritaet += 0.010
            self.meinung += (partner_meinung - self.meinung) * 0.07 * beweglichkeit
        elif meine_aktion == 'C' and andere_aktion == 'D' and not ich_wurde_erwischt:
            self.kooperations_neigung -= 0.004
            self.reputation += 0.002
            self.commitment_integritaet -= 0.015 if partner_wurde_erwischt else 0.005
        elif meine_aktion == 'D' and andere_aktion == 'C' and not ich_wurde_erwischt:
            self.intelligenz *= 0.996
            self.reputation -= 0.020
            self.commitment_integritaet -= 0.010
        elif meine_aktion == 'D' and andere_aktion == 'D' and not ich_wurde_erwischt:
            self.intelligenz *= 0.991
            self.reputation -= 0.010
            self.commitment_integritaet -= 0.008
            self.kooperations_neigung += 0.002

        if partner_wurde_erwischt:
            self.reputation += 0.005

        self.kooperations_neigung = max(0.03, min(0.97, self.kooperations_neigung))
        self.intelligenz = max(0.1, min(8.0, self.intelligenz))
        self.reputation = max(0.0, min(1.0, self.reputation))
        self.commitment_integritaet = max(0.0, min(1.0, self.commitment_integritaet))
        self.meinung = max(0.0, min(1.0, self.meinung))


def parse_float_grid(name: str, default_values):
    raw = os.getenv(name)
    if not raw:
        return list(default_values)
    return [float(value.strip()) for value in raw.split(',') if value.strip()]


def studienparameter():
    if is_test_mode():
        rep_thresholds = parse_float_grid('KKI_COMMITMENT_REP_THRESHOLDS', [0.25, 0.40])
        trust_thresholds = parse_float_grid('KKI_COMMITMENT_TRUST_THRESHOLDS', [0.55, 0.75])
        repetitions = int(os.getenv('KKI_COMMITMENT_REPETITIONS', '2'))
        rounds = min(DEFAULT_TOTAL_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        rep_thresholds = parse_float_grid('KKI_COMMITMENT_REP_THRESHOLDS', [0.25, 0.35, 0.45, 0.55])
        trust_thresholds = parse_float_grid('KKI_COMMITMENT_TRUST_THRESHOLDS', [0.55, 0.70, 0.85, 0.95])
        repetitions = int(os.getenv('KKI_COMMITMENT_REPETITIONS', '3'))
        rounds = DEFAULT_TOTAL_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_COMMITMENT_ATTACK_ROUND', str(DEFAULT_ATTACK_ROUND)))

    return {
        'rep_thresholds': rep_thresholds,
        'trust_thresholds': trust_thresholds,
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'native_count': int(os.getenv('KKI_NATIVE_AGENT_COUNT', str(DEFAULT_NATIVE_AGENT_COUNT))),
        'attacker_count': int(os.getenv('KKI_ATTACKER_AGENT_COUNT', str(DEFAULT_ATTACKER_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'attack_strength': float(os.getenv('KKI_COMMITMENT_ATTACK_STRENGTH', '0.45')),
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
        hartnaeckigkeit = 0.08 if index % 10 == 0 else 0.04
        meinung = max(0.0, min(1.0, random.gauss(basis_meinung, 0.05)))
        agenten.append(Agent(index, gruppe, meinung, kooperation, hartnaeckigkeit=hartnaeckigkeit))
    return agenten


def erstelle_basisnetz(agenten, degree):
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
        if random.random() < 0.25:
            andere = [ziel for ziel in agenten if ziel.gruppe != agent.gruppe and ziel.id != agent.id]
            if andere:
                agent.verbinde(random.choice(andere))


def fuege_manipulatoren_hinzu(agenten, agenten_dict, config, runde):
    start_id = max(agent.id for agent in agenten) + 1
    manipulatoren = []
    for offset in range(int(config['attacker_count'])):
        meinung = max(0.0, min(1.0, random.gauss(0.78, 0.05)))
        manipulator = Agent(
            start_id + offset,
            2,
            meinung,
            0.22,
            ist_manipulator=True,
            hartnaeckigkeit=0.30,
        )
        manipulator.geboren_runde = runde
        manipulatoren.append(manipulator)
        agenten.append(manipulator)
        agenten_dict[manipulator.id] = manipulator

    degree = int(config['degree'])
    native_agenten = [agent for agent in agenten if not agent.ist_manipulator]
    for manipulator in manipulatoren:
        ziele = random.sample(native_agenten, min(degree, len(native_agenten)))
        for ziel in ziele:
            manipulator.verbinde(ziel)
    return manipulatoren


def waehle_partner(agent, aktive_agenten, agenten_dict):
    if agent.nachbarn and random.random() < 0.9:
        gueltige = [nachbar_id for nachbar_id in agent.nachbarn if nachbar_id in agenten_dict]
        if gueltige:
            return agenten_dict[random.choice(gueltige)]
    kandidaten = [anderer for anderer in aktive_agenten if anderer.id != agent.id]
    return random.choice(kandidaten)


def commitment_kantenanteil(agenten):
    kanten = set()
    manipulator_kanten = 0
    agenten_dict = {agent.id: agent for agent in agenten}
    for agent in agenten:
        for nachbar_id in agent.nachbarn:
            kante = tuple(sorted((agent.id, nachbar_id)))
            if kante in kanten:
                continue
            kanten.add(kante)
            if agent.ist_manipulator or agenten_dict[nachbar_id].ist_manipulator:
                manipulator_kanten += 1
    return manipulator_kanten / len(kanten) if kanten else 0.0


def finde_neuen_commitment_nachbarn(agent, agenten, config):
    trust_threshold = float(config['trust_threshold'])
    bester_score = None
    beste_kandidaten = []

    for kandidat in agenten:
        if kandidat.id == agent.id or kandidat.id in agent.nachbarn:
            continue
        if kandidat.commitment_integritaet < trust_threshold - 0.10:
            continue

        aehnlichkeit = 1.0 - abs(agent.meinung - kandidat.meinung)
        score = 0.45 * kandidat.commitment_integritaet + 0.35 * kandidat.reputation + 0.20 * aehnlichkeit
        if kandidat.gruppe == agent.gruppe:
            score += 0.03

        if bester_score is None or score > bester_score + 1e-9:
            bester_score = score
            beste_kandidaten = [kandidat]
        elif abs(score - bester_score) <= 1e-9:
            beste_kandidaten.append(kandidat)

    if not beste_kandidaten:
        return None
    return random.choice(beste_kandidaten)


def aktualisiere_commitment_netzwerk(agenten, config):
    if not config.get('adaptive_enabled'):
        return {'rewired_edges': 0}

    rep_threshold = float(config['rep_threshold'])
    trust_threshold = float(config['trust_threshold'])
    target_degree = int(config['degree'])
    removed_edges = 0
    added_edges = 0
    agenten_dict = {agent.id: agent for agent in agenten}

    for agent in agenten:
        zu_trennen = []
        for nachbar_id in list(agent.nachbarn):
            history_len = len(agent.interaktions_history.get(nachbar_id, []))
            if history_len < 2:
                continue
            partner = agenten_dict[nachbar_id]
            partner_rep = agent.berechne_partner_reputation(nachbar_id)
            partner_trust = agent.berechne_partner_commitment_trust(nachbar_id)
            if (
                partner_rep < rep_threshold
                or partner_trust < trust_threshold
                or partner.commitment_integritaet < trust_threshold
            ):
                zu_trennen.append(partner)

        for partner in zu_trennen:
            if partner.id not in agent.nachbarn:
                continue
            agent.trenne(partner)
            removed_edges += 1

    for agent in agenten:
        if len(agent.nachbarn) >= target_degree:
            continue
        versuche = 0
        while len(agent.nachbarn) < target_degree and versuche < 2:
            versuche += 1
            kandidat = finde_neuen_commitment_nachbarn(agent, agenten, config)
            if kandidat is None or kandidat.id in agent.nachbarn:
                break
            agent.verbinde(kandidat)
            added_edges += 1

    return {'rewired_edges': removed_edges + added_edges}


def run_commitment_experiment(config, *, adaptive_enabled, rep_threshold, trust_threshold):
    agenten = erstelle_native_agenten(int(config['native_count']))
    agenten_dict = {agent.id: agent for agent in agenten}
    erstelle_basisnetz(agenten, int(config['degree']))

    total_rounds = int(config['rounds'])
    attack_round = int(config['attack_round'])
    interactions_per_round = int(config['interactions'])
    manipulatoren = []
    pre_attack_native_phi = None
    native_phi_history = []
    manipulator_phi_history = []
    native_integrity_history = []
    manipulator_integrity_history = []
    rewiring_history = []
    manipulator_edge_history = []
    detection_rate_history = []
    density_history = []

    experiment_config = {
        'adaptive_enabled': adaptive_enabled,
        'rep_threshold': rep_threshold,
        'trust_threshold': trust_threshold,
        'degree': int(config['degree']),
    }

    for runde in range(1, total_rounds + 1):
        if runde == attack_round:
            manipulatoren = fuege_manipulatoren_hinzu(agenten, agenten_dict, config, runde)
            pre_attack_native_phi = mittelwert([agent.intelligenz for agent in agenten if not agent.ist_manipulator])

        aktive_agenten = [agent for agent in agenten if agent.geboren_runde <= runde]
        versuche_runde = 0
        detections_runde = 0

        for _ in range(interactions_per_round):
            if len(aktive_agenten) < 2:
                continue

            a1 = random.choice(aktive_agenten)
            a2 = waehle_partner(a1, aktive_agenten, agenten_dict)

            vertrauen12 = 0.5 * a1.berechne_partner_reputation(a2.id) + 0.5 * a1.berechne_partner_commitment_trust(a2.id)
            vertrauen21 = 0.5 * a2.berechne_partner_reputation(a1.id) + 0.5 * a2.berechne_partner_commitment_trust(a1.id)

            aktion1_geplant, commitment1 = a1.plane_aktion(vertrauen12)
            aktion2_geplant, commitment2 = a2.plane_aktion(vertrauen21)

            attack_strength = float(config['attack_strength']) if runde >= attack_round else 0.0
            aktion1_final, a1_ok, a1_attack = a1.fuehre_commitment_aus(aktion1_geplant, commitment1, attack_strength)
            aktion2_final, a2_ok, a2_attack = a2.fuehre_commitment_aus(aktion2_geplant, commitment2, attack_strength)

            versuche_runde += int(a1_attack) + int(a2_attack)
            detections_runde += int(a1_attack and not a1_ok) + int(a2_attack and not a2_ok)

            a1.lerne(aktion1_final, aktion2_final, a2.id, a2.intelligenz, a2.meinung, not a1_ok, not a2_ok)
            a2.lerne(aktion2_final, aktion1_final, a1.id, a1.intelligenz, a1.meinung, not a2_ok, not a1_ok)

        rewiring_stats = {'rewired_edges': 0}
        if manipulatoren and adaptive_enabled and runde >= attack_round:
            rewiring_stats = aktualisiere_commitment_netzwerk(agenten, experiment_config)

        native_agents = [agent for agent in agenten if not agent.ist_manipulator]
        active_manipulators = [agent for agent in manipulatoren if agent.geboren_runde <= runde]
        metrics = berechne_netzwerkmetriken(agenten, agenten_dict)

        native_phi_history.append(mittelwert([agent.intelligenz for agent in native_agents]))
        manipulator_phi_history.append(mittelwert([agent.intelligenz for agent in active_manipulators]))
        native_integrity_history.append(mittelwert([agent.commitment_integritaet for agent in native_agents]))
        manipulator_integrity_history.append(mittelwert([agent.commitment_integritaet for agent in active_manipulators]))
        rewiring_history.append(rewiring_stats['rewired_edges'])
        manipulator_edge_history.append(commitment_kantenanteil(agenten))
        detection_rate_history.append(detections_runde / max(1, versuche_runde) if versuche_runde else 1.0)
        density_history.append(metrics['density'])

    native_final_phi = native_phi_history[-1]
    manipulator_final_phi = manipulator_phi_history[-1] if manipulator_phi_history else 0.0
    native_final_integrity = native_integrity_history[-1]
    manipulator_final_integrity = manipulator_integrity_history[-1] if manipulator_integrity_history else 0.0
    pre_attack_native_phi = pre_attack_native_phi if pre_attack_native_phi is not None else native_phi_history[0]
    native_retention = native_final_phi / pre_attack_native_phi if pre_attack_native_phi else 0.0
    detection_rate = mittelwert(detection_rate_history[attack_round - 1 :]) if manipulatoren else 1.0
    attack_success_rate = 1.0 - detection_rate
    edge_share = manipulator_edge_history[-1]
    commitment_divergence = native_final_integrity - manipulator_final_integrity
    average_rewiring = mittelwert(rewiring_history[attack_round - 1 :]) if manipulatoren else 0.0
    resilience_score = native_retention + detection_rate + commitment_divergence + (1.0 - edge_share) - manipulator_final_phi

    return {
        'native_retention': native_retention,
        'detection_rate': detection_rate,
        'attack_success_rate': attack_success_rate,
        'commitment_divergence': commitment_divergence,
        'manipulator_edge_share': edge_share,
        'average_rewiring': average_rewiring,
        'native_final_phi': native_final_phi,
        'manipulator_final_phi': manipulator_final_phi,
        'resilience_score': resilience_score,
        'native_phi_history': native_phi_history,
        'manipulator_phi_history': manipulator_phi_history,
        'native_integrity_history': native_integrity_history,
        'manipulator_integrity_history': manipulator_integrity_history,
        'rewiring_history': rewiring_history,
        'manipulator_edge_history': manipulator_edge_history,
        'density_history': density_history,
    }


def run_once(seed, params, *, adaptive_enabled, rep_threshold=None, trust_threshold=None):
    random.seed(seed)
    np.random.seed(seed)
    return run_commitment_experiment(
        params,
        adaptive_enabled=adaptive_enabled,
        rep_threshold=0.35 if rep_threshold is None else rep_threshold,
        trust_threshold=0.75 if trust_threshold is None else trust_threshold,
    )


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print("=" * 84)
    print("KKI COMMITMENT-RESILIENZ IN ADAPTIVEN NETZWERKEN")
    print("=" * 84)
    print(
        f"Seed-Basis: {base_seed} | Runden: {params['rounds']} | "
        f"Angriff ab Runde {params['attack_round']}"
    )
    print(
        f"Basisnetz: Agenten={params['native_count']} + Manipulatoren={params['attacker_count']}, "
        f"Grad={params['degree']} | Angriffsstärke={params['attack_strength']:.2f}"
    )
    print(
        f"Rep-Schwellen: {params['rep_thresholds']} | "
        f"Commitment-Schwellen: {params['trust_thresholds']} | "
        f"Wiederholungen: {params['repetitions']}"
    )
    print("\nStudie läuft...\n")

    baseline_runs = []
    for repetition in range(params['repetitions']):
        baseline_runs.append(run_once(base_seed + repetition, params, adaptive_enabled=False))

    baseline = {
        'resilience_score': mittelwert([run['resilience_score'] for run in baseline_runs]),
        'native_retention': mittelwert([run['native_retention'] for run in baseline_runs]),
        'detection_rate': mittelwert([run['detection_rate'] for run in baseline_runs]),
        'commitment_divergence': mittelwert([run['commitment_divergence'] for run in baseline_runs]),
        'manipulator_edge_share': mittelwert([run['manipulator_edge_share'] for run in baseline_runs]),
    }
    print(
        "Statisches Basisnetz:\n"
        f"  Resilienz-Score:         {baseline['resilience_score']:+.3f}\n"
        f"  Native-Retention:        {baseline['native_retention']:.3f}\n"
        f"  Erkennungsrate:          {baseline['detection_rate']:.1%}\n"
        f"  Commitment-Divergenz:    {baseline['commitment_divergence']:+.3f}\n"
        f"  Manipulator-Kantenanteil:{baseline['manipulator_edge_share']:.1%}\n"
    )

    rep_thresholds = params['rep_thresholds']
    trust_thresholds = params['trust_thresholds']
    shape = (len(rep_thresholds), len(trust_thresholds))
    resilience_matrix = np.zeros(shape)
    retention_matrix = np.zeros(shape)
    divergence_matrix = np.zeros(shape)
    rewiring_matrix = np.zeros(shape)
    edge_share_matrix = np.zeros(shape)
    detection_matrix = np.zeros(shape)
    best_score = None
    best_setting = None

    for row, rep_threshold in enumerate(rep_thresholds):
        for col, trust_threshold in enumerate(trust_thresholds):
            runs = []
            for repetition in range(params['repetitions']):
                seed = base_seed + row * 100 + col * 10 + repetition
                runs.append(
                    run_once(
                        seed,
                        params,
                        adaptive_enabled=True,
                        rep_threshold=rep_threshold,
                        trust_threshold=trust_threshold,
                    )
                )

            resilience_matrix[row, col] = mittelwert([run['resilience_score'] for run in runs])
            retention_matrix[row, col] = mittelwert([run['native_retention'] for run in runs])
            divergence_matrix[row, col] = mittelwert([run['commitment_divergence'] for run in runs])
            rewiring_matrix[row, col] = mittelwert([run['average_rewiring'] for run in runs])
            edge_share_matrix[row, col] = mittelwert([run['manipulator_edge_share'] for run in runs])
            detection_matrix[row, col] = mittelwert([run['detection_rate'] for run in runs])

            print(
                f"Rep={rep_threshold:.2f}, Commitment={trust_threshold:.2f} -> "
                f"Score={resilience_matrix[row, col]:+.3f}, "
                f"Retention={retention_matrix[row, col]:.3f}, "
                f"Divergenz={divergence_matrix[row, col]:+.3f}, "
                f"Manipulator-Kanten={edge_share_matrix[row, col]:.1%}"
            )

            if best_score is None or resilience_matrix[row, col] > best_score:
                best_score = resilience_matrix[row, col]
                best_setting = {
                    'rep_threshold': rep_threshold,
                    'trust_threshold': trust_threshold,
                    'resilience_score': resilience_matrix[row, col],
                    'retention': retention_matrix[row, col],
                    'divergence': divergence_matrix[row, col],
                    'rewiring': rewiring_matrix[row, col],
                    'edge_share': edge_share_matrix[row, col],
                    'detection_rate': detection_matrix[row, col],
                }

    print("\n" + "=" * 84)
    print("ERGEBNISSE")
    print("=" * 84)
    print(
        "Beste adaptive Commitment-Abwehr:\n"
        f"  Reputations-Schwelle:   {best_setting['rep_threshold']:.2f}\n"
        f"  Commitment-Schwelle:    {best_setting['trust_threshold']:.2f}\n"
        f"  Resilienz-Score:        {best_setting['resilience_score']:+.3f}\n"
        f"  Native-Retention:       {best_setting['retention']:.3f}\n"
        f"  Erkennungsrate:         {best_setting['detection_rate']:.1%}\n"
        f"  Commitment-Divergenz:   {best_setting['divergence']:+.3f}\n"
        f"  Manipulator-Kantenanteil:{best_setting['edge_share']:.1%}\n"
        f"  Ø Rewiring/Runde:       {best_setting['rewiring']:.2f}"
    )
    print(
        "\nDelta zum statischen Basisnetz:\n"
        f"  Δ Resilienz:      {best_setting['resilience_score'] - baseline['resilience_score']:+.3f}\n"
        f"  Δ Retention:      {best_setting['retention'] - baseline['native_retention']:+.3f}\n"
        f"  Δ Divergenz:      {best_setting['divergence'] - baseline['commitment_divergence']:+.3f}\n"
        f"  Δ Kantenanteil:   {best_setting['edge_share'] - baseline['manipulator_edge_share']:+.3f}"
    )

    fig, axes = plt.subplots(2, 3, figsize=(17, 11))
    fig.suptitle(
        'KKI Adaptive Netzwerke gegen Commitment-Angriffe',
        fontsize=14,
        fontweight='bold',
    )

    heatmaps = [
        (axes[0, 0], resilience_matrix, 'Resilienz-Score\n(größer ist besser)', 'viridis'),
        (axes[0, 1], retention_matrix, 'Native-Retention', 'Blues'),
        (axes[0, 2], divergence_matrix, 'Commitment-Divergenz', 'PuBuGn'),
        (axes[1, 0], detection_matrix, 'Erkennungsrate', 'Greens'),
        (axes[1, 1], rewiring_matrix, 'Ø Rewiring pro Runde', 'Oranges'),
        (axes[1, 2], edge_share_matrix, 'Manipulator-Kantenanteil\n(kleiner ist besser)', 'magma_r'),
    ]

    for axis, matrix, title, cmap in heatmaps:
        image = axis.imshow(matrix, cmap=cmap, aspect='auto')
        axis.set_title(title)
        axis.set_xlabel('Commitment-Schwelle')
        axis.set_ylabel('Reputations-Schwelle')
        axis.set_xticks(range(len(trust_thresholds)))
        axis.set_xticklabels([f'{value:.2f}' for value in trust_thresholds])
        axis.set_yticks(range(len(rep_thresholds)))
        axis.set_yticklabels([f'{value:.2f}' for value in rep_thresholds])

        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                axis.text(col, row, f'{matrix[row, col]:.2f}', ha='center', va='center', fontsize=9)

        if title.startswith('Resilienz'):
            best_row = rep_thresholds.index(best_setting['rep_threshold'])
            best_col = trust_thresholds.index(best_setting['trust_threshold'])
            axis.scatter(best_col, best_row, s=140, facecolors='none', edgecolors='white', linewidths=2)

        fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)

    fig.text(
        0.5,
        0.02,
        (
            f"Statisches Basisnetz: Score={baseline['resilience_score']:+.3f}, "
            f"Retention={baseline['native_retention']:.3f}, "
            f"Erkennung={baseline['detection_rate']:.1%}, "
            f"Manipulator-Kanten={baseline['manipulator_edge_share']:.1%}"
        ),
        ha='center',
        fontsize=10,
    )
    plt.tight_layout(rect=(0, 0.04, 1, 0.98))
    save_and_maybe_show(plt, 'kki_commitment_resilienz.png', dpi=150)


if __name__ == '__main__':
    main()
