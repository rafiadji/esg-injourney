from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index),
    path("user_form/<str:mode>/", views.user_form),
    path("user_form/<str:mode>/<int:id>", views.user_form),
    path("delete_usr/<int:id>", views.delete_usr),
    
    path("indicator", views.indicator),
    path("get_group_pic/<int:id>", views.get_group_pic),
    path("get_indicator_list/<str:category>", views.get_indicator_list),
    path("indicator_form/<str:category>/<str:mode>", views.indicator_form),
    path("indicator_form/<str:category>/<str:mode>/<int:id>", views.indicator_form),
    path("delete_sub/<int:id>", views.delete_sub),
    path("delete_ind/<int:id>", views.delete_ind),
    
    path("entity", views.entity),
    path("entity_form/<str:mode>/", views.entity_form),
    path("entity_form/<str:mode>/<int:id>", views.entity_form),
    path("delete_grp/<int:id>", views.delete_grp),
    path("delete_ent/<int:id>", views.delete_ent),
    
    path("detail/<int:id>", views.detail),
    path("form/<int:id>/<str:mode>", views.form),
    path("save_pic/<int:id>/<int:id_pic>", views.save_pic),
    path("remove_pic/<int:id>", views.remove_pic),
    path("save_maturity/<int:id>", views.save_maturity),
    path("remove_maturity/<int:id>/<int:id_kriteria>", views.remove_maturity),
    path("get_column/<int:id>", views.get_column),
    path("add_column/<int:id>", views.add_column),
    path("save_column/<int:id>", views.save_column),
    path("remove_column/<int:id>", views.remove_column),
    
    path("get_indicator/<str:pillar>", views.get_indicator),
    path("get_number/<int:id>", views.get_number),
    path("get_pic_master/<int:id>", views.get_pic_master),
    path("get_pic_list/<int:id>", views.get_pic_list),
    path("get_edit_kriteria/<int:id>", views.get_edit_kriteria),
    path("delete_maturity/<int:id>", views.delete_maturity),
    path("delete_kriteria/<int:id>", views.delete_kriteria),
    path('set-tahun-session/', views.set_tahun_session, name='set_tahun_session'),
    path("mast_form/", views.mast_form),
    path('mast_formind/', views.mast_formind),
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
