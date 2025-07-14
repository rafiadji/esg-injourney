from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import *
from django.http import HttpResponseRedirect

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
    return render(request, "dashboard.html", context)

