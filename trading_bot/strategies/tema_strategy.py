import pandas as pd
import ta

def tema_strategy(data, window=20):
    """
    Vérifie la stratégie Triple Exponential Moving Average (TEMA).

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période de la TEMA (défaut: 20).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul de la TEMA
    tema_indicator = ta.trend.TEMAIndicator(close=data['Close'], window=window)
    data['tema'] = tema_indicator.tema_indicator()

    # Vérification des signaux d'achat et de vente
    buy_signal = (
        data['Close'].iloc[-1] > data['tema'].iloc[-1] and
        data['Close'].iloc[-2] <= data['tema'].iloc[-2]
    )
    sell_signal = (
        data['Close'].iloc[-1] < data['tema'].iloc[-1] and
        data['Close'].iloc[-2] >= data['tema'].iloc[-2]
    )
    if buy_signal:
        print(f"TEMA Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"TEMA Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None
