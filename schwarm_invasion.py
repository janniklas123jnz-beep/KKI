"""
KKI Invasions-Test: Was passiert wenn Defektoren einen stabilen Schwarm infiltrieren?
======================================================================================
Testet die Robustheit des kooperativen Schwarms gegen plötzliche Störungen
"""

import random
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

from kki_runtime import (
    apply_test_overrides,
    configure_matplotlib,
    initialize_runtime,
    save_and_maybe_show,
)

configure_matplotlib(plt)

# === KONFIGURATION ===
ANZAHL_AGENTEN_START = 80
ANZAHL_INVASOREN = 20  # 20 neue Defektoren nach Stabilisierung
INVASION_RUNDE = 100   # Wann die Invasion startet
RUNDEN_GESAMT = 300
VERBINDUNGEN_PRO_AGENT = 8
INTERAKTIONEN_PRO_RUNDE = 120
TEST_OVERRIDES = apply_test_overrides({
    'INVASION_RUNDE': INVASION_RUNDE,
    'RUNDEN_GESAMT': RUNDEN_GESAMT,
    'INTERAKTIONEN_PRO_RUNDE': INTERAKTIONEN_PRO_RUNDE,
})
INVASION_RUNDE = TEST_OVERRIDES['INVASION_RUNDE']
RUNDEN_GESAMT = TEST_OVERRIDES['RUNDEN_GESAMT']
INTERAKTIONEN_PRO_RUNDE = TEST_OVERRIDES['INTERAKTIONEN_PRO_RUNDE']
SEED = initialize_runtime(np)

PAYOFFS = {
    ('C', 'C'): 3,
    ('C', 'D'): 0,
    ('D', 'C'): 5,
    ('D', 'D'): 1,
}


class Agent:
    """Agent mit Netzwerk und Gedächtnis."""
    
    def __init__(self, id, ist_defektor=False, ist_invasor=False):
        self.id = id
        self.ist_defektor = ist_defektor
        self.ist_invasor = ist_invasor  # Neu: Markierung für Invasoren
        
        if ist_invasor:
            self.name = f"INV{id}"
            self.kooperations_neigung = 0.1  # Sehr aggressiv
        elif ist_defektor:
            self.name = f"D{id}"
            self.kooperations_neigung = 0.2
        else:
            self.name = f"A{id}"
            self.kooperations_neigung = 0.5
            
        self.intelligenz = 1.0
        self.nachbarn = set()
        self.reputation = 0.5
        self.interaktions_history = defaultdict(list)
        self.geboren_runde = 0
        
        # Tracking
        self.intelligenz_history = []
        self.kooperation_history = []
        self.reputation_history = []
    
    def verbinde(self, anderer):
        self.nachbarn.add(anderer.id)
        anderer.nachbarn.add(self.id)
    
    def trenne(self, anderer_id):
        """Trenne Verbindung zu Agent mit schlechter Reputation."""
        self.nachbarn.discard(anderer_id)
    
    def waehle_aktion(self, partner_reputation):
        reputation_gewicht = min(1.0, self.intelligenz / 2.0)
        effektive_neigung = self.kooperations_neigung * (1 - reputation_gewicht * 0.5) + \
                           self.kooperations_neigung * partner_reputation * reputation_gewicht * 0.5
        effektive_neigung = max(0.05, min(0.95, effektive_neigung))
        
        if random.random() < effektive_neigung:
            return 'C'
        return 'D'
    
    def lerne(self, meine_aktion, andere_aktion, partner_id, partner_intelligenz):
        self.interaktions_history[partner_id].append(andere_aktion)
        
        if meine_aktion == 'C' and andere_aktion == 'C':
            synergie = 1.0 + (partner_intelligenz * 0.002)
            self.intelligenz *= 1.002 * synergie
            self.kooperations_neigung += 0.005
            self.reputation += 0.012
            
        elif meine_aktion == 'C' and andere_aktion == 'D':
            self.kooperations_neigung -= 0.002
            self.reputation += 0.003
            
        elif meine_aktion == 'D' and andere_aktion == 'C':
            self.intelligenz *= 0.997
            self.reputation -= 0.02
            
        elif meine_aktion == 'D' and andere_aktion == 'D':
            self.intelligenz *= 0.99
            self.kooperations_neigung += 0.004
            self.reputation -= 0.01
        
        self.kooperations_neigung = max(0.05, min(0.95, self.kooperations_neigung))
        self.intelligenz = max(0.1, min(8.0, self.intelligenz))
        self.reputation = max(0.0, min(1.0, self.reputation))
    
    def berechne_partner_reputation(self, partner_id):
        history = self.interaktions_history.get(partner_id, [])
        if not history:
            return 0.5
        return sum(1 for a in history[-12:] if a == 'C') / len(history[-12:])
    
    def runde_beenden(self):
        self.intelligenz_history.append(self.intelligenz)
        self.kooperation_history.append(self.kooperations_neigung)
        self.reputation_history.append(self.reputation)


def erstelle_netzwerk(agenten, neue_agenten=None):
    """Erstelle oder erweitere Netzwerk."""
    if neue_agenten is None:
        # Initiales Netzwerk
        n = len(agenten)
        for i in range(n):
            for j in range(1, VERBINDUNGEN_PRO_AGENT // 2 + 1):
                agenten[i].verbinde(agenten[(i + j) % n])
        
        for agent in agenten:
            if random.random() < 0.15:
                ziel = random.choice(agenten)
                if ziel.id != agent.id:
                    agent.verbinde(ziel)
    else:
        # Invasoren verbinden sich mit existierenden Agenten
        alle_agenten = agenten + neue_agenten
        for invasor in neue_agenten:
            # Jeder Invasor verbindet sich mit zufälligen existierenden Agenten
            targets = random.sample(agenten, min(VERBINDUNGEN_PRO_AGENT, len(agenten)))
            for target in targets:
                invasor.verbinde(target)


def simulation():
    """Invasions-Simulation."""
    
    # Phase 1: Erstelle stabilen kooperativen Schwarm
    agenten = []
    for i in range(ANZAHL_AGENTEN_START):
        # Nur 5 ursprüngliche Defektoren (6.25%)
        ist_defektor = i >= (ANZAHL_AGENTEN_START - 5)
        agent = Agent(i, ist_defektor=ist_defektor)
        agent.geboren_runde = 0
        agenten.append(agent)
    
    agenten_dict = {a.id: a for a in agenten}
    erstelle_netzwerk(agenten)
    
    print("=" * 75)
    print("KKI INVASIONS-TEST: ROBUSTHEIT DES KOOPERATIVEN SCHWARMS")
    print("=" * 75)
    print(f"\nPhase 1 (Runde 1-{INVASION_RUNDE}): Schwarm stabilisiert sich")
    print(f"  → {ANZAHL_AGENTEN_START} Agenten (davon 5 Defektoren)")
    print(f"\nPhase 2 (Runde {INVASION_RUNDE}): 💥 INVASION!")
    print(f"  → {ANZAHL_INVASOREN} aggressive Defektoren treten bei")
    print(f"\nPhase 3 (Runde {INVASION_RUNDE}-{RUNDEN_GESAMT}): Schwarm-Reaktion")
    print("\nSimulation läuft...\n")
    
    # Tracking
    schwarm_phi_history = []
    urspruengliche_phi_history = []
    invasoren_phi_history = []
    kooperation_rate_history = []
    anzahl_agenten_history = []
    
    invasoren = []
    invasion_erfolgt = False
    
    for runde in range(1, RUNDEN_GESAMT + 1):
        
        # === INVASION in Runde 100 ===
        if runde == INVASION_RUNDE and not invasion_erfolgt:
            print(f"\n{'='*50}")
            print(f"💥 RUNDE {INVASION_RUNDE}: INVASION BEGINNT!")
            print(f"{'='*50}")
            
            # Status vor Invasion
            avg_phi_vor = np.mean([a.intelligenz for a in agenten])
            avg_koop_vor = np.mean([a.kooperations_neigung for a in agenten])
            print(f"Schwarm vor Invasion: Φ={avg_phi_vor:.2f}, Koop={avg_koop_vor:.1%}")
            
            # Erstelle Invasoren
            naechste_id = max(a.id for a in agenten) + 1
            for i in range(ANZAHL_INVASOREN):
                invasor = Agent(naechste_id + i, ist_defektor=True, ist_invasor=True)
                invasor.geboren_runde = runde
                # Invasoren starten mit niedrigeren Werten
                invasor.intelligenz = 0.8
                invasor.reputation = 0.3
                invasoren.append(invasor)
                agenten.append(invasor)
                agenten_dict[invasor.id] = invasor
            
            # Verbinde Invasoren mit dem Netzwerk
            erstelle_netzwerk([a for a in agenten if not a.ist_invasor], invasoren)
            
            print(f"{ANZAHL_INVASOREN} Invasoren eingeschleust!")
            print(f"Neue Gesamtzahl: {len(agenten)} Agenten")
            print(f"{'='*50}\n")
            
            invasion_erfolgt = True
        
        # Interaktionen
        aktive_agenten = [a for a in agenten if a.geboren_runde <= runde]
        
        for _ in range(INTERAKTIONEN_PRO_RUNDE):
            if len(aktive_agenten) < 2:
                continue
                
            agent = random.choice(aktive_agenten)
            
            # Wähle Partner
            if agent.nachbarn and random.random() < 0.85:
                gueltige_nachbarn = [n for n in agent.nachbarn if n in agenten_dict]
                if gueltige_nachbarn:
                    partner_id = random.choice(gueltige_nachbarn)
                else:
                    partner_id = random.choice([a.id for a in aktive_agenten if a.id != agent.id])
            else:
                partner_id = random.choice([a.id for a in aktive_agenten if a.id != agent.id])
            
            partner = agenten_dict[partner_id]
            
            # Reputationen
            agent_rep = partner.berechne_partner_reputation(agent.id)
            partner_rep = agent.berechne_partner_reputation(partner.id)
            
            # Aktionen
            aktion_a = agent.waehle_aktion(partner_rep)
            aktion_p = partner.waehle_aktion(agent_rep)
            
            # Lernen
            agent.lerne(aktion_a, aktion_p, partner.id, partner.intelligenz)
            partner.lerne(aktion_p, aktion_a, agent.id, agent.intelligenz)
        
        # Runde beenden
        for agent in aktive_agenten:
            agent.runde_beenden()
        
        # Statistiken
        urspruengliche = [a for a in agenten if not a.ist_invasor and a.geboren_runde == 0]
        aktive_invasoren = [a for a in invasoren if a.geboren_runde <= runde]
        
        schwarm_phi = np.mean([a.intelligenz for a in aktive_agenten])
        urspr_phi = np.mean([a.intelligenz for a in urspruengliche]) if urspruengliche else 0
        inv_phi = np.mean([a.intelligenz for a in aktive_invasoren]) if aktive_invasoren else 0
        
        schwarm_phi_history.append(schwarm_phi)
        urspruengliche_phi_history.append(urspr_phi)
        invasoren_phi_history.append(inv_phi)
        anzahl_agenten_history.append(len(aktive_agenten))
        
        # Progress
        if runde % 50 == 0 or runde == INVASION_RUNDE + 1:
            status = "⚔️ " if runde > INVASION_RUNDE else ""
            print(f"{status}Runde {runde:3d}: Schwarm-Φ={schwarm_phi:.2f}, "
                  f"Ursprüngliche={urspr_phi:.2f}, "
                  f"Invasoren={inv_phi:.2f}, "
                  f"Agenten={len(aktive_agenten)}")
    
    # === ERGEBNISSE ===
    print("\n" + "=" * 75)
    print("FINALE ERGEBNISSE")
    print("=" * 75)
    
    urspruengliche = [a for a in agenten if not a.ist_invasor]
    urspr_normale = [a for a in urspruengliche if not a.ist_defektor]
    urspr_defektoren = [a for a in urspruengliche if a.ist_defektor]
    
    print(f"\n{'=== URSPRÜNGLICHE AGENTEN (vor Invasion) ==='}")
    print(f"Normale (n={len(urspr_normale)}):     Ø Intelligenz = {np.mean([a.intelligenz for a in urspr_normale]):.2f}")
    print(f"Defektoren (n={len(urspr_defektoren)}):  Ø Intelligenz = {np.mean([a.intelligenz for a in urspr_defektoren]):.2f}")
    
    print(f"\n{'=== INVASOREN ==='}")
    print(f"Invasoren (n={len(invasoren)}):    Ø Intelligenz = {np.mean([a.intelligenz for a in invasoren]):.2f}")
    print(f"                       Ø Reputation  = {np.mean([a.reputation for a in invasoren]):.2f}")
    print(f"                       Ø Kooperation = {np.mean([a.kooperations_neigung for a in invasoren]):.1%}")
    
    # Vergleich
    avg_urspr = np.mean([a.intelligenz for a in urspruengliche])
    avg_inv = np.mean([a.intelligenz for a in invasoren])
    
    print(f"\n{'=== VERGLEICH ==='}")
    print(f"Ursprüngliche vs. Invasoren: {avg_urspr:.2f} vs {avg_inv:.2f}")
    print(f"Differenz: {avg_urspr - avg_inv:.2f}")
    
    # Hat der Schwarm die Invasion überstanden?
    phi_vor_invasion = urspruengliche_phi_history[INVASION_RUNDE - 2]
    phi_nach_invasion = urspruengliche_phi_history[-1]
    
    print(f"\n{'=== SCHWARM-RESILIENZ ==='}")
    print(f"Ursprüngliche Φ vor Invasion (Runde {INVASION_RUNDE-1}):  {phi_vor_invasion:.2f}")
    print(f"Ursprüngliche Φ nach Invasion (Runde {RUNDEN_GESAMT}): {phi_nach_invasion:.2f}")
    print(f"Veränderung: {((phi_nach_invasion/phi_vor_invasion)-1)*100:+.1f}%")
    
    if phi_nach_invasion >= phi_vor_invasion:
        print("\n🛡️ SCHWARM HAT INVASION ÜBERSTANDEN UND IST STÄRKER GEWORDEN!")
    elif phi_nach_invasion >= phi_vor_invasion * 0.8:
        print("\n⚔️ SCHWARM HAT INVASION ÜBERSTANDEN (leichte Verluste)")
    else:
        print("\n💀 SCHWARM WURDE DURCH INVASION GESCHWÄCHT")
    
    if avg_inv < avg_urspr * 0.7:
        print("🐝 INVASOREN WURDEN MARGINALISIERT!")
    
    # === VISUALISIERUNG ===
    fig = plt.figure(figsize=(18, 12))
    
    ax1 = fig.add_subplot(2, 3, 1)
    ax2 = fig.add_subplot(2, 3, 2)
    ax3 = fig.add_subplot(2, 3, 3)
    ax4 = fig.add_subplot(2, 3, 4)
    ax5 = fig.add_subplot(2, 3, 5)
    ax6 = fig.add_subplot(2, 3, 6)
    
    fig.suptitle('KKI Invasions-Test: Kann ein kooperativer Schwarm eine Invasion überstehen?', 
                 fontsize=14, fontweight='bold')
    
    # --- Graph 1: Individuelle Verläufe ---
    ax1.set_title('Individuelle Intelligenz')
    ax1.set_ylabel('Intelligenz (Φ)')
    ax1.set_xlabel('Runde')
    
    for agent in urspruengliche:
        color = '#E74C3C' if agent.ist_defektor else '#3498DB'
        alpha = 0.5 if agent.ist_defektor else 0.2
        ax1.plot(range(1, len(agent.intelligenz_history)+1), agent.intelligenz_history, 
                color=color, alpha=alpha, linewidth=0.5)
    
    for agent in invasoren:
        # Invasoren starten später
        start = agent.geboren_runde
        ax1.plot(range(start, start + len(agent.intelligenz_history)), agent.intelligenz_history,
                color='#8E44AD', alpha=0.6, linewidth=1, linestyle='--')
    
    ax1.axvline(x=INVASION_RUNDE, color='red', linestyle='-', linewidth=2, alpha=0.7, label='Invasion')
    ax1.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # --- Graph 2: Gruppen-Vergleich ---
    ax2.set_title('Intelligenz: Ursprüngliche vs. Invasoren')
    ax2.set_ylabel('Ø Intelligenz')
    ax2.set_xlabel('Runde')
    
    ax2.plot(range(1, RUNDEN_GESAMT + 1), urspruengliche_phi_history, 
             color='#3498DB', linewidth=2.5, label='Ursprüngliche')
    ax2.plot(range(1, RUNDEN_GESAMT + 1), invasoren_phi_history, 
             color='#8E44AD', linewidth=2.5, linestyle='--', label='Invasoren')
    ax2.axvline(x=INVASION_RUNDE, color='red', linestyle='-', linewidth=2, alpha=0.7)
    ax2.fill_between(range(INVASION_RUNDE, RUNDEN_GESAMT + 1), 
                     urspruengliche_phi_history[INVASION_RUNDE-1:],
                     invasoren_phi_history[INVASION_RUNDE-1:],
                     alpha=0.2, color='#2ECC71')
    ax2.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # --- Graph 3: Schwarm-Größe ---
    ax3.set_title('Schwarm-Größe über Zeit')
    ax3.set_ylabel('Anzahl Agenten')
    ax3.set_xlabel('Runde')
    
    ax3.fill_between(range(1, RUNDEN_GESAMT + 1), anzahl_agenten_history, 
                     alpha=0.3, color='#F39C12')
    ax3.plot(range(1, RUNDEN_GESAMT + 1), anzahl_agenten_history, 
             color='#E67E22', linewidth=2)
    ax3.axvline(x=INVASION_RUNDE, color='red', linestyle='-', linewidth=2, alpha=0.7, label='Invasion')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # --- Graph 4: Schwarm-Intelligenz ---
    ax4.set_title('Gesamt Schwarm-Intelligenz')
    ax4.set_ylabel('Schwarm-Φ')
    ax4.set_xlabel('Runde')
    
    ax4.fill_between(range(1, RUNDEN_GESAMT + 1), schwarm_phi_history, 
                     alpha=0.3, color='#9B59B6')
    ax4.plot(range(1, RUNDEN_GESAMT + 1), schwarm_phi_history, 
             color='#8E44AD', linewidth=2)
    ax4.axvline(x=INVASION_RUNDE, color='red', linestyle='-', linewidth=2, alpha=0.7, label='Invasion')
    ax4.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # --- Graph 5: Scatter finale Position ---
    ax5.set_title('Finale Position: Intelligenz vs. Reputation')
    ax5.set_xlabel('Reputation')
    ax5.set_ylabel('Intelligenz')
    
    for agent in urspr_normale:
        ax5.scatter(agent.reputation, agent.intelligenz, c='#3498DB', marker='o', s=40, alpha=0.6)
    for agent in urspr_defektoren:
        ax5.scatter(agent.reputation, agent.intelligenz, c='#E74C3C', marker='x', s=60, alpha=0.8)
    for agent in invasoren:
        ax5.scatter(agent.reputation, agent.intelligenz, c='#8E44AD', marker='s', s=80, alpha=0.8)
    
    ax5.axhline(y=1.0, color='gray', linestyle=':', alpha=0.3)
    ax5.axvline(x=0.5, color='gray', linestyle=':', alpha=0.3)
    
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#3498DB', markersize=10, label='Urspr. Normale'),
        Line2D([0], [0], marker='x', color='#E74C3C', markersize=10, label='Urspr. Defektoren', linestyle='None'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#8E44AD', markersize=10, label='Invasoren'),
    ]
    ax5.legend(handles=legend_elements, loc='lower right', fontsize=8)
    ax5.grid(True, alpha=0.3)
    
    # --- Graph 6: Histogramm ---
    ax6.set_title('Verteilung finale Intelligenz')
    ax6.set_xlabel('Intelligenz')
    ax6.set_ylabel('Anzahl Agenten')
    
    ax6.hist([a.intelligenz for a in urspr_normale], bins=15, alpha=0.5, 
             color='#3498DB', label=f'Urspr. Normale (n={len(urspr_normale)})', edgecolor='black')
    ax6.hist([a.intelligenz for a in invasoren], bins=10, alpha=0.5, 
             color='#8E44AD', label=f'Invasoren (n={len(invasoren)})', edgecolor='black')
    
    ax6.axvline(x=np.mean([a.intelligenz for a in urspr_normale]), 
                color='#2980B9', linestyle='--', linewidth=2)
    ax6.axvline(x=np.mean([a.intelligenz for a in invasoren]), 
                color='#6C3483', linestyle='--', linewidth=2)
    ax6.legend(loc='upper right', fontsize=9)
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    save_and_maybe_show(plt, 'kki_invasion.png', dpi=150)


if __name__ == "__main__":
    simulation()
