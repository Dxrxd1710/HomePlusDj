"""
HOME+ - Panel de Administración Propio
Vistas del panel: lista usuarios, aprobar/rechazar, detalle, reportes
"""

import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from .models import Usuario, PerfilProfesional, ReporteAdmin


# ─────────────────────────────────────────
# DECORADOR: proteger rutas del panel
# ─────────────────────────────────────────

def admin_requerido(view_func):
    """Decorador que verifica que el usuario en sesión sea admin."""
    def wrapper(request, *args, **kwargs):
        if request.session.get('usuario_tipo') != 'admin':
            messages.error(request, 'Acceso restringido al administrador.')
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def _get_admin(request):
    """Helper: obtener el objeto admin desde la sesión."""
    return get_object_or_404(Usuario, id_usuario=request.session['usuario_id'])


# ─────────────────────────────────────────
# DASHBOARD DEL PANEL
# ─────────────────────────────────────────

@admin_requerido
def panel_dashboard(request):
    """Vista principal del panel con estadísticas generales."""
    admin = _get_admin(request)

    # ── Estadísticas rápidas ──
    total_usuarios    = Usuario.objects.exclude(tipo_usuario='admin').count()
    total_clientes    = Usuario.objects.filter(tipo_usuario='cliente').count()
    total_profesionales = Usuario.objects.filter(tipo_usuario='profesional').count()
    pendientes        = Usuario.objects.filter(estado_cuenta='pendiente', activo=True).count()
    aprobados         = Usuario.objects.filter(estado_cuenta='aprobado').count()
    rechazados        = Usuario.objects.filter(estado_cuenta='rechazado').count()
    sin_activar       = Usuario.objects.filter(activo=False).exclude(tipo_usuario='admin').count()

    # ── Últimos 5 registros ──
    ultimos_registros = (
        Usuario.objects
        .exclude(tipo_usuario='admin')
        .order_by('-fecha_registro')[:5]
    )

    # ── Registros por día (últimos 7 días) para la gráfica ──
    hoy = timezone.now().date()
    registros_semana = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        count = Usuario.objects.filter(
            fecha_registro__date=dia
        ).exclude(tipo_usuario='admin').count()
        registros_semana.append({'dia': dia.strftime('%d/%m'), 'count': count})

    # ── Últimos reportes ──
    ultimos_reportes = ReporteAdmin.objects.order_by('-fecha_creacion')[:4]

    ctx = {
        'admin': admin,
        'total_usuarios': total_usuarios,
        'total_clientes': total_clientes,
        'total_profesionales': total_profesionales,
        'pendientes': pendientes,
        'aprobados': aprobados,
        'rechazados': rechazados,
        'sin_activar': sin_activar,
        'ultimos_registros': ultimos_registros,
        'registros_semana': json.dumps(registros_semana),
        'ultimos_reportes': ultimos_reportes,
    }
    return render(request, 'usuarios/panel/dashboard.html', ctx)


# ─────────────────────────────────────────
# LISTA DE USUARIOS
# ─────────────────────────────────────────

@admin_requerido
def panel_usuarios(request):
    """Lista completa de usuarios con filtros y búsqueda."""
    admin = _get_admin(request)

    # ── Filtros ──
    tipo    = request.GET.get('tipo', '')
    estado  = request.GET.get('estado', '')
    activo  = request.GET.get('activo', '')
    buscar  = request.GET.get('q', '').strip()

    qs = Usuario.objects.exclude(tipo_usuario='admin').order_by('-fecha_registro')

    if tipo:
        qs = qs.filter(tipo_usuario=tipo)
    if estado:
        qs = qs.filter(estado_cuenta=estado)
    if activo == '1':
        qs = qs.filter(activo=True)
    elif activo == '0':
        qs = qs.filter(activo=False)
    if buscar:
        qs = qs.filter(
            Q(nombre__icontains=buscar) |
            Q(apellido__icontains=buscar) |
            Q(correo__icontains=buscar)
        )

    ctx = {
        'admin': admin,
        'usuarios': qs,
        'total': qs.count(),
        'filtro_tipo': tipo,
        'filtro_estado': estado,
        'filtro_activo': activo,
        'buscar': buscar,
    }
    return render(request, 'usuarios/panel/usuarios.html', ctx)


# ─────────────────────────────────────────
# DETALLE DE USUARIO
# ─────────────────────────────────────────

@admin_requerido
def panel_usuario_detalle(request, usuario_id):
    """Vista de detalle de un usuario con toda su información."""
    admin    = _get_admin(request)
    usuario  = get_object_or_404(Usuario, id_usuario=usuario_id)
    perfil   = getattr(usuario, 'perfil_profesional', None)

    ctx = {
        'admin': admin,
        'usuario': usuario,
        'perfil': perfil,
    }
    return render(request, 'usuarios/panel/usuario_detalle.html', ctx)


# ─────────────────────────────────────────
# APROBAR / RECHAZAR CUENTA
# ─────────────────────────────────────────

@admin_requerido
def panel_aprobar(request, usuario_id):
    """Aprueba la cuenta de un usuario."""
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    usuario.estado_cuenta = 'aprobado'
    usuario.save()
    messages.success(request, f'Cuenta de {usuario.nombre} {usuario.apellido} aprobada.')
    return redirect(request.META.get('HTTP_REFERER', 'usuarios:panel_usuarios'))


@admin_requerido
def panel_rechazar(request, usuario_id):
    """Rechaza la cuenta de un usuario."""
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    usuario.estado_cuenta = 'rechazado'
    usuario.save()
    messages.warning(request, f'Cuenta de {usuario.nombre} {usuario.apellido} rechazada.')
    return redirect(request.META.get('HTTP_REFERER', 'usuarios:panel_usuarios'))


@admin_requerido
def panel_pendiente(request, usuario_id):
    """Vuelve a poner en pendiente la cuenta de un usuario."""
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    usuario.estado_cuenta = 'pendiente'
    usuario.save()
    messages.info(request, f'Cuenta de {usuario.nombre} vuelta a pendiente.')
    return redirect(request.META.get('HTTP_REFERER', 'usuarios:panel_usuarios'))


# ─────────────────────────────────────────
# REPORTES
# ─────────────────────────────────────────

@admin_requerido
def panel_reportes(request):
    """Lista de reportes creados."""
    admin    = _get_admin(request)
    reportes = ReporteAdmin.objects.order_by('-fecha_creacion')

    ctx = {
        'admin': admin,
        'reportes': reportes,
    }
    return render(request, 'usuarios/panel/reportes.html', ctx)


@admin_requerido
def panel_reporte_crear(request):
    """Crea un nuevo reporte basado en el tipo seleccionado."""
    admin = _get_admin(request)

    if request.method == 'POST':
        titulo      = request.POST.get('titulo', '').strip()
        tipo        = request.POST.get('tipo', 'general')
        descripcion = request.POST.get('descripcion', '').strip()

        if not titulo:
            messages.error(request, 'El título es obligatorio.')
            return redirect('usuarios:panel_reporte_crear')

        # ── Generar datos del reporte según tipo ──
        datos = _generar_datos_reporte(tipo)

        reporte = ReporteAdmin.objects.create(
            titulo=titulo,
            tipo=tipo,
            descripcion=descripcion,
            creado_por=admin,
            datos_json=json.dumps(datos, ensure_ascii=False, default=str),
        )
        messages.success(request, f'Reporte "{titulo}" creado exitosamente.')
        return redirect('usuarios:panel_reporte_detalle', reporte_id=reporte.pk)

    ctx = {'admin': admin}
    return render(request, 'usuarios/panel/reporte_crear.html', ctx)


@admin_requerido
def panel_reporte_detalle(request, reporte_id):
    """Vista de detalle de un reporte con sus datos."""
    admin   = _get_admin(request)
    reporte = get_object_or_404(ReporteAdmin, pk=reporte_id)

    try:
        datos = json.loads(reporte.datos_json) if reporte.datos_json else {}
    except json.JSONDecodeError:
        datos = {}

    ctx = {
        'admin': admin,
        'reporte': reporte,
        'datos': datos,
    }
    return render(request, 'usuarios/panel/reporte_detalle.html', ctx)


@admin_requerido
def panel_reporte_eliminar(request, reporte_id):
    """Elimina un reporte."""
    reporte = get_object_or_404(ReporteAdmin, pk=reporte_id)
    nombre  = reporte.titulo
    reporte.delete()
    messages.success(request, f'Reporte "{nombre}" eliminado.')
    return redirect('usuarios:panel_reportes')


# ─────────────────────────────────────────
# HELPER: generar datos del reporte
# ─────────────────────────────────────────

def _generar_datos_reporte(tipo):
    """Genera el snapshot de datos según el tipo de reporte."""
    ahora = datetime.now().strftime('%d/%m/%Y %H:%M')

    base = {
        'generado_en': ahora,
        'tipo': tipo,
        'resumen': {
            'total_usuarios':      Usuario.objects.exclude(tipo_usuario='admin').count(),
            'total_clientes':      Usuario.objects.filter(tipo_usuario='cliente').count(),
            'total_profesionales': Usuario.objects.filter(tipo_usuario='profesional').count(),
            'aprobados':           Usuario.objects.filter(estado_cuenta='aprobado').count(),
            'pendientes':          Usuario.objects.filter(estado_cuenta='pendiente').count(),
            'rechazados':          Usuario.objects.filter(estado_cuenta='rechazado').count(),
            'sin_activar':         Usuario.objects.filter(activo=False).exclude(tipo_usuario='admin').count(),
        }
    }

    if tipo in ('usuarios', 'general'):
        base['usuarios'] = list(
            Usuario.objects
            .exclude(tipo_usuario='admin')
            .values('nombre', 'apellido', 'correo', 'tipo_usuario',
                    'estado_cuenta', 'activo', 'fecha_registro')
            .order_by('-fecha_registro')
        )

    if tipo in ('profesionales', 'general'):
        base['profesionales'] = list(
            PerfilProfesional.objects
            .select_related('usuario')
            .values('usuario__nombre', 'usuario__apellido',
                    'usuario__correo', 'servicio', 'anos_experiencia',
                    'usuario__estado_cuenta')
        )

    if tipo == 'pendientes':
        base['cuentas_pendientes'] = list(
            Usuario.objects
            .filter(estado_cuenta='pendiente', activo=True)
            .values('nombre', 'apellido', 'correo',
                    'tipo_usuario', 'fecha_registro')
            .order_by('fecha_registro')
        )

    return base
