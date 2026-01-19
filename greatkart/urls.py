from django.contrib import admin
from django.urls import path, include
from . import views as main_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.home, name='home'),     # home page
    path('store/', include('store.urls')),  # <-- include your store app
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

