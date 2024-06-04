Python
import pandas as pd
import ta

def bollinger_check(data, window=20, window_dev=2):
    """
    Vérifie la stratégie des bandes de Bollinger.

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période de la moyenne mobile (défaut: 20).
        window_dev (int, optional): Nombre d'écarts-types pour les bandes (défaut: 2).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul des bandes de Bollinger
    indicator_bb = ta.volatility.BollingerBands(close=data['Close'], window=window, window_dev=window_dev)
    data['bb_high'] = indicator_bb.bollinger_hband()
    data['bb_low'] = indicator_bb.bollinger_lband()

    # Vérification des signaux d'achat et de vente
    buy_signal = data['Close'].iloc[-1] < data['bb_low'].iloc[-1]
    sell_signal = data['Close'].iloc[-1] > data['bb_high'].iloc[-1]

    if buy_signal:
        print(f"Bollinger Bands Buy signal for {data['symbol'].iloc[-1]} at {data['Close'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"Bollinger Bands Sell signal for {data['symbol'].iloc[-1]} at {data['Close'].iloc[-1]}")
        return False
    else:
        return None