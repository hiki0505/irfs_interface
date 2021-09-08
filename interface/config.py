# FEATURES = ['repd', 'resd', 'st_date', 'end_date', 'bthday', 'dp', 'di', 'anp_m', 'anp_c', 'aop_m', 'aop_c',
#             'ani_m', 'ani_c', 'aoi_m', 'aoi_c', 'aor_m', 'aor_c', 'id_l', 'id_c', 'id_sub', 'cid', 'pid', 'ctype', 'ptype']
# database_table_name = 'portfolio_test2'
# database_table_name_caps = 'PORTFOLIO_TEST2'
import pandas

username = 'ruqiyye_bedirova'  # it is temporary
''' GLOBALS '''


''' GLOBALS COMING FROM macro and adjustment part '''

# seasonal adjustment
# method (covariance ...)
# cycle
# lag
# monte_carlo_n_sample

    # mcols = ['neer', 'nneer', 'reer', 'nreer', 'usdazn', 'gdp', 'ngdp', 'rgdp', 'rngdp',
#              'cap_invest', 'nominc', 'cpi_cumul', 'budrev', 'budexp', 'brent_oil_price']
#
# msigns = [False, False, False, False, True, False, False, False, False,
#           False, False, True, False, False, False]
#
# mgroups = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 4, 4, 5]


''' FOR INTERFACE '''
database_table_name = 'portfolio_21'
database_table_name_caps = 'PORTFOLIO_21'  # could be converted by uppercase method
PLIST_GLOBS = {
    'consumer': "(01801, 02201, 02203, 02800, 02801, 02803, 02805)",
    'corporate': "(01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002, 02004, 02009, 02014, 02017, 02100, 02102, 02103, 02201, 02203, 02300, 02304, 02400, 02600) and must_novu not like 'F%Z%K%'",
    'sole': "(01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002, 02004, 02009, 02014, "
            "02017, 02100, 02102, 02103, 02300, 02304, 02400, 02600) and must_novu like 'F%Z%K%' "
}

recovery_period_pd = 185  # coming from pd sql script
stage2_start_date = 31  # coming from pd sql script
stage2_end_date = 90  # coming from pd sql script
odeme_qaydasi = ''  # from sql script also
# portfolio start date
# portfolio end date
# sheet_name
