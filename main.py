"""
This is the main script which is used for the Web3 portfolio analysis
"""
import pandas as pd
import keplr
import metamask
import phantom


def run():
    wallets_file = 'data/Web3 wallets.xlsx'
    wallets = pd.read_excel(wallets_file, sheet_name=['phantom', 'keplr', 'metamask', 'investment'])

    # run analysis for the three wallets
    phantom.run(data=wallets['phantom'])
    keplr.run(data=wallets['keplr'])
    metamask.run(data=wallets['metamask'])


if __name__ == "__main__":
    run()
