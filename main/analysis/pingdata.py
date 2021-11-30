from os import path

import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np

DATADIR = path.dirname(path.dirname(path.realpath(__file__)))
PING_DATA = path.join(DATADIR, 'data', 'ping_data.xlsx')
pdata = pd.read_excel(PING_DATA)
pdata = pdata[~pdata['Country'].isin(['IR', 'US'])]  # clean data


def clean_data(df):
    return df[~df['Country'].isin(['IR', 'US'])]


def plot_ping_by_country(saveto=None):
    plt.cla()
    savepath = saveto or 'ping-by-country.png'
    pdmean = pdata.groupby('Country')['Ping'].mean()
    pdm_mean = pdata.groupby('Country')['Ping'].mean().mean()
    plot = pdmean.plot.bar(figsize=(22, 7))
    plt.axhline(y=pdm_mean, color='r')
    plt.ylabel('Ping')
    plt.text(1, 115, f"Average: {pdm_mean:.4f}", fontsize=18, color='red')
    plt.savefig(savepath)
    return savepath


def plot_ping_by_provider_country(saveto=None):
    plt.close()
    aws = pdata[pdata['Cloudp'] == 'AWS'].groupby('Country')['Ping'].mean()
    gcp = pdata[pdata['Cloudp'] == 'Google_Cloud'].groupby('Country')['Ping'].mean()
    azure = pdata[pdata['Cloudp'] == 'Azure'].groupby('Country')['Ping'].mean()
    fig = plt.figure("Ping per Cloud Provider")

    width = 0.23
    plt.figure(figsize=(22, 7))
    aws_bar = plt.bar(np.arange(aws.index.size) - width, aws, width=width, color='g', align='center', alpha=0.75)
    gcp_bar = plt.bar(gcp.index, gcp, width=width, color='b', align='center', alpha=0.75)
    azure_bar = plt.bar(np.arange(azure.index.size) + width, azure, width=width, color='r', align='center', alpha=0.75)
    plt.legend([aws_bar, gcp_bar, azure_bar], ['AWS', 'GCP', 'Azure'])

    savepath = saveto or 'ping-by-provider-per-country.png'
    plt.savefig(savepath)


def plot_ping_per_provider(saveto=None):
    plt.cla()
    plot = pdata.groupby('Cloudp')['Ping'].mean().plot.bar()
    plt.xticks(rotation=45)
    savepath = saveto or 'ping-by-provider.png'
    plt.savefig(savepath)
    plt.close()


if __name__ == '__main__':
    savedto = plot_ping_by_country()
    print("Ping Data saved to {}".format(savedto))
    savedto = plot_ping_by_provider_country()
    print("Ping Data by provider per country saved to {}".format(savedto))
    savedto = plot_ping_per_provider()
    print("Ping Data saved to {}".format(savedto))