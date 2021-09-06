# database_table_name = 'portfolio_test2'
# database_table_name_caps = 'PORTFOLIO_TEST2'
import pandas
database_table_name = 'portfolio_21'
database_table_name_caps = 'PORTFOLIO_21'
username = 'ruqiyye_bedirova'
PLIST_GLOBS = {
    'consumer': "(01801, 02201, 02203, 02800, 02801, 02803, 02805)",
    'corporate': "(01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002, 02004, 02009, 02014, 02017, 02100, 02102, 02103, 02201, 02203, 02300, 02304, 02400, 02600) and must_novu not like 'F%Z%K%'",
    'sole': "(01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002, 02004, 02009, 02014, "
            "02017, 02100, 02102, 02103, 02300, 02304, 02400, 02600) and must_novu like 'F%Z%K%' "
}
# FEATURES = ['DATE_OPER', 'REST_NEW', 'DATE_OPEN', 'DATE_PLANCLOSE', 'DATEOFBIRTH', 'OVERDUEDAY',
#             'INTEREST_OVERDUEDAY', 'SUMMAAZN', 'SUMMA', 'SUMMA_19AZN', 'SUMMA_19', 'PROCAZN', 'PROC', 'PROCPROSAZN',
#             'PROCPROS', 'SUMMAKREAZN', 'SUMMAKRE', 'PROCSTAVKRE', 'KOD1', 'LICSCHKRE', 'subaccount', 'cid', 'pid',
#             'plist', 'wrof']
FEATURES = ['repd', 'resd', 'st_date', 'end_date', 'bthday', 'dp', 'di', 'anp_m', 'anp_c', 'aop_m', 'aop_c',
            'ani_m', 'ani_c', 'aoi_m', 'aoi_c', 'aor_m', 'aor_c', 'id_l', 'id_c', 'id_sub', 'cid', 'pid', 'ctype', 'ptype']

