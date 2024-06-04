import pandas as pd
import ta

def candlestick_check(data):
    """
    Vérifie les signaux basés sur l'analyse des chandeliers japonais.

    Args:
        data (pd.DataFrame): Données de marché avec les colonnes 'Open', 'High', 'Low', 'Close'.

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    # Exemple de vérification d'un motif de chandelier haussier (marteau)
    hammer = ta.trend.Hammer(data['Open'], data['High'], data['Low'], data['Close'])
    data['hammer'] = hammer.hammer()
    if data['hammer'].iloc[-1]:
        print(f"Candlestick Buy signal (Hammer) for {data['symbol'].iloc[-1]}")
        return True

    # Exemple de vérification d'un motif de chandelier baissier (étoile filante)
    shooting_star = ta.trend.ShootingStar(data['Open'], data['High'], data['Low'], data['Close'])
    data['shooting_star'] = shooting_star.shooting_star()
    if data['shooting_star'].iloc[-1]:
        print(f"Candlestick Sell signal (Shooting Star) for {data['symbol'].iloc[-1]}")
        return False

    return None  # Aucun motif de chandelier significatif détecté
