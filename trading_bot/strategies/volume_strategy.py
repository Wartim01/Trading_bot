import pandas as pd

def volume_strategy(data, window=20):
    """
    Vérifie la stratégie basée sur le volume.

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'window' périodes.
        window (int, optional): Période pour calculer la moyenne mobile du volume (défaut: 20).

    Returns:
        bool or None: True (signal d'achat si le volume augmente), False (signal de vente si le volume diminue), None (pas de signal clair).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < window:
        return None

    # Calcul de la moyenne mobile du volume
    data['volume_ma'] = data['Volume'].rolling(window=window).mean()

    # Vérification de l'augmentation ou de la diminution du volume
    if data['Volume'].iloc[-1] > data['volume_ma'].iloc[-1] * 1.5:  # Seuil d'augmentation du volume
        print(f"Volume Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif data['Volume'].iloc[-1] < data['volume_ma'].iloc[-1] * 0.5:  # Seuil de diminution du volume
        print(f"Volume Sell signal for {data['symbol'].iloc[-1]}")
        return False

    return None  # Pas de changement significatif du volume
