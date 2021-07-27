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

    # portfolio['EAD'] = portfolio.ESAS_RESID_AZN + portfolio.VK_ESAS_QALIQ_AZN + portfolio.PROCAZN + portfolio.PROCPROSAZN  # QUESTION
    portfolio['EAD_PRIN'] = portfolio.ESAS_RESID_AZN + portfolio.VK_ESAS_QALIQ_AZN
    # portfolio['EAD_INT'] = portfolio.PROCAZN + portfolio.PROCPROSAZN
    # portfolio['EAD_LINE'] = np.where(portfolio.TIPKREDITA.isin(prod_cards),
    #                                  0.5 * (portfolio.SUMMAKREAZN - portfolio.EAD), 0)
    portfolio['EAD_TOTAL_WITH_LINES'] = portfolio.EAD + portfolio.EAD_LINE

    portfolio = portfolio[portfolio.EAD_TOTAL_WITH_LINES != 0]

    print(portfolio.shape)

    # new interest rate

    portfolio['ADJ_INT_RATE'] = np.where(portfolio.PROCSTAVKRE == 1, 15, portfolio.PROCSTAVKRE)

    portfolio['ADJ_INT_RATE_24'] = np.where(portfolio.PROCSTAVKRE == 1, 24, portfolio.PROCSTAVKRE)

    # collateral and EAD

    real_est = [2, 10, 11, 12, 13, 14]
    depo = [8]
    sec = [9]
    pmetals = [4]

    # REAL ESTATE
    portfolio['COLL_REAL'] = np.where(portfolio.TIPZALOGA.isin(real_est), portfolio.SUMMA_ZALOGAAZN, 0)
    portfolio['COLL_REAL_HAIRCUT_80'] = np.where(portfolio.TIPZALOGA.isin(real_est), 0.8 * portfolio.SUMMA_ZALOGAAZN, 0)

    portfolio['COLL_REAL_HAIRCUT_80_DISC_15_4Y'] = np.where(portfolio.TIPZALOGA.isin(real_est),
                                                            0.8 * portfolio.SUMMA_ZALOGAAZN * np.power(
                                                                1 + portfolio.ADJ_INT_RATE / 1200, -48), 0)

    portfolio['COLL_REAL_HAIRCUT_80_DISC_24_4Y'] = np.where(portfolio.TIPZALOGA.isin(real_est),
                                                            0.8 * portfolio.SUMMA_ZALOGAAZN * np.power(
                                                                1 + portfolio.ADJ_INT_RATE_24 / 1200, -48), 0)

    # DEPOSITS
    portfolio['COLL_DEPO'] = np.where(portfolio.TIPZALOGA.isin(depo), portfolio.SUMMA_ZALOGAAZN, 0)

    # SECURITIES
    portfolio['COLL_SEC'] = np.where(portfolio.TIPZALOGA.isin(sec), portfolio.SUMMA_ZALOGAAZN, 0)
    portfolio['COLL_SEC_HAIRCUT_70'] = np.where(portfolio.TIPZALOGA.isin(sec), 0.7 * portfolio.SUMMA_ZALOGAAZN, 0)

    # PRECIOUS METALS
    portfolio['COLL_PMET'] = np.where(portfolio.TIPZALOGA.isin(pmetals), portfolio.SUMMA_ZALOGAAZN, 0)

    portfolio['COLL_PMET_HAIRCUT_80'] = np.where(portfolio.TIPZALOGA.isin(pmetals), 0.8 * portfolio.SUMMA_ZALOGAAZN, 0)

    portfolio['COLL_PMET_HAIRCUT_80_DISC_15_1Y'] = np.where(portfolio.TIPZALOGA.isin(pmetals),
                                                            0.8 * portfolio.SUMMA_ZALOGAAZN * np.power(
                                                                1 + portfolio.ADJ_INT_RATE / 1200, -12), 0)

    portfolio['COLL_PMET_HAIRCUT_80_DISC_24_1Y'] = np.where(portfolio.TIPZALOGA.isin(pmetals),
                                                            0.8 * portfolio.SUMMA_ZALOGAAZN * np.power(
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

    portfolio['REST_NEW'] = np.where(portfolio.PROCSTAVKRE == 1, portfolio.DATE_OPEN, portfolio.DATE_RESTRUCTURE)

    # solving stage issue

    portfolio = portfolio.merge(stages[['CLIENT_ID', 'STAGE']], how='left', left_on='LICSCHKRE', right_on='CLIENT_ID')

    portfolio['FINAL_STAGE'] = np.where(portfolio.PROCSTAVKRE == 1, 'POCI', portfolio.STAGE)

