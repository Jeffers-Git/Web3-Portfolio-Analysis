"""
This is the main script which is used for the Web3 portfolio analysis
"""
import pandas as pd
import keplr
import metamask
import phantom
import sui
import yaml
import logging


def run():
    logging.basicConfig(level=logging.INFO, format='\033[92m%(asctime)s - %(levelname)s: %(message)s\033[0m')
    logging.info('Maxu farmu activated...')
    with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)

    wallets_file = 'data/Web3 wallets.xlsx'
    wallets = pd.read_excel(wallets_file, sheet_name=['phantom', 'keplr', 'metamask', 'sui', 'investment'])

    # run analysis for the three wallets
    logging.info("Running the analysis for all wallets...")
    phantom_data = phantom.run(data=wallets['phantom'])
    keplr_data = keplr.run(data=wallets['keplr'])
    metamask_data = metamask.run(data=wallets['metamask'])
    sui_data = sui.run(data=wallets['sui'])

    logging.info('Maxu farmu ran succesfully...')


if __name__ == "__main__":
    run()
