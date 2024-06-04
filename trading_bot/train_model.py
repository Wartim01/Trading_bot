import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping
import joblib
from sklearn.preprocessing import StandardScaler

# Chemin d'accès aux données
data_path = 'data/historical_data.csv'

# Charger les données historiques
try:
    data = pd.read_csv(data_path)
except FileNotFoundError:
    print(f"Erreur : Fichier de données '{data_path}' introuvable.")
    exit(1)  # Quitte le script si les données ne sont pas disponibles

# Vérifier les valeurs manquantes et infinies
print("Valeurs manquantes :")
print(data.isnull().sum().to_markdown(numalign="left", stralign="left"))
data.replace([np.inf, -np.inf], np.nan, inplace=True)
data.dropna(inplace=True)

# Caractéristiques et cible
features = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote_asset_volume', 'Number_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume']
target = 'Close'
X = data[features]
y = data[target]

# Normalisation des données
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Séparation des données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Modèle de Forêt Aléatoire pour régression
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
joblib.dump(rf_model, 'models/rf_model.pkl')  # Sauvegarde dans le répertoire 'models'

# Modèle de Réseau Neuronal pour régression
nn_model = Sequential()
nn_model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
nn_model.add(Dense(32, activation='relu'))
nn_model.add(Dense(1)) 
nn_model.compile(loss='mean_squared_error', optimizer='adam')
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
nn_model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.1, callbacks=[early_stopping])
nn_model.save('models/nn_model.h5')  # Sauvegarde dans le répertoire 'models'

# Évaluation des modèles sur l'ensemble de test
rf_predictions = rf_model.predict(X_test)
nn_predictions = nn_model.predict(X_test).flatten()
rf_mse = mean_squared_error(y_test, rf_predictions)
nn_mse = mean_squared_error(y_test, nn_predictions)
rf_r2 = r2_score(y_test, rf_predictions)
nn_r2 = r2_score(y_test, nn_predictions)

print("\nÉvaluation des modèles sur l'ensemble de test :")
print(f"Random Forest - MSE: {rf_mse:.4f}, R²: {rf_r2:.4f}")
print(f"Neural Network - MSE: {nn_mse:.4f}, R²: {nn_r2:.4f}")
