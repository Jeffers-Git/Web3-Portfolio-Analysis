"""
This script runs the analysis for the keplr wallet
The coinmarketcap API is used to import token prices
"""
from functions import (get_crypto_prices_coinmarketcap, get_crypto_prices_coingecko,
                       save_to_excel_wallets, create_directory)
import pandas as pd


def run(data, config):
    # basic data cleaning
    data = data.dropna(axis=0, how='all')
    data = data.reset_index(drop=True)
    data.columns = data.columns.str.lower()
    data['ticker'] = data['ticker'].str.upper()
    data['amount'] = data['amount'].astype(float)
    data['rewards ticker'] = data['rewards ticker'].fillna('').str.upper()
    data['rewards'] = data['rewards'].astype(float)

    ticker_coingecko = config['ticker_coingecko']
    data_coingecko = data[data['ticker'].isin(ticker_coingecko) | data['rewards ticker'].isin(ticker_coingecko)]
    if not data_coingecko.empty:
        data_coingecko = get_crypto_prices_coingecko(data_coingecko)
    data_rest = data[~(data['ticker'].isin(ticker_coingecko) | data['rewards ticker'].isin(ticker_coingecko))]
    data_rest = get_crypto_prices_coinmarketcap(data_rest)
    data = pd.concat([data_rest, data_coingecko], ignore_index=True)
    create_directory('results/keplr/')
    data.to_csv('results/keplr/wallet.csv')

    # Replace the wallet sheet with the updated data
    save_to_excel_wallets(data, wallet='keplr')

    value_per_dapp = data.groupby(['app'])[['value', 'rewards value', 'total value']].sum()
    value_per_dapp = value_per_dapp.rename(columns={'value': 'TVL'})
    # Exclude total in case of rerun in debug
    value_per_dapp.loc['Total'] = value_per_dapp[value_per_dapp.index != 'Total'].sum()
    value_per_dapp = value_per_dapp.round(2)
    value_per_dapp.to_csv('results/keplr/value_per_dapp.csv')

    value_per_validator = data.groupby(['app', 'validator'])['total value'].sum()
    value_per_validator.loc['Total'] = value_per_validator[value_per_validator.index != 'Total'].sum()
    value_per_validator = value_per_validator.round(2)
    value_per_validator.to_csv('results/keplr/value_per_validator.csv')

    return data

