import datetime
from itertools import chain
import json
import psycopg2
import pyodbc
import pymysql
import cx_Oracle as co
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
import ast
from .script import IRFS
from .services import db_connection
import pprint
from .models import DatabaseCredentials, Ifrs, Plist
from .pd_script import pd_calculator
from .lgd import lgd_calculator
from .staging import staging_calculator
from .big_macro_func import big_macro_function


class DatabaseConnectionError(Exception):
    pass


PLIST_GLOBS = {
    'consumer': "(01801, 02201, 02203, 02800, 02801, 02803, 02805)",
    'corporate': "(01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002, 02004, 02009, 02014, 02017, 02100, 02102, 02103, 02201, 02203, 02300, 02304, 02400, 02600) and must_novu not like 'F%Z%K%'",
    'sole': "(01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002, 02004, 02009, 02014, 02017, 02100, 02102, 02103, 02300, 02304, 02400, 02600) and must_novu like 'F%Z%K%'"
}

FEATURES = ['DATE_OPER', 'REST_NEW', 'DATE_OPEN', 'DATE_PLANCLOSE', 'DATEOFBIRTH', 'OVERDUEDAY',
            'INTEREST_OVERDUEDAY', 'SUMMAAZN', 'SUMMA', 'SUMMA_19AZN', 'SUMMA_19', 'PROCAZN', 'PROC', 'PROCPROSAZN',
            'PROCPROS', 'SUMMAKREAZN', 'SUMMAKRE', 'PROCSTAVKRE', 'KOD1', 'LICSCHKRE', 'subaccount', 'cid', 'pid',
            'plist', 'wrof']


def connect(request):
    return render(request, 'irfs/db_conn.html')


def dbconn_view(request):
    if request.method == 'POST':
        if request.POST.get('db', False) and request.POST['host'] and request.POST['username'] and request.POST[
            'password'] and request.POST['db_name']:
            database = DatabaseCredentials()
            database.engine = request.POST.get('db', False)
            database.host = request.POST['host']
            database.username = request.POST['username']
            database.password = request.POST['password']
            database.dbname = request.POST['db_name']
            database.save()
            context = {'success': 'Database saved!'}
            return render(request, 'irfs/general.html', context=context)
        else:
            return render(request, 'irfs/general.html', {'error': 'All fields are required!'})
    else:
        return render(request, 'irfs/general.html')

    #     engine = request.POST.get('engine')
    #     host = request.POST.get('host')
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')
    #     dbname = request.POST.get('dbname')
    #     print('Obtained: ', engine, host, username, password, dbname)
    #     conn = db_connection(engine, username, password, host, dbname)
    #     print(conn)
    #     if conn is None:
    #         print('No connection established')
    #         raise DatabaseConnectionError('Error occurred when connecting to database')
    #     # request.session['connection'] = conn
    #
    # # print(request.session.get('connection'))
    # cursor = conn.cursor()
    # cursor.execute("SELECT * FROM persons")
    #
    # context = {'conn': cursor}
    #
    # return render(request, 'irfs/db_conn.html', context)


def homepage(request):
    return render(request, 'irfs/base.html')

    # return HttpResponse()


def general(request):
    return render(request, 'irfs/general.html')


def predictMPG(request):
    if request.method == 'POST':
        macros = Ifrs()
        macros.repd_start = request.POST.get('repd_start', '')
        macros.repd_end = request.POST.get('repd_end', '')
        macros.repd = request.POST.get('repd', '')
        macros.resd = request.POST.get('resd', '')
        macros.st_date = request.POST.get('st_date', '')
        macros.end_date = request.POST.get('end_date', '')
        macros.bthday = request.POST.get('bthday', '')
        macros.dp = request.POST.get('dp', '')
        macros.di = request.POST.get('di', '')
        macros.anp_m = request.POST.get('anp_m', '')
        macros.anp_c = request.POST.get('anp_c', '')
        macros.aop_m = request.POST.get('aop_m', '')
        macros.aop_c = request.POST.get('aop_c', '')
        macros.ani_m = request.POST.get('ani_m', '')
        macros.ani_c = request.POST.get('ani_c', '')
        macros.aoi_m = request.POST.get('aoi_m', '')
        macros.aoi_c = request.POST.get('aoi_c', '')
        macros.aor_m = request.POST.get('aor_m', '')
        macros.aor_c = request.POST.get('aor_c', '')
        macros.int_rate = request.POST.get('int_rate', '')
        macros.id_l = request.POST.get('id_l', '')
        macros.id_c = request.POST.get('id_c', '')
        macros.id_sub = request.POST.get('id_sub', '')
        macros.cid = request.POST.get('cid', '')
        macros.pid = request.POST.get('pid', '')
        macros.ctype = request.POST.get('ctype', '')
        macros.ptype = request.POST.get('ptype', '')
        # macros.plist_corp = request.POST.get('plist_corp', '')
        # macros.plist_cons = request.POST.get('plist_cons', '')
        # macros.plist_sole = request.POST.get('plist_sole', '')
        macros.wrof = request.POST.get('wrof', '')
        macros.save()
        context = {'success2': 'Saved successfully'}
        # temp = dict(zip(FEATURES, values))
        # print(temp)
        # result = IRFS.fake_score(temp, FEATURES)
        # testDtaa = pd.DataFrame({'x': temp}).transpose()
        # scoreval = reloadModel.predict(testDtaa)[0]
        # context = {'scoreval': scoreval, 'temp': temp}
        # context = {'result': result}
        return render(request, 'irfs/general.html', context=context)
    else:
        return render(request, 'irfs/general.html')


def calculate(request):
    if request.method == 'POST':
        pd_df_list = {}
        # pd_df_list = []
        queryset = Ifrs.objects.last()
        print(request.POST.get('repd_period', 'Salam necesen?'))
        if request.POST.get('repd_period') == 'yearly':
            # queryset.update(repd_start = queryset.repd_start + relativedelta(years=+1))
            # queryset.update(repd_end=queryset.repd_end + relativedelta(years=-1))
            repd_start = queryset.repd_start + relativedelta(years=+1)
            repd_end = queryset.repd_end + relativedelta(years=-1)
        elif request.POST.get('repd_period') == 'monthly':
            # queryset.update(repd_start=queryset.repd_start + relativedelta(months=+1))
            # queryset.update(repd_end=queryset.repd_end + relativedelta(months=-1))
            repd_start = queryset.repd_start + relativedelta(months=+1)
            repd_end = queryset.repd_end + relativedelta(months=-1)
        queryset.repd_period = request.POST.get('repd_period')
        repd_start = repd_start.strftime("%d-%b-%y")
        repd_end = repd_end.strftime("%d-%b-%y")
        print('repd start -> ', repd_start)
        print('repd end -> ', repd_end)
        queryset.save()
        values = [
            {key: value for key, value in Ifrs.objects.values()[0].items() if key != 'id'}
        ]
        print(values)
        queryset2 = DatabaseCredentials.objects
        db_credentials = {key: value for key, value in queryset2.values()[0].items() if key != 'id'}
        print(db_credentials)
        for i, j in PLIST_GLOBS.items():
            pd_df_list[i] = pd_calculator(db_credentials, values[0], j, repd_start, repd_end)
        # print('tut budet to wto nado')
        # print(pd_df_list['consumer'][0])
        # print(pd_df_list['consumer'][1])
        # for i in PLIST_GLOBS.values():
        #     pd_df_list.append(pd_calculator(db_credentials, values[0], i, repd_start, repd_end))
        pd_json_list_show = {}
        pd_json_list = {}
        for i, j in pd_df_list.items():
            pd_json_list_show[i] = [json.loads(df.reset_index().to_json(orient='records', date_format='iso')) for df in
                                    j]
            pd_json_list[i] = [df.to_json(orient='index') for df in j]
        # for i, j in pd_df_list.items():
        #     pd_json_list[i] = [df.to_json(orient='index') for df in j]

        '''
        {
        'concumer': [data1, data2],
        fsfsdf
        }
        '''
        # print(pd_json_list_show['consumer'][0])
        # print(pd_json_list_show['consumer'][1])
        request.session['pd_data_dict'] = pd_json_list
        print(request.session.get('pd_data_dict'))
        print('-' * 30)
        print(pd_json_list['consumer'][0])
        print('-' * 30)
        # dataframe1 = pd.DataFrame.from_dict(pd_json_list['consumer'][0], orient="records")
        dataframe2 = pd.read_json(pd_json_list['consumer'][0], orient='index')
        # print(dataframe1)
        print(dataframe2)
        smth = pd.to_datetime(dataframe2.ACT_DATE, unit='ms')
        print('here is smth')
        print(smth)
        dataframe2['ACT_DATE'] = smth
        print(dataframe2)

        # print(pd_df_list)
        # pd_df_1dlist = list(chain.from_iterable(pd_df_list))
        # pd_df_1dlist_html = [pd_df.to_html() for pd_df in pd_df_1dlist]
        # pd_jsons = [json.loads(df.reset_index().to_json(orient ='records')) for df in pd_df_1dlist]
        # df_html = pd_df_list[0][0].to_html()
        context = {'pd_json_list': pd_json_list_show}
        return render(request, 'irfs/pd.html', context=context)
        # return HttpResponse(df_html)
    else:
        return render(request, 'irfs/pd.html')


def plist_save(request):
    if request.method == 'POST':
        names = ast.literal_eval(str(request.POST.getlist('client_name')))
        codes = ast.literal_eval(str(request.POST.getlist('client_code')))
        # print(type(names), names)
        # print(type(codes), codes)

        plists = dict(zip(names, codes))
        # print(plists)
        for name, code in plists.items():
            plists = Plist()
            plists.name = name
            plists.product_code = code
            plists.save()

        context = {'pl_success': 'Plists saved successfully!'}

        return render(request, 'irfs/pd.html', context=context)

    return render(request, 'irfs/pd.html')


def upload(request):
    if request.method == 'POST':
        queryset = Ifrs.objects.last()
        uploaded_file = request.FILES['document']
        pd_data_dict = request.session.get('pd_data_dict')
        print(pd_data_dict)
        dataframe1 = pd.read_json(pd_data_dict['consumer'][0], orient='index')
        dataframe2 = pd.read_json(pd_data_dict['consumer'][1], orient='index')
        act_date1 = pd.to_datetime(dataframe1.ACT_DATE, unit='ms')
        act_date2 = pd.to_datetime(dataframe2.ACT_DATE, unit='ms')
        dataframe1['DATE_OPER'] = act_date1
        dataframe2['DATE_OPER'] = act_date2
        dataframe1.drop('ACT_DATE', axis=1, inplace=True)
        dataframe2.drop('ACT_DATE', axis=1, inplace=True)

        overall_pd_st1, overall_pd_st2, preds_st1, preds_st2 = big_macro_function(dataframe1, dataframe2, uploaded_file,
                                                                                  queryset.repd_period)
        print(overall_pd_st1, overall_pd_st2, preds_st1, preds_st2)
        context = {'overall_pd_st1': overall_pd_st1, 'overall_pd_st2': overall_pd_st2, 'preds_st1': preds_st1,
                   'preds_st2': preds_st2}
        return render(request, 'irfs/upload.html', context=context)

    return render(request, 'irfs/upload.html')
    # queryset = Ifrs.objects
    # values = [
    #     { key: value for key, value in queryset.values()[0].items() if key != 'id'}
    # ]
    # # print(values[0])
    # queryset2 = DatabaseCredentials.objects
    # db_credentials = {key: value for key, value in queryset2.values()[0].items() if key != 'id'}
    #
    # pd_calculator(db_credentials, values[0])
    # # print(db_dict)
    # # db_credentials = 'ruqiyye_bedirova/ruqiyye03@192.168.0.17:1521/bank'
    # context = {'queryset': queryset}
    # return render(request, 'irfs/pd.html', context=context)


def lgd(request):
    if request.method == 'POST':
        rec_per = int(request.POST.get('rec_per'))
        print(rec_per)
        print(type(rec_per))
        lgd_df_list = {}
        queryset2 = DatabaseCredentials.objects
        db_credentials = {key: value for key, value in queryset2.values()[0].items() if key != 'id'}
        values = [
            {key: value for key, value in Ifrs.objects.values()[0].items() if key != 'id'}
        ]

        queryset = Ifrs.objects.last()
        repd_rec_date = queryset.repd_end + relativedelta(months=rec_per)
        print(repd_rec_date)
        repd_rec_date_ns = repd_rec_date.strftime("%d-%b-%y")
        print(repd_rec_date_ns)

        for i, j in PLIST_GLOBS.items():
            lgd_df_list[i] = lgd_calculator(db_credentials, values[0], j, repd_rec_date_ns)

        print(lgd_df_list)
        return render(request, 'irfs/lgd.html')

    return render(request, 'irfs/lgd.html')


def staging(request):
    if request.method == 'POST':
        queryset2 = DatabaseCredentials.objects
        db_credentials = {key: value for key, value in queryset2.values()[0].items() if key != 'id'}
        values = [
            {key: value for key, value in Ifrs.objects.values()[0].items() if key != 'id'}
        ]

        queryset = Ifrs.objects.last()
        repd_end = queryset.repd_end.strftime("%d-%b-%y")
        stage_data = staging_calculator(db_credentials, values[0], repd_end)
        print(stage_data)
        return render(request, 'irfs/staging.html')

    return render(request, 'irfs/staging.html')

