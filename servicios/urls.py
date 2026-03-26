from django.urls import path
from . import views

app_name = 'servicios'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    path('editar/<int:id>/', views.editar_servicio, name='editar'),

    path('eliminar/<int:id>/', views.eliminar_servicio, name='eliminar'),
    path('dashboard/profesional/', views.dashboard_profesional,
         name='dashboard_profesional'),
    path('detalle/<int:id>/', views.detalle_servicio, name='detalle'),
    path('aplicar/<int:servicio_id>/', views.aplicar_servicio, name='aplicar'),
    path('aplicaciones/<int:servicio_id>/',
         views.ver_aplicaciones, name='aplicaciones'),
    path('aceptar/<int:aplicacion_id>/',
         views.aceptar_profesional, name='aceptar_profesional'),
    path('subir-contrato/<int:id>/', views.subir_contrato, name='subir_contrato'),
    path('finalizar/<int:id>/', views.finalizar_servicio, name='finalizar'),
    path('seguimiento/<int:id>/', views.seguimiento_servicio, name='seguimiento'),
    path('subir-evidencia/<int:id>/',
         views.subir_evidencia, name='subir_evidencia'),
    path('calificar/<int:id>/', views.calificar_servicio, name='calificar'),
    path('visita/<int:id>/', views.gestionar_visita, name='visita'),
    path('pago/<int:servicio_id>/', views.seleccionar_pago, name='seleccionar_pago'),
path('contrato/<int:servicio_id>/', views.generar_contrato, name='generar_contrato'),
path("dashboard/", views.dashboard, name="dashboard"),
    path("carga-masiva/", views.carga_masiva, name="carga_masiva"),

path('logout/', views.cerrar_sesion, name='logout')








]
