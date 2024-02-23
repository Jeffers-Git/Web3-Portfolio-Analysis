"""
This scrip runs the analysis for the phantom wallet
"""
import pandas as pd
import requests


def get_crypto_prices(data):
    # Coingecko API
    api = "https://api.coingecko.com/api/v3/simple/price"
    crypto_mapping = pd.read_csv('tables/crypto_mapping.csv')
    tickers = data[~data['ticker'].str.contains('-|usdt|usdc')]['ticker'].unique()
    prices = {}
    for ticker in tickers:
        id = crypto_mapping[crypto_mapping['ticker'] == ticker]['id'].iloc[0]
        parameters = {
            "ids": id,
            "vs_currencies": "usd"
        }
        response = requests.get(api, params=parameters)
        data = response.json()
        price = data[id]['usd']
        prices[ticker] = price


def run(data):
    # basic data cleaning
    data = data.dropna(axis=0, how='all')
    data = data.reset_index(drop=True)
    data = data.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    data.columns = data.columns.str.lower()

    data = get_crypto_prices(data)

    data.groupby(['App', 'Purpose']).sum()
