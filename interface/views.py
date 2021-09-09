import json
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
import pandas as pd
import ast
from .models import DatabaseCredentials, Ifrs, Plist, LGD, LGD_DF, PD_UPD, STAGING
from .pd_script import pd_calculator
from .lgd2 import lgd_calculator
from .staging import staging_calculator
from .big_macro_func import big_macro_function
from .ecl import ecl_calculator
from .mehsul_calc_script import mehsul_adding
from .config import username, PLIST_GLOBS
from .Metrics_Interface import PD


class DatabaseConnectionError(Exception):
    pass


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

        return render(request, 'irfs/general.html', context=context)
    else:
        return render(request, 'irfs/general.html')


def calculate(request):
    if request.method == 'POST':
        pd_df_list = {}
        queryset = Ifrs.objects.last()
        repd_start, repd_end = PD.repd_period(queryset=queryset, repd_period=request.POST.get('repd_period'))
        queryset2 = DatabaseCredentials.objects.last()
        pd_pl_list = request.session.get('pd_plist')

        for pd_pl_name, pd_pl_code in pd_pl_list.items():
            pd_obj = PD(queryset2, pd_pl_code, repd_start, repd_end)
            pd_df_list[pd_pl_name] = pd_obj.calculate_metric()

        pd_json_list, pd_json_list_show = PD.convert_data_to_json(pd_df_list)
        request.session['pd_data_dict'] = pd_json_list
        context = {'pd_json_list': pd_json_list_show}
        return render(request, 'irfs/pd.html', context=context)
    else:
        pd_list = PLIST_GLOBS
        return render(request, 'irfs/pd.html', context={'pd_list': pd_list})


def pd_plist_save(request):
    if request.method == 'POST':
        names = ast.literal_eval(str(request.POST.getlist('pd_client_name')))
        codes = ast.literal_eval(str(request.POST.getlist('pd_client_code')))
        # print(type(names), names)
        # print(type(codes), codes)

        plists = dict(zip(names, codes))
        # print(plists)
        # haven_plists = Plist.objects.all()
        # for name, code in plists.items():
        #     filtered = haven_plists.filter(measure='pd', name=name)
        #     if filtered:
        #         filtered.update(product_code=code)
        #     else:
        #         plists = Plist()
        #         plists.name = name
        #         plists.product_code = code
        #         plists.measure = 'pd'
        #         plists.save()
        request.session['pd_plist'] = plists
        print(request.session.get('pd_plist'))

        context = {'pl_success': 'Plists saved successfully!'}

        return render(request, 'irfs/pd.html', context=context)

    return render(request, 'irfs/pd.html')


def lgd_plist_save(request):
    if request.method == 'POST':
        names = ast.literal_eval(str(request.POST.getlist('lgd_client_name')))
        codes = ast.literal_eval(str(request.POST.getlist('lgd_client_code')))
        # print(type(names), names)
        # print(type(codes), codes)

        plists = dict(zip(names, codes))
        # haven_plists = Plist.objects.all()
        # # print(plists)
        # for name, code in plists.items():
        #     filtered = haven_plists.filter(measure='lgd', name=name)
        #     if filtered:
        #         filtered.update(product_code=code)
        #     else:
        #         plists = Plist()
        #         plists.name = name
        #         plists.product_code = code
        #         plists.measure = 'lgd'
        #         plists.save()
        request.session['lgd_plist'] = plists
        print(request.session.get('lgd_plist'))

        context = {'pl_success': 'Plists saved successfully!'}

        return render(request, 'irfs/lgd.html', context=context)

    return render(request, 'irfs/lgd.html')


def macro_calc(pd_data):
    data = pd.read_json(pd_data, orient='index')
    act_date = pd.to_datetime(data.ACT_DATE, unit='ms')
    data['DATE_OPER'] = act_date
    data.drop('ACT_DATE', axis=1, inplace=True)
    return data


def upload(request):
    if request.method == 'POST':
        queryset = Ifrs.objects.last()
        uploaded_file = request.FILES['document']
        pd_data_dict = request.session.get('pd_data_dict')
        print(pd_data_dict)
        macro_df_list = {}
        pd_pl_list = request.session.get('pd_plist')
        for pd_pl_name in pd_pl_list.keys():
            if pd_pl_name == 'corporate':  # TEMPORARY CONDITION FOR PORTFOLIO_21
                continue
            dataframe1 = macro_calc(pd_data_dict[pd_pl_name][0])
            dataframe2 = macro_calc(pd_data_dict[pd_pl_name][1])
            final_macro_df = big_macro_function(dataframe1, dataframe2,
                                                uploaded_file,
                                                queryset.repd_period)
            macro_df_list[pd_pl_name] = final_macro_df
            print(final_macro_df)

        datafile_pd = PD_UPD()
        datafile_pd.macro_data = macro_df_list
        datafile_pd.save()

        # macro_json_list = {}
        # for i, j in macro_df_list.items():
        #     macro_json_list[i] = [df.to_json(orient='index') for df in j]

        # request.session['macro_data_dict'] = macro_json_list
        # print(request.session.get('macro_data_dict'))

        # dataframe1 = pd.read_json(pd_data_dict['consumer'][0], orient='index')
        # dataframe2 = pd.read_json(pd_data_dict['consumer'][1], orient='index')
        # act_date1 = pd.to_datetime(dataframe1.ACT_DATE, unit='ms')
        # act_date2 = pd.to_datetime(dataframe2.ACT_DATE, unit='ms')
        # dataframe1['DATE_OPER'] = act_date1
        # dataframe2['DATE_OPER'] = act_date2
        # dataframe1.drop('ACT_DATE', axis=1, inplace=True)
        # dataframe2.drop('ACT_DATE', axis=1, inplace=True)
        #
        # overall_pd_st1, overall_pd_st2, preds_st1, preds_st2 = big_macro_function(dataframe1, dataframe2, uploaded_file,
        #                                                                           queryset.repd_period)
        # print(overall_pd_st1, overall_pd_st2, preds_st1, preds_st2)
        # context = {'overall_pd_st1': overall_pd_st1, 'overall_pd_st2': overall_pd_st2, 'preds_st1': preds_st1,
        #            'preds_st2': preds_st2}
        return render(request, 'irfs/upload.html')

    datapd = PD_UPD.objects.last()
    print(datapd.macro_data)
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
        queryset2 = DatabaseCredentials.objects.filter(username=username)[0]
        # db_credentials = {key: value for key, value in queryset2.values()[0].items() if key != 'id'}
        values = [
            {key: value for key, value in Ifrs.objects.values()[0].items() if key != 'id'}
        ]

        queryset = Ifrs.objects.last()
        repd_rec_date = queryset.repd_end + relativedelta(months=rec_per)
        print(repd_rec_date)
        repd_rec_date_ns = repd_rec_date.strftime("%d-%b-%y")
        print(repd_rec_date_ns)

        # for i, j in PLIST_GLOBS.items():
        #     lgd_df_list[i] = lgd_calculator(db_credentials, values[0], j, repd_rec_date_ns)
        # for pd_pl_name, pd_pl_code in pd_pl_list:
        #     pd_df_list[pd_pl_name] = pd_calculator(db_credentials, values[0], pd_pl_code, repd_start,
        #                                            repd_end)
        lgd_pl_list = request.session.get('lgd_plist')
        for lgd_pl_name, lgd_pl_code in lgd_pl_list.items():
            lgd_df_list[lgd_pl_name] = lgd_calculator(queryset2, values[0], lgd_pl_code,
                                                      repd_rec_date_ns)
        datafile_lgd = LGD()
        datafile_lgd.data_dict = lgd_df_list
        datafile_lgd.save()

        # lgd_json_list = {}
        # for i, j in lgd_df_list.items():
        #     lgd_json_list[i] = [df.to_json(orient='index') for df in j]

        print(lgd_df_list)

        print('Here some tests')
        list_of_lgds = []
        for i, j in lgd_df_list.items():
            j['PRODUCT'] = i
            lgd_df_list[i] = j
            list_of_lgds.append(j)

        print('lgd df list after transformation')
        print(lgd_df_list)
        # newdf = j.insert(1, 'PRODUCT', i)
        # print(newdf)
        # list_of_lgds.append(newdf)

        print(list_of_lgds)

        final_lgd = pd.concat(list_of_lgds, axis=0)
        print(final_lgd)
        # user = settings.DATABASES['default']['USER']
        # password = settings.DATABASES['default']['PASSWORD']
        # database_name = settings.DATABASES['default']['NAME']
        #
        # sqlite3.connect(database_name)
        # engine = create_engine(database_url, echo=False)

        # entries = []
        # for e in final_lgd.T.to_dict().values():
        #     entries.append(LGD(**e))
        # LGD.objects.bulk_create(entries)
        datafile = LGD_DF()

        datafile.data = final_lgd
        datafile.save()

        return render(request, 'irfs/lgd.html')

    dataf = LGD_DF.objects.last()
    print(dataf.data)
    # lgd_list = Plist.objects.filter(measure='lgd')
    lgd_list = PLIST_GLOBS
    return render(request, 'irfs/lgd.html', context={'lgd_list': lgd_list})


def staging(request):
    if request.method == 'POST':
        queryset2 = DatabaseCredentials.objects.filter(username=username)[0]
        # db_credentials = {key: value for key, value in queryset2.values()[0].items() if key != 'id'}
        values = [
            {key: value for key, value in Ifrs.objects.values()[0].items() if key != 'id'}
        ]

        queryset = Ifrs.objects.last()
        repd_end = queryset.repd_end.strftime("%d-%b-%y")
        stage_data = staging_calculator(queryset2, values[0], repd_end)
        print(stage_data)
        stage_data_json = stage_data.to_json(orient='index')
        request.session['stage_data_json'] = stage_data_json

        return render(request, 'irfs/staging.html')

    return render(request, 'irfs/staging.html')


def ecl(request):
    if request.method == 'POST':
        # db_credentials = {key: value for key, value in DatabaseCredentials.objects.values()[0].items() if key != 'id'}
        portfolio = mehsul_adding(DatabaseCredentials.objects.filter(username=username)[0], PLIST_GLOBS)

        print(request.POST)
        print(request.POST.getlist('pd_list'))
        names = ast.literal_eval(str(request.POST.getlist('client_name')))
        pd_s = ast.literal_eval(str(request.POST.getlist('pd_list')))
        lgd_s = ast.literal_eval(str(request.POST.getlist('lgd_list')))
        pd_names = dict(zip(names, pd_s))
        lgd_names = dict(zip(names, lgd_s))
        datapd = PD_UPD.objects.last().macro_data
        lgds = LGD.objects.last().data_dict
        print(pd_names)
        print(datapd)
        print(lgds)
        obtained_pd_dict = {}
        for pd_prod_name, pd_name in pd_names.items():
            obtained_pd_dict[pd_prod_name] = datapd[pd_name]

        obtained_lgd_dict = {}
        for lgd_prod_name, lgd_name in lgd_names.items():
            obtained_lgd_dict[lgd_prod_name] = lgds[lgd_name]

        print('Here is obtainations ')
        print(obtained_pd_dict)
        print(obtained_lgd_dict)
        staging = request.session.get('stage_data_json')
        staging_df = pd.read_json(staging, orient='index')
        ecl_calculator(obtained_pd_dict, obtained_lgd_dict, staging_df, pd_names, lgd_names, portfolio)
        # plists = Plist.objects.all()
        # print(request.POST)
        # names = ast.literal_eval(str(request.POST.getlist('client_name')))
        # plists_list = ast.literal_eval(str(request.POST.getlist('plist')))
        # plist_dict = dict(zip(names, plists_list))
        # print(plist_dict)
        # plist_dict_with_prod_codes = {}
        # for i, j in plist_dict.items():
        #     plist_dict_with_prod_codes[i] = Plist.objects.filter(measure=j.split('_')[0], name=j.split('_')[1])[0].product_code
        #
        # print(plist_dict_with_prod_codes)
        #
        # # plist_codes = [code for code in Plist.objects.filter(measure=plists_list, name=name)]
        # # print(request.POST)
        return render(request, 'irfs/ecl.html')

    pd_list = PD_UPD.objects.last().macro_data

    lgd_list = LGD.objects.last().data_dict

    return render(request, 'irfs/ecl.html', context={'pd_list': pd_list, 'lgd_list': lgd_list})
