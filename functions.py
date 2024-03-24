"""
This script contains functions used in the analysis
"""
import logging
import requests
import pandas as pd
import math
import numpy as np
import os
from matplotlib import pyplot as plt
import matplotlib.ticker as mticker
import datetime
from datetime import date, timedelta


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
    data = data.copy()
    # Get LP and DLMM values
    if meteora:
        data = get_lp_dlmm_values(data)

    # Coinmarketcap API
    api_key = 'b6d2dd7f-93c1-473e-b763-47db602a2f0e'
    # Set up the request headers
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    data = data.dropna(subset=['ticker'])
    tickers = list(data[~data['ticker'].str.contains('-|&')]['ticker'].unique())
    tickers_rewards = list(data['rewards ticker'].unique())
    tickers.extend(tickers_rewards)
    tickers = [x for x in tickers if pd.notna(x) and x]
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
    data.loc[:, 'rewards prices'] = data['rewards ticker'].map(prices)
    data.loc[~data['prices'].isna(), 'value'] = data['amount'] * data['prices']
    data.loc[:, 'value'] = np.where(data['purpose'] == 'Borrowing', -data['value'], data['value'])
    data.loc[~data['rewards prices'].isna(), 'rewards value'] = data['rewards'] * data['rewards prices']
    data['value'].fillna(0, inplace=True)
    data['rewards value'].fillna(0, inplace=True)
    data['total value'] = data['value'] + data['rewards value']

    return data


def get_crypto_prices_coingecko(data):
    # Coingecko API
    data = data.copy()
    api = "https://api.coingecko.com/api/v3/simple/price"
    crypto_mapping = pd.read_csv('tables/crypto_mapping.csv')
    tickers = list(data['ticker'].unique())
    tickers_rewards = list(data['rewards ticker'].unique())
    tickers.extend(tickers_rewards)
    tickers = [x for x in tickers if pd.notna(x) and x]
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
    data.loc[:, 'rewards prices'] = data['rewards ticker'].map(prices)
    data.loc[~data['prices'].isna(), 'value'] = data['amount'] * data['prices']
    data.loc[~data['rewards prices'].isna(), 'rewards value'] = data['rewards'] * data['rewards prices']
    data['value'].fillna(0, inplace=True)
    data['rewards value'].fillna(0, inplace=True)
    data['total value'] = data['value'] + data['rewards value']

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
    portfolio_value = {'Metric': 'Portfolio value',
                       'Phantom': phantom_data['total value'].sum(),
                       'Keplr': keplr_data['total value'].sum(),
                       'Metamask': metamask_data['total value'].sum(),
                       'Sui': sui_data['total value'].sum()}
    portfolio_value['Total'] = (portfolio_value['Phantom'] + portfolio_value['Keplr'] +
                                portfolio_value['Metamask'] + portfolio_value['Sui'])
    rewards = {'Metric': 'Rewards value',
               'Phantom': phantom_data['rewards value'].sum(),
               'Keplr': keplr_data['rewards value'].sum(),
               'Metamask': metamask_data['rewards value'].sum(),
               'Sui': sui_data['rewards value'].sum()}
    rewards['Total'] = (rewards['Phantom'] + rewards['Keplr'] +
                        rewards['Metamask'] + rewards['Sui'])
    roi_absolute = {'Metric': 'Absolute ROI',
                    'Phantom': portfolio_value['Phantom'] - investments['Phantom'][0],
                    'Keplr': portfolio_value['Keplr'] - investments['Keplr'][0],
                    'Metamask': portfolio_value['Metamask'] - investments['Metamask'][0],
                    'Sui': portfolio_value['Sui'] - investments['Sui'][0],
                    'Total': portfolio_value['Total'] - investments['Total'][0]}
    roi_relative = {'Metric': 'Relative ROI (%)',
                    'Phantom': roi_absolute['Phantom'] / investments['Phantom'][0] * 100,
                    'Keplr': roi_absolute['Keplr'] / investments['Keplr'][0] * 100,
                    'Metamask': roi_absolute['Metamask'] / investments['Metamask'][0] * 100,
                    'Sui': roi_absolute['Sui'] / investments['Sui'][0] * 100,
                    'Total': roi_absolute['Total'] / investments['Total'][0] * 100}
    metrics_to_add = [portfolio_value, rewards, roi_absolute, roi_relative]

    metrics = investments
    for metric in metrics_to_add:
        metrics = metrics.append(metric, ignore_index=True)
    metrics = metrics.set_index('Metric')
    metrics = metrics.round(2)
    metrics.to_csv('results/metrics_table.csv')

    # Save metrics over time
    create_directory('results/metrics over time/')
    today = date.today().strftime('%Y-%m-%d')
    date_path = f'results/metrics over time/{today}.csv'
    metrics.to_csv(date_path)

    return metrics


def plot_roi(df):
    fig, ax = plt.subplots(figsize=(12, 8))

    # Separate data for initial investment, rewards, and absolute ROI
    investment = df.loc["Initial investment"]
    total = df.loc["Portfolio value"]
    roi = df.loc["Absolute ROI"]
    roi_rel = df.loc['Relative ROI (%)']
    wallets = df.columns

    plt.xticks(range(len(wallets)), wallets)

    # Stacked bar plots
    ax.bar(range(len(wallets)), investment, label='Initial Investment')
    # Add initial investment
    for i, value in enumerate(investment):
        # Calculate bar center position (assuming bars have width 1)
        x_pos = i
        y_pos = value / 2
        ax.text(x_pos, y_pos, '$'+str(value), ha='center', va='center', fontsize=8)

    bars_roi = ax.bar(range(len(wallets)), roi, bottom=investment, label='ROI', color='green')
    # Add ROI and total
    j = 0
    for i, value in enumerate(roi):
        # Calculate bar center position (assuming bars have width 1)
        x_pos = i
        y_pos = investment[j] + value / 2
        label = '$' + str(value) + " (" + str(roi_rel[j]) + '%)'
        ax.text(x_pos, y_pos, label, ha='center', va='center', fontsize=8)
        total_height = investment[j] + bars_roi[j].get_height() + 270
        ax.text(x_pos, total_height, '$' + str(total[j]), ha='center', va='top', fontsize=8)
        j += 1

    # Customize the chart
    plt.xlabel("Wallets")
    plt.ylabel(f"Portfolio Value")
    plt.title(f"Portfolio Value Breakdown per Wallet")
    plt.legend()

    formatter = mticker.StrMethodFormatter("${x:.2f}")
    ax.yaxis.set_major_formatter(formatter)

    create_directory('results/plots/')
    plt.savefig('results/plots/absolute_roi.png')


def calculate_metrics_over_time(metrics, wallet):
    today = date.today()
    yesterday = today - timedelta(days=1)
    try:
        metrics_prev = pd.read_csv(f'results/metrics over time/{yesterday}.csv', index_col=0)
        pnl_day = metrics.loc['Absolute ROI', wallet] - metrics_prev.loc['Absolute ROI', wallet]
        pnl_day = pnl_day.round(2)
    except:
        pnl_day = 0

    if pnl_day > 0:
        logging.info(f'Your {wallet} daily PnL is ' + '$' + str(pnl_day) + ' :-)')
    else:
        logging.info(f'Your {wallet} daily PnL is ' + '$' + str(pnl_day) + ' :-(')

    if not os.path.exists(f'results/wallets over time/{wallet}_over_time.csv'):
        df = pd.DataFrame(columns=['Portfolio value', 'Absolute ROI', 'PnL day', 'Rewards'])
        df.index.name = 'Date'
        create_directory('results/wallets over time/')
    else:
        df = pd.read_csv(f'results/wallets over time/{wallet}_over_time.csv', index_col=0)

    today = str(today)
    df.loc[today, 'Portfolio value'] = metrics.loc['Portfolio value', wallet]
    df.loc[today, 'Absolute ROI'] = metrics.loc['Absolute ROI', wallet]
    df.loc[today, 'PnL day'] = pnl_day
    df.loc[today, 'Rewards'] = metrics.loc['Rewards value', wallet]
    df.to_csv(f'results/wallets over time/{wallet}_over_time.csv')


def create_plots_over_time(config):
    wallets = config['wallets']

    dataframes = {}
    wallet_data = pd.DataFrame(columns=wallets)
    metrics = config['metrics']
    metrics_dict = {}
    for metric in metrics:
        for wallet in wallets:
            data = pd.read_csv(f'results/wallets over time/{wallet}_over_time.csv', index_col=0)
            dataframes[wallet] = data
            wallet_data[wallet] = dataframes[wallet][metric]
        # metrics_dict[metric] = wallet_data

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot each column series using a different line style and label
        for wallet in wallets:
            ax.plot(wallet_data[wallet], label=wallet, linestyle='-')

        # Customize the plot
        plt.xlabel('Date')
        plt.ylabel(metric)
        plt.title(f'{metric} of all wallets over time')
        plt.legend()
        formatter = mticker.StrMethodFormatter("${x:.2f}")
        ax.yaxis.set_major_formatter(formatter)

        create_directory('results/plots/')
        plt.savefig(f'results/plots/{metric}_over_time.png')


def save_to_excel_wallets(data, wallet='phantom'):
    with pd.ExcelWriter('data/Web3 wallets.xlsx', engine='openpyxl', mode='a') as writer:
        del writer.book[wallet]
        writer.book.save('data/Web3 wallets.xlsx')
    with pd.ExcelWriter('data/Web3 wallets.xlsx', engine='openpyxl', mode='a') as writer:
        data.to_excel(writer, sheet_name=wallet, index=False)


def create_directory(directory_path):
    # Check if the directory exists
    if not os.path.exists(directory_path):
        # If it doesn't exist, create the directory
        os.makedirs(directory_path)


