# pdf_app/urls.py
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import DocumentoPDFViewSet, UsuarioPersonalizadoViewSet, home_view
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

# Router para los viewsets
router = DefaultRouter()
router.register(r'documentos', DocumentoPDFViewSet)
router.register(r'usuarios', UsuarioPersonalizadoViewSet)

urlpatterns = [
    # Ruta para el home de la API
    path('', home_view, name='home'),  
    
    # Incluir todas las rutas definidas en el router bajo el prefijo 'api/'
    path('api/', include(router.urls)),  
    
    # Ruta para obtener el token de acceso
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  
    
    # Ruta para refrescar el token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
