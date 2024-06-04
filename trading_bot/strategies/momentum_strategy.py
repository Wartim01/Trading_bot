import pandas as pd
import ta

def momentum_check(data, window=10):
    """
    Vérifie la stratégie Momentum.

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période pour le calcul du momentum (défaut: 10).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul du Momentum
    data['momentum'] = ta.momentum.roc(data['Close'], window=window)

    # Vérification des signaux d'achat et de vente
    buy_signal = data['momentum'].iloc[-1] > 0 and data['momentum'].iloc[-2] <= 0
    sell_signal = data['momentum'].iloc[-1] < 0 and data['momentum'].iloc[-2] >= 0
    if buy_signal:
        print(f"Momentum Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"Momentum Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None
