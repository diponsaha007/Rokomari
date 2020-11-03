from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
import cx_Oracle
from argon2 import PasswordHasher as ph

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')

conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.
def login(request):
    # If user is already logged in then he cannot visit the login page
    if request.session.has_key('user_id'):
        return redirect(reverse('rokomariapp:index'))
    if request.method == 'POST':
        user_id = check_login(request)
        if user_id != -1:
            # this line here logs the user in
            request.session['user_id'] = user_id
            return redirect(reverse('rokomariapp:index'))
        else:
            # failed to enter
            dict = {'failed': True}
            return render(request, "login_registration/login.html", dict)
    return render(request, "login_registration/login.html")


def logout(request):
    # delete the users session. this logs the user out
    try:
        del request.session['user_id']
    except:
        pass
    return redirect(reverse('rokomariapp:index'))


def registration(request):
    # If user is already logged in then he cannot visit the registration page
    if request.session.has_key('user_id'):
        return redirect(reverse('rokomariapp:index'))
    if request.method == 'POST':
        res = check_registration(request)
        dict = {'can_reg': res}
        return render(request, "login_registration/registration.html", context=dict)
    return render(request, "login_registration/registration.html")


# These are helper functions for the views
def check_login(request):
    """
    Takes a POST request object and determines if the user can login
    :returns user_id if the user can login, -1 otherwise
    """
    username = str(request.POST['username'])
    password = str(request.POST['password'])
    result = conn.cursor()
    result.execute("SELECT USER_ID, USER_NAME,PASSWORD FROM ROKOMARIADMIN.CUSTOMER WHERE USER_NAME= :mybv",
                   mybv=username)
    cnt = result.fetchone()
    # username pai ni
    if cnt is None:
        return -1
    try:
        ph().verify(cnt[2], password)
        return cnt[0]
    except:
        return -1


def check_registration(request):
    """
    Takes a POST request object and determines if all the fields are valid
    so that the user can register.
    :returns 1 if all the fields are valid, -2 if username exists and -1 if fields are not valid.
    If returned 1 this function also adds the user to the database.
    """
    username = str(request.POST['username'])
    firstname = str(request.POST['firstname'])
    lastname = str(request.POST['lastname'])
    email = str(request.POST['email'])
    password = str(request.POST['password'])
    # using argon2 hashing for password
    password = ph().hash(password)
    address1 = str(request.POST['address1'])
    address2 = str(request.POST['address2'])
    city = str(request.POST['city'])
    country = str(request.POST['country'])
    phone = str(request.POST['phone'])
    # check if the lens are valid
    if len(username) > 512 or len(firstname) > 512 or len(lastname) > 512 or len(email) > 128:
        return -1
    if len(password) > 512 or len(address1) > 512 or len(address2) > 512 or len(city) > 128:
        return -1
    if len(country) > 128 or len(phone) > 30:
        return -1
    # check if this username already exists
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM ROKOMARIADMIN.CUSTOMER WHERE USER_NAME= :mybv", mybv=username)
    cnt = result.fetchone()
    if cnt is not None:
        # print("Already ache")
        return -2
    # get the maximum id till now
    result.execute("SELECT MAX(USER_ID) FROM ROKOMARIADMIN.CUSTOMER")
    # add 1 to the
    new_id = 1
    try:
        new_id = result.fetchone()[0] + 1
    except:
        pass
    result.execute(
        "INSERT INTO ROKOMARIADMIN.CUSTOMER (USER_ID,USER_NAME,FIRST_NAME,LAST_NAME,EMAIL,PASSWORD) VALUES(:p,:q,:r,:s,:t,:u)",
        [new_id, username, firstname, lastname, email, password])
    result.execute(
        "INSERT INTO ROKOMARIADMIN.ADDRESS_DETAIL (USER_ID,ADDRESS_1,ADDRESS_2,CITY,COUNTRY,PHONE) VALUES(:p,:q,:r,:s,:t,:u)",
        [new_id, address1, address2, city, country, phone])
    # committing to database
    conn.commit()
    return 1


#########        Admin Code            #########


def login_admin(request):
    # If user is already logged in then he cannot visit the login page
    if request.session.has_key('user_id'):
        return redirect(reverse('admin_dashboard:admin_dashboard'))
    if request.method == 'POST':
        user_id = check_login_admin(request)
        if user_id != -1:
            # this line here logs the user in
            request.session['user_id'] = user_id
            request.session['is_admin'] = True
            return redirect(reverse('admin_dashboard:admin_dashboard'))
        else:
            # failed to enter
            dict = {'failed': True}
            return render(request, "login_registration/login_admin.html", dict)
    return render(request, "login_registration/login_admin.html")


def logout_admin(request):
    # delete the users session. this logs the user out
    try:
        del request.session['user_id']
        del request.session['is_admin']
    except:
        pass
    return redirect(reverse('login_registration:login_admin'))


def registration_admin(request):
    # Only an admin can register another admin
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': False, 'is_admin': False}
        dict['logged_in'] = get_user_name_admin(request.session['user_id'])
        dict['is_admin'] = True
        if request.method == 'POST':
            res = check_registration_admin(request)
            dict['can_reg'] = res
            return render(request, "login_registration/registration_admin.html", context=dict)
        return render(request, "login_registration/registration_admin.html", dict)
    else:
        return redirect(reverse('rokomariapp:index'))


# These are helper functions for the views
def get_user_name_admin(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM ADMIN WHERE ADMIN_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])


def check_login_admin(request):
    """
    Takes a POST request object and determines if the user can login
    :returns user_id if the user can login, -1 otherwise
    """
    username = str(request.POST['username'])
    password = str(request.POST['password'])
    result = conn.cursor()
    result.execute("SELECT ADMIN_ID, USER_NAME,PASSWORD FROM ROKOMARIADMIN.ADMIN WHERE USER_NAME= :mybv",
                   mybv=username)
    cnt = result.fetchone()
    # username pai ni
    if cnt is None:
        return -1
    try:
        ph().verify(cnt[2], password)
        return cnt[0]
    except:
        return -1


def check_registration_admin(request):
    """
    Takes a POST request object and determines if all the fields are valid
    so that the user can register.
    :returns 1 if all the fields are valid, -2 if username exists and -1 if fields are not valid.
    If returned 1 this function also adds the user to the database.
    """
    username = str(request.POST['username'])
    firstname = str(request.POST['firstname'])
    lastname = str(request.POST['lastname'])
    email = str(request.POST['email'])
    password = str(request.POST['password'])
    # using argon2 hashing for password
    password = ph().hash(password)
    phone = str(request.POST['phone'])
    # check if the lens are valid
    if len(username) > 512 or len(firstname) > 512 or len(lastname) > 512 or len(email) > 128:
        return -1
    if len(password) > 512:
        return -1
    if len(phone) > 30:
        return -1
    # check if this username already exists
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM ROKOMARIADMIN.ADMIN WHERE USER_NAME= :mybv", mybv=username)
    cnt = result.fetchone()
    if cnt is not None:
        # print("Already ache")
        return -2
    # get the maximum id till now
    result.execute("SELECT MAX(ADMIN_ID) FROM ROKOMARIADMIN.ADMIN")
    # add 1 to the
    new_id = 1
    try:
        new_id = result.fetchone()[0] + 1
    except:
        pass
    result.execute(
        "INSERT INTO ROKOMARIADMIN.ADMIN (ADMIN_ID,USER_NAME,FIRST_NAME,LAST_NAME,EMAIL,PASSWORD, PHONE) VALUES(:p,:q,:r,:s,:t,:u, :v)",
        [new_id, username, firstname, lastname, email, password, phone])

    # committing to database
    conn.commit()
    return 1
