"""
This script runs the analysis for the keplr wallet
The coinmarketcap API is used to import token prices
"""
from functions import get_crypto_prices_coinmarketcap, save_to_excel_wallets


def run(data, config):
    # basic data cleaning
    data = data.dropna(axis=0, how='all')
    data = data.reset_index(drop=True)
    data.columns = data.columns.str.lower()
    data['ticker'] = data['ticker'].str.upper()

    data = get_crypto_prices_coinmarketcap(data)
    data.to_csv('results/keplr/wallet.csv')

    # Replace the wallet sheet with the updated data
    save_to_excel_wallets(data, wallet='keplr')

    value_per_dapp = data.groupby(['app'])['value'].sum()
    # exclude total in case of rerun in debug
    value_per_dapp['Total'] = value_per_dapp[value_per_dapp.index != 'Total'].sum()
    value_per_dapp = value_per_dapp.round(2)
    value_per_dapp.to_csv('results/keplr/value_per_dapp.csv')

    value_per_validator = data.groupby(['app', 'validator'])['value'].sum()
    value_per_validator['Total'] = value_per_dapp['Total']
    value_per_validator = value_per_validator.round(2)
    value_per_validator.to_csv('results/keplr/value_per_validator.csv')

    return data

