import pandas as pd
from pandas import DatetimeIndex as dtIndex
import numpy as np
import sklearn.preprocessing as skp
import statsmodels.api as sms
from statsmodels.tsa.seasonal import seasonal_decompose
from itertools import product, combinations
import scipy.stats as ss
from copulas.multivariate import GaussianMultivariate
from numpy.linalg import cholesky
from datetime import datetime


def big_macro_function(st1, st2, data_macro, repd_period):
    # st1 = pd.read_excel('dcorp1.xlsx', engine='openpyxl')
    # st1.drop(columns=['Unnamed: 0'], inplace=True)

    # st2 = pd.read_excel('dcorp2.xlsx', engine='openpyxl')
    # st2.drop(columns=['Unnamed: 0'], inplace=True)

    print(st1)
    print(st2)

    macro = pd.read_excel(data_macro, sheet_name="2010", engine='openpyxl')

    print(macro)

    mcols = ['neer', 'nneer', 'reer', 'nreer', 'usdazn', 'gdp', 'ngdp', 'rgdp', 'rngdp',
             'cap_invest', 'nominc', 'cpi_cumul', 'budrev', 'budexp', 'brent_oil_price']

    msigns = [False, False, False, False, True, False, False, False, False,
              False, False, True, False, False, False]

    mgroups = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 4, 4, 5]

    mdf = pd.DataFrame(list(map(list, zip(*[msigns, mgroups]))), index=mcols, columns=['msigns', 'mgroups'])

    def period_detector(period):
        return 12 if period == 'yearly' else 1

    def prepare_data(data):
        data['act_end'] = data['DATE_OPER'].apply(lambda x: x - pd.DateOffset(months=period_detector(repd_period)))
        data['month'] = dtIndex(data.DATE_OPER).month
        data['time_index'] = dtIndex(data.DATE_OPER).year.astype('str') + dtIndex(data.DATE_OPER).month.astype('str')
        data['time_index2'] = dtIndex(data.act_end).year.astype('str') + dtIndex(data.act_end).month.astype('str')
        data['RATE'] = data['RATE'].replace(0, 0.0000001)
        # print(dt)-
        data['rate2'] = np.log(data.RATE) - np.log(1 - data.RATE)
        data = data[
            ((data.rate2 != np.nan) & (abs(data.rate2) != np.inf) & (data.ORIG_COUNT > 4) & (data.ORIG_AMOUNT > 0))]
        # data = data.loc[data['rate2'] != np.nan, :]
        print(data)
        print('burdadi')
        print(data['rate2'])
        macro['ym'] = macro['year'].astype('str') + macro['month'].astype('str')
        data = data.merge(macro, how='left', left_on='time_index', right_on='ym').merge(macro, how='left',
                                                                                        left_on='time_index2',
                                                                                        right_on='ym')

        for i in mcols:
            data[i] = np.log(data[i + '_y']) - np.log(data[i + '_x'])

        # standardizing macro variables
        scaler = skp.StandardScaler()
        data[mcols] = scaler.fit_transform(data[mcols])

        # getting some dummies
        dummy_months = list(pd.get_dummies(data.month, drop_first=True, prefix='M', prefix_sep=""))
        data[dummy_months] = pd.get_dummies(data.month, drop_first=True, prefix='M', prefix_sep="")

        return data, scaler

    st1, scaler1 = prepare_data(st1)
    st2, scaler2 = prepare_data(st2)

    st1 = st1[((st1.rate2 != np.nan) & (abs(st1.rate2) != np.inf) & (st1.ORIG_COUNT > 4) & (st1.ORIG_AMOUNT > 0))]
    st2 = st2[((st2.rate2 != np.nan) & (abs(st2.rate2) != np.inf) & (st2.ORIG_COUNT > 4) & (st2.ORIG_AMOUNT > 0))]

    scale = pd.DataFrame(index=mcols)
    scale['ave1'] = scaler1.mean_
    scale['std1'] = scaler1.scale_
    scale['ave2'] = scaler2.mean_
    scale['std2'] = scaler2.scale_

    st1.dropna(inplace=True)
    st2.dropna(inplace=True)

    # temp1 = macro[(macro.year > 2013) & (macro.year < 2019)]['gdp'] / 45 + \
    #         macro[(macro.year > 2013) & (macro.year < 2019)]['budrev'] / 45 + \
    #         macro[(macro.year > 2013) & (macro.year < 2019)]['nreer']
    # temp2 = macro[(macro.year > 2013) & (macro.year < 2019)]['nreer'] / 45 + \
    #         macro[(macro.year > 2013) & (macro.year < 2019)]['cap_invest'] / 45 + \
    #         macro[(macro.year > 2013) & (macro.year < 2019)]['nominc']
    #
    # temp1 = temp1 + np.random.normal(0, 10, 60)
    # temp2 = temp2 + np.random.normal(0, 10, 60)
    #
    # temp1 = (temp1 - temp1.min()) / (temp1.max() - temp1.min())
    # temp2 = (temp2 - temp2.min()) / (temp2.max() - temp2.min())

    # st1['rate2'] = temp1
    # st2['rate2'] = temp2

    # st1['rate2']=np.log(st1['RATE']) - np.log(1-st1['RATE'])

    # st1.rate2 = temp1.reset_index().drop('index', axis=1)
    # st2.rate2 = temp2.reset_index().drop('index', axis=1)

    def get_bic_for_dummies(data, mlist, mdf, last_mn, curr_mn, bicc, mnlist, cycle, x1):
        # print('!------------------------------step bashladi')

        if not mdf.empty:

            # print('last --> ', last_mn, 'curr --> ', curr_mn)
            flag = False

            if curr_mn != 'base':
                mlist = list(mdf.loc[mdf.mgroups != mdf.loc[last_mn, "mgroups"], :].index)
                mdf = mdf.drop(list(mdf.loc[mdf.mgroups == mdf.loc[last_mn, "mgroups"], :].index), axis=0)
                curr_mn = last_mn[:]
            else:
                base_model = sms.OLS(data['rate2'], np.ones(len(data['rate2']))).fit()
                bicc['base'] = base_model.bic

            #         print('mlist', mlist)
            # print('curr', curr_mn)
            print(data.isnull().sum())
            for i in mlist:

                if last_mn == '':
                    reg = sms.OLS(data.rate2, sms.add_constant(data[[i, i + '_s', 'st_dummy']])).fit()
                else:
                    reg = sms.OLS(data.rate2,
                                  x1.merge(data[[i, i + '_s', 'st_dummy']], left_index=True, right_index=True)).fit()

                # if sum((reg.params[reg.params.index[reg.params.index!='const']]>0) ==
                # mdf.loc[reg.params.index[reg.params.index!='const'], 'msigns']) == len(
                # reg.params.index[reg.params.index!='const']):

                #             print(bicc)
                if reg.bic < bicc[min(bicc, key=bicc.get)]:
                    # print('sert odeyir', i)
                    flag = True
                    bicc['_'.join(mnlist) + "_" + i] = reg.bic
                    curr_mn = i

                    globals()['reg_c%s_%s' % (cycle, i)] = reg

            mnlist.append(curr_mn)
            # print('curr', curr_mn)

            if flag:
                if last_mn == '':
                    x1 = sms.add_constant(data[[curr_mn, curr_mn + '_s', 'st_dummy']])
                else:
                    x1 = x1.merge(data[[curr_mn, curr_mn + '_s']], left_index=True, right_index=True)

            if last_mn != curr_mn:
                return get_bic_for_dummies(data, mlist, mdf, curr_mn, 'test', bicc, mnlist, cycle, x1)

        X = sms.add_constant(x1)
        lr = sms.OLS(data['rate2'], X).fit()

        return lr, x1, mnlist[:-1]

    def run_rec_func(st1, st2, mlist, mdf, last_mn, curr_mn):
        st1['st_dummy'] = 0
        st2['st_dummy'] = 1

        st = pd.concat([st1, st2])

        st_merged = st[['neer', 'nneer', 'reer', 'nreer', 'usdazn', 'gdp', 'ngdp', 'rgdp', 'rngdp',
                        'cap_invest', 'nominc', 'cpi_cumul', 'budrev', 'budexp', 'brent_oil_price', 'st_dummy',
                        'DATE_OPER',
                        'rate2']]
        table = pd.Categorical(st_merged['st_dummy'])
        st_merged.set_index(['st_dummy', 'DATE_OPER'], inplace=True)
        st_merged['st_dummy'] = table

        for macro in mcols:
            st_merged[macro + '_s'] = st_merged[macro] * st_merged['st_dummy'].astype('int')

        bicc = {}
        mdf = pd.DataFrame(list(map(list, zip(*[msigns, mgroups]))), index=mcols, columns=['msigns', 'mgroups'])
        x1 = pd.DataFrame()
        mnlist = []
        cycle = 0
        lr, data, selected_cols = get_bic_for_dummies(st_merged, mcols, mdf, last_mn, curr_mn, bicc, mnlist, cycle, x1)

        return lr, data, selected_cols

    lr, data_reg, selected_cols = run_rec_func(st1, st2, mcols, mdf, '', 'base')

    data = pd.read_excel(data_macro, sheet_name='2010', engine='openpyxl')
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
                1 if data.iloc[i, col] <= l[0][col] else 2 if data.iloc[i, col] <= l[1][col] else 3 if data.iloc[
                                                                                                           i, col] <=
                                                                                                       l[2][col] else 4
                for
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
                counts[
                    q_dict[comb[0]][i] - 1, q_dict[comb[1]][i] - 1, q_dict[comb[2]][i] - 1, q_dict[comb[3]][i] - 1] += 1
            else:
                counts[q_dict[comb[0]][i] - 1, q_dict[comb[1]][i] - 1, q_dict[comb[2]][i] - 1, q_dict[comb[3]][i] - 1,
                       q_dict[comb[4]][i] - 1] += 1

        # finding probabilities
        return counts / N

    def main_func_adj(reg_obj, data, selected_cols, start_date='2010-01-01', end_date='2021-06-30',
                      method='covariance', seasonal_adjustment=True, lag=1, cycle='monthly',
                      monte_carlo_n_sample=100000):
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
                                   np.mean(quantiles.iloc[500:750, :]), np.mean(quantiles.iloc[750:, :]))).reshape(-1,
                                                                                                                   quantiles.shape[1])
        print(averages)
        print('*'*30)
        print(quantiles.columns)
        q_test = pd.DataFrame(averages, columns=quantiles.columns)
        q_test['key'] = 1
        all_scenarios = pd.merge(q_test.iloc[:, 0], q_test.iloc[:, 1], on=q_test['key']).drop('key_0', axis=1)
        all_scenarios['probs'] = scenario_probs

        preds_st1 = reg_obj.params[0] + reg_obj.params[selected_cols].values.reshape(1, -1) @ all_scenarios[
            selected_cols].T

        st2_scenarios = np.concatenate((np.ones((16, 1)), np.repeat(all_scenarios.iloc[:, 0].values, 2).reshape(-1, 2),
                                        np.ones((16, 1)), np.repeat(all_scenarios.iloc[:, 1].values, 2).reshape(-1, 2)),
                                       axis=1)
        preds_st2 = reg_obj.params.values.reshape(1, -1) @ st2_scenarios.T

        overall_pd_st1 = (preds_st1 * np.array(scenario_probs)).sum(axis=1)[0]
        overall_pd_st2 = (preds_st2 * scenario_probs).sum(axis=1)[0]

        return overall_pd_st1, overall_pd_st2, preds_st1.T.values, preds_st2.T

    overall_pd_st1, overall_pd_st2, preds_st1, preds_st2 = main_func_adj(lr, data, selected_cols,
                                                                         monte_carlo_n_sample=1000)

    # arr1 = np.random.randint(1, 10, 16).reshape(-1, 1)
    # arr2 = np.random.randint(1, 10, 16).reshape(-1, 1)
    # np.concatenate((preds_st1, preds_st2), axis=1)
    overall_pd = pd.DataFrame(np.array([overall_pd_st1, overall_pd_st2]))
    overall_pd = overall_pd.T
    overall_pd.index = ['total_pd']
    final_macro_df = pd.concat((pd.DataFrame(np.concatenate((preds_st1, preds_st2), axis=1)), overall_pd), axis=0)

    return final_macro_df
