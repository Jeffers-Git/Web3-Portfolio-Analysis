"""
This script runs the analysis for the sui wallet
The coinmarketcap API is used to import token prices
"""
from functions import get_crypto_prices_coinmarketcap, save_to_excel_wallets, create_directory


def run(data, config):
    # basic data cleaning
    data = data.dropna(axis=0, how='all')
    data = data.reset_index(drop=True)
    data.columns = data.columns.str.lower()
    data['ticker'] = data['ticker'].str.upper()

    data = get_crypto_prices_coinmarketcap(data)
    create_directory('results/sui/')
    data.to_csv('results/sui/wallet.csv')

    # Replace the wallet sheet with the updated data
    save_to_excel_wallets(data, wallet='sui')

    value_per_dapp = data.groupby(['app'])[['value', 'rewards']].sum()
    value_per_dapp = value_per_dapp.rename(columns={'value': 'TVL'})
    # exclude total in case of rerun in debug
    value_per_dapp['Total'] = value_per_dapp[value_per_dapp.index != 'Total'].sum(axis=1)
    value_per_dapp.loc['Total'] = value_per_dapp[value_per_dapp.index != 'Total'].sum()
    value_per_dapp = value_per_dapp.round(2)
    value_per_dapp.to_csv('results/sui/value_per_dapp.csv')

    return data
