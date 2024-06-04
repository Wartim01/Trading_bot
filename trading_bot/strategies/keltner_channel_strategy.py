import pandas as pd
import ta

def keltner_channel_check(data, window=20, multiplier=2):
    """
    Vérifie la stratégie Keltner Channel.

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période pour le calcul (défaut: 20).
        multiplier (float, optional): Multiplicateur de l'ATR pour les bandes (défaut: 2).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul du Keltner Channel
    keltner = ta.volatility.KeltnerChannel(high=data["High"], low=data["Low"], close=data["Close"], window=window, window_atr=window, original_version=True)
    data['keltner_mband'] = keltner.keltner_channel_mband()
    data['keltner_hband'] = keltner.keltner_channel_hband()
    data['keltner_lband'] = keltner.keltner_channel_lband()

    # Vérification des signaux d'achat et de vente
    buy_signal = data['Close'].iloc[-1] < data['keltner_lband'].iloc[-1]
    sell_signal = data['Close'].iloc[-1] > data['keltner_hband'].iloc[-1]
    if buy_signal:
        print(f"Keltner Channel Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"Keltner Channel Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None
