from django.http import HttpResponse
from django.shortcuts import render

# import pandas as pd

FEATURES = ['DATE_OPER', 'REST_NEW', 'DATE_OPEN', 'DATE_PLANCLOSE', 'DATEOFBIRTH', 'OVERDUEDAY',
               'INTEREST_OVERDUEDAY', 'SUMMAAZN', 'SUMMA', 'SUMMA_19AZN', 'SUMMA_19', 'PROCAZN', 'PROC', 'PROCPROSAZN',
               'PROCPROS', 'SUMMAKREAZN', 'SUMMAKRE', 'PROCSTAVKRE', 'KOD1', 'LICSCHKRE', 'subaccount', 'cid', 'pid',
               'plist', 'wrof']


# def homepage(request):
#     return render(request, 'irfs/base.html')
#
#     # return HttpResponse()


def index(request):
    context = {'a': 'HelloWorld!'}
    return render(request, 'irfs/index.html', context)
    # return render(request, 'irfs/index.html')


# def predictMPG(request):
#     # print(request)
#     if request.method == 'POST':
#         print(request.POST.dict())
#     context = {'a': 'Score is: '}
#     return render(request, 'irfs/index.html', context)
#     # return render(request, 'irfs/index.html')

def predictMPG(request):
    if request.method == 'POST':

        values = [
            request.POST.get(value)
            for value in request.POST
            if value != 'csrfmiddlewaretoken'
        ]

        temp = dict(zip(FEATURES, values))
        print(temp)

    # testDtaa = pd.DataFrame({'x': temp}).transpose()
    # scoreval = reloadModel.predict(testDtaa)[0]
    # context = {'scoreval': scoreval, 'temp': temp}
    return render(request, 'irfs/index.html', context={})
