from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    dict = {'logged_in': False}
    if request.session.has_key('user_id'):
        dict['logged_in'] = True
    return render(request, "rokomariapp/index.html", dict)
