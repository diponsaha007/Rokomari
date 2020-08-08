from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
import cx_Oracle
import os

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.

def wishlist(request):
    dict = {'logged_in': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = True
        dict['wishlist_books'] = get_wishlist_books(request.session['user_id'])
    return render(request, "wishlist/wishlist.html", dict)


def remove_book(request, pk):
    if request.session.has_key('user_id'):
        delete_book(request.session['user_id'], pk)
    return redirect(reverse('wishlist:wishlist'))


def add_book(request, pk):
    if request.session.has_key('user_id'):
        add_book_to_wishlist(request.session['user_id'], pk)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def add_book_to_wishlist(user_id, book_id):
    result = conn.cursor()
    result.execute(
        "SELECT * FROM WISH_LIST WHERE USER_ID = :bv1 AND BOOK_ID = :bv2", bv1=user_id, bv2=book_id
    )
    cnt = result.fetchone()
    if cnt is not None:
        return
    result.execute(
        "INSERT INTO WISH_LIST VALUES (:bv1,:bv2)", bv1=user_id, bv2=book_id
    )
    conn.commit()


def delete_book(user_id, book_id):
    result = conn.cursor()
    result.execute(
        "SELECT * FROM WISH_LIST WHERE USER_ID = :bv1 AND BOOK_ID = :bv2", bv1=user_id, bv2=book_id
    )
    cnt = result.fetchone()
    if cnt is None:
        return
    result.execute(
        "DELETE FROM WISH_LIST WHERE USER_ID = :bv1 AND BOOK_ID = :bv2", bv1=user_id, bv2=book_id
    )
    conn.commit()


def get_wishlist_books(id):
    result = conn.cursor()
    result.execute(
        "SELECT B.BOOK_ID,B.BOOK_NAME,(SELECT C.AUTHOR_NAME FROM AUTHOR  C WHERE B.AUTHOR_ID = C.AUTHOR_ID)AUTHOR_NAME,B.BOOK_GENRE,B.RATINGS,B.PRICE FROM WISH_LIST A JOIN BOOK B ON (B.BOOK_ID = A.BOOK_ID AND A.USER_ID=:mybv) ORDER BY B.BOOK_ID ASC",
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
