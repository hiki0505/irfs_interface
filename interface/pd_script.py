# import numpy as np
# import scipy as sp
# import scipy.stats as ss
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import statsmodels as sm
# import statsmodels.api as sms
import cx_Oracle as co
# import sklearn.linear_model as slm
# import sklearn.metrics as smr
# import sklearn.preprocessing as skp
# from datetime import datetime as dt
from datetime import timedelta as dlt
from .config import database_table_name
from .services import get_ifrs_data
# from dateutil.relativedelta import relativedelta as rlt
# import sys
# import dill
# import pickle

def pd_calculator(db_credentials, plist, repd_start, repd_end):
    conn = co.connect(
        u'{}/{}@{}/{}'.format(db_credentials.username, db_credentials.password, db_credentials.host,
                              db_credentials.dbname))
    # 'ruqiyye_bedirova/ruqiyye03@192.168.0.17:1521/bank'
    print(conn)
    print(db_credentials)
    cursor = conn.cursor()
    cursor.execute(""" ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS' """)

    ddate = pd.read_sql('select distinct act_date from {} order by act_date'.format(database_table_name), con=conn)
    print(ddate)
    print('*' * 30)
    ddm = ddate[:]
    ddm.index = pd.to_datetime(ddm.ACT_DATE)
    ddm = ddm.resample('M').last()
    print(ddm.tail())
    # globs

    # dbt = "portfolio_17"  # table name in the database
    dbt = database_table_name
    ifrs_creds = get_ifrs_data()

    # plist = ifrs_creds['plist']  # Product id or name list
    # wrof = "WROF" # write-off status column

    # mortgage - (01000, 01001)

    # soleprop - business and must_novu like 'f%z%k%'
    # corporate - business and must_novu not like 'f%z%k%'

    """business - (01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 
    01858, 02002, 02004, 02009, 02014, 02017, 02100, 02102, 02103, 
    02201, 02203, 02300, 02304, 02400, 02600)"""

    # car - (02802)

    # cards - (02804)

    # consumer - (01801, 02201, 02203, 02800, 02801, 02803, 02805)

    p0 = "select * from "

    stg1 = ""
    stg2 = ""
    '''
    TypeError at /calculate
    Invalid comparison between dtype=datetime64[ns] and date
    '''
    for i in ddm.ACT_DATE[((ddm.ACT_DATE > repd_start) & (ddm.ACT_DATE < repd_end))]:
        end_date = i + dlt(days=370)
        stage2_st_date = i - dlt(days=185)
        stage3_st_date = i - dlt(days=370)

        x1 = """union (select t0.{repd}, count(t0.acc) as orig_count, 
        sum(t0.amt) as orig_amount, sum(nvl(t3.deft,0))/count(t0.acc) as rate from """.format(repd=ifrs_creds['repd'])

        stg1 += x1
        stg2 += x1

        x2 = """(select max({repd}) as {repd}, {id_c} as acc, sum(({anp_m}+{aop_m})) as amt, 
        case 
        when (max(greatest(nvl({dp},0), nvl({di},0))) > 90) or 
        ((max(greatest(nvl({dp},0), nvl({di},0))) between 31 and 90) 
        and nvl(max({repd})-max({resd}),999) < 182) then 'stage3'
        
        
        when ((max(greatest(nvl({dp},0), nvl({di},0))) between 31 and 90) and 
        (nvl(max({repd})-max({resd}),999) > 181)) or 
        
        
        ((max(greatest(nvl({dp},0), nvl({di},0))) between 11 and 30) and 
        nvl(max({repd})-max({resd}),999) < 182) 
        
        then 'stage2' 
        else 'stage1' end as par_status 
        from {dbt} where {repd} = '{start}' and 
        {pid} in {plist} and {ptype}='A' group by {id_c}) t0""".format(repd=ifrs_creds['repd'], resd=ifrs_creds['resd'],
                                                                       id_c=ifrs_creds['id_c'], anp_m=ifrs_creds['anp_m'], aop_m=ifrs_creds['aop_m'], dp=ifrs_creds['dp'],
                                                                       di=ifrs_creds['di'], dbt=dbt, start=i, pid=ifrs_creds['pid'], plist=plist,
                                                                       ptype=ifrs_creds['ptype'])

        stg1 += x2
        stg2 += x2

        past6_stage = """ left outer join (select {id_c} as acc1, 
            case 
            when max(greatest(nvl({dp},0), nvl({di},0)))>90 or 
            max(case when (greatest(nvl({dp},0), nvl({di},0)) between 31 and 90) and  
            nvl({repd}-{resd},999) < 182 then 1 else 0 end) = 1 then 3 
            when 
            max(case when (greatest(nvl({dp},0), nvl({di},0)) between 31 and 90) and 
            nvl({repd}-{resd},999) > 181 then 1 else 0 end) = 1 or 
            max(case when (greatest(nvl({dp},0), nvl({di},0)) between 11 and 30) and 
            nvl({repd}-{resd},999) < 182 then 1 else 0 end) = 1 then 2 
            else 1 end as past6_stage      
            from {dbt} where {repd} < '{i}' and {repd} > '{stage2_st_date}' group by {id_c}) 
            t1 on t0.acc = t1.acc1 """.format(
            dbt=dbt, i=i, stage2_st_date=stage2_st_date, repd=ifrs_creds['repd'], resd=ifrs_creds['resd'], id_c=ifrs_creds['id_c'], dp=ifrs_creds['dp'], di=ifrs_creds['di'])

        stg1 += past6_stage
        stg2 += past6_stage

        past7_12_stage = """ left outer join (select {id_c} as acc2, 
            case 
            when max(greatest(nvl({dp},0), nvl({di},0)))>90 or 
            max(case when (greatest(nvl({dp},0), nvl({di},0)) between 31 and 90) and  
            nvl({repd}-{resd},999) < 182 then 1 else 0 end) = 1 then 3 
            when 
            max(case when (greatest(nvl({dp},0), nvl({di},0)) between 31 and 90) and 
            nvl({repd}-{resd},999) > 181 then 1 else 0 end) = 1 or 
            max(case when (greatest(nvl({dp},0), nvl({di},0)) between 11 and 30) and 
            nvl({repd}-{resd},999) < 182 then 1 else 0 end) = 1 then 2 
            else 1 end as past712_stage       
            from {dbt} where {repd} < '{stage2_st_date}' and {repd} > '{stage3_st_date}' group by {id_c}) 
            t2 on t0.acc = t2.acc2 """.format(
            dbt=dbt, stage2_st_date=stage2_st_date, stage3_st_date=stage3_st_date, repd=ifrs_creds['repd'],
            resd=ifrs_creds['resd'], id_c=ifrs_creds['id_c'], dp=ifrs_creds['dp'], di=ifrs_creds['di'])

        stg1 += past7_12_stage
        stg2 += past7_12_stage

        x3 = """
        left outer join 
        (select {id_c} as acc3, 
        case 
        when max(greatest(nvl({dp},0), nvl({di},0)))>90 or 
        max(case when (greatest(nvl({dp},0), nvl({di},0)) between 11 and 30) and  
        nvl({repd}-{resd},999) < 182 then 1 else 0 end) = 1
        then 1 else 0 end as deft from {dbt} where {repd} > '{start}' and {repd} < '{end}'
        group by {id_c}) t3 on t0.acc = t3.acc3
        """.format(dbt=dbt, repd=ifrs_creds['repd'], resd=ifrs_creds['resd'], id_c=ifrs_creds['id_c'], anp_m=ifrs_creds['anp_m'], aop_m=ifrs_creds['aop_m'],
                   dp=ifrs_creds['dp'], di=ifrs_creds['di'], start=i, end=end_date)

        stg1 += x3
        stg2 += x3

        stg1 += " where t0.par_status='stage1' and nvl(t1.past6_stage,1)=1 and nvl(t2.past712_stage,1)!=3 group by t0.{repd}) ".format(
            repd=ifrs_creds['repd'])
        stg2 += " where (t0.par_status='stage2' and nvl(t1.past6_stage,1)!=3) or (t0.par_status='stage1' and nvl(t1.past6_stage,1)=2) group by t0.{repd}) ".format(
            repd=ifrs_creds['repd'])

    sql1 = p0 + stg1[5:] + "  order by {repd} ".format(repd=ifrs_creds['repd'])
    sql2 = p0 + stg2[5:] + "  order by {repd} ".format(repd=ifrs_creds['repd'])

    data1 = pd.read_sql(sql1, con=conn)
    # data1.to_pickle('cons_tr_data1.pkl')
    print('*' * 30)
    print(data1)
    data2 = pd.read_sql(sql2, con=conn)
    print('*' * 30)
    print(data2)
    # data3 = pd.merge(data1, data2)
    # data2.to_pickle('cons_tr_data2.pkl')
    return data1, data2
