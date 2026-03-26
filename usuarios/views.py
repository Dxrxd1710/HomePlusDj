"""
HOME+ - Módulo de Gestión de Usuarios
Vistas para registro, activación, login y recuperación de contraseña
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from .models import Usuario, PerfilProfesional
from .forms import RegistroForm, LoginForm, RecuperarPasswordForm, ResetPasswordForm, PerfilProfesionalForm


# ─────────────────────────────────────────
# REGISTRO
# ─────────────────────────────────────────
def landing(request):
    return render(request, 'usuarios/landing.html')


def registro(request):
    """
    Vista de registro de usuarios.
    Guarda el usuario con estado 'pendiente' y envía correo de activación.
    """
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)

            # Encriptar contraseña
            usuario.set_password(form.cleaned_data['password'])

            # Generar token de activación
            usuario.token_activacion = usuario.generar_token()
            usuario.estado_cuenta = 'pendiente'
            usuario.activo = False
            usuario.save()

            # Enviar correo de activación
            _enviar_correo_activacion(request, usuario)

            # Si es profesional, redirigir a completar perfil
            if usuario.tipo_usuario == 'profesional':
                messages.info(
                    request,
                    '¡Registro exitoso! Completa tu perfil profesional y luego revisa tu correo para activar tu cuenta.'
                )
                return redirect('usuarios:perfil_profesional', usuario_id=usuario.id_usuario)

            messages.success(
                request,
                '¡Registro exitoso! Revisa tu correo para activar tu cuenta.'
            )
            return redirect('usuarios:login')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})


def _enviar_correo_activacion(request, usuario):
    """Envía el correo electrónico con el enlace de activación."""
    enlace = request.build_absolute_uri(
        reverse('usuarios:activar_cuenta', args=[usuario.token_activacion])
    )
    asunto = 'HOME+ - Activa tu cuenta'
    mensaje = f"""
Hola {usuario.nombre},

Gracias por registrarte en HOME+. Por favor, activa tu cuenta haciendo clic en el siguiente enlace:

{enlace}

Si no te registraste en HOME+, ignora este correo.

Saludos,
El equipo de HOME+
    """
    send_mail(
        asunto,
        mensaje,
        settings.EMAIL_HOST_USER,
        [usuario.correo],
        fail_silently=False,
    )


# ─────────────────────────────────────────
# ACTIVACIÓN DE CUENTA
# ─────────────────────────────────────────

def activar_cuenta(request, token):
    """
    Vista para activar cuenta mediante token recibido por correo.
    Cambia 'activo' a True si el token es válido.
    """
    try:
        usuario = Usuario.objects.get(token_activacion=token)
    except Usuario.DoesNotExist:
        messages.error(
            request, 'El enlace de activación no es válido o ya fue usado.')
        return redirect('usuarios:login')

    if usuario.activo:
        messages.info(request, 'Tu cuenta ya fue activada anteriormente.')
        return redirect('usuarios:login')

    usuario.activo = True
    usuario.token_activacion = None  # Invalidar token usado
    usuario.save()

    return render(request, 'usuarios/activacion_exitosa.html', {'usuario': usuario})


# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────

def login_usuario(request):
    """
    Vista de inicio de sesión.
    Verifica correo, contraseña, activación y aprobación del admin.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            password = form.cleaned_data['password']

            try:
                usuario = Usuario.objects.get(correo=correo)
            except Usuario.DoesNotExist:
                messages.error(request, 'Correo o contraseña incorrectos.')
                return render(request, 'usuarios/login.html', {'form': form})

            # Verificar contraseña
            if not check_password(password, usuario.password):
                messages.error(request, 'Correo o contraseña incorrectos.')
                return render(request, 'usuarios/login.html', {'form': form})

            # Verificar activación por correo
            if not usuario.activo:
                messages.warning(
                    request,
                    'Tu cuenta no ha sido activada. Revisa tu correo electrónico.'
                )
                return render(request, 'usuarios/login.html', {'form': form})

            # Verificar aprobación del administrador
            if usuario.estado_cuenta == 'pendiente':
                messages.warning(
                    request,
                    'Tu cuenta está pendiente de aprobación por el administrador.'
                )
                return render(request, 'usuarios/login.html', {'form': form})

            if usuario.estado_cuenta == 'rechazado':
                messages.error(
                    request,
                    'Tu cuenta ha sido rechazada. Contacta al administrador.'
                )
                return render(request, 'usuarios/login.html', {'form': form})

            # Guardar sesión
            request.session['usuario_id'] = usuario.id_usuario
            request.session['usuario_nombre'] = usuario.nombre
            request.session['usuario_tipo'] = usuario.tipo_usuario

            messages.success(request, f'¡Bienvenido, {usuario.nombre}!')

             # Redirección según tipo de usuario
            if usuario.tipo_usuario == 'admin':
                return redirect('usuarios:admin_dashboard')

            elif usuario.tipo_usuario == 'profesional':
                return redirect('servicios:dashboard_profesional')

            else:
                return redirect('servicios:dashboard')
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})

def logout_usuario(request):
    """Vista para cerrar sesión."""
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('usuarios:login')


def dashboard(request):
    """Vista de panel principal (solo usuarios autenticados)."""
    if 'usuario_id' not in request.session:
        messages.error(request, 'Debes iniciar sesión para acceder.')
        return redirect('usuarios:login')

    usuario = get_object_or_404(
        Usuario, id_usuario=request.session['usuario_id'])
    return render(request, 'usuarios/dashboard.html', {'usuario': usuario})


# ─────────────────────────────────────────
# RECUPERACIÓN DE CONTRASEÑA
# ─────────────────────────────────────────


def recuperar_password(request):
    """
    Vista para solicitar recuperación de contraseña.
    Envía un correo con enlace y token único.
    """
    if request.method == 'POST':
        form = RecuperarPasswordForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            usuario = Usuario.objects.get(correo=correo)

            # Generar token de recuperación
            usuario.token_recuperacion = usuario.generar_token()
            usuario.save()

            # Enviar correo
            _enviar_correo_recuperacion(request, usuario)

            messages.success(
                request,
                'Te hemos enviado un correo con instrucciones para cambiar tu contraseña.'
            )
            return redirect('usuarios:login')
    else:
        form = RecuperarPasswordForm()

    return render(request, 'usuarios/recuperar_password.html', {'form': form})


def _enviar_correo_recuperacion(request, usuario):
    """Envía el correo con el enlace de recuperación de contraseña."""
    enlace = request.build_absolute_uri(
        reverse('usuarios:reset_password', args=[usuario.token_recuperacion])
    )
    asunto = 'HOME+ - Recupera tu contraseña'
    mensaje = f"""
Hola {usuario.nombre},

Recibimos una solicitud para cambiar la contraseña de tu cuenta HOME+.

Haz clic en el siguiente enlace para crear una nueva contraseña:

{enlace}

Este enlace es válido por uso único. Si no solicitaste este cambio, ignora este correo.

Saludos,
El equipo de HOME+
    """
    send_mail(
        asunto,
        mensaje,
        settings.EMAIL_HOST_USER,
        [usuario.correo],
        fail_silently=False,
    )


def reset_password(request, token):
    """
    Vista para establecer nueva contraseña usando el token de recuperación.
    """
    try:
        usuario = Usuario.objects.get(token_recuperacion=token)
    except Usuario.DoesNotExist:
        messages.error(request, 'El enlace no es válido o ya fue utilizado.')
        return redirect('usuarios:recuperar_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            usuario.set_password(form.cleaned_data['nueva_password'])
            usuario.token_recuperacion = None  # Invalidar token
            usuario.save()

            messages.success(
                request,
                '¡Contraseña actualizada correctamente! Ya puedes iniciar sesión.'
            )
            return redirect('usuarios:login')
    else:
        form = ResetPasswordForm()

    return render(request, 'usuarios/reset_password.html', {'form': form, 'token': token})


# ─────────────────────────────────────────
# PERFIL PROFESIONAL
# ─────────────────────────────────────────

def perfil_profesional(request, usuario_id):
    """
    Vista para que el profesional complete su perfil tras el registro.
    Solicita: servicio, descripción, años de experiencia, historial y certificaciones.
    """
    usuario = get_object_or_404(
        Usuario, id_usuario=usuario_id, tipo_usuario='profesional')

    # Evitar que se complete dos veces
    if hasattr(usuario, 'perfil_profesional'):
        messages.info(request, 'Ya completaste tu perfil profesional.')
        return redirect('usuarios:login')

    if request.method == 'POST':
        form = PerfilProfesionalForm(request.POST)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

            messages.success(
                request,
                '¡Perfil profesional guardado! Revisa tu correo para activar tu cuenta.'
            )
            return redirect('usuarios:login')
    else:
        form = PerfilProfesionalForm()

    return render(request, 'usuarios/perfil_profesional.html', {
        'form': form,
        'usuario': usuario
    })
