# import connection_url
import psycopg2
import pyodbc
import pymysql
import cx_Oracle as co
from .models import Ifrs


def db_connection(engine, username, password, host, db_name):
    conn = None
    if engine == 'postgres':
        conn = psycopg2.connect(host=host, database=db_name, user=username, password=password)
    elif engine == 'pymysql':
        conn = pymysql.connect(host=host, user=username, password=password, database=db_name)
    elif engine == 'pyodbc':
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+host+';DATABASE='+db_name+';UID='+username+';PWD='+password)
    elif engine == 'oracle':
        conn_str = u'{}/{}@{}/{}'.format(username, password, host, db_name)  # db_name here stands for service
        conn = co.connect(conn_str)

    return conn


def get_ifrs_data():
    ifrs_dict = {}

    for field in Ifrs._meta.fields:
        field_name = field.name
        # field_object = Ifrs._meta.get_field(field_name)
        # field_value = field_object.value_from_object(Ifrs.objects.last())
        obj = Ifrs.objects.last()
        field_value = getattr(obj, field_name)
        ifrs_dict[field_name] = field_value

    return ifrs_dict
    # repd = ifrs_creds['repd']  # report date for the portfolio
    # resd = ifrs_creds['resd']  # date of restructuring
    # st_date = ifrs_creds['st_date']  # loan origination date
    # end_date = ifrs_creds['end_date']  # contractual loan maturity date
    # bthday = ifrs_creds['bthday']
    #
    # dp = ifrs_creds['dp']  # days principal is past due
    # di = ifrs_creds['di']  # days interest is past due
    #
    # anp_m = ifrs_creds['anp_m']  # normal principal amount in manats
    # anp_c = ifrs_creds['anp_c']  # normal principal amount in currency
    # aop_m = ifrs_creds['aop_m']  # overdue principal amount in manats
    # aop_c = ifrs_creds['aop_c']  # overdue principal amount in currency
    #
    # ani_m = ifrs_creds['ani_m']  # normal interest amount in manats
    # ani_c = ifrs_creds['ani_c']  # normal interest amount in currency
    # aoi_m = ifrs_creds['aoi_m']  # overdue interest amount in manats
    # aoi_c = ifrs_creds['aoi_c']  # overdue interest amount in currency
    #
    # aor_m = ifrs_creds['aor_m']  # original amount in manats
    # aor_c = ifrs_creds['aor_c']  # original amount in currency
    #
    # id_l = ifrs_creds['id_l']  # contract (loan) ID which is client id here
    # id_c = ifrs_creds['id_c']  # client ID
    # id_sub = ifrs_creds['id_sub']  # subaccount (order of loan)
    #
    # # bid = "debt_standard_gl_acct_no" # balance account No
    # cid = ifrs_creds['cid']  # currency ID (or name)
    # pid = ifrs_creds['pid']  # product ID or name
    # ctype = ifrs_creds['ctype']  # customer type, individual or legal
    # ptype = ifrs_creds['ptype']  # payment type, annuity for these purposes


