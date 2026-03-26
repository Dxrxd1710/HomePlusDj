"""
HOME+ - Módulo de Gestión de Usuarios
Modelo de usuario personalizado y perfil de profesional
"""

import uuid
from django.db import models
from django.contrib.auth.hashers import make_password


class Usuario(models.Model):
    """Modelo principal de usuario para HOME+"""

    TIPO_USUARIO_CHOICES = [
    ('cliente', 'Cliente'),
    ('profesional', 'Profesional'),
    ('admin', 'Administrador'),
    ]

    ESTADO_CUENTA_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    correo = models.EmailField(unique=True, verbose_name='Correo electrónico')
    telefono = models.CharField(max_length=20, verbose_name='Teléfono')
    direccion = models.TextField(verbose_name='Dirección')
    password = models.CharField(max_length=255, verbose_name='Contraseña')
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='cliente',
        verbose_name='Tipo de usuario'
    )
    estado_cuenta = models.CharField(
        max_length=20,
        choices=ESTADO_CUENTA_CHOICES,
        default='pendiente',
        verbose_name='Estado de cuenta'
    )
    activo = models.BooleanField(default=False, verbose_name='Cuenta activada')
    token_activacion = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Token de activación'
    )
    token_recuperacion = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Token de recuperación'
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.correo})'

    def set_password(self, raw_password):
        """Encripta y guarda la contraseña."""
        self.password = make_password(raw_password)

    def generar_token(self):
        """Genera un token único para activación o recuperación."""
        return str(uuid.uuid4()).replace('-', '')

    def puede_iniciar_sesion(self):
        """Verifica si el usuario puede iniciar sesión."""
        return self.activo and self.estado_cuenta == 'aprobado'


class PerfilProfesional(models.Model):
    """
    Perfil extendido para usuarios de tipo 'profesional'.
    Se crea en un paso separado después del registro base.
    """

    SERVICIOS_CHOICES = [
        ('plomeria', 'Plomería'),
        ('electricidad', 'Electricidad'),
        ('pintura', 'Pintura'),
        ('albanileria', 'Albañilería'),
        ('limpieza', 'Limpieza del hogar'),
        ('otro', 'Otro'),
    ]

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_profesional',
        verbose_name='Usuario'
    )
    servicio = models.CharField(
        max_length=50,
        choices=SERVICIOS_CHOICES,
        verbose_name='Servicio que brinda'
    )
    servicio_descripcion = models.TextField(
        verbose_name='Descripción del servicio',
        help_text='Describe con detalle el servicio que ofreces.'
    )
    anos_experiencia = models.PositiveIntegerField(
        verbose_name='Años de experiencia'
    )
    historial = models.TextField(
        verbose_name='Historial profesional',
        help_text='Describe tu experiencia, empleos anteriores, proyectos o logros relevantes.'
    )
    certificaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Certificaciones o estudios',
        help_text='Opcional: menciona cursos, certificaciones o títulos relacionados.'
    )
    fecha_completado = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro del perfil'
    )

    class Meta:
        db_table = 'perfiles_profesionales'
        verbose_name = 'Perfil profesional'
        verbose_name_plural = 'Perfiles profesionales'

    def __str__(self):
        return f'Perfil de {self.usuario.nombre} {self.usuario.apellido} — {self.get_servicio_display()}'

class ReporteAdmin(models.Model):
    """Reportes generados por el administrador"""

    TIPO_REPORTE_CHOICES = [
        ('usuarios', 'Reporte de usuarios'),
        ('profesionales', 'Reporte de profesionales'),
        ('pendientes', 'Cuentas pendientes'),
        ('general', 'Reporte general'),
    ]

    titulo = models.CharField(max_length=200)

    tipo = models.CharField(
        max_length=30,
        choices=TIPO_REPORTE_CHOICES
    )

    descripcion = models.TextField(blank=True)

    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reportes_admin'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    datos_json = models.TextField(blank=True)

    class Meta:
        db_table = 'reportes_admin'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.titulo} — {self.get_tipo_display()}'