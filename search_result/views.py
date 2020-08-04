from django.shortcuts import render
import cx_Oracle
import os

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.
def search_result(request):
    print("Req Aise")
    print(request)
    print(request.POST)
    print(request.GET)
    return render(request, "search_result/search_result.html")