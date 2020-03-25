from django.contrib import admin
from  django.conf.urls import  url
from django.urls import path,include
from  django.views.generic import TemplateView
from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include("search.urls")),
    path('',include("user.urls")),

    # path('captcha/', include('captcha.urls'))
]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

