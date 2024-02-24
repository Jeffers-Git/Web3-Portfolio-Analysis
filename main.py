"""
This is the main script which is used for the Web3 portfolio analysis
"""
import pandas as pd
import keplr
import metamask
import phantom
import sui
import yaml


def run():
    with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)

    wallets_file = 'data/Web3 wallets.xlsx'
    wallets = pd.read_excel(wallets_file, sheet_name=['phantom', 'keplr', 'metamask', 'investment'])

    # run analysis for the three wallets
    phantom_data = phantom.run(data=wallets['phantom'])
    keplr_data = keplr.run(data=wallets['keplr'])
    metamask_data = metamask.run(data=wallets['metamask'])
    sui_data = sui.run(data=wallets['sui'])


if __name__ == "__main__":
    run()
