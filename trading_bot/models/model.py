# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import logging

# Configuration de la journalisation
logging.basicConfig(filename='training.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def train_model(data):
    logging.info("Début de l'entraînement du modèle")
    
    # Ajout des indicateurs manquants
    required_indicators = ['rsi', 'ma50', 'ma200', 'macd']
    for indicator in required_indicators:
        if indicator not in data.columns:
            logging.error(f"{indicator} manquant dans les données")
            return None
    
    X = data[['open', 'high', 'low', 'close', 'volume', 'rsi', 'ma50', 'ma200', 'macd']]
    y = (data['close'].shift(-1) > data['close']).astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(X[:-1], y[:-1], test_size=0.2, random_state=42)
    
    logging.info("Début de l'entraînement du RandomForestClassifier")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    logging.info("Évaluation du modèle")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    logging.info(f"Model accuracy: {accuracy:.2f}")
    
    with open('trading_bot/models/trading_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    logging.info("Modèle sauvegardé avec succès")
    
    return model

def load_model():
    try:
        with open('trading_bot/models/trading_model.pkl', 'rb') as f:
            model = pickle.load(f)
        logging.info("Modèle chargé avec succès")
        return model
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        return None
