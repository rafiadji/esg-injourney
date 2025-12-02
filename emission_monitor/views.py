from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect, JsonResponse
from main.models import *
import json
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timedelta

context = {'menu' : 'emission_monitor'}
@login_required(login_url='/')
# Create your views here.
def index(request):
    print("tes")
    return render(request, "emission_monitor.html", context)