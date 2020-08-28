from django.shortcuts import render
from django.http import HttpResponse
import cx_Oracle
import os

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.
def index(request):
    """
    dict contains the following key and values
    :key ------ :value
    'best_seller' : contains 12 most sold books
    'best_discount' : contains 12 books with most discount
    'humayun_ahmed' : contains 12 highest sold books of humayun_ahmed
    'zafar_iqbal' : contains 12 highest sold books of zafar_iqbal
    'categories' : contains top 10 highest sold category
    'publisher' : contains top 10 publications based on no. of books sold
    'authors' : constains top 10 authors based on no. of books sold
    """
    dict = {'logged_in': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = get_user_name(request.session['user_id'])
    dict['best_seller'] = get_best_seller()
    dict['best_discount'] = get_best_discount()
    dict['humayun_ahmed'] = get_humayun_ahmed()
    dict['zafar_iqbal'] = get_zafar_iqbal()
    dict['categories'] = get_categories()
    dict['pubishers'] = get_publishers()
    dict['authors'] = get_authors()

    return render(request, "rokomariapp/index.html", dict)


def get_publishers():
    result = conn.cursor()
    result.execute(
        "SELECT A.PUBLISHER_NAME,SUM(B.TOTAL_SOLD) SOLD FROM PUBLISHER A JOIN BOOK B USING(PUBLISHER_ID) GROUP BY A.PUBLISHER_NAME ORDER BY SOLD DESC")
    li = []
    for i in range(10):
        cnt = result.fetchone()
        li.append(cnt[0])
    return li


def get_authors():
    result = conn.cursor()
    result.execute(
        "SELECT A.AUTHOR_NAME,SUM(B.TOTAL_SOLD) SOLD FROM AUTHOR A JOIN BOOK B USING(AUTHOR_ID) GROUP BY A.AUTHOR_NAME ORDER BY SOLD DESC")
    li = []
    for i in range(10):
        cnt = result.fetchone()
        li.append(cnt[0])
    return li


def get_categories():
    result = conn.cursor()
    result.execute("SELECT BOOK_GENRE,SUM(TOTAL_SOLD) SOLD FROM BOOK GROUP BY BOOK_GENRE ORDER BY SOLD DESC")
    li = []
    for i in range(10):
        cnt = result.fetchone()
        li.append(cnt[0])
    return li


def get_zafar_iqbal():
    result = conn.cursor()
    result.execute(
        "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE+B.DISCOUNT,B.PRICE,B.RATINGS FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) WHERE A.AUTHOR_NAME = 'মুহম্মদ জাফর ইকবাল' ORDER BY TOTAL_SOLD DESC")
    li = []
    for i in range(12):
        cnt = result.fetchone()
        l2 = []
        for j in cnt:
            l2.append(j)
        l2[1] = slice_name(l2[1])
        if check_if_image_exists(l2[0]):
            l2.append(l2[0])
        else:
            l2.append("book_image")
        li.append(l2)
    return li


def get_humayun_ahmed():
    result = conn.cursor()
    result.execute(
        "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE+B.DISCOUNT,B.PRICE,B.RATINGS FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) WHERE A.AUTHOR_NAME = 'হুমায়ূন আহমেদ' ORDER BY TOTAL_SOLD DESC")
    li = []
    for i in range(12):
        cnt = result.fetchone()
        l2 = []
        for j in cnt:
            l2.append(j)
        l2[1] = slice_name(l2[1])
        if check_if_image_exists(l2[0]):
            l2.append(l2[0])
        else:
            l2.append("book_image")
        li.append(l2)
    return li


def get_best_discount():
    result = conn.cursor()
    result.execute(
        "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE+B.DISCOUNT,B.PRICE,B.RATINGS FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) ORDER BY DISCOUNT DESC")

    li = []
    for i in range(12):
        cnt = result.fetchone()
        l2 = []
        # print(l2)
        for j in cnt:
            l2.append(j)
        l2[1] = slice_name(l2[1])
        if check_if_image_exists(l2[0]):
            l2.append(l2[0])
        else:
            l2.append("book_image")
        li.append(l2)
    return li


def get_best_seller():
    result = conn.cursor()
    result.execute(
        "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE+B.DISCOUNT,B.PRICE,B.RATINGS FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) ORDER BY TOTAL_SOLD DESC")
    li = []
    for i in range(12):
        cnt = result.fetchone()
        l2 = []
        for j in cnt:
            l2.append(j)
        l2[1] = slice_name(l2[1])
        if check_if_image_exists(l2[0]):
            l2.append(l2[0])
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
        if len(ret) >= 23:
            ret += "..."
            break
        if str[i] == ':' or str[i] == '(':
            break
        ret += str[i]

    return ret


def get_user_name(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM CUSTOMER WHERE USER_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])
