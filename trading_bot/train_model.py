import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Charger les données historiques
data = pd.read_csv('data/historical_data.csv')

# Vérifier les valeurs manquantes et infinies
print(data.isnull().sum())
data.replace([np.inf, -np.inf], np.nan, inplace=True)
data.dropna(inplace=True)

# Utilisez vos caractéristiques
X = data[['Open', 'High', 'Low', 'Close', 'Volume', 'Quote_asset_volume', 'Number_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume']]
# Utilisez la colonne Close comme cible pour cet exemple
y = data['Close']

# Normalisation des données
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Diviser les données
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Modèle de Forêt Aléatoire pour régression
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
joblib.dump(rf_model, 'models/rf_model.pkl')

# Modèle de Réseau Neuronal pour régression
nn_model = Sequential()
nn_model.add(Dense(64, input_shape=(X_train.shape[1],), activation='relu'))
nn_model.add(Dense(32, activation='relu'))
nn_model.add(Dense(1))  # Pas d'activation finale pour la régression
nn_model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mean_squared_error'])
nn_model.fit(X_train, y_train, epochs=50, batch_size=10)
nn_model.save('models/nn_model.h5')

# Évaluation des modèles
rf_mse = rf_model.score(X_test, y_test)
nn_mse = nn_model.evaluate(X_test, y_test)[1]
print(f"Random Forest MSE: {rf_mse}")
print(f"Neural Network MSE: {nn_mse}")
