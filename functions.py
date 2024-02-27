"""
This script contains functions used in the analysis
"""
import requests
import pandas as pd
import math
import numpy as np


def get_lp_dlmm_values(data):
    # Liquidity pools
    data_LP = data[data['purpose'] == 'Liquidity pool']
    lp_tickers = data_LP['ticker'].unique()
    bool_LP = input("Do you want to enter new LP values? ")
    if bool_LP == 'yes':
        for lp in lp_tickers:
            lp_value = input(f"Enter dollar value for {lp} LP: ")
            lp_value = float(lp_value)
            data.loc[data['ticker'] == lp, 'value'] = lp_value
    elif bool_LP == 'no':
        pass
    else:
        raise ValueError("Not a valid answer bro")

    # DLMMs
    data_dlmm = data[data['purpose'] == 'DLMM']
    dlmm_tickers = data_dlmm['ticker'].unique()
    bool_dlmm = input("Do you want to enter new DLMM values? ")
    if bool_dlmm == 'yes':
        for dlmm in dlmm_tickers:
            dlmm_value = input(f"Enter dollar value for {dlmm} DLMM: ")
            dlmm_value = float(dlmm_value)
            data.loc[data['ticker'] == dlmm, 'value'] = dlmm_value
    elif bool_dlmm == 'no':
        pass
    else:
        raise ValueError("Not a valid answer bro")

    return data


def get_crypto_prices_coinmarketcap(data, meteora=False):
    # Coinmarketcap API
    data = data.copy()
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
            'symbol': ticker
        }
        # Make the API request
        response = requests.get(url, headers=headers, params=params)
        response = response.json()
        # Extract token price information from the response
        price = response['data'][ticker]['quote']['USD']['price']
        prices[ticker] = price

    data.loc[:, 'prices'] = data['ticker'].map(prices)
    data.loc[~data['prices'].isna(), 'value'] = data['amount'] * data['prices']
    data.loc[:, 'value'] = np.where(data['purpose'] == 'Borrowing', -data['value'], data['value'])

    # Get LP and DLMM values
    if meteora:
        data = get_lp_dlmm_values(data)

    return data


def get_crypto_prices_coingecko(data):
    # Coingecko API
    data = data.copy()
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

    data.loc[:, 'prices'] = data['ticker'].map(prices)
    data.loc[~data['prices'].isna(), 'value'] = data['amount'] * data['prices']

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


def save_to_excel_wallets(data, wallet='phantom'):
    with pd.ExcelWriter('data/Web3 wallets.xlsx', engine='openpyxl', mode='a') as writer:
        del writer.book[wallet]
        writer.book.save('data/Web3 wallets.xlsx')
    with pd.ExcelWriter('data/Web3 wallets.xlsx', engine='openpyxl', mode='a') as writer:
        data.to_excel(writer, sheet_name=wallet, index=False)






# meteora_key = 'https://app.meteora.ag/pools/D58yVqQUNk6LWqXoiWfYyskACuUNdF8xi6EYVJGjryFq'
        # response = requests.get(meteora_key)
        # meteora = response.json()
        # selected_dict = []
        # for d in meteora['data']:
        #     if 'pool_name' in d and d['pool_name'] == 'BSOL-JUP':
        #         selected_dict = d
        #         break
        #
        # # Connect to a Solana RPC node
        # rpc_url = 'https://api.mainnet-beta.solana.com'
        # solana_client = Client(rpc_url)
        # solana_client.get_supply()
        # solana_client.get_account_info()