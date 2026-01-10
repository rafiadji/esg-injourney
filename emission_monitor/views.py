from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect, JsonResponse
from main.models import *
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import IntegerField
from django.db.models.functions import Cast

from datetime import datetime, timedelta
import math

context = {'menu' : 'emission_monitor'}
@login_required(login_url='/')
# Create your views here.
def index(request):
    context['entity'] = MPic.objects.order_by('id').all()
    return render(request, "emission_monitor.html", context)

def get_location(request, pic, year):
    data = MLocation.objects.order_by('id').filter(pic_id=pic).values('id', 'location', 'lat', 'long', 'group__id', 'group__group', 'pic__id', 'pic__pic', 'pic__pic_icon', 'banjir', 'kekeringan', 'cuacaEkstrim', 'longsor')
    for dt in data:
        #Emission
        emission = TREmission.objects.filter(year=year, location_id=dt['id'])
        #scope1
        scope1 = 0
        for emisi in emission.filter(category='scope1'):
            scope1 = float(scope1) + float(emisi.value)
        
        #scope2
        scope2 = 0
        for emisi in emission.filter(category='scope2'):
            scope2 = float(scope2) + float(emisi.value)
            
        #scope3
        scope3 = 0
        for emisi in emission.filter(category='scope3'):
            scope3 = float(scope3) + float(emisi.value)
            
        total_emission = scope1 + scope2 + scope3
        
        #reduction
        emission_reduce = TREmission.objects.annotate(year_int=Cast('year', IntegerField())).filter(year_int__lte=int(year), category='reduction_total')
        reduce_emisi = 0
        year_reduce = []
        year_val_reduce = []
        
        for red in emission_reduce:
            if red.year == year:
                reduce_emisi = red.value
            year_reduce.append(red.year)
            year_val_reduce.append(red.value)
        
        #Energy Consumption
        energy_consumption = 0
        for emisi in emission.filter(category='energy_consumption'):
            energy_consumption = float(energy_consumption) + float(emisi.value)
        
        #Water Consumption
        water_consumption = 0
        for emisi in emission.filter(category='water_consumption_total'):
            water_consumption = float(water_consumption) + float(emisi.value)
        
        #Fuel Consumption
        fuel_consumption = 0
        for emisi in emission.filter(category='fuel_consumption'):
            fuel_consumption = float(fuel_consumption) + float(emisi.value)
        
        #B3
        b3 = 0
        for emisi in emission.filter(category='b3_total'):
            b3 = float(b3) + float(emisi.value)
        
        #nonB3
        nonb3 = 0
        for emisi in emission.filter(category='non_b3_total'):
            nonb3 = float(nonb3) + float(emisi.value)
        
        #waste water
        waste_water = 0
        for emisi in emission.filter(category='waste_water_total'):
            waste_water = float(waste_water) + float(emisi.value)
        
        dt['scope1'] = scope1
        dt['scope2'] = scope2
        dt['scope3'] = scope3
        dt['total_emission'] = total_emission
        dt['reduce_emisi'] = abs(float(reduce_emisi))
        dt['year_reduce'] = year_reduce
        dt['year_val_reduce'] = year_val_reduce
        dt['energy_consumption'] = energy_consumption
        dt['water_consumption'] = water_consumption
        dt['fuel_consumption'] = fuel_consumption
        dt['b3'] = b3
        dt['nonb3'] = nonb3
        dt['waste_water'] = waste_water
    
    return JsonResponse({
        "status": "success",
        "data":list(data)
    })