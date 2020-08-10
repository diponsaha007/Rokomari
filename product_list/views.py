from django.shortcuts import render
import cx_Oracle
import os
import numpy as np
from pyavrophonetic import avro
from django.core.paginator import Paginator

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.
def product_list_author(request, query):
    x = request.META['QUERY_STRING']
    querar = x.split("page=")
    shape = np.asarray(querar).shape[0]

    if shape == 1:
        page_num = 1
    else:
        page_num = querar[1]


    dict = {'logged_in': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = True
    dict['classify'] = "এর"
    dict['name'] = query
    dict['type'] = "A.AUTHOR_NAME"
    dict['is_author'] = True
    dict['is_genre'] = False
    dict['is_publisher'] = False


    if request.method == "POST":
        price_from = request.POST.get("price_from")
        price_to = request.POST.get("price_to")
        rating_from = request.POST.get("rating_from")
        rating_to = request.POST.get("rating_to")
        sort = request.POST.get("sort")
        if price_from=='':
            price_from = 0
        if price_to=='':
            price_to = 50000
        if rating_from=='':
            rating_from = 0
        if rating_to=='':
            rating_to = 5
        if sort== None:
            sort = "TOTAL_SOLD DESC"
        price_from = int(float(price_from))
        price_to = int(float(price_to))
        rating_from = int(float(rating_from))
        rating_to = int(float(rating_to))
        #print(price_from, price_to, rating_from, rating_to, sort)
        dict['search_result'], dict['summary'] = get_book_info(query, "POST", dict['type'], price_from, price_to, rating_from, rating_to,sort)
        return render(request, "product_list/product_list.html", dict)


    else:
        dict['search_result'], dict['summary'] = get_book_info(query, "GET", dict['type'])


    P = Paginator(dict['search_result'], 9)

    try:
        page = P.page(page_num)
    except EmptyPage:
        page = P.page(1)
    print(dict['summary'])
    dict2 = {'logged_in' : dict['logged_in'], 'search_result': page,  'name' : query, 'classify' : 'এর', 'is_author' : True, 'is_genre' : False , 'is_publication' : False ,  type : "A.AUTHOR_NAME", 'summary' : dict['summary']}

    return render(request, "product_list/product_list.html", dict2)

def product_list_genre(request, query):
    x = request.META['QUERY_STRING']
    querar = x.split("page=")
    shape = np.asarray(querar).shape[0]

    if shape == 1:
        page_num = 1
    else:
        page_num = querar[1]


    dict = {'logged_in': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = True
    dict['classify'] = "জন্রা'র"
    dict['name'] = query
    dict['type'] = "B.BOOK_GENRE"
    dict['is_author'] = False
    dict['is_genre'] = True
    dict['is_publisher'] = False


    if request.method == "POST":
        price_from = request.POST.get("price_from")
        price_to = request.POST.get("price_to")
        rating_from = request.POST.get("rating_from")
        rating_to = request.POST.get("rating_to")
        sort = request.POST.get("sort")
        if price_from=='':
            price_from = 0
        if price_to=='':
            price_to = 50000
        if rating_from=='':
            rating_from = 0
        if rating_to=='':
            rating_to = 5
        if sort== None:
            sort = "TOTAL_SOLD DESC"
        price_from = int(float(price_from))
        price_to = int(float(price_to))
        rating_from = int(float(rating_from))
        rating_to = int(float(rating_to))
        dict['search_result'], dict['summary'] = get_book_info(query, "POST", dict['type'], price_from, price_to, rating_from, rating_to,sort)
        return render(request, "product_list/product_list.html", dict)


    else:
        dict['search_result'], dict['summary'] = get_book_info(query, "GET", dict['type'])


    P = Paginator(dict['search_result'], 9)

    try:
        page = P.page(page_num)
    except EmptyPage:
        page = P.page(1)
    print(dict['summary'])
    dict2 = {'logged_in' : dict['logged_in'], 'search_result': page,  'name' : query, 'classify' : "জন্রা'র", 'is_author' : False, 'is_genre' : True , 'is_publication' : False ,  type : "A.AUTHOR_NAME", 'summary' : dict['summary']}

    return render(request, "product_list/product_list.html", dict2)

def product_list_publisher(request, query):
    x = request.META['QUERY_STRING']
    querar = x.split("page=")
    shape = np.asarray(querar).shape[0]

    if shape == 1:
        page_num = 1
    else:
        page_num = querar[1]


    dict = {'logged_in': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = True
    dict['classify'] = "এর"
    dict['name'] = query
    dict['type'] = "C.PUBLISHER_NAME"
    dict['is_author'] = False
    dict['is_genre'] = False
    dict['is_publisher'] = True


    if request.method == "POST":
        price_from = request.POST.get("price_from")
        price_to = request.POST.get("price_to")
        rating_from = request.POST.get("rating_from")
        rating_to = request.POST.get("rating_to")
        sort = request.POST.get("sort")
        if price_from=='':
            price_from = 0
        if price_to=='':
            price_to = 50000
        if rating_from=='':
            rating_from = 0
        if rating_to=='':
            rating_to = 5
        if sort== None:
            sort = "TOTAL_SOLD DESC"
        price_from = int(float(price_from))
        price_to = int(float(price_to))
        rating_from = int(float(rating_from))
        rating_to = int(float(rating_to))
        dict['search_result'], dict['summary'] = get_book_info(query, "POST", dict['type'], price_from, price_to, rating_from, rating_to,sort)
        return render(request, "product_list/product_list.html", dict)


    else:
        dict['search_result'], dict['summary'] = get_book_info(query, "GET", dict['type'])


    P = Paginator(dict['search_result'], 9)

    try:
        page = P.page(page_num)
    except EmptyPage:
        page = P.page(1)
    print(dict['summary'])
    dict2 = {'logged_in' : dict['logged_in'], 'search_result': page,  'name' : query, 'classify' : "এর", 'is_author' : False, 'is_genre' : False , 'is_publisher' : True ,  type : "A.AUTHOR_NAME", 'summary' : dict['summary']}

    return render(request, "product_list/product_list.html", dict2)

def get_book_info(query,method, type, price_from=0, price_to=50000, rating_from = 0, rating_to = 5, sort = "TOTAL_SOLD DESC"):
    if method == "GET":
        quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE,B.RATINGS,C.PUBLISHER_NAME, B.DISCOUNT, A.AUTHOR_SUMMARY, B.BOOK_GENRE, C.PUBLISHER_SUMMARY FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) JOIN PUBLISHER C USING(PUBLISHER_ID) WHERE  " + type +" = '" + query +"' ORDER BY B.TOTAL_SOLD DESC"
        print(quercmd)
    elif method == "POST":
        quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE,B.RATINGS,C.PUBLISHER_NAME, B.DISCOUNT, A.AUTHOR_SUMMARY, B.BOOK_GENRE, C.PUBLISHER_SUMMARY FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) JOIN PUBLISHER C USING(PUBLISHER_ID) WHERE  B.PRICE >= " + str(price_from) + " AND B.PRICE <= " + str(price_to) + " AND B.RATINGS >= " + str(rating_from) + " AND B.RATINGS <= " + str(rating_to) + " AND " + type +" = '" + query +"' ORDER BY B." + sort

    db_cursor = conn.cursor()
    db_cursor.execute(quercmd)

    search_results = db_cursor.fetchall()
    li = []
    summary = ' '
    for row in search_results:
        l2 = []
        for item in row:
            l2.append(item)
        l2[1] = slice_name(l2[1])
        if type == "A.AUTHOR_NAME":
            summary = row[7]
        elif type == "C.PUBLISHER_NAME":
            summary = row[9]
        else:
            summary = ' '

        print(row[7], row[9], summary)
        if check_if_image_exists(l2[0]):
            l2.append(l2[0])
        else:
            l2.append("book_image")

        li.append(l2)

    if summary == None:
        summary = ' '
    return li , summary


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
