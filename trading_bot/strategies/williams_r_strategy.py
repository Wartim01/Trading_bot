import pandas as pd
import ta

def williams_r_strategy(data, lbp=14):
    """
    Vérifie la stratégie Williams %R.

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'lbp' périodes.
        lbp (int, optional): Lookback period (défaut: 14).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < lbp:
        return None

    # Calcul du Williams %R
    williams = ta.momentum.WilliamsRIndicator(high=data['High'], low=data['Low'], close=data['Close'], lbp=lbp)
    data['williams_r'] = williams.williams_r()

    # Vérification des signaux d'achat et de vente
    buy_signal = data['williams_r'].iloc[-1] < -80  # Survente
    sell_signal = data['williams_r'].iloc[-1] > -20  # Surachat
    if buy_signal:
        print(f"Williams %R Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"Williams %R Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None
