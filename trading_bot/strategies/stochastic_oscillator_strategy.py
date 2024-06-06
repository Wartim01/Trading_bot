import pandas as pd
import ta

def stochastic_oscillator_strategy(data, window=14, smooth_window=3, overbought=80, oversold=20):
    """
    Vérifie la stratégie de l'oscillateur stochastique.

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période de l'oscillateur stochastique (défaut: 14).
        smooth_window (int, optional): Période de lissage (défaut: 3).
        overbought (int, optional): Seuil de surachat (défaut: 80).
        oversold (int, optional): Seuil de survente (défaut: 20).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul de l'oscillateur stochastique
    stoch = ta.momentum.StochasticOscillator(high=data['High'], low=data['Low'], close=data['Close'], window=window, smooth_window=smooth_window)
    data['stoch_k'] = stoch.stoch()
    data['stoch_d'] = stoch.stoch_signal()

    # Vérification des signaux d'achat et de vente
    buy_signal = (
        data['stoch_k'].iloc[-1] < oversold and
        data['stoch_d'].iloc[-1] < oversold and
        data['stoch_k'].iloc[-1] > data['stoch_d'].iloc[-1] 
    )
    sell_signal = (
        data['stoch_k'].iloc[-1] > overbought and
        data['stoch_d'].iloc[-1] > overbought and
        data['stoch_k'].iloc[-1] < data['stoch_d'].iloc[-1]
    )
    if buy_signal:
        print(f"Stochastic Oscillator Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"Stochastic Oscillator Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None
