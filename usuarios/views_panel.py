"""
HOME+ - Panel de Administración Propio
Vistas para gestión de usuarios, aprobaciones y reportes
"""

import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from .models import Usuario, PerfilProfesional, ReporteAdmin


# ─────────────────────────────────────────
# DECORADOR: proteger rutas del panel
# ─────────────────────────────────────────

def admin_required(view_func):
    """Decorador que verifica que el usuario sea administrador."""
    def wrapper(request, *args, **kwargs):
        if request.session.get('usuario_tipo') != 'admin':
            messages.error(request, 'Acceso restringido al administrador.')
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def _get_admin(request):
    """Obtiene el objeto admin desde la sesión."""
    return get_object_or_404(Usuario, id_usuario=request.session['usuario_id'])


# ─────────────────────────────────────────
# DASHBOARD DEL PANEL
# ─────────────────────────────────────────

@admin_required
def panel_dashboard(request):
    """Vista principal del panel de administración con estadísticas."""
    admin = _get_admin(request)

    # ── Estadísticas generales ──
    total_usuarios    = Usuario.objects.exclude(tipo_usuario='admin').count()
    total_clientes    = Usuario.objects.filter(tipo_usuario='cliente').count()
    total_profesional = Usuario.objects.filter(tipo_usuario='profesional').count()
    pendientes        = Usuario.objects.filter(estado_cuenta='pendiente', activo=True).count()
    aprobados         = Usuario.objects.filter(estado_cuenta='aprobado').count()
    rechazados        = Usuario.objects.filter(estado_cuenta='rechazado').count()
    sin_activar       = Usuario.objects.filter(activo=False).exclude(tipo_usuario='admin').count()

    # ── Últimos 5 registros pendientes ──
    ultimos_pendientes = (
        Usuario.objects
        .filter(estado_cuenta='pendiente', activo=True)
        .exclude(tipo_usuario='admin')
        .order_by('-fecha_registro')[:5]
    )

    # ── Registros por día (últimos 7 días) ──
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

    context = {
        'admin': admin,
        'total_usuarios': total_usuarios,
        'total_clientes': total_clientes,
        'total_profesional': total_profesional,
        'pendientes': pendientes,
        'aprobados': aprobados,
        'rechazados': rechazados,
        'sin_activar': sin_activar,
        'ultimos_pendientes': ultimos_pendientes,
        'registros_semana': registros_semana,
        'ultimos_reportes': ultimos_reportes,
    }
    return render(request, 'usuarios/panel/dashboard.html', context)


# ─────────────────────────────────────────
# LISTA DE USUARIOS
# ─────────────────────────────────────────

@admin_required
def panel_usuarios(request):
    """Lista completa de usuarios con filtros y búsqueda."""
    admin = _get_admin(request)

    usuarios = Usuario.objects.exclude(tipo_usuario='admin').order_by('-fecha_registro')

    # ── Filtros ──
    filtro_tipo   = request.GET.get('tipo', '')
    filtro_estado = request.GET.get('estado', '')
    filtro_activo = request.GET.get('activo', '')
    busqueda      = request.GET.get('q', '')

    if filtro_tipo:
        usuarios = usuarios.filter(tipo_usuario=filtro_tipo)
    if filtro_estado:
        usuarios = usuarios.filter(estado_cuenta=filtro_estado)
    if filtro_activo == '1':
        usuarios = usuarios.filter(activo=True)
    elif filtro_activo == '0':
        usuarios = usuarios.filter(activo=False)
    if busqueda:
        usuarios = usuarios.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellido__icontains=busqueda) |
            Q(correo__icontains=busqueda)
        )

    context = {
        'admin': admin,
        'usuarios': usuarios,
        'total': usuarios.count(),
        'filtro_tipo': filtro_tipo,
        'filtro_estado': filtro_estado,
        'filtro_activo': filtro_activo,
        'busqueda': busqueda,
    }
    return render(request, 'usuarios/panel/usuarios.html', context)


# ─────────────────────────────────────────
# DETALLE DE USUARIO
# ─────────────────────────────────────────

@admin_required
def panel_usuario_detalle(request, usuario_id):
    """Vista de detalle de un usuario con todas sus acciones."""
    admin = _get_admin(request)
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    perfil = None
    if usuario.tipo_usuario == 'profesional':
        try:
            perfil = usuario.perfil_profesional
        except PerfilProfesional.DoesNotExist:
            perfil = None

    context = {
        'admin': admin,
        'usuario': usuario,
        'perfil': perfil,
    }
    return render(request, 'usuarios/panel/usuario_detalle.html', context)


# ─────────────────────────────────────────
# ACCIONES SOBRE CUENTAS
# ─────────────────────────────────────────

@admin_required
def panel_aprobar(request, usuario_id):
    """Aprueba la cuenta de un usuario."""
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    usuario.estado_cuenta = 'aprobado'
    usuario.save()
    messages.success(request, f'Cuenta de {usuario.nombre} {usuario.apellido} aprobada.')
    return redirect(request.META.get('HTTP_REFERER', 'usuarios:panel_usuarios'))


@admin_required
def panel_rechazar(request, usuario_id):
    """Rechaza la cuenta de un usuario."""
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    usuario.estado_cuenta = 'rechazado'
    usuario.save()
    messages.warning(request, f'Cuenta de {usuario.nombre} {usuario.apellido} rechazada.')
    return redirect(request.META.get('HTTP_REFERER', 'usuarios:panel_usuarios'))


@admin_required
def panel_pendiente(request, usuario_id):
    """Regresa la cuenta a estado pendiente."""
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    usuario.estado_cuenta = 'pendiente'
    usuario.save()
    messages.info(request, f'Cuenta de {usuario.nombre} devuelta a pendiente.')
    return redirect(request.META.get('HTTP_REFERER', 'usuarios:panel_usuarios'))


@admin_required
def panel_accion_masiva(request):
    """Procesa acciones masivas sobre usuarios seleccionados."""
    if request.method == 'POST':
        ids      = request.POST.getlist('usuarios_ids')
        accion   = request.POST.get('accion')
        mapeo    = {'aprobar': 'aprobado', 'rechazar': 'rechazado', 'pendiente': 'pendiente'}

        if accion in mapeo and ids:
            actualizados = Usuario.objects.filter(id_usuario__in=ids).update(
                estado_cuenta=mapeo[accion]
            )
            messages.success(request, f'{actualizados} cuenta(s) actualizadas a "{mapeo[accion]}".')
        else:
            messages.error(request, 'Selecciona una acción y al menos un usuario.')

    return redirect('usuarios:panel_usuarios')


# ─────────────────────────────────────────
# REPORTES
# ─────────────────────────────────────────

@admin_required
def panel_reportes(request):
    """Lista de reportes generados."""
    admin = _get_admin(request)
    reportes = ReporteAdmin.objects.order_by('-fecha_creacion')

    context = {
        'admin': admin,
        'reportes': reportes,
    }
    return render(request, 'usuarios/panel/reportes.html', context)


@admin_required
def panel_crear_reporte(request):
    """Crea un nuevo reporte automático según el tipo elegido."""
    admin = _get_admin(request)

    if request.method == 'POST':
        tipo        = request.POST.get('tipo')
        titulo      = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if not titulo or not tipo:
            messages.error(request, 'El título y tipo son obligatorios.')
            return redirect('usuarios:panel_crear_reporte')

        # ── Generar datos según el tipo ──
        datos = {}

        if tipo == 'general':
            datos = {
                'total_usuarios':    Usuario.objects.exclude(tipo_usuario='admin').count(),
                'total_clientes':    Usuario.objects.filter(tipo_usuario='cliente').count(),
                'total_profesionales': Usuario.objects.filter(tipo_usuario='profesional').count(),
                'aprobados':         Usuario.objects.filter(estado_cuenta='aprobado').count(),
                'pendientes':        Usuario.objects.filter(estado_cuenta='pendiente').count(),
                'rechazados':        Usuario.objects.filter(estado_cuenta='rechazado').count(),
                'activados':         Usuario.objects.filter(activo=True).exclude(tipo_usuario='admin').count(),
                'sin_activar':       Usuario.objects.filter(activo=False).exclude(tipo_usuario='admin').count(),
            }

        elif tipo == 'usuarios':
            qs = Usuario.objects.filter(tipo_usuario='cliente').values(
                'nombre', 'apellido', 'correo', 'estado_cuenta', 'activo', 'fecha_registro'
            )
            datos = {
                'total': qs.count(),
                'lista': [
                    {
                        'nombre': u['nombre'] + ' ' + u['apellido'],
                        'correo': u['correo'],
                        'estado': u['estado_cuenta'],
                        'activo': u['activo'],
                        'fecha':  u['fecha_registro'].strftime('%d/%m/%Y') if u['fecha_registro'] else '',
                    }
                    for u in qs
                ]
            }

        elif tipo == 'profesionales':
            qs = Usuario.objects.filter(tipo_usuario='profesional').prefetch_related('perfil_profesional')
            lista = []
            for u in qs:
                item = {
                    'nombre': u.nombre + ' ' + u.apellido,
                    'correo': u.correo,
                    'estado': u.estado_cuenta,
                    'activo': u.activo,
                    'fecha':  u.fecha_registro.strftime('%d/%m/%Y'),
                }
                try:
                    item['servicio'] = u.perfil_profesional.get_servicio_display()
                    item['experiencia'] = u.perfil_profesional.anos_experiencia
                except Exception:
                    item['servicio'] = 'Sin perfil'
                    item['experiencia'] = '-'
                lista.append(item)
            datos = {'total': len(lista), 'lista': lista}

        elif tipo == 'pendientes':
            qs = Usuario.objects.filter(
                estado_cuenta='pendiente', activo=True
            ).exclude(tipo_usuario='admin')
            datos = {
                'total': qs.count(),
                'lista': [
                    {
                        'nombre': u.nombre + ' ' + u.apellido,
                        'correo': u.correo,
                        'tipo':   u.tipo_usuario,
                        'fecha':  u.fecha_registro.strftime('%d/%m/%Y'),
                    }
                    for u in qs
                ]
            }

        # ── Guardar reporte ──
        ReporteAdmin.objects.create(
            titulo=titulo,
            tipo=tipo,
            descripcion=descripcion,
            creado_por=admin,
            datos_json=json.dumps(datos, ensure_ascii=False),
        )

        messages.success(request, f'Reporte "{titulo}" creado correctamente.')
        return redirect('usuarios:panel_reportes')

    context = {'admin': admin}
    return render(request, 'usuarios/panel/crear_reporte.html', context)


@admin_required
def panel_ver_reporte(request, reporte_id):
    """Visualiza el detalle de un reporte."""
    admin   = _get_admin(request)
    reporte = get_object_or_404(ReporteAdmin, id=reporte_id)

    datos = {}
    if reporte.datos_json:
        try:
            datos = json.loads(reporte.datos_json)
        except Exception:
            datos = {}

    context = {
        'admin':   admin,
        'reporte': reporte,
        'datos':   datos,
    }
    return render(request, 'usuarios/panel/ver_reporte.html', context)


@admin_required
def panel_eliminar_reporte(request, reporte_id):
    """Elimina un reporte."""
    reporte = get_object_or_404(ReporteAdmin, id=reporte_id)
    nombre  = reporte.titulo
    reporte.delete()
    messages.success(request, f'Reporte "{nombre}" eliminado.')
    return redirect('usuarios:panel_reportes')
