import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from itertools import product, combinations
import scipy.stats as ss
from copulas.multivariate import GaussianMultivariate
from numpy.linalg import cholesky
from datetime import datetime


data = pd.read_excel('data.xlsx', sheet_name='2010', engine='openpyxl')
data.index = data.tarix


def log_diff(data, lag=1):
    '''
     Returns lag-months logarithmic differences
    '''
    diff = pd.DataFrame(index=data.index)

    for col in data.columns:
        diff[col] = np.log(data[col]) - np.log(data[col].shift(lag))  # lag-months change with log
    return diff


def remove_seasonality(data, cycle='monthly'):
    """
    cycle - can take one of the following: 'monthly', 'quarterly'
    """

    data_adj = pd.DataFrame(index=data.index)
    data.fillna(0, inplace=True)

    if cycle == 'monthly':
        for i in range(data.shape[1]):
            s = seasonal_decompose(data.iloc[1:, i], model='additive')
            data_adj[data.columns[i]] = data.iloc[1:, i] - s.seasonal  # subtracting seasonal component
    elif cycle == 'quarterly':
        for i in range(data.shape[1]):
            s = seasonal_decompose(data.iloc[:, i], model='additive')
            temp = np.array(s.seasonal).reshape(-1, 3).sum(axis=1) / 3
            temp = np.repeat(temp, 3)
            data_adj[data.columns[i]] = data.iloc[:, i] - temp  # subtracting seasonal component
    return data_adj


# def find_dist(data, macro_cols):
#     dists = ['cauchy', 'norm', 't', 'logistic', 'gennorm', 'genlogistic']
#
#     # combination of dists and macro_cols elements
#     combs = tuple(product(macro_cols, dists))
#
#     params_fitted = {}
#
#     # Kolmogorov–Smirnov test(used to find right distribution for each macroeconmic variable.
#     ks_test = {}
#
#     for macro, dist in combs:
#         mod = getattr(ss, dist)
#         fitted = mod.fit(diff_adj[macro].dropna())  # fit
#         params_fitted[dist + ' ' + macro] = fitted
#
#         prob = ss.kstest(diff_adj[macro].dropna(), dist, fitted).pvalue  # pvalue of kstest
#         ks_test[macro + ' ' + dist] = prob
#
#     return params_fitted, ks_test


def apply_t_dist(data, macro_cols):
    '''
    Returns a dictionary contains df, mean, standard deviation of variables.
    '''
    params_final = {}

    quantiles = pd.DataFrame(index=np.arange(0.05, 100, 0.1))

    for macro in macro_cols:
        mod = getattr(ss, 't')
        fitted = mod.fit(data[macro].dropna())
        quantiles[macro] = ss.t.ppf(np.arange(0.0005, 1, 0.001), df=fitted[0], loc=fitted[1], scale=fitted[2])
        params_final[macro + '_t'] = fitted

    # quantiles.to_excel('macro_quantiles.xlsx')
    # quantiles.to_pickle('macro_quantiles.pkl')

    return params_final, quantiles


def gen_data_using_copula(data, macro_cols, monte_carlo_n_sample):
    copula = GaussianMultivariate()
    copula.fit(data[macro_cols].iloc[1:, :])

    df_random = copula.sample(monte_carlo_n_sample)

    return df_random


def monte_carlo(data, macro_cols, params_final, monte_carlo_n_sample):
    '''
    Creating random series for each variable using their parameter coming from t-distribution.
    '''
    new_vars = []

    for key in list([col + '_t' for col in macro_cols]):
        # Generating random data from t-distribution using df, mean, std of macro variables
        rv = ss.t.rvs(df=params_final[key][0], loc=params_final[key][1], scale=params_final[key][2],
                      size=monte_carlo_n_sample)
        new_vars.append(rv)

    df_random = pd.DataFrame(np.array(new_vars).T)
    df_random.columns = list([col + '_t' for col in macro_cols])

    return df_random


def cholesky_decomposition(data, macro_cols, params_final, monte_carlo_n_sample, method):
    '''
    Imposing correlation of macroeconomic data on random series coming from Monte Carlo Simulations.
    '''
    df_random = monte_carlo(data, macro_cols, params_final, monte_carlo_n_sample)

    # Getting lower triangular matrix using Cholesky decomposition of Covariance matrix
    if method == 'covariance':
        L = cholesky(data[macro_cols].cov())
    elif method == 'correlation':
        L = cholesky(data[macro_cols].corr())
    df_cholesky = df_random @ L
    df_cholesky.columns = macro_cols

    return df_cholesky


def make_joint_dist(data, comb, n_columns=2):
    '''
    Returns joint probability tables of given combinations.
    '''
    N, D = data.shape
    columns = data.columns

    q_dict = {}
    arr = []

    # Initializing quantiles
    l = np.full(shape=(3, D), fill_value=-999.9)

    num_quantiles = 2

    # choosing number of parts data will be divided into, based on number of columns in combinations
    if n_columns == 2:
        l[0], l[1], l[2] = data.quantile(0.25), data.quantile(0.5), data.quantile(0.75)
        num_quantiles = 4
    elif n_columns == 3:
        l[0], l[1], l[2] = data.quantile(1 / 3), data.quantile(2 / 3), data.quantile(1)
        num_quantiles = 3
    else:
        l[0], l[1] = data.quantile(0.5), data.quantile(1)

    # determining which part the values belong to
    for col in range(D):
        quantiles = [
            1 if data.iloc[i, col] <= l[0][col] else 2 if data.iloc[i, col] <= l[1][col] else 3 if data.iloc[i, col] <=
                                                                                                   l[2][col] else 4 for
            i in range(N)]
        q_dict[columns[col]] = quantiles

    # Initializing joint probability tables
    counts = np.zeros([num_quantiles] * n_columns)

    # counting number of values in each probability table
    for i in range(N):
        if n_columns == 2:
            counts[q_dict[comb[0]][i] - 1, q_dict[comb[1]][i] - 1] += 1
        elif n_columns == 3:
            counts[q_dict[comb[0]][i] - 1, q_dict[comb[1]][i] - 1, q_dict[comb[2]][i] - 1] += 1
        elif n_columns == 4:
            counts[q_dict[comb[0]][i] - 1, q_dict[comb[1]][i] - 1, q_dict[comb[2]][i] - 1, q_dict[comb[3]][i] - 1] += 1
        else:
            counts[q_dict[comb[0]][i] - 1, q_dict[comb[1]][i] - 1, q_dict[comb[2]][i] - 1, q_dict[comb[3]][i] - 1,
                   q_dict[comb[4]][i] - 1] += 1

    # finding probabilities
    return counts / N


def main_func_adj(reg_obj, data, selected_cols, start_date='2010-01-01', end_date='2020-01-01',
                  method='covariance', seasonal_adjustment=True, lag=1, cycle='monthly', monte_carlo_n_sample=100000):
    n_columns = len(selected_cols)

    data = data[data['tarix'] >= datetime.strptime(start_date, '%Y-%m-%d')]
    data = data[data['tarix'] <= datetime.strptime(end_date, '%Y-%m-%d')]

    diff = log_diff(data[selected_cols])
    diff.fillna(0, inplace=True)
    if seasonal_adjustment:
        diff = remove_seasonality(diff, cycle)

    params_final, quantiles = apply_t_dist(diff, selected_cols)

    if method == 'copula':
        df_random = gen_data_using_copula(diff, selected_cols, monte_carlo_n_sample)
    elif method == 'covariance' or method == 'correlation':
        df_random = cholesky_decomposition(diff, selected_cols, params_final, monte_carlo_n_sample, method)

    array = make_joint_dist(df_random, selected_cols, n_columns)
    probs = np.array(array)

    scenario_probs = []
    for row in probs:
        for item in row:
            scenario_probs.append(item)

    averages = np.concatenate((np.mean(quantiles.iloc[:250, :]), np.mean(quantiles.iloc[250:500, :]),
                               np.mean(quantiles.iloc[500:750, :]), np.mean(quantiles.iloc[750:, :]))).reshape(-1, 2)
    q_test = pd.DataFrame(averages, columns=quantiles.columns)
    q_test['key'] = 1
    all_scenarios = pd.merge(q_test.iloc[:, 0], q_test.iloc[:, 1], on=q_test['key']).drop('key_0', axis=1)
    all_scenarios['probs'] = scenario_probs

    preds_st1 = reg_obj.params[0] + reg_obj.params[selected_cols].values.reshape(1, -1) @ all_scenarios[selected_cols].T

    st2_scenarios = np.concatenate((np.ones((16, 1)), np.repeat(all_scenarios.iloc[:, 0].values, 2).reshape(-1, 2),
                                    np.ones((16, 1)), np.repeat(all_scenarios.iloc[:, 1].values, 2).reshape(-1, 2)),
                                   axis=1)
    preds_st2 = reg_obj.params.values.reshape(1, -1) @ st2_scenarios.T

    overall_pd_st1 = (preds_st1 * np.array(scenario_probs)).sum(axis=1)[0]
    overall_pd_st2 = (preds_st2 * scenario_probs).sum(axis=1)[0]

    return overall_pd_st1, overall_pd_st2, preds_st1.T.values, preds_st2.T



# from . import macroandadj_part1


# def main_func():
#     lr, data_reg, selected_cols = macroandadj_part1.run_rec_func(macroandadj_part1.st1, macroandadj_part1.st2,
#                                                                  macroandadj_part1.mcols, macroandadj_part1.mdf, '',
#                                                                  'base')
#     overall_pd_st1, overall_pd_st2, preds_st1, preds_st2 = main_func_adj(lr, data, selected_cols,
#                                                                          monte_carlo_n_sample=1000)
#     return overall_pd_st1, overall_pd_st2, preds_st1, preds_st2

