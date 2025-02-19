"""
This is the main script which is used for the Web3 portfolio analysis
"""
import pandas as pd
import wallet_analysis
import yaml
import logging
from functions import calculate_metrics, plot_roi, calculate_metrics_over_time, create_plots_over_time
import time


def run():
    logging.basicConfig(level=logging.INFO, format='\033[92m%(asctime)s - %(levelname)s: %(message)s\033[0m')
    logging.info('Maxu farmu activated...')
    logging.info('Remember to close excel data file!!!')
    with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)

    # read in wallet data
    wallets_file = 'data/Web3 wallets.xlsx'
    wallets = pd.read_excel(wallets_file, sheet_name=['phantom', 'metamask', 'trust', 'okx', 'solflare',
                                                      'phantom2', 'solflare2', 'backpack'])

    # calculate dollar value for all wallets
    logging.info("Running the analysis for Phantom wallet...")
    phantom_data = wallet_analysis.run(data=wallets['phantom'], config=config['phantom'], wallet='phantom')
    logging.info("Running the analysis for Metamask wallet...")
    metamask_data = wallet_analysis.run(data=wallets['metamask'], config=config['metamask'], wallet='metamask')
    logging.info("Running the analysis for Trust wallet...")
    trust_data = wallet_analysis.run(data=wallets['trust'], config=config['trust'], wallet='trust')
    logging.info("Running the analysis for OKX wallet...")
    okx_data = wallet_analysis.run(data=wallets['okx'], config=config['okx'], wallet='okx')

    time.sleep(10)

    logging.info("Running the analysis for Solflare wallet...")
    solfl_data = wallet_analysis.run(data=wallets['solflare'], config=config['solflare'], wallet='solflare')
    logging.info("Running the analysis for Phantom2 wallet...")
    phantom2_data = wallet_analysis.run(data=wallets['phantom2'], config=config['phantom2'], wallet='phantom2')
    logging.info("Running the analysis for Solflare2 wallet...")
    solfl2_data = wallet_analysis.run(data=wallets['solflare2'], config=config['solflare2'], wallet='solflare2')
    logging.info("Running the analysis for Backpack wallet...")
    backpack_data = wallet_analysis.run(data=wallets['backpack'], config=config['backpack'], wallet='backpack')

    # create df with relevant metrics
    logging.info("Creating metrics tables and plots...")
    calculate_metrics(phantom_data=phantom_data, metamask_data=metamask_data, trust_data=trust_data,
                      okx_data=okx_data, solfl_data=solfl_data, phantom2_data=phantom2_data, solfl2_data=solfl2_data,
                      backpack_data=backpack_data)

    # create bar plot with ROI
    # plot_roi(metrics)
    #
    # for wallet in config['wallets']:
    #     calculate_metrics_over_time(metrics, wallet=wallet)
    #
    # create_plots_over_time(config)

    logging.info('Maxu farmu ran succesfully...')


if __name__ == "__main__":
    run()
