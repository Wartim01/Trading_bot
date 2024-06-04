
import pandas as pd
import ta

def rsi_check(data, window=14, overbought=70, oversold=30):
    """
    Vérifie la stratégie RSI (Relative Strength Index).

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période du RSI (défaut: 14).
        overbought (int, optional): Seuil de surachat (défaut: 70).
        oversold (int, optional): Seuil de survente (défaut: 30).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """

    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul du RSI
    rsi_indicator = ta.momentum.RSIIndicator(close=data['Close'], window=window)
    data['rsi'] = rsi_indicator.rsi()

    # Vérification des signaux d'achat et de vente
    buy_signal = data['rsi'].iloc[-1] < oversold
    sell_signal = data['rsi'].iloc[-1] > overbought
    if buy_signal:
        print(f"RSI Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"RSI Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None