import pandas as pd
import ta

def atr_check(data, window=14, risk_factor=2):
    """
    Vérifie la stratégie basée sur l'Average True Range (ATR).

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période de l'ATR (défaut: 14).
        risk_factor (float, optional): Facteur de risque pour le stop-loss (défaut: 2).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul de l'ATR
    atr_indicator = ta.volatility.AverageTrueRange(high=data["High"], low=data["Low"], close=data["Close"], window=window)
    data['atr'] = atr_indicator.average_true_range()

    # Vérification des signaux d'achat et de vente
    # Cette stratégie est plus utilisée pour la gestion du risque (stop-loss) que pour générer des signaux d'entrée.
    stop_loss = data['Close'].iloc[-1] - (risk_factor * data['atr'].iloc[-1])

    print(f"ATR for {data['symbol'].iloc[-1]}: {data['atr'].iloc[-1]}, Stop Loss: {stop_loss}")

    return None  # Pas de signal d'entrée direct, mais information sur le stop-loss
