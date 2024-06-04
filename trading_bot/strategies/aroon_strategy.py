import pandas as pd
import ta

def aroon_check(data, window=25):
    """
    Vérifie la stratégie Aroon Indicator.

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période de l'indicateur Aroon (défaut: 25).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul de l'indicateur Aroon
    aroon = ta.trend.AroonIndicator(close=data['Close'], window=window)
    data['aroon_up'] = aroon.aroon_up()
    data['aroon_down'] = aroon.aroon_down()

    # Vérification des signaux d'achat et de vente
    buy_signal = (
        data['aroon_up'].iloc[-1] > 70 and
        data['aroon_down'].iloc[-1] < 30
    )
    sell_signal = (
        data['aroon_up'].iloc[-1] < 30 and
        data['aroon_down'].iloc[-1] > 70
    )
    if buy_signal:
        print(f"Aroon Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"Aroon Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None
