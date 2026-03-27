#!/usr/bin/env python
"""
🌟 Leitstern Trading — Haupt-Start-Skript

Verwendung:
  python -m trading.run_leitstern demo      # Einmal-Demo mit Signalen
  python -m trading.run_leitstern backtest  # Historischen Backtest laufen
  python -m trading.run_leitstern auto      # Auto-Trading starten (Ctrl+C zum Stoppen)
  python -m trading.run_leitstern status    # Portfolio-Status anzeigen
  python -m trading.run_leitstern setup     # Live-Setup-Guide anzeigen
  python -m trading.run_leitstern telegram  # Telegram-Setup-Guide
"""
from __future__ import annotations
import sys

def main():
    import os
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, ".")

    cmd = sys.argv[1] if len(sys.argv) > 1 else "demo"

    if cmd == "demo":
        from trading.engine import run_demo
        run_demo()

    elif cmd == "backtest":
        from trading.backtest import run_multi_backtest
        run_multi_backtest()

    elif cmd == "auto":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        print(f"🤖 Auto-Trading alle {interval} Minuten (Ctrl+C zum Stoppen)")
        from trading.scheduler import run_auto
        run_auto(interval_minutes=interval)

    elif cmd == "status":
        from trading.portfolio import Portfolio
        from trading.goal_tracker import status_report
        from trading.logger import print_log_summary
        p = Portfolio(10.0)
        print(p.status())
        print(status_report(p.total_value))
        print_log_summary()

    elif cmd == "setup":
        from trading.live_setup import print_setup_guide
        print_setup_guide()

    elif cmd == "telegram":
        from trading.telegram_bot import setup_guide
        print(setup_guide())

    elif cmd == "check":
        from trading.live_setup import check_readiness
        from trading.logger import SUMMARY_JSON
        import json, os
        if os.path.exists(SUMMARY_JSON):
            with open(SUMMARY_JSON) as f:
                s = json.load(f)
            check_readiness(
                win_rate=s.get("win_rate", 0) / 100,
                max_drawdown=0.10,
                paper_days=1,
                return_pct=s.get("total_return_pct", 0)
            )
        else:
            print("Noch kein Trading-Log. Erst 'demo' oder 'auto' ausführen!")
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
