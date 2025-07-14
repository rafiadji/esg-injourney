from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index),
    path("detail/<int:id>", views.detail),
    path("form/<str:mode>/<int:id>", views.get_form),
    path('update_level_get', views.update_level_get, name='update_level_get'),
    path('update_weight', views.update_weight, name='update_weight'),
    path("get_detail_status/<int:id>", views.get_detail_status),
    path("get_detail_pic/<int:id>", views.get_detail_pic),
    path('import-excel/', views.import_excel, name='import_excel'),
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
