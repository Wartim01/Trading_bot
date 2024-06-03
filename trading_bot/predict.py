import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler

# Charger le modèle Random Forest
rf_model = joblib.load('models/rf_model.pkl')

# Charger le modèle Neural Network
nn_model = load_model('models/nn_model.h5')

# Charger et préparer de nouvelles données pour les prédictions
new_data = pd.read_csv('data/new_data.csv')
X_new = new_data[['Open', 'High', 'Low', 'Close', 'Volume', 'Quote_asset_volume', 'Number_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume']]

# Normaliser les nouvelles données
scaler = StandardScaler()
X_new_scaled = scaler.fit_transform(X_new)

# Prédictions avec Random Forest
rf_predictions = rf_model.predict(X_new_scaled)

# Prédictions avec Neural Network
nn_predictions = nn_model.predict(X_new_scaled)

# Afficher les prédictions
new_data['RF_Predictions'] = rf_predictions
new_data['NN_Predictions'] = nn_predictions
print(new_data)

# Sauvegarder les prédictions dans un nouveau fichier CSV
new_data.to_csv('data/predictions.csv', index=False)
