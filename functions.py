"""
This script contains functions used in the analysis
"""
import requests
import pandas as pd


def get_crypto_prices_coinmarketcap(data, wallet=None):
    # Coinmarketcap API
    api_key = 'b6d2dd7f-93c1-473e-b763-47db602a2f0e'
    # Set up the request headers
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    tickers = data[~data['ticker'].str.contains('-')]['ticker'].unique()
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


def get_crypto_prices_coingecko(data):
    # Coingecko API
    api = "https://api.coingecko.com/api/v3/simple/price"
    crypto_mapping = pd.read_csv('tables/crypto_mapping.csv')
    tickers = data[~data['ticker'].str.contains('-|usdt|usdc|jitosol|jup')]['ticker'].unique()
    prices = {}
    for ticker in tickers:
        id = crypto_mapping[crypto_mapping['ticker'] == ticker]['id'].iloc[0]
        parameters = {
            "ids": id,
            "vs_currencies": "usd"
        }
        response = requests.get(api, params=parameters)
        coingecko = response.json()
        price = coingecko[id]['usd']
        prices[ticker] = price

    prices['usdc'] = 1
    prices['usdt'] = 1
    data['prices'] = data['ticker'].map(prices)
    data['value'] = data['amount'] * data['prices']

    return data
