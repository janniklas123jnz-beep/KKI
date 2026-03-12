"""
KKI Schwarm-Simulation: Emergenz von Kooperation im Multi-Agenten-System
=========================================================================
Zeigt wie Kooperation in einem Schwarm emergiert und wie
einzelne Defektoren ihre Intelligenz verlieren.
"""

import random
import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import (
    configure_simulation,
    save_and_maybe_show,
)

# === KONFIGURATION ===
ANZAHL_AGENTEN = 10
RUNDEN = 150
LERNRATE = 0.1
INTERAKTIONEN_PRO_RUNDE = 15  # Wie viele zufällige Begegnungen pro Runde
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

# Farben für die Agenten
FARBEN = ['#E74C3C', '#3498DB', '#2ECC71', '#9B59B6', '#F39C12',
          '#1ABC9C', '#E91E63', '#00BCD4', '#FF5722', '#607D8B']


class Agent:
    """Ein lernender Agent im Schwarm."""
    
    def __init__(self, name, farbe, ist_defektor=False):
        self.name = name
        self.farbe = farbe
        self.kooperations_neigung = 0.2 if ist_defektor else 0.5  # Defektoren starten niedrig
        self.intelligenz = 1.0
        self.ist_defektor = ist_defektor
        
        # Tracking
        self.intelligenz_history = [1.0]
        self.kooperation_history = [self.kooperations_neigung]
        self.interaktionen = 0
        self.erfolgreiche_kooperationen = 0
    
    def waehle_aktion(self):
        if random.random() < self.kooperations_neigung:
            return 'C'
        return 'D'
    
    def lerne(self, meine_aktion, andere_aktion, partner_intelligenz):
        """
        Erweiterte Lernregel:
        - Kooperation mit intelligentem Partner = großer Boost
        - Defektion = Intelligenzverlust
        - Schwarm-Effekt: Je intelligenter der Partner, desto mehr lernt man
        """
        self.interaktionen += 1
        
        if meine_aktion == 'C' and andere_aktion == 'C':
            # Gegenseitige Kooperation: Intelligenz-Boost proportional zum Partner
            boost = 1.005 + (0.002 * min(partner_intelligenz, 5.0))
            self.intelligenz *= boost
            self.kooperations_neigung += LERNRATE * 0.05
            self.erfolgreiche_kooperationen += 1
            
        elif meine_aktion == 'C' and andere_aktion == 'D':
            # Ich wurde ausgenutzt: leichter Rückgang der Kooperationsneigung
            self.kooperations_neigung -= LERNRATE * 0.02
            
        elif meine_aktion == 'D' and andere_aktion == 'C':
            # Ich habe ausgenutzt: kurzfristiger Gewinn, aber Intelligenz sinkt
            self.intelligenz *= 0.99
            
        elif meine_aktion == 'D' and andere_aktion == 'D':
            # Gegenseitige Defektion: beide verlieren
            self.intelligenz *= 0.97
            self.kooperations_neigung += LERNRATE * 0.01  # Leichter Anreiz zu kooperieren
        
        # Grenzen
        self.kooperations_neigung = max(0.05, min(0.95, self.kooperations_neigung))
        self.intelligenz = max(0.1, min(10.0,  self.intelligenz,)) # Minimum-Intelligenz
    
    def runde_beenden(self):
        """Speichere Werte für diese Runde."""
        self.intelligenz_history.append(self.intelligenz)
        self.kooperation_history.append(self.kooperations_neigung)


def schwarm_simulation():
    """Führe die Schwarm-Simulation durch."""
    
    # Erstelle Agenten: 8 normale + 2 Defektoren
    agenten = []
    for i in range(ANZAHL_AGENTEN):
        ist_defektor = i >= 8  # Die letzten 2 sind Defektoren
        name = f"D{i-7}" if ist_defektor else f"A{i+1}"
        agent = Agent(name, FARBEN[i], ist_defektor)
        agenten.append(agent)
    
    print("=" * 60)
    print("KKI SCHWARM-SIMULATION")
    print("=" * 60)
    print(f"\nAgenten: {ANZAHL_AGENTEN} (davon 2 Defektoren: D1, D2)")
    print(f"Runden: {RUNDEN}")
    print(f"Interaktionen pro Runde: {INTERAKTIONEN_PRO_RUNDE}")
    print("\nSimulation läuft...\n")
    
    # Schwarm-Intelligenz über Zeit
    schwarm_intelligenz_history = []
    
    for runde in range(1, RUNDEN + 1):
        # Zufällige Paarungen für Interaktionen
        for _ in range(INTERAKTIONEN_PRO_RUNDE):
            # Wähle zwei verschiedene Agenten
            a1, a2 = random.sample(agenten, 2)
            
            aktion1 = a1.waehle_aktion()
            aktion2 = a2.waehle_aktion()
            
            # Beide lernen
            a1.lerne(aktion1, aktion2, a2.intelligenz)
            a2.lerne(aktion2, aktion1, a1.intelligenz)
        
        # Runde beenden
        for agent in agenten:
            agent.runde_beenden()
        
        # Schwarm-Intelligenz berechnen (Durchschnitt)
        schwarm_int = np.mean([a.intelligenz for a in agenten])
        schwarm_intelligenz_history.append(schwarm_int)
        
        # Progress alle 30 Runden
        if runde % 30 == 0:
            koop_rate = np.mean([a.kooperations_neigung for a in agenten])
            print(f"Runde {runde:3d}: Schwarm-Φ = {schwarm_int:.2f}, "
                  f"Ø Kooperation = {koop_rate:.1%}")
    
    # === ERGEBNISSE ===
    print("\n" + "=" * 60)
    print("ERGEBNISSE")
    print("=" * 60)
    
    # Sortiere nach Intelligenz
    agenten_sortiert = sorted(agenten, key=lambda a: a.intelligenz, reverse=True)
    
    print(f"\n{'Agent':<8} {'Typ':<10} {'Intelligenz':>12} {'Kooperation':>12}")
    print("-" * 45)
    for agent in agenten_sortiert:
        typ = "DEFEKTOR" if agent.ist_defektor else "Normal"
        print(f"{agent.name:<8} {typ:<10} {agent.intelligenz:>12.2f} "
              f"{agent.kooperations_neigung:>11.1%}")
    
    # Statistik
    normale = [a for a in agenten if not a.ist_defektor]
    defektoren = [a for a in agenten if a.ist_defektor]
    
    avg_normal = np.mean([a.intelligenz for a in normale])
    avg_defekt = np.mean([a.intelligenz for a in defektoren])
    
    print(f"\nØ Intelligenz Normale:    {avg_normal:.2f}")
    print(f"Ø Intelligenz Defektoren: {avg_defekt:.2f}")
    print(f"Differenz:                {avg_normal - avg_defekt:.2f}")
    
    if avg_normal > avg_defekt * 1.2:
        print("\n✓ KOOPERATION HAT SICH DURCHGESETZT!")
        print("  → Defektoren wurden vom Schwarm 'abgehängt'")
    
    # === VISUALISIERUNG ===
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('KKI Schwarm-Simulation: Emergenz kollektiver Intelligenz', 
                 fontsize=14, fontweight='bold')
    
    runden_x = list(range(RUNDEN + 1))
    
    # --- Graph 1: Individuelle Intelligenz ---
    ax1 = axes[0, 0]
    ax1.set_title('Individuelle Intelligenz über Zeit')
    ax1.set_ylabel('Intelligenz (Φ)')
    ax1.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    
    for agent in agenten:
        linestyle = '--' if agent.ist_defektor else '-'
        linewidth = 2.5 if agent.ist_defektor else 1.5
        ax1.plot(runden_x, agent.intelligenz_history, 
                color=agent.farbe, linestyle=linestyle, 
                linewidth=linewidth, label=agent.name, alpha=0.8)
    
    ax1.legend(loc='upper left', fontsize=8, ncol=2)
    ax1.grid(True, alpha=0.3)
    
    # --- Graph 2: Schwarm-Intelligenz ---
    ax2 = axes[0, 1]
    ax2.set_title('Schwarm-Intelligenz (Durchschnitt)')
    ax2.set_ylabel('Schwarm-Φ')
    ax2.fill_between(range(1, RUNDEN + 1), schwarm_intelligenz_history, 
                     alpha=0.3, color='#2ECC71')
    ax2.plot(range(1, RUNDEN + 1), schwarm_intelligenz_history, 
             color='#27AE60', linewidth=2)
    ax2.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax2.grid(True, alpha=0.3)
    
    # --- Graph 3: Kooperationsneigung ---
    ax3 = axes[1, 0]
    ax3.set_title('Kooperationsneigung über Zeit')
    ax3.set_xlabel('Runde')
    ax3.set_ylabel('Kooperationsneigung')
    
    for agent in agenten:
        linestyle = '--' if agent.ist_defektor else '-'
        linewidth = 2.5 if agent.ist_defektor else 1.5
        ax3.plot(runden_x, agent.kooperation_history,
                color=agent.farbe, linestyle=linestyle,
                linewidth=linewidth, label=agent.name, alpha=0.8)
    
    ax3.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    ax3.set_ylim(0, 1)
    ax3.grid(True, alpha=0.3)
    
    # --- Graph 4: Finale Verteilung ---
    ax4 = axes[1, 1]
    ax4.set_title('Finale Intelligenz-Verteilung')
    ax4.set_xlabel('Agent')
    ax4.set_ylabel('Finale Intelligenz')
    
    namen = [a.name for a in agenten_sortiert]
    intelligenzen = [a.intelligenz for a in agenten_sortiert]
    farben = [a.farbe for a in agenten_sortiert]
    
    bars = ax4.bar(namen, intelligenzen, color=farben, edgecolor='black', linewidth=1)
    ax4.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Startwert')
    
    # Markiere Defektoren
    for i, agent in enumerate(agenten_sortiert):
        if agent.ist_defektor:
            bars[i].set_hatch('//')
    
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    save_and_maybe_show(plt, 'kki_schwarm_simulation.png', dpi=150)


if __name__ == "__main__":
    schwarm_simulation()
