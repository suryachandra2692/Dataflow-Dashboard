from os import path

import pandas as pd
from scipy import stats

import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt

DATADIR = path.dirname(path.dirname(path.realpath(__file__)))
INDEPENDENT_DATA = path.join(DATADIR, 'data', 'Independent.xlsx')
DATA_FLOW_DATA = path.join(DATADIR, 'data', 'Data_Flow_by_Country.xlsx')
COUNTRY_CODES = path.join(DATADIR, 'data', 'CountryCodes.html')
indp = pd.read_excel(INDEPENDENT_DATA)
exd = pd.read_excel(DATA_FLOW_DATA)
cc = pd.read_html(COUNTRY_CODES)[0]  # country codes


def get_linregress(X, y):
    slope, intercept, r, p, std_err = stats.linregress(X, y)
    return {
        'slope': slope, 'intercept': intercept,
        'correlation_coef': r, 'std_err': std_err,
        'name': X.name
    }


def get_datavolumen_df():
    indpm = indp.merge(cc)
    exd_mean = exd.iloc[:, 2:].mean()  # Calculate mean of data flow for each country
    exd_mean = pd.DataFrame(exd_mean)
    exd_mean = exd_mean.reset_index()
    exd_mean = exd_mean.rename(columns={'index': 'Country', 0: 'Data Volume'})
    fin = indpm.merge(exd_mean, how='inner', left_on='Alpha-2 code', right_on='Country')  # DB style join
    return fin


def get_relations():
    """
    Return list of coefficient of correlation for each independent variable
    """
    fin = get_datavolumen_df()
    datav = fin['Data Volume']
    relations = []
    for i in indp.columns[1:]:
        r = get_linregress(fin[i], datav)
        relations.append((r['name'], r['correlation_coef']))
    return pd.DataFrame(relations)


def get_influencing_vars():
    """" Return filtered influencing independent variables of Data Flow"""
    df = get_relations()
    filtered = df[df[1] > 0.5].sort_values(by=1, ascending=False)
    return filtered


def plot_correlations(saveto=None):
    df = get_relations()
    df = df.set_index([0])
    df.plot.bar(figsize=(22, 10))
    plt.xticks(rotation=45)
    plt.xlabel("Independent Variable")
    plt.ylabel("Coefficient of Correlation")
    savepath = saveto or 'dataflow-influencing-vars.png'
    return plt.savefig(savepath), savepath


def plot_regression(x, y):
    plt.close()
    slope, intercept, r, p, std_err = stats.linregress(x, y)

    def reg_line(x):
        return slope * x + intercept

    model = list(map(reg_line, x))

    plt.scatter(x, y)
    plt.plot(x, model)
    if hasattr(x, 'name'):
        plt.xlabel(x.name)
    if hasattr(y, 'name'):
        plt.ylabel(y.name)


class RegressionPlot:

    def __init__(self):
        self.dataset = get_datavolumen_df()

    def plot_inter_trade(self, savepath):
        plt.cla()
        plot_regression(self.dataset['International Trade'], self.dataset['Data Volume'])
        plt.savefig(savepath)

    def plot_labour_force(self, savepath):
        plt.cla()
        plot_regression(self.dataset['Labour Force'], self.dataset['Data Volume'])
        plt.savefig(savepath)

    def plot_electricity_consumption(self, savepath):
        plt.cla()
        plot_regression(self.dataset['Electricity Consumption'], self.dataset['Data Volume'])
        plt.savefig(savepath)

    def plot_numcars(self, savepath):
        plt.cla()
        plot_regression(self.dataset['Number of Cars'], self.dataset['Data Volume'])
        plt.savefig(savepath)


if __name__ == '__main__':
    print(get_relations())
    print("=======================")
    print("Influencing Independent Variables on Data Flow")
    print(get_influencing_vars())
    _, savepath = plot_correlations()
    print("Plot saved to {}".format(savepath))
