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


def lgd_calculator(db_credentials, ifrs_creds, plist, act_date):
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

    ddate = pd.read_sql('select distinct act_date from {} order by act_date'.format(database_table_name), con=conn)
    ddm = ddate[:]
    ddm.index = pd.to_datetime(ddm.ACT_DATE)
    ddm = ddm.resample('M').last()

    temp_table_sql = """
    DECLARE
        Table_exists INTEGER;
    BEGIN

        SELECT COUNT(*) INTO Table_exists FROM sys.all_tables WHERE table_name = 'SHABZUL2';

        IF (table_exists) = 1
        THEN
            DBMS_OUTPUT.PUT_LINE('WANNA DROP TABLE AND CREATE AGAIN');
            EXECUTE IMMEDIATE 'DROP TABLE shabzul2';
            EXECUTE IMMEDIATE 'CREATE TABLE shabzul2 (
                                                 id NUMBER GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),
                                                 act_date DATE,
                                                 par_status VARCHAR(100),
                                                 original NUMBER(10, 0),
                                                 c0 NUMBER(38, 7),
                                                 loss NUMBER(38, 7),
                                                 paid NUMBER(38, 7)
                                                 )';
            commit;
            DBMS_OUTPUT.PUT_LINE('Table Dropped and Re-Created!');
        ELSE
            DBMS_OUTPUT.PUT_LINE('WANNA JUST CREATE');
            EXECUTE IMMEDIATE 'CREATE TABLE shabzul2 (
                                                 id NUMBER GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),
                                                 act_date DATE,
                                                 par_status VARCHAR(100),
                                                 original NUMBER(10, 0),
                                                 c0 NUMBER(38, 7),
                                                 loss NUMBER(38, 7),
                                                 paid NUMBER(38, 7)
                                                 )';
            commit;
            DBMS_OUTPUT.PUT_LINE('New Table Created!');
        END IF;
    END;
    """
    cursor.execute(temp_table_sql)
    conn.commit()

    p1 = "select * from "

    # p2 = ""

    for i in ddm.ACT_DATE[(ddm.ACT_DATE <= act_date)]:
        p2_start = """insert into shabzul2 (
         act_date,
         par_status,
         original,
         c0,
         loss,
         paid)
        select t1.act_date, t1.par_status, sum(t1.amt) as original, 
        sum(case when t2.par_status = '0' then t2.amt else 0 end)/sum(t1.amt) as c0,
        sum(case when t2.par_status = '1_' then t2.amt else 0 end)/sum(t1.amt) as loss,

        1-sum(case when t2.par_status = '0' then t2.amt else 0 end)/sum(t1.amt)-
        sum(case when t2.par_status = '1_' then t2.amt else 0 end)/sum(t1.amt) as paid

        from
        (select act_date, kredit_hesabi as acc, subhesab as acc2,
        case 
        """
        p2_middle = '''
        when greatest(FAIZ_OVER_DAYS, ESAS_OVER_DAYS) = 0 then '00_0'
        when greatest(FAIZ_OVER_DAYS, ESAS_OVER_DAYS) between 1 and 90 then '01_1_90'
        when greatest(FAIZ_OVER_DAYS, ESAS_OVER_DAYS) between 91 and 120 then '02_91_120'
        when greatest(FAIZ_OVER_DAYS, ESAS_OVER_DAYS) between 121 and 150 then '03_121_150'
        when greatest(FAIZ_OVER_DAYS, ESAS_OVER_DAYS) between 151 and 180 then '04_151_180'    
        when greatest(FAIZ_OVER_DAYS, ESAS_OVER_DAYS) between 181 and 210 then '05_181_210'
        when greatest(FAIZ_OVER_DAYS, ESAS_OVER_DAYS) between 211 and 240 then '06_211_240'
        when greatest(FAIZ_OVER_DAYS, ESAS_OVER_DAYS) between 241 and 270 then '07_241_270'
        when greatest(FAIZ_OVER_DAYS, ESAS_OVER_DAYS) between 271 and 300 then '08_271_300'
        when greatest(FAIZ_OVER_DAYS, ESAS_OVER_DAYS) between 301 and 330 then '09_301_330'
        when greatest(FAIZ_OVER_DAYS, ESAS_OVER_DAYS) between 331 and 360 then '10_331_360'
        when greatest(FAIZ_OVER_DAYS, ESAS_OVER_DAYS) > 360 then '11_360_'
        '''
        stage_3_start = 90
        p2_middle_generate = """
        when greatest({di}, {dp}) = 0 then '00_0'
        when greatest({di}, {dp}) between 1 and {stage_3_start} then '01_1_{stage_3_start}'
        """.format(stage_3_start=stage_3_start, di=ifrs_creds['di'], dp=ifrs_creds['dp'])

        for i in ['02', '03', '04', '05', '06', '07', '08', '09', '10', '11']:
            if i == '11':
                p2_middle_generate += "when greatest({di}, {dp}) > {stage_3_start} then '{i}_{stage_3_start}_'".format(
                                        stage_3_start=stage_3_start, i=i, di=ifrs_creds['di'], dp=ifrs_creds['dp'])
                break
            btw1_date = stage_3_start+1
            btw2_date = stage_3_start+30

            p2_middle_generate += "when greatest({di}, {dp}) between {btw1_date} and {btw2_date} then '{i}_{btw1_date}_{btw2_date}'".format(btw1_date=btw1_date, btw2_date=btw2_date, i=i, di=ifrs_creds['di'], dp=ifrs_creds['dp'])
            stage_3_start += 30

        p2_end = """
        end as par_status,
        esas_resid_azn + vk_esas_qaliq_azn as amt
        from {dbt} where act_date='{i}' and odeme_qaydasi='A' and {pid} in {plist}) t1 
        left join
        (select kredit_hesabi as acc, subhesab as acc2, 
        case 
        when greatest({di}, {dp}) = 0 then '0'
        when greatest({di}, {dp}) > 1 then '1_'
        end as par_status,
        esas_resid_azn + vk_esas_qaliq_azn as amt
        from {dbt} where act_date = add_months(to_date('{i}', 'YYYY/MM/DD HH24:MI:SS'),12)) t2
        on t1.acc = t2.acc and t1.acc2=t2.acc2
        group by t1.act_date, t1.par_status""".format(dbt=dbt, i=i, pid=ifrs_creds['pid'], plist=plist, di=ifrs_creds['di'], dp=ifrs_creds['dp'])

        p2 = p2_start + p2_middle_generate + p2_end
        cursor.execute(p2)
        conn.commit()

    cursor.execute('''
    ALTER TABLE shabzul2
    ADD cl NUMBER(38,7)
    ''')
    conn.commit()

    cursor.execute('''
        DECLARE
        CURSOR cur 
        IS
            SELECT loss, id 
            FROM shabzul2;
            maxloss NUMBER(38,7);
        --    product_ VARCHAR(500);
            loss_ NUMBER(38,7);
            id_ NUMBER(38,7);
        BEGIN
        OPEN cur;
        LOOP
        FETCH cur INTO loss_, id_;
        IF cur%NOTFOUND
        THEN
        EXIT;
        END IF;
        
        IF id_ = 1 THEN
            maxloss := loss_;
        ElSE
            IF loss_ > maxloss
            THEN
                maxloss := loss_;
            ELSE maxloss := maxloss;
            END IF;
        END IF;
        UPDATE shabzul2 SET cl = maxloss WHERE id = id_;
        
        END LOOP;
        CLOSE cur;
        END;
    ''')




    # sql = p1 + p2[7:] + "order by act_date, par_status"
    sql = "select * from shabzul2 order by id, act_date, par_status"
    data = pd.read_sql(sql, con=conn)

    return data

