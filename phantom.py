"""
This script runs the analysis for the phantom wallet.
The coinmarketcap API is used to import token prices
"""
from functions import get_crypto_prices_coinmarketcap


def run(data):
    # basic data cleaning
    data = data.dropna(axis=0, how='all')
    data = data.reset_index(drop=True)
    data.columns = data.columns.str.lower()
    data['ticker'] = data['ticker'].str.upper()
    data = data[data['purpose'] != 'DLMM']
    data['amount'] = data['amount'].astype(float)

    data = get_crypto_prices_coinmarketcap(data, meteora=True)
    data.to_csv('results/phantom/wallet.csv')

    value_per_dapp = data.groupby(['app'])['value'].sum()
    # exclude total in case of rerun in debug
    value_per_dapp['Total'] = value_per_dapp[value_per_dapp.index != 'Total'].sum()
    value_per_dapp = value_per_dapp.round(2)
    value_per_dapp.to_csv('results/phantom/value_per_dapp.csv')

    value_per_purpose = data.groupby(['purpose'])['value'].sum()
    value_per_purpose['Total'] = value_per_purpose[value_per_purpose.index != 'Total'].sum()
    value_per_purpose = value_per_purpose[value_per_purpose != 0]
    value_per_purpose = value_per_purpose.round(2)
    value_per_purpose.to_csv('results/phantom/value_per_purpose.csv')

    return data
