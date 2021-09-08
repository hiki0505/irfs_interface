import numpy as np
import pandas as pd
import cx_Oracle as co
from datetime import datetime as dt
from datetime import timedelta as dlt
from dateutil.relativedelta import relativedelta as rlt
import sys
import dill
import pickle
from .config import database_table_name
from .services import get_ifrs_data


def staging_calculator(db_credentials, ifrs_creds, repd_end):
    # conn = co.connect(
    #     u'{}/{}@{}/{}'.format(db_credentials['username'], db_credentials['password'], db_credentials['host'],
    #                           db_credentials['dbname']))
    conn = co.connect(
        u'{}/{}@{}/{}'.format(db_credentials.username, db_credentials.password, db_credentials.host,
                              db_credentials.dbname))

    cursor = conn.cursor()
    cursor.execute(""" ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS' """)

    # dbt = "portfolio_21"  # table name in the database
    dbt = database_table_name
    ifrs_creds = get_ifrs_data()
    # payment type, annuity for these purposes  # payment type, annuity for these purposes

    staging_date = dt.strptime(repd_end, "%d-%b-%y")
    stage2_st_date = staging_date - dlt(days=185)
    stage3_st_date = staging_date - dlt(days=370)

    x1 = """
    select t0.{repd}, t0.client_id, t0.curr_stage, t1.past6_stage, t2.past712_stage,
    case 
    when t0.curr_stage=1 and nvl(t1.past6_stage,1)=1 and nvl(t2.past712_stage,1)!=3 then 1
    when (t0.curr_stage=2 and nvl(t1.past6_stage,1)!=3) or (t0.curr_stage=1 and nvl(t1.past6_stage,1)=2) then 2
    else 3 end as stage from """.format(repd=ifrs_creds['repd'])

    x2 = """(select max({repd}) as {repd}, {id_c} as client_id, 
    case 
    when (max(greatest(nvl({dp},0), nvl({di},0))) > 90) or 
    ((max(greatest(nvl({dp},0), nvl({di},0))) between 31 and 90) and nvl(max({repd})-max({resd}),999) < 182) then 3 
    when ((max(greatest(nvl({dp},0), nvl({di},0))) between 31 and 90) and (nvl(max({repd})-max({resd}),999) > 181)) or 
    ((max(greatest(nvl({dp},0), nvl({di},0))) between 11 and 30) and nvl(max({repd})-max({resd}),999) < 182) then 2 
    else 1 end as curr_stage 
    from {dbt} where {repd} = '{staging_date}' group by {id_c}) t0 """.format(repd=ifrs_creds['repd'], resd=ifrs_creds['resd'],
                                                                              id_c=ifrs_creds['id_c'], dp=ifrs_creds['dp'], di=ifrs_creds['di'], dbt=dbt,
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
        repd=ifrs_creds['repd'], resd=ifrs_creds['resd'], id_c=ifrs_creds['id_c'], dp=ifrs_creds['dp'], di=ifrs_creds['di'])

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
        dbt=dbt, stage2_st_date=stage2_st_date, stage3_st_date=stage3_st_date, repd=ifrs_creds['repd'],
        resd=ifrs_creds['resd'], id_c=ifrs_creds['id_c'], dp=ifrs_creds['dp'], di=ifrs_creds['di'])

    sql = x1 + x2 + x3 + x4

    stage_data = pd.read_sql(sql, con=conn)

    return stage_data

