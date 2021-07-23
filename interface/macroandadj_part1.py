import pandas as pd
from pandas import DatetimeIndex as dtIndex
import numpy as np
import sklearn.preprocessing as skp
import statsmodels.api as sms


st1 = pd.read_excel('dcorp1.xlsx', engine='openpyxl')
st1.drop(columns = ['Unnamed: 0'], inplace=True)

st2 = pd.read_excel('dcorp2.xlsx', engine='openpyxl')
st2.drop(columns = ['Unnamed: 0'], inplace=True)

macro = pd.read_excel("data.xlsx", sheet_name="2010", engine='openpyxl')

mcols = ['neer', 'nneer', 'reer', 'nreer', 'usdazn', 'gdp', 'ngdp', 'rgdp', 'rngdp',
       'cap_invest', 'nominc', 'cpi_cumul', 'budrev', 'budexp', 'brent_oil_price']

msigns = [False, False, False, False, True, False, False, False, False,
       False, False, True, False, False, False]

mgroups = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 4, 4, 5]

mdf = pd.DataFrame(list(map(list, zip(*[msigns,mgroups]))), index = mcols, columns = ['msigns', 'mgroups'])


def prepare_data(data):
    data['act_end'] = data['DATE_OPER'].apply(lambda x: x + pd.DateOffset(years=1))
    data['month'] = dtIndex(data.DATE_OPER).month
    data['time_index'] = dtIndex(data.DATE_OPER).year.astype('str') + dtIndex(data.DATE_OPER).month.astype('str')
    data['time_index2'] = dtIndex(data.act_end).year.astype('str') + dtIndex(data.act_end).month.astype('str')
    data['rate2'] = np.log(data.RATE) - np.log(1 - data.RATE)

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

st1 = st1[((st1.rate2!=np.nan)&(abs(st1.rate2)!=np.inf)&(st1.ORIG_COUNT>4)&(st1.ORIG_AMOUNT>0))]
st2 = st2[((st2.rate2!=np.nan)&(abs(st2.rate2)!=np.inf)&(st2.ORIG_COUNT>4)&(st2.ORIG_AMOUNT>0))]

scale = pd.DataFrame(index=mcols)
scale['ave1'] = scaler1.mean_
scale['std1'] = scaler1.scale_
scale['ave2'] = scaler2.mean_
scale['std2'] = scaler2.scale_

st1.dropna(inplace=True)
st2.dropna(inplace=True)

temp1 = macro[(macro.year>2013) & (macro.year<2019)]['gdp']/45 + macro[(macro.year>2013) & (macro.year<2019)]['budrev']/45 + macro[(macro.year>2013) & (macro.year<2019)]['nreer']
temp2 = macro[(macro.year>2013) & (macro.year<2019)]['nreer']/45 + macro[(macro.year>2013) & (macro.year<2019)]['cap_invest']/45 + macro[(macro.year>2013) & (macro.year<2019)]['nominc']

temp1 = temp1 + np.random.normal(0, 10, 60)
temp2 = temp2 + np.random.normal(0, 10, 60)

temp1 = (temp1-temp1.min())/(temp1.max()-temp1.min())
temp2 = (temp2-temp2.min())/(temp2.max()-temp2.min())

st1['rate2']=temp1
st2['rate2']=temp2

st1.rate2 = temp1.reset_index().drop('index',axis=1)
st2.rate2 = temp2.reset_index().drop('index',axis=1)


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
                    'cap_invest', 'nominc', 'cpi_cumul', 'budrev', 'budexp', 'brent_oil_price', 'st_dummy', 'DATE_OPER',
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

# lr, data_reg, selected_cols = run_rec_func(st1,st2, mcols, mdf, '', 'base')

