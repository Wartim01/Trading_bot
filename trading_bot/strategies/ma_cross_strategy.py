Python
import pandas as pd

def ma_cross_check(data, short_window=10, long_window=50):
    """
    Vérifie la stratégie de croisement de moyennes mobiles (MA Cross).

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'long_window' périodes.
        short_window (int, optional): Période de la moyenne mobile courte (défaut: 10).
        long_window (int, optional): Période de la moyenne mobile longue (défaut: 50).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < long_window:
        return None

    # Calcul des moyennes mobiles
    data['ma_short'] = data['Close'].rolling(window=short_window).mean()
    data['ma_long'] = data['Close'].rolling(window=long_window).mean()

    # Vérification du croisement
    buy_signal = (
        data['ma_short'].iloc[-1] > data['ma_long'].iloc[-1] and 
        data['ma_short'].iloc[-2] <= data['ma_long'].iloc[-2]
    )
    sell_signal = (
        data['ma_short'].iloc[-1] < data['ma_long'].iloc[-1] and 
        data['ma_short'].iloc[-2] >= data['ma_long'].iloc[-2]
    )
    if buy_signal:
        print(f"MA Cross Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"MA Cross Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None