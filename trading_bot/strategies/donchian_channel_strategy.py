import pandas as pd

def donchian_channel_check(data, window=20):
    """
    Vérifie la stratégie Donchian Channel.

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période pour le calcul (défaut: 20).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul du Donchian Channel
    data['donchian_high'] = data['High'].rolling(window=window).max()
    data['donchian_low'] = data['Low'].rolling(window=window).min()

    # Vérification des signaux d'achat et de vente
    buy_signal = data['Close'].iloc[-1] > data['donchian_high'].iloc[-1]
    sell_signal = data['Close'].iloc[-1] < data['donchian_low'].iloc[-1]
    if buy_signal:
        print(f"Donchian Channel Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"Donchian Channel Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None
