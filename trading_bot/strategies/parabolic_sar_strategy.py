import pandas as pd
import ta

def parabolic_sar_check(data, acceleration=0.02, maximum=0.2):
    """
    Vérifie la stratégie Parabolic SAR (Stop and Reverse).

    Args:
        data (pd.DataFrame): Données de marché avec les colonnes 'High' et 'Low'.
        acceleration (float, optional): Facteur d'accélération (défaut: 0.02).
        maximum (float, optional): Accélération maximale (défaut: 0.2).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    # Calcul du Parabolic SAR
    psar = ta.trend.PSARIndicator(high=data['High'], low=data['Low'], close=data['Close'], step=acceleration, max_step=maximum)
    data['psar'] = psar.psar()

    # Vérification des signaux d'achat et de vente
    buy_signal = data['Close'].iloc[-1] > data['psar'].iloc[-1] 
    sell_signal = data['Close'].iloc[-1] < data['psar'].iloc[-1]
    if buy_signal:
        print(f"Parabolic SAR Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"Parabolic SAR Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None
