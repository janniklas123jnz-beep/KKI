"""
KKI Polarisierungs-Experiment: Konsensbildung und Lagerbildung im Schwarm
=========================================================================
Untersucht, wie sich Meinungen, Kooperation und Gruppenbildung in einem
Netzwerk-Schwarm gegenseitig beeinflussen.
"""

import os
import random
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import configure_simulation, save_and_maybe_show

# === KONFIGURATION ===
ANZAHL_AGENTEN = 60
RUNDEN = 180
VERBINDUNGEN_PRO_AGENT = 6
INTERAKTIONEN_PRO_RUNDE = 90
CONFIG, SEED = configure_simulation(
    {
        'RUNDEN': RUNDEN,
        'INTERAKTIONEN_PRO_RUNDE': INTERAKTIONEN_PRO_RUNDE,
    },
    np_module=np,
    plt_module=plt,
)
RUNDEN = CONFIG['RUNDEN']
INTERAKTIONEN_PRO_RUNDE = CONFIG['INTERAKTIONEN_PRO_RUNDE']

SZENARIO = os.getenv('KKI_POLARIZATION_SCENARIO', 'polarization').strip().lower()
GUELTIGE_SZENARIEN = {'polarization', 'consensus'}

if SZENARIO not in GUELTIGE_SZENARIEN:
    raise ValueError(
        f"Unbekanntes Szenario '{SZENARIO}'. Erlaubt: {', '.join(sorted(GUELTIGE_SZENARIEN))}"
    )


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


def szenario_titel():
    if SZENARIO == 'consensus':
        return 'KONSENS-SZENARIO'
    return 'POLARISIERUNGS-SZENARIO'


def erstelle_agenten():
    agenten = []
    gruppengroesse = ANZAHL_AGENTEN // 2

    for index in range(ANZAHL_AGENTEN):
        gruppe = 0 if index < gruppengroesse else 1

        if SZENARIO == 'consensus':
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


def erstelle_netzwerk(agenten):
    gruppen = {
        0: [agent for agent in agenten if agent.gruppe == 0],
        1: [agent for agent in agenten if agent.gruppe == 1],
    }

    for gruppen_agenten in gruppen.values():
        n = len(gruppen_agenten)
        for i in range(n):
            for j in range(1, VERBINDUNGEN_PRO_AGENT // 2 + 1):
                gruppen_agenten[i].verbinde(gruppen_agenten[(i + j) % n])

    ueberkreuz_chance = 0.35 if SZENARIO == 'consensus' else 0.08
    for agent in agenten:
        if random.random() < ueberkreuz_chance:
            andere_gruppe = [ziel for ziel in agenten if ziel.gruppe != agent.gruppe and ziel.id != agent.id]
            ziel = random.choice(andere_gruppe)
            agent.verbinde(ziel)

        if random.random() < 0.1:
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


def simulation():
    agenten = erstelle_agenten()
    agenten_dict = {agent.id: agent for agent in agenten}
    erstelle_netzwerk(agenten)

    print("=" * 78)
    print(f"KKI POLARISIERUNGS-EXPERIMENT: {szenario_titel()}")
    print("=" * 78)
    print(f"\nSzenario: {SZENARIO}")
    print(f"Agenten: {ANZAHL_AGENTEN}, Runden: {RUNDEN}, Interaktionen/Runde: {INTERAKTIONEN_PRO_RUNDE}")
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

    for runde in range(1, RUNDEN + 1):
        gruppenuebergreifende_interaktionen = 0

        for _ in range(INTERAKTIONEN_PRO_RUNDE):
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
        cross_group_history.append(gruppenuebergreifende_interaktionen / INTERAKTIONEN_PRO_RUNDE)

        if runde % 30 == 0:
            print(
                f"Runde {runde:3d}: PI={polarisierungs_index:.3f}, "
                f"Konsens={konsens_score:.3f}, Gruppenabstand={gruppenabstand:.3f}, "
                f"Links/Mitte/Rechts={links}/{mitte}/{rechts}"
            )

    print("\n" + "=" * 78)
    print("ERGEBNISSE")
    print("=" * 78)

    finale_pi = polarisierungs_history[-1]
    finaler_konsens = konsens_history[-1]
    finaler_abstand = gruppenabstand_history[-1]
    links, mitte, rechts = berechne_lager(agenten)

    print(f"\nFinaler Polarisierungs-Index: {finale_pi:.3f}")
    print(f"Finaler Konsens-Score:       {finaler_konsens:.3f}")
    print(f"Finaler Gruppenabstand:      {finaler_abstand:.3f}")
    print(f"Lagerverteilung:             Links={links}, Mitte={mitte}, Rechts={rechts}")
    print(f"Ø gruppenübergreifende Interaktionen: {np.mean(cross_group_history):.1%}")

    mean_group_a = np.mean([agent.meinung for agent in agenten if agent.gruppe == 0])
    mean_group_b = np.mean([agent.meinung for agent in agenten if agent.gruppe == 1])
    print(f"\nØ Meinung Gruppe 1: {mean_group_a:.3f}")
    print(f"Ø Meinung Gruppe 2: {mean_group_b:.3f}")

    if finale_pi > 0.22 and finaler_abstand > 0.35:
        print("\n⚡ Der Schwarm ist in stabile Lager polarisiert.")
    elif finaler_konsens > 0.72 and mitte > links and mitte > rechts:
        print("\n🤝 Der Schwarm hat eine robuste Konsenszone ausgebildet.")
    else:
        print("\n🔄 Der Schwarm bleibt in einer hybriden Zwischenphase aus Konsens und Lagerbildung.")

    fig = plt.figure(figsize=(18, 12))
    ax1 = fig.add_subplot(2, 3, 1)
    ax2 = fig.add_subplot(2, 3, 2)
    ax3 = fig.add_subplot(2, 3, 3)
    ax4 = fig.add_subplot(2, 3, 4)
    ax5 = fig.add_subplot(2, 3, 5)
    ax6 = fig.add_subplot(2, 3, 6)

    fig.suptitle(
        f'KKI Polarisierungs-Experiment: {szenario_titel()}',
        fontsize=14,
        fontweight='bold',
    )

    runden_x = list(range(RUNDEN + 1))

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
    ax2.plot(range(1, RUNDEN + 1), polarisierungs_history, color='#8E44AD', linewidth=2, label='Polarisierungs-Index')
    ax2.plot(range(1, RUNDEN + 1), konsens_history, color='#27AE60', linewidth=2, label='Konsens-Score')
    ax2.plot(range(1, RUNDEN + 1), gruppenabstand_history, color='#F39C12', linewidth=2, label='Gruppenabstand')
    ax2.set_ylim(0, 1)
    ax2.legend(loc='best', fontsize=8)
    ax2.grid(True, alpha=0.3)

    ax3.set_title('Lagerbildung über Zeit')
    ax3.set_xlabel('Runde')
    ax3.set_ylabel('Anzahl Agenten')
    ax3.fill_between(range(1, RUNDEN + 1), links_history, alpha=0.5, color='#3498DB', label='Links')
    ax3.fill_between(range(1, RUNDEN + 1), mitte_history, alpha=0.5, color='#95A5A6', label='Mitte')
    ax3.fill_between(range(1, RUNDEN + 1), rechts_history, alpha=0.5, color='#E74C3C', label='Rechts')
    ax3.set_ylim(0, ANZAHL_AGENTEN)
    ax3.legend(loc='upper right', fontsize=8)
    ax3.grid(True, alpha=0.3)

    ax4.set_title('Intelligenz nach Gruppen')
    ax4.set_xlabel('Runde')
    ax4.set_ylabel('Ø Intelligenz')
    ax4.plot(range(1, RUNDEN + 1), gruppe_a_intelligenz, color='#3498DB', linewidth=2, label='Gruppe 1')
    ax4.plot(range(1, RUNDEN + 1), gruppe_b_intelligenz, color='#E74C3C', linewidth=2, label='Gruppe 2')
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
    save_and_maybe_show(plt, 'kki_polarisierung.png', dpi=150)


if __name__ == '__main__':
    simulation()
