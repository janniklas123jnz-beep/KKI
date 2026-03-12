"""
KKI Große Schwarm-Simulation: 100 Agenten
==========================================
Testet Skalierbarkeit und emergente Strukturen bei größerem Schwarm
"""

import random
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

from kki_runtime import (
    configure_simulation,
    save_and_maybe_show,
)

# === KONFIGURATION ===
ANZAHL_AGENTEN = 100
ANZAHL_DEFEKTOREN = 15  # 15% Defektoren
RUNDEN = 250
VERBINDUNGEN_PRO_AGENT = 8  # Etwas mehr Verbindungen bei größerem Netzwerk
INTERAKTIONEN_PRO_RUNDE = 150  # Mehr Interaktionen
CONFIG, SEED = configure_simulation({
    'RUNDEN': RUNDEN,
    'INTERAKTIONEN_PRO_RUNDE': INTERAKTIONEN_PRO_RUNDE,
}, np_module=np, plt_module=plt)
RUNDEN = CONFIG['RUNDEN']
INTERAKTIONEN_PRO_RUNDE = CONFIG['INTERAKTIONEN_PRO_RUNDE']

# Payoff-Matrix
PAYOFFS = {
    ('C', 'C'): 3,
    ('C', 'D'): 0,
    ('D', 'C'): 5,
    ('D', 'D'): 1,
}


class Agent:
    """Ein Agent mit Nachbarschafts-Netzwerk und Gedächtnis."""
    
    def __init__(self, id, ist_defektor=False):
        self.id = id
        self.name = f"D{id}" if ist_defektor else f"A{id}"
        self.ist_defektor = ist_defektor
        self.kooperations_neigung = 0.15 if ist_defektor else 0.5
        self.intelligenz = 1.0
        self.nachbarn = set()
        
        # Reputation und Gedächtnis
        self.reputation = 0.5
        self.interaktions_history = defaultdict(list)
        self.gesamt_kooperationen = 0
        self.gesamt_interaktionen = 0
        
        # Tracking
        self.intelligenz_history = [1.0]
        self.kooperation_history = [self.kooperations_neigung]
        self.reputation_history = [0.5]
    
    def verbinde(self, anderer):
        self.nachbarn.add(anderer.id)
        anderer.nachbarn.add(self.id)
    
    def waehle_aktion(self, partner_reputation):
        """Intelligentere Entscheidung basierend auf Reputation."""
        # Je höher meine eigene Intelligenz, desto besser kann ich Reputation einschätzen
        reputation_gewicht = min(1.0, self.intelligenz / 2.0)
        effektive_neigung = self.kooperations_neigung * (1 - reputation_gewicht) + \
                           self.kooperations_neigung * partner_reputation * reputation_gewicht
        effektive_neigung = max(0.05, min(0.95, effektive_neigung))
        
        if random.random() < effektive_neigung:
            return 'C'
        return 'D'
    
    def lerne(self, meine_aktion, andere_aktion, partner_id, partner_intelligenz):
        """Erweitertes Lernen mit Schwarm-Effekt."""
        self.interaktions_history[partner_id].append(andere_aktion)
        self.gesamt_interaktionen += 1
        
        if meine_aktion == 'C':
            self.gesamt_kooperationen += 1
        
        if meine_aktion == 'C' and andere_aktion == 'C':
            # Synergie: Boost proportional zur kombinierten Intelligenz
            synergie = 1.0 + (partner_intelligenz * 0.002)
            self.intelligenz *= 1.002 * synergie
            self.kooperations_neigung += 0.006
            self.reputation += 0.015
            
        elif meine_aktion == 'C' and andere_aktion == 'D':
            # Wurde ausgenutzt - leichte Anpassung
            self.kooperations_neigung -= 0.002
            self.reputation += 0.005
            
        elif meine_aktion == 'D' and andere_aktion == 'C':
            # Habe ausgenutzt - Intelligenz sinkt, Reputation leidet
            self.intelligenz *= 0.998
            self.reputation -= 0.025
            
        elif meine_aktion == 'D' and andere_aktion == 'D':
            # Gegenseitige Destruktion
            self.intelligenz *= 0.992
            self.kooperations_neigung += 0.003
            self.reputation -= 0.008
        
        # Grenzen
        self.kooperations_neigung = max(0.05, min(0.95, self.kooperations_neigung))
        self.intelligenz = max(0.1, min(8.0, self.intelligenz))  # Höheres Max für 100 Agenten
        self.reputation = max(0.0, min(1.0, self.reputation))
    
    def berechne_partner_reputation(self, partner_id):
        history = self.interaktions_history.get(partner_id, [])
        if not history:
            return 0.5
        return sum(1 for a in history[-15:] if a == 'C') / len(history[-15:])
    
    def runde_beenden(self):
        self.intelligenz_history.append(self.intelligenz)
        self.kooperation_history.append(self.kooperations_neigung)
        self.reputation_history.append(self.reputation)


def erstelle_netzwerk(agenten):
    """Small-World Netzwerk mit Clustering."""
    n = len(agenten)
    
    # Ring-Topologie
    for i in range(n):
        for j in range(1, VERBINDUNGEN_PRO_AGENT // 2 + 1):
            agenten[i].verbinde(agenten[(i + j) % n])
    
    # Shortcuts für Small-World Eigenschaft
    for agent in agenten:
        if random.random() < 0.15:
            ziel = random.choice(agenten)
            if ziel.id != agent.id and ziel.id not in agent.nachbarn:
                agent.verbinde(ziel)


def berechne_netzwerk_stats(agenten):
    """Berechne Netzwerk-Statistiken."""
    avg_verbindungen = np.mean([len(a.nachbarn) for a in agenten])
    
    # Clustering-Koeffizient (vereinfacht)
    clustering = []
    for agent in agenten:
        if len(agent.nachbarn) < 2:
            continue
        nachbar_ids = list(agent.nachbarn)
        verbindungen = 0
        moegliche = len(nachbar_ids) * (len(nachbar_ids) - 1) / 2
        for i, n1 in enumerate(nachbar_ids):
            for n2 in nachbar_ids[i+1:]:
                if n2 in agenten[n1].nachbarn:
                    verbindungen += 1
        if moegliche > 0:
            clustering.append(verbindungen / moegliche)
    
    return avg_verbindungen, np.mean(clustering) if clustering else 0


def simulation():
    """Hauptsimulation mit 100 Agenten."""
    
    # Erstelle Agenten - Defektoren zufällig verteilt
    alle_ids = list(range(ANZAHL_AGENTEN))
    random.shuffle(alle_ids)
    defektor_ids = set(alle_ids[:ANZAHL_DEFEKTOREN])
    
    agenten = []
    for i in range(ANZAHL_AGENTEN):
        ist_defektor = i in defektor_ids
        agent = Agent(i, ist_defektor)
        agenten.append(agent)
    
    agenten_dict = {a.id: a for a in agenten}
    
    # Netzwerk erstellen
    erstelle_netzwerk(agenten)
    avg_verb, clustering = berechne_netzwerk_stats(agenten)
    
    print("=" * 70)
    print("KKI GROSSE SCHWARM-SIMULATION: 100 AGENTEN")
    print("=" * 70)
    print(f"\nAgenten: {ANZAHL_AGENTEN} (davon {ANZAHL_DEFEKTOREN} Defektoren = {ANZAHL_DEFEKTOREN}%)")
    print(f"Netzwerk: Ø {avg_verb:.1f} Verbindungen, Clustering = {clustering:.2f}")
    print(f"Runden: {RUNDEN}, Interaktionen/Runde: {INTERAKTIONEN_PRO_RUNDE}")
    print("\nSimulation läuft...\n")
    
    # Tracking
    schwarm_phi_history = []
    normale_phi_history = []
    defektor_phi_history = []
    kooperation_rate_history = []
    
    for runde in range(1, RUNDEN + 1):
        runden_kooperationen = 0
        runden_interaktionen = 0
        
        for _ in range(INTERAKTIONEN_PRO_RUNDE):
            agent = random.choice(agenten)
            
            # 85% Chance mit Nachbar, 15% mit Fremdem
            if agent.nachbarn and random.random() < 0.85:
                partner_id = random.choice(list(agent.nachbarn))
            else:
                partner_id = random.choice([a.id for a in agenten if a.id != agent.id])
            
            partner = agenten_dict[partner_id]
            
            # Reputationen
            agent_rep = partner.berechne_partner_reputation(agent.id)
            partner_rep = agent.berechne_partner_reputation(partner.id)
            
            # Aktionen
            aktion_a = agent.waehle_aktion(partner_rep)
            aktion_p = partner.waehle_aktion(agent_rep)
            
            # Tracking
            if aktion_a == 'C':
                runden_kooperationen += 1
            if aktion_p == 'C':
                runden_kooperationen += 1
            runden_interaktionen += 2
            
            # Lernen
            agent.lerne(aktion_a, aktion_p, partner.id, partner.intelligenz)
            partner.lerne(aktion_p, aktion_a, agent.id, agent.intelligenz)
        
        # Runde beenden
        for agent in agenten:
            agent.runde_beenden()
        
        # Statistiken
        normale = [a for a in agenten if not a.ist_defektor]
        defektoren = [a for a in agenten if a.ist_defektor]
        
        schwarm_phi = np.mean([a.intelligenz for a in agenten])
        normale_phi = np.mean([a.intelligenz for a in normale])
        defektor_phi = np.mean([a.intelligenz for a in defektoren])
        koop_rate = runden_kooperationen / runden_interaktionen if runden_interaktionen > 0 else 0
        
        schwarm_phi_history.append(schwarm_phi)
        normale_phi_history.append(normale_phi)
        defektor_phi_history.append(defektor_phi)
        kooperation_rate_history.append(koop_rate)
        
        if runde % 50 == 0:
            print(f"Runde {runde:3d}: Schwarm-Φ={schwarm_phi:.2f}, "
                  f"Normale={normale_phi:.2f}, Defektoren={defektor_phi:.2f}, "
                  f"Koop-Rate={koop_rate:.1%}")
    
    # === ERGEBNISSE ===
    print("\n" + "=" * 70)
    print("FINALE ERGEBNISSE")
    print("=" * 70)
    
    normale = [a for a in agenten if not a.ist_defektor]
    defektoren = [a for a in agenten if a.ist_defektor]
    
    # Top 10 und Bottom 10
    sortiert = sorted(agenten, key=lambda a: a.intelligenz, reverse=True)
    
    print(f"\n{'=== TOP 10 AGENTEN ==='}")
    print(f"{'Agent':<8} {'Typ':<10} {'Intelligenz':>12} {'Reputation':>12} {'Koop-Rate':>12}")
    print("-" * 56)
    for agent in sortiert[:10]:
        typ = "DEFEKTOR" if agent.ist_defektor else "Normal"
        koop_rate = agent.gesamt_kooperationen / agent.gesamt_interaktionen if agent.gesamt_interaktionen > 0 else 0
        print(f"{agent.name:<8} {typ:<10} {agent.intelligenz:>12.2f} {agent.reputation:>12.2f} {koop_rate:>12.1%}")
    
    print(f"\n{'=== BOTTOM 10 AGENTEN ==='}")
    print(f"{'Agent':<8} {'Typ':<10} {'Intelligenz':>12} {'Reputation':>12} {'Koop-Rate':>12}")
    print("-" * 56)
    for agent in sortiert[-10:]:
        typ = "DEFEKTOR" if agent.ist_defektor else "Normal"
        koop_rate = agent.gesamt_kooperationen / agent.gesamt_interaktionen if agent.gesamt_interaktionen > 0 else 0
        print(f"{agent.name:<8} {typ:<10} {agent.intelligenz:>12.2f} {agent.reputation:>12.2f} {koop_rate:>12.1%}")
    
    # Statistiken
    avg_normal_phi = np.mean([a.intelligenz for a in normale])
    avg_defekt_phi = np.mean([a.intelligenz for a in defektoren])
    avg_normal_rep = np.mean([a.reputation for a in normale])
    avg_defekt_rep = np.mean([a.reputation for a in defektoren])
    
    print(f"\n{'=== GRUPPENVERGLEICH ==='}")
    print(f"{'Metrik':<25} {'Normale (85)':>15} {'Defektoren (15)':>15} {'Differenz':>12}")
    print("-" * 70)
    print(f"{'Ø Intelligenz':<25} {avg_normal_phi:>15.2f} {avg_defekt_phi:>15.2f} {avg_normal_phi-avg_defekt_phi:>12.2f}")
    print(f"{'Ø Reputation':<25} {avg_normal_rep:>15.2f} {avg_defekt_rep:>15.2f} {avg_normal_rep-avg_defekt_rep:>12.2f}")
    
    # Wie viele Defektoren unter Durchschnitt?
    schwarm_avg = np.mean([a.intelligenz for a in agenten])
    defektoren_unter_avg = sum(1 for a in defektoren if a.intelligenz < schwarm_avg)
    print(f"\nDefektoren unter Schwarm-Durchschnitt: {defektoren_unter_avg}/{ANZAHL_DEFEKTOREN}")
    
    if avg_normal_phi > avg_defekt_phi * 1.5:
        print("\n🐝 SCHWARM-DOMINANZ: Kooperateure haben Defektoren klar übertroffen!")
    
    # === VISUALISIERUNG ===
    fig = plt.figure(figsize=(18, 12))
    
    ax1 = fig.add_subplot(2, 3, 1)
    ax2 = fig.add_subplot(2, 3, 2)
    ax3 = fig.add_subplot(2, 3, 3)
    ax4 = fig.add_subplot(2, 3, 4)
    ax5 = fig.add_subplot(2, 3, 5)
    ax6 = fig.add_subplot(2, 3, 6)
    
    fig.suptitle('KKI Schwarm-Simulation: 100 Agenten – Emergenz kollektiver Intelligenz', 
                 fontsize=14, fontweight='bold')
    
    runden_x = list(range(RUNDEN + 1))
    
    # --- Graph 1: Alle Intelligenz-Verläufe ---
    ax1.set_title('Individuelle Intelligenz (100 Agenten)')
    ax1.set_ylabel('Intelligenz (Φ)')
    ax1.set_xlabel('Runde')
    
    for agent in agenten:
        color = '#E74C3C' if agent.ist_defektor else '#3498DB'
        alpha = 0.7 if agent.ist_defektor else 0.2
        linewidth = 1.2 if agent.ist_defektor else 0.4
        ax1.plot(runden_x, agent.intelligenz_history, color=color, alpha=alpha, linewidth=linewidth)
    
    ax1.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    ax1.grid(True, alpha=0.3)
    
    # --- Graph 2: Gruppendurchschnitte ---
    ax2.set_title('Intelligenz: Normale vs. Defektoren')
    ax2.set_ylabel('Ø Intelligenz')
    ax2.set_xlabel('Runde')
    
    ax2.plot(range(1, RUNDEN + 1), normale_phi_history, color='#3498DB', 
             linewidth=2.5, label=f'Normale (n={len(normale)})')
    ax2.plot(range(1, RUNDEN + 1), defektor_phi_history, color='#E74C3C', 
             linewidth=2.5, linestyle='--', label=f'Defektoren (n={len(defektoren)})')
    ax2.fill_between(range(1, RUNDEN + 1), normale_phi_history, defektor_phi_history, 
                     alpha=0.2, color='#2ECC71')
    
    ax2.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # --- Graph 3: Kooperationsrate ---
    ax3.set_title('Kooperationsrate über Zeit')
    ax3.set_ylabel('Kooperationsrate')
    ax3.set_xlabel('Runde')
    
    ax3.fill_between(range(1, RUNDEN + 1), kooperation_rate_history, alpha=0.3, color='#2ECC71')
    ax3.plot(range(1, RUNDEN + 1), kooperation_rate_history, color='#27AE60', linewidth=2)
    ax3.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5)
    ax3.set_ylim(0, 1)
    ax3.grid(True, alpha=0.3)
    
    # --- Graph 4: Schwarm-Intelligenz ---
    ax4.set_title('Schwarm-Intelligenz (Gesamt)')
    ax4.set_ylabel('Schwarm-Φ')
    ax4.set_xlabel('Runde')
    
    ax4.fill_between(range(1, RUNDEN + 1), schwarm_phi_history, alpha=0.3, color='#9B59B6')
    ax4.plot(range(1, RUNDEN + 1), schwarm_phi_history, color='#8E44AD', linewidth=2)
    ax4.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    ax4.grid(True, alpha=0.3)
    
    # --- Graph 5: Scatter Intelligenz vs Reputation ---
    ax5.set_title('Finale Position: Intelligenz vs. Reputation')
    ax5.set_xlabel('Reputation')
    ax5.set_ylabel('Intelligenz')
    
    for agent in agenten:
        color = '#E74C3C' if agent.ist_defektor else '#3498DB'
        marker = 'X' if agent.ist_defektor else 'o'
        size = 80 if agent.ist_defektor else 30
        ax5.scatter(agent.reputation, agent.intelligenz, c=color, marker=marker, s=size, alpha=0.7)
    
    ax5.axhline(y=1.0, color='gray', linestyle=':', alpha=0.3)
    ax5.axvline(x=0.5, color='gray', linestyle=':', alpha=0.3)
    ax5.grid(True, alpha=0.3)
    
    # --- Graph 6: Histogramm finale Intelligenz ---
    ax6.set_title('Verteilung finale Intelligenz')
    ax6.set_xlabel('Intelligenz')
    ax6.set_ylabel('Anzahl Agenten')
    
    normale_intel = [a.intelligenz for a in normale]
    defekt_intel = [a.intelligenz for a in defektoren]
    
    ax6.hist(normale_intel, bins=20, alpha=0.6, color='#3498DB', label='Normale', edgecolor='black')
    ax6.hist(defekt_intel, bins=10, alpha=0.6, color='#E74C3C', label='Defektoren', edgecolor='black')
    ax6.axvline(x=np.mean(normale_intel), color='#2980B9', linestyle='--', linewidth=2, label=f'Ø Normale: {np.mean(normale_intel):.2f}')
    ax6.axvline(x=np.mean(defekt_intel), color='#C0392B', linestyle='--', linewidth=2, label=f'Ø Defektoren: {np.mean(defekt_intel):.2f}')
    ax6.legend(loc='upper right', fontsize=8)
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    save_and_maybe_show(plt, 'kki_100_agenten.png', dpi=150)


if __name__ == "__main__":
    simulation()
