"""
This script runs the analysis for the keplr wallet
"""
import pandas as pd
import requests

def get_crypto_prices_coinmarketcap(data):
    # Coinmarketcap API
    api_key = 'b6d2dd7f-93c1-473e-b763-47db602a2f0e'
    # Set up the request headers
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    tickers = data['ticker'].unique()
    prices = {}
    for ticker in tickers:
        params = {
            'symbol': ticker  # Example token symbol (Ethereum)
        }
        # Make the API request
        response = requests.get(url, headers=headers, params=params)
        response = response.json()
        # Extract token price information from the response
        price = response['data'][ticker]['quote']['USD']['price']
        prices[ticker] = price

    data['prices'] = data['ticker'].map(prices)
    data['value'] = data['amount'] * data['prices']

    return data

def run(data):
    # basic data cleaning
    data = data.dropna(axis=0, how='all')
    data = data.reset_index(drop=True)
    # data = data.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    data.columns = data.columns.str.lower()

    data = get_crypto_prices_coinmarketcap(data)

    value_per_dapp = data.groupby(['app'])['value'].sum()
    # exclude total in case of rerun in debug
    value_per_dapp['total'] = value_per_dapp[value_per_dapp.index != 'total'].sum()
    value_per_dapp = value_per_dapp.round(2)
    value_per_dapp.to_csv('results/keplr/value_per_dapp.csv')

    value_per_validator = data.groupby(['app', 'validator'])['value'].sum()
    value_per_validator['total'] = value_per_dapp['total']
    value_per_validator = value_per_validator.round(2)
    value_per_validator.to_csv('results/keplr/value_per_validator.csv')

    return data

