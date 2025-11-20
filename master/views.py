from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect, JsonResponse
from main.models import *
import json
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timedelta

context = {'menu' : 'master'}
@login_required(login_url='/')
# Create your views here.
def index(request):
    # [PERUBAHAN 1] Ambil tahun dari session
    current_year = str(datetime.now().year)
    selected_year = request.session.get('tahun_periode', current_year)
    
    # [PERUBAHAN 2] Tambah filter tahun di query utama
    context['matlev_kriteria'] = TMatlevKriteria.objects.filter(
        year=selected_year
    ).order_by('indicator__id').all()
    
    if request.method == "POST":
        r = request.POST
        if r['kriteria_id'] == 'add':
            indicator = TMatlevIndicator.objects.get(id=r.get('indicator'))
            post = TMatlevKriteria()
            post.indicator = indicator
            post.number = r.get('number')
            post.kriteria = r.get('kriteria')
            post.max_level = 3
            post.level_get = 0
            post.level_sum = 0
            post.level_weight = 0
            # [PERUBAHAN 3] Gunakan selected_year dari session untuk tahun baru
            post.year = selected_year
            post.save()
        else:
            post = TMatlevKriteria.objects.get(id=r.get('kriteria_id'))
            post.kriteria = r.get('kriteria')
            post.save()
        return HttpResponseRedirect('/master')
            
    return render(request, "master_kriteria.html", context)

def detail(request, id):
    context['matlev_kriteria'] = TMatlevKriteria.objects.filter(id=id).first()
    context['counter_matlev'] = TMatlevKriteriaDetail.objects.filter(kriteria_id=id).count()
    context['matlev'] = TMatlevKriteriaDetail.objects.order_by('level').filter(kriteria_id=id)
    return render(request, "master_detail.html", context)

def form(request, id, mode):
    if mode == 'add':
        kriteria = TMatlevKriteria.objects.get(id=id)
        counting_detail = TMatlevKriteriaDetail.objects.filter(kriteria_id=id).count()
        context['titlle_form'] = 'Tambah Indikasi Kematangan'
        
        post = TMatlevKriteriaDetail()
        post.level = counting_detail + 1
        post.kriteria = kriteria
        post.status = 'on progress'
        post.save()
        
        context['matlev_detail'] = post
    else:
        context['titlle_form'] = 'Ubah Indikasi Kematangan'
        post = TMatlevKriteriaDetail.objects.filter(id=mode).first()
        context['matlev_detail'] = post
        
    context['matlev_kriteria'] = TMatlevKriteria.objects.filter(id=id).first()
    context['pic_list'] = MPic.objects.order_by('id').all()
    context['mode'] = mode
    return render(request, "master_form.html", context)

def save_pic(request, id, id_pic):
    maturity = TMatlevKriteriaDetail.objects.get(id=id)
    pic = MPic.objects.get(id=id_pic)
    matlev_pic = TMatlevKriteriaPic()
    matlev_pic.maturity = maturity
    matlev_pic.pic = pic
    matlev_pic.save()
    
    return JsonResponse({
        'success':True,
        'data':''
    })

def remove_pic(request, id):
    matlev_pic = TMatlevKriteriaPic.objects.get(id=id)
    matlev_pic.delete()
    
    return JsonResponse({
        'success':True,
        'data':''
    })

def save_maturity(request, id):
    r = request.POST
    maturity = TMatlevKriteriaDetail.objects.get(id=id)
    maturity.maturity = r.get('maturity')
    maturity.evidence = r.get('evidence')
    maturity.data_type = r.get('data_type')
    maturity.save()
    
    return JsonResponse({
        'success':True,
        'data':''
    })

def remove_maturity(request, id, id_kriteria):
    try:
        TMatlevKriteriaPic.objects.get(maturity_id=id).delete()
    except ObjectDoesNotExist:
        print('PIC None')
    
    try:
        TMatlevKriteriaColumn.objects.get(maturity_id=id).delete()
    except ObjectDoesNotExist:
        print('Column None')
    
    TMatlevKriteriaDetail.objects.get(id=id).delete()
    
    return HttpResponseRedirect('/master/detail/' + str(id_kriteria))

def add_column(request, id):
    maturity = TMatlevKriteriaDetail.objects.get(id=id)
    post = TMatlevKriteriaColumn()
    post.maturity = maturity
    post.save()
    
    return JsonResponse({
        'success':True,
        'data':''
    })

def get_column(request, id):
    matlev_column = TMatlevKriteriaColumn.objects.order_by('id').filter(maturity_id=id).values()
    
    return JsonResponse({
        'success':True,
        'data':list(matlev_column)
    })

def save_column(request, id):
    r = request.POST
    sub = None
    if r.get('sub_column') != '':
        sub = TMatlevKriteriaColumn.objects.get(id=r.get('sub_column'))
    matlev_column = TMatlevKriteriaColumn.objects.get(id=id)
    matlev_column.column_name = r.get('column_name')
    matlev_column.column_type = r.get('column_type')
    matlev_column.hints = r.get('hints')
    matlev_column.sub_column = sub
    matlev_column.show_table = True if r.get('show_table') == 'true' else False
    if 'negative' in r:
        matlev_column.negative_input = True if r.get('negative') == 'true' else False
    if 'equation' in r:
        matlev_column.equation = r.get('equation')
    matlev_column.save()
    
    return JsonResponse({
        'success':True,
        'data':''
    })

def remove_column(request, id):
    TMatlevKriteriaColumn.objects.get(id=id).delete()
    
    return JsonResponse({
        'success':True,
        'data':''
    })

def get_pic_master(request, id):
    pic_list = MPic.objects.order_by('id').exclude(id__in=TMatlevKriteriaPic.objects.filter(maturity_id=id).values('pic')).values()
    return JsonResponse({
        'success':True,
        'data':list(pic_list)
    })

def get_pic_list(request, id):
    pic_list = TMatlevKriteriaPic.objects.order_by('id').filter(maturity_id=id).values('id', 'pic__pic')
    return JsonResponse({
        'success':True,
        'data':list(pic_list)
    })

def get_indicator(request, pillar):
    indicator = TMatlevIndicator.objects.order_by('id').filter(pillar=pillar).values()
    return JsonResponse({
        'success':True,
        'data':list(indicator)
    })
    
def get_number(request, id):
    indicator = TMatlevIndicator.objects.filter(id=id).first()
    counter = TMatlevKriteria.objects.filter(indicator_id=id).count()
    number = str(indicator.number) + '.' + str(counter + 1)
    return JsonResponse({
        'success':True,
        'number':number
    })

def get_edit_kriteria(request, id):
    indicator = TMatlevKriteria.objects.filter(id=id).values('id', 'indicator__pillar', 'indicator__id', 'indicator__indicator', 'number', 'kriteria')[0]
    return JsonResponse({
        'success':True,
        'data':indicator
    })
    
def delete_maturity(request, id):
    try:
        TMatlevKriteriaPic.objects.get(maturity_id=id).delete()
    except ObjectDoesNotExist:
        print('PIC None')
    
    try:
        TMatlevKriteriaColumn.objects.get(maturity_id=id).delete()
    except ObjectDoesNotExist:
        print('Column None')
    
    TMatlevKriteriaDetail.objects.get(id=id).delete()
    
    return JsonResponse({
        'success':True,
        'data':''
    })

def delete_kriteria(request, id):
    check = TRMatlev.objects.filter(kriteria_id=id).count()
    indicator_id = TMatlevKriteria.objects.get(id=id).indicator.id
    indicator_num = TMatlevKriteria.objects.get(id=id).indicator.number
    if check > 0:
        return JsonResponse({
            'success':False,
            'message':'Data Ini Tidak Bisa Dihapus, Sudah DI Isi oleh PIC'
        })
        
    try:
        TMatlevKriteriaPic.objects.get(maturity_id__in=TMatlevKriteriaDetail.objects.filter(kriteria_id=id).values('id')).delete()
    except ObjectDoesNotExist:
        print('PIC None')
    
    try:
        TMatlevKriteriaColumn.objects.get(maturity_id__in=TMatlevKriteriaDetail.objects.filter(kriteria_id=id).values('id')).delete()
    except ObjectDoesNotExist:
        print('Column None')
    
    try:
        TMatlevKriteriaDetail.objects.get(kriteria_id=id).delete()
    except ObjectDoesNotExist:
        print('Detail None')
    
    TMatlevKriteria.objects.get(id=id).delete()
    
    reset_num = TMatlevKriteria.objects.order_by('id').filter(indicator_id=indicator_id)
    if reset_num.count() > 1:
        counting = 1
        for rn in reset_num:
            rn.number = str(indicator_num) + str(counting)
            rn.save()
            counting = counting + 1
    
    return JsonResponse({
        'success':True,
        'data':''
    })

@csrf_exempt
def set_tahun_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['tahun_periode'] = data.get('tahun_periode', '2024')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def mast_form(request):
    # if submenu == 'user':
    #         context['title'] = "Users"
    #         context['entity'] = [
    #             'InJourney Holding',
    #             'InJourney Airport',
    #             'InJourney Aviation',
    #             'InJourney Retail',
    #             'InJourney Hospitality',
    #             'InJourney Destination Management',
    #             'InJourney Tourism Development Corporation'
    #         ]
    #         context['username'] = [
    #             'admin'
    #         ]
    #         context['email'] = [
    #             'Admin@injourney.id',
    #             'admin_airport@injourney.id',
    #             'Admin_avtiation@injourney.id',
    #             'Admin_retail@injourney.id',
    #             'Admin_hospitality@injourney.id',
    #             'Admin_destination@injourney.id',
    #             'Admin_torism@injourney.id'
    #         ]
    #         context['email'] = [
    #             'Super Admin'
    #         ]
    # elif submenu == 'role':
    #         context['title'] = "Role"
            
    # elif submenu == 'indicator':
    #         context['title'] = "Indicator"
    #         context['indicatorname'] = [
    #             'Climate Change Adaptation & Mitigation Actions',
    #             'Climate Change Adaptation & Mitigation Actions',
    #             'GHG Emissions Management'
    #         ]
    #         context['subindicatorname'] = [
    #             'Corporate Physical and Transition Risks',
    #             'Financial Risks Due to Climate Change',
    #             'Greenhouse Gas Emissions Scope 1, 2, and 3'
    #         ]
    return render(request, "mast_form.html", context)

def mast_formind(request):
    return render(request, "mast_formind.html", context)