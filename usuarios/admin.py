"""
HOME+ - Módulo de Gestión de Usuarios
Configuración del panel de administración Django
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Usuario, PerfilProfesional


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """Configuración del admin para gestión de usuarios HOME+."""

    list_display = [
        'id_usuario', 'nombre', 'apellido', 'correo',
        'tipo_usuario', 'estado_cuenta_badge', 'activo', 'fecha_registro'
    ]
    list_filter = ['tipo_usuario', 'estado_cuenta', 'activo', 'fecha_registro']
    search_fields = ['nombre', 'apellido', 'correo', 'telefono']
    readonly_fields = ['fecha_registro', 'token_activacion', 'token_recuperacion', 'password']
    ordering = ['-fecha_registro']

    fieldsets = (
        ('Información personal', {
            'fields': ('nombre', 'apellido', 'correo', 'telefono', 'direccion')
        }),
        ('Tipo y estado', {
            'fields': ('tipo_usuario', 'estado_cuenta', 'activo')
        }),
        ('Seguridad (solo lectura)', {
            'fields': ('password', 'token_activacion', 'token_recuperacion'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_registro',)
        }),
    )

    actions = ['aprobar_cuentas', 'rechazar_cuentas']

    def estado_cuenta_badge(self, obj):
        """Muestra el estado de cuenta con color en el admin."""
        colores = {
            'pendiente': '#f39c12',
            'aprobado': '#27ae60',
            'rechazado': '#e74c3c',
        }
        color = colores.get(obj.estado_cuenta, '#999')
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:4px;font-size:12px">{}</span>',
            color,
            obj.get_estado_cuenta_display()
        )
    estado_cuenta_badge.short_description = 'Estado de cuenta'

    @admin.action(description='✅ Aprobar cuentas seleccionadas')
    def aprobar_cuentas(self, request, queryset):
        """Acción para aprobar cuentas seleccionadas."""
        actualizados = queryset.update(estado_cuenta='aprobado')
        self.message_user(
            request,
            f'{actualizados} cuenta(s) aprobada(s) correctamente.'
        )

    @admin.action(description='❌ Rechazar cuentas seleccionadas')
    def rechazar_cuentas(self, request, queryset):
        """Acción para rechazar cuentas seleccionadas."""
        actualizados = queryset.update(estado_cuenta='rechazado')
        self.message_user(
            request,
            f'{actualizados} cuenta(s) rechazada(s) correctamente.'
        )


@admin.register(PerfilProfesional)
class PerfilProfesionalAdmin(admin.ModelAdmin):
    """Configuración del admin para perfiles de profesionales."""

    list_display = [
        'usuario', 'get_servicio_display_label', 'anos_experiencia', 'fecha_completado'
    ]
    list_filter = ['servicio', 'fecha_completado']
    search_fields = [
        'usuario__nombre', 'usuario__apellido',
        'usuario__correo', 'servicio_descripcion'
    ]
    readonly_fields = ['fecha_completado']

    fieldsets = (
        ('Profesional', {
            'fields': ('usuario',)
        }),
        ('Información del servicio', {
            'fields': ('servicio', 'servicio_descripcion', 'anos_experiencia')
        }),
        ('Trayectoria', {
            'fields': ('historial', 'certificaciones')
        }),
        ('Fechas', {
            'fields': ('fecha_completado',)
        }),
    )

    def get_servicio_display_label(self, obj):
        return obj.get_servicio_display()
    get_servicio_display_label.short_description = 'Servicio'
