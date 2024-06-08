import pandas as pd
import ta
import talib

def adx_strategy(data, window=14):
    """
    Vérifie la stratégie de l'Average Directional Index (ADX).

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période de l'ADX (défaut: 14).

    Returns:
        bool or None: True (signal d'achat si tendance haussière), False (signal de vente si tendance baissière), None (pas de signal clair).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul de l'ADX
    adx_indicator = ta.trend.ADXIndicator(high=data['High'], low=data['Low'], close=data['Close'], window=window)
    data['adx'] = adx_indicator.adx()
    data['di_pos'] = adx_indicator.adx_pos()
    data['di_neg'] = adx_indicator.adx_neg()

    # Vérification de la force de la tendance et de sa direction
    if data['adx'].iloc[-1] > 25:  # Seuil pour une tendance forte
        if data['di_pos'].iloc[-1] > data['di_neg'].iloc[-1]:
            print(f"ADX Buy signal for {data['symbol'].iloc[-1]}")
            return True  # Tendance haussière forte
        elif data['di_neg'].iloc[-1] > data['di_pos'].iloc[-1]:
            print(f"ADX Sell signal for {data['symbol'].iloc[-1]}")
            return False # Tendance baissière forte
        
        except Exception as e:
        print(f"Erreur lors de l'exécution de la stratégie ADX: {e}")
        return {}