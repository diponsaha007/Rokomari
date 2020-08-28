from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
import cx_Oracle
import os

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.

def cart(request):
    dict = {'logged_in': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = get_user_name(request.session['user_id'])
        if request.method == 'POST':
            print(request.POST)
            if 'save_cart' in request.POST.keys():
                save_cart(request)
            else:
                place_order(request)

        dict['cart_books'] = get_cart_books(request.session['user_id'])
    return render(request, "cart/cart.html", dict)


def get_user_name(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM CUSTOMER WHERE USER_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])


def get_admin_id_with_minimum_order_managing():
    result = conn.cursor()
    result.execute(
        "SELECT E.ADMIN_ID FROM (SELECT A.ADMIN_ID , (SELECT COUNT(O.ADMIN_ID) FROM ORDER_LIST O WHERE O.ADMIN_ID = A.ADMIN_ID AND O.RECEIVED_DATE IS NULL) CNT FROM ADMIN A) E WHERE E.CNT = ( SELECT MIN(F.CNT) FROM (SELECT A.ADMIN_ID , (SELECT COUNT(O.ADMIN_ID) FROM ORDER_LIST O WHERE O.ADMIN_ID = A.ADMIN_ID AND O.RECEIVED_DATE IS NULL) CNT FROM ADMIN A) F)")
    return result.fetchone()[0]


def save_cart(request):
    quantity = request.POST.getlist('quantity')
    user_id = request.session['user_id']
    result = conn.cursor()
    result.execute("SELECT BOOK_ID from CART_DETAILS WHERE CART_ID = :bv ORDER BY BOOK_ID ASC", bv=user_id)
    book_id_list = []
    while True:
        cnt = result.fetchone()
        if cnt is None:
            break
        book_id_list.append(int(cnt[0]))
    for i in range(len(book_id_list)):
        result.execute("UPDATE CART_DETAILS SET QUANTITY = :bv1 WHERE (BOOK_ID = :bv2 and CART_ID = :bv3)",
                       bv1=int(quantity[i]), bv2=int(book_id_list[i]), bv3=user_id)
        conn.commit()


def place_order(request):
    quantity = request.POST.getlist('quantity')
    location = request.POST['location']
    user_id = request.session['user_id']
    admin_id = get_admin_id_with_minimum_order_managing()
    if len(quantity) == 0 or len(location) == 0:
        return
    result = conn.cursor()
    result.execute("SELECT BOOK_ID from CART_DETAILS WHERE CART_ID = :bv ORDER BY BOOK_ID ASC", bv=user_id)
    if result.fetchone() is None:
        return
    total_price = request.POST['total_price']
    result.execute("SELECT MAX(ORDER_ID) FROM ORDER_LIST")
    order_id = 1
    try:
        order_id = result.fetchone()[0] + 1
    except:
        pass
    result.execute(
        "INSERT INTO ORDER_LIST (ORDER_ID,USER_ID,ADMIN_ID ,TOTAL_PRICE , ORDER_LOCATION) VALUES (:bv1, :bv2, :bv5, :bv4, :bv3)",
        bv1=order_id, bv2=user_id, bv5=int(admin_id), bv4=int(total_price), bv3=location)
    conn.commit()
    result.execute("SELECT BOOK_ID from CART_DETAILS WHERE CART_ID = :bv ORDER BY BOOK_ID ASC", bv=user_id)
    book_id_list = []
    while True:
        cnt = result.fetchone()
        if cnt is None:
            break
        book_id_list.append(int(cnt[0]))
    for i in range(len(book_id_list)):
        result.execute("UPDATE CART_DETAILS SET QUANTITY = :bv1 WHERE (BOOK_ID = :bv2 and CART_ID = :bv3)",
                       bv1=int(quantity[i]), bv2=int(book_id_list[i]), bv3=user_id)
        conn.commit()
    result.execute(
        "INSERT INTO ORDER_DETAILS (ORDER_ID,BOOK_ID,QUANTITY)  SELECT :bv1, BOOK_ID , QUANTITY FROM CART_DETAILS WHERE CART_ID = :bv2 ",
        bv1=order_id, bv2=user_id)
    conn.commit()
    result.execute("DELETE FROM CART_DETAILS WHERE CART_ID = :bv1", bv1=user_id)
    conn.commit()


def remove_book(request, pk):
    if request.session.has_key('user_id'):
        delete_book(request.session['user_id'], pk)
    return redirect(reverse('cart:cart'))


def add_book(request, pk):
    if request.session.has_key('user_id'):
        add_book_to_cart(request.session['user_id'], pk)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def add_book_to_cart(user_id, book_id):
    result = conn.cursor()
    result.execute(
        "SELECT * FROM CART_DETAILS WHERE CART_ID = :bv1 AND BOOK_ID = :bv2", bv1=user_id, bv2=book_id
    )
    cnt = result.fetchone()
    if cnt is not None:
        return
    result.execute(
        "INSERT INTO CART_DETAILS VALUES (:bv1,:bv2,1)", bv1=user_id, bv2=book_id
    )
    conn.commit()


def delete_book(user_id, book_id):
    result = conn.cursor()
    result.execute(
        "SELECT * FROM CART_DETAILS WHERE CART_ID = :bv1 AND BOOK_ID = :bv2", bv1=user_id, bv2=book_id
    )
    cnt = result.fetchone()
    if cnt is None:
        return
    result.execute(
        "DELETE FROM CART_DETAILS WHERE CART_ID = :bv1 AND BOOK_ID = :bv2", bv1=user_id, bv2=book_id
    )
    conn.commit()


def get_cart_books(id):
    result = conn.cursor()
    result.execute(
        "SELECT B.BOOK_ID,B.BOOK_NAME,(SELECT C.AUTHOR_NAME FROM AUTHOR  C WHERE B.AUTHOR_ID = C.AUTHOR_ID)AUTHOR_NAME,B.BOOK_GENRE,B.RATINGS,B.PRICE*A.QUANTITY,A.QUANTITY FROM CART_DETAILS A JOIN BOOK B ON (B.BOOK_ID = A.BOOK_ID AND A.CART_ID=:mybv) ORDER BY B.BOOK_ID ASC",
        mybv=id)
    li = []
    while True:
        cnt = result.fetchone()
        if cnt is None:
            break
        l2 = []
        for j in cnt:
            l2.append(j)
        if check_if_image_exists(l2[0]):
            l2.append(l2[0])
        else:
            l2.append("book_image")
        li.append(l2)

    return li


def check_if_image_exists(id):
    nam = 'static/images/rokomariapp/images/' + str(id) + '.jpg'
    if os.path.isfile(nam):
        return True
    return False
