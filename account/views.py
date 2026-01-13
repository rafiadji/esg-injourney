from django.shortcuts import render

from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout

from main.models import *

from datetime import datetime, timedelta

# Create your views here.
def index(request):
    return render(request, "landing.html")

def login_account(request):
    if request.method=="POST":
        r = request.POST
        username = r['username']
        password = r['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['selected_pic'] = 1
            if user.is_superuser == False:
                dt = UserDetail.objects.filter(user=user).first()
                request.session['role'] = dt.role
                
                pic = UserPIC.objects.filter(user=user).first()
                request.session['pic'] = pic.pic_id
                request.session['selected_pic'] = pic.pic_id
            return HttpResponseRedirect('dashboard/')
        else:
            return HttpResponseRedirect('/')
    if request.user.is_authenticated:
        return HttpResponseRedirect('dashboard/')
    else:
        return render(request, "login.html")

def logout_account(request):
    request.session.flush()
    logout(request)
    return HttpResponseRedirect('/')

def change_year(request, choose):
    request.session['tahun_periode'] = choose
    return JsonResponse({'status': 'success'})

def change_pic(request, choose):
    request.session['selected_pic'] = choose
    return JsonResponse({'status': 'success'})