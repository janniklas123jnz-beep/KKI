"""
KKI Polarisierungs-Experiment: Konsensbildung und Lagerbildung im Schwarm
=========================================================================
Untersucht, wie sich Meinungen, Kooperation und Gruppenbildung in einem
Netzwerk-Schwarm gegenseitig beeinflussen.
"""

from __future__ import annotations

import os
import random
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import configure_simulation, save_and_maybe_show

DEFAULT_AGENT_COUNT = 60
DEFAULT_ROUNDS = 180
DEFAULT_CONNECTIONS_PER_AGENT = 6
DEFAULT_INTERACTIONS_PER_ROUND = 90
DEFAULT_RANDOM_EDGE_CHANCE = 0.1
VALID_SCENARIOS = {'polarization', 'consensus'}
DEFAULT_REWIRE_MIN_INTERACTIONS = 3
DEFAULT_REWIRE_REPUTATION_THRESHOLD = 0.35
DEFAULT_REWIRE_OPINION_DISTANCE_THRESHOLD = 0.55
DEFAULT_REWIRE_PROXIMITY_WEIGHT = 0.45
DEFAULT_REWIRE_REMOVAL_PROBABILITY = 0.35
DEFAULT_REWIRE_ADDITION_PROBABILITY = 0.75
DEFAULT_REWIRE_CROSS_GROUP_BONUS = 0.08
DEFAULT_CENTER_MIN = 0.35
DEFAULT_CENTER_MAX = 0.65
DEFAULT_GENERALIST_SHARE = 0.55
DEFAULT_CONNECTOR_SHARE = 0.25
DEFAULT_SENTINEL_SHARE = 0.20
DEFAULT_MEDIATOR_SHARE = 0.0
DEFAULT_ANALYZER_SHARE = 0.0
DEFAULT_CONNECTOR_BONUS = 0.10
DEFAULT_SENTINEL_REP_THRESHOLD = 0.45
DEFAULT_SENTINEL_COOPERATION_PENALTY = 0.06
DEFAULT_CONNECTOR_CROSS_GROUP_LEARNING = 0.15
DEFAULT_SENTINEL_REPUTATION_LEARNING = 1.20
DEFAULT_MEDIATOR_BONUS = 0.06
DEFAULT_MEDIATOR_CONTACT_BIAS = 0.70
DEFAULT_MEDIATOR_OPINION_DISTANCE = 0.25
DEFAULT_ANALYZER_MEMORY_WINDOW = 15
DEFAULT_ANALYZER_LEARNING_MULTIPLIER = 1.10
DEFAULT_ROLE_SWITCH_INTERVAL = 20
DEFAULT_ROLE_SWITCH_MIN_TENURE = 20
DEFAULT_ROLE_SWITCH_REPUTATION_COST = 0.02


class Agent:
    """Agent mit Meinung, Kooperationsneigung und Netzwerkbeziehungen."""

    def __init__(self, agent_id, gruppe, meinung, kooperations_neigung, hartnaeckigkeit=0.0):
        self.id = agent_id
        self.gruppe = gruppe
        self.name = f"G{gruppe + 1}-A{agent_id}"
        self.meinung = meinung
        self.kooperations_neigung = kooperations_neigung
        self.hartnaeckigkeit = hartnaeckigkeit
        self.intelligenz = 1.0
        self.reputation = 0.5
        self.nachbarn = set()
        self.interaktions_history = defaultdict(list)
        self.role = 'generalist'
        self.bridge_bonus = 0.0
        self.rewire_reputation_threshold = None
        self.cooperation_penalty_threshold = None
        self.cooperation_penalty = 0.0
        self.intelligence_learning_multiplier = 1.0
        self.cooperation_learning_multiplier = 1.0
        self.reputation_learning_multiplier = 1.0
        self.opinion_learning_multiplier = 1.0
        self.cross_group_learning_bonus = 0.0
        self.memory_window = 10
        self.partner_bias_probability = 0.0
        self.partner_bias_min_distance = 0.0
        self.role_tenure = 0
        self.initial_role = 'generalist'
        self.role_transition_history = []

        self.meinung_history = [meinung]
        self.kooperation_history = [kooperations_neigung]
        self.intelligenz_history = [1.0]

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
        fenster = history[-self.memory_window :]
        return sum(1 for aktion in fenster if aktion == 'C') / len(fenster)

    def waehle_aktion(self, partner_reputation, partner_meinung, cooperation_bonus=0.0):
        meinungs_distanz = abs(self.meinung - partner_meinung)
        aehnlichkeit = 1.0 - meinungs_distanz
        effektive_neigung = self.kooperations_neigung
        effektive_neigung *= 0.55 + 0.45 * partner_reputation
        effektive_neigung *= 0.35 + 0.65 * aehnlichkeit
        if (
            self.cooperation_penalty_threshold is not None
            and partner_reputation < self.cooperation_penalty_threshold
        ):
            effektive_neigung -= self.cooperation_penalty
        effektive_neigung += cooperation_bonus
        effektive_neigung = max(0.05, min(0.95, effektive_neigung))

        if random.random() < effektive_neigung:
            return 'C'
        return 'D'

    def lerne(
        self,
        meine_aktion,
        andere_aktion,
        partner_id,
        partner_intelligenz,
        partner_meinung,
        gleiche_gruppe,
        opinion_pull=0.0,
    ):
        self.interaktions_history[partner_id].append(andere_aktion)
        meinungs_distanz = abs(self.meinung - partner_meinung)
        aehnlichkeit = 1.0 - meinungs_distanz
        beweglichkeit = 1.0 - self.hartnaeckigkeit
        learning_factor = self.intelligence_learning_multiplier
        cooperation_factor = self.cooperation_learning_multiplier
        reputation_factor = self.reputation_learning_multiplier
        opinion_factor = self.opinion_learning_multiplier
        if not gleiche_gruppe:
            learning_factor *= 1.0 + self.cross_group_learning_bonus

        if meine_aktion == 'C' and andere_aktion == 'C':
            self.intelligenz *= 1.0 + (
                (1.002 + 0.002 * aehnlichkeit + 0.001 * min(partner_intelligenz, 4.0)) - 1.0
            ) * learning_factor
            self.kooperations_neigung += 0.006 * cooperation_factor * (0.5 + aehnlichkeit)
            self.reputation += 0.012 * reputation_factor
            zugkraft = 0.12 if gleiche_gruppe else 0.08
            zugkraft = (zugkraft + opinion_pull) * opinion_factor
            self.meinung += (partner_meinung - self.meinung) * zugkraft * beweglichkeit

        elif meine_aktion == 'C' and andere_aktion == 'D':
            self.kooperations_neigung -= 0.004 * cooperation_factor
            self.reputation += 0.004 * reputation_factor
            if meinungs_distanz > 0.3:
                self.meinung += (self.meinung - partner_meinung) * 0.03 * opinion_factor * beweglichkeit

        elif meine_aktion == 'D' and andere_aktion == 'C':
            self.intelligenz *= 1.0 - (1.0 - 0.997) * learning_factor
            self.reputation -= 0.02 * reputation_factor
            if meinungs_distanz > 0.25:
                self.meinung += (self.meinung - partner_meinung) * 0.025 * opinion_factor * beweglichkeit

        elif meine_aktion == 'D' and andere_aktion == 'D':
            self.intelligenz *= 1.0 - (1.0 - 0.991) * learning_factor
            self.reputation -= 0.01 * reputation_factor
            self.kooperations_neigung += 0.002 * cooperation_factor
            if meinungs_distanz > 0.2:
                self.meinung += (self.meinung - partner_meinung) * 0.02 * opinion_factor * beweglichkeit

        self.kooperations_neigung = max(0.05, min(0.95, self.kooperations_neigung))
        self.intelligenz = max(0.1, min(6.0, self.intelligenz))
        self.reputation = max(0.0, min(1.0, self.reputation))
        self.meinung = max(0.0, min(1.0, self.meinung))

    def runde_beenden(self):
        self.meinung_history.append(self.meinung)
        self.kooperation_history.append(self.kooperations_neigung)
        self.intelligenz_history.append(self.intelligenz)


def resolve_scenario(name: str) -> str:
    scenario = name.strip().lower()
    if scenario not in VALID_SCENARIOS:
        raise ValueError(f"Unbekanntes Szenario '{name}'. Erlaubt: {', '.join(sorted(VALID_SCENARIOS))}")
    return scenario


def scenario_title(scenario: str) -> str:
    return 'KONSENS-SZENARIO' if scenario == 'consensus' else 'POLARISIERUNGS-SZENARIO'


def default_cross_group_chance(scenario: str) -> float:
    return 0.35 if scenario == 'consensus' else 0.08


def build_runtime_config() -> tuple[dict[str, float | int | str], int]:
    rounds_config, seed = configure_simulation(
        {
            'RUNDEN': DEFAULT_ROUNDS,
            'INTERAKTIONEN_PRO_RUNDE': DEFAULT_INTERACTIONS_PER_ROUND,
        },
        np_module=np,
        plt_module=plt,
    )

    scenario = resolve_scenario(os.getenv('KKI_POLARIZATION_SCENARIO', 'polarization'))
    rewiring_enabled = os.getenv('KKI_REWIRING_ENABLED', '').strip().lower() in {'1', 'true', 'yes', 'on'}
    target_degree = int(os.getenv('KKI_REWIRE_TARGET_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT)))
    config = {
        'scenario': scenario,
        'agent_count': int(os.getenv('KKI_POLARIZATION_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'rounds': rounds_config['RUNDEN'],
        'interactions_per_round': rounds_config['INTERAKTIONEN_PRO_RUNDE'],
        'connections_per_agent': int(
            os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))
        ),
        'cross_group_chance': float(
            os.getenv('KKI_CROSS_GROUP_CHANCE', str(default_cross_group_chance(scenario)))
        ),
        'random_edge_chance': float(
            os.getenv('KKI_RANDOM_EDGE_CHANCE', str(DEFAULT_RANDOM_EDGE_CHANCE))
        ),
        'enable_dynamic_rewiring': rewiring_enabled,
        'rewire_min_interactions': int(
            os.getenv('KKI_REWIRE_MIN_INTERACTIONS', str(DEFAULT_REWIRE_MIN_INTERACTIONS))
        ),
        'rewire_reputation_threshold': float(
            os.getenv('KKI_REWIRE_REP_THRESHOLD', str(DEFAULT_REWIRE_REPUTATION_THRESHOLD))
        ),
        'rewire_opinion_distance_threshold': float(
            os.getenv('KKI_REWIRE_OPINION_THRESHOLD', str(DEFAULT_REWIRE_OPINION_DISTANCE_THRESHOLD))
        ),
        'rewire_proximity_weight': float(
            os.getenv('KKI_REWIRE_PROXIMITY_WEIGHT', str(DEFAULT_REWIRE_PROXIMITY_WEIGHT))
        ),
        'rewire_removal_probability': float(
            os.getenv('KKI_REWIRE_REMOVAL_PROB', str(DEFAULT_REWIRE_REMOVAL_PROBABILITY))
        ),
        'rewire_addition_probability': float(
            os.getenv('KKI_REWIRE_ADDITION_PROB', str(DEFAULT_REWIRE_ADDITION_PROBABILITY))
        ),
        'rewire_cross_group_bonus': float(
            os.getenv('KKI_REWIRE_CROSS_GROUP_BONUS', str(DEFAULT_REWIRE_CROSS_GROUP_BONUS))
        ),
        'rewire_target_degree': target_degree,
        'enable_bridge_mechanism': os.getenv('KKI_BRIDGE_MECHANISM', '').strip().lower() in {'1', 'true', 'yes', 'on'},
        'bridge_cooperation_bonus': float(os.getenv('KKI_BRIDGE_COOPERATION_BONUS', '0.08')),
        'enable_centrist_moderation': os.getenv('KKI_CENTRIST_MODERATION', '').strip().lower() in {'1', 'true', 'yes', 'on'},
        'centrist_pull_strength': float(os.getenv('KKI_CENTRIST_PULL', '0.08')),
        'enable_mediator_encouragement': os.getenv('KKI_MEDIATOR_MODE', '').strip().lower() in {'1', 'true', 'yes', 'on'},
        'mediator_contact_bias': float(os.getenv('KKI_MEDIATOR_CONTACT_BIAS', '0.60')),
        'center_zone_min': float(os.getenv('KKI_CENTER_ZONE_MIN', str(DEFAULT_CENTER_MIN))),
        'center_zone_max': float(os.getenv('KKI_CENTER_ZONE_MAX', str(DEFAULT_CENTER_MAX))),
        'roles_enabled': os.getenv('KKI_ROLES_ENABLED', '').strip().lower() in {'1', 'true', 'yes', 'on'},
        'generalist_share': float(os.getenv('KKI_GENERALIST_SHARE', str(DEFAULT_GENERALIST_SHARE))),
        'connector_share': float(os.getenv('KKI_CONNECTOR_SHARE', str(DEFAULT_CONNECTOR_SHARE))),
        'sentinel_share': float(os.getenv('KKI_SENTINEL_SHARE', str(DEFAULT_SENTINEL_SHARE))),
        'mediator_share': float(os.getenv('KKI_MEDIATOR_SHARE', str(DEFAULT_MEDIATOR_SHARE))),
        'analyzer_share': float(os.getenv('KKI_ANALYZER_SHARE', str(DEFAULT_ANALYZER_SHARE))),
        'connector_bridge_bonus': float(os.getenv('KKI_CONNECTOR_BRIDGE_BONUS', str(DEFAULT_CONNECTOR_BONUS))),
        'sentinel_rep_threshold': float(
            os.getenv('KKI_SENTINEL_REP_THRESHOLD', str(DEFAULT_SENTINEL_REP_THRESHOLD))
        ),
        'sentinel_cooperation_penalty': float(
            os.getenv(
                'KKI_SENTINEL_COOPERATION_PENALTY',
                str(DEFAULT_SENTINEL_COOPERATION_PENALTY),
            )
        ),
        'connector_cross_group_learning_bonus': float(
            os.getenv(
                'KKI_CONNECTOR_CROSS_GROUP_LEARNING',
                str(DEFAULT_CONNECTOR_CROSS_GROUP_LEARNING),
            )
        ),
        'sentinel_reputation_learning_multiplier': float(
            os.getenv(
                'KKI_SENTINEL_REPUTATION_LEARNING',
                str(DEFAULT_SENTINEL_REPUTATION_LEARNING),
            )
        ),
        'mediator_bridge_bonus': float(
            os.getenv('KKI_MEDIATOR_BRIDGE_BONUS', str(DEFAULT_MEDIATOR_BONUS))
        ),
        'mediator_partner_bias': float(
            os.getenv('KKI_MEDIATOR_PARTNER_BIAS', str(DEFAULT_MEDIATOR_CONTACT_BIAS))
        ),
        'mediator_partner_distance': float(
            os.getenv('KKI_MEDIATOR_PARTNER_DISTANCE', str(DEFAULT_MEDIATOR_OPINION_DISTANCE))
        ),
        'analyzer_memory_window': int(
            os.getenv('KKI_ANALYZER_MEMORY_WINDOW', str(DEFAULT_ANALYZER_MEMORY_WINDOW))
        ),
        'analyzer_learning_multiplier': float(
            os.getenv(
                'KKI_ANALYZER_LEARNING_MULTIPLIER',
                str(DEFAULT_ANALYZER_LEARNING_MULTIPLIER),
            )
        ),
        'enable_role_switching': os.getenv('KKI_ENABLE_ROLE_SWITCHING', '').strip().lower() in {'1', 'true', 'yes', 'on'},
        'role_switch_interval': int(
            os.getenv('KKI_ROLE_SWITCH_INTERVAL', str(DEFAULT_ROLE_SWITCH_INTERVAL))
        ),
        'role_switch_min_tenure': int(
            os.getenv('KKI_ROLE_SWITCH_MIN_TENURE', str(DEFAULT_ROLE_SWITCH_MIN_TENURE))
        ),
        'role_switch_reputation_cost': float(
            os.getenv(
                'KKI_ROLE_SWITCH_REPUTATION_COST',
                str(DEFAULT_ROLE_SWITCH_REPUTATION_COST),
            )
        ),
    }
    return config, seed


def normalisiere_rollenanteile(config):
    generalist = max(0.0, float(config.get('generalist_share', DEFAULT_GENERALIST_SHARE)))
    connector = max(0.0, float(config.get('connector_share', DEFAULT_CONNECTOR_SHARE)))
    sentinel = max(0.0, float(config.get('sentinel_share', DEFAULT_SENTINEL_SHARE)))
    mediator = max(0.0, float(config.get('mediator_share', DEFAULT_MEDIATOR_SHARE)))
    analyzer = max(0.0, float(config.get('analyzer_share', DEFAULT_ANALYZER_SHARE)))
    total = generalist + connector + sentinel + mediator + analyzer
    if total <= 0.0:
        return {
            'generalist': 1.0,
            'connector': 0.0,
            'sentinel': 0.0,
            'mediator': 0.0,
            'analyzer': 0.0,
        }
    return {
        'generalist': generalist / total,
        'connector': connector / total,
        'sentinel': sentinel / total,
        'mediator': mediator / total,
        'analyzer': analyzer / total,
    }


def apply_role_profile(agent, role, config):
    agent.role = role
    agent.bridge_bonus = 0.0
    agent.rewire_reputation_threshold = None
    agent.cooperation_penalty_threshold = None
    agent.cooperation_penalty = 0.0
    agent.intelligence_learning_multiplier = 1.0
    agent.cooperation_learning_multiplier = 1.0
    agent.reputation_learning_multiplier = 1.0
    agent.opinion_learning_multiplier = 1.0
    agent.cross_group_learning_bonus = 0.0
    agent.memory_window = 10
    agent.partner_bias_probability = 0.0
    agent.partner_bias_min_distance = 0.0

    if role == 'connector':
        agent.bridge_bonus = float(config.get('connector_bridge_bonus', DEFAULT_CONNECTOR_BONUS))
        agent.opinion_learning_multiplier = 1.15
        agent.cross_group_learning_bonus = float(
            config.get(
                'connector_cross_group_learning_bonus',
                DEFAULT_CONNECTOR_CROSS_GROUP_LEARNING,
            )
        )
    elif role == 'sentinel':
        agent.rewire_reputation_threshold = float(
            config.get('sentinel_rep_threshold', DEFAULT_SENTINEL_REP_THRESHOLD)
        )
        agent.cooperation_penalty_threshold = agent.rewire_reputation_threshold
        agent.cooperation_penalty = float(
            config.get('sentinel_cooperation_penalty', DEFAULT_SENTINEL_COOPERATION_PENALTY)
        )
        agent.reputation_learning_multiplier = float(
            config.get(
                'sentinel_reputation_learning_multiplier',
                DEFAULT_SENTINEL_REPUTATION_LEARNING,
            )
        )
        agent.opinion_learning_multiplier = 0.75
        agent.memory_window = 12
    elif role == 'mediator':
        agent.bridge_bonus = float(config.get('mediator_bridge_bonus', DEFAULT_MEDIATOR_BONUS))
        agent.partner_bias_probability = float(
            config.get('mediator_partner_bias', DEFAULT_MEDIATOR_CONTACT_BIAS)
        )
        agent.partner_bias_min_distance = float(
            config.get('mediator_partner_distance', DEFAULT_MEDIATOR_OPINION_DISTANCE)
        )
        agent.opinion_learning_multiplier = 1.30
        agent.cross_group_learning_bonus = 0.10
    elif role == 'analyzer':
        agent.memory_window = int(config.get('analyzer_memory_window', DEFAULT_ANALYZER_MEMORY_WINDOW))
        agent.intelligence_learning_multiplier = float(
            config.get(
                'analyzer_learning_multiplier',
                DEFAULT_ANALYZER_LEARNING_MULTIPLIER,
            )
        )
        agent.reputation_learning_multiplier = 1.10
        agent.opinion_learning_multiplier = 0.85


def weise_rollen_zu(agenten, config):
    shares = normalisiere_rollenanteile(config)
    agent_count = len(agenten)
    connector_count = int(round(agent_count * shares['connector']))
    sentinel_count = int(round(agent_count * shares['sentinel']))
    mediator_count = int(round(agent_count * shares['mediator']))
    analyzer_count = int(round(agent_count * shares['analyzer']))
    connector_count = min(agent_count, connector_count)
    sentinel_count = min(agent_count - connector_count, sentinel_count)
    mediator_count = min(agent_count - connector_count - sentinel_count, mediator_count)
    analyzer_count = min(
        agent_count - connector_count - sentinel_count - mediator_count,
        analyzer_count,
    )

    shuffled = list(agenten)
    random.shuffle(shuffled)
    connector_ids = {agent.id for agent in shuffled[:connector_count]}
    offset = connector_count
    sentinel_ids = {agent.id for agent in shuffled[offset : offset + sentinel_count]}
    offset += sentinel_count
    mediator_ids = {agent.id for agent in shuffled[offset : offset + mediator_count]}
    offset += mediator_count
    analyzer_ids = {agent.id for agent in shuffled[offset : offset + analyzer_count]}

    for agent in agenten:
        zielrolle = 'generalist'
        if agent.id in connector_ids:
            zielrolle = 'connector'
            agent.hartnaeckigkeit = max(0.0, agent.hartnaeckigkeit * 0.6)
            agent.kooperations_neigung = min(0.95, agent.kooperations_neigung + 0.04)
        elif agent.id in sentinel_ids:
            zielrolle = 'sentinel'
            agent.reputation = min(1.0, agent.reputation + 0.04)
        elif agent.id in mediator_ids:
            zielrolle = 'mediator'
            agent.hartnaeckigkeit = max(0.0, agent.hartnaeckigkeit * 0.5)
        elif agent.id in analyzer_ids:
            zielrolle = 'analyzer'

        apply_role_profile(agent, zielrolle, config)
        agent.initial_role = zielrolle
        agent.role_tenure = 0
        agent.role_transition_history = []


def erstelle_agenten(config):
    agenten = []
    agent_count = int(config['agent_count'])
    scenario = str(config['scenario'])
    gruppengroesse = agent_count // 2

    for index in range(agent_count):
        gruppe = 0 if index < gruppengroesse else 1

        if scenario == 'consensus':
            basis_meinung = 0.45 if gruppe == 0 else 0.55
            streuung = 0.05
            hartnaeckigkeit = 0.15 if index % 7 == 0 else 0.05
            kooperation = 0.58 if gruppe == 0 else 0.56
        else:
            basis_meinung = 0.2 if gruppe == 0 else 0.8
            streuung = 0.08
            hartnaeckigkeit = 0.55 if index % 6 == 0 else 0.2
            kooperation = 0.5

        meinung = max(0.0, min(1.0, random.gauss(basis_meinung, streuung)))
        agenten.append(Agent(index, gruppe, meinung, kooperation, hartnaeckigkeit))

    if config.get('roles_enabled'):
        weise_rollen_zu(agenten, config)

    return agenten


def erstelle_netzwerk(agenten, config):
    gruppen = {
        0: [agent for agent in agenten if agent.gruppe == 0],
        1: [agent for agent in agenten if agent.gruppe == 1],
    }
    connections_per_agent = int(config['connections_per_agent'])
    cross_group_chance = float(config['cross_group_chance'])
    random_edge_chance = float(config['random_edge_chance'])

    for gruppen_agenten in gruppen.values():
        n = len(gruppen_agenten)
        for i in range(n):
            for j in range(1, connections_per_agent // 2 + 1):
                gruppen_agenten[i].verbinde(gruppen_agenten[(i + j) % n])

    for agent in agenten:
        if random.random() < cross_group_chance:
            andere_gruppe = [ziel for ziel in agenten if ziel.gruppe != agent.gruppe and ziel.id != agent.id]
            ziel = random.choice(andere_gruppe)
            agent.verbinde(ziel)

        if random.random() < random_edge_chance:
            moegliche = [ziel for ziel in agenten if ziel.id != agent.id and ziel.id not in agent.nachbarn]
            if moegliche:
                agent.verbinde(random.choice(moegliche))


def waehle_partner(agent, agenten, agenten_dict, config=None):
    partner_bias_probability = getattr(agent, 'partner_bias_probability', 0.0)
    if partner_bias_probability > 0.0 and random.random() < partner_bias_probability:
        bias_distance = getattr(agent, 'partner_bias_min_distance', 0.0)
        kandidaten = [
            anderer
            for anderer in agenten
            if anderer.id != agent.id and abs(anderer.meinung - agent.meinung) >= bias_distance
        ]
        if kandidaten:
            kandidaten.sort(key=lambda anderer: abs(anderer.meinung - agent.meinung), reverse=True)
            return kandidaten[0]
    if config and config.get('enable_mediator_encouragement') and ist_zentrist(agent.meinung, config):
        bias = float(config['mediator_contact_bias'])
        if random.random() < bias:
            kandidaten = [
                anderer
                for anderer in agenten
                if anderer.id != agent.id and abs(anderer.meinung - agent.meinung) > 0.30
            ]
            if kandidaten:
                return random.choice(kandidaten)
    if agent.nachbarn and random.random() < 0.9:
        return agenten_dict[random.choice(list(agent.nachbarn))]
    kandidaten = [anderer for anderer in agenten if anderer.id != agent.id]
    return random.choice(kandidaten)


def berechne_lager(agenten):
    links = sum(1 for agent in agenten if agent.meinung < 0.35)
    mitte = sum(1 for agent in agenten if 0.35 <= agent.meinung <= 0.65)
    rechts = sum(1 for agent in agenten if agent.meinung > 0.65)
    return links, mitte, rechts


def berechne_polarisierungs_index(agenten):
    return float(np.std([agent.meinung for agent in agenten]))


def berechne_konsens_score(agenten):
    meinungen = np.array([agent.meinung for agent in agenten])
    abweichung = np.mean(np.abs(meinungen - np.mean(meinungen)))
    return max(0.0, 1.0 - min(1.0, abweichung * 2.0))


def berechne_gruppenabstand(agenten):
    gruppe_links = [agent.meinung for agent in agenten if agent.gruppe == 0]
    gruppe_rechts = [agent.meinung for agent in agenten if agent.gruppe == 1]
    return abs(np.mean(gruppe_links) - np.mean(gruppe_rechts))


def ist_zentrist(meinung, config):
    center_min = float(config.get('center_zone_min', DEFAULT_CENTER_MIN))
    center_max = float(config.get('center_zone_max', DEFAULT_CENTER_MAX))
    return center_min <= meinung <= center_max


def berechne_brueckenagenten(agenten, agenten_dict):
    bridge_ids = set()
    for agent in agenten:
        gruppen = {agenten_dict[nachbar_id].gruppe for nachbar_id in agent.nachbarn if nachbar_id in agenten_dict}
        if 0 in gruppen and 1 in gruppen:
            bridge_ids.add(agent.id)
    return bridge_ids


def berechne_netzwerkmetriken(agenten, agenten_dict):
    kanten = set()
    nachbarschaftsdistanzen = []
    gruppenuebergreifende_kanten = 0

    for agent in agenten:
        for nachbar_id in agent.nachbarn:
            kante = tuple(sorted((agent.id, nachbar_id)))
            if kante in kanten:
                continue
            kanten.add(kante)
            nachbar = agenten_dict[nachbar_id]
            nachbarschaftsdistanzen.append(abs(agent.meinung - nachbar.meinung))
            if agent.gruppe != nachbar.gruppe:
                gruppenuebergreifende_kanten += 1

    kantenanzahl = len(kanten)
    agentenzahl = len(agenten)
    moegliche_kanten = agentenzahl * (agentenzahl - 1) / 2

    return {
        'edge_count': kantenanzahl,
        'density': kantenanzahl / moegliche_kanten if moegliche_kanten else 0.0,
        'mean_degree': float(np.mean([len(agent.nachbarn) for agent in agenten])) if agenten else 0.0,
        'mean_neighbor_opinion_distance': (
            float(np.mean(nachbarschaftsdistanzen)) if nachbarschaftsdistanzen else 0.0
        ),
        'cross_group_edge_share': (
            gruppenuebergreifende_kanten / kantenanzahl if kantenanzahl else 0.0
        ),
    }


def finde_neuen_nachbarn(agent, agenten, config):
    proximity_weight = float(config['rewire_proximity_weight'])
    opinion_threshold = float(config['rewire_opinion_distance_threshold'])
    cross_group_bonus = float(config['rewire_cross_group_bonus'])

    bester_score = None
    beste_kandidaten = []

    for kandidat in agenten:
        if kandidat.id == agent.id or kandidat.id in agent.nachbarn:
            continue

        distanz = abs(agent.meinung - kandidat.meinung)
        if distanz > opinion_threshold + 0.25:
            continue

        aehnlichkeit = 1.0 - distanz
        score = (1.0 - proximity_weight) * kandidat.reputation + proximity_weight * aehnlichkeit
        if distanz > opinion_threshold:
            score -= (distanz - opinion_threshold) * 0.6
        if kandidat.gruppe != agent.gruppe:
            score += cross_group_bonus

        if bester_score is None or score > bester_score + 1e-9:
            bester_score = score
            beste_kandidaten = [kandidat]
        elif abs(score - bester_score) <= 1e-9:
            beste_kandidaten.append(kandidat)

    if not beste_kandidaten:
        return None
    return random.choice(beste_kandidaten)


def aktualisiere_adaptives_netzwerk(agenten, agenten_dict, config):
    if not config.get('enable_dynamic_rewiring'):
        return {
            'removed_edges': 0,
            'added_edges': 0,
            'rewired_edges': 0,
            'removed_for_reputation': 0,
            'removed_for_distance': 0,
        }

    min_interactions = int(config['rewire_min_interactions'])
    rep_threshold = float(config['rewire_reputation_threshold'])
    opinion_threshold = float(config['rewire_opinion_distance_threshold'])
    removal_probability = float(config['rewire_removal_probability'])
    addition_probability = float(config['rewire_addition_probability'])
    target_degree = max(1, int(config['rewire_target_degree']))

    removed_edges = 0
    added_edges = 0
    removed_for_reputation = 0
    removed_for_distance = 0

    for agent in agenten:
        zu_trennen = []
        agent_role_threshold = getattr(agent, 'rewire_reputation_threshold', None)
        lokaler_rep_threshold = (
            float(agent_role_threshold)
            if agent_role_threshold is not None
            else rep_threshold
        )
        for nachbar_id in list(agent.nachbarn):
            history = agent.interaktions_history.get(nachbar_id, [])
            if len(history) < min_interactions:
                continue

            nachbar = agenten_dict[nachbar_id]
            schwache_reputation = agent.berechne_partner_reputation(nachbar_id) < lokaler_rep_threshold
            grosse_distanz = abs(agent.meinung - nachbar.meinung) > opinion_threshold
            if (schwache_reputation or grosse_distanz) and random.random() < removal_probability:
                zu_trennen.append((nachbar, schwache_reputation, grosse_distanz))

        for nachbar, schwache_reputation, grosse_distanz in zu_trennen:
            if nachbar.id not in agent.nachbarn:
                continue
            agent.trenne(nachbar)
            removed_edges += 1
            if schwache_reputation:
                removed_for_reputation += 1
            else:
                removed_for_distance += 1

    for agent in agenten:
        additions_versucht = 0
        while len(agent.nachbarn) < target_degree and additions_versucht < 2:
            additions_versucht += 1
            if random.random() > addition_probability:
                break

            kandidat = finde_neuen_nachbarn(agent, agenten, config)
            if kandidat is None or kandidat.id in agent.nachbarn:
                break

            agent.verbinde(kandidat)
            added_edges += 1

    return {
        'removed_edges': removed_edges,
        'added_edges': added_edges,
        'rewired_edges': removed_edges + added_edges,
        'removed_for_reputation': removed_for_reputation,
        'removed_for_distance': removed_for_distance,
    }


def bestimme_rollenwechsel(agent, agenten_dict):
    if not agent.nachbarn:
        return None

    nachbarn = [agenten_dict[nachbar_id] for nachbar_id in agent.nachbarn if nachbar_id in agenten_dict]
    if not nachbarn:
        return None

    cross_group_neighbors = sum(1 for nachbar in nachbarn if nachbar.gruppe != agent.gruppe)
    cross_group_share = cross_group_neighbors / len(nachbarn)
    mean_partner_reputation = float(np.mean([agent.berechne_partner_reputation(nachbar.id) for nachbar in nachbarn]))
    mean_neighbor_distance = float(np.mean([abs(agent.meinung - nachbar.meinung) for nachbar in nachbarn]))

    if agent.role == 'generalist':
        if cross_group_share >= 0.35 and agent.kooperations_neigung >= 0.62:
            return 'connector'
        if agent.reputation >= 0.60 and mean_partner_reputation <= 0.45:
            return 'sentinel'
    elif agent.role == 'connector':
        if cross_group_share >= 0.45 and 0.30 <= agent.meinung <= 0.70:
            return 'mediator'
        if mean_partner_reputation <= 0.42 and agent.reputation >= 0.60:
            return 'sentinel'
    elif agent.role == 'sentinel':
        if agent.reputation >= 0.72 and mean_neighbor_distance <= 0.28:
            return 'analyzer'
        if cross_group_share >= 0.40 and agent.kooperations_neigung >= 0.60:
            return 'connector'
    elif agent.role == 'mediator':
        if mean_neighbor_distance <= 0.18 and agent.reputation >= 0.62:
            return 'analyzer'
        if mean_partner_reputation <= 0.40:
            return 'sentinel'
    elif agent.role == 'analyzer':
        if cross_group_share >= 0.40 and agent.reputation >= 0.65:
            return 'connector'
        if agent.kooperations_neigung <= 0.42:
            return 'generalist'

    if len(agent.nachbarn) <= 2 and agent.role != 'generalist':
        return 'generalist'
    return None


def aktualisiere_rollenwechsel(agenten, agenten_dict, config, runde):
    if not config.get('enable_role_switching') or not config.get('roles_enabled'):
        return {'switches': 0, 'transitions': []}

    interval = max(1, int(config.get('role_switch_interval', DEFAULT_ROLE_SWITCH_INTERVAL)))
    min_tenure = max(1, int(config.get('role_switch_min_tenure', DEFAULT_ROLE_SWITCH_MIN_TENURE)))
    if runde % interval != 0:
        return {'switches': 0, 'transitions': []}

    max_switches = int(config.get('max_role_switches_per_round', max(1, len(agenten) // 10)))
    switch_cost = float(config.get('role_switch_reputation_cost', DEFAULT_ROLE_SWITCH_REPUTATION_COST))
    transitions = []

    kandidaten = list(agenten)
    random.shuffle(kandidaten)
    for agent in kandidaten:
        if len(transitions) >= max_switches:
            break
        if agent.role_tenure < min_tenure:
            continue

        neue_rolle = bestimme_rollenwechsel(agent, agenten_dict)
        if neue_rolle is None or neue_rolle == agent.role:
            continue

        alte_rolle = agent.role
        apply_role_profile(agent, neue_rolle, config)
        agent.reputation = max(0.0, min(1.0, agent.reputation - switch_cost))
        agent.role_tenure = 0
        agent.role_transition_history.append((runde, alte_rolle, neue_rolle))
        transitions.append((alte_rolle, neue_rolle))

    return {'switches': len(transitions), 'transitions': transitions}


def run_polarization_experiment(
    config,
    *,
    make_plot=True,
    output_filename='kki_polarisierung.png',
    print_summary=True,
):
    config = dict(config)
    config.setdefault('center_zone_min', DEFAULT_CENTER_MIN)
    config.setdefault('center_zone_max', DEFAULT_CENTER_MAX)
    config.setdefault('enable_bridge_mechanism', False)
    config.setdefault('enable_centrist_moderation', False)
    config.setdefault('enable_mediator_encouragement', False)
    config.setdefault('bridge_cooperation_bonus', 0.08)
    config.setdefault('centrist_pull_strength', 0.08)
    config.setdefault('mediator_contact_bias', 0.60)
    config.setdefault('roles_enabled', False)
    config.setdefault('generalist_share', DEFAULT_GENERALIST_SHARE)
    config.setdefault('connector_share', DEFAULT_CONNECTOR_SHARE)
    config.setdefault('sentinel_share', DEFAULT_SENTINEL_SHARE)
    config.setdefault('mediator_share', DEFAULT_MEDIATOR_SHARE)
    config.setdefault('analyzer_share', DEFAULT_ANALYZER_SHARE)
    config.setdefault('connector_bridge_bonus', DEFAULT_CONNECTOR_BONUS)
    config.setdefault('sentinel_rep_threshold', DEFAULT_SENTINEL_REP_THRESHOLD)
    config.setdefault('sentinel_cooperation_penalty', DEFAULT_SENTINEL_COOPERATION_PENALTY)
    config.setdefault('connector_cross_group_learning_bonus', DEFAULT_CONNECTOR_CROSS_GROUP_LEARNING)
    config.setdefault('sentinel_reputation_learning_multiplier', DEFAULT_SENTINEL_REPUTATION_LEARNING)
    config.setdefault('mediator_bridge_bonus', DEFAULT_MEDIATOR_BONUS)
    config.setdefault('mediator_partner_bias', DEFAULT_MEDIATOR_CONTACT_BIAS)
    config.setdefault('mediator_partner_distance', DEFAULT_MEDIATOR_OPINION_DISTANCE)
    config.setdefault('analyzer_memory_window', DEFAULT_ANALYZER_MEMORY_WINDOW)
    config.setdefault('analyzer_learning_multiplier', DEFAULT_ANALYZER_LEARNING_MULTIPLIER)
    config.setdefault('enable_role_switching', False)
    config.setdefault('role_switch_interval', DEFAULT_ROLE_SWITCH_INTERVAL)
    config.setdefault('role_switch_min_tenure', DEFAULT_ROLE_SWITCH_MIN_TENURE)
    config.setdefault('role_switch_reputation_cost', DEFAULT_ROLE_SWITCH_REPUTATION_COST)
    config.setdefault('max_role_switches_per_round', max(1, int(config['agent_count']) // 10))
    scenario = str(config['scenario'])
    rounds = int(config['rounds'])
    interactions_per_round = int(config['interactions_per_round'])
    connections_per_agent = int(config['connections_per_agent'])

    agenten = erstelle_agenten(config)
    agenten_dict = {agent.id: agent for agent in agenten}
    erstelle_netzwerk(agenten, config)

    if print_summary:
        print("=" * 78)
        print(f"KKI POLARISIERUNGS-EXPERIMENT: {scenario_title(scenario)}")
        print("=" * 78)
        print(f"\nSzenario: {scenario}")
        print(
            f"Agenten: {config['agent_count']}, Runden: {rounds}, "
            f"Interaktionen/Runde: {interactions_per_round}"
        )
        print(
            "Netzwerk: "
            f"Grad={connections_per_agent}, "
            f"Cross-Group={float(config['cross_group_chance']):.2f}, "
            f"Shortcut={float(config['random_edge_chance']):.2f}"
        )
        if config.get('enable_dynamic_rewiring'):
            print(
                "Adaptives Rewiring: "
                f"aktiv | Rep-Schwelle={float(config['rewire_reputation_threshold']):.2f}, "
                f"Meinungs-Schwelle={float(config['rewire_opinion_distance_threshold']):.2f}, "
                f"Zielgrad={int(config['rewire_target_degree'])}"
            )
        if config.get('roles_enabled'):
            shares = normalisiere_rollenanteile(config)
            print(
                "Rollen: "
                f"Generalisten={shares['generalist']:.0%}, "
                f"Brueckenbauer={shares['connector']:.0%}, "
                f"Waechter={shares['sentinel']:.0%}, "
                f"Vermittler={shares['mediator']:.0%}, "
                f"Analytiker={shares['analyzer']:.0%}"
            )
            if config.get('enable_role_switching'):
                print(
                    "Rollenwechsel: "
                    f"aktiv | Intervall={int(config['role_switch_interval'])}, "
                    f"Mindestdauer={int(config['role_switch_min_tenure'])}, "
                    f"Kosten={float(config['role_switch_reputation_cost']):.2f}"
                )
        print("Ziel: Beobachte, ob der Schwarm in Richtung Konsens oder in stabile Lager driftet.")
        print("\nSimulation läuft...\n")

    polarisierungs_history = []
    konsens_history = []
    gruppenabstand_history = []
    links_history = []
    mitte_history = []
    rechts_history = []
    gruppe_a_intelligenz = []
    gruppe_b_intelligenz = []
    cross_group_history = []
    cross_group_cooperation_history = []
    bridge_count_history = []
    center_zone_history = []
    role_cross_group_contacts = defaultdict(int)
    role_cross_group_cooperations = defaultdict(int)
    role_switch_history = []
    role_transition_counts = defaultdict(int)
    removed_edges_history = []
    added_edges_history = []
    rewired_edges_history = []
    removed_reputation_history = []
    removed_distance_history = []
    density_history = []
    mean_degree_history = []
    neighbor_distance_history = []
    cross_group_edge_share_history = []

    for runde in range(1, rounds + 1):
        gruppenuebergreifende_interaktionen = 0
        gruppenuebergreifende_kooperationen = 0
        bridge_ids = berechne_brueckenagenten(agenten, agenten_dict)

        for _ in range(interactions_per_round):
            agent = random.choice(agenten)
            partner = waehle_partner(agent, agenten, agenten_dict, config)

            if agent.gruppe != partner.gruppe:
                gruppenuebergreifende_interaktionen += 1
                role_cross_group_contacts[agent.role] += 1
                role_cross_group_contacts[partner.role] += 1

            partner_rep_aus_agent_sicht = agent.berechne_partner_reputation(partner.id)
            agent_rep_aus_partner_sicht = partner.berechne_partner_reputation(agent.id)

            cooperation_bonus_a = 0.0
            cooperation_bonus_p = 0.0
            if agent.gruppe != partner.gruppe and config.get('enable_bridge_mechanism'):
                if agent.id in bridge_ids:
                    cooperation_bonus_a += float(config['bridge_cooperation_bonus'])
                if partner.id in bridge_ids:
                    cooperation_bonus_p += float(config['bridge_cooperation_bonus'])
            if agent.gruppe != partner.gruppe:
                cooperation_bonus_a += agent.bridge_bonus
                cooperation_bonus_p += partner.bridge_bonus
            if agent.gruppe != partner.gruppe and config.get('enable_centrist_moderation'):
                if ist_zentrist(agent.meinung, config):
                    cooperation_bonus_a += 0.04
                if ist_zentrist(partner.meinung, config):
                    cooperation_bonus_p += 0.04

            aktion_a = agent.waehle_aktion(partner_rep_aus_agent_sicht, partner.meinung, cooperation_bonus_a)
            aktion_p = partner.waehle_aktion(agent_rep_aus_partner_sicht, agent.meinung, cooperation_bonus_p)
            if agent.gruppe != partner.gruppe and aktion_a == 'C' and aktion_p == 'C':
                gruppenuebergreifende_kooperationen += 1
                role_cross_group_cooperations[agent.role] += 1
                role_cross_group_cooperations[partner.role] += 1

            opinion_pull_a = 0.0
            opinion_pull_p = 0.0
            if config.get('enable_centrist_moderation') and agent.gruppe != partner.gruppe:
                if ist_zentrist(agent.meinung, config) or ist_zentrist(partner.meinung, config):
                    opinion_pull_a += float(config['centrist_pull_strength'])
                    opinion_pull_p += float(config['centrist_pull_strength'])

            agent.lerne(
                aktion_a,
                aktion_p,
                partner.id,
                partner.intelligenz,
                partner.meinung,
                agent.gruppe == partner.gruppe,
                opinion_pull=opinion_pull_a,
            )
            partner.lerne(
                aktion_p,
                aktion_a,
                agent.id,
                agent.intelligenz,
                agent.meinung,
                agent.gruppe == partner.gruppe,
                opinion_pull=opinion_pull_p,
            )

        switch_stats = aktualisiere_rollenwechsel(agenten, agenten_dict, config, runde)
        rewiring_stats = aktualisiere_adaptives_netzwerk(agenten, agenten_dict, config)
        for agent in agenten:
            agent.role_tenure += 1
            agent.runde_beenden()

        polarisierungs_index = berechne_polarisierungs_index(agenten)
        konsens_score = berechne_konsens_score(agenten)
        gruppenabstand = berechne_gruppenabstand(agenten)
        netzwerkmetriken = berechne_netzwerkmetriken(agenten, agenten_dict)
        links, mitte, rechts = berechne_lager(agenten)

        polarisierungs_history.append(polarisierungs_index)
        konsens_history.append(konsens_score)
        gruppenabstand_history.append(gruppenabstand)
        links_history.append(links)
        mitte_history.append(mitte)
        rechts_history.append(rechts)
        gruppe_a_intelligenz.append(np.mean([agent.intelligenz for agent in agenten if agent.gruppe == 0]))
        gruppe_b_intelligenz.append(np.mean([agent.intelligenz for agent in agenten if agent.gruppe == 1]))
        cross_group_history.append(gruppenuebergreifende_interaktionen / interactions_per_round)
        cross_group_cooperation_history.append(
            gruppenuebergreifende_kooperationen / max(1, gruppenuebergreifende_interaktionen)
        )
        bridge_count_history.append(len(bridge_ids))
        center_zone_history.append(sum(1 for agent in agenten if ist_zentrist(agent.meinung, config)))
        role_switch_history.append(switch_stats['switches'])
        for alte_rolle, neue_rolle in switch_stats['transitions']:
            role_transition_counts[f'{alte_rolle}->{neue_rolle}'] += 1
        removed_edges_history.append(rewiring_stats['removed_edges'])
        added_edges_history.append(rewiring_stats['added_edges'])
        rewired_edges_history.append(rewiring_stats['rewired_edges'])
        removed_reputation_history.append(rewiring_stats['removed_for_reputation'])
        removed_distance_history.append(rewiring_stats['removed_for_distance'])
        density_history.append(netzwerkmetriken['density'])
        mean_degree_history.append(netzwerkmetriken['mean_degree'])
        neighbor_distance_history.append(netzwerkmetriken['mean_neighbor_opinion_distance'])
        cross_group_edge_share_history.append(netzwerkmetriken['cross_group_edge_share'])

        if print_summary and runde % 30 == 0:
            status = (
                f"Runde {runde:3d}: PI={polarisierungs_index:.3f}, "
                f"Konsens={konsens_score:.3f}, Gruppenabstand={gruppenabstand:.3f}, "
                f"Links/Mitte/Rechts={links}/{mitte}/{rechts}"
            )
            if config.get('enable_bridge_mechanism') or config.get('enable_centrist_moderation'):
                status += f", Brücken={len(bridge_ids)}, Mitte={center_zone_history[-1]}"
            if config.get('enable_role_switching'):
                status += f", Wechsel={switch_stats['switches']}"
            if config.get('enable_dynamic_rewiring'):
                status += f", Rewiring={rewiring_stats['rewired_edges']}"
            print(status)

    finale_pi = polarisierungs_history[-1]
    finaler_konsens = konsens_history[-1]
    finaler_abstand = gruppenabstand_history[-1]
    links, mitte, rechts = berechne_lager(agenten)
    cross_group_rate = float(np.mean(cross_group_history))
    cross_group_cooperation_rate = float(np.mean(cross_group_cooperation_history))
    mean_group_a = float(np.mean([agent.meinung for agent in agenten if agent.gruppe == 0]))
    mean_group_b = float(np.mean([agent.meinung for agent in agenten if agent.gruppe == 1]))
    finale_netzwerkmetriken = berechne_netzwerkmetriken(agenten, agenten_dict)
    durchschnitt_rewiring = float(np.mean(rewired_edges_history)) if rewired_edges_history else 0.0
    bekannte_rollen = ('generalist', 'connector', 'sentinel', 'mediator', 'analyzer')
    initial_role_counts = {role: sum(1 for agent in agenten if agent.initial_role == role) for role in bekannte_rollen}
    role_counts = {role: sum(1 for agent in agenten if agent.role == role) for role in bekannte_rollen}
    role_mean_intelligence = {
        role: float(np.mean([agent.intelligenz for agent in agenten if agent.role == role]))
        if role_counts[role]
        else 0.0
        for role in role_counts
    }
    role_mean_reputation = {
        role: float(np.mean([agent.reputation for agent in agenten if agent.role == role]))
        if role_counts[role]
        else 0.0
        for role in role_counts
    }
    role_mean_opinion_shift = {
        role: float(
            np.mean(
                [
                    abs(agent.meinung_history[-1] - agent.meinung_history[0])
                    for agent in agenten
                    if agent.role == role
                ]
            )
        )
        if role_counts[role]
        else 0.0
        for role in role_counts
    }
    role_cross_group_cooperation_rate = {
        role: role_cross_group_cooperations[role] / max(1, role_cross_group_contacts[role])
        for role in role_counts
    }

    interpretation = "hybrid"
    if finale_pi > 0.22 and finaler_abstand > 0.35:
        interpretation = "polarized"
    elif finaler_konsens > 0.72 and mitte > links and mitte > rechts:
        interpretation = "consensus"

    if print_summary:
        print("\n" + "=" * 78)
        print("ERGEBNISSE")
        print("=" * 78)
        print(f"\nFinaler Polarisierungs-Index: {finale_pi:.3f}")
        print(f"Finaler Konsens-Score:       {finaler_konsens:.3f}")
        print(f"Finaler Gruppenabstand:      {finaler_abstand:.3f}")
        print(f"Lagerverteilung:             Links={links}, Mitte={mitte}, Rechts={rechts}")
        print(f"Ø gruppenübergreifende Interaktionen: {cross_group_rate:.1%}")
        print(f"Ø gruppenübergreifende Kooperation:   {cross_group_cooperation_rate:.1%}")
        if config.get('enable_bridge_mechanism') or config.get('enable_centrist_moderation'):
            print(f"Ø Brückenagenten:            {float(np.mean(bridge_count_history)):.2f}")
            print(f"Ø Agenten in Mittelzone:     {float(np.mean(center_zone_history)):.2f}")
        if config.get('roles_enabled'):
            print(
                "Rollen-Kooperation:          "
                f"Generalisten={role_cross_group_cooperation_rate['generalist']:.1%}, "
                f"Brueckenbauer={role_cross_group_cooperation_rate['connector']:.1%}, "
                f"Waechter={role_cross_group_cooperation_rate['sentinel']:.1%}, "
                f"Vermittler={role_cross_group_cooperation_rate['mediator']:.1%}, "
                f"Analytiker={role_cross_group_cooperation_rate['analyzer']:.1%}"
            )
            if config.get('enable_role_switching'):
                print(f"Ø Rollenwechsel/Runde:       {float(np.mean(role_switch_history)):.2f}")
        if config.get('enable_dynamic_rewiring'):
            print(f"Ø Rewiring-Operationen/Runde: {durchschnitt_rewiring:.2f}")
            print(f"Finale Netzwerkdichte:       {finale_netzwerkmetriken['density']:.3f}")
            print(f"Finaler mittlerer Grad:      {finale_netzwerkmetriken['mean_degree']:.2f}")
            print(f"Anteil gruppenübergreifender Kanten: {finale_netzwerkmetriken['cross_group_edge_share']:.1%}")
        print(f"\nØ Meinung Gruppe 1: {mean_group_a:.3f}")
        print(f"Ø Meinung Gruppe 2: {mean_group_b:.3f}")

        if interpretation == "polarized":
            print("\n⚡ Der Schwarm ist in stabile Lager polarisiert.")
        elif interpretation == "consensus":
            print("\n🤝 Der Schwarm hat eine robuste Konsenszone ausgebildet.")
        else:
            print("\n🔄 Der Schwarm bleibt in einer hybriden Zwischenphase aus Konsens und Lagerbildung.")

    results = {
        'scenario': scenario,
        'config': dict(config),
        'final_polarization_index': finale_pi,
        'final_consensus_score': finaler_konsens,
        'final_group_distance': finaler_abstand,
        'left_count': links,
        'center_count': mitte,
        'right_count': rechts,
        'cross_group_interaction_rate': cross_group_rate,
        'cross_group_cooperation_rate': cross_group_cooperation_rate,
        'role_switch_enabled': bool(config.get('enable_role_switching')),
        'initial_role_counts': initial_role_counts,
        'role_counts': role_counts,
        'role_mean_intelligence': role_mean_intelligence,
        'role_mean_reputation': role_mean_reputation,
        'role_mean_opinion_shift': role_mean_opinion_shift,
        'role_cross_group_cooperation_rate': role_cross_group_cooperation_rate,
        'role_switch_history': role_switch_history,
        'role_switch_total': int(sum(role_switch_history)),
        'role_transition_counts': dict(role_transition_counts),
        'group_1_mean_opinion': mean_group_a,
        'group_2_mean_opinion': mean_group_b,
        'interpretation': interpretation,
        'rewiring_enabled': bool(config.get('enable_dynamic_rewiring')),
        'polarization_history': polarisierungs_history,
        'consensus_history': konsens_history,
        'group_distance_history': gruppenabstand_history,
        'left_history': links_history,
        'center_history': mitte_history,
        'right_history': rechts_history,
        'group_a_intelligence_history': gruppe_a_intelligenz,
        'group_b_intelligence_history': gruppe_b_intelligenz,
        'cross_group_history': cross_group_history,
        'cross_group_cooperation_history': cross_group_cooperation_history,
        'bridge_count_history': bridge_count_history,
        'center_zone_history': center_zone_history,
        'removed_edges_history': removed_edges_history,
        'added_edges_history': added_edges_history,
        'rewired_edges_history': rewired_edges_history,
        'removed_reputation_history': removed_reputation_history,
        'removed_distance_history': removed_distance_history,
        'network_density_history': density_history,
        'mean_degree_history': mean_degree_history,
        'neighbor_opinion_distance_history': neighbor_distance_history,
        'cross_group_edge_share_history': cross_group_edge_share_history,
        'average_rewired_edges_per_round': durchschnitt_rewiring,
        'final_network_density': finale_netzwerkmetriken['density'],
        'final_mean_degree': finale_netzwerkmetriken['mean_degree'],
        'final_cross_group_edge_share': finale_netzwerkmetriken['cross_group_edge_share'],
        'final_neighbor_opinion_distance': finale_netzwerkmetriken['mean_neighbor_opinion_distance'],
        'agents': agenten,
    }

    if make_plot:
        if config.get('enable_dynamic_rewiring'):
            fig = plt.figure(figsize=(18, 16))
            axes = [fig.add_subplot(3, 3, index + 1) for index in range(9)]
            ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9 = axes
        else:
            fig = plt.figure(figsize=(18, 12))
            axes = [fig.add_subplot(2, 3, index + 1) for index in range(6)]
            ax1, ax2, ax3, ax4, ax5, ax6 = axes

        fig.suptitle(
            f'KKI Polarisierungs-Experiment: {scenario_title(scenario)}',
            fontsize=14,
            fontweight='bold',
        )

        runden_x = list(range(rounds + 1))

        ax1.set_title('Meinungsdynamik aller Agenten')
        ax1.set_ylabel('Meinung (0 = links, 1 = rechts)')
        ax1.set_xlabel('Runde')
        for agent in agenten:
            color = '#3498DB' if agent.gruppe == 0 else '#E74C3C'
            alpha = 0.6 if agent.hartnaeckigkeit > 0.4 else 0.25
            linewidth = 1.4 if agent.hartnaeckigkeit > 0.4 else 0.7
            ax1.plot(runden_x, agent.meinung_history, color=color, alpha=alpha, linewidth=linewidth)
        ax1.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5)
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3)

        ax2.set_title('Polarisierung vs. Konsens')
        ax2.set_xlabel('Runde')
        ax2.set_ylabel('Index')
        ax2.plot(range(1, rounds + 1), polarisierungs_history, color='#8E44AD', linewidth=2, label='Polarisierungs-Index')
        ax2.plot(range(1, rounds + 1), konsens_history, color='#27AE60', linewidth=2, label='Konsens-Score')
        ax2.plot(range(1, rounds + 1), gruppenabstand_history, color='#F39C12', linewidth=2, label='Gruppenabstand')
        ax2.set_ylim(0, 1)
        ax2.legend(loc='best', fontsize=8)
        ax2.grid(True, alpha=0.3)

        ax3.set_title('Lagerbildung über Zeit')
        ax3.set_xlabel('Runde')
        ax3.set_ylabel('Anzahl Agenten')
        ax3.fill_between(range(1, rounds + 1), links_history, alpha=0.5, color='#3498DB', label='Links')
        ax3.fill_between(range(1, rounds + 1), mitte_history, alpha=0.5, color='#95A5A6', label='Mitte')
        ax3.fill_between(range(1, rounds + 1), rechts_history, alpha=0.5, color='#E74C3C', label='Rechts')
        ax3.set_ylim(0, int(config['agent_count']))
        ax3.legend(loc='upper right', fontsize=8)
        ax3.grid(True, alpha=0.3)

        ax4.set_title('Intelligenz nach Gruppen')
        ax4.set_xlabel('Runde')
        ax4.set_ylabel('Ø Intelligenz')
        ax4.plot(range(1, rounds + 1), gruppe_a_intelligenz, color='#3498DB', linewidth=2, label='Gruppe 1')
        ax4.plot(range(1, rounds + 1), gruppe_b_intelligenz, color='#E74C3C', linewidth=2, label='Gruppe 2')
        ax4.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
        ax4.legend(loc='best', fontsize=8)
        ax4.grid(True, alpha=0.3)

        ax5.set_title('Finale Position: Meinung vs. Kooperation')
        ax5.set_xlabel('Meinung')
        ax5.set_ylabel('Kooperationsneigung')
        for agent in agenten:
            color = '#3498DB' if agent.gruppe == 0 else '#E74C3C'
            ax5.scatter(
                agent.meinung,
                agent.kooperations_neigung,
                c=color,
                s=40 + agent.intelligenz * 12,
                alpha=0.7,
            )
        ax5.axvline(x=0.5, color='gray', linestyle=':', alpha=0.4)
        ax5.set_xlim(0, 1)
        ax5.set_ylim(0, 1)
        ax5.grid(True, alpha=0.3)

        ax6.set_title('Finale Meinungsverteilung')
        ax6.set_xlabel('Meinung')
        ax6.set_ylabel('Anzahl Agenten')
        agenten_g1 = [agent.meinung for agent in agenten if agent.gruppe == 0]
        agenten_g2 = [agent.meinung for agent in agenten if agent.gruppe == 1]
        ax6.hist(agenten_g1, bins=12, alpha=0.6, color='#3498DB', edgecolor='black', label='Gruppe 1')
        ax6.hist(agenten_g2, bins=12, alpha=0.6, color='#E74C3C', edgecolor='black', label='Gruppe 2')
        ax6.axvline(x=np.mean(agenten_g1), color='#1F618D', linestyle='--', linewidth=2)
        ax6.axvline(x=np.mean(agenten_g2), color='#922B21', linestyle='--', linewidth=2)
        ax6.legend(loc='best', fontsize=8)
        ax6.grid(True, alpha=0.3)

        if config.get('enable_dynamic_rewiring'):
            runden = range(1, rounds + 1)

            ax7.set_title('Adaptive Kanten pro Runde')
            ax7.set_xlabel('Runde')
            ax7.set_ylabel('Kantenänderungen')
            ax7.plot(runden, added_edges_history, color='#27AE60', linewidth=2, label='Hinzugefügt')
            ax7.plot(runden, removed_edges_history, color='#C0392B', linewidth=2, label='Entfernt')
            ax7.plot(runden, rewired_edges_history, color='#8E44AD', linewidth=2, label='Gesamt')
            ax7.legend(loc='best', fontsize=8)
            ax7.grid(True, alpha=0.3)

            ax8.set_title('Netzwerkdichte und mittlerer Grad')
            ax8.set_xlabel('Runde')
            ax8.set_ylabel('Dichte')
            linie_dichte = ax8.plot(runden, density_history, color='#1F618D', linewidth=2, label='Dichte')[0]
            ax8.set_ylim(0, max(0.05, max(density_history) * 1.2))
            ax8.grid(True, alpha=0.3)
            ax8_rechts = ax8.twinx()
            linie_grad = ax8_rechts.plot(
                runden,
                mean_degree_history,
                color='#F39C12',
                linewidth=2,
                label='Ø Grad',
            )[0]
            ax8_rechts.set_ylabel('Ø Grad')
            ax8.legend([linie_dichte, linie_grad], ['Dichte', 'Ø Grad'], loc='best', fontsize=8)

            ax9.set_title('Brücken und Nachbarschaftsabstand')
            ax9.set_xlabel('Runde')
            ax9.set_ylabel('Anteil / Distanz')
            ax9.plot(
                runden,
                cross_group_edge_share_history,
                color='#16A085',
                linewidth=2,
                label='Cross-Group-Kantenanteil',
            )
            ax9.plot(
                runden,
                neighbor_distance_history,
                color='#7F8C8D',
                linewidth=2,
                label='Ø Nachbarschaftsdistanz',
            )
            ax9.set_ylim(0, 1)
            ax9.legend(loc='best', fontsize=8)
            ax9.grid(True, alpha=0.3)

        plt.tight_layout()
        save_and_maybe_show(plt, output_filename, dpi=150)

    return results


def main():
    config, _ = build_runtime_config()
    run_polarization_experiment(config)


if __name__ == '__main__':
    main()
