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
    return render(request, "workpaper_form.html", context)

def leveldetail(request):
    context['category'] = request.GET.get('category')
    return render(request, "level_detail.html", context)

def esgindex(request,category):
    if category == 'env':
        context['title'] = "Environment"
        context['subtitle'] = "We are committed to preserving the planet by reducing carbon footprints, managing natural resources responsibly, and driving eco-friendly innovation."
        context['imgurl'] = "assets/images/env.jpg"
        context['submenulist'] = [
            'Climate Change Adaptation & Mitigation Actions',
            'GHG Emissions Management',
            'Waste Management',
            'Water Management',
            'Energy Management',
            'Environmental Management',
            'Biodiversity'
        ]
        context['titlecontent'] = "Climate Change Adaptation & Mitigation Actions"
        context['subtitlecontent'] = "Corporate Physical and Transition Risks"
        context['level'] = [
            {"level 1" : "The company has conveyed initial commitments or policies regarding the management of both physical and transitional climate risks and the climate risk governance."},
            {"level 2" : "The company has preparation of a climate change risk assessment. This assessment includes a more detailed risk identification and has been validated by the responsible unit."},
            {"level 3" : "The company has prepared mitigation actions for climate risk identification that are integrated with the risk register."}
        ]
        context['category'] = category
    elif category == 'soc':
        context['title'] = "Social"
        context['subtitle'] = "Empowering communities through inclusion, employee well-being, and supporting fair, sustainable growth for all."
        context['imgurl'] = "assets/images/soc.jpg"
        context['submenulist'] = [
            'Labor Practices (Diversity and Inclusion)',
            'Recruitment, Development, and Retention',
            'Safety and Health',
            'Consumer Relations',
            'Human Rights'
        ]
        context['titlecontent'] = "Labor Practices (Diversity and Inclusion)"
        context['subtitlecontent'] = "Labor Practices (Diversity and Inclusion)"
        context['level'] = [
            {"level 1" : "The company has initial commitments regarding labor practices (ex : equal remuneration, working hours, paying a living wage, workers annual leave, notice period before mass termination, prohibited discrimination and harassment)."},
            {"level 2" : "The company discloses data on women based on management level, employee data based on nationality or ethnicity and implements diversity initiatives and programs (e.g., DEI training)."},
            {"level 3" : "The company discloses data on women based on management level, employee data based on nationality or ethnicity and implements diversity initiatives and programs (e.g., DEI training)."}
        ]
        
    elif category == 'gov' :
        context['title'] = "Governance"
        context['subtitle'] = "Building trust with transparency, integrity, and responsible governance to create long-term value."
        context['imgurl'] = "assets/images/gov.jpg"
        context['submenulist'] = [
            'Business Ethics',
            'Supply Chai',
            'IT',
            'Human Rights'
        ]
        context['titlecontent'] = "Business Ethics"
        context['subtitlecontent'] = "Business Ethics"
        context['levels'] = [
            {"level 1" : "The company has a Code of Conduct in place which has been formally documented and socialized to employees and relevant stakeholders."},
            {"level 2" : "The company has established a Whistleblowing System (WBS) with a clear investigation Standard Opration Procedure."}
        ]
        
    context['category'] = category
    return render(request, 'esgindex.html', context)

def upload_file(request):
    if request.method == "POST":
        print("File diterima:", request.FILES)
        return JsonResponse({"status": "ok"})

