import numpy as np
import pandas as pd
import cx_Oracle as co
from datetime import datetime as dt
from datetime import timedelta as dlt
from dateutil.relativedelta import relativedelta as rlt
import sys
import dill
import pickle


def staging_calculator(db_credentials, ifrs_creds, repd_end):
    conn = co.connect(
        u'{}/{}@{}/{}'.format(db_credentials['username'], db_credentials['password'], db_credentials['host'],
                              db_credentials['dbname']))

    cursor = conn.cursor()
    cursor.execute(""" ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS' """)

    dbt = "portfolio_21"  # table name in the database

    repd = ifrs_creds['repd']  # report date for the portfolio
    resd = ifrs_creds['resd']  # date of restructuring
    st_date = ifrs_creds['st_date']  # loan origination date
    end_date = ifrs_creds['end_date']  # contractual loan maturity date
    bthday = ifrs_creds['bthday']

    dp = ifrs_creds['dp']  # days principal is past due
    di = ifrs_creds['di']  # days interest is past due

    anp_m = ifrs_creds['anp_m']  # normal principal amount in manats
    anp_c = ifrs_creds['anp_c']  # normal principal amount in currency
    aop_m = ifrs_creds['aop_m']  # overdue principal amount in manats
    aop_c = ifrs_creds['aop_c']  # overdue principal amount in currency

    # ani_m =  # normal interest amount in manats
    # ani_c =  # normal interest amount in currency
    # aoi_m =  # overdue interest amount in manats
    # aoi_c =  # overdue interest amount in currency

    aor_m = ifrs_creds['aor_m']  # original amount in manats
    aor_c = ifrs_creds['aor_c']  # original amount in currency

    id_l = ifrs_creds['id_l']  # contract (loan) ID which is client id here
    id_c = ifrs_creds['id_c']  # client ID
    id_sub = ifrs_creds['id_sub']  # subaccount (order of loan)

    # bid = "debt_standard_gl_acct_no" # balance account No
    cid = ifrs_creds['cid']  # currency ID (or name)
    pid = ifrs_creds['pid']  # product ID or name
    ctype = ifrs_creds['ctype']  # customer type, individual or legal
    ptype = ifrs_creds['ptype']  # payment type, annuity for these purposes  # payment type, annuity for these purposes

    staging_date = dt.strptime(repd_end, "%d-%b-%y")
    stage2_st_date = staging_date - dlt(days=185)
    stage3_st_date = staging_date - dlt(days=370)

    x1 = """
    select t0.{repd}, t0.client_id, t0.curr_stage, t1.past6_stage, t2.past712_stage,
    case 
    when t0.curr_stage=1 and nvl(t1.past6_stage,1)=1 and nvl(t2.past712_stage,1)!=3 then 1
    when (t0.curr_stage=2 and nvl(t1.past6_stage,1)!=3) or (t0.curr_stage=1 and nvl(t1.past6_stage,1)=2) then 2
    else 3 end as stage from """.format(repd=repd)

    x2 = """(select max({repd}) as {repd}, {id_c} as client_id, 
    case 
    when (max(greatest(nvl({dp},0), nvl({di},0))) > 90) or 
    ((max(greatest(nvl({dp},0), nvl({di},0))) between 31 and 90) and nvl(max({repd})-max({resd}),999) < 182) then 3 
    when ((max(greatest(nvl({dp},0), nvl({di},0))) between 31 and 90) and (nvl(max({repd})-max({resd}),999) > 181)) or 
    ((max(greatest(nvl({dp},0), nvl({di},0))) between 11 and 30) and nvl(max({repd})-max({resd}),999) < 182) then 2 
    else 1 end as curr_stage 
    from {dbt} where {repd} = '{staging_date}' group by {id_c}) t0 """.format(repd=repd, resd=resd,
                                                                              id_c=id_c, dp=dp, di=di, dbt=dbt,
                                                                              staging_date=staging_date
                                                                              )

    x3 = """ left outer join (select {id_c} as acc1, 
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
    from {dbt} where {repd} < '{staging_date}' and {repd} > '{stage2_st_date}' group by {id_c}) 
    t1 on t0.client_id = t1.acc1 """.format(
        dbt=dbt, staging_date=staging_date, stage2_st_date=stage2_st_date,
        repd=repd, resd=resd, id_c=id_c, dp=dp, di=di)

    x4 = """ left outer join (select {id_c} as acc2, 
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
    t2 on t0.client_id = t2.acc2 """.format(
        dbt=dbt, stage2_st_date=stage2_st_date, stage3_st_date=stage3_st_date, repd=repd,
        resd=resd, id_c=id_c, dp=dp, di=di)

    sql = x1 + x2 + x3 + x4

    stage_data = pd.read_sql(sql, con=conn)

    return stage_data

