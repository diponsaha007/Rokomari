from django.shortcuts import render
import cx_Oracle
import os
from django.core.files.storage import FileSystemStorage

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')

conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.
def my_account(request):
    dict = {'logged_in': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = True
        dict['profile_info'] = get_profile_info(request.session['user_id'])
        print(dict)
    return render(request, "my_account/my_account.html", dict)

def update_personal(request):
    dict = {'logged_in': False}
    user_id = 0
    if request.session.has_key('user_id'):
        dict['logged_in'] = True
        user_id = request.session['user_id']

    username = request.POST.get("username")
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    email = request.POST.get("email")
    mobile_number = request.POST.get("mobile_number")

    result = conn.cursor()
    updatecmd = "UPDATE CUSTOMER SET USER_NAME = '" + username + "', FIRST_NAME = '" + first_name +"', LAST_NAME = '" + last_name +"', EMAIL = '" + email +"' WHERE USER_ID = " + str(user_id)
    result.execute(updatecmd)

    conn.commit()

    updatecmd = "UPDATE ADDRESS_DETAIL SET PHONE = '" + str(mobile_number) + "' WHERE USER_ID = " + str(user_id)
    result.execute(updatecmd)

    conn.commit()

    print(username, first_name, last_name, email, mobile_number)
    dict['profile_info'] = get_profile_info(user_id)
    print(dict)
    return render(request, "my_account/my_account.html", dict)

def update_contact(request):
    dict = {'logged_in': False}
    user_id = 0
    if request.session.has_key('user_id'):
        dict['logged_in'] = True
        user_id = request.session['user_id']


    present_address = request.POST.get("present_address")
    city = request.POST.get("city")
    country = request.POST.get("country")
    permanent_address = request.POST.get("permanent_address")

    result = conn.cursor()
    updatecmd = "UPDATE ADDRESS_DETAIL SET ADDRESS_1 = '" + present_address + "', ADDRESS_2 = '" + permanent_address +"', CITY = '" + city +"', COUNTRY = '" + country +"' WHERE USER_ID = " + str(user_id)
    result.execute(updatecmd)
    conn.commit()

    print(present_address, city, country, permanent_address)
    dict['profile_info'] = get_profile_info(user_id)
    print(dict)
    return render(request, "my_account/my_account.html", dict)

def update_photo(request):
    dict = {'logged_in': False}
    user_id = 0
    if request.session.has_key('user_id'):
        dict['logged_in'] = True
        user_id = request.session['user_id']

    folder = 'static/photos'

    myfile = request.FILES['filename']
    extension = myfile.name
    extension = extension.split('.')
    extension = extension[1]
    filename = str(user_id)+'.'+extension
    fs = FileSystemStorage(location=folder)  # defaults to   MEDIA_ROOT
    filename = fs.save(filename, myfile)
    file_url = fs.url(filename)

    dict['profile_info'] = get_profile_info(user_id)
    print(dict['profile_info'])
    return render(request, "my_account/my_account.html", dict)


def get_profile_info(id):
    result = conn.cursor()
    quercmd = "SELECT * FROM CUSTOMER C JOIN ADDRESS_DETAIL A  USING(USER_ID) WHERE USER_ID = "+ str(id)
    result.execute(quercmd)
    cnt = result.fetchone()
    l2 = []
    for j in cnt:
        l2.append(j)
    nam = 'static/photos/' + str(id) + '.jpg'
    nam2 = 'static/photos/' + str(id) + '.png'
    if os.path.isfile(nam):
        l2.append(l2[0])
        l2.append("jpg")
    elif os.path.isfile(nam2):
        l2.append(l2[0])
        l2.append("png")
    else:
        l2.append("static\backgroundimg\icons")
    #print(l2)
    return l2