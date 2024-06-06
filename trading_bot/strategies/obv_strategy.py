import pandas as pd
import ta

def obv_strategy(data, window=20):
    """
    Vérifie la stratégie On-Balance Volume (OBV).

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période pour calculer la moyenne mobile de l'OBV (défaut: 20).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul de l'OBV
    obv_indicator = ta.volume.OnBalanceVolumeIndicator(close=data['Close'], volume=data['Volume'])
    data['obv'] = obv_indicator.on_balance_volume()

    # Calcul de la moyenne mobile de l'OBV
    data['obv_ma'] = data['obv'].rolling(window=window).mean()

    # Vérification des signaux d'achat et de vente
    buy_signal = (
        data['obv'].iloc[-1] > data['obv_ma'].iloc[-1] and
        data['obv'].iloc[-2] <= data['obv_ma'].iloc[-2]
    )
    sell_signal = (
        data['obv'].iloc[-1] < data['obv_ma'].iloc[-1] and
        data['obv'].iloc[-2] >= data['obv_ma'].iloc[-2]
    )
    if buy_signal:
        print(f"OBV Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"OBV Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None
