"""Telegram Benachrichtigungen für Leitstern Trading."""
from __future__ import annotations
import os
import requests
from datetime import datetime

# Konfiguration via Umgebungsvariablen (kein Token im Code!)
TELEGRAM_TOKEN = os.environ.get("LEITSTERN_TG_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("LEITSTERN_TG_CHAT_ID", "")

def _send(message: str) -> bool:
    """Telegram-Nachricht senden."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"📱 [Telegram nicht konfiguriert] {message}")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"⚠️ Telegram-Fehler: {e}")
        return False

def notify_trade(side: str, symbol: str, price: float,
                 amount_eur: float, pnl: float = 0.0, note: str = ""):
    emoji = "🟢" if side == "BUY" else ("✅" if pnl >= 0 else "❌")
    pnl_str = f" | PnL: {pnl:+.2f}€" if side == "SELL" else ""
    msg = (f"{emoji} <b>Leitstern Trade</b>\n"
           f"  {side} {symbol}\n"
           f"  Preis: {price:.4f} USDT\n"
           f"  Betrag: {amount_eur:.2f}€{pnl_str}\n"
           f"  {note}\n"
           f"  ⏰ {datetime.now().strftime('%H:%M:%S')}")
    return _send(msg)

def notify_milestone(milestone: float, portfolio_value: float, multiplier: float):
    msg = (f"🎉🏆 <b>MEILENSTEIN ERREICHT!</b>\n"
           f"  Ziel: <b>{milestone:.0f}€</b> erreicht!\n"
           f"  Portfolio: {portfolio_value:.2f}€\n"
           f"  Wachstum: {multiplier:.1f}x vom Start\n"
           f"  🌟 Leitstern wächst weiter!")
    return _send(msg)

def notify_status(portfolio_value: float, pnl_pct: float,
                  cash: float, positions: int, goal: float):
    emoji = "📈" if pnl_pct >= 0 else "📉"
    msg = (f"{emoji} <b>Leitstern Daily Report</b>\n"
           f"  Portfolio: {portfolio_value:.2f}€ ({pnl_pct:+.1f}%)\n"
           f"  Cash: {cash:.2f}€ | Positionen: {positions}\n"
           f"  Nächstes Ziel: {goal:.0f}€\n"
           f"  ⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    return _send(msg)

def notify_stop_loss(symbol: str, loss_pct: float, loss_eur: float):
    msg = (f"🛑 <b>Stop-Loss ausgelöst!</b>\n"
           f"  Symbol: {symbol}\n"
           f"  Verlust: {loss_pct:.1f}% ({loss_eur:.2f}€)\n"
           f"  Kapital geschützt ✅")
    return _send(msg)

def setup_guide() -> str:
    return """
📱 TELEGRAM BOT SETUP (einmalig, 2 Minuten):

1. Öffne Telegram → suche @BotFather
2. Sende: /newbot
3. Name: LeitsternTrader
4. Username: leitstern_trader_bot (oder ähnlich)
5. Kopiere den TOKEN

6. Starte deinen Bot: Suche ihn in Telegram, sende /start
7. Öffne: https://api.telegram.org/bot<TOKEN>/getUpdates
8. Kopiere deine Chat-ID

9. Setze Umgebungsvariablen:
   export LEITSTERN_TG_TOKEN="dein_token"
   export LEITSTERN_TG_CHAT_ID="deine_chat_id"

Danach empfängst du alle Trade-Benachrichtigungen! 🚀
"""
