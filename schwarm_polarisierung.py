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

        self.meinung_history = [meinung]
        self.kooperation_history = [kooperations_neigung]
        self.intelligenz_history = [1.0]

    def verbinde(self, anderer):
        self.nachbarn.add(anderer.id)
        anderer.nachbarn.add(self.id)

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
    ):
        self.interaktions_history[partner_id].append(andere_aktion)
        meinungs_distanz = abs(self.meinung - partner_meinung)
        aehnlichkeit = 1.0 - meinungs_distanz
        beweglichkeit = 1.0 - self.hartnaeckigkeit

        if meine_aktion == 'C' and andere_aktion == 'C':
            self.intelligenz *= 1.002 + 0.002 * aehnlichkeit + 0.001 * min(partner_intelligenz, 4.0)
            self.kooperations_neigung += 0.006 * (0.5 + aehnlichkeit)
            self.reputation += 0.012
            zugkraft = 0.12 if gleiche_gruppe else 0.08
            self.meinung += (partner_meinung - self.meinung) * zugkraft * beweglichkeit

        elif meine_aktion == 'C' and andere_aktion == 'D':
            self.kooperations_neigung -= 0.004
            self.reputation += 0.004
            if meinungs_distanz > 0.3:
                self.meinung += (self.meinung - partner_meinung) * 0.03 * beweglichkeit

        elif meine_aktion == 'D' and andere_aktion == 'C':
            self.intelligenz *= 0.997
            self.reputation -= 0.02
            if meinungs_distanz > 0.25:
                self.meinung += (self.meinung - partner_meinung) * 0.025 * beweglichkeit

        elif meine_aktion == 'D' and andere_aktion == 'D':
            self.intelligenz *= 0.991
            self.reputation -= 0.01
            self.kooperations_neigung += 0.002
            if meinungs_distanz > 0.2:
                self.meinung += (self.meinung - partner_meinung) * 0.02 * beweglichkeit

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
    }
    return config, seed


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


def waehle_partner(agent, agenten, agenten_dict):
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


def run_polarization_experiment(
    config,
    *,
    make_plot=True,
    output_filename='kki_polarisierung.png',
    print_summary=True,
):
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

    for runde in range(1, rounds + 1):
        gruppenuebergreifende_interaktionen = 0

        for _ in range(interactions_per_round):
            agent = random.choice(agenten)
            partner = waehle_partner(agent, agenten, agenten_dict)

            if agent.gruppe != partner.gruppe:
                gruppenuebergreifende_interaktionen += 1

            partner_rep_aus_agent_sicht = agent.berechne_partner_reputation(partner.id)
            agent_rep_aus_partner_sicht = partner.berechne_partner_reputation(agent.id)

            aktion_a = agent.waehle_aktion(partner_rep_aus_agent_sicht, partner.meinung)
            aktion_p = partner.waehle_aktion(agent_rep_aus_partner_sicht, agent.meinung)

            agent.lerne(
                aktion_a,
                aktion_p,
                partner.id,
                partner.intelligenz,
                partner.meinung,
                agent.gruppe == partner.gruppe,
            )
            partner.lerne(
                aktion_p,
                aktion_a,
                agent.id,
                agent.intelligenz,
                agent.meinung,
                agent.gruppe == partner.gruppe,
            )

        for agent in agenten:
            agent.runde_beenden()

        polarisierungs_index = berechne_polarisierungs_index(agenten)
        konsens_score = berechne_konsens_score(agenten)
        gruppenabstand = berechne_gruppenabstand(agenten)
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

        if print_summary and runde % 30 == 0:
            print(
                f"Runde {runde:3d}: PI={polarisierungs_index:.3f}, "
                f"Konsens={konsens_score:.3f}, Gruppenabstand={gruppenabstand:.3f}, "
                f"Links/Mitte/Rechts={links}/{mitte}/{rechts}"
            )

    finale_pi = polarisierungs_history[-1]
    finaler_konsens = konsens_history[-1]
    finaler_abstand = gruppenabstand_history[-1]
    links, mitte, rechts = berechne_lager(agenten)
    cross_group_rate = float(np.mean(cross_group_history))
    mean_group_a = float(np.mean([agent.meinung for agent in agenten if agent.gruppe == 0]))
    mean_group_b = float(np.mean([agent.meinung for agent in agenten if agent.gruppe == 1]))

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
        'group_1_mean_opinion': mean_group_a,
        'group_2_mean_opinion': mean_group_b,
        'interpretation': interpretation,
        'polarization_history': polarisierungs_history,
        'consensus_history': konsens_history,
        'group_distance_history': gruppenabstand_history,
        'left_history': links_history,
        'center_history': mitte_history,
        'right_history': rechts_history,
        'group_a_intelligence_history': gruppe_a_intelligenz,
        'group_b_intelligence_history': gruppe_b_intelligenz,
        'cross_group_history': cross_group_history,
        'agents': agenten,
    }

    if make_plot:
        fig = plt.figure(figsize=(18, 12))
        ax1 = fig.add_subplot(2, 3, 1)
        ax2 = fig.add_subplot(2, 3, 2)
        ax3 = fig.add_subplot(2, 3, 3)
        ax4 = fig.add_subplot(2, 3, 4)
        ax5 = fig.add_subplot(2, 3, 5)
        ax6 = fig.add_subplot(2, 3, 6)

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

        plt.tight_layout()
        save_and_maybe_show(plt, output_filename, dpi=150)

    return results


def main():
    config, _ = build_runtime_config()
    run_polarization_experiment(config)


if __name__ == '__main__':
    main()
