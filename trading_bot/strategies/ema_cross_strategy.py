import pandas as pd
import ta

def ema_cross_strategy(data, short_window=12, long_window=26):
    """
    Vérifie la stratégie de croisement de moyennes mobiles exponentielles (EMA Crossover).

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'long_window' périodes.
        short_window (int, optional): Période de l'EMA courte (défaut: 12).
        long_window (int, optional): Période de l'EMA longue (défaut: 26).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < long_window:
        return None

    # Calcul des moyennes mobiles exponentielles
    data['ema_short'] = ta.trend.EMAIndicator(close=data['Close'], window=short_window).ema_indicator()
    data['ema_long'] = ta.trend.EMAIndicator(close=data['Close'], window=long_window).ema_indicator()

    # Vérification du croisement
    buy_signal = (
        data['ema_short'].iloc[-1] > data['ema_long'].iloc[-1] and 
        data['ema_short'].iloc[-2] <= data['ema_long'].iloc[-2]
    )
    sell_signal = (
        data['ema_short'].iloc[-1] < data['ema_long'].iloc[-1] and 
        data['ema_short'].iloc[-2] >= data['ema_long'].iloc[-2]
    )
    if buy_signal:
        print(f"EMA Cross Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"EMA Cross Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None
