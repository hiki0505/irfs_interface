import psycopg2
import pyodbc
import pymysql
import cx_Oracle as co

from django.http import HttpResponse
from django.shortcuts import render

from .script import IRFS
from .services import db_connection
from .models import DatabaseCredentials, Ifrs
from .pd_script import pd_calculator
class DatabaseConnectionError(Exception):
    pass


FEATURES = ['DATE_OPER', 'REST_NEW', 'DATE_OPEN', 'DATE_PLANCLOSE', 'DATEOFBIRTH', 'OVERDUEDAY',
            'INTEREST_OVERDUEDAY', 'SUMMAAZN', 'SUMMA', 'SUMMA_19AZN', 'SUMMA_19', 'PROCAZN', 'PROC', 'PROCPROSAZN',
            'PROCPROS', 'SUMMAKREAZN', 'SUMMAKRE', 'PROCSTAVKRE', 'KOD1', 'LICSCHKRE', 'subaccount', 'cid', 'pid',
            'plist', 'wrof']


def connect(request):
    return render(request, 'irfs/db_conn.html')


def dbconn_view(request):
    if request.method == 'POST':
        if request.POST.get('db', False) and request.POST['host'] and request.POST['username'] and request.POST['password'] and request.POST['db_name']:
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
        macros.plist = request.POST.get('plist', '')
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


def calculate_pd(request):
    queryset = Ifrs.objects
    # print(queryset.values()[0])
    # for i, j in queryset.values()[0].items():
    #     print(i, j)
        # if i == 'id':
        #     continue
    # values = [
    #     { key: value }
    #     for key, value in queryset.values()[0].items()
    #     if key != 'id'
    # ]
    values = [
        { key: value for key, value in queryset.values()[0].items() if key != 'id'}
    ]
    # print(values[0])
    queryset2 = DatabaseCredentials.objects
    db_credentials = {key: value for key, value in queryset2.values()[0].items() if key != 'id'}

    pd_calculator(db_credentials, values[0])
    # print(db_dict)
    # db_credentials = 'ruqiyye_bedirova/ruqiyye03@192.168.0.17:1521/bank'
    context = {'queryset': queryset}
    return render(request, 'irfs/pd.html', context=context)