from rest_framework import serializers
from .models import DocumentoPDF
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


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
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'username', 'password']

    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return value

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user
