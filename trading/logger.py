"""Performance-Logger — trackt alle Trades und Portfolio-Entwicklung."""
from __future__ import annotations
import csv
import json
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
TRADES_CSV = os.path.join(LOG_DIR, "trades.csv")
EQUITY_CSV = os.path.join(LOG_DIR, "equity.csv")
SUMMARY_JSON = os.path.join(LOG_DIR, "summary.json")

def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.path.exists(TRADES_CSV):
        with open(TRADES_CSV, "w", newline="") as f:
            csv.writer(f).writerow(["timestamp", "symbol", "side", "quantity", "price", "value_eur", "pnl", "note"])
    if not os.path.exists(EQUITY_CSV):
        with open(EQUITY_CSV, "w", newline="") as f:
            csv.writer(f).writerow(["timestamp", "total_value", "cash", "positions_value", "pnl_pct"])

def log_trade(symbol: str, side: str, quantity: float, price: float,
              pnl: float = 0.0, note: str = ""):
    ensure_log_dir()
    with open(TRADES_CSV, "a", newline="") as f:
        csv.writer(f).writerow([
            datetime.now().isoformat(), symbol, side,
            f"{quantity:.8f}", f"{price:.4f}",
            f"{quantity * price:.4f}", f"{pnl:.4f}", note
        ])

def log_equity(total_value: float, cash: float, initial: float = 10.0):
    ensure_log_dir()
    positions_value = total_value - cash
    pnl_pct = (total_value - initial) / initial * 100
    with open(EQUITY_CSV, "a", newline="") as f:
        csv.writer(f).writerow([
            datetime.now().isoformat(),
            f"{total_value:.4f}", f"{cash:.4f}",
            f"{positions_value:.4f}", f"{pnl_pct:.2f}"
        ])

def save_summary(portfolio_value: float, initial: float, trade_count: int,
                 win_rate: float, current_goal: float):
    ensure_log_dir()
    summary = {
        "last_updated": datetime.now().isoformat(),
        "portfolio_value": round(portfolio_value, 4),
        "initial_capital": initial,
        "total_return_pct": round((portfolio_value - initial) / initial * 100, 2),
        "trade_count": trade_count,
        "win_rate": round(win_rate * 100, 1),
        "current_goal": current_goal,
        "progress_pct": round(portfolio_value / current_goal * 100, 1)
    }
    with open(SUMMARY_JSON, "w") as f:
        json.dump(summary, f, indent=2)
    return summary

def print_log_summary():
    if not os.path.exists(SUMMARY_JSON):
        print("Noch kein Trading-Log vorhanden.")
        return
    with open(SUMMARY_JSON) as f:
        s = json.load(f)
    print(f"""
📋 LEITSTERN TRADING SUMMARY
  Stand:         {s['last_updated'][:19]}
  Portfolio:     {s['portfolio_value']:.2f}€
  Rendite:       {s['total_return_pct']:+.1f}%
  Trades:        {s['trade_count']}
  Win-Rate:      {s['win_rate']:.0f}%
  Nächstes Ziel: {s['current_goal']:.0f}€ ({s['progress_pct']:.0f}% erreicht)
""")
