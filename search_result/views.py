from django.shortcuts import render
import cx_Oracle
import os
import numpy as np
from pyavrophonetic import avro
from django.core.paginator import Paginator

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.
def search_result(request):
    query = request.GET.get('search')

    querar = query.split("/?page=")
    shape = np.asarray(querar).shape[0]

    if shape == 1:
        query = querar[0]
        page_num = 1
    else:
        query = querar[0]
        page_num = querar[1]
    print(request.GET)
    print(page_num)
    print(query)

    dict = {'logged_in': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = True
    dict['search_result'] = get_book_info(query)

    P = Paginator(dict['search_result'], 9)

    try:
        page = P.page(page_num)
    except EmptyPage:
        page = P.page(1)

    dict2 = {'logged_in' : dict['logged_in'], 'search_result': page, 'query' : query}
    print(dict2)
    return render(request, "search_result/search_result.html", dict2)

def get_book_info(query):
    if is_banglish(query):
        #print(avro.parse(query))
        query = avro.parse(query)
    quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE,B.RATINGS,C.PUBLISHER_NAME FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) JOIN PUBLISHER C USING(PUBLISHER_ID) WHERE  ((B.BOOK_NAME LIKE '%" + query + "%') OR (A.AUTHOR_NAME LIKE '%" + query + "%') OR (C.PUBLISHER_NAME LIKE '%" + query + "%')) ORDER BY B.TOTAL_SOLD DESC"
    #print(quercmd)
    #print(query)
    db_cursor = conn.cursor()
    db_cursor.execute(quercmd)

    search_results = db_cursor.fetchall()
    li = []

    for row in search_results:
        l2 = []
        for item in row:
            l2.append(item)
        l2[1] = slice_name(l2[1])
        if check_if_image_exists(l2[0]):
            l2.append(l2[0])
        else:
            l2.append("book_image")
        #print(l2)
        li.append(l2)
    return li


def check_if_image_exists(id):
    nam = 'static/images/rokomariapp/images/' + str(id) + '.jpg'
    if os.path.isfile(nam):
        return True
    return False


def slice_name(str):
    ret = ""
    for i in range(len(str)):
        if str[i] == ':' or str[i] == '(':
            break
        ret += str[i]
    return ret

def is_banglish(query):
    banglish = False
    for letter in query:
        if(letter >= 'a' and letter <= 'z') or (letter >= 'A' and letter <= 'Z') or (letter >= '0' and letter <= '9'):
            banglish = True
            break
    return banglish