import requests
from config import settings  # Changer config en config.settings pour l'import correct

def get_market_data():
    try:
        response = requests.get(f"{settings.BASE_URL}/market_data", headers={
            "API-KEY": settings.API_KEY
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching market data: {e}")
        return None

def execute_trade(action, market_data):
    try:
        response = requests.post(f"{settings.BASE_URL}/trade", json={
            "action": action,
            "price": market_data['price']
        }, headers={
            "API-KEY": settings.API_KEY
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error executing trade: {e}")
        return None
