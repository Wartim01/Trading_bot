import ccxt
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from textblob import TextBlob
import time
import logging
import requests
import schedule
import joblib
import ta

# Configuration
api_key = 'Cw6pBOG5Ct1GElMgwfD28PsVLKI9BW73STuVzEfJvIjSGIIPlNEB4TmDyBIWB4kT'
api_secret = 'i3H2TpMxndXmfDNIQf5oNA17fiy0x8QQhumIxwab1L6lMpGSt8QI7JaSZaFwkIog'
twitter_bearer_token = 'AAAAAAAAAAAAAAAAAAAAANcSuAEAAAAAu8y3Xbf%2B5byeaai1UMum6sqLiQE%3D1anQgrLCNJ3KryDepkXHsu7Dd0LrWbYC0wX9xjOv1WIOmA6U0B'
newsapi_key = '809b47ee129f4a1d9942760ca5dcb1a7'
symbol = 'BTC/USDT'
initial_balance = 20
risk_management_factor = 0.02  # 2% du solde à risque par trade
duration = 12 * 60 * 60  # 12 heures

# Configuration des logs
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Initialisation de l'API Binance
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

# Récupérer les données historiques
def fetch_ohlcv(symbol, timeframe='1m', limit=100):
    attempts = 3
    for attempt in range(attempts):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des données OHLCV : {e}")
            time.sleep(5)
    return None

# Préparation des données
def prepare_data(df):
    df['return'] = df['close'].pct_change()
    df['sma_5'] = df['close'].rolling(window=5).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_hist'] = macd.macd_diff()
    df.dropna(inplace=True)
    return df

# Entraînement du modèle ML
def train_model(df):
    df['target'] = np.where(df['return'].shift(-1) > 0, 1, 0)
    features = ['sma_5', 'sma_20', 'rsi', 'macd', 'macd_signal']
    X = df[features]
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, 'trading_model.pkl')
    return model

# Charger le modèle
def load_model():
    try:
        model = joblib.load('trading_model.pkl')
        return model
    except FileNotFoundError:
        df = fetch_ohlcv(symbol)
        if df is not None:
            df = prepare_data(df)
            model = train_model(df)
            return model
        else:
            raise Exception("Impossible de charger ou d'entraîner le modèle")

# Analyse de sentiment
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Récupérer les tweets récents
def fetch_tweets(keyword):
    url = f"https://api.twitter.com/2/tweets/search/recent?query={keyword}&max_results=10"
    headers = {'Authorization': f'Bearer {twitter_bearer_token}'}
    response = requests.get(url, headers=headers)
    tweets = response.json()
    return tweets

# Récupérer les articles de news
def fetch_news(keyword):
    url = f"https://newsapi.org/v2/everything?q={keyword}&apiKey={newsapi_key}"
    response = requests.get(url)
    news = response.json()
    return news

# Récupérer les posts Reddit
def fetch_reddit_posts(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=10"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    posts = response.json()
    return posts

# Obtenir le score de sentiment pour BTC
def get_market_sentiment():
    tweets = fetch_tweets('Bitcoin')
    news = fetch_news('Bitcoin')
    reddit_posts = fetch_reddit_posts('Bitcoin')

    sentiment_scores = [analyze_sentiment(tweet['text']) for tweet in tweets['data']] + \
                       [analyze_sentiment(article['title']) for article in news['articles']] + \
                       [analyze_sentiment(post['data']['title']) for post in reddit_posts['data']['children']]
    
    avg_sentiment = np.mean(sentiment_scores)
    return avg_sentiment

# Réentraînement périodique du modèle
def retrain_model():
    df = fetch_ohlcv(symbol)
    if df is not None:
        df = prepare_data(df)
        train_model(df)
        logging.info("Modèle réentraîné")

schedule.every().day.at("00:00").do(retrain_model)

# Charger le modèle initial
model = load_model()

# Boucle de trading
start_time = time.time()
while time.time() - start_time < duration:
    try:
        schedule.run_pending()
        df = fetch_ohlcv(symbol)
        if df is None:
            continue
        df = prepare_data(df)
        
        # Prédire
        latest_data = df[['sma_5', 'sma_20', 'rsi', 'macd', 'macd_signal']].iloc[-1].values.reshape(1, -1)
        prediction = model.predict(latest_data)
        
        current_price = df['close'].iloc[-1]
        stop_loss = 0.02  # exemple de stop loss à 2%
        take_profit = 0.04  # exemple de take profit à 4%
        stop_loss_price = current_price * (1 - stop_loss)
        take_profit_price = current_price * (1 + take_profit)

        # Calculer la taille du trade en fonction de la gestion des risques
        balance = exchange.fetch_balance()
        usdt_balance = balance['total']['USDT']
        max_risk_amount = usdt_balance * risk_management_factor
        trade_amount = max_risk_amount / (current_price * stop_loss)

        if prediction == 1 and get_market_sentiment() > 0:
            # Placer un ordre d'achat
            order = exchange.create_market_buy_order(symbol, trade_amount)
            logging.info(f"Ordre d'achat exécuté: {order}")

            # Surveiller le trade
            while True:
                time.sleep(60)
                new_price = exchange.fetch_ticker(symbol)['last']
                
                if new_price <= stop_loss_price:
                    exchange.create_market_sell_order(symbol, trade_amount)
                    logging.info(f"Stop-Loss déclenché à {new_price}")
                    break
                elif new_price >= take_profit_price:
                    exchange.create_market_sell_order(symbol, trade_amount)
                    logging.info(f"Take-Profit déclenché à {new_price}")
                    break

    except Exception as e:
        logging.error(f"Erreur: {e}")

# Récupérer le solde final
balance = exchange.fetch_balance()
usdt_balance = balance['total']['USDT']
logging.info(f"Solde final: {usdt_balance} USDT")
