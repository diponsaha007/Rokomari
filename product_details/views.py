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
        "SELECT B.BOOK_ID, B.BOOK_NAME, A.AUTHOR_NAME, B.BOOK_GENRE, B.RATINGS, B.NO_OF_RATINGS, B.PRICE+ B.DISCOUNT, B.PRICE , C.PUBLISHER_NAME, B.ISBN, B.BOOK_EDITION, B.PAGES, B.COUNTRY, B.LANGUAGE, B.SUMMARY FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) JOIN PUBLISHER C USING(PUBLISHER_ID) WHERE B.BOOK_ID = :mybv",
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

    cntcmd1 = "SELECT COUNT(*) FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) WHERE (A.AUTHOR_NAME = :myauth AND B.BOOK_GENRE= :mygenre AND B.BOOK_ID <> :myid) ORDER BY RATINGS DESC, TOTAL_SOLD DESC"
    cntcmd2 = "SELECT COUNT(*) FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) WHERE ((A.AUTHOR_NAME = :myauth OR B.BOOK_GENRE= :mygenre) AND B.BOOK_ID <> :myid) ORDER BY RATINGS DESC,TOTAL_SOLD DESC"

    quercmd1 = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE,B.RATINGS FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) WHERE  (A.AUTHOR_NAME = :myauth AND B.BOOK_GENRE= :mygenre AND B.BOOK_ID <> :myid) ORDER BY RATINGS DESC,TOTAL_SOLD DESC"
    quercmd2 = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE,B.RATINGS FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) WHERE ((A.AUTHOR_NAME = :myauth OR B.BOOK_GENRE= :mygenre) AND B.BOOK_ID <> :myid) ORDER BY RATINGS DESC,TOTAL_SOLD DESC"
    quercmd3 = "SELECT B.BOOK_ID,B.BOOK_NAME,A.AUTHOR_NAME,B.PRICE,B.RATINGS FROM BOOK B JOIN AUTHOR A USING(AUTHOR_ID) WHERE (B.BOOK_ID <> :myid) ORDER BY RATINGS DESC,TOTAL_SOLD DESC"

    totalsimprod = 3

    result2 = conn.cursor()
    result2.execute(cntcmd1, myauth=dict['author_name'], mygenre=dict['genre'], myid=id)
    countrow1 = result2.fetchone()[0]
    # print(countrow1)

    result2 = conn.cursor()
    result2.execute(quercmd1, myauth=dict['author_name'], mygenre=dict['genre'], myid=id)
    simprods = result2.fetchmany(countrow1)
    prodnum = 1

    for row in simprods:
        bookid_key = "prod_" + str(prodnum) + "_book_id"
        bookname_key = "prod_" + str(prodnum) + "_book_name"
        authname_key = "prod_" + str(prodnum) + "_author_name"
        rating_key = "prod_" + str(prodnum) + "_rating"
        price_key = "prod_" + str(prodnum) + "_price"
        image_key = "prod_" + str(prodnum) + "_image"

        dict[bookid_key] = row[0]
        dict[bookname_key] = slice_name(str(row[1]))
        dict[authname_key] = row[2]
        dict[rating_key] = row[4]
        dict[price_key] = row[3]

        if check_if_image_exists(row[0]):
            dict[image_key] = row[0]
        else:
            dict[image_key] = "book_image"

        # print(dict[bookname_key])
        prodnum = prodnum + 1

    if countrow1 < totalsimprod:
        result2 = conn.cursor()
        result2.execute(cntcmd2, myauth=dict['author_name'], mygenre=dict['genre'], myid=id)
        countrow2 = result2.fetchone()[0]
        #print(countrow2)

        fetchnum = totalsimprod - countrow1
        if fetchnum > countrow2:
            fetchnum = countrow2
        result2 = conn.cursor()
        result2.execute(quercmd2, myauth=dict['author_name'], mygenre=dict['genre'], myid=id)
        simprods = result2.fetchmany(fetchnum)

        for row in simprods:
            bookid_key = "prod_" + str(prodnum) + "_book_id"
            bookname_key = "prod_" + str(prodnum) + "_book_name"
            authname_key = "prod_" + str(prodnum) + "_author_name"
            rating_key = "prod_" + str(prodnum) + "_rating"
            price_key = "prod_" + str(prodnum) + "_price"
            image_key = "prod_" + str(prodnum) + "_image"

            dict[bookid_key] = row[0]
            dict[bookname_key] = slice_name(str(row[1]))
            dict[authname_key] = row[2]
            dict[rating_key] = row[4]
            dict[price_key] = row[3]

            if check_if_image_exists(row[0]):
                dict[image_key] = row[0]
            else:
                dict[image_key] = "book_image"

            # print(dict[bookname_key])
            prodnum = prodnum + 1

        if (countrow2 + countrow1) < totalsimprod:
            fetchnum = totalsimprod - countrow1 - countrow2
            result2 = conn.cursor()
            result2.execute(quercmd3, myid=id)
            simprods = result2.fetchmany(fetchnum)

            for row in simprods:
                bookid_key = "prod_" + str(prodnum) + "_book_id"
                bookname_key = "prod_" + str(prodnum) + "_book_name"
                authname_key = "prod_" + str(prodnum) + "_author_name"
                rating_key = "prod_" + str(prodnum) + "_rating"
                price_key = "prod_" + str(prodnum) + "_price"
                image_key = "prod_" + str(prodnum) + "_image"

                dict[bookid_key] = row[0]
                dict[bookname_key] = slice_name(str(row[1]))
                dict[authname_key] = row[2]
                dict[rating_key] = row[4]
                dict[price_key] = row[3]

                if check_if_image_exists(row[0]):
                    dict[image_key] = row[0]
                else:
                    dict[image_key] = "book_image"

                # print(dict[bookname_key])
                prodnum = prodnum + 1


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
