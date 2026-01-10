from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect, JsonResponse
from main.models import *
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from datetime import datetime, timedelta

context = {'menu' : 'master'}
@login_required(login_url='/')
# Create your views here.
def index(request):
    context['submenu'] = 'user'
    user = User.objects.filter(is_superuser=False)
    for usr in user:
        entity = UserPIC.objects.filter(user_id=usr.id).first()
        usr.pic = entity.pic.pic
        
        usrdet = UserDetail.objects.filter(user_id=usr.id).first()
        if usrdet.role == 'admin':
            role = 'Admin Branch'
        else :
            role = 'Contributor'
        usr.role = role
        
    context['data'] = user
    return render(request, "master_user.html", context)

def user_form(request, mode, id=None):
    context['entity'] = MPic.objects.order_by('id').all()
    context['mode'] = mode
    if mode == 'edit':
        context['data_user'] = User.objects.filter(id=id).first()
        context['detail_user'] = UserDetail.objects.filter(user_id=id).first()
        context['pic_user'] = UserPIC.objects.filter(user_id=id).first()
        context['group_edit'] = MGroup.objects.order_by('id').filter(pic_id=context['pic_user'].pic.id)
        context['location_edit'] = MLocation.objects.order_by('id').filter(pic_id=context['pic_user'].pic.id)
    else:
        context['data_user'] = []
        context['detail_user'] = []
        context['pic_user'] = []
        context['group_edit'] = []
        context['location_edit'] = []
    if request.method=="POST":
        r = request.POST
        if mode == 'add':
            usr = User()
            usr.username = r.get('username')
            usr.first_name = r.get('name')
            usr.email = r.get('email')
            usr.set_password(r.get('password'))
            usr.save()
            
            det = UserDetail()
            if r.get('location') != '':
                det.location = MLocation.objects.get(id=r.get('location'))
            det.user = usr
            det.role = r.get('role')
            det.save()
            
            pic = UserPIC()
            pic.pic = MPic.objects.get(id=r.get('entity'))
            pic.user = usr
            pic.save()
            
            return HttpResponseRedirect('/master')
        elif mode == 'edit':
            usr = User.objects.get(id=id)
            usr.username = r.get('username')
            usr.first_name = r.get('name')
            usr.email = r.get('email')
            usr.save()
            
            det = UserDetail.objects.get(user_id=id)
            if r.get('location') != '':
                det.location = MLocation.objects.get(id=r.get('location'))
            det.user = usr
            det.role = r.get('role')
            det.save()
            
            pic = UserPIC.objects.get(user_id=id)
            pic.pic = MPic.objects.get(id=r.get('entity'))
            pic.user = usr
            pic.save()
            
            return HttpResponseRedirect('/master')
    return render(request, "master_formuser.html", context)

def delete_usr(request, id):
    UserPIC.objects.filter(user_id=id).delete()
    UserDetail.objects.filter(user_id=id).delete()
    User.objects.filter(id=id).delete()
    return JsonResponse({
        'success':True
    })

def get_group_pic(request, id):
    group = MGroup.objects.order_by('id').filter(pic_id=id).values()
    return JsonResponse({
        'success':True,
        'data':list(group)
    })

def get_location(request, pic_id, grp_id=None):
    location = MLocation.objects.order_by('id').filter(pic_id=pic_id).values()
    if grp_id != None :
        location = MLocation.objects.order_by('id').filter(pic_id=pic_id,group_id=grp_id).values()
    return JsonResponse({
        'success':True,
        'data':list(location)
    })
    
def location(request):
    context['submenu'] = 'location'
    context['data'] = MLocation.objects.order_by('id').all()
    return render(request, "master_location.html", context)

def location_form(request, mode, id=None):
    context['entity'] = MPic.objects.order_by('id').all()
    if mode == 'edit':
        context['location_edit'] = MLocation.objects.filter(id=id).first()
    else:
        context['location_edit'] = []
    if request.method=="POST":
        r = request.POST
        if mode == 'add':
            loc = MLocation()
            loc.pic = MPic.objects.get(id=r.get('pic'))
            if r.get('group') != '':
                loc.group = MGroup.objects.get(id=r.get('group'))
            loc.location = r.get('location')
            loc.lat = r.get('lat')
            loc.long = r.get('long')
            loc.save()
            return HttpResponseRedirect('/master/location')
        elif mode == 'edit':
            loc = MLocation.objects.get(id=id)
            loc.pic = MPic.objects.get(id=r.get('pic'))
            if r.get('group') != '':
                loc.group = MGroup.objects.get(id=r.get('group'))
            loc.location = r.get('location')
            loc.lat = r.get('lat')
            loc.long = r.get('long')
            loc.save()
            return HttpResponseRedirect('/master/location')
    return render(request, "master_formlocation.html", context)
    
def entity(request):
    context['submenu'] = 'entity'
    context['data'] = MPic.objects.order_by('id').all()
    return render(request, "master_entitas.html", context)

def entity_form(request, mode, id=None):
    if mode == 'edit':
        context['entity_edit'] = MPic.objects.filter(id=id).first()
        context['group_edit'] = MGroup.objects.filter(pic_id=id).order_by('id')
    else:
        context['entity_edit'] = []
        context['group_edit'] = []
    if request.method=="POST":
        r = request.POST
        if mode == 'add':
            ent = MPic()
            ent.pic = r.get('pic')
            ent.save()
            for group in r.getlist('group'):
                grp = MGroup()
                grp.group = group
                grp.pic = ent
                grp.save()
            return HttpResponseRedirect('/master/entity')
        elif mode == 'edit':
            ent = MPic.objects.get(id=id)
            ent.pic = r.get('pic')
            ent.save()
            for group, group_id in zip(r.getlist('group'), r.getlist('group_id')):
                if group_id == '':
                    grp = MGroup()
                    grp.group = group
                    grp.pic = ent
                    grp.save()
                else:
                    grp = MGroup.objects.get(id=group_id)
                    grp.group = group
                    grp.save()
            return HttpResponseRedirect('/master/entity')
    return render(request, "master_formentitas.html", context)

def delete_grp(request, id):
    MGroup.objects.filter(id=id).delete()
    return JsonResponse({
        'success':True
    })

def delete_ent(request, id):
    MGroup.objects.filter(pic_id=id).delete()
    MPic.objects.filter(id=id).delete()
    return JsonResponse({
        'success':True
    })

def indicator(request):
    context['submenu'] = 'indicator'
    return render(request, "master_indicator.html", context)

def get_indicator_list(request, category):
    ind_list = TMatlevIndicator.objects.order_by('number').filter(pillar=category).values('id', 'indicator')
    for ind in ind_list:
        subind_list = TMatlevKriteria.objects.order_by('number').filter(indicator_id=ind['id']).values('id', 'kriteria')
        ind['subindicator'] = list(subind_list)
    return JsonResponse({
        'success':True,
        'data':list(ind_list)
    })

def indicator_form(request, category, mode, id=None):
    if mode == 'edit':
        context['indicator_edit'] = TMatlevIndicator.objects.filter(id=id).first()
        context['subindicator_edit'] = TMatlevKriteria.objects.filter(indicator_id=id).order_by('number')
    else:
        context['indicator_edit'] = []
        context['subindicator_edit'] = []
    if request.method=="POST":
        r = request.POST
        if mode == 'add':
            last_number = TMatlevIndicator.objects.filter(
                pillar=category
            ).order_by('-number').values_list('number', flat=True).first()
            ind = TMatlevIndicator()
            ind.pillar = category
            ind.number = (int(last_number) if last_number is not None else 0) + 1
            ind.indicator = r.get('indicator')
            ind.year = '2025'
            ind.save()
            for kriteria, max_level in zip(r.getlist('kriteria'), r.getlist('max_level')):
                last_number_sub = TMatlevKriteria.objects.filter(
                    indicator_id=ind.id
                ).order_by('-number').values_list('number', flat=True).first()
                krit = TMatlevKriteria()
                krit.number = (int(last_number_sub) if last_number_sub is not None else 0) + 1
                krit.kriteria = kriteria
                krit.max_level = max_level
                krit.level_get = 0
                krit.level_weight = 0
                krit.level_sum = 0
                krit.year = '2025'
                krit.indicator = ind
                krit.save()
            return HttpResponseRedirect('/master/indicator')
        elif mode == 'edit':
            ind = TMatlevIndicator.objects.get(id=id)
            ind.pillar = category
            ind.indicator = r.get('indicator')
            ind.year = '2025'
            ind.save()
            for kriteria, max_level, subind_id in zip(r.getlist('kriteria'), r.getlist('max_level'), r.getlist('subind_id')):
                print(subind_id)
                if subind_id == '':
                    last_number_sub = TMatlevKriteria.objects.filter(
                        indicator_id=ind.id
                    ).order_by('-number').values_list('number', flat=True).first()
                    krit = TMatlevKriteria()
                    krit.number = (int(last_number_sub) if last_number_sub is not None else 0) + 1
                    krit.kriteria = kriteria
                    krit.max_level = max_level
                    krit.level_get = 0
                    krit.level_weight = 0
                    krit.level_sum = 0
                    krit.year = '2025'
                    krit.indicator = ind
                    krit.save()
                else:
                    krit = TMatlevKriteria.objects.get(id=subind_id)
                    krit.kriteria = kriteria
                    krit.max_level = max_level
                    krit.level_get = 0
                    krit.level_weight = 0
                    krit.level_sum = 0
                    krit.year = '2025'
                    krit.indicator = ind
                    krit.save()
            return HttpResponseRedirect('/master/indicator')
            
    return render(request, "master_formindicator.html", context)

def delete_sub(request, id):
    TMatlevKriteria.objects.filter(id=id).delete()
    return JsonResponse({
        'success':True
    })

def delete_ind(request, id):
    TMatlevKriteria.objects.filter(indicator_id=id).delete()
    TMatlevIndicator.objects.filter(id=id).delete()
    return JsonResponse({
        'success':True
    })

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