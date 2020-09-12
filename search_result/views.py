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
    # print(request.POST.get("price"), "post method", request.method)
    querar = query.split("/?page=")
    shape = np.asarray(querar).shape[0]

    if shape == 1:
        query = querar[0]
        page_num = 1
    else:
        query = querar[0]
        page_num = querar[1]
    # print(request.GET)
    # print(page_num)
    # print(query)

    dict = {'logged_in': False, 'is_admin': False}

    if request.session.has_key('is_admin'):
        dict['logged_in'] = get_user_name_admin(request.session['user_id'])
        dict['is_admin'] = True
    elif request.session.has_key('user_id'):
        dict['logged_in'] = get_user_name(request.session['user_id'])
    if request.method == "GET":
        dict['search_result'] = get_book_info(query, "GET")
        # print("GET er vitor")
    elif request.method == "POST":
        price_from = request.POST.get("price_from")
        price_to = request.POST.get("price_to")
        rating_from = request.POST.get("rating_from")
        rating_to = request.POST.get("rating_to")
        sort = request.POST.get("sort")
        if price_from == '':
            price_from = 0
        if price_to == '':
            price_to = 50000
        if rating_from == '':
            rating_from = 0
        if rating_to == '':
            rating_to = 5
        if sort == None:
            sort = "TOTAL_SOLD DESC"
        price_from = int(float(price_from))
        price_to = int(float(price_to))
        rating_from = int(float(rating_from))
        rating_to = int(float(rating_to))
        # print(price_from, price_to, rating_from, rating_to, sort)
        dict['search_result'] = get_book_info(query, "POST", price_from, price_to, rating_from, rating_to, sort)
        dict['query'] = query
        return render(request, "search_result/search_result.html", dict)
        # print("POST er vitor", price_from, price_to)

    P = Paginator(dict['search_result'], 9)

    try:
        page = P.page(page_num)
    except EmptyPage:
        page = P.page(1)

    dict2 = {'logged_in': dict['logged_in'], 'search_result': page, 'query': query}
    # print(dict2)
    return render(request, "search_result/search_result.html", dict2)


def get_book_info(query, method, price_from=0, price_to=50000, rating_from=0, rating_to=5, sort="TOTAL_SOLD DESC"):
    if is_banglish(query):
        # print(avro.parse(query))
        query = avro.parse(query)
    # print(sort)
    if method == "GET":
        quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE,B.RATINGS,C.PUBLISHER_NAME, B.DISCOUNT FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) JOIN PUBLISHER C USING(PUBLISHER_ID) WHERE  ((B.BOOK_NAME LIKE '%" + query + "%') OR (A.AUTHOR_NAME LIKE '%" + query + "%') OR (C.PUBLISHER_NAME LIKE '%" + query + "%') OR (B.BOOK_GENRE LIKE '%" + query + "%')) ORDER BY B.TOTAL_SOLD DESC"
    elif method == "POST":
        quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE,B.RATINGS,C.PUBLISHER_NAME, B.DISCOUNT FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) JOIN PUBLISHER C USING(PUBLISHER_ID) WHERE  ((B.PRICE >= " + str(
            price_from) + " AND B.PRICE <= " + str(price_to) + " AND B.RATINGS >= " + str(
            rating_from) + " AND B.RATINGS <= " + str(
            rating_to) + ") AND ((B.BOOK_NAME LIKE '%" + query + "%') OR (A.AUTHOR_NAME LIKE '%" + query + "%') OR (C.PUBLISHER_NAME LIKE '%" + query + "%')OR (B.BOOK_GENRE LIKE '%" + query + "%'))) ORDER BY B." + sort
    # print(quercmd)
    # print(query)
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
            # print(l2)
        else:
            l2.append("book_image")
        # print(l2)
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
        if (letter >= 'a' and letter <= 'z') or (letter >= 'A' and letter <= 'Z') or (letter >= '0' and letter <= '9'):
            banglish = True
            break
    return banglish


def get_user_name(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM CUSTOMER WHERE USER_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])

def get_user_name_admin(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM ADMIN WHERE ADMIN_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])
