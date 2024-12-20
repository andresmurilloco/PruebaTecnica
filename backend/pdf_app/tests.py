from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import DocumentoPDF

class DocumentoPDFTests(TestCase):

    def setUp(self):
        # Usando get_user_model() para crear el usuario personalizado
        self.user = get_user_model().objects.create_user(
            username='usuario',  # Agregar un username
            email='usuario@test.com',
            password='testpass'
        )

    def test_crear_documento(self):
        documento = DocumentoPDF.objects.create(
            titulo='Documento de prueba',
            descripcion='Este es un documento de prueba',
            archivo='path/a/archivo.pdf',
            aprobador='approver@test.com',
            remitente=self.user
        )
        self.assertEqual(documento.titulo, 'Documento de prueba')
        self.assertEqual(documento.remitente, self.user)

    def test_aprobar_documento(self):
        documento = DocumentoPDF.objects.create(
            titulo='Documento pendiente',
            descripcion='Este documento está pendiente de aprobación',
            archivo='path/a/archivo.pdf',
            aprobador='approver@test.com',
            remitente=self.user
        )

        # Simulando que el aprobador aprueba el documento
        documento.estado = 'aprobado'
        documento.save()

        self.assertEqual(documento.estado, 'aprobado')
