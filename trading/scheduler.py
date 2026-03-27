"""Auto-Scheduler — führt Trading-Zyklen automatisch aus."""
from __future__ import annotations
import time
import signal
import sys
from datetime import datetime
from .portfolio import Portfolio
from .engine import run_cycle
from .logger import log_equity, save_summary
from .goal_tracker import get_current_goal, MILESTONES

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "ADAUSDT"]

def _signal_handler(sig, frame):
    print("\n\n🛑 Leitstern Trading gestoppt. Portfolio gespeichert.")
    sys.exit(0)

signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

def run_auto(interval_minutes: int = 60, max_cycles: int = None):
    """Trading-Schleife — läuft alle interval_minutes Minuten."""
    portfolio = Portfolio(initial_capital_eur=10.0)
    cycle = 0

    print(f"""
🌟 LEITSTERN AUTO-TRADING GESTARTET
   Modus:      Paper-Trading (kein echtes Geld)
   Intervall:  alle {interval_minutes} Minuten
   Startkapital: {portfolio.initial_capital:.2f}€
   Ziel:       {get_current_goal(portfolio.total_value):.0f}€
   Stop:       Ctrl+C
{'='*50}""")

    while True:
        cycle += 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        print(f"\n[{now}] ▶ Zyklus #{cycle}")

        try:
            result = run_cycle(portfolio, SYMBOLS, verbose=False)

            # Ziel-Check
            goal = get_current_goal(portfolio.total_value)
            pct = portfolio.total_value / portfolio.initial_capital

            status_emoji = "📈" if portfolio.total_pnl >= 0 else "📉"
            print(f"  {status_emoji} Portfolio: {portfolio.total_value:.2f}€ ({portfolio.total_pnl_pct:+.1f}%) | Ziel: {goal:.0f}€")

            if result["actions"]:
                print(f"  🚀 Aktion: {', '.join(result['actions'])}")

            # Meilenstein erreicht?
            for milestone in MILESTONES[1:]:
                if portfolio.total_value >= milestone:
                    prev = MILESTONES[MILESTONES.index(milestone) - 1]
                    if portfolio.total_value < milestone * 1.02:
                        print(f"\n  🎉🏆 MEILENSTEIN ERREICHT: {milestone:.0f}€! 🎉")

            # Logging
            log_equity(portfolio.total_value, portfolio.cash, portfolio.initial_capital)
            sell_trades = [t for t in portfolio.trades if t.side == "SELL"]
            win_trades = [t for t in sell_trades if t.pnl > 0]
            win_rate = len(win_trades) / len(sell_trades) if sell_trades else 0.0
            save_summary(portfolio.total_value, portfolio.initial_capital,
                        len(portfolio.trades), win_rate, goal)

        except Exception as e:
            print(f"  ⚠️ Fehler in Zyklus #{cycle}: {e}")

        if max_cycles and cycle >= max_cycles:
            print(f"\n✅ {max_cycles} Zyklen abgeschlossen.")
            break

        print(f"  ⏳ Nächster Zyklus in {interval_minutes} Min...")
        time.sleep(interval_minutes * 60)

def run_once(verbose: bool = True):
    """Einmaligen Zyklus ausführen (für Tests)."""
    portfolio = Portfolio(initial_capital_eur=10.0)
    return run_cycle(portfolio, SYMBOLS, verbose=verbose)
