"""Simuliertes Paper-Trading Portfolio."""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

PORTFOLIO_FILE = os.path.join(os.path.dirname(__file__), "portfolio_state.json")

@dataclass
class Trade:
    id: str
    symbol: str
    side: str          # "BUY" oder "SELL"
    quantity: float
    price: float
    timestamp: str
    pnl: float = 0.0
    note: str = ""

@dataclass
class Position:
    symbol: str
    quantity: float
    avg_price: float
    current_price: float = 0.0

    @property
    def value(self) -> float:
        return self.quantity * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.avg_price) * self.quantity

    @property
    def unrealized_pnl_pct(self) -> float:
        if self.avg_price == 0:
            return 0.0
        return (self.current_price - self.avg_price) / self.avg_price * 100

class Portfolio:
    def __init__(self, initial_capital_eur: float = 10.0):
        self.initial_capital = initial_capital_eur
        self.cash = initial_capital_eur          # In EUR (simuliert als USDT)
        self.positions: dict[str, Position] = {}
        self.trades: list[Trade] = []
        self.trade_counter = 0
        self._load()

    def _load(self):
        if os.path.exists(PORTFOLIO_FILE):
            try:
                with open(PORTFOLIO_FILE) as f:
                    data = json.load(f)
                self.cash = data.get("cash", self.initial_capital)
                self.trade_counter = data.get("trade_counter", 0)
                self.trades = [Trade(**t) for t in data.get("trades", [])]
                for sym, pos in data.get("positions", {}).items():
                    self.positions[sym] = Position(**pos)
            except Exception:
                pass

    def save(self):
        data = {
            "cash": self.cash,
            "trade_counter": self.trade_counter,
            "trades": [t.__dict__ for t in self.trades],
            "positions": {sym: pos.__dict__ for sym, pos in self.positions.items()}
        }
        with open(PORTFOLIO_FILE, "w") as f:
            json.dump(data, f, indent=2)

    @property
    def total_value(self) -> float:
        return self.cash + sum(p.value for p in self.positions.values())

    @property
    def total_pnl(self) -> float:
        return self.total_value - self.initial_capital

    @property
    def total_pnl_pct(self) -> float:
        return self.total_pnl / self.initial_capital * 100

    def buy(self, symbol: str, price: float, amount_eur: float, note: str = "") -> Optional[Trade]:
        """Kauforder simulieren."""
        if amount_eur > self.cash:
            print(f"⚠️ Nicht genug Cash: {self.cash:.2f}€ < {amount_eur:.2f}€")
            return None
        quantity = amount_eur / price
        self.cash -= amount_eur
        if symbol in self.positions:
            pos = self.positions[symbol]
            total_qty = pos.quantity + quantity
            pos.avg_price = (pos.avg_price * pos.quantity + price * quantity) / total_qty
            pos.quantity = total_qty
        else:
            self.positions[symbol] = Position(symbol=symbol, quantity=quantity, avg_price=price, current_price=price)
        self.trade_counter += 1
        trade = Trade(
            id=f"T{self.trade_counter:04d}",
            symbol=symbol, side="BUY",
            quantity=quantity, price=price,
            timestamp=datetime.now().isoformat(),
            note=note
        )
        self.trades.append(trade)
        self.save()
        print(f"✅ BUY {symbol}: {quantity:.6f} @ {price:.2f} = {amount_eur:.2f}€ | Cash: {self.cash:.2f}€")
        return trade

    def sell(self, symbol: str, price: float, quantity: Optional[float] = None, note: str = "") -> Optional[Trade]:
        """Verkauforder simulieren."""
        if symbol not in self.positions:
            print(f"⚠️ Keine Position in {symbol}")
            return None
        pos = self.positions[symbol]
        qty = quantity or pos.quantity
        if qty > pos.quantity:
            qty = pos.quantity
        proceeds = qty * price
        pnl = (price - pos.avg_price) * qty
        self.cash += proceeds
        pos.quantity -= qty
        pos.current_price = price
        if pos.quantity < 1e-10:
            del self.positions[symbol]
        self.trade_counter += 1
        trade = Trade(
            id=f"T{self.trade_counter:04d}",
            symbol=symbol, side="SELL",
            quantity=qty, price=price,
            timestamp=datetime.now().isoformat(),
            pnl=pnl, note=note
        )
        self.trades.append(trade)
        self.save()
        print(f"{'✅' if pnl >= 0 else '❌'} SELL {symbol}: {qty:.6f} @ {price:.2f} = {proceeds:.2f}€ | PnL: {pnl:+.2f}€ | Cash: {self.cash:.2f}€")
        return trade

    def update_prices(self, prices: dict[str, float]):
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].current_price = price

    def status(self) -> str:
        lines = [
            "═" * 50,
            f"💼 LEITSTERN PORTFOLIO",
            f"   Startkapital:  {self.initial_capital:.2f}€",
            f"   Cash:          {self.cash:.2f}€",
            f"   Positionen:    {sum(p.value for p in self.positions.values()):.2f}€",
            f"   Gesamtwert:    {self.total_value:.2f}€",
            f"   PnL:           {self.total_pnl:+.2f}€ ({self.total_pnl_pct:+.1f}%)",
            "─" * 50,
        ]
        if self.positions:
            lines.append("   Offene Positionen:")
            for sym, pos in self.positions.items():
                lines.append(f"   {sym}: {pos.quantity:.6f} @ {pos.avg_price:.2f} | Aktuell: {pos.current_price:.2f} | PnL: {pos.unrealized_pnl:+.2f}€ ({pos.unrealized_pnl_pct:+.1f}%)")
        lines.append("═" * 50)
        return "\n".join(lines)
