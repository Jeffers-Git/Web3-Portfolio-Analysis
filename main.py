"""
This is the main script which is used for the Web3 portfolio analysis
"""
import pandas as pd


def run():
    wallets_file = 'Data/Web3 wallets.xlsx'
    wallets = pd.read_excel(wallets_file, sheet_name=['phantom', 'keplr', 'metamask', 'investment'])


if __name__ == "__main__":
    run()
