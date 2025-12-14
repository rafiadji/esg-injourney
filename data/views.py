from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from main.models import *
import os
import json

import traceback  # Tambahkan ini di bagian import
import sys
import pandas as pd

from datetime import datetime, timedelta
context = {'menu' : 'data'}
@login_required(login_url='/')
# Create your views here.
def index(request):
    
    current_year = str(datetime.now().year)
    selected_year = request.session.get('tahun_periode', current_year)

    if not request.user.is_superuser:
        context['matlev_detail'] = TMatlevKriteriaDetail.objects.filter(
            tmatlevkriteriapic__pic__userpic__user=request.user,
    
            kriteria__year=selected_year  
        ).order_by('kriteria__indicator__id', 'id').distinct()
    else:
        context['matlev_detail'] = TMatlevKriteriaDetail.objects.filter(
    
            kriteria__year=selected_year  
        ).order_by('kriteria__indicator__id', 'id').all()
    for md in context['matlev_detail']:
        pic = TMatlevKriteriaPic.objects.filter(maturity_id=md.id)
        if pic.count() > 0:
            if pic.count() > 1 :
                list_pic = []
                for pc in pic:
                    list_pic.append(pc.pic.pic)
                pics = ', '.join(list_pic)
                md.pic = pics
            else:
                md.pic = pic.first().pic.pic
    if request.method=="POST":
        r = request.POST
        matlev_det = TMatlevKriteriaDetail.objects.get(id=r.get('maturity_id'))
        matlev_det.status = r.get('status')
        matlev_det.keterangan = r.get('keterangan')
        matlev_det.due_date = r.get('due_date') or None
        matlev_det.save()
        return HttpResponseRedirect('/data')
    return render(request, "data_list.html", context)

def detail(request, id):
    context['matlev_detail'] = TMatlevKriteriaDetail.objects.filter(id=id).first()
    context['column'] = TMatlevKriteriaColumn.objects.order_by('id').filter(maturity_id=context['matlev_detail'].id, show_table=True).exclude(column_type='sub')
    context['all_column'] = TMatlevKriteriaColumn.objects.order_by('id').filter(maturity_id=context['matlev_detail'].id).exclude(column_type='sub')
    
    column_tr = TRMatlev.objects.order_by('id').filter(maturity_id=context['matlev_detail'].id)
    column_value = []
    matlev_id = []
    
    for col_tr in column_tr:
        vl = TRMatlevColumn.objects.order_by('id').filter(matlev=col_tr)
        temp = []
        for val in vl:
            if val.column.show_table == True:
                if val.column.column_type == 'file':
                    temp.append((val.value_files, val.column.column_type))
                else:
                    temp.append((val.value, val.column.column_type))
        column_value.append(temp)
        matlev_id.append(col_tr.id)
    context['matlev'] = zip(matlev_id, column_value)
    return render(request, "data_detail.html", context)

def get_form(request, mode, id):
    matlev = TMatlevKriteriaDetail.objects.filter(id=id).first()
    context['matlev_detail'] = matlev
    # context['matlev_detail'] = TMatlevKriteriaDetail.objects.filter(id=id).first()
    year = []
    for x in range(2020, 2031):
        year.append(x)
    context['year'] = year
    context['month'] = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    
    if mode == 'add':
        context['matlev_title'] = matlev.maturity
        context['mode_title'] = 'Add Data Kertas Kerja'
        context['column'] = TMatlevKriteriaColumn.objects.order_by('id').filter(maturity_id=id)
    
        if request.method=="POST":
            r = request.POST
            rf = request.FILES
            user = request.user
            post = TRMatlev()
            post.user = user
            post.maturity = matlev
            post.kriteria = matlev.kriteria
            post.indicator = matlev.kriteria.indicator
            post.save()
            # print(f"Before save - Status: {matlev.status}")  
            matlev.status = 'submitted'
            matlev.save()
            # print(f"After save - Status: {matlev.status}") 
            for key, val in request.POST.items():
                if key != 'csrfmiddlewaretoken' and key != 'search_terms':
                    print(key)
                    col = TMatlevKriteriaColumn.objects.get(id=key)
                    in_t = TRMatlevColumn()
                    in_t.column = col
                    in_t.matlev = post
                    in_t.value = r.get(key)
                    in_t.save()
                    
            for key, val in request.FILES.items():
                col = TMatlevKriteriaColumn.objects.get(id=key)
                in_f = TRMatlevColumn()
                in_f.column = col
                in_f.matlev = post
                in_f.value_files = rf.get(key)
                in_f.save()
            return HttpResponseRedirect('/data/detail/'+str(context['matlev_detail'].id))
    else:
        context['matlev_title'] = matlev.maturity
        context['mode_title'] = 'Edit Data Kertas Kerja'
        context['column'] = TMatlevKriteriaColumn.objects.order_by('id').filter(maturity_id=id)

        matlev.status = 'submitted'
        matlev.save()
        for cl in context['column']:
            trans = TRMatlevColumn.objects.filter(matlev_id=mode, column_id=cl.id).first()
            if trans is not None:
                if cl.column_type == 'file':
                    cl.value = trans.value_files.name.replace('uploads/', '')
                else:
                    cl.value = trans.value
        
        if request.method=="POST":
            r = request.POST
            rf = request.FILES
            for key, val in request.POST.items():
                if key != 'csrfmiddlewaretoken' and key != 'search_terms':
                    col = TMatlevKriteriaColumn.objects.get(id=key)
                    in_t = TRMatlevColumn.objects.get(matlev_id=mode, column_id=key)
                    in_t.value = r.get(key)
                    in_t.save()
                    
            for key, val in request.FILES.items():
                col = TMatlevKriteriaColumn.objects.get(id=key)
                in_f = TRMatlevColumn.objects.get(matlev_id=mode, column_id=key)
                in_f.value_files = rf.get(key)
                in_f.save()
            return HttpResponseRedirect('/data/detail/'+str(context['matlev_detail'].id))
                    
    return render(request, "data_form.html", context)

def get_detail_pic(request, id):
    pic_list = TMatlevKriteriaPic.objects.order_by('id').filter(maturity_id=id).values('id', 'pic__pic')
    return JsonResponse({
        'success':True,
        'data':list(pic_list)
    })

def get_detail_status(request, id):
    detail_status = TMatlevKriteriaDetail.objects.filter(id=id).values()[0]
    return JsonResponse({
        'success':True,
        'data':detail_status
    })

def update_level_get(request):
    try:
        # Parse data dari request body
        data = json.loads(request.body)
        kriteria_id = data.get('id')
        new_level = data.get('level')
        
        # Validasi input
        if not kriteria_id or not new_level:
            return JsonResponse({'success': False, 'message': 'ID dan Level harus diisi'}, status=400)
        
        try:
            # Konversi new_level ke integer
            new_level = int(new_level)
            
            # Dapatkan objek kriteria
            kriteria = TMatlevKriteria.objects.get(id=kriteria_id)
            
            
            # Validasi level tidak melebihi max_level
            if kriteria.max_level and new_level > kriteria.max_level:
                return JsonResponse({
                    'success': False, 
                    'message': f'Level tidak boleh melebihi {kriteria.max_level}'
                }, status=400)
            
            detail_kriteria = TMatlevKriteriaDetail.objects.filter(kriteria_id=kriteria_id)
            for detail in detail_kriteria:
                if new_level >= detail.level:
                    detail.status='verified'
                    detail.save()
            # Update level_get
            kriteria.level_get = new_level
            
            kriteria.level_sum = new_level*kriteria.level_weight
            kriteria.save()
            

            return JsonResponse({
                'success': True, 
                'message': 'Level berhasil diperbarui',
                'new_level': new_level
            })
            
        except TMatlevKriteria.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Data kriteria tidak ditemukan'}, status=404)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Level harus berupa angka'}, status=400)
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)



def update_weight(request):
    try:
        # Parse data dari request body
        data = json.loads(request.body)
        kriteria_id = data.get('id')
        new_weight = data.get('weight')
        
        # Validasi input
        if not kriteria_id or not new_weight:
            return JsonResponse({'success': False, 'message': 'ID dan weight harus diisi'}, status=400)
        
        try:
            # Konversi new_weight ke integer
            new_weight = int(new_weight)
            
            # Dapatkan objek kriteria
            kriteria = TMatlevKriteria.objects.get(id=kriteria_id)
            
           
                
            # Update level_get
            kriteria.level_weight = new_weight
            kriteria.level_sum = new_weight*kriteria.level_get
            kriteria.save()
            

            return JsonResponse({
                'success': True, 
                'message': 'Level berhasil diperbarui',
                'new_level': new_weight
            })
            
        except TMatlevKriteria.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Data kriteria tidak ditemukan'}, status=404)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Level harus berupa angka'}, status=400)
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)



def import_excel(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():  # Mulai transaksi
                excel_file = request.FILES['excel_file']
                matlev_id = request.POST['matlev_id']
                user = request.user

                # Baca file excel
                df = pd.read_excel(excel_file)
                
                matlev = TMatlevKriteriaDetail.objects.get(id=matlev_id)
                
                # 1. Buat record TRMatlev (masih dalam transaksi)
                new_tr = TRMatlev.objects.create(
                    maturity_id=matlev_id,
                    kriteria=matlev.kriteria,
                    indicator=matlev.kriteria.indicator,
                    user=user
                )
                
                # 2. Ambil daftar kolom
                columns = TMatlevKriteriaColumn.objects.filter(
                    maturity_id=matlev_id
                ).exclude(column_type='sub')
                
                # 3. Validasi kolom excel vs database
                excel_columns = set(df.columns)
                required_columns = {col.column_name for col in columns if col.column_type != 'file'}
                missing_columns = required_columns - excel_columns
                
                if missing_columns:
                    raise ValueError(f"Kolom wajib tidak ditemukan: {', '.join(missing_columns)}")
                
                # 4. Persiapkan data untuk bulk_create
                data_to_create = []
                for index, row in df.iterrows():
                    for column in columns:
                        data_to_create.append(TRMatlevColumn(
                            matlev=new_tr,
                            column=column,
                            value=row.get(column.column_name) if column.column_type != 'file' else None,
                            value_files=row.get(column.column_name) if column.column_type == 'file' else None
                        ))
                
                # 5. Simpan semua data sekaligus
                TRMatlevColumn.objects.bulk_create(data_to_create)
                
                return JsonResponse({'success': True})

        except Exception as e:
            # Otomatis rollback semua operasi database dalam blok atomic()

            traceback.print_exc()  # Ini akan mencetak traceback lengkap
            print("\nError details:", str(e), file=sys.stderr)  # Print pesan error tambahan
            
            return JsonResponse({
                'success': False,
                'error': "Periksa Excel Anda kembali"
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


def envindex(request):
    return render(request, "envindex.html", context)
    
def socindex(request):
    return render(request, "socindex.html", context)

def govindex(request):
    return render(request, "govindex.html", context)

def workpaper_form(request):
    category = request.GET.get("cat")
    indicator = request.GET.get("ind")
    subindicator = request.GET.get("sub")
    idmatlev = request.GET.get("id")
    context['category'] = category
    context['matlevid'] = request.GET.get("id")
    # print(category)
    context['matlevind'] = TMatlevIndicator.objects.filter(id=indicator).order_by('number').values()
    context['matlevkrit'] = TMatlevKriteria.objects.filter(id=subindicator, indicator__id=indicator).order_by('number').values()
    # context['matlevsub'] = TMatlevKriteria.objects.filter(id=subindicator).order_by('number').values()
    context['matlevdet'] = TMatlevKriteriaDetail.objects.filter(kriteria_id = subindicator).order_by('-id').first()
    context['matlevcol'] = TMatlevKriteriaColumn.objects.filter(maturity_id = idmatlev).order_by('id').values()
    
    count = TMatlevKriteriaDetail.objects.filter(kriteria_id=subindicator).count()
    
    # context['matlev_id'] = matlev.id
    context['countlevel'] = count
    return render(request, "workpaper_form.html", context)

def leveldetail(request):

    idlev = request.GET.get('matlev')
    subindicator = request.GET.get('sub')
    indicator = request.GET.get('ind')
    context['category'] = request.GET.get('category')
    context['ind'] = request.GET.get('ind')
    context['sub'] = request.GET.get('sub')
    context['idlev'] = idlev
    context['matlev'] = TMatlevKriteriaDetail.objects.filter(id=idlev).first()
    context['matlevsubid'] = TMatlevKriteria.objects.filter(id=subindicator).first()
    return render(request, "level_detail.html", context)

def esgindex(request,category):
    
    
    if category == 'env':
        context['title'] = "Environment"
        context['subtitle'] = "We are committed to preserving the planet by reducing carbon footprints, managing natural resources responsibly, and driving eco-friendly innovation."
        context['imgurl'] = "assets/images/env.jpg"
        context['submenulist'] = TMatlevIndicator.objects.filter(pillar='env').order_by('number')
        for submenu in context['submenulist']:
            kriteria = TMatlevKriteria.objects.filter(indicator_id=submenu.id).order_by('number')
            submenu.kriteria = kriteria
        

    elif category == 'soc':
        context['title'] = "Social"
        context['subtitle'] = "Empowering communities through inclusion, employee well-being, and supporting fair, sustainable growth for all."
        context['imgurl'] = "assets/images/soc.jpg"
        context['submenulist'] = TMatlevIndicator.objects.filter(pillar='soc').order_by('number')
        for submenu in context['submenulist']:
            kriteria = TMatlevKriteria.objects.filter(indicator_id=submenu.id).order_by('number')
            submenu.kriteria = kriteria
        
        
    elif category == 'gov' :
        context['title'] = "Governance"
        context['subtitle'] = "Building trust with transparency, integrity, and responsible governance to create long-term value."
        context['imgurl'] = "assets/images/gov.jpg"
        context['submenulist'] = TMatlevIndicator.objects.filter(pillar='gov').order_by('number')
        for submenu in context['submenulist']:
            kriteria = TMatlevKriteria.objects.filter(indicator_id=submenu.id).order_by('number')
            submenu.kriteria = kriteria
        
    context['category'] = category
    return render(request, 'esgindex.html', context)

def get_data(request, indicator, subindicator):

    # return render(request, "level_detail.html", context)
    matlev = TMatlevKriteriaDetail.objects.filter(kriteria__id=subindicator, kriteria__indicator__id=indicator).order_by('level').values()
    counting_detail = TMatlevKriteriaDetail.objects.filter(kriteria_id=subindicator).count()
    # maxlevel = TMatlevKriteria.objects.filter(id=subindicator)
    
    return JsonResponse({
        "status": "success",
        "data":list(matlev),
        "counting_detail": counting_detail
        # "maxlevel" : maxlevel
    })
    

def get_subind(request, val):
    # print(val)
    matlev = TMatlevKriteria.objects.filter(indicator_id=val).order_by('number').values()
    return JsonResponse({
        "status": "success",
        "data":list(matlev)
    })
    
def get_subinddetail(request, val):
    # print(val)
    counting_detail = TMatlevKriteriaDetail.objects.filter(kriteria_id=val).count()
    if(counting_detail) : 
        matlev = TMatlevKriteriaDetail.objects.filter(kriteria__id=val).order_by('-level').first()
    else:
        matlev = []
    
    
    
    return JsonResponse({
        "status": "success",
        "data":list(matlev)
    })

def get_leveldetail(request, val):
    # print(val)
    matlev = TMatlevKriteriaDetail.objects.filter(id=val).order_by('level').values()
    return JsonResponse({
        "status": "success",
        "data":list(matlev)
    })



def upload_file(request):
    if request.method == "POST":
        print("File diterima:", request.FILES)
        return JsonResponse({"status": "ok"})


def add_column(request, id):
    matlevcolumn = TMatlevKriteriaColumn()
    matlevcolumn.maturity_id = id
    matlevcolumn.save()
    
    columnid = matlevcolumn.id
    
    return JsonResponse({
        "status": "success",
        "data":columnid
    })

def add_data(request, indicator, subindicator):
    # print(subindicator)
    counting_detail = TMatlevKriteriaDetail.objects.filter(kriteria_id=subindicator).count()
    if(counting_detail) : 
        matlev = TMatlevKriteriaDetail.objects.filter(kriteria__id=subindicator).order_by('-level').first()
    else:
        matlev = []
    
    matlev = TMatlevKriteriaDetail()
    matlev.kriteria_id = subindicator
    matlev.save()
    
    matlevid = matlev.id
    
    
    return JsonResponse({
        "status": "success",
        "data":matlevid
    })
        
    
def remove_column(request, id):
    # print(id)
    
    matlevcol = TMatlevKriteriaColumn.objects.get(id=id)
    matlevcol.delete()
    
    return JsonResponse({
        'success':True,
        # 'data':id
    })

def get_column(request, id):
    matlev_column = TMatlevKriteriaColumn.objects.order_by('id').filter(maturity_id=id).values()
    
    return JsonResponse({
        'success':True,
        'data':list(matlev_column)
    })

def save_column(request, id):
    column_id = request.GET.get('column_id')
    subcolumn_id = request.GET.get('subcolumn_id')
    column_name = request.GET.get('column_name')
    column_type = request.GET.get('column_type')
    column_hint = request.GET.get('column_hint')
    show_table = request.GET.get('show_table')
    maturity_id = request.GET.get('maturity_id')
    
    value_showtbl = True if show_table == "true" else False
    
    matlevcol = TMatlevKriteriaColumn()
    matlevcol.id = column_id
    matlevcol.column_name = column_name
    matlevcol.column_type = column_type
    matlevcol.hints = column_hint
    matlevcol.sub_column_id = subcolumn_id
    matlevcol.show_table = value_showtbl
    matlevcol.maturity_id = maturity_id
    matlevcol.save()
    
    return JsonResponse({
        'success':True,
        # 'data':list(data)
    })
    
def remove_form(request, id):
    
    matlevcol = TMatlevKriteriaColumn.objects.get(maturity_id=id)
    matlevcol.delete()
    
    matlev = TMatlevKriteriaDetail.objects.get(id=id)
    matlev.delete()
    
    return JsonResponse({
        'success':True,
        # 'data':id
    })
    
def save_form(request, id):
    
    
    matlevdet = TMatlevKriteriaDetail()
    matlevdet.id = id
    matlevdet.maturity = request.GET.get('maturity')
    matlevdet.level = request.GET.get('level')
    matlevdet.evidence = request.GET.get('evidence')
    matlevdet.data_type = request.GET.get('datatype')
    matlevdet.status = request.GET.get('status')
    matlevdet.kriteria_id = request.GET.get('kriteria_id')
    matlevdet.save()
    
    return JsonResponse({
        'success':True,
        # 'data':id
    })