from django.shortcuts import render, redirect, reverse
import cx_Oracle
import os
from django.core.files.storage import FileSystemStorage

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.
def my_account(request):
    dict = {'logged_in': False, 'is_admin': False}

    if request.session.has_key('is_admin'):
        dict['logged_in'] = get_user_name_admin(request.session['user_id'])
        dict['profile_info'] = get_profile_info(request.session['user_id'])
        dict['is_admin'] = True
    elif request.session.has_key('user_id'):
        dict['logged_in'] = get_user_name(request.session['user_id'])
        dict['profile_info'] = get_profile_info(request.session['user_id'])

    return render(request, "my_account/my_account.html", dict)


def get_user_name(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM CUSTOMER WHERE USER_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])


def update_personal(request):
    if request.method == 'POST' and request.session.has_key('user_id'):
        user_id = request.session['user_id']
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        mobile_number = request.POST.get("mobile_number")
        result = conn.cursor()
        updatecmd = "UPDATE CUSTOMER SET USER_NAME = '" + username + "', FIRST_NAME = '" + first_name + "', LAST_NAME = '" + last_name + "', EMAIL = '" + email + "' WHERE USER_ID = " + str(
            user_id)
        result.execute(updatecmd)
        conn.commit()
        updatecmd = "UPDATE ADDRESS_DETAIL SET PHONE = '" + str(mobile_number) + "' WHERE USER_ID = " + str(user_id)
        result.execute(updatecmd)
        conn.commit()
    return redirect(reverse('my_account:my_account'))


def update_contact(request):
    if request.method == 'POST' and request.session.has_key('user_id'):
        user_id = request.session['user_id']
        present_address = request.POST.get("present_address")
        city = request.POST.get("city")
        country = request.POST.get("country")
        permanent_address = request.POST.get("permanent_address")

        result = conn.cursor()
        updatecmd = "UPDATE ADDRESS_DETAIL SET ADDRESS_1 = '" + present_address + "', ADDRESS_2 = '" + permanent_address + "', CITY = '" + city + "', COUNTRY = '" + country + "' WHERE USER_ID = " + str(
            user_id)
        result.execute(updatecmd)
        conn.commit()
    return redirect(reverse('my_account:my_account'))


def update_photo(request):
    if request.method == 'POST' and request.session.has_key('user_id'):
        user_id = request.session['user_id']
        check_and_delete_if_image_exists(user_id)
        folder = 'static/images/my_account'
        try:
            myfile = request.FILES['filename']
            extension = myfile.name
            extension = extension.split('.')
            extension = extension[1]
            filename = str(user_id) + '.' + 'jpg'
            fs = FileSystemStorage(location=folder)  # defaults to   MEDIA_ROOT
            filename = fs.save(filename, myfile)
            file_url = fs.url(filename)
        except:
            pass
    return redirect(reverse('my_account:my_account'))


def check_and_delete_if_image_exists(id):
    nam = 'static/images/my_account/' + str(id) + '.jpg'
    if os.path.isfile(nam):
        os.remove(nam)


def get_profile_info(id):
    result = conn.cursor()
    quercmd = "SELECT * FROM CUSTOMER C JOIN ADDRESS_DETAIL A  USING(USER_ID) WHERE USER_ID = " + str(id)
    result.execute(quercmd)
    cnt = result.fetchone()
    l2 = []
    for j in cnt:
        l2.append(j)
    nam = 'static/images/my_account/' + str(id) + '.jpg'
    # print(nam)
    if os.path.isfile(nam):
        # print("here")
        l2.append(nam)
    else:
        l2.append("static/images/my_account/default.jpg")
    # print(l2)
    return l2


def get_user_name_admin(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM ADMIN WHERE ADMIN_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])
