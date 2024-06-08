import talib
import pandas as pd
from typing import Optional

def candlestick_strategy(data: pd.DataFrame) -> Optional[int]:
    """
    Implémentation de la stratégie basée sur les motifs des chandeliers japonais.
    
    Parameters:
    data (pd.DataFrame): Données de marché contenant les colonnes 'open', 'high', 'low', 'close'.

    Returns:
    int: 1 pour un signal d'achat, -1 pour un signal de vente, None pour aucun signal.
    """
    try:
        # Calcul des motifs de chandeliers japonais
        data['hammer'] = talib.CDLHAMMER(data['Open'], data['High'], data['Low'], data['Close'])
        data['engulfing'] = talib.CDLENGULFING(data['Open'], data['High'], data['Low'], data['Close'])

        # Génération des signaux d'achat et de vente
        buy_signal = (data['hammer'] != 0) | (data['engulfing'] == 100)
        sell_signal = (data['engulfing'] == -100)

        if buy_signal.any():
            return 1
        elif sell_signal.any():
            return -1
        else:
            return None

    except Exception as e:
        # Gestion des exceptions et journalisation de l'erreur
        print(f"Erreur lors de l'exécution de la stratégie: {e}")
        return None
