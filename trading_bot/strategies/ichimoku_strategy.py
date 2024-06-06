import pandas as pd
import ta

def ichimoku_strategy(data, conversion_line_period=9, base_line_period=26, leading_span_b_period=52, lagging_span_period=26):
    """
    Vérifie la stratégie Ichimoku Cloud.

    Args:
        data (pd.DataFrame): Données de marché avec au moins 'leading_span_b_period' périodes.
        conversion_line_period (int, optional): Période de la ligne de conversion (Tenkan-sen) (défaut: 9).
        base_line_period (int, optional): Période de la ligne de base (Kijun-sen) (défaut: 26).
        leading_span_b_period (int, optional): Période du deuxième span avant (Senkou Span B) (défaut: 52).
        lagging_span_period (int, optional): Période du span décalé (Chikou Span) (défaut: 26).

    Returns:
        bool or None: True (signal d'achat), False (signal de vente), None (pas de signal).
    """
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame([data])

    if len(data) < leading_span_b_period:
        return None

    # Calcul de l'Ichimoku Cloud
    ichimoku = ta.trend.IchimokuIndicator(high=data['High'], low=data['Low'], window1=conversion_line_period, window2=base_line_period, window3=leading_span_b_period)
    data['tenkan_sen'] = ichimoku.ichimoku_conversion_line()
    data['kijun_sen'] = ichimoku.ichimoku_base_line()
    data['senkou_span_a'] = ichimoku.ichimoku_a()
    data['senkou_span_b'] = ichimoku.ichimoku_b()
    data['chikou_span'] = ichimoku.ichimoku_leading_line()

    # Vérification des signaux d'achat et de vente
    buy_signal = (
        data['Close'].iloc[-1] > data['senkou_span_a'].iloc[-1] and
        data['Close'].iloc[-1] > data['senkou_span_b'].iloc[-1] and
        data['tenkan_sen'].iloc[-1] > data['kijun_sen'].iloc[-1] and
        data['tenkan_sen'].iloc[-2] <= data['kijun_sen'].iloc[-2]
    )

    sell_signal = (
        data['Close'].iloc[-1] < data['senkou_span_a'].iloc[-1] and
        data['Close'].iloc[-1] < data['senkou_span_b'].iloc[-1] and
        data['tenkan_sen'].iloc[-1] < data['kijun_sen'].iloc[-1] and
        data['tenkan_sen'].iloc[-2] >= data['kijun_sen'].iloc[-2]
    )
    if buy_signal:
        print(f"Ichimoku Cloud Buy signal for {data['symbol'].iloc[-1]}")
        return True
    elif sell_signal:
        print(f"Ichimoku Cloud Sell signal for {data['symbol'].iloc[-1]}")
        return False
    else:
        return None
