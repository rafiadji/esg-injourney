from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from main.models import ActivityLog  # Sesuaikan dengan lokasi model Anda
from django.core.paginator import Paginator


@login_required(login_url='/')
def user_activity_list(request):
    context = {'menu' : 'activity'} # Inisialisasi context dictionary
    
    # Ambil aktivitas user yang sedang login
    if request.user.is_superuser:
        activities = ActivityLog.objects.all().order_by('-timestamp')
    else:
        activities = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    
    
    # Tambahkan pagination
    paginator = Paginator(activities, 20)  # 20 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context['activities'] = page_obj
    
    # Hitung statistik aktivitas (opsional)
    context['total_activities'] = activities.count()
    context['page_views'] = activities.filter(activity_type='VIEW').count()
    context['edits'] = activities.filter(activity_type='EDIT').count()
    
    return render(request, "list.html", context)