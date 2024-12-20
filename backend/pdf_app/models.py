from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class DocumentoPDF(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    archivo = models.FileField(upload_to='documentos_pdfs/')
    aprobador = models.EmailField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    # Cambié esto para usar el modelo de usuario personalizado
    remitente = models.ForeignKey('UsuarioPersonalizado', on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class UsuarioPersonalizado(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'  # Usar email como identificador
    REQUIRED_FIELDS = ['username']  # username sigue siendo necesario para Django

    def __str__(self):
        return self.email
