"""
HOME+ - Módulo de Gestión de Usuarios
Configuración de URLs
"""

from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Registro
    path('registro/', views.registro, name='registro'),

    # Activación de cuenta
    path('activar-cuenta/<str:token>/', views.activar_cuenta, name='activar_cuenta'),

    # Login / Logout
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Recuperación de contraseña
    path('recuperar-password/', views.recuperar_password, name='recuperar_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),

    # Perfil profesional (paso 2 del registro)
    path('perfil-profesional/<int:usuario_id>/', views.perfil_profesional, name='perfil_profesional'),
]

# ── Panel de Administración Propio ──────────────────────────────────────
from . import views_admin

urlpatterns += [
    path('admin-panel/',                          views_admin.admin_dashboard,       name='admin_dashboard'),
    path('admin-panel/usuarios/',                 views_admin.admin_usuarios,        name='admin_usuarios'),
    path('admin-panel/usuarios/<int:usuario_id>/',views_admin.admin_usuario_detalle, name='admin_usuario_detalle'),
    path('admin-panel/aprobar/<int:usuario_id>/', views_admin.admin_aprobar,         name='admin_aprobar'),
    path('admin-panel/rechazar/<int:usuario_id>/',views_admin.admin_rechazar,        name='admin_rechazar'),
    path('admin-panel/accion-masiva/',            views_admin.admin_aprobar_masivo,  name='admin_aprobar_masivo'),
    path('admin-panel/reportes/',                 views_admin.admin_reportes,        name='admin_reportes'),
    path('admin-panel/reportes/crear/',           views_admin.admin_crear_reporte,   name='admin_crear_reporte'),
    path('admin-panel/reportes/<int:reporte_id>/',views_admin.admin_reporte_detalle, name='admin_reporte_detalle'),
    path('admin-panel/reportes/<int:reporte_id>/eliminar/', views_admin.admin_eliminar_reporte, name='admin_eliminar_reporte'),
]