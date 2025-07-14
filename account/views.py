from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout

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
            return HttpResponseRedirect('dashboard/')
        else:
            return HttpResponseRedirect('/')
    if request.user.is_authenticated:
        return HttpResponseRedirect('dashboard/')
    else:
        return render(request, "login.html")

def logout_account(request):
    logout(request)
    return HttpResponseRedirect('/')