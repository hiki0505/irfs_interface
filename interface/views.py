from django.http import HttpResponse
from django.shortcuts import render


def homepage(request):
    return render(request, 'irfs/base.html')

    # return HttpResponse()


def general(request):
    return render(request, 'irfs/general.html')


def predictMPG(request):
    if request.method == 'POST':
        temp = {}
        temp['repd'] = request.POST.get('dateoper')
        temp['resd'] = request.POST.get('restnew')
        temp['st_date'] = request.POST.get('dateopen')
        temp['end_date'] = request.POST.get('dateplancode')
        temp['bthday'] = request.POST.get('dateofbirth')
        temp['dp'] = request.POST.get('overdueday')
        temp['di'] = request.POST.get('interestoverdueday')
        temp['anp_m'] = request.POST.get('summaazn')
        temp['anp_c'] = request.POST.get('summa')
        temp['aop_m'] = request.POST.get('summa19azn')
        temp['aop_c'] = request.POST.get('summa19')
        temp['ani_m'] = request.POST.get('procazn')
        temp['ani_c'] = request.POST.get('proc')
        temp['aoi_m'] = request.POST.get('procprosazn')
        temp['aoi_c'] = request.POST.get('procpros')
        temp['aor_m'] = request.POST.get('summakreazn')
        temp['aor_c'] = request.POST.get('summakre')
        temp['int_rate'] = request.POST.get('procstavkre')
        temp['id_l'] = request.POST.get('kod1')
        temp['id_c'] = request.POST.get('licschkre')
        temp['id_sub'] = request.POST.get('subaccount')
        temp['cid'] = request.POST.get('cid')
        temp['pid'] = request.POST.get('pid')
        temp['plist'] = request.POST.get('plist')
        temp['wrof'] = request.POST.get('wrof')
        # temp2 = temp.copy()
        # temp2['model year'] = temp['model_year']
        # print(temp.keys(), temp2.keys())
        # # del temp2['model_year']

    testDtaa = pd.DataFrame({'x': temp2}).transpose()
    scoreval = reloadModel.predict(testDtaa)[0]
    context = {'scoreval': scoreval, 'temp': temp}
    return render(request, 'irfs/general.html', context)
