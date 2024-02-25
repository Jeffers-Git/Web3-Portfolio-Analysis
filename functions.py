"""
This script contains functions used in the analysis
"""
import requests
import pandas as pd
import math
import numpy as np


def get_crypto_prices_coinmarketcap(data):
    # Coinmarketcap API
    api_key = 'b6d2dd7f-93c1-473e-b763-47db602a2f0e'
    # Set up the request headers
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    tickers = data[~data['ticker'].str.contains('-|&')]['ticker'].unique()
    tickers = [x for x in tickers if not (isinstance(x, float) and math.isnan(x))]
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
    data['value'] = np.where(data['purpose'] == 'Borrowing', -data['value'], data['value'])

    return data


def get_crypto_prices_coingecko(data):
    # Coingecko API
    api = "https://api.coingecko.com/api/v3/simple/price"
    crypto_mapping = pd.read_csv('tables/crypto_mapping.csv')
    tickers = data['ticker'].unique()
    tickers = [x for x in tickers if not (isinstance(x, float) and math.isnan(x))]
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

    data['prices'] = data['ticker'].map(prices)
    data['value'] = data['amount'] * data['prices']

    return data


def calculate_metrics(investments, phantom_data, keplr_data, metamask_data, sui_data):
    """
    This function calculates relevant metrics for the performance of the wallets
    :param investments:
    :param phantom_data:
    :param keplr_data:
    :param metamask_data:
    :param sui_data:
    :return:
    """
    current_value = {'Metric': 'Current value',
                     'Phantom': phantom_data['value'].sum(),
                     'Keplr': keplr_data['value'].sum(),
                     'Metamask': metamask_data['value'].sum(),
                     'Sui': sui_data['value'].sum()}
    current_value['Total'] = current_value['Phantom'] + current_value['Keplr'] + \
                             current_value['Metamask'] + current_value['Sui']
    roi_absolute = {'Metric': 'Absolute ROI',
                    'Phantom': current_value['Phantom'] - investments['Phantom'][0],
                    'Keplr': current_value['Keplr'] - investments['Keplr'][0],
                    'Metamask': current_value['Metamask'] - investments['Metamask'][0],
                    'Sui': current_value['Sui'] - investments['Sui'][0],
                    'Total': current_value['Total'] - investments['Total'][0]}
    roi_relative = {'Metric': 'ROI (%)',
                    'Phantom': roi_absolute['Phantom'] / investments['Phantom'][0] * 100,
                    'Keplr': roi_absolute['Keplr'] / investments['Keplr'][0] * 100,
                    'Metamask': roi_absolute['Metamask'] / investments['Metamask'][0] * 100,
                    'Sui': roi_absolute['Sui'] / investments['Sui'][0] * 100,
                    'Total': roi_absolute['Total'] / investments['Total'][0] * 100}
    metrics_to_add = [current_value, roi_absolute, roi_relative]

    metrics = investments
    for metric in metrics_to_add:
        metrics = metrics.append(metric, ignore_index=True)
    metrics = metrics.set_index('Metric')
    metrics = metrics.round(2)
    metrics.to_csv('results/metrics_table.csv')

    return metrics
