import os

# Code pour créer/mettre à jour les fichiers
def create_or_update_file(filename, content):
    # Si le fichier existe déjà, sauvegarder l'original
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            original_content = file.read()
        with open(filename + '.bak', 'w') as backup_file:
            backup_file.write(original_content)
    
    # Écrire le nouveau contenu dans le fichier
    with open(filename, 'w') as file:
        file.write(content)

# Contenu du fichier historical_data.py
historical_data_content = """\
import pandas as pd

def load_historical_data(filepath):
    return pd.read_csv(filepath)
"""

# Contenu du fichier backtester.py
backtester_content = """\
import pandas as pd
from trading_bot import TradingBot

class Backtester:
    def __init__(self, strategy, historical_data):
        self.strategy = strategy
        self.historical_data = historical_data
        self.trades = []

    def run(self):
        for index, row in self.historical_data.iterrows():
            trade_signal = self.strategy(row)
            if trade_signal:
                self.trades.append(trade_signal)
        
        return self.trades
"""

# Contenu du fichier strategies.py
strategies_content = """\
import numpy as np
import pandas as pd

def simple_moving_average_strategy(data):
    short_window = 40
    long_window = 100

    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()

    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()

    return signals
"""

# Contenu du fichier main.py
main_content = """\
from historical_data import load_historical_data
from backtester import Backtester
from strategies import simple_moving_average_strategy

# Charger les données historiques
historical_data = load_historical_data('path_to_historical_data.csv')

# Initialiser le backtester avec une stratégie
backtester = Backtester(simple_moving_average_strategy, historical_data)

# Exécuter le backtesting
backtest_results = backtester.run()

# Afficher les résultats
print(backtest_results)
"""

# Création/mise à jour des fichiers
create_or_update_file('historical_data.py', historical_data_content)
create_or_update_file('backtester.py', backtester_content)
create_or_update_file('strategies.py', strategies_content)
create_or_update_file('main.py', main_content)

print("Fichiers créés/mis à jour avec succès.")
