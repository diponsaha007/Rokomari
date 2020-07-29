from django.shortcuts import render
import cx_Oracle
import os

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.
def product_details(request, pk):
    dict = {'logged_in': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = True
    get_book_info(pk, dict)
    return render(request, "product_details/product.html", dict)


def get_book_info(id, dict):
    result = conn.cursor()
    result.execute(
        "SELECT B.BOOK_ID, B.BOOK_NAME, A.AUTHOR_NAME, B.BOOK_GENRE, B.RATINGS, B.NO_OF_RATINGS, B.PRICE, B.PRICE - B.DISCOUNT, C.PUBLISHER_NAME, B.ISBN, B.BOOK_EDITION, B.PAGES, B.COUNTRY, B.LANGUAGE, B.SUMMARY FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) JOIN PUBLISHER C USING(PUBLISHER_ID) WHERE B.BOOK_ID = :mybv",
        mybv=id)
    cnt = result.fetchone()
    dict['book_id'] = cnt[0]
    dict['book_name'] = cnt[1]
    dict['author_name'] = cnt[2]
    dict['genre'] = cnt[3]
    dict['rating'] = cnt[4]
    dict['rating_num'] = cnt[5]
    dict['price'] = cnt[6]
    dict['discount_price'] = cnt[7]
    dict['publisher_name'] = cnt[8]
    dict['isbn'] = cnt[9]
    dict['book_edition'] = cnt[10]
    dict['pages'] = cnt[11]
    dict['country'] = cnt[12]
    dict['language'] = cnt[13]
    if cnt[14] is None or len(cnt[14]) == 0:
        dict[
            'summary'] = "Sorry! No summary or description was provided for this book.\nদুঃখিত এই বইটির কোন সারমর্ম প্রদান করা হয় নি। :("
    else:
        dict['summary'] = cnt[14]

    if check_if_image_exists(id):
        dict['image'] = id
    else:
        dict['image'] = "book_image"


def check_if_image_exists(id):
    nam = 'static/images/rokomariapp/images/' + str(id) + '.jpg'
    if os.path.isfile(nam):
        return True
    return False
