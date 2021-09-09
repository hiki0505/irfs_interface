# db_credentials, plist, act_date
# db_credentials, plist, repd_start, repd_end
import json

from dateutil.relativedelta import relativedelta

from .models import Ifrs
from .services import db_connection
import pandas as pd
from .config import database_table_name
from datetime import timedelta as dlt


class MetricsCalculator:
    def __init__(self, db_credentials):
        self.db_credentials = db_credentials
        self.connection = db_connection(db_credentials.engine, db_credentials.username, db_credentials.password,
                                        db_credentials.host, db_credentials.db_name)

        self.cursor = self.connection.cursor()

    def get_ifrs_data(self):
        ifrs_dict = {}
        for field in Ifrs._meta.fields:
            field_name = field.name
            obj = Ifrs.objects.last()
            field_value = getattr(obj, field_name)
            ifrs_dict[field_name] = field_value
        return ifrs_dict

    def calculate_metric(self):
        pass

    def obtain_data_from_sql(self):
        pass


class PD(MetricsCalculator):
    def __init__(self, db_credentials, plist, repd_start, repd_end):
        super().__init__(db_credentials)
        self.plist = plist
        self.repd_end = repd_end
        self.repd_start = repd_start

    @classmethod
    def repd_period(cls, queryset, repd_period):

        if repd_period == 'yearly':
            repd_start = queryset.repd_start + relativedelta(years=+1)
            repd_end = queryset.repd_end + relativedelta(years=-1)
        elif repd_period == 'monthly':
            repd_start = queryset.repd_start + relativedelta(months=+1)
            repd_end = queryset.repd_end + relativedelta(months=-1)

        queryset.repd_period = repd_period
        repd_start = repd_start.strftime("%d-%b-%y")
        repd_end = repd_end.strftime("%d-%b-%y")
        queryset.save()

        return repd_start, repd_end

    def calculate_metric(self):
        with self.connection:
            self.cursor.execute(""" ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS' """)

            ddate = pd.read_sql('select distinct act_date from {} order by act_date'.format(database_table_name),
                                con=self.connection)
            # print(ddate)
            # print('*' * 30)
            ddm = ddate[:]
            ddm.index = pd.to_datetime(ddm.ACT_DATE)
            ddm = ddm.resample('M').last()
            print(ddm.tail())
            dbt = database_table_name
            ifrs_creds = self.get_ifrs_data()
            p0 = "select * from "

            stg1 = ""
            stg2 = ""

            for i in ddm.ACT_DATE[((ddm.ACT_DATE > self.repd_start) & (ddm.ACT_DATE < self.repd_end))]:
                end_date = i + dlt(days=370)
                stage2_st_date = i - dlt(days=185)
                stage3_st_date = i - dlt(days=370)

                x1 = """union (select t0.{repd}, count(t0.acc) as orig_count, 
                sum(t0.amt) as orig_amount, sum(nvl(t3.deft,0))/count(t0.acc) as rate from """.format(
                    repd=ifrs_creds['repd'])

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
                {pid} in {plist} and {ptype}='A' group by {id_c}) t0""".format(repd=ifrs_creds['repd'],
                                                                               resd=ifrs_creds['resd'],
                                                                               id_c=ifrs_creds['id_c'],
                                                                               anp_m=ifrs_creds['anp_m'],
                                                                               aop_m=ifrs_creds['aop_m'],
                                                                               dp=ifrs_creds['dp'],
                                                                               di=ifrs_creds['di'], dbt=dbt, start=i,
                                                                               pid=ifrs_creds['pid'], plist=self.plist,
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
                    dbt=dbt, i=i, stage2_st_date=stage2_st_date, repd=ifrs_creds['repd'], resd=ifrs_creds['resd'],
                    id_c=ifrs_creds['id_c'], dp=ifrs_creds['dp'], di=ifrs_creds['di'])

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
                """.format(dbt=dbt, repd=ifrs_creds['repd'], resd=ifrs_creds['resd'], id_c=ifrs_creds['id_c'],
                           anp_m=ifrs_creds['anp_m'], aop_m=ifrs_creds['aop_m'],
                           dp=ifrs_creds['dp'], di=ifrs_creds['di'], start=i, end=end_date)

                stg1 += x3
                stg2 += x3

                stg1 += " where t0.par_status='stage1' and nvl(t1.past6_stage,1)=1 and nvl(t2.past712_stage,1)!=3 group by t0.{repd}) ".format(
                    repd=ifrs_creds['repd'])
                stg2 += " where (t0.par_status='stage2' and nvl(t1.past6_stage,1)!=3) or (t0.par_status='stage1' and nvl(t1.past6_stage,1)=2) group by t0.{repd}) ".format(
                    repd=ifrs_creds['repd'])

            sql1 = p0 + stg1[5:] + "  order by {repd} ".format(repd=ifrs_creds['repd'])
            sql2 = p0 + stg2[5:] + "  order by {repd} ".format(repd=ifrs_creds['repd'])

        return sql1, sql2

    def obtain_data_from_sql(self):
        sql1, sql2 = self.calculate_metric()
        with self.connection:
            data1 = pd.read_sql(sql1, con=self.connection)
            data2 = pd.read_sql(sql2, con=self.connection)
            print('*' * 30)
            print(data1)
            print('*' * 30)
            print(data2)

        return data1, data2

    @classmethod
    def convert_data_to_json(cls, pd_df_list):
        pd_json_list_show = {}
        pd_json_list = {}
        for i, j in pd_df_list.items():
            pd_json_list_show[i] = [json.loads(df.reset_index().to_json(orient='records', date_format='iso')) for df in
                                    j]
            pd_json_list[i] = [df.to_json(orient='index') for df in j]

        return pd_json_list, pd_json_list_show

class LGD(MetricsCalculator):
    def __init__(self, db_credentials, plist, act_date):
        super().__init__(db_credentials)
        self.act_date = act_date
        self.plist = plist

    def calculate_metric(self):
        with self.connection:
            self.cursor.execute(""" ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS' """)

            # dbt = "portfolio_21"  # table name in the database
            dbt = database_table_name
            ifrs_creds = self.get_ifrs_data()

            ddate = pd.read_sql('select distinct act_date from {} order by act_date'.format(database_table_name),
                                con=self.connection)
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
            self.cursor.execute(temp_table_sql)
            self.connection.commit()

            p1 = "select * from "

            # p2 = ""

            for i in ddm.ACT_DATE[(ddm.ACT_DATE <= self.act_date)]:
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
                    btw1_date = stage_3_start + 1
                    btw2_date = stage_3_start + 30

                    p2_middle_generate += "when greatest({di}, {dp}) between {btw1_date} and {btw2_date} then '{i}_{btw1_date}_{btw2_date}'".format(
                        btw1_date=btw1_date, btw2_date=btw2_date, i=i, di=ifrs_creds['di'], dp=ifrs_creds['dp'])
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
                    group by t1.act_date, t1.par_status""".format(dbt=dbt, i=i, pid=ifrs_creds['pid'], plist=self.plist,
                                                                  di=ifrs_creds['di'], dp=ifrs_creds['dp'])

                p2 = p2_start + p2_middle_generate + p2_end
                self.cursor.execute(p2)
                self.connection.commit()

            self.cursor.execute('''
                ALTER TABLE shabzul2
                ADD cl NUMBER(38,7)
                ''')
            self.connection.commit()

            self.cursor.execute('''
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

        return sql

    def obtain_data_from_sql(self):
        sql = self.calculate_metric()
        with self.connection:
            data = pd.read_sql(sql, con=self.connection)
            return data
