from django.shortcuts import render, redirect, reverse
from json import dumps
import cx_Oracle
import os

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='globaldb')
conn = cx_Oracle.connect(user='ROKOMARIADMIN', password='ROKADMIN', dsn=dsn_tns)


# Create your views here.

def admin_dashboard(request):
    if request.session.has_key('user_id') and request.session.has_key('is_admin'):
        dict = {'logged_in': False, 'is_admin': False}
        dict['logged_in'] = get_user_name_admin(request.session['user_id'])
        dict['is_admin'] = True
        dict['monthly_sell'] = dumps(get_monthly_earnings())
        dict['genre_sell'] = dumps(get_genre_sell())
        dict['monthly_avg'] = get_monthly_avg()
        dict['annual_avg'] = get_annual_avg()
        dict['current_year_income'] = get_current_year_earning()
        dict['pending_orders'] = get_pending_orders(request.session['user_id'])
        dict['best_buyers'] = get_best_buyers()
        dict['recent_orders'] = get_order_list(request.session['user_id'])
        return render(request, "admin_dashboard/admin_dashboard.html", dict)
    else:
        return redirect(reverse('rokomariapp:index'))


def get_order_list(admin_id):
    result = conn.cursor()
    result.execute(
        "SELECT O.ORDER_ID , (SELECT X.FIRST_NAME || ' '|| X.LAST_NAME FROM CUSTOMER X WHERE X.USER_ID = O.USER_ID) AS \"NAME\" , TO_CHAR(ORDER_DATE,'DD, Month, YYYY') , TO_CHAR(RECEIVED_DATE,'DD, Month, YYYY'),O.ORDER_LOCATION ,(SELECT SUM(X.QUANTITY * X.PRICE_PER_BOOK) FROM ORDER_DETAILS X WHERE X.ORDER_ID = O.ORDER_ID) FROM ORDER_LIST O WHERE O.ADMIN_ID = :bv ORDER BY RECEIVED_DATE DESC,ORDER_DATE DESC",
        bv=admin_id)
    li = []
    koto = 0
    while (True):
        cnt = result.fetchone()
        if cnt is None:
            break
        if len(li) >= 10 and koto >= 4:
            break
        tmp = []
        for i in range(len(cnt)):
            tmp.append(cnt[i])
        if tmp[3] is None:
            tmp[3] = "---"
            tmp.append(0)
        else:
            tmp.append(1)
            koto += 1
        result2 = conn.cursor()
        result2.execute("SELECT  DISCOUNT FROM ORDER_LIST WHERE ORDER_ID = :v1", v1=tmp[0])
        tmp[5] -= int(result2.fetchone()[0])
        tmp[5] += 60
        li.append(tmp)
    # print(li)
    return li


def get_best_buyers():
    result = conn.cursor()
    result.execute(
        "SELECT OL.USER_ID ,(SELECT FIRST_NAME || ' ' || LAST_NAME FROM CUSTOMER WHERE USER_ID = OL.USER_ID) AS \"NAME\", SUM((SELECT SUM(OD.QUANTITY) FROM ORDER_DETAILS OD WHERE OD.ORDER_ID = OL.ORDER_ID )) AS \"QUANTITY\" ,SUM((SELECT SUM(OD.PRICE_PER_BOOK * OD.QUANTITY) FROM ORDER_DETAILS OD WHERE OD.ORDER_ID = OL.ORDER_ID )) AS \"PRICE\"  FROM ORDER_LIST OL GROUP BY OL.USER_ID ORDER BY \"PRICE\" DESC")
    li = []
    while (True):
        cnt = result.fetchone()
        if cnt is None:
            break
        if len(li) >= 10:
            break
        tmp = []
        for i in range(len(cnt)):
            tmp.append(cnt[i])
        tmp.append(check_file(cnt[0]))
        li.append(tmp)
    # print(li)
    return li


def check_file(user_id):
    nam = 'static/images/my_account/' + str(user_id) + '.jpg'
    if os.path.isfile(nam):
        return nam
    else:
        return 'static/images/my_account/' + 'default.jpg'


def get_genre_sell():
    result = conn.cursor()
    result.execute(
        "SELECT B.BOOK_GENRE AS \"GENRE\",ROUND((SELECT  SUM(OD.QUANTITY) FROM ORDER_LIST OL,ORDER_DETAILS OD WHERE EXTRACT(YEAR FROM OL.ORDER_DATE)=2020 AND OL.ORDER_ID = OD.ORDER_ID AND B.BOOK_GENRE = (SELECT X.BOOK_GENRE FROM BOOK X WHERE X.BOOK_ID = OD.BOOK_ID) )/(SELECT  SUM(OD.QUANTITY) FROM ORDER_LIST OL,ORDER_DETAILS OD WHERE EXTRACT(YEAR FROM OL.ORDER_DATE)=2020 AND OL.ORDER_ID = OD.ORDER_ID)*100,2 )AS \"CNT\" FROM BOOK B  GROUP BY B.BOOK_GENRE ORDER BY CNT DESC NULLS LAST")
    li = []
    total = 100.00
    while (True):
        cnt = result.fetchone()
        if cnt is None:
            break
        if len(li) >= 10:
            break
        tmp = []
        tmp.append(cnt[0])
        tmp.append(cnt[1])
        li.append(tmp)
        total -= cnt[1]
    if total > 0:
        li.append(['Others', total])
    # print(li)
    return li


def get_pending_orders(admin_id):
    result = conn.cursor()
    result.execute("SELECT COUNT(*) FROM ORDER_LIST WHERE RECEIVED_DATE IS NULL AND ADMIN_ID = :bv1", bv1=admin_id)
    return result.fetchone()[0]


def get_current_year_earning():
    result = conn.cursor()
    result.execute(
        "SELECT YEAR, SUM( EARNINGS ) AS \"SUM_EARN\" FROM ( SELECT TO_CHAR( O.ORDER_DATE, 'yyyy' ) AS \"YEAR\",( SELECT SUM( X.PRICE_PER_BOOK ) FROM ORDER_DETAILS X WHERE X.ORDER_ID = O.ORDER_ID ) AS \"EARNINGS\" FROM ORDER_LIST O WHERE extract(YEAR from O.ORDER_DATE) = 2020 ) GROUP BY YEAR ORDER BY TO_DATE( YEAR, 'YYYY' )")
    return result.fetchone()[1]


def get_annual_avg():
    result = conn.cursor()
    result.execute(
        "SELECT ROUND( AVG( SUM_EARN ) ) FROM (SELECT YEAR, SUM( EARNINGS ) AS \"SUM_EARN\" FROM ( SELECT TO_CHAR( O.ORDER_DATE, 'yyyy' ) AS \"YEAR\",( SELECT SUM( X.PRICE_PER_BOOK ) FROM ORDER_DETAILS X WHERE X.ORDER_ID = O.ORDER_ID ) AS \"EARNINGS\" FROM ORDER_LIST O ) GROUP BY YEAR ORDER BY TO_DATE( YEAR, 'YYYY' ) )")
    return result.fetchone()[0]


def get_monthly_avg():
    result = conn.cursor()
    result.execute(
        "SELECT ROUND(AVG(SUM_EARN)) FROM ( SELECT MONTH , SUM(EARNINGS) AS \"SUM_EARN\" FROM (SELECT TO_CHAR(O.ORDER_DATE , 'Mon') AS \"MONTH\" , (SELECT SUM(X.PRICE_PER_BOOK) FROM ORDER_DETAILS X WHERE X.ORDER_ID = O.ORDER_ID) AS \"EARNINGS\" FROM ORDER_LIST O WHERE extract(YEAR from O.ORDER_DATE) = 2020 ) GROUP BY MONTH ORDER BY TO_DATE(MONTH, 'Mon') )"
    )
    return result.fetchone()[0]


def get_monthly_earnings():
    result = conn.cursor()
    result.execute(
        "SELECT MONTH , SUM(EARNINGS) FROM (SELECT TO_CHAR(O.ORDER_DATE , 'Mon') AS \"MONTH\" , (SELECT SUM(X.PRICE_PER_BOOK) FROM ORDER_DETAILS X WHERE X.ORDER_ID = O.ORDER_ID) AS \"EARNINGS\" FROM ORDER_LIST O WHERE extract(YEAR from O.ORDER_DATE) = 2020 ) GROUP BY MONTH ORDER BY TO_DATE(MONTH, 'Mon')")
    li = []
    while (True):
        cnt = result.fetchone()
        if cnt is None:
            break
        tmp = []
        tmp.append(cnt[0])
        tmp.append(cnt[1])
        li.append(tmp)
    # print(li)
    return li


def get_user_name_admin(user_id):
    result = conn.cursor()
    result.execute("SELECT USER_NAME FROM ADMIN WHERE ADMIN_ID = :bv1", bv1=user_id)
    return str(result.fetchone()[0])
