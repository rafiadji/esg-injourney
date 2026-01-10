from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.login_account),
    # path("login", views.login_account),
    path("logout", views.logout_account),
    path("change_year/<str:choose>", views.change_year),
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
