from rest_framework import generics
from rest_framework.response import Response

from .serializers import DatabaseConnectionSerializer
# import psycopg2
# import pyodbc
# import pymysql
# import cx_Oracle as co
#
# from django.http import HttpResponse
# from django.shortcuts import render
#
# from .script import IRFS
# from .services import db_connection
#
#
# class DatabaseConnectionError(Exception):
#     pass
#
#
# FEATURES = ['DATE_OPER', 'REST_NEW', 'DATE_OPEN', 'DATE_PLANCLOSE', 'DATEOFBIRTH', 'OVERDUEDAY',
#             'INTEREST_OVERDUEDAY', 'SUMMAAZN', 'SUMMA', 'SUMMA_19AZN', 'SUMMA_19', 'PROCAZN', 'PROC', 'PROCPROSAZN',
#             'PROCPROS', 'SUMMAKREAZN', 'SUMMAKRE', 'PROCSTAVKRE', 'KOD1', 'LICSCHKRE', 'subaccount', 'cid', 'pid',
#             'plist', 'wrof']
#
#
# def connect(request):
#     return render(request, 'irfs/db_conn.html')
#
#
# def dbconn_view(request):
#     if request.method == 'POST':
#         engine = request.POST.get('engine')
#         host = request.POST.get('host')
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         dbname = request.POST.get('dbname')
#         print('Obtained: ', engine, host, username, password, dbname)
#         conn = db_connection(engine, username, password, host, dbname)
#         print(conn)
#         if conn is None:
#             print('No connection established')
#             raise DatabaseConnectionError('Error occurred when connecting to database')
#         # request.session['connection'] = conn
#
#     # print(request.session.get('connection'))
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM persons")
#
#     context = {'conn': cursor}
#
#     return render(request, 'irfs/db_conn.html', context)
#
#
# def homepage(request):
#     return render(request, 'irfs/base.html')
#
#     # return HttpResponse()
#
#
# def general(request):
#     return render(request, 'irfs/general.html')
#
#
# def predictMPG(request):
#     if request.method == 'POST':
#         values = [
#             request.POST.get(value)
#             for value in request.POST
#             if value != 'csrfmiddlewaretoken'
#         ]
#
#         temp = dict(zip(FEATURES, values))
#         # print(temp)
#         result = IRFS.fake_score(temp, FEATURES)
#     # testDtaa = pd.DataFrame({'x': temp}).transpose()
#     # scoreval = reloadModel.predict(testDtaa)[0]
#     # context = {'scoreval': scoreval, 'temp': temp}
#     context = {'result': result}
#     return render(request, 'irfs/general.html', context=context)


class DatabaseLogin(generics.GenericAPIView):
    serializer_class = DatabaseConnectionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "success": "Database connected successfully"
        })