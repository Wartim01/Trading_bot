import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from decimal import Decimal
import joblib
from sklearn.preprocessing import StandardScaler
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import numpy as np
import time
import logging
import re
import subprocess
import schedule


# Importation des stratégies
from strategies.bollinger_strategy import bollinger_strategy
from strategies.ma_cross_strategy import ma_cross_strategy
from strategies.macd_strategy import macd_strategy
from strategies.rsi_strategy import rsi_strategy
from strategies.ema_cross_strategy import ema_cross_strategy
from strategies.stochastic_oscillator_strategy import stochastic_oscillator_strategy
from strategies.adx_strategy import adx_strategy
from strategies.ichimoku_strategy import ichimoku_strategy
from strategies.volume_strategy import volume_strategy
from strategies.candlestick_strategy import candlestick_strategy
from strategies.obv_strategy import obv_strategy
from strategies.aroon_strategy import aroon_strategy
from strategies.parabolic_sar_strategy import parabolic_sar_strategy
from strategies.williams_r_strategy import williams_r_strategy
from strategies.tema_strategy import tema_strategy
from strategies.atr_strategy import atr_strategy
from strategies.keltner_channel_strategy import keltner_channel_strategy
from strategies.donchian_channel_strategy import donchian_channel_strategy
from strategies.rvi_strategy import rvi_strategy
from strategies.momentum_strategy import momentum_strategy
# Configurer les logs
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Clés API Binance pour le Testnet
api_key = 'fvo67wee5dq10q00pajP2y9Rqz5Pwkdc01h2RY8m9OirvQ0oOPJhrFUW2QyKYfEJ'
api_secret = 'wvM9TmcVEG76GwNwFtPHZNx1z6W56h6VfFmUaqchkI3VpuPVbOcrxlDojXP1k29f'
client = Client(api_key, api_secret, testnet=True)

# Liste des symboles des crypto-monnaies
symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'SHIBUSDT']

open_positions = {}

# Fonction pour récupérer les nouvelles données (optimisée)
def fetch_new_data(symbols):
    new_data = []
    valid_symbols = []

    for symbol in symbols:
        if re.match("^[A-Z0-9]{1,20}$", symbol):  # Vérification du format du symbole
            valid_symbols.append(symbol)
        else:
            logging.warning(f"Invalid symbol: {symbol} - Reason: Does not match regex")

    if not valid_symbols:
        logging.error("No valid symbols found.")
        return pd.DataFrame() 

    for symbol in valid_symbols:
        logging.info(f"Fetching klines for symbol: {symbol}")
        try:
            klines = client.get_klines(symbol=symbol, interval='1h')
        except BinanceAPIException as e:
            logging.error(f"Binance API error fetching klines for {symbol}: {e.message}")
            continue
        except Exception as e:
            logging.error(f"General error fetching klines for {symbol}: {e}")
            continue

        for kline in klines:
            new_data.append({
                'symbol': symbol,
                'timestamp': pd.to_datetime(kline[0], unit='ms'),
                'Open': float(kline[1]),
                'High': float(kline[2]),
                'Low': float(kline[3]),
                'Close': float(kline[4]),
                'Volume': float(kline[5]),
                'Close_time': pd.to_datetime(kline[6], unit='ms'),
                'Quote_asset_volume': float(kline[7]),
                'Number_of_trades': int(kline[8]),
                'Taker_buy_base_asset_volume': float(kline[9]),
                'Taker_buy_quote_asset_volume': float(kline[10]),
                'ignore': kline[11]
            })

    return pd.DataFrame(new_data)
# Fonction pour gérer les risques et calculer la quantité de trade
def calculate_trade_amount(capital, current_price, symbol):
    global used_capital

    risk_percentage = 0.02

    info = client.get_symbol_info(symbol)

    # Initialiser trade_amount à une valeur par défaut en cas d'erreur
    trade_amount = 0.0 

    # Trouver le filtre LOT_SIZE
    step_size = None
    min_qty = None
    for filter_dict in info['filters']:
        if filter_dict['filterType'] == 'LOT_SIZE':
            step_size = float(filter_dict['stepSize'])
            min_qty = float(filter_dict['minQty'])
            break
    else:
        logging.error(f"LOT_SIZE filter not found for symbol {symbol}")
        return 0  # Ou lever une exception si vous préférez
        
    # Trouver le filtre MIN_NOTIONAL
    min_notional = None
    for filter_dict in info['filters']:
        if filter_dict['filterType'] == 'MIN_NOTIONAL':
            min_notional = float(filter_dict['minNotional'])
            break
    else:
        # Gérer le cas où le filtre MIN_NOTIONAL n'est pas trouvé
        logging.warning(f"MIN_NOTIONAL filter not found for symbol {symbol}, using default min_notional of 10")
        min_notional = 10

    try:
        # Assurez-vous que le price est un nombre décimal
        current_price = float(current_price)

        max_trade_amount = capital * risk_percentage / current_price
        available_capital = capital - used_capital

        # Vérifier si le capital disponible est suffisant
        if available_capital < max_trade_amount * current_price:
            trade_amount = available_capital / current_price
            logging.warning(
                f"Insufficient capital for {symbol}. Using available capital: {available_capital}"
            )
        else:
            trade_amount = max_trade_amount
            

    except ValueError:
        logging.error(f"Invalid price format for {symbol}: {current_price}")
        return 0

    # Arrondir la quantité à la précision requise et vérifier minQty 
    # après avoir calculé trade_amount   
    trade_amount = float(round(Decimal(trade_amount), int(info['baseAssetPrecision']))) # Arrondir avec Decimal
    trade_amount = max(trade_amount, min_qty)

    if trade_amount * current_price < min_notional:
        logging.warning(f"Trade amount for {symbol} is below minNotional: {trade_amount}. Skipping trade.")
        return 0

    logging.info(f"Calculated trade amount for {symbol}: {trade_amount}")
    return trade_amount

# Fonction pour vérifier les stratégies
def apply_strategies(data):
    signals = {}
    for strategy in [
        bollinger_strategy, ma_cross_strategy, macd_strategy, rsi_strategy,
    ema_cross_strategy, stochastic_oscillator_strategy, adx_strategy, ichimoku_strategy,
    volume_strategy, candlestick_strategy, obv_strategy, aroon_strategy,
    parabolic_sar_strategy, williams_r_strategy, tema_strategy, atr_strategy,
    keltner_channel_strategy, donchian_channel_strategy, rvi_strategy, momentum_strategy
    ]:
        result = strategy(data.copy())
        if isinstance(result, dict):
            signals.update({k: v for k, v in result.items() if v is not None})
        else:
            signals[strategy.__name__] = {strategy.__name__:result} 
    return signals


# Fonction pour placer un ordre d'achat
def place_buy_order(symbol, quantity):
    try:
        order = client.create_order(  
            symbol=symbol,
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
        logging.info(f"Buy order placed for {symbol}: {order}")

        # Attendre que l'ordre soit rempli (avec un délai maximum)
        max_wait_time = 10  # Temps d'attente maximum en secondes
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            order_status = client.get_order(symbol=symbol, orderId=order['orderId'])
            if order_status['status'] == ORDER_STATUS_FILLED:
                # Ajouter la position au dictionnaire des positions ouvertes
                open_positions[symbol] = {
                    'entry_price': float(order_status['fills'][0]['price']),
                    'quantity': quantity,
                    'stop_loss': None
                }
                return True  # L'ordre a été rempli
            elif order_status['status'] in [ORDER_STATUS_CANCELED, ORDER_STATUS_REJECTED, ORDER_STATUS_EXPIRED]:
                logging.warning(f"Buy order for {symbol} was not filled. Status: {order_status['status']}")
                return False  # L'ordre n'a pas été rempli
            else:
                time.sleep(1)  # Attendre 1 seconde avant de revérifier

        logging.warning(f"Buy order for {symbol} timed out after {max_wait_time} seconds.")
        return False  # L'ordre n'a pas été rempli dans le délai imparti

    except Exception as e:
        logging.error(f"An error occurred while placing buy order: {e}")
        return False

# Fonction pour placer un ordre de vente
def place_sell_order(symbol, quantity):
    try:
        order = client.order_market_sell(
            symbol=symbol,
            quantity=quantity
        )
        logging.info(f"Sell order placed for {symbol}: {order}")
        
        # Supprimer la position du dictionnaire des positions ouvertes
        if symbol in open_positions:
            del open_positions[symbol]
    except Exception as e:
        logging.error(f"An error occurred while placing sell order: {e}")

# Fonction pour définir le stop loss
def set_stop_loss(symbol, entry_price, stop_loss_percentage):
    stop_loss_price = entry_price * (1 - stop_loss_percentage)
    open_positions[symbol]['stop_loss'] = stop_loss_price
    logging.info(f"Stop loss set for {symbol} at {stop_loss_price}")

# Fonction pour vérifier et exécuter les stop loss
def check_stop_losses():
    for symbol, position in open_positions.copy().items():  
        current_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        if current_price <= position['stop_loss']:
            logging.info(f"Stop loss triggered for {symbol} at {current_price}")
            place_sell_order(symbol, position['quantity'])

# Fonction pour prendre des décisions de trading
def trade_decision(data, capital):
    global used_capital  # Accès à la variable globale used_capital
    # Configuration des poids pour chaque stratégie
    strategy_weights = {
        'bollinger_strategy': 1,        # Stratégie de base
        'ma_cross_strategy': 1.2,      # Moyennes mobiles, bon indicateur de tendance
        'macd_strategy': 1.5,         # MACD, efficace pour les croisements de moyennes
        'rsi_strategy': 1,             # RSI, utile pour les zones de surachat/survente
        'ema_cross_strategy': 1.2,     # EMA, similaire aux moyennes mobiles
        'stochastic_oscillator_strategy': 1.3,  # Oscillateur stochastique, bon pour les retournements
        'adx_strategy': 0.8,           # ADX, moins pertinent pour le court terme
        'ichimoku_strategy': 1.1,      # Ichimoku, peut être utile pour les tendances
        'volume_strategy': 1.4,        # Volume, important pour confirmer les mouvements
        'candlestick_strategy': 1.8,    # Chandeliers, signaux forts mais potentiellement moins fiables
        'obv_strategy': 1.2,           # OBV, indicateur de volume cumulé
        'aroon_strategy': 1,           # Aroon, indicateur de tendance
        'parabolic_sar_strategy': 1.6,  # SAR parabolique, bon pour le suivi de tendance
        'williams_r_strategy': 1.3,    # Williams %R, oscillateur de momentum
        'tema_strategy': 1.2,          # TEMA, moyenne mobile lissée
        'atr_strategy': 0.7,           # ATR, indicateur de volatilité (moins utile pour l'entrée)
        'keltner_channel_strategy': 1,   # Canal de Keltner, similaire aux bandes de Bollinger
        'donchian_channel_strategy': 1,  # Canal de Donchian, indicateur de volatilité
        'rvi_strategy': 1.1,           # RVI, indicateur de momentum
        'momentum_strategy': 1.5       # Momentum, indicateur de force de la tendance
    }

    for index, row in data.iterrows():
        symbol = row['symbol']

        # Vérification si le symbole est déjà en position
        if symbol in open_positions:
            check_stop_losses()
            continue
        trade_amount = calculate_trade_amount(capital, row['Close'], symbol)
        # Vérifier si la quantité est supérieure à zéro
        if trade_amount <= 0:
            logging.warning(f"Trade amount for {symbol} is too small: {trade_amount}. Skipping trade.")
            continue

        row_df = data.iloc[max(0, index-50):index+1]
        strategies_signals = apply_strategies(row_df)

        # Calcul des scores pondérés pour l'achat et la vente
        buy_score = 0
        sell_score = 0
        for strategy, signal in strategies_signals.items():
            if isinstance(signal, dict):
                for sig_name, sig_value in signal.items():
                    if sig_value is not None:  # Ignorer les signaux None
                        if sig_value:  # Signal d'achat
                            buy_score += strategy_weights.get(strategy, 1)  # Poids par défaut de 1
                        else:  # Signal de vente
                            sell_score += strategy_weights.get(strategy, 1)
            else:
                if signal is not None:
                    if signal:
                        buy_score += strategy_weights.get(strategy, 1)
                    else:
                        sell_score += strategy_weights.get(strategy, 1)

        if buy_score >= 3 and row['symbol'] not in open_positions:
            logging.info(f"Buy signal for {symbol} at {row['Close']} (Buy score: {buy_score}, Sell score: {sell_score})")
            order_filled = place_buy_order(symbol, trade_amount)
            
            if order_filled:
                # Attendre que l'ordre soit rempli
                while True:
                    order_status = client.get_order(symbol=symbol, orderId=order['orderId'])
                    if order_status['status'] == ORDER_STATUS_FILLED:
                        set_stop_loss(symbol, open_positions[symbol]['entry_price'], 0.01)
                        used_capital += trade_amount * row['Close']
                        break
                    else:
                        time.sleep(1)  # Attendre 1 seconde avant de revérifier
        #...

        elif sell_score >= 3 and symbol in open_positions:
            logging.info(f"Sell signal for {symbol} at {row['Close']} (Buy score: {buy_score}, Sell score: {sell_score})")
            place_sell_order(symbol, open_positions[symbol]['quantity'])  # Vendre la quantité détenue
            used_capital -= open_positions[symbol]['quantity'] * row['Close']  # Mettre à jour le capital utilisé


def run_bot():
    global used_capital
    capital = 20
    used_capital = 0.0

    # Récupérer les nouvelles données et les enregistrer
    new_data = fetch_new_data(symbols)
    if not new_data.empty:
        new_data.to_csv('data/new_data.csv', index=False)

    # Charger les données
    data = pd.read_csv('data/new_data.csv')
    print("Available columns in loaded data:", data.columns)
    trade_decision(data, capital)

# Planification de l'exécution du bot toutes les heures
schedule.every().hour.do(run_bot)

def main():
    # Lancer le bot une première fois au démarrage
    run_bot()

    # Boucle principale
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Arrêt manuel du bot...")
            # Annuler les ordres ouverts (si nécessaire)
            open_orders = client.get_open_orders()
            for order in open_orders:
                client.cancel_order(symbol=order['symbol'], orderId=order['orderId'])
                logging.info(f"Ordre {order['orderId']} annulé pour {order['symbol']}")

            # Sauvegarder l'état du bot (si nécessaire)
            # ...

            # Afficher un message de fin
            logging.info("Bot arrêté avec succès.")
            break  # Sortir de la boucle en cas d'interruption
    

if __name__ == "__main__":
    main()