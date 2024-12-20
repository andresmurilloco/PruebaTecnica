from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import DocumentoPDF
from .serializers import DocumentoPDFSerializer, UsuarioPersonalizadoSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied

class DocumentoPDFViewSet(viewsets.ModelViewSet):
    queryset = DocumentoPDF.objects.all()
    serializer_class = DocumentoPDFSerializer
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados pueden acceder

    def perform_create(self, serializer):
        # Asignar el remitente como el usuario autenticado
        serializer.save(remitente=self.request.user)

    def update(self, request, *args, **kwargs):
        # Verificar que el usuario autenticado sea el remitente del documento
        documento = self.get_object()
        if documento.remitente != request.user:
            raise PermissionDenied("No tienes permisos para editar este documento.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Verificar que el usuario autenticado sea el remitente del documento
        documento = self.get_object()
        if documento.remitente != request.user:
            raise PermissionDenied("No tienes permisos para eliminar este documento.")
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['patch'])
    def aprobar(self, request, pk=None):
        documento = self.get_object()
        if request.user.email == documento.aprobador:  # Compara el email del usuario con el campo aprobador
            documento.estado = 'aprobado'
            documento.save()
            return Response({'status': 'Documento aprobado'})
        return Response({'error': 'No tienes permisos para aprobar este documento'}, status=403)

    @action(detail=True, methods=['patch'])
    def rechazar(self, request, pk=None):
        documento = self.get_object()
        if request.user.email == documento.aprobador:  # Verifica si el usuario es el aprobador
            documento.estado = 'rechazado'
            documento.save()
            return Response({'status': 'Documento rechazado'})
        return Response({'error': 'No tienes permisos para rechazar este documento'}, status=403)


class UsuarioPersonalizadoViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UsuarioPersonalizadoSerializer
    permission_classes = [IsAuthenticated]

from django.http import HttpResponse

def home_view(request):
    return HttpResponse("Bienvenido a la API de gestión de documentos PDF.")
