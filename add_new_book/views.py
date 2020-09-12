from django.shortcuts import render, redirect, reverse
import cx_Oracle
import os
from django.core.files.storage import FileSystemStorage

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.
def add_new(request):
    dict = {'logged_in': False, 'is_admin': False}

    if request.session.has_key('is_admin'):
        dict['logged_in'] = get_user_name_admin(request.session['user_id'])
        dict['is_admin'] = True
    elif request.session.has_key('user_id'):
        dict['logged_in'] = get_user_name(request.session['user_id'])
        dict['profile_info'] = get_profile_info(request.session['user_id'])

    return render(request, "add_new_book/add_new_book.html", dict)


def get_user_name(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM CUSTOMER WHERE USER_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])

def update_database(request):
    if request.method == 'POST' and request.session.has_key('user_id'):
        #print(request.POST.get("edition"))
        book_name = request.POST.get("book_name")
        book_genre = request.POST.get("book_genre")
        edition = request.POST.get("edition")
        author = request.POST.get("author")
        publisher = request.POST.get("publisher")
        price = request.POST.get("price")
        discount = request.POST.get("discount")
        country = request.POST.get("country")
        language = request.POST.get("language")
        summary = request.POST.get("summary")
        isbn = request.POST.get("isbn")
        pages = request.POST.get("pages")
        #print(book_name, book_genre)

        cmd_book_id ="SELECT MAX(BOOK_ID) FROM BOOK"
        cmd_author_id = "SELECT AUTHOR_ID FROM AUTHOR WHERE AUTHOR_NAME = '" + author +"'"
        cmd_publisher_id = "SELECT PUBLISHER_ID FROM PUBLISHER WHERE PUBLISHER_NAME = '" + publisher +"'"

        result = conn.cursor()
        result.execute(cmd_book_id)
        try:
            book_id = result.fetchone()[0] + 1
        except:
            pass

        result.execute(cmd_author_id)
        try:
            author_id = result.fetchone()[0]
        except:
            result.execute("SELECT MAX(AUTHOR_ID) FROM AUTHOR")
            author_id = result.fetchone()[0] + 1
            cmd_insert_author = "INSERT INTO AUTHOR (AUTHOR_ID, AUTHOR_NAME) VALUES(" + str(author_id) + ", '" + author + "' )"
            result.execute(cmd_insert_author)
            conn.commit()

        result.execute(cmd_publisher_id)
        try:
            publisher_id = result.fetchone()[0]
        except:
            result.execute("SELECT MAX(PUBLISHER_ID) FROM PUBLISHER")
            publisher_id = result.fetchone()[0] + 1
            cmd_insert_publisher = "INSERT INTO PUBLISHER (PUBLISHER_ID, PUBLISHER_NAME) VALUES("+ str(publisher_id) +", '"+ publisher +"' )"
            result.execute(cmd_insert_publisher)
            conn.commit()

        cmd_insert_book = "INSERT INTO BOOK (BOOK_ID, BOOK_NAME, BOOK_GENRE, BOOK_EDITION, AUTHOR_ID, PUBLISHER_ID, PRICE, DISCOUNT, COUNTRY, LANGUAGE, SUMMARY, ISBN, PAGES) " \
                          "VALUES("+ str(book_id) +", '"+ book_name +"', '"+ book_genre +"', '"+ edition +"', "+ str(author_id)+", "+ str(publisher_id) +", "+ str(price) +", "+ str(discount) +", '"+ country +"', '"+ language +"', '"+ summary +"', '"+ isbn +"', "+ str(pages) +" )"
        print(book_id, author_id, publisher_id)
        result.execute(cmd_insert_book)
        conn.commit()
        update_photo(request, book_id)
        print(request.FILES)
    return redirect(reverse('product_details:product_details', kwargs={'pk': book_id}))
    #return redirect(reverse('add_new_book:add_new'))

def update_photo(request, book_id):
        folder = 'static/images/rokomariapp/images'
        myfile = request.FILES['filename']
        filename = str(book_id) + '.' + 'jpg'

        fs = FileSystemStorage(location=folder)  # defaults to   MEDIA_ROOT
        filename = fs.save(filename, myfile)
        file_url = fs.url(filename)


def get_user_name_admin(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM ADMIN WHERE ADMIN_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])
