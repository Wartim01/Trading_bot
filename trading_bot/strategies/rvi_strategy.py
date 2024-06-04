import pandas as pd
import ta

def rvi_check(data, window=14):
    """
    Vérifie la stratégie Relative Vigor Index (RVI).

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période du RVI (défaut: 14).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul du RVI
    rvi_indicator = ta.momentum.RVIIndicator(close=data['Close'], high=data['High'], low=data['Low'], window=window)
    data['rvi'] = rvi_indicator.rvi()
    data['rvi_signal'] = rvi_indicator.rvi_signal()

    # Vérification des signaux d'achat et de vente
    buy_signal = (
        data['rvi'].iloc[-1] > data['rvi_signal'].iloc[-1] and
        data['rvi'].iloc[-2] <= data['rvi_signal'].iloc[-2]
    )
    sell_signal = (
        data['rvi'].iloc[-1] < data['rvi_signal'].iloc[-1] and
        data['rvi'].iloc[-2] >= data['rvi_signal'].iloc[-2]
    )

    if buy_signal:
        print(f"RVI Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"RVI Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None
