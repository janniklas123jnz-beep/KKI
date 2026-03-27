"""Leitstern Backtesting — Strategie auf historischen Daten testen."""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from .market_data import get_klines, Candle

@dataclass
class BacktestTrade:
    symbol: str
    side: str
    price: float
    quantity: float
    timestamp: int
    reason: str
    pnl: float = 0.0

@dataclass
class BacktestResult:
    symbol: str
    initial_capital: float
    final_capital: float
    trades: list[BacktestTrade]
    win_rate: float
    max_drawdown: float
    sharpe_approx: float

    @property
    def total_return_pct(self) -> float:
        return (self.final_capital - self.initial_capital) / self.initial_capital * 100

    @property
    def total_trades(self) -> int:
        return len([t for t in self.trades if t.side == "SELL"])

def _sma(prices: list[float], period: int) -> float:
    if len(prices) < period:
        return prices[-1] if prices else 0.0
    return sum(prices[-period:]) / period

def _rsi(prices: list[float], period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0
    gains, losses = [], []
    for i in range(-period, 0):
        diff = prices[i] - prices[i-1]
        (gains if diff > 0 else losses).append(abs(diff))
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 1e-10
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def run_backtest(symbol: str = "BTCUSDT", initial_capital: float = 10.0,
                 interval: str = "1h", limit: int = 200) -> BacktestResult:
    """Backtest für ein Symbol auf historischen Kerzen."""
    candles = get_klines(symbol, interval=interval, limit=limit)
    if len(candles) < 30:
        print(f"⚠️ Nicht genug Daten für {symbol}")
        return BacktestResult(symbol, initial_capital, initial_capital, [], 0.0, 0.0, 0.0)

    cash = initial_capital
    position_qty = 0.0
    position_price = 0.0
    trades: list[BacktestTrade] = []
    equity_curve: list[float] = [initial_capital]

    prices = [c.close for c in candles]

    for i in range(26, len(candles)):
        window = prices[:i+1]
        price = prices[i]
        sma7 = _sma(window, 7)
        sma21 = _sma(window, 21)
        rsi = _rsi(window, 14)

        # BUY Signal
        if position_qty == 0 and cash > 0.5:
            if sma7 > sma21 * 1.001 and rsi < 60:
                buy_amount = cash * 0.9
                qty = buy_amount / price
                cash -= buy_amount
                position_qty = qty
                position_price = price
                trades.append(BacktestTrade(symbol=symbol, side="BUY",
                    price=price, quantity=qty,
                    timestamp=candles[i].open_time, reason=f"SMA7>{sma21:.0f}, RSI={rsi:.1f}"))

        # SELL Signal (Take-Profit, Stop-Loss, oder Trendumkehr)
        elif position_qty > 0:
            pnl_pct = (price - position_price) / position_price
            should_sell = False
            reason = ""
            if pnl_pct >= 0.12:
                should_sell = True; reason = f"Take-Profit +{pnl_pct*100:.1f}%"
            elif pnl_pct <= -0.05:
                should_sell = True; reason = f"Stop-Loss {pnl_pct*100:.1f}%"
            elif sma7 < sma21 * 0.999 and rsi > 60:
                should_sell = True; reason = f"Trendumkehr RSI={rsi:.1f}"

            if should_sell:
                proceeds = position_qty * price
                pnl = (price - position_price) * position_qty
                cash += proceeds
                trades.append(BacktestTrade(symbol=symbol, side="SELL",
                    price=price, quantity=position_qty,
                    timestamp=candles[i].open_time, reason=reason, pnl=pnl))
                position_qty = 0.0
                position_price = 0.0

        # Equity
        equity = cash + position_qty * price
        equity_curve.append(equity)

    # Offene Position schließen
    final_price = prices[-1]
    if position_qty > 0:
        cash += position_qty * final_price
        position_qty = 0.0

    # Metriken
    sell_trades = [t for t in trades if t.side == "SELL"]
    winning = [t for t in sell_trades if t.pnl > 0]
    win_rate = len(winning) / len(sell_trades) if sell_trades else 0.0

    # Max Drawdown
    peak = equity_curve[0]
    max_dd = 0.0
    for eq in equity_curve:
        peak = max(peak, eq)
        dd = (peak - eq) / peak if peak > 0 else 0.0
        max_dd = max(max_dd, dd)

    # Sharpe (vereinfacht)
    returns = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
               for i in range(1, len(equity_curve)) if equity_curve[i-1] > 0]
    if returns:
        import statistics
        avg_r = statistics.mean(returns)
        std_r = statistics.stdev(returns) if len(returns) > 1 else 1e-10
        sharpe = (avg_r / std_r) * (24**0.5) if std_r > 0 else 0.0
    else:
        sharpe = 0.0

    return BacktestResult(
        symbol=symbol, initial_capital=initial_capital, final_capital=cash,
        trades=trades, win_rate=win_rate, max_drawdown=max_dd, sharpe_approx=sharpe
    )

def run_multi_backtest(symbols: list[str] = None, initial: float = 10.0) -> None:
    """Mehrere Symbole backtesten und Ergebnisse ausgeben."""
    if symbols is None:
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "BNBUSDT"]

    print("=" * 60)
    print("🔬 LEITSTERN BACKTEST — Letzte 200 Stunden (ca. 8 Tage)")
    print("=" * 60)
    results = []
    for sym in symbols:
        print(f"  Teste {sym}...", end=" ", flush=True)
        r = run_backtest(sym, initial_capital=initial)
        results.append(r)
        emoji = "✅" if r.total_return_pct > 0 else "❌"
        print(f"{emoji} {r.total_return_pct:+.1f}% | {r.total_trades} Trades | Win-Rate: {r.win_rate:.0%} | MaxDD: {r.max_drawdown:.1%}")

    print("\n📊 Zusammenfassung:")
    best = max(results, key=lambda x: x.total_return_pct)
    print(f"  🏆 Bestes Symbol:  {best.symbol} ({best.total_return_pct:+.1f}%)")
    profitable = [r for r in results if r.total_return_pct > 0]
    print(f"  ✅ Profitable:     {len(profitable)}/{len(results)}")
    avg_return = sum(r.total_return_pct for r in results) / len(results)
    print(f"  📈 Ø Return:       {avg_return:+.1f}%")
    print(f"  💰 {initial:.0f}€ → Ø {initial * (1 + avg_return/100):.2f}€")
    print("=" * 60)
    return results
