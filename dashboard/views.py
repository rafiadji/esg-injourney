from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import *
from django.http import HttpResponseRedirect
from django.db.models import IntegerField
from django.db.models.functions import Cast
import math

context = {'menu' : 'dashboard'}
@login_required(login_url='/')
# Create your views here.
def index(request):
    
    current_year = str(datetime.now().year)
    selected_year = request.session.get('tahun_periode', current_year)
    
    # Filter indicators by session year
    indicators = TMatlevIndicator.objects.filter(year=selected_year)
    gov = []
    env = []
    soc = []

    # GOVERNANCE
    for indicator in indicators.filter(pillar='gov'):
        kriteria_list = TMatlevKriteria.objects.filter(indicator=indicator)
        indicator_max_score = 0
        current_score = 0
        for kriteria in kriteria_list:
            indicator_max_score += kriteria.max_level
            current_score += kriteria.level_get 
        if len(kriteria_list) != 0 :
            indicator_max_score = indicator_max_score / len(kriteria_list)
            current_score = current_score / len(kriteria_list)
        gov.append({
            'indicator': indicator,
            'progress' : ((current_score / indicator_max_score) * 100) if indicator_max_score != 0 else 0,
            'indicator_max_score': indicator_max_score,
            'indicator_current_score': current_score,
            'kriteria': kriteria_list
        })
    # ENVIRONMENT
    for indicator in indicators.filter(pillar='env'):
        kriteria_list = TMatlevKriteria.objects.filter(indicator=indicator)
        indicator_max_score = 0
        current_score = 0
        for kriteria in kriteria_list:
            indicator_max_score += kriteria.max_level
            current_score += kriteria.level_get 
        if len(kriteria_list) != 0 :
            indicator_max_score = indicator_max_score / len(kriteria_list) 
            current_score = current_score / len(kriteria_list)
        env.append({
            'indicator': indicator,
            'progress' : ((current_score / indicator_max_score) * 100) if indicator_max_score != 0 else 0,
            'indicator_max_score': indicator_max_score,
            'indicator_current_score': current_score,
            'kriteria': kriteria_list
        })
    # SOCIAL
    for indicator in indicators.filter(pillar='soc'):
        kriteria_list = TMatlevKriteria.objects.filter(indicator=indicator)
        indicator_max_score = 0
        current_score = 0
        for kriteria in kriteria_list:
            indicator_max_score += kriteria.max_level
            current_score += kriteria.level_get 
        if len(kriteria_list) != 0 :
            indicator_max_score = indicator_max_score / len(kriteria_list)
            current_score = current_score / len(kriteria_list)
        soc.append({
            'indicator': indicator,
            'progress' : ((current_score / indicator_max_score) * 100) if indicator_max_score != 0 else 0,
            'indicator_max_score': indicator_max_score,
            'indicator_current_score': current_score,
            'kriteria': kriteria_list
        })
        

    gov_avg = sum(i['progress'] for i in gov) / len(gov) if gov else 0
    env_avg = sum(i['progress'] for i in env) / len(env) if env else 0
    soc_avg = sum(i['progress'] for i in soc) / len(soc) if soc else 0

    context['gov_progress'] = round(gov_avg, 2)
    context['env_progress'] = round(env_avg, 2)
    context['soc_progress'] = round(soc_avg, 2)


    context['gov'] = gov
    context['env'] = env
    context['soc'] = soc
    
    if request.user.is_superuser:
        context['matlev_detail'] = TMatlevKriteriaDetail.objects.order_by('kriteria__indicator__id', 'id').all()
    else:
        context['matlev_detail'] =  TMatlevKriteriaDetail.objects.filter(
            tmatlevkriteriapic__pic__userpic__user=request.user
        ).order_by('kriteria__indicator__id', 'id').distinct()
    
    #Emission
    emission = TREmission.objects.filter(year=selected_year)
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
    emission_reduce = TREmission.objects.annotate(year_int=Cast('year', IntegerField())).filter(year_int__lte=int(selected_year), category='reduction_total').order_by('year')
    reduce_emisi = 0
    year_reduce = []
    year_val_reduce = []
    
    for red in emission_reduce:
        if red.year == selected_year:
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
    
    context['scope1'] = scope1
    context['scope2'] = scope2
    context['scope3'] = scope3
    context['total_emission'] = total_emission
    context['reduce_emisi'] = abs(float(reduce_emisi))
    context['year_reduce'] = year_reduce
    context['year_val_reduce'] = year_val_reduce
    context['energy_consumption'] = energy_consumption
    context['water_consumption'] = water_consumption
    context['fuel_consumption'] = fuel_consumption
    context['b3'] = b3
    context['nonb3'] = nonb3
    context['waste_water'] = waste_water
    
    return render(request, "dashboard.html", context)

