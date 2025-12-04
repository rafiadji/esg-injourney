from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("category/<str:category>/", views.esgindex),
    path("get_data/<int:indicator>/<int:subindicator>", views.get_data),
    path("detail/<int:id>", views.get_data),
    path("get_subind/<int:val>", views.get_subind),
    path("get_subinddetail/<int:val>", views.get_subinddetail),
    path("get_leveldetail/<int:val>", views.get_leveldetail),
    path("add_column/<int:id>", views.add_column),
    
    path("detail/<int:id>", views.detail),
    path("form/<str:mode>/<int:id>", views.get_form),
    path('update_level_get', views.update_level_get, name='update_level_get'),
    path('update_weight', views.update_weight, name='update_weight'),
    path("get_detail_status/<int:id>", views.get_detail_status),
    path("get_detail_pic/<int:id>", views.get_detail_pic),
    path('import-excel/', views.import_excel, name='import_excel'),
    path('envindex/', views.envindex),
    path('socindex/', views.socindex),
    path('govindex/', views.govindex),
    path('workpaper_form/', views.workpaper_form),
    path('leveldetail/', views.leveldetail),
    # path('esgindex/<str:category>/', views.esgindex, name='esgindex'),
    path("upload/", views.upload_file),

]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
