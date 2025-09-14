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
    wallets = pd.read_excel(wallets_file, sheet_name=['phantom', 'phantom2', 'solflare', 'solflare2',
                                                        'backpack', 'metamask', 'okx', 'seeker',
                                                        'phantom tablet 1', 'phantom tablet 2', 'solflare tablet 1', 'solflare tablet 2',
                                                        'slush laptop 1', 'slush laptop 2', 'backpack laptop 1', 'backpack laptop 2',
                                                        'backpack laptop 3', 'backpack laptop 4', 'backpack phone 1', 'backpack phone 2',
                                                        'slush phone 1', 'slush phone 2', 'slush phone 3', 'slush phone 4'])

    # calculate dollar value for all wallets
    logging.info("Running the analysis for Phantom wallet...")
    phantom_data = wallet_analysis.run(data=wallets['phantom'], config=config['phantom'], wallet='phantom')
    logging.info("Running the analysis for Phantom2 wallet...")
    phantom2_data = wallet_analysis.run(data=wallets['phantom2'], config=config['phantom2'], wallet='phantom2')
    logging.info("Running the analysis for Solflare wallet...")
    solfl_data = wallet_analysis.run(data=wallets['solflare'], config=config['solflare'], wallet='solflare')
    logging.info("Running the analysis for Solflare2 wallet...")
    solfl2_data = wallet_analysis.run(data=wallets['solflare2'], config=config['solflare2'], wallet='solflare2')

    time.sleep(10)

    logging.info("Running the analysis for Backpack wallet...")
    backpack_data = wallet_analysis.run(data=wallets['backpack'], config=config['backpack'], wallet='backpack')
    logging.info("Running the analysis for Metamask wallet...")
    metamask_data = wallet_analysis.run(data=wallets['metamask'], config=config['metamask'], wallet='metamask')
    logging.info("Running the analysis for OKX wallet...")
    okx_data = wallet_analysis.run(data=wallets['okx'], config=config['okx'], wallet='okx')
    logging.info("Running the analysis for Seeker wallet...")
    seeker_data = wallet_analysis.run(data=wallets['seeker'], config=config['seeker'], wallet='seeker')

    time.sleep(10)

    logging.info("Running the analysis for Phantom tablet 1 wallet...")
    phantomtablet1_data = wallet_analysis.run(data=wallets['phantom tablet 1'], config=config['phantom tablet 1'], wallet='phantom tablet 1')
    logging.info("Running the analysis for Phantom tablet 2 wallet...")
    phantomtablet2_data = wallet_analysis.run(data=wallets['phantom tablet 2'], config=config['phantom tablet 2'], wallet='phantom tablet 2')
    logging.info("Running the analysis for Solflare tablet 1 wallet...")
    solfltablet1_data = wallet_analysis.run(data=wallets['solflare tablet 1'], config=config['solflare tablet 1'], wallet='solflare tablet 1')
    logging.info("Running the analysis for Solflare tablet 2 wallet...")
    solfltablet2_data = wallet_analysis.run(data=wallets['solflare tablet 2'], config=config['solflare tablet 2'], wallet='solflare tablet 2')

    time.sleep(10)

    logging.info("Running the analysis for Slush laptop 1 wallet...")
    slushlaptop1_data = wallet_analysis.run(data=wallets['slush laptop 1'], config=config['slush laptop 1'], wallet='slush laptop 1')
    logging.info("Running the analysis for Slush laptop 2 wallet...")
    slushlaptop2_data = wallet_analysis.run(data=wallets['slush laptop 2'], config=config['slush laptop 2'], wallet='slush laptop 2')
    logging.info("Running the analysis for Backpack laptop 1 wallet...")
    backpacklaptop1_data = wallet_analysis.run(data=wallets['backpack laptop 1'], config=config['backpack laptop 1'], wallet='backpack laptop 1')
    logging.info("Running the analysis for Backpack laptop 2 wallet...")
    backpacklaptop2_data = wallet_analysis.run(data=wallets['backpack laptop 2'], config=config['backpack laptop 2'], wallet='backpack laptop 2')
    logging.info("Running the analysis for Backpack laptop 3 wallet...")
    backpacklaptop3_data = wallet_analysis.run(data=wallets['backpack laptop 3'], config=config['backpack laptop 3'], wallet='backpack laptop 3')
    logging.info("Running the analysis for Backpack laptop 4 wallet...")
    backpacklaptop4_data = wallet_analysis.run(data=wallets['backpack laptop 4'], config=config['backpack laptop 4'], wallet='backpack laptop 4')

    time.sleep(10)

    logging.info("Running the analysis for Backpack phone 1 wallet...")
    backpackphone1_data = wallet_analysis.run(data=wallets['backpack phone 1'], config=config['backpack phone 1'], wallet='backpack phone 1')
    logging.info("Running the analysis for Backpack phone 2 wallet...")
    backpackphone2_data = wallet_analysis.run(data=wallets['backpack phone 2'], config=config['backpack phone 2'], wallet='backpack phone 2')
    logging.info("Running the analysis for Slush phone 1 wallet...")
    slushphone1_data = wallet_analysis.run(data=wallets['slush phone 1'], config=config['slush phone 1'], wallet='slush phone 1')
    logging.info("Running the analysis for Slush phone 2 wallet...")
    slushphone2_data = wallet_analysis.run(data=wallets['slush phone 2'], config=config['slush phone 2'], wallet='slush phone 2')
    logging.info("Running the analysis for Slush phone 3 wallet...")
    slushphone3_data = wallet_analysis.run(data=wallets['slush phone 3'], config=config['slush phone 3'], wallet='slush phone 3')
    logging.info("Running the analysis for Slush phone 4 wallet...")
    slushphone4_data = wallet_analysis.run(data=wallets['slush phone 4'], config=config['slush phone 4'], wallet='slush phone 4')

    # create df with relevant metrics
    logging.info("Creating metrics tables and plots...")
    calculate_metrics(phantom_data=phantom_data, phantom2_data=phantom2_data, solfl_data=solfl_data, solfl2_data=solfl2_data,
                      backpack_data=backpack_data, metamask_data=metamask_data, okx_data=okx_data, seeker_data=seeker_data,
                      phantomtablet1_data=phantomtablet1_data, phantomtablet2_data=phantomtablet2_data, solfltablet1_data=solfltablet1_data, solfltablet2_data=solfltablet2_data,
                      slushlaptop1_data=slushlaptop1_data, slushlaptop2_data=slushlaptop2_data, backpacklaptop1_data=backpacklaptop1_data,backpacklaptop2_data=backpacklaptop2_data,
                      backpacklaptop3_data=backpacklaptop3_data, backpacklaptop4_data=backpacklaptop4_data, backpackphone1_data=backpackphone1_data, backpackphone2_data=backpackphone2_data,
                      slushphone1_data=slushphone1_data, slushphone2_data=slushphone2_data, slushphone3_data=slushphone3_data, slushphone4_data=slushphone4_data)

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
