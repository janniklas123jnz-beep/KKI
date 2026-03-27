"""Leitstern Trading Engine — Haupt-Modul."""
from __future__ import annotations
import sys
import time
from .portfolio import Portfolio
from .market_data import get_price, get_ticker
from .strategy import scan_opportunities, Signal, momentum_strategy
from .risk_manager import DEFAULT_RISK, position_size, check_stop_loss, check_take_profit
from .goal_tracker import status_report, get_current_goal

def run_cycle(portfolio: Portfolio, symbols: list[str] = None, verbose: bool = True) -> dict:
    """Einen Trading-Zyklus ausführen."""
    if symbols is None:
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "ADAUSDT"]

    # Preise aktualisieren
    prices = {}
    for sym in symbols:
        price = get_price(sym)
        if price > 0:
            prices[sym] = price
    portfolio.update_prices(prices)

    actions = []

    # Stop-Loss / Take-Profit Check für offene Positionen
    for sym, pos in list(portfolio.positions.items()):
        current_price = prices.get(sym, pos.current_price)
        if current_price <= 0:
            continue
        if check_stop_loss(pos.avg_price, current_price):
            trade = portfolio.sell(sym, current_price, note="🛑 Stop-Loss ausgelöst")
            if trade:
                actions.append(f"STOP-LOSS {sym}")
        elif check_take_profit(pos.avg_price, current_price):
            trade = portfolio.sell(sym, current_price, note="🎯 Take-Profit ausgelöst")
            if trade:
                actions.append(f"TAKE-PROFIT {sym}")

    # Neue Signale scannen
    if len(portfolio.positions) < DEFAULT_RISK.max_open_positions and portfolio.cash > 1.0:
        open_syms = list(portfolio.positions.keys())
        scan_syms = [s for s in symbols if s not in open_syms]
        signals = scan_opportunities(scan_syms)

        for sig in signals:
            if sig.signal == Signal.BUY and portfolio.cash > 1.0:
                size = position_size(portfolio.total_value, sig.confidence,
                                    sig.suggested_size_pct)
                size = min(size, portfolio.cash * 0.9)
                if size >= 0.5:
                    price = prices.get(sig.symbol, get_price(sig.symbol))
                    trade = portfolio.buy(sig.symbol, price, size,
                                         note=f"Signal: {sig.reason}")
                    if trade:
                        actions.append(f"BUY {sig.symbol} (conf: {sig.confidence:.0%})")
                    break  # Ein Trade pro Zyklus

    result = {
        "portfolio_value": portfolio.total_value,
        "cash": portfolio.cash,
        "positions": len(portfolio.positions),
        "actions": actions,
        "goal": get_current_goal(portfolio.total_value),
    }

    if verbose:
        print(portfolio.status())
        print(status_report(portfolio.total_value))
        if actions:
            print(f"\n🚀 Aktionen: {', '.join(actions)}")

    return result


def run_demo(cycles: int = 1):
    """Demo-Lauf: zeigt Portfolio-Status und Signale."""
    print("🌟 LEITSTERN TRADING ENGINE — Paper Trading Demo")
    print("=" * 50)
    portfolio = Portfolio(initial_capital_eur=10.0)

    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "ADAUSDT"]

    # Aktuelle Preise & Signale anzeigen
    print("\n📊 Aktuelle Marktdaten:")
    for sym in symbols:
        ticker = get_ticker(sym)
        if ticker:
            emoji = "🟢" if ticker.change_24h > 0 else "🔴"
            print(f"  {emoji} {sym}: {ticker.price:.4f} USDT ({ticker.change_24h:+.2f}%)")

    print("\n🔍 Strategie-Analyse:")
    for sym in symbols:
        sig = momentum_strategy(sym)
        emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}.get(sig.signal.value, "⚪")
        print(f"  {emoji} {sym}: {sig.signal.value} (Konfidenz: {sig.confidence:.0%}) — {sig.reason}")

    print("\n")
    result = run_cycle(portfolio, symbols, verbose=True)
    return result
