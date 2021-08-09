import numpy as np
import pandas as pd
import openpyxl


def ecl_calculator(pd_cons, pd_soles, pd_corps, lgds, stagings):
    cons_pds = pd_cons
    # pension_pds = pd.read_pickle('pension_pds.pkl')
    # lomb_pds = pd.read_pickle('lomb_pds.pkl')
    # micro_pds = pd.read_pickle('mikro_pds.pkl') # QUESTION
    sole_pds = pd_soles
    corp_pds = pd_corps


    # LGDs
    lgs = lgds

    # stages
    stages = stagings

    # payments

    # payments = pd.read_pickle('payments.pkl')

    # portfolio
    portfolio = pd.read_pickle('port2020.pkl')  # QUESTION

    # product codes

    # prod_mort = [3]
    prod_cons = [4, 24, 7, 23, 12, 13, 15, 28]
    # prod_car - (4)
    # prod_cards = [5, 25]
    # prod_pensioner = [11, 16, 17, 18, 20]

    # prod_lomb = [10, 26]
    # prod_micro = [9, 14, 19, 21, 29]
    prod_sole = [2, 27]
    prod_corp = [1, 8, 31]

    print(lgs.head())
    print(stages.STAGE.unique())
    print(stages.head())

    portfolio['EAD'] = portfolio.ESAS_RESID_AZN + portfolio.VK_ESAS_QALIQ_AZN + portfolio.FAIZ_QALIQ_AZN + portfolio.VK_FAIZ_QALIQ_AZN
    portfolio['EAD_PRIN'] = portfolio.ESAS_RESID_AZN + portfolio.VK_ESAS_QALIQ_AZN
    portfolio['EAD_INT'] = portfolio.FAIZ_QALIQ_AZN + portfolio.VK_FAIZ_QALIQ_AZN
    portfolio['EAD_LINE'] = np.where(portfolio.FEA_KODU.isin(prod_cards),  # QUESTION
                                     0.5 * (portfolio.ESAS_INIT_AZN - portfolio.EAD), 0)
    portfolio['EAD_TOTAL_WITH_LINES'] = portfolio.EAD + portfolio.EAD_LINE

    portfolio = portfolio[portfolio.EAD_TOTAL_WITH_LINES != 0]

    print(portfolio.shape)

    # new interest rate

    portfolio['ADJ_INT_RATE'] = np.where(portfolio.FAIZ == 1, 15, portfolio.FAIZ)  # QUESTION

    portfolio['ADJ_INT_RATE_24'] = np.where(portfolio.FAIZ == 1, 24, portfolio.FAIZ)  # QUESTION

    # collateral and EAD

    real_est = [2, 10, 11, 12, 13, 14]
    depo = [8]
    sec = [9]
    pmetals = [4]

    # REAL ESTATE
    portfolio['COLL_REAL'] = np.where(portfolio.GIROV_NOVU.isin(real_est), portfolio.GIROV_MEBLEG_AZN, 0)
    portfolio['COLL_REAL_HAIRCUT_80'] = np.where(portfolio.GIROV_NOVU.isin(real_est), 0.8 * portfolio.GIROV_MEBLEG_AZN, 0)

    portfolio['COLL_REAL_HAIRCUT_80_DISC_15_4Y'] = np.where(portfolio.GIROV_NOVU.isin(real_est),
                                                            0.8 * portfolio.GIROV_MEBLEG_AZN * np.power(
                                                                1 + portfolio.ADJ_INT_RATE / 1200, -48), 0)

    portfolio['COLL_REAL_HAIRCUT_80_DISC_24_4Y'] = np.where(portfolio.GIROV_NOVU.isin(real_est),
                                                            0.8 * portfolio.GIROV_MEBLEG_AZN * np.power(
                                                                1 + portfolio.ADJ_INT_RATE_24 / 1200, -48), 0)

    # DEPOSITS
    portfolio['COLL_DEPO'] = np.where(portfolio.GIROV_NOVU.isin(depo), portfolio.GIROV_MEBLEG_AZN, 0)

    # SECURITIES
    portfolio['COLL_SEC'] = np.where(portfolio.GIROV_NOVU.isin(sec), portfolio.GIROV_MEBLEG_AZN, 0)
    portfolio['COLL_SEC_HAIRCUT_70'] = np.where(portfolio.GIROV_NOVU.isin(sec), 0.7 * portfolio.GIROV_MEBLEG_AZN, 0)

    # PRECIOUS METALS
    portfolio['COLL_PMET'] = np.where(portfolio.GIROV_NOVU.isin(pmetals), portfolio.GIROV_MEBLEG_AZN, 0)

    portfolio['COLL_PMET_HAIRCUT_80'] = np.where(portfolio.GIROV_NOVU.isin(pmetals), 0.8 * portfolio.GIROV_MEBLEG_AZN, 0)

    portfolio['COLL_PMET_HAIRCUT_80_DISC_15_1Y'] = np.where(portfolio.GIROV_NOVU.isin(pmetals),
                                                            0.8 * portfolio.GIROV_MEBLEG_AZN * np.power(
                                                                1 + portfolio.ADJ_INT_RATE / 1200, -12), 0)

    portfolio['COLL_PMET_HAIRCUT_80_DISC_24_1Y'] = np.where(portfolio.GIROV_NOVU.isin(pmetals),
                                                            0.8 * portfolio.GIROV_MEBLEG_AZN * np.power(
                                                                1 + portfolio.ADJ_INT_RATE_24 / 1200, -12), 0)

    # SOME TOTALS

    portfolio['TOTAL_COLL_NO_DISCOUNT'] = portfolio.COLL_REAL_HAIRCUT_80 + portfolio.COLL_DEPO + \
                                          portfolio.COLL_SEC_HAIRCUT_70 + portfolio.COLL_PMET_HAIRCUT_80

    portfolio['TOTAL_COLL_15'] = portfolio.COLL_REAL_HAIRCUT_80_DISC_15_4Y + portfolio.COLL_DEPO + \
                                 portfolio.COLL_SEC_HAIRCUT_70 + portfolio.COLL_PMET_HAIRCUT_80_DISC_15_1Y

    portfolio['TOTAL_COLL_24'] = portfolio.COLL_REAL_HAIRCUT_80_DISC_24_4Y + portfolio.COLL_DEPO + \
                                 portfolio.COLL_SEC_HAIRCUT_70 + portfolio.COLL_PMET_HAIRCUT_80_DISC_24_1Y

    # SOME MINIMUM BASED DISCOUNTING

    portfolio['EAD_AFTER_DEPO_SEC_PMET'] = portfolio['EAD_TOTAL_WITH_LINES'] - portfolio['COLL_DEPO'] - \
                                           portfolio['COLL_SEC_HAIRCUT_70'] - portfolio[
                                               'COLL_PMET_HAIRCUT_80_DISC_24_1Y']

    portfolio['MIN_EAD_OR_COLL_REAL'] = portfolio[['EAD_AFTER_DEPO_SEC_PMET', 'COLL_REAL_HAIRCUT_80']].min(axis=1)

    portfolio['MIN_EAD_OR_COLL_REALDISC_15_4Y'] = portfolio['MIN_EAD_OR_COLL_REAL'] * np.power(
        1 + portfolio.ADJ_INT_RATE / 1200, -48)

    portfolio['MIN_EAD_OR_COLL_REALDISC_24_4Y'] = portfolio['MIN_EAD_OR_COLL_REAL'] * np.power(
        1 + portfolio.ADJ_INT_RATE_24 / 1200, -48)

    # EAD AFTER COLLATERAL

    portfolio['EAD_TOT_ADJ_15'] = np.where(portfolio.EAD_TOTAL_WITH_LINES - portfolio.TOTAL_COLL_15 < 0, 0,
                                           portfolio.EAD_TOTAL_WITH_LINES - portfolio.TOTAL_COLL_15)

    portfolio['EAD_TOT_ADJ_24'] = np.where(portfolio.EAD_TOTAL_WITH_LINES - portfolio.TOTAL_COLL_24 < 0, 0,
                                           portfolio.EAD_TOTAL_WITH_LINES - portfolio.TOTAL_COLL_24)

    portfolio['EAD_TOT_ADJ_MIN_BASED_15'] = np.where(
        portfolio.EAD_TOTAL_WITH_LINES - portfolio.COLL_DEPO - portfolio.COLL_SEC_HAIRCUT_70 - \
        portfolio.COLL_PMET_HAIRCUT_80_DISC_15_1Y - portfolio.MIN_EAD_OR_COLL_REALDISC_15_4Y < 0, 0,
        portfolio.EAD_TOTAL_WITH_LINES - portfolio.COLL_DEPO - portfolio.COLL_SEC_HAIRCUT_70 - \
        portfolio.COLL_PMET_HAIRCUT_80_DISC_15_1Y - portfolio.MIN_EAD_OR_COLL_REALDISC_15_4Y)

    portfolio['EAD_TOT_ADJ_MIN_BASED_24'] = np.where(
        portfolio.EAD_TOTAL_WITH_LINES - portfolio.COLL_DEPO - portfolio.COLL_SEC_HAIRCUT_70 - \
        portfolio.COLL_PMET_HAIRCUT_80_DISC_24_1Y - portfolio.MIN_EAD_OR_COLL_REALDISC_24_4Y < 0, 0,
        portfolio.EAD_TOTAL_WITH_LINES - portfolio.COLL_DEPO - portfolio.COLL_SEC_HAIRCUT_70 - \
        portfolio.COLL_PMET_HAIRCUT_80_DISC_24_1Y - portfolio.MIN_EAD_OR_COLL_REALDISC_24_4Y)

    # new rest date

    portfolio['REST_NEW'] = np.where(portfolio.FAIZ == 1, portfolio.DATE_START, portfolio.DATE_REST)

    # solving stage issue

    portfolio = portfolio.merge(stages[['CLIENT_ID', 'STAGE']], how='left', left_on='KREDIT_HESABI', right_on='CLIENT_ID')

    portfolio['FINAL_STAGE'] = np.where(portfolio.FAIZ == 1, 'POCI', portfolio.STAGE)

    print(portfolio.FINAL_STAGE.unique())

    # print(payments.head())
    #
    # payments['TOTAL_PAY'] = payments.PRIN + payments.INT
    # pmt = payments[['CONTRACT_ID', 'YR', 'TOTAL_PAY']].pivot(index='CONTRACT_ID', columns='YR', values='TOTAL_PAY')

    # portfolio = portfolio.merge(pmt, how='left', left_on='KOD', right_index=True)

    portfolio['EAD_1'] = portfolio.EAD_TOT_ADJ_24

    for i in range(2, 30):
        portfolio['EAD_' + str(i)] = np.where(portfolio.FINAL_STAGE.isin(['1', '3', 'POCI']), 0,
                                              np.where(
                                                  portfolio['EAD_' + str(i - 1)] - np.where(portfolio[i - 1].isna(), 0,
                                                                                            portfolio[i - 1]) < 0, 0,
                                                  portfolio['EAD_' + str(i - 1)] - np.where(portfolio[i - 1].isna(), 0,
                                                                                            portfolio[i - 1])))

    portfolio['FIN_DATE_CLOSE'] = portfolio[['DATE_END_CONTRACT', 'DATE_REST']].max(axis=1)

    portfolio['MATURITY'] = np.select(
        condlist=[
            (((portfolio.FIN_DATE_CLOSE - portfolio.ACT_DATE) / np.timedelta64(1, 'Y') > 0) &
             ((portfolio.FIN_DATE_CLOSE - portfolio.ACT_DATE) / np.timedelta64(1, 'Y') < 1) &
             (portfolio.FINAL_STAGE == '2')),
            ((portfolio.FIN_DATE_CLOSE - portfolio.ACT_DATE) / np.timedelta64(1, 'Y') > 0)],
        choicelist=[1, (portfolio.FIN_DATE_CLOSE - portfolio.ACT_DATE) / np.timedelta64(1, 'Y')],
        default=1)

    # product and currency

    portfolio['VALYUTA'] = np.where(portfolio.CURRENCY == 0, 'AZN', 'CURR')

    # lgs['VALYUTA'] = np.where(lgs.CURRENCY_ID == 0, 'AZN', 'CURR')  # question

    portfolio['MEHSUL_PD'] = np.select(
        condlist=[portfolio.FEA_KODU.isin(prod_mort + prod_cons + prod_cards),
                  portfolio.FEA_KODU.isin(prod_pensioner),
                  portfolio.FEA_KODU.isin(prod_lomb),
                  portfolio.FEA_KODU.isin(prod_micro),
                  portfolio.FEA_KODU.isin(prod_sole),
                  portfolio.FEA_KODU.isin(prod_corp)],
        choicelist=['consumer', 'pensioner', 'lombard', 'micro', 'sole', 'corp']
    )  # question

    portfolio['MEHSUL_LGD'] = np.select(
        condlist=[portfolio.FEA_KODU.isin(prod_mort + prod_cons + prod_cards + prod_pensioner),
                  portfolio.FEA_KODU.isin(prod_lomb + prod_micro),
                  portfolio.FEA_KODU.isin(prod_sole),
                  portfolio.FEA_KODU.isin(prod_corp)],
        choicelist=['consumer', 'micro', 'sole', 'corp']
    )  # question

    print(cons_pds)

    pds = pd.DataFrame(columns=['MEHSUL', 'PD_STAGE1', 'PD_STAGE2'])

    pd_list = [cons_pds, pension_pds, lomb_pds, micro_pds, sole_pds, corp_pds]
    pd_names = ['consumer', 'pensioner', 'lombard', 'micro', 'sole', 'corp']

    for i in range(6):
        pds.loc[i, 'MEHSUL'] = pd_names[i]
        pds.loc[i, 'PD_STAGE1'] = pd_list[i].loc['total_pd', 'stage1']
        pds.loc[i, 'PD_STAGE2'] = pd_list[i].loc['total_pd', 'stage2']

    print(pds)

    portfolio['LGD_BUCKET'] = np.select(
        condlist=[portfolio.FINAL_STAGE == 'POCI',
                  portfolio.ESAS_OVER_DAYS < 121,
                  portfolio.ESAS_OVER_DAYS < 151,
                  portfolio.ESAS_OVER_DAYS < 181,
                  portfolio.ESAS_OVER_DAYS < 211,
                  portfolio.ESAS_OVER_DAYS < 241,
                  portfolio.ESAS_OVER_DAYS < 271,
                  portfolio.ESAS_OVER_DAYS < 301,
                  portfolio.ESAS_OVER_DAYS < 331,
                  portfolio.ESAS_OVER_DAYS < 361,
                  portfolio.ESAS_OVER_DAYS > 360],
        choicelist=['10_360_', '01_90-120', '02_120-150', '03_150-180',
                    '04_180-210', '05_210-240', '06_240-270', '07_270-300',
                    '08_300-330', '09_330-360', '10_360_'],
        default='10_360_'
    )

    portfolio = portfolio.merge(pds, how='left', left_on='MEHSUL_PD', right_on='MEHSUL')  # question
    portfolio = portfolio.merge(lgs[['BUCKET', 'PRODUCT', 'CONSISTENT LOSS']],
                                how='left', left_on=['LGD_BUCKET', 'MEHSUL_LGD', 'VALYUTA'],
                                right_on=['BUCKET', 'PRODUCT'])

    portfolio['LGD'] = np.where(portfolio['PRODUCT'].isna(), 0.54, portfolio['CONSISTENT LOSS'])
    portfolio['LGD'] = np.where(portfolio.TOTAL_COLL_24 > 0, 1, portfolio.LGD)

    portfolio['PD_GEN'] = np.select(
        condlist=[
            portfolio.FINAL_STAGE.isin(['3', 'POCI']),
            portfolio.FINAL_STAGE == '2'
        ],
        choicelist=[
            1, portfolio.PD_STAGE2
        ],
        default=portfolio.PD_STAGE1)

    portfolio['PD_GEN_MATURITY_ADJ'] = np.select(
        condlist=[
            portfolio.FINAL_STAGE.isin(['3', 'POCI']),
            portfolio.FINAL_STAGE == '2',
            ((portfolio.FINAL_STAGE == '1') & (portfolio.MATURITY < 1))
        ],
        choicelist=[
            portfolio.PD_GEN,
            (1 - np.power(1 - portfolio.PD_GEN, portfolio.MATURITY)),
            (1 - np.power(1 - portfolio.PD_GEN, portfolio.MATURITY))
        ],
        default=portfolio.PD_GEN)

    # final PDs per year

    ead_pd_list = []

    for i in range(29):
        portfolio['PD_' + str(i + 1)] = (1 - np.power(1 - portfolio.PD_GEN, i + 1)) - (
                    1 - np.power(1 - portfolio.PD_GEN, i))
        portfolio['EAD_PD_' + str(i + 1)] = portfolio['PD_' + str(i + 1)] * portfolio['EAD_' + str(i + 1)]
        ead_pd_list.append('EAD_PD_' + str(i + 1))

    portfolio['ECL_NOT_USED'] = portfolio[ead_pd_list].sum(axis=1) * portfolio.LGD

    print(portfolio.ECL_NOT_USED.sum())

    portfolio['SEP'] = ''

    # DIFFERENT ECL-S

    portfolio['ECL_15_NOMIN'] = portfolio.EAD_TOT_ADJ_15 * portfolio.PD_GEN_MATURITY_ADJ * portfolio.LGD

    portfolio['ECL_24_NOMIN'] = portfolio.EAD_TOT_ADJ_24 * portfolio.PD_GEN_MATURITY_ADJ * portfolio.LGD

    portfolio['ECL_15_MIN'] = portfolio.EAD_TOT_ADJ_MIN_BASED_15 * portfolio.PD_GEN_MATURITY_ADJ * portfolio.LGD

    portfolio['ECL_24_MIN'] = portfolio.EAD_TOT_ADJ_MIN_BASED_24 * portfolio.PD_GEN_MATURITY_ADJ * portfolio.LGD

    portfolio['ECL_15_NOMIN'].sum(), portfolio['ECL_24_NOMIN'].sum(), portfolio['ECL_15_MIN'].sum(), portfolio[
        'ECL_24_MIN'].sum()

    print(portfolio.columns.values)

    # print(portfolio.FILIALNAME.unique())

    subsetport = portfolio[['DATE_OPER', 'FILIALNUMBER',
                            'LICSCHKRE', 'SUBSCHKRE', 'KOD', 'NAME_LICSCH', 'SUMMAKRE',
                            'SUMMAKREAZN', 'DATE_OPEN', 'DATE_CLOSE', 'DATE_PLANCLOSE', 'FIN_DATE_CLOSE', 'SROK',
                            'LGOTPERIOD',
                            'PROCSTAVKRE', 'ADJ_INT_RATE', 'ADJ_INT_RATE_24',
                            'VALYUTA', 'TIPKREDITA', 'NAME_TIPKREDITA', 'PRODUCT', 'MEHSUL', 'MEHSUL_PD',
                            'MEHSUL_LGD',

                            'SEP',

                            'SUMMA', 'SUMMAAZN', 'SUMMA_19', 'SUMMA_19AZN', 'PROC', 'PROCAZN', 'PROCPROS',
                            'PROCPROSAZN', 'OVERDUEDAY',
                            'DATE_RESTRUCTURE', 'REST_NEW', 'KOLIC_RESTRUCTURE', 'DATE_PROLONG', 'KOLIC_PROLONG',

                            'SEP',

                            'TIPZALOGA', 'NAME_TIPZALOGA', 'SUMMA_ZALOGA',
                            'SUMMA_ZALOGAAZN', 'KOLIC_PEREOCEN_ZALOGA',
                            'SUMMA_PEREOCEN_ZALOGA', 'SUMMA_PEREOCEN_ZALOGAAZN',
                            'DATA_PEREOCEN_ZALOGA',

                            'SEP',

                            'EAD', 'EAD_PRIN', 'EAD_INT', 'EAD_LINE',
                            'EAD_TOTAL_WITH_LINES',

                            'COLL_REAL', 'COLL_REAL_HAIRCUT_80',
                            'COLL_REAL_HAIRCUT_80_DISC_15_4Y',
                            'COLL_REAL_HAIRCUT_80_DISC_24_4Y', 'COLL_DEPO', 'COLL_SEC',
                            'COLL_SEC_HAIRCUT_70', 'COLL_PMET', 'COLL_PMET_HAIRCUT_80',
                            'COLL_PMET_HAIRCUT_80_DISC_15_1Y',
                            'COLL_PMET_HAIRCUT_80_DISC_24_1Y',

                            'SEP',
                            'TOTAL_COLL_15', 'TOTAL_COLL_24',

                            'SEP',

                            'FINAL_STAGE', 'PD_GEN',

                            'SEP',

                            'EAD_TOT_ADJ_15', 'MATURITY', 'PD_GEN_MATURITY_ADJ', 'LGD_BUCKET', 'CONSISTENT LOSS', 'LGD',
                            'ECL_15_NOMIN',

                            'SEP',

                            'EAD_TOT_ADJ_24', 'MATURITY', 'PD_GEN_MATURITY_ADJ', 'LGD_BUCKET', 'CONSISTENT LOSS', 'LGD',
                            'ECL_24_NOMIN',

                            'SEP',

                            'EAD_TOT_ADJ_MIN_BASED_15', 'MATURITY', 'PD_GEN_MATURITY_ADJ', 'LGD_BUCKET',
                            'CONSISTENT LOSS', 'LGD', 'ECL_15_MIN',

                            'SEP',

                            'EAD_TOT_ADJ_MIN_BASED_24', 'MATURITY', 'PD_GEN_MATURITY_ADJ', 'LGD_BUCKET',
                            'CONSISTENT LOSS', 'LGD', 'ECL_24_MIN'

                            ]]

    subsetport[subsetport.MEHSUL_PD == '0']

    print(subsetport.dtypes)

    # subsetport.pivot_table(index=['MEHSUL_PD', 'FINAL_STAGE'],
    #                        values=['EAD', 'EAD_TOTAL_WITH_LINES', 'ECL_24_MIN', 'ECL_24_NOMIN'],
    #                        aggfunc='sum', margins=True)

