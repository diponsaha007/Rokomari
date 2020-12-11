from django.shortcuts import render, redirect, reverse
import cx_Oracle
import os
from django.core.files.storage import FileSystemStorage

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.
def add_new(request):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': get_user_name_admin(request.session['user_id']), 'is_admin': True}
        return render(request, "add_new_book/add_new_book.html", dict)
    else:
        return redirect(reverse('rokomariapp:index'))


def add_author(request):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': get_user_name_admin(request.session['user_id']), 'is_admin': True}
        if request.method == 'POST':
            update_author(request.POST.get("author_name"), request.POST.get("summary"))
            return redirect(reverse('admin_dashboard:admin_dashboard'))
        return render(request, "add_new_book/add_author.html", dict)
    else:
        return redirect(reverse('rokomariapp:index'))


def add_publisher(request):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': get_user_name_admin(request.session['user_id']), 'is_admin': True}
        if request.method == 'POST':
            update_publisher(request.POST.get("publisher_name"), request.POST.get("summary"))
            return redirect(reverse('admin_dashboard:admin_dashboard'))
        return render(request, "add_new_book/add_publisher.html", dict)
    else:
        return redirect(reverse('rokomariapp:index'))


def send_token(request):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': get_user_name_admin(request.session['user_id']), 'is_admin': True}
        if request.method == 'POST':
            update_token(request)
            return redirect(reverse('admin_dashboard:admin_dashboard'))
        return render(request, "add_new_book/send_token.html", dict)
    else:
        return redirect(reverse('rokomariapp:index'))


def update_token(request):
    admin_id = request.session['user_id']
    user_id = request.POST.get("user_id")
    expire_date = request.POST.get("expire_date")
    no_of_use = request.POST.get("no_of_use")
    min_order = request.POST.get("min_order")
    discount_amount = request.POST.get("discount_amount")
    if min_order < discount_amount:
        return
    result = conn.cursor()
    result.execute("SELECT NVL(MAX(TOKEN_ID),0)+1 FROM DISCOUNT_TOKEN")
    token_id = result.fetchone()[0]
    result.execute(
        "INSERT INTO DISCOUNT_TOKEN (TOKEN_ID, USER_ID, ADMIN_ID , EXPIRE_DATE , NO_OF_USE , MINIMUM_ORDER , DISCOUNT_AMOUNT) VALUES (:v1,:v2,:v3,TO_DATE(:v4, 'dd/mm/yyyy') , :v5,:v6,:v7)",
        v1=token_id, v2=user_id, v3=admin_id, v4=expire_date, v5=no_of_use, v6=min_order, v7=discount_amount)
    conn.commit()


def update_author(name, summary):
    result = conn.cursor()
    result.execute("SELECT MAX(AUTHOR_ID)+1 FROM AUTHOR")
    pub_id = result.fetchone()[0]
    result.execute("INSERT INTO AUTHOR (AUTHOR_ID,AUTHOR_NAME,AUTHOR_SUMMARY) VALUES (:v1,:v2,:v3)",
                   v1=pub_id, v2=name, v3=summary)
    conn.commit()


def update_publisher(name, summary):
    result = conn.cursor()
    result.execute("SELECT MAX(PUBLISHER_ID)+1 FROM PUBLISHER")
    pub_id = result.fetchone()[0]
    result.execute("INSERT INTO PUBLISHER (PUBLISHER_ID,PUBLISHER_NAME,PUBLISHER_SUMMARY) VALUES (:v1,:v2,:v3)",
                   v1=pub_id, v2=name, v3=summary)
    conn.commit()


def get_user_name(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM CUSTOMER WHERE USER_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])


def update_database(request):
    if request.method == 'POST' and request.session.has_key('user_id'):
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

        cmd_book_id = "SELECT MAX(BOOK_ID) FROM BOOK"
        cmd_author_id = "SELECT AUTHOR_ID FROM AUTHOR WHERE AUTHOR_NAME = '" + author + "'"
        cmd_publisher_id = "SELECT PUBLISHER_ID FROM PUBLISHER WHERE PUBLISHER_NAME = '" + publisher + "'"

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
            cmd_insert_author = "INSERT INTO AUTHOR (AUTHOR_ID, AUTHOR_NAME) VALUES(" + str(
                author_id) + ", '" + author + "' )"
            result.execute(cmd_insert_author)
            conn.commit()

        result.execute(cmd_publisher_id)
        try:
            publisher_id = result.fetchone()[0]
        except:
            result.execute("SELECT MAX(PUBLISHER_ID) FROM PUBLISHER")
            publisher_id = result.fetchone()[0] + 1
            cmd_insert_publisher = "INSERT INTO PUBLISHER (PUBLISHER_ID, PUBLISHER_NAME) VALUES(" + str(
                publisher_id) + ", '" + publisher + "' )"
            result.execute(cmd_insert_publisher)
            conn.commit()

        cmd_insert_book = "INSERT INTO BOOK (BOOK_ID, BOOK_NAME, BOOK_GENRE, BOOK_EDITION, AUTHOR_ID, PUBLISHER_ID, PRICE, DISCOUNT, COUNTRY, LANGUAGE, SUMMARY, ISBN, PAGES) " \
                          "VALUES(" + str(
            book_id) + ", '" + book_name + "', '" + book_genre + "', '" + edition + "', " + str(author_id) + ", " + str(
            publisher_id) + ", " + str(price) + ", " + str(
            discount) + ", '" + country + "', '" + language + "', '" + summary + "', '" + isbn + "', " + str(
            pages) + " )"
        print(book_id, author_id, publisher_id)
        result.execute(cmd_insert_book)
        conn.commit()
        update_photo(request, book_id)
        print(request.FILES)
    return redirect(reverse('admin_dashboard:admin_dashboard'))


def update_photo(request, book_id):
    try:
        folder = 'static/images/rokomariapp/images'
        myfile = request.FILES['filename']
        filename = str(book_id) + '.' + 'jpg'
        check_and_delete_if_book_image_exists(filename)
        fs = FileSystemStorage(location=folder)  # defaults to   MEDIA_ROOT
        filename = fs.save(filename, myfile)
        file_url = fs.url(filename)
    except:
        pass


def check_and_delete_if_book_image_exists(idname):
    nam = 'static/images/rokomariapp/images' + idname
    if os.path.isfile(nam):
        os.remove(nam)


def get_user_name_admin(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM ADMIN WHERE ADMIN_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])
