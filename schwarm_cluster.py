"""
KKI Cluster-Simulation: 50 Agenten mit Netzwerk-Topologie
==========================================================
Zeigt Clusterbildung: Kooperative Gruppen isolieren Defektoren
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
ANZAHL_AGENTEN = 50
ANZAHL_DEFEKTOREN = 8  # 16% Defektoren
RUNDEN = 200
VERBINDUNGEN_PRO_AGENT = 6  # Jeder kennt ~6 andere (Small World)
INTERAKTIONEN_PRO_RUNDE = 75
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
    """Ein Agent mit Nachbarschafts-Netzwerk."""
    
    def __init__(self, id, ist_defektor=False):
        self.id = id
        self.name = f"D{id}" if ist_defektor else f"A{id}"
        self.ist_defektor = ist_defektor
        self.kooperations_neigung = 0.2 if ist_defektor else 0.5
        self.intelligenz = 1.0
        self.nachbarn = set()  # Verbundene Agenten
        
        # Reputation im Netzwerk
        self.reputation = 0.5
        self.interaktions_history = defaultdict(list)  # Partner -> [C/D, ...]
        
        # Tracking
        self.intelligenz_history = [1.0]
        self.kooperation_history = [self.kooperations_neigung]
        self.cluster_id = None
    
    def verbinde(self, anderer):
        """Erstelle bidirektionale Verbindung."""
        self.nachbarn.add(anderer.id)
        anderer.nachbarn.add(self.id)
    
    def waehle_aktion(self, partner_reputation):
        """Wähle Aktion basierend auf eigener Neigung UND Partner-Reputation."""
        # Kooperiere eher mit Partnern guter Reputation
        effektive_neigung = self.kooperations_neigung * (0.5 + partner_reputation)
        effektive_neigung = min(0.95, effektive_neigung)
        
        if random.random() < effektive_neigung:
            return 'C'
        return 'D'
    
    def lerne(self, meine_aktion, andere_aktion, partner_id, partner_intelligenz):
        """Lerne aus Interaktion und aktualisiere Reputation."""
        # Speichere Interaktion
        self.interaktions_history[partner_id].append(andere_aktion)
        
        if meine_aktion == 'C' and andere_aktion == 'C':
            boost = 1.003 + (0.001 * min(partner_intelligenz, 3.0))
            self.intelligenz *= boost
            self.kooperations_neigung += 0.008
            self.reputation += 0.02
            
        elif meine_aktion == 'C' and andere_aktion == 'D':
            self.kooperations_neigung -= 0.003
            self.reputation += 0.01  # Ich war kooperativ
            
        elif meine_aktion == 'D' and andere_aktion == 'C':
            self.intelligenz *= 0.997
            self.reputation -= 0.03  # Reputation sinkt!
            
        elif meine_aktion == 'D' and andere_aktion == 'D':
            self.intelligenz *= 0.99
            self.kooperations_neigung += 0.005
            self.reputation -= 0.01
        
        # Grenzen
        self.kooperations_neigung = max(0.05, min(0.95, self.kooperations_neigung))
        self.intelligenz = max(0.1, min(5.0, self.intelligenz))
        self.reputation = max(0.0, min(1.0, self.reputation))
    
    def berechne_partner_reputation(self, partner_id):
        """Berechne Reputation eines Partners basierend auf History."""
        history = self.interaktions_history.get(partner_id, [])
        if not history:
            return 0.5  # Unbekannt = neutral
        # Anteil kooperativer Aktionen
        return sum(1 for a in history[-10:] if a == 'C') / len(history[-10:])
    
    def runde_beenden(self):
        self.intelligenz_history.append(self.intelligenz)
        self.kooperation_history.append(self.kooperations_neigung)


def erstelle_netzwerk(agenten):
    """Erstelle Small-World Netzwerk."""
    n = len(agenten)
    
    # Ring-Topologie als Basis
    for i in range(n):
        for j in range(1, VERBINDUNGEN_PRO_AGENT // 2 + 1):
            agenten[i].verbinde(agenten[(i + j) % n])
    
    # Zufällige Shortcuts (Small World)
    for agent in agenten:
        if random.random() < 0.1:  # 10% Chance für Shortcut
            ziel = random.choice(agenten)
            if ziel.id != agent.id:
                agent.verbinde(ziel)


def finde_cluster(agenten):
    """Finde Cluster basierend auf Kooperationsneigung."""
    # Einfache Cluster: Hohe vs. niedrige Kooperation
    cluster = {'kooperativ': [], 'neutral': [], 'defektierend': []}
    
    for agent in agenten:
        if agent.kooperations_neigung > 0.7:
            cluster['kooperativ'].append(agent)
            agent.cluster_id = 'K'
        elif agent.kooperations_neigung < 0.4:
            cluster['defektierend'].append(agent)
            agent.cluster_id = 'D'
        else:
            cluster['neutral'].append(agent)
            agent.cluster_id = 'N'
    
    return cluster


def simulation():
    """Hauptsimulation."""
    
    # Erstelle Agenten
    agenten = []
    for i in range(ANZAHL_AGENTEN):
        ist_defektor = i >= (ANZAHL_AGENTEN - ANZAHL_DEFEKTOREN)
        agent = Agent(i, ist_defektor)
        agenten.append(agent)
    
    agenten_dict = {a.id: a for a in agenten}
    
    # Erstelle Netzwerk
    erstelle_netzwerk(agenten)
    
    print("=" * 70)
    print("KKI CLUSTER-SIMULATION: 50 AGENTEN MIT NETZWERK")
    print("=" * 70)
    print(f"\nAgenten: {ANZAHL_AGENTEN} (davon {ANZAHL_DEFEKTOREN} Defektoren)")
    print(f"Verbindungen pro Agent: ~{VERBINDUNGEN_PRO_AGENT}")
    print(f"Runden: {RUNDEN}")
    print("\nSimulation läuft...\n")
    
    # Tracking
    schwarm_phi_history = []
    cluster_history = {'kooperativ': [], 'neutral': [], 'defektierend': []}
    
    for runde in range(1, RUNDEN + 1):
        # Interaktionen: Agenten interagieren mit Nachbarn
        for _ in range(INTERAKTIONEN_PRO_RUNDE):
            # Wähle zufälligen Agenten
            agent = random.choice(agenten)
            
            # Wähle Nachbarn (oder zufällig mit kleiner Chance)
            if agent.nachbarn and random.random() < 0.9:
                partner_id = random.choice(list(agent.nachbarn))
            else:
                partner_id = random.choice([a.id for a in agenten if a.id != agent.id])
            
            partner = agenten_dict[partner_id]
            
            # Berechne Reputation
            agent_rep = partner.berechne_partner_reputation(agent.id)
            partner_rep = agent.berechne_partner_reputation(partner.id)
            
            # Aktionen
            aktion_a = agent.waehle_aktion(partner_rep)
            aktion_p = partner.waehle_aktion(agent_rep)
            
            # Lernen
            agent.lerne(aktion_a, aktion_p, partner.id, partner.intelligenz)
            partner.lerne(aktion_p, aktion_a, agent.id, agent.intelligenz)
        
        # Runde beenden
        for agent in agenten:
            agent.runde_beenden()
        
        # Statistiken
        schwarm_phi = np.mean([a.intelligenz for a in agenten])
        schwarm_phi_history.append(schwarm_phi)
        
        cluster = finde_cluster(agenten)
        cluster_history['kooperativ'].append(len(cluster['kooperativ']))
        cluster_history['neutral'].append(len(cluster['neutral']))
        cluster_history['defektierend'].append(len(cluster['defektierend']))
        
        if runde % 40 == 0:
            avg_koop = np.mean([a.kooperations_neigung for a in agenten])
            print(f"Runde {runde:3d}: Φ={schwarm_phi:.2f}, Koop={avg_koop:.1%}, "
                  f"Cluster: K={len(cluster['kooperativ'])}, "
                  f"N={len(cluster['neutral'])}, D={len(cluster['defektierend'])}")
    
    # === ERGEBNISSE ===
    print("\n" + "=" * 70)
    print("ERGEBNISSE")
    print("=" * 70)
    
    # Sortiere nach Intelligenz
    normale = [a for a in agenten if not a.ist_defektor]
    defektoren = [a for a in agenten if a.ist_defektor]
    
    avg_normal = np.mean([a.intelligenz for a in normale])
    avg_defekt = np.mean([a.intelligenz for a in defektoren])
    avg_rep_normal = np.mean([a.reputation for a in normale])
    avg_rep_defekt = np.mean([a.reputation for a in defektoren])
    
    print(f"\n{'Metrik':<25} {'Normale':>12} {'Defektoren':>12} {'Differenz':>12}")
    print("-" * 65)
    print(f"{'Ø Intelligenz':<25} {avg_normal:>12.2f} {avg_defekt:>12.2f} {avg_normal-avg_defekt:>12.2f}")
    print(f"{'Ø Reputation':<25} {avg_rep_normal:>12.2f} {avg_rep_defekt:>12.2f} {avg_rep_normal-avg_rep_defekt:>12.2f}")
    print(f"{'Ø Kooperationsneigung':<25} {np.mean([a.kooperations_neigung for a in normale]):>12.1%} "
          f"{np.mean([a.kooperations_neigung for a in defektoren]):>12.1%}")
    
    final_cluster = finde_cluster(agenten)
    print(f"\nFinale Cluster-Verteilung:")
    print(f"  Kooperativ (>70%):    {len(final_cluster['kooperativ']):3d} Agenten")
    print(f"  Neutral (40-70%):     {len(final_cluster['neutral']):3d} Agenten")
    print(f"  Defektierend (<40%):  {len(final_cluster['defektierend']):3d} Agenten")
    
    # Wie viele ursprüngliche Defektoren sind jetzt kooperativ?
    bekehrte = sum(1 for a in defektoren if a.kooperations_neigung > 0.7)
    print(f"\n'Bekehrte' Defektoren:  {bekehrte}/{ANZAHL_DEFEKTOREN}")
    
    if avg_normal > avg_defekt * 1.3:
        print("\n✓ KOOPERATION DOMINIERT - Defektoren wurden marginalisiert!")
    
    # === VISUALISIERUNG ===
    fig = plt.figure(figsize=(16, 12))
    
    # Layout: 2x2 oben, 1 breit unten
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)
    
    fig.suptitle('KKI Cluster-Simulation: Emergenz kooperativer Netzwerke (50 Agenten)', 
                 fontsize=14, fontweight='bold')
    
    runden_x = list(range(RUNDEN + 1))
    
    # --- Graph 1: Intelligenz alle Agenten ---
    ax1.set_title('Individuelle Intelligenz')
    ax1.set_ylabel('Intelligenz (Φ)')
    
    for agent in agenten:
        alpha = 0.8 if agent.ist_defektor else 0.3
        color = '#E74C3C' if agent.ist_defektor else '#3498DB'
        linestyle = '--' if agent.ist_defektor else '-'
        linewidth = 1.5 if agent.ist_defektor else 0.5
        ax1.plot(runden_x, agent.intelligenz_history, 
                color=color, alpha=alpha, linestyle=linestyle, linewidth=linewidth)
    
    ax1.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    ax1.set_ylim(0, max(3.0, max(a.intelligenz for a in agenten) * 1.1))
    ax1.grid(True, alpha=0.3)
    
    # Legende
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='#3498DB', label='Normale'),
        Line2D([0], [0], color='#E74C3C', linestyle='--', label='Defektoren')
    ]
    ax1.legend(handles=legend_elements, loc='upper left')
    
    # --- Graph 2: Cluster-Entwicklung ---
    ax2.set_title('Cluster-Entwicklung über Zeit')
    ax2.set_ylabel('Anzahl Agenten')
    
    ax2.fill_between(range(1, RUNDEN + 1), cluster_history['kooperativ'], 
                     alpha=0.5, color='#2ECC71', label='Kooperativ')
    ax2.fill_between(range(1, RUNDEN + 1), cluster_history['neutral'],
                     alpha=0.5, color='#F39C12', label='Neutral')
    ax2.fill_between(range(1, RUNDEN + 1), cluster_history['defektierend'],
                     alpha=0.5, color='#E74C3C', label='Defektierend')
    
    ax2.set_ylim(0, ANZAHL_AGENTEN)
    ax2.legend(loc='center right')
    ax2.grid(True, alpha=0.3)
    
    # --- Graph 3: Schwarm-Intelligenz ---
    ax3.set_title('Schwarm-Intelligenz (Durchschnitt)')
    ax3.set_xlabel('Runde')
    ax3.set_ylabel('Schwarm-Φ')
    
    ax3.fill_between(range(1, RUNDEN + 1), schwarm_phi_history, 
                     alpha=0.3, color='#9B59B6')
    ax3.plot(range(1, RUNDEN + 1), schwarm_phi_history, 
             color='#8E44AD', linewidth=2)
    ax3.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    ax3.grid(True, alpha=0.3)
    
    # --- Graph 4: Finale Verteilung (Scatter) ---
    ax4.set_title('Finale Position: Intelligenz vs. Reputation')
    ax4.set_xlabel('Reputation')
    ax4.set_ylabel('Intelligenz')
    
    for agent in agenten:
        color = '#E74C3C' if agent.ist_defektor else '#3498DB'
        marker = 'x' if agent.ist_defektor else 'o'
        size = 100 if agent.ist_defektor else 50
        ax4.scatter(agent.reputation, agent.intelligenz, 
                   c=color, marker=marker, s=size, alpha=0.7)
    
    ax4.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    ax4.axvline(x=0.5, color='gray', linestyle=':', alpha=0.5)
    ax4.set_xlim(0, 1)
    ax4.grid(True, alpha=0.3)
    
    # Quadranten beschriften
    ax4.text(0.75, ax4.get_ylim()[1]*0.9, 'Erfolgreiche\nKooperateure', 
             ha='center', fontsize=9, color='#27AE60')
    ax4.text(0.25, ax4.get_ylim()[0]+0.1, 'Gescheiterte\nDefektoren', 
             ha='center', fontsize=9, color='#E74C3C')
    
    plt.tight_layout()
    save_and_maybe_show(plt, 'kki_cluster_simulation.png', dpi=150)


if __name__ == "__main__":
    simulation()
