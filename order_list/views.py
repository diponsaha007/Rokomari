from django.shortcuts import render, redirect, reverse
import cx_Oracle
import os

# Create your views here.

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')

conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


def order_list(request):
    dict = {'logged_in': False, 'is_admin': False}

    if request.session.has_key('user_id'):
        dict['logged_in'] = get_user_name(request.session['user_id'])
        dict['orders'] = get_order(request.session['user_id'])
    return render(request, 'order_list/order_list.html', dict)


def get_user_name(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM CUSTOMER WHERE USER_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])


def get_order(user_id):
    result = conn.cursor()
    result.execute(
        "SELECT ORDER_ID , ORDER_DATE,RECEIVED_DATE,ORDER_LOCATION  from ORDER_LIST WHERE USER_ID = :bv1 ORDER BY RECEIVED_DATE DESC NULLS FIRST, ORDER_DATE DESC",
        bv1=user_id)
    li = []
    while True:
        cnt = result.fetchone()
        if cnt is None:
            break
        l2 = []
        for j in cnt:
            l2.append(j)
        order_id = l2[0]
        if l2[2] is None:
            l2[2] = 'Pending Delivery'
        l3 = []
        total_price = 0
        result2 = conn.cursor()
        result2.execute(
            "SELECT O.BOOK_ID, B.BOOK_NAME ,A.AUTHOR_NAME, O.QUANTITY,O.PRICE_PER_BOOK FROM BOOK B JOIN ORDER_DETAILS O On (B.BOOK_ID = O.BOOK_ID) JOIN AUTHOR A ON(A.AUTHOR_ID=B.AUTHOR_ID) WHERE O.ORDER_ID = :bv1",
            bv1=order_id)
        while True:
            cnt2 = result2.fetchone()
            if cnt2 is None:
                break
            total_price += int(cnt2[3]) * int(cnt2[4])
            l4 = []
            for x in cnt2:
                l4.append(x)
            if check_if_image_exists(l4[0]):
                l4.append(l4[0])
            else:
                l4.append("book_image")
            l3.append(l4)
        l2.append(total_price)
        result2.execute("SELECT  DISCOUNT FROM ORDER_LIST WHERE ORDER_ID = :v1", v1=order_id)
        l2.append(int(result2.fetchone()[0]))
        l2.append(l3)
        li.append(l2)

    print(li)
    return li


def check_if_image_exists(id):
    nam = 'static/images/rokomariapp/images/' + str(id) + '.jpg'
    if os.path.isfile(nam):
        return True
    return False


def get_user_name_admin(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM ADMIN WHERE ADMIN_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])
