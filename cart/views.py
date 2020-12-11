from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
import cx_Oracle
import os

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.

def cart(request):
    dict = {'logged_in': False, 'is_admin': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = get_user_name(request.session['user_id'])
        if request.method == 'POST':
            print(request.POST)
            if 'save_cart' in request.POST.keys():
                save_cart(request)
            else:
                save_cart(request)
                token_id = 0
                try:
                    token_id = int(request.POST['token_id'])
                except:
                    pass
                quantity = request.POST.getlist('quantity')
                if len(quantity) > 0:
                    return redirect(reverse('cart:cart_checkout', args=(token_id,)))

        dict['cart_books'] = get_cart_books(request.session['user_id'])
    return render(request, "cart/cart.html", dict)


def cart_checkout(request, pk):
    dict = {'logged_in': False, 'is_admin': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = get_user_name(request.session['user_id'])
        dict['get_books'] = get_cart_books(request.session['user_id'])
        if request.method == 'POST':
            place_order(request, pk)
            return redirect(reverse('rokomariapp:index'))
        tmp = get_prices(request.session['user_id'], pk)
        dict['subtotal'] = tmp[0]
        dict['discount'] = tmp[1]
        dict['shipping'] = tmp[2]
        dict['total'] = tmp[3]
    return render(request, "cart/checkout.html", dict)


def update_discount(user_id, token_id, order_id):
    result = conn.cursor()
    result.execute(
        "SELECT DISCOUNT_AMOUNT FROM DISCOUNT_TOKEN WHERE USER_ID = :v1 AND TOKEN_ID = :v2 AND EXPIRE_DATE > SYSDATE AND NO_OF_USE >= 1",
        v1=user_id, v2=token_id)
    cnt = result.fetchone()
    if cnt is not None:
        discount = int(cnt[0])
        result.execute("UPDATE DISCOUNT_TOKEN  SET NO_OF_USE = NO_OF_USE-1 WHERE TOKEN_ID = :v1 AND USER_ID = :v2",
                       v1=token_id, v2=user_id)
        conn.commit()
        result.execute("UPDATE ORDER_LIST SET DISCOUNT = :v1 WHERE ORDER_ID = :v2", v1=discount, v2=order_id)
        conn.commit()


def get_prices(user_id, token_id):
    discount = 0
    shipping = 60
    result = conn.cursor()
    result.execute(
        "SELECT NVL(SUM(B.PRICE * C.QUANTITY),0) FROM BOOK B, CART_DETAILS C WHERE B.BOOK_ID = C.BOOK_ID AND C.CART_ID = :bv1",
        bv1=user_id)
    subtotal = int(result.fetchone()[0])
    result.execute(
        "SELECT DISCOUNT_AMOUNT FROM DISCOUNT_TOKEN WHERE USER_ID = :v1 AND TOKEN_ID = :v2 AND MINIMUM_ORDER<=:v3 AND EXPIRE_DATE > SYSDATE AND NO_OF_USE >= 1",
        v1=user_id, v2=token_id, v3=subtotal)
    cnt = result.fetchone()
    if cnt is not None:
        discount = int(cnt[0])

    total = subtotal + shipping - discount
    return subtotal, discount, shipping, total


def get_user_name(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM CUSTOMER WHERE USER_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])


def get_user_name_admin(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM ADMIN WHERE ADMIN_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])


def get_admin_id_with_minimum_order_managing():
    result = conn.cursor()
    returnVal = result.callfunc("MINIMUM_ORDER_ADMIN", int)
    return returnVal


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


def place_order(request, token_id):
    location = request.POST['location']
    user_id = request.session['user_id']
    admin_id = get_admin_id_with_minimum_order_managing()
    result = conn.cursor()
    result.execute("SELECT BOOK_ID from CART_DETAILS WHERE CART_ID = :bv ORDER BY BOOK_ID ASC", bv=user_id)
    if result.fetchone() is None:
        return
    result.execute("SELECT MAX(ORDER_ID) FROM ORDER_LIST")
    order_id = 1
    try:
        order_id = result.fetchone()[0] + 1
    except:
        pass
    result.execute(
        "INSERT INTO ORDER_LIST (ORDER_ID,USER_ID,ADMIN_ID  , ORDER_LOCATION) VALUES (:bv1, :bv2, :bv5,  :bv3)",
        bv1=order_id, bv2=user_id, bv5=int(admin_id), bv3=location)
    conn.commit()
    result.execute(
        "INSERT INTO ORDER_DETAILS (ORDER_ID,BOOK_ID,QUANTITY,PRICE_PER_BOOK) SELECT :bv1, C.BOOK_ID , C.QUANTITY,B.PRICE FROM CART_DETAILS C JOIN BOOK B ON(B.BOOK_ID = C.BOOK_ID) WHERE  C.CART_ID = :bv2",
        bv1=order_id, bv2=user_id)
    conn.commit()
    result.execute("DELETE FROM CART_DETAILS WHERE CART_ID = :bv1", bv1=user_id)
    conn.commit()
    update_discount(user_id, token_id, order_id)


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
