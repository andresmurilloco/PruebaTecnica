from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Ruta del panel de administración de Django
    path('', include('pdf_app.urls')),  # Incluir las rutas de la aplicación pdf_app
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
