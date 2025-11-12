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


def get_crypto_prices_coinmarketcap(data, wallet):
    data = data.copy()
    # Get LP and DLMM values
    # if wallet == 'phantom':
    #     data = get_lp_dlmm_values(data)

    # Coinmarketcap API
    api_key = 'b6d2dd7f-93c1-473e-b763-47db602a2f0e'
    # Set up the request headers
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    data['ticker'] = data['ticker'].fillna('-')
    tickers = list(data[~data['ticker'].str.contains('-|&')]['ticker'].unique())
    tickers_rewards = list(data['rewards ticker'].unique())
    tickers.extend(tickers_rewards)
    tickers = [x for x in tickers if pd.notna(x) and x]
    prices = {}
    for ticker in tickers:
        if ticker == 'EIGEN':
            continue
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
    data['value'] = data['value'].fillna(0)
    data['rewards value'] = data['rewards value'].fillna(0)
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
    data['value'] = data['value'].fillna(0)
    data['rewards value'] = data['rewards value'].fillna(0)
    data['total value'] = data['value'] + data['rewards value']

    return data


def sum_numeric_values(data):
    """Sums the values in a dictionary that are not strings."""
    total_sum = 0
    for value in data.values():
        if not isinstance(value, str):
            total_sum += value
    return total_sum


def fill_dict(metric, keys, values):
    for i in range(len(keys)):
        metric[keys[i]] = values[i]

    return metric


def calculate_metrics(phantom_data, phantom2_data, solfl_data, solfl2_data,
                      backpack_data, metamask_data, okx_data, seeker_data,
                      phantomtablet1_data, phantomtablet2_data, solfltablet1_data, solfltablet2_data,
                      slushlaptop1_data, slushlaptop2_data, backpacklaptop1_data, backpacklaptop2_data,
                      backpacklaptop3_data, backpacklaptop4_data, backpackphone1_data, backpackphone2_data,
                      slushphone1_data, slushphone2_data, slushphone3_data, slushphone4_data,
                      bitget_data, bybit_data, photon_data, ledger1_data):
    """
    This function calculates relevant metrics for the performance of the wallets
    :param phantom_data:
    :param metamask_data:
    :param trust_data:
    :param okx_data:
    :param solfl_data:
    :param phantom2_data:
    :param solfl2_data:
    :param backpack_data:
    :return:
    """

    # concat all dataframes
    df_list = [phantom_data, phantom2_data, solfl_data, solfl2_data,
              backpack_data, metamask_data, okx_data, seeker_data,
              phantomtablet1_data, phantomtablet2_data, solfltablet1_data, solfltablet2_data,
              slushlaptop1_data, slushlaptop2_data, backpacklaptop1_data, backpacklaptop2_data,
              backpacklaptop3_data, backpacklaptop4_data, backpackphone1_data, backpackphone2_data,
              slushphone1_data, slushphone2_data, slushphone3_data, slushphone4_data,
               bitget_data, bybit_data, photon_data, ledger1_data]
    big_df = pd.concat(df_list, ignore_index=True)

    # group by ticker and sum 'total value'
    result = big_df.groupby("ticker", as_index=False)[['amount', 'total value']].sum()
    result[['amount', 'total value']] = result[['amount', 'total value']].round(2)

    total_value = result["total value"].sum().round(2)

    # add percentage column rounded to 2 decimals
    result["percentage"] = (result["total value"] / total_value * 100).round(2)

    # add total row
    total = pd.DataFrame({
        "ticker": ["Total"],
        "amount": ['nan'],
        "total value": [total_value],
        "percentage": [100.00]
    })

    # concat total row temporarily for sorting
    metrics = pd.concat([result, total], ignore_index=True)

    # separate total row, sort rest by percentage descending
    metrics_no_total = metrics[metrics['ticker'] != "Total"].sort_values(
        by='percentage', ascending=False
    )

    # concat sorted rows with total at the end
    metrics_per_ticker = pd.concat([metrics_no_total, metrics[metrics['ticker'] == "Total"]], ignore_index=True)

    # format columns as strings with 2 decimals
    metrics_per_ticker['total value'] = metrics_per_ticker['total value'].map(lambda x: f"{x:.2f}")
    metrics_per_ticker['percentage'] = metrics_per_ticker['percentage'].map(lambda x: f"{x:.2f}%")
    metrics_per_ticker.to_csv('results/metrics_per_ticker.csv')


    keys = ['Metric', 'Phantom', 'Phantom 2', 'Solflare', 'Solflare 2',
            'Backpack', 'Metamask', 'OKX', 'Seeker',
            'Phantom Tablet 1', 'Phantom Tablet 2', 'Solflare Tablet 1', 'Solflare Tablet 2',
            'Slush Laptop 1', 'Slush Laptop 2', 'Backpack Laptop 1', 'Backpack Laptop 2',
            'Backpack Laptop 3', 'Backpack Laptop 4', 'Backpack Phone 1', 'Backpack Phone 2',
            'Slush Phone 1', 'Slush Phone 2', 'Slush Phone 3', 'Slush Phone 4', 'Bitget', 'Bybit', 'Photon']

    portfolio_value = {}

    port_values = ['Portfolio value', phantom_data['total value'].sum(), phantom2_data['total value'].sum(), solfl_data['total value'].sum(), solfl2_data['total value'].sum(),
                    backpack_data['total value'].sum(), metamask_data['total value'].sum(), okx_data['total value'].sum(), seeker_data['total value'].sum(),
                    phantomtablet1_data['total value'].sum(), phantomtablet2_data['total value'].sum(), solfltablet1_data['total value'].sum(), solfltablet2_data['total value'].sum(),
                    slushlaptop1_data['total value'].sum(), slushlaptop2_data['total value'].sum(), backpacklaptop1_data['total value'].sum(), backpacklaptop2_data['total value'].sum(),
                    backpacklaptop3_data['total value'].sum(), backpacklaptop4_data['total value'].sum(), backpackphone1_data['total value'].sum(), backpackphone2_data['total value'].sum(),
                    slushphone1_data['total value'].sum(), slushphone2_data['total value'].sum(), slushphone3_data['total value'].sum(), slushphone4_data['total value'].sum(),
                   bitget_data['total value'].sum(), bybit_data['total value'].sum(), photon_data['total value'].sum(), ledger1_data['total value'].sum()]
    portfolio_value = fill_dict(portfolio_value, keys, port_values)
    portfolio_value['Total'] = sum_numeric_values(portfolio_value)

    metrics = pd.Series(portfolio_value)
    metrics_rounded = metrics.apply(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)
    metrics_rounded.to_csv('results/metrics_table.csv')

    # Save metrics over time
    create_directory('results/metrics over time/')
    today = date.today().strftime('%Y-%m-%d')
    date_path = f'results/metrics over time/{today}.csv'
    metrics_rounded.to_csv(date_path)

    date_path_ticker = f'results/metrics per ticker over time/{today}.csv'
    metrics_per_ticker.to_csv(date_path_ticker)


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
        ax.text(x_pos, y_pos, '$' + str(value), ha='center', va='center', fontsize=8)

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
    for metric in metrics:
        for wallet in wallets:
            data = pd.read_csv(f'results/wallets over time/{wallet}_over_time.csv', index_col=0)
            dataframes[wallet] = data
            wallet_data[wallet] = dataframes[wallet][metric]

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
