from django.shortcuts import render, redirect, reverse
import cx_Oracle
import os
import numpy as np
from pyavrophonetic import avro
from django.core.paginator import Paginator

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.
def search_result(request):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        query = request.GET.get('search')
        print(query, request.method)
        if query == None:
            page_num = 1
            query = ""
        else:
            querar = query.split("/?page=")
            shape = np.asarray(querar).shape[0]

            if shape == 1:
                query = querar[0]
                page_num = 1
            else:
                query = querar[0]
                page_num = querar[1]

        dict = {'logged_in': False, 'is_admin': False}

        if request.session.has_key('is_admin'):
            dict['logged_in'] = get_user_name_admin(request.session['user_id'])
            dict['is_admin'] = True
        elif request.session.has_key('user_id'):
            dict['logged_in'] = get_user_name(request.session['user_id'])
        if request.method == "GET":
            dict['search_result'] = get_book_info(query, "GET")
        elif request.method == "POST":
            query = ""
            price_from = request.POST.get("price_from")
            price_to = request.POST.get("price_to")
            rating_from = request.POST.get("rating_from")
            rating_to = request.POST.get("rating_to")
            sort = request.POST.get("sort")
            book_name = request.POST.get("book_name")
            author_name = request.POST.get("author_name")
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
            dict['search_result'] = get_book_info(query, "POST", price_from, price_to, rating_from, rating_to, sort,
                                                  book_name, author_name)
            dict['query'] = query
            return render(request, "showdata/showdata.html", dict)
            # print("POST er vitor", price_from, price_to)

        # dict['search_result'] = get_book_info("query", "GET")
        # page_num = 1
        P = Paginator(dict['search_result'], 20)

        try:
            page = P.page(page_num)
        except:
            page = P.page(1)

        dict2 = {'logged_in': dict['logged_in'], 'is_admin': dict['is_admin'], 'search_result': page, 'query': "query"}
        # print(dict2)
        return render(request, "showdata/showdata.html", dict2)
    else:
        return redirect(reverse('rokomariapp:index'))


def get_book_info(query, method, price_from=0, price_to=50000, rating_from=0, rating_to=5, sort="TOTAL_SOLD DESC",
                  book_name="", author_name=""):
    if method == "UPDATE":
        quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE,B.RATINGS,C.PUBLISHER_NAME, B.DISCOUNT, B.BOOK_EDITION, B.PAGES, B.BOOK_GENRE, B.SUMMARY FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) JOIN PUBLISHER C USING(PUBLISHER_ID) WHERE B.BOOK_ID = " + str(
            query)
    elif is_banglish(query):
        # print(avro.parse(query))
        query = avro.parse(query)
    # print(sort)
    if method == "GET":
        quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE,B.RATINGS,C.PUBLISHER_NAME, B.DISCOUNT FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) JOIN PUBLISHER C USING(PUBLISHER_ID) ORDER BY B.BOOK_ID"
    elif method == "POST":
        quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE,B.RATINGS,C.PUBLISHER_NAME, B.DISCOUNT FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) JOIN PUBLISHER C USING(PUBLISHER_ID) WHERE  ((B.PRICE >= " + str(
            price_from) + " AND B.PRICE <= " + str(price_to) + " AND B.RATINGS >= " + str(
            rating_from) + " AND B.RATINGS <= " + str(
            rating_to) + ") AND (B.BOOK_NAME LIKE '%" + book_name + "%') AND (A.AUTHOR_NAME LIKE '%" + author_name + "%') AND (C.PUBLISHER_NAME LIKE '%" + query + "%') AND (B.BOOK_GENRE LIKE '%" + query + "%')) ORDER BY B." + sort

    db_cursor = conn.cursor()
    db_cursor.execute(quercmd)

    search_results = db_cursor.fetchall()
    li = []

    for row in search_results:
        l2 = []
        for item in row:
            if item == None:
                item = ""
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


def delete_book(request, pk):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': False, 'is_admin': False}

        if request.session.has_key('is_admin'):
            dict['logged_in'] = get_user_name_admin(request.session['user_id'])
            dict['is_admin'] = True
            quercmd = "DELETE FROM BOOK WHERE BOOK_ID = " + str(pk)
            db_cursor = conn.cursor()
            db_cursor.execute(quercmd)
            conn.commit()
            return redirect(reverse('showdata:showdata'))
    else:
        return redirect(reverse('rokomariapp:index'))


def update_book(request, pk):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': False, 'is_admin': False}

        if request.session.has_key('is_admin'):
            dict['logged_in'] = get_user_name_admin(request.session['user_id'])
            dict['is_admin'] = True

        if request.method == "POST":
            edition = request.POST.get("edition")
            price = request.POST.get("price")
            discount = request.POST.get("discount")
            summary = request.POST.get("summary")
            pages = request.POST.get("pages")
            print(edition, price, discount, summary, pages)
            quercmd = "UPDATE BOOK SET BOOK_EDITION = '" + edition + "', PRICE = " + str(price) + ", DISCOUNT = " + str(
                discount) + ", SUMMARY = '" + summary + "', PAGES = " + str(pages) + " WHERE BOOK_ID = " + str(pk)
            db_cursor = conn.cursor()
            db_cursor.execute(quercmd)
            conn.commit()
            # print(edition, price, discount, summary, pages)
            # return redirect(reverse('showdata:showdata'))
            return redirect(reverse('product_details:product_details', kwargs={'pk': pk}))

        else:
            dict['search_result'] = get_book_info(pk, "UPDATE")
            return render(request, "showdata/update_book.html", dict)
    else:
        return redirect(reverse('rokomariapp:index'))


def search_result_author(request):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        query = request.GET.get('search')
        # print(query, request.method)
        if query == None:
            page_num = 1
            query = ""
        else:
            querar = query.split("/?page=")
            shape = np.asarray(querar).shape[0]

            if shape == 1:
                query = querar[0]
                page_num = 1
            else:
                query = querar[0]
                page_num = querar[1]

        dict = {'logged_in': False, 'is_admin': False}

        if request.session.has_key('is_admin'):
            dict['logged_in'] = get_user_name_admin(request.session['user_id'])
            dict['is_admin'] = True
        elif request.session.has_key('user_id'):
            dict['logged_in'] = get_user_name(request.session['user_id'])
        if request.method == "GET":
            dict['search_result'] = get_author_publisher_info(query, "GET", "AUTHOR")
            # print("GET er vitor")
        elif request.method == "POST":
            query = ""
            author_name_part = request.POST.get("author_name_part")

            if author_name_part == None:
                author_name_part = ""
            query = author_name_part
            # print(price_from, price_to, rating_from, rating_to, sort)
            dict['search_result'] = get_author_publisher_info(query, "POST", "AUTHOR")
            dict['query'] = query
            return render(request, "showdata/showdata_author.html", dict)
            # print("POST er vitor", price_from, price_to)

        # dict['search_result'] = get_book_info("query", "GET")
        # page_num = 1
        P = Paginator(dict['search_result'], 20)

        try:
            page = P.page(page_num)
        except:
            page = P.page(1)

        dict2 = {'logged_in': dict['logged_in'], 'is_admin': dict['is_admin'], 'search_result': page, 'query': "query"}
        # print(dict2)
        return render(request, "showdata/showdata_author.html", dict2)
    else:
        return redirect(reverse('rokomariapp:index'))


def get_author_publisher_info(query, method, table):
    if is_banglish(query):
        # print(avro.parse(query))
        query = avro.parse(query)
    # print(sort)
    if table == "AUTHOR":
        if method == "GET":
            quercmd = "SELECT A.AUTHOR_ID,A.AUTHOR_NAME FROM  AUTHOR A ORDER BY A.AUTHOR_ID"
        elif method == "POST":
            quercmd = "SELECT A.AUTHOR_ID,A.AUTHOR_NAME FROM  AUTHOR A WHERE A.AUTHOR_NAME LIKE '%" + query + "%' ORDER BY A.AUTHOR_NAME"

    elif table == "PUBLISHER":
        if method == "GET":
            quercmd = "SELECT A.PUBLISHER_ID,A.PUBLISHER_NAME FROM  PUBLISHER A ORDER BY A.PUBLISHER_ID"
        elif method == "POST":
            quercmd = "SELECT A.PUBLISHER_ID,A.PUBLISHER_NAME FROM  PUBLISHER A WHERE A.PUBLISHER_NAME LIKE '%" + query + "%' ORDER BY A.PUBLISHER_NAME"

    # print(quercmd)
    # print(query)
    db_cursor = conn.cursor()
    db_cursor.execute(quercmd)

    search_results = db_cursor.fetchall()
    li = []

    for row in search_results:
        l2 = []
        for item in row:
            if item == None:
                item = ""
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


def delete_author(request, pk):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': False, 'is_admin': False}

        if request.session.has_key('is_admin'):
            dict['logged_in'] = get_user_name_admin(request.session['user_id'])
            dict['is_admin'] = True
            quercmd = "DELETE FROM AUTHOR WHERE AUTHOR_ID = " + str(pk)
            db_cursor = conn.cursor()
            db_cursor.execute(quercmd)
            conn.commit()
            return redirect(reverse('showdata:showdata_author'))
    else:
        return redirect(reverse('rokomariapp:index'))


def search_result_publisher(request):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        query = request.GET.get('search')
        if query == None:
            page_num = 1
            query = ""
        else:
            querar = query.split("/?page=")
            shape = np.asarray(querar).shape[0]

            if shape == 1:
                query = querar[0]
                page_num = 1
            else:
                query = querar[0]
                page_num = querar[1]

        dict = {'logged_in': False, 'is_admin': False}

        if request.session.has_key('is_admin'):
            dict['logged_in'] = get_user_name_admin(request.session['user_id'])
            dict['is_admin'] = True
        elif request.session.has_key('user_id'):
            dict['logged_in'] = get_user_name(request.session['user_id'])
        if request.method == "GET":
            dict['search_result'] = get_author_publisher_info(query, "GET", "PUBLISHER")
            # print("GET er vitor")
        elif request.method == "POST":
            query = ""
            publisher_name_part = request.POST.get("publisher_name_part")

            if publisher_name_part == None:
                publisher_name_part = ""
            query = publisher_name_part
            # print(price_from, price_to, rating_from, rating_to, sort)
            dict['search_result'] = get_author_publisher_info(query, "POST", "PUBLISHER")
            dict['query'] = query
            return render(request, "showdata/showdata_publisher.html", dict)
        P = Paginator(dict['search_result'], 20)

        try:
            page = P.page(page_num)
        except:
            page = P.page(1)

        dict2 = {'logged_in': dict['logged_in'], 'is_admin': dict['is_admin'], 'search_result': page, 'query': "query"}
        # print(dict2)
        return render(request, "showdata/showdata_publisher.html", dict2)
    else:
        return redirect(reverse('rokomariapp:index'))


def delete_publisher(request, pk):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': False, 'is_admin': False}
        if request.session.has_key('is_admin'):
            dict['logged_in'] = get_user_name_admin(request.session['user_id'])
            dict['is_admin'] = True
            quercmd = "DELETE FROM PUBLISHER WHERE PUBLISHER_ID = " + str(pk)
            db_cursor = conn.cursor()
            db_cursor.execute(quercmd)
            conn.commit()
            return redirect(reverse('showdata:showdata_publisher'))
    else:
        return redirect(reverse('rokomariapp:index'))
