"""
HOME+ — Panel de Administración Propio
Solo accesible para usuarios con tipo_usuario = 'admin'.
"""

import json
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from .models import Usuario, PerfilProfesional, ReporteAdmin


# ─────────────────────────────────────────────────────────────
# DECORADOR: proteger vistas de admin
# ─────────────────────────────────────────────────────────────

def admin_requerido(func):
    def wrapper(request, *args, **kwargs):
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            messages.error(request, 'Debes iniciar sesión.')
            return redirect('usuarios:login')
        try:
            admin = Usuario.objects.get(id_usuario=usuario_id, tipo_usuario='admin')
        except Usuario.DoesNotExist:
            messages.error(request, 'No tienes permisos para acceder al panel.')
            return redirect('usuarios:login')
        return func(request, *args, admin=admin, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# ─────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────

@admin_requerido
def admin_dashboard(request, admin):
    hoy = date.today()

    stats = {
        'total':         Usuario.objects.exclude(tipo_usuario='admin').count(),
        'clientes':      Usuario.objects.filter(tipo_usuario='cliente').count(),
        'profesionales': Usuario.objects.filter(tipo_usuario='profesional').count(),
        'pendientes':    Usuario.objects.filter(estado_cuenta='pendiente', activo=True).count(),
        'aprobados':     Usuario.objects.filter(estado_cuenta='aprobado').count(),
        'rechazados':    Usuario.objects.filter(estado_cuenta='rechazado').count(),
        'sin_activar':   Usuario.objects.filter(activo=False, tipo_usuario__in=['cliente','profesional']).count(),
        'hoy':           Usuario.objects.filter(fecha_registro__date=hoy).exclude(tipo_usuario='admin').count(),
    }

    # Registros últimos 7 días para gráfica
    semana = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        semana.append({
            'dia': dia.strftime('%d/%m'),
            'cantidad': Usuario.objects.filter(fecha_registro__date=dia).exclude(tipo_usuario='admin').count()
        })

    ultimos_pendientes = (
        Usuario.objects
        .filter(estado_cuenta='pendiente', activo=True)
        .exclude(tipo_usuario='admin')
        .order_by('-fecha_registro')[:6]
    )

    servicios = (
        PerfilProfesional.objects
        .values('servicio')
        .annotate(total=Count('servicio'))
        .order_by('-total')[:6]
    )

    ultimos_reportes = ReporteAdmin.objects.order_by('-fecha_creacion')[:4]

    return render(request, 'usuarios/admin/dashboard.html', {
        'admin': admin,
        'stats': stats,
        'semana_json': json.dumps(semana),
        'ultimos_pendientes': ultimos_pendientes,
        'servicios': servicios,
        'ultimos_reportes': ultimos_reportes,
    })


# ─────────────────────────────────────────────────────────────
# LISTA DE USUARIOS
# ─────────────────────────────────────────────────────────────

@admin_requerido
def admin_usuarios(request, admin):
    qs = Usuario.objects.exclude(tipo_usuario='admin').order_by('-fecha_registro')

    tipo    = request.GET.get('tipo', '')
    estado  = request.GET.get('estado', '')
    activo  = request.GET.get('activo', '')
    q       = request.GET.get('q', '').strip()

    if tipo:    qs = qs.filter(tipo_usuario=tipo)
    if estado:  qs = qs.filter(estado_cuenta=estado)
    if activo == '1': qs = qs.filter(activo=True)
    elif activo == '0': qs = qs.filter(activo=False)
    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) | Q(apellido__icontains=q) |
            Q(correo__icontains=q) | Q(telefono__icontains=q)
        )

    return render(request, 'usuarios/admin/usuarios.html', {
        'admin': admin, 'usuarios': qs, 'total': qs.count(),
        'tipo': tipo, 'estado': estado, 'activo': activo, 'q': q,
    })


# ─────────────────────────────────────────────────────────────
# DETALLE DE USUARIO
# ─────────────────────────────────────────────────────────────

@admin_requerido
def admin_usuario_detalle(request, usuario_id, admin):
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    perfil  = getattr(usuario, 'perfil_profesional', None)
    return render(request, 'usuarios/admin/usuario_detalle.html', {
        'admin': admin, 'usuario': usuario, 'perfil': perfil,
    })


# ─────────────────────────────────────────────────────────────
# APROBAR / RECHAZAR
# ─────────────────────────────────────────────────────────────

@admin_requerido
def admin_aprobar(request, usuario_id, admin):
    u = get_object_or_404(Usuario, id_usuario=usuario_id)
    u.estado_cuenta = 'aprobado'
    u.save()
    messages.success(request, f'✅ Cuenta de {u.nombre} {u.apellido} aprobada.')
    return redirect(request.META.get('HTTP_REFERER', 'usuarios:admin_usuarios'))


@admin_requerido
def admin_rechazar(request, usuario_id, admin):
    u = get_object_or_404(Usuario, id_usuario=usuario_id)
    u.estado_cuenta = 'rechazado'
    u.save()
    messages.warning(request, f'❌ Cuenta de {u.nombre} {u.apellido} rechazada.')
    return redirect(request.META.get('HTTP_REFERER', 'usuarios:admin_usuarios'))


@admin_requerido
def admin_aprobar_masivo(request, admin):
    if request.method == 'POST':
        ids    = request.POST.getlist('ids')
        accion = request.POST.get('accion')
        if not ids:
            messages.error(request, 'No seleccionaste ningún usuario.')
            return redirect('usuarios:admin_usuarios')
        estado = 'aprobado' if accion == 'aprobar' else 'rechazado'
        n = Usuario.objects.filter(id_usuario__in=ids).update(estado_cuenta=estado)
        messages.success(request, f'{n} usuario(s) {"aprobados" if estado=="aprobado" else "rechazados"}.')
    return redirect('usuarios:admin_usuarios')


# ─────────────────────────────────────────────────────────────
# REPORTES
# ─────────────────────────────────────────────────────────────

@admin_requerido
def admin_reportes(request, admin):
    reportes = ReporteAdmin.objects.order_by('-fecha_creacion')
    return render(request, 'usuarios/admin/reportes.html', {
        'admin': admin, 'reportes': reportes,
    })


@admin_requerido
def admin_crear_reporte(request, admin):
    if request.method == 'POST':
        titulo      = request.POST.get('titulo', '').strip()
        tipo        = request.POST.get('tipo', 'general')
        descripcion = request.POST.get('descripcion', '').strip()
        if not titulo:
            messages.error(request, 'El título es obligatorio.')
            return render(request, 'usuarios/admin/crear_reporte.html', {'admin': admin})

        datos = _generar_datos(tipo)
        reporte = ReporteAdmin.objects.create(
            titulo=titulo, tipo=tipo, descripcion=descripcion,
            creado_por=admin,
            datos_json=json.dumps(datos, ensure_ascii=False, default=str)
        )
        messages.success(request, f'Reporte "{titulo}" generado.')
        return redirect('usuarios:admin_reporte_detalle', reporte_id=reporte.pk)

    return render(request, 'usuarios/admin/crear_reporte.html', {'admin': admin})


def _generar_datos(tipo):
    hoy = date.today()
    datos = {
        'generado_el':     timezone.now().strftime('%d/%m/%Y %H:%M'),
        'total_usuarios':  Usuario.objects.exclude(tipo_usuario='admin').count(),
        'clientes':        Usuario.objects.filter(tipo_usuario='cliente').count(),
        'profesionales':   Usuario.objects.filter(tipo_usuario='profesional').count(),
        'aprobados':       Usuario.objects.filter(estado_cuenta='aprobado').count(),
        'pendientes':      Usuario.objects.filter(estado_cuenta='pendiente').count(),
        'rechazados':      Usuario.objects.filter(estado_cuenta='rechazado').count(),
        'sin_activar':     Usuario.objects.filter(activo=False).exclude(tipo_usuario='admin').count(),
    }
    if tipo in ('profesionales', 'general'):
        datos['servicios'] = list(
            PerfilProfesional.objects.values('servicio').annotate(total=Count('servicio')).order_by('-total')
        )
    if tipo in ('usuarios', 'general'):
        registros = []
        for i in range(29, -1, -1):
            dia = hoy - timedelta(days=i)
            registros.append({
                'dia': dia.strftime('%d/%m'),
                'cantidad': Usuario.objects.filter(fecha_registro__date=dia).exclude(tipo_usuario='admin').count()
            })
        datos['registros_30_dias'] = registros
    if tipo == 'pendientes':
        datos['lista_pendientes'] = list(
            Usuario.objects.filter(estado_cuenta='pendiente', activo=True)
            .exclude(tipo_usuario='admin')
            .values('nombre', 'apellido', 'correo', 'tipo_usuario', 'fecha_registro')
        )
    return datos


@admin_requerido
def admin_reporte_detalle(request, reporte_id, admin):
    reporte = get_object_or_404(ReporteAdmin, pk=reporte_id)
    try:
        datos = json.loads(reporte.datos_json) if reporte.datos_json else {}
    except json.JSONDecodeError:
        datos = {}
    return render(request, 'usuarios/admin/reporte_detalle.html', {
        'admin': admin, 'reporte': reporte, 'datos': datos,
        'datos_json': json.dumps(datos, ensure_ascii=False),
    })


@admin_requerido
def admin_eliminar_reporte(request, reporte_id, admin):
    reporte = get_object_or_404(ReporteAdmin, pk=reporte_id)
    titulo = reporte.titulo
    reporte.delete()
    messages.success(request, f'Reporte "{titulo}" eliminado.')
    return redirect('usuarios:admin_reportes')
