from rest_framework import serializers
from .models import DocumentoPDF
from django.contrib.auth import get_user_model

class DocumentoPDFSerializer(serializers.ModelSerializer):
    remitente = serializers.StringRelatedField(read_only=True)  # Campo de solo lectura para el email del remitente

    class Meta:
        model = DocumentoPDF
        fields = ['id', 'titulo', 'descripcion', 'archivo', 'aprobador', 'estado', 'remitente']
        read_only_fields = ['remitente']  # Remitente no puede ser modificado desde el frontend

    def validate_aprobador(self, value):
        """
        Validación personalizada para asegurar que el correo electrónico del aprobador sea válido.
        """
        if not value or '@' not in value:
            raise serializers.ValidationError("Introduzca una dirección de correo electrónico válida.")
        return value

class UsuarioPersonalizadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'username']
