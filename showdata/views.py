from django.shortcuts import render, redirect, reverse
import cx_Oracle
import os
import numpy as np
from pyavrophonetic import avro
from django.core.paginator import Paginator

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.

def order_database(request):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': get_user_name_admin(request.session['user_id']), 'is_admin': True}
        if request.method == "GET":
            dict['orders'] = get_order_list(request.session['user_id'], -1)
        elif request.method == "POST":
            dict['orders'] = get_order_list(request.session['user_id'], request.POST.get("order_id"))
        return render(request, "showdata/showdata_order.html", dict)
    else:
        return redirect(reverse('rokomariapp:index'))


def mark_as_delivered(request, pk):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        db_cursor = conn.cursor()
        db_cursor.callproc('MARK_DELIVERED', [int(pk), int(request.session['user_id'])])
        conn.commit()
        return redirect(reverse('showdata:order_database'))
    else:
        return redirect(reverse('rokomariapp:index'))


def show_order_details(request, pk):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': get_user_name_admin(request.session['user_id']), 'is_admin': True,
                'order_id': pk}
        x = get_ordered_books(pk)
        dict['order_details'] = x[0]
        dict['subtotal'] = x[1]
        dict['discount'] = x[2]
        dict['shipping'] = x[3]
        dict['total'] = x[4]
        return render(request, "showdata/showdata_order_details.html", dict)
    else:
        return redirect(reverse('rokomariapp:index'))


def show_tokens(request):
    dict = {'logged_in': False, 'is_admin': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = get_user_name(request.session['user_id'])
        dict['token_details'] = get_token_database(request.session['user_id'])
    return render(request, "showdata/showdata_tokens.html", dict)


def get_token_database(user_id):
    result = conn.cursor()
    result.execute(
        "SELECT TOKEN_ID ,TO_CHAR( CREATION_DATE,'dd/mm/yyyy') ,TO_CHAR( EXPIRE_DATE,'dd/mm/yyyy') , MINIMUM_ORDER , DISCOUNT_AMOUNT , NO_OF_USE FROM DISCOUNT_TOKEN WHERE USER_ID = :v1 AND NO_OF_USE >= 1 AND EXPIRE_DATE > SYSDATE",
        v1=user_id)
    li = []
    while True:
        cnt = result.fetchone()
        if cnt is None:
            break
        tmp = []
        for i in range(len(cnt)):
            tmp.append(cnt[i])
        li.append(tmp)
    return li


def get_ordered_books(order_id):
    result = conn.cursor()
    result.execute(
        "SELECT O.BOOK_ID,(SELECT BOOK_NAME FROM BOOK WHERE O.BOOK_ID = BOOK_ID),O.QUANTITY , O.PRICE_PER_BOOK  FROM ORDER_DETAILS O WHERE O.ORDER_ID = :v ORDER BY O.BOOK_ID",
        v=order_id)
    li = []
    sum = 0
    discount = 0
    shipping = 60
    total = 0
    while True:
        cnt = result.fetchone()
        if cnt is None:
            break
        tmp = []
        for i in range(len(cnt)):
            tmp.append(cnt[i])
        sum += tmp[2] * tmp[3]
        li.append(tmp)
    result2 = conn.cursor()
    result2.execute("SELECT  DISCOUNT FROM ORDER_LIST WHERE ORDER_ID = :v1", v1=order_id)
    discount = int(result2.fetchone()[0])
    total = sum + shipping - discount
    return li, sum, discount, shipping, total


def get_order_list(admin_id, order_id):
    result = conn.cursor()
    if order_id == -1:
        result.execute(
            "SELECT O.ORDER_ID , (SELECT X.FIRST_NAME || ' '|| X.LAST_NAME FROM CUSTOMER X WHERE X.USER_ID = O.USER_ID) AS \"NAME\" , TO_CHAR(ORDER_DATE,'DD, Month, YYYY') , TO_CHAR(RECEIVED_DATE,'DD, Month, YYYY'),O.ORDER_LOCATION ,(SELECT SUM(X.QUANTITY * X.PRICE_PER_BOOK) FROM ORDER_DETAILS X WHERE X.ORDER_ID = O.ORDER_ID) FROM ORDER_LIST O WHERE O.ADMIN_ID = :bv ORDER BY RECEIVED_DATE DESC,ORDER_DATE DESC",
            bv=admin_id)
    else:
        result.execute(
            "SELECT O.ORDER_ID , (SELECT X.FIRST_NAME || ' '|| X.LAST_NAME FROM CUSTOMER X WHERE X.USER_ID = O.USER_ID) AS \"NAME\" , TO_CHAR(ORDER_DATE,'DD, Month, YYYY') , TO_CHAR(RECEIVED_DATE,'DD, Month, YYYY'),O.ORDER_LOCATION ,(SELECT SUM(X.QUANTITY * X.PRICE_PER_BOOK) FROM ORDER_DETAILS X WHERE X.ORDER_ID = O.ORDER_ID) FROM ORDER_LIST O WHERE O.ADMIN_ID = :bv AND O.ORDER_ID = :bv2 ORDER BY RECEIVED_DATE DESC, ORDER_DATE DESC",
            bv=admin_id, bv2=order_id)
    li = []
    while (True):
        cnt = result.fetchone()
        if cnt is None:
            break
        tmp = []
        for i in range(len(cnt)):
            tmp.append(cnt[i])
        if tmp[3] is None:
            tmp[3] = "---"
            tmp.append(0)
        else:
            tmp.append(1)
        result2 = conn.cursor()
        result2.execute("SELECT  DISCOUNT FROM ORDER_LIST WHERE ORDER_ID = :v1", v1=tmp[0])
        tmp[5] -= int(result2.fetchone()[0])
        tmp[5] += 60
        li.append(tmp)

    return li


def customer_database(request):
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
            dict['search_result'] = get_customer_info(query, "GET")
        elif request.method == "POST":
            query = ""
            customer_name_part = request.POST.get("customer_name_part")

            if customer_name_part is None:
                customer_name_part = ""
            query = customer_name_part

            dict['search_result'] = get_customer_info(query, "POST")
            dict['query'] = query
            return render(request, "showdata/showdata_customer.html", dict)

        P = Paginator(dict['search_result'], 20)

        try:
            page = P.page(page_num)
        except:
            page = P.page(1)

        dict2 = {'logged_in': dict['logged_in'], 'is_admin': dict['is_admin'], 'search_result': page, 'query': "query"}

        return render(request, "showdata/showdata_customer.html", dict2)
    else:
        return redirect(reverse('rokomariapp:index'))


def get_customer_info(query, method):
    query = query.lower()
    if method == "GET":
        quercmd = "SELECT C.USER_ID , C.USER_NAME , C.FIRST_NAME , C.LAST_NAME , C.EMAIL ,C.SIGNUP_DATE, A.ADDRESS_1 , A.ADDRESS_2 , A.CITY,A.COUNTRY,A.PHONE FROM CUSTOMER C , ADDRESS_DETAIL A WHERE C.USER_ID = A.USER_ID ORDER BY USER_ID"
    elif method == "POST":
        quercmd = "SELECT C.USER_ID , C.USER_NAME , C.FIRST_NAME , C.LAST_NAME , C.EMAIL ,C.SIGNUP_DATE, A.ADDRESS_1 , A.ADDRESS_2 , A.CITY,A.COUNTRY,A.PHONE FROM CUSTOMER C , ADDRESS_DETAIL A WHERE C.USER_ID = A.USER_ID AND ( LOWER(C.FIRST_NAME || ' ' || C.LAST_NAME) LIKE '%" + query + "%' OR LOWER(C.USER_NAME) LIKE '%" + query + "%' ) ORDER BY USER_ID"
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

        l2.append(check_file(l2[0]))
        li.append(l2)
    return li


def check_file(user_id):
    nam = 'static/images/my_account/' + str(user_id) + '.jpg'
    if os.path.isfile(nam):
        return nam
    else:
        return 'static/images/my_account/' + 'default.jpg'


def admin_database(request):
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
            dict['search_result'] = get_admin_info(query, "GET")
        elif request.method == "POST":
            query = ""
            admin_name_part = request.POST.get("admin_name_part")

            if admin_name_part is None:
                admin_name_part = ""
            query = admin_name_part

            dict['search_result'] = get_admin_info(query, "POST")
            dict['query'] = query
            return render(request, "showdata/showdata_admin.html", dict)

        P = Paginator(dict['search_result'], 20)

        try:
            page = P.page(page_num)
        except:
            page = P.page(1)

        dict2 = {'logged_in': dict['logged_in'], 'is_admin': dict['is_admin'], 'search_result': page, 'query': "query"}

        return render(request, "showdata/showdata_admin.html", dict2)
    else:
        return redirect(reverse('rokomariapp:index'))


def get_admin_info(query, method):
    query = query.lower()
    if method == "GET":
        quercmd = "SELECT ADMIN_ID , FIRST_NAME , LAST_NAME , EMAIL , PHONE FROM ADMIN ORDER BY ADMIN_ID"
    elif method == "POST":
        quercmd = "SELECT ADMIN_ID , FIRST_NAME , LAST_NAME , EMAIL , PHONE FROM ADMIN  WHERE ( LOWER(FIRST_NAME || ' ' || LAST_NAME) LIKE '%" + query + "%' ) ORDER BY ADMIN_ID"
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

        l2.append(check_admin_file(l2[0]))
        li.append(l2)
    return li


def check_admin_file(user_id):
    nam = 'static/images/admin/' + str(user_id) + '.jpg'
    if os.path.isfile(nam):
        return nam
    else:
        return 'static/images/admin/' + 'default.jpg'


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


def deleted_books(request):
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
            dict['search_result'] = get_deleted_book_info(query, "GET")
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
            dict['search_result'] = get_deleted_book_info(query, "POST", price_from, price_to, rating_from, rating_to,
                                                          sort,
                                                          book_name, author_name)
            dict['query'] = query
            return render(request, "showdata/showdata_deleted_book.html", dict)
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
        return render(request, "showdata/showdata_deleted_book.html", dict2)
    else:
        return redirect(reverse('rokomariapp:index'))


def get_deleted_book_info(query, method, price_from=0, price_to=50000, rating_from=0, rating_to=5,
                          sort="TOTAL_SOLD DESC",
                          book_name="", author_name=""):
    if method == "UPDATE":
        quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,B.AUTHOR_NAME,B.PRICE,B.RATINGS,B.PUBLISHER_NAME, B.DISCOUNT, B.BOOK_EDITION, B.PAGES, B.BOOK_GENRE, B.SUMMARY FROM DELETED_BOOK B  WHERE B.BOOK_ID = " + str(
            query)
    elif is_banglish(query):
        # print(avro.parse(query))
        query = avro.parse(query)
    # print(sort)
    if method == "GET":
        quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,B.AUTHOR_NAME,B.PRICE, B.BOOK_GENRE, B.BOOK_EDITION, B.RATINGS, B.NO_OF_RATINGS, B.PUBLISHER_NAME, B.DISCOUNT, B.COUNTRY, B.LANGUAGE, B.SUMMARY, B.ISBN, B.PAGES, B.TOTAL_SOLD FROM DELETED_BOOK B  ORDER BY B.BOOK_ID"
    elif method == "POST":
        quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,B.AUTHOR_NAME,B.PRICE, B.BOOK_GENRE, B.BOOK_EDITION, B.RATINGS, B.NO_OF_RATINGS, B.PUBLISHER_NAME, B.DISCOUNT, B.COUNTRY, B.LANGUAGE, B.SUMMARY, B.ISBN, B.PAGES, B.TOTAL_SOLD FROM DELETED_BOOK B  WHERE  ((B.PRICE >= " + str(
            price_from) + " AND B.PRICE <= " + str(price_to) + " AND B.RATINGS >= " + str(
            rating_from) + " AND B.RATINGS <= " + str(
            rating_to) + ") AND (B.BOOK_NAME LIKE '%" + book_name + "%') AND (B.AUTHOR_NAME LIKE '%" + author_name + "%') AND (B.PUBLISHER_NAME LIKE '%" + query + "%') AND (B.BOOK_GENRE LIKE '%" + query + "%')) ORDER BY B." + sort

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
        else:
            l2.append("book_image")
        li.append(l2)
    return li


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
        quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE, B.BOOK_GENRE, B.BOOK_EDITION, B.RATINGS, B.NO_OF_RATINGS, C.PUBLISHER_NAME, B.DISCOUNT, B.COUNTRY, B.LANGUAGE, B.SUMMARY, B.ISBN, B.PAGES, B.TOTAL_SOLD FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) JOIN PUBLISHER C USING(PUBLISHER_ID) ORDER BY B.BOOK_ID"
    elif method == "POST":
        quercmd = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE, B.BOOK_GENRE, B.BOOK_EDITION, B.RATINGS, B.NO_OF_RATINGS, C.PUBLISHER_NAME, B.DISCOUNT, B.COUNTRY, B.LANGUAGE, B.SUMMARY, B.ISBN, B.PAGES, B.TOTAL_SOLD FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) JOIN PUBLISHER C USING(PUBLISHER_ID) WHERE  ((B.PRICE >= " + str(
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
            # return redirect(reverse('product_details:product_details', kwargs={'pk': pk}))
            return redirect(reverse('showdata:showdata'))
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

        return render(request, "showdata/showdata_author.html", dict2)
    else:
        return redirect(reverse('rokomariapp:index'))


def get_author_publisher_info(query, method, table):
    query = query.lower()
    if table == "AUTHOR":
        if method == "GET":
            quercmd = "SELECT A.AUTHOR_ID,A.AUTHOR_NAME FROM  AUTHOR A ORDER BY A.AUTHOR_ID"
        elif method == "POST":
            quercmd = "SELECT A.AUTHOR_ID,A.AUTHOR_NAME FROM  AUTHOR A WHERE lower(A.AUTHOR_NAME) LIKE '%" + query + "%' ORDER BY A.AUTHOR_NAME"

    elif table == "PUBLISHER":
        if method == "GET":
            quercmd = "SELECT A.PUBLISHER_ID,A.PUBLISHER_NAME FROM  PUBLISHER A ORDER BY A.PUBLISHER_ID"
        elif method == "POST":
            quercmd = "SELECT A.PUBLISHER_ID,A.PUBLISHER_NAME FROM  PUBLISHER A WHERE lower(A.PUBLISHER_NAME) LIKE '%" + query + "%' ORDER BY A.PUBLISHER_NAME"

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
            db_cursor = conn.cursor()
            db_cursor.callproc('DELETE_AUTHOR', [int(pk)])
            conn.commit()
            return redirect(reverse('showdata:showdata_author'))
    else:
        return redirect(reverse('rokomariapp:index'))


def restore_book(request, pk):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': False, 'is_admin': False}
        if request.session.has_key('is_admin'):
            dict['logged_in'] = get_user_name_admin(request.session['user_id'])
            dict['is_admin'] = True
            db_cursor = conn.cursor()
            db_cursor.callproc('RESTORE_BOOK', [int(pk)])
            conn.commit()
            return redirect(reverse('showdata:deleted_books'))
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
            db_cursor = conn.cursor()
            db_cursor.callproc('DELETE_PUBLISHER', [int(pk)])
            conn.commit()
            return redirect(reverse('showdata:showdata_publisher'))
    else:
        return redirect(reverse('rokomariapp:index'))
