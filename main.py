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

    # run analysis for all wallets
    logging.info("Running the analysis for all wallets...")
    phantom_data = phantom.run(data=wallets['phantom'])
    keplr_data = keplr.run(data=wallets['keplr'])
    metamask_data = metamask.run(data=wallets['metamask'])
    sui_data = sui.run(data=wallets['sui'])

    # create df with relevant metrics
    investments = wallets['investment']
    current_value = {'Metric': 'Current value',
                     'Phantom': phantom_data['value'].sum(),
                     'Keplr': keplr_data['value'].sum(),
                     'Metamask': metamask_data['value'].sum(),
                     'Sui': sui_data['value'].sum()}
    current_value['Total'] = current_value['Phantom'] + current_value['Keplr'] + \
                             current_value['Metamask'] + current_value['Sui']
    roi_absolute = {'Metric': 'Absolute ROI',
                    'Phantom': current_value['Phantom'] - investments['Phantom'][0],
                    'Keplr': current_value['Keplr'] - investments['Keplr'][0],
                    'Metamask': current_value['Metamask'] - investments['Metamask'][0],
                    'Sui': current_value['Sui'] - investments['Sui'][0],
                    'Total': current_value['Total'] - investments['Total'][0]}
    roi_relative = {'Metric': 'ROI (%)',
                    'Phantom': roi_absolute['Phantom']/investments['Phantom'][0]*100,
                    'Keplr': roi_absolute['Keplr']/investments['Keplr'][0]*100,
                    'Metamask': roi_absolute['Metamask']/investments['Metamask'][0]*100,
                    'Sui': roi_absolute['Sui']/investments['Sui'][0]*100,
                    'Total': roi_absolute['Total']/investments['Total'][0]*100}
    metrics_to_add = [current_value, roi_absolute, roi_relative]

    metrics = wallets['investment'].round(2)
    for metric in metrics_to_add:
        metrics = metrics.append(metric, ignore_index=True)
    metrics = metrics.set_index('Metric')
    metrics = metrics.round(2)
    metrics.to_csv('results/metrics_table.csv')

    logging.info('Maxu farmu ran succesfully...')


if __name__ == "__main__":
    run()
