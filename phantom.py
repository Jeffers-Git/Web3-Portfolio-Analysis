"""
This scrip runs the analysis for the phantom wallet
"""
import pandas as pd
import requests


def get_crypto_prices(data):
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

    return data, prices


def run(data):
    # basic data cleaning
    data = data.dropna(axis=0, how='all')
    data = data.reset_index(drop=True)
    data = data.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    data.columns = data.columns.str.lower()

    data, prices = get_crypto_prices(data)
    data['prices'] = data['ticker'].map(prices)
    data['value'] = data['amount']*data['prices']

    value_per_dapp = data.groupby(['app'])['value'].sum()
    # exclude total in case of rerun in debug
    value_per_dapp['total'] = value_per_dapp[value_per_dapp.index != 'total'].sum()
    value_per_dapp.to_csv('results/value_per_dapp.csv')

    return data
