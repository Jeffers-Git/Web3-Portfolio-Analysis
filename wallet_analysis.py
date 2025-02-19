"""
This script runs the analysis for all wallets.
The coinmarketcap API is used to import token prices
"""
from functions import get_crypto_prices_coinmarketcap, get_crypto_prices_coingecko, \
    save_to_excel_wallets, create_directory
import pandas as pd
import warnings


def run(data, config, wallet):
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
    data_rest = get_crypto_prices_coinmarketcap(data_rest, wallet=wallet)
    data = pd.concat([data_rest, data_coingecko], ignore_index=True)
    create_directory(f'results/{wallet}/')
    data.to_csv(f'results/{wallet}/wallet.csv')

    # Replace the wallet sheet with the updated data
    save_to_excel_wallets(data, wallet=wallet)

    # Warn about SOL for fees running low
    if wallet == 'phantom':
        sol_spot = data[(data['app'] == 'Wallet') & (data['ticker'] == 'SOL')]
        if sol_spot['amount'].iloc[0] < 0.05:
            warnings.warn(f"Solana balance for fees are running low: {sol_spot['amount'].iloc[0]}")

    value_per_dapp = data.groupby(['app'])[['value', 'rewards value', 'total value']].sum()
    value_per_dapp = value_per_dapp.rename(columns={'value': 'TVL'})
    # Exclude total in case of rerun in debug
    value_per_dapp.loc['Total'] = value_per_dapp[value_per_dapp.index != 'Total'].sum()
    value_per_dapp = value_per_dapp.round(2)
    value_per_dapp.to_csv(f'results/{wallet}/value_per_dapp.csv')

    value_per_purpose = data.groupby(['purpose'])['total value'].sum()
    value_per_purpose['Total'] = value_per_purpose[value_per_purpose.index != 'Total'].sum()
    value_per_purpose = value_per_purpose[value_per_purpose != 0]
    value_per_purpose = value_per_purpose.round(2)
    value_per_purpose.to_csv(f'results/{wallet}/value_per_purpose.csv')

    return data