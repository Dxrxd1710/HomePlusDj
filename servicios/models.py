from django.db import models
from django.shortcuts import redirect
from usuarios.models import Usuario


class Servicio(models.Model):

    CATEGORIA_CHOICES = [
        ('plomeria', 'Plomería'),
        ('electricidad', 'Electricidad'),
        ('pintura', 'Pintura'),
        ('limpieza', 'Limpieza'),
        ('otro', 'Otro'),
    ]

    URGENCIA_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]

    ESTADO_CHOICES = [
        ('publicado', 'Publicado'),
        ('proceso', 'En proceso'),
        ('finalizado', 'Finalizado'),
    ]

    id_servicio = models.AutoField(primary_key=True)

    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='servicios'
    )

    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()

    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    referencia = models.TextField(blank=True, null=True)

    urgencia = models.CharField(max_length=10, choices=URGENCIA_CHOICES)

    # 🔥 ESTADO AUTOMÁTICO
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='publicado'  # 👈 CLAVE
    )

    requiere_visita = models.BooleanField(default=False)
    fecha_visita = models.DateTimeField(blank=True, null=True)

    imagen = models.ImageField(upload_to='servicios/', blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.cliente.nombre}"

    contrato = models.FileField(
        upload_to='contratos/',
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='publicado'
    )
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
    ]

    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        blank=True,
        null=True
    )


class Aplicacion(models.Model):

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
    ]

    profesional = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name='aplicaciones'
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profesional.nombre} → {self.servicio.titulo}"


class Evidencia(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='evidencias/')
    fecha = models.DateTimeField(auto_now_add=True)


class Calificacion(models.Model):

    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='calificaciones_realizadas'
    )

    profesional = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='calificaciones_recibidas'
    )

    servicio = models.OneToOneField(
        Servicio,
        on_delete=models.CASCADE
    )

    puntuacion = models.IntegerField()  # 1 a 5
    comentario = models.TextField(blank=True, null=True)

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.puntuacion}⭐ - {self.profesional.nombre}"


class VisitaDiagnostico(models.Model):

    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    profesional = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    fecha_propuesta = models.DateTimeField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('aceptada', 'Aceptada'),
            ('rechazada', 'Rechazada'),
        ],
        default='pendiente'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)


def proponer_visita(request, id):

    servicio = Servicio.objects.get(id_servicio=id)

    if request.method == 'POST':
        fecha = request.POST.get('fecha')

        VisitaDiagnostico.objects.create(
            servicio=servicio,
            profesional=servicio.aplicaciones.filter(
                estado='aceptado').first().profesional,
            fecha_propuesta=fecha
        )

        return redirect('servicios:dashboard')


def responder_visita(request, id):

    visita = VisitaDiagnostico.objects.get(id=id)

    accion = request.POST.get('accion')

    if accion == 'aceptar':
        visita.estado = 'aceptada'
        visita.fecha_confirmada = visita.fecha_propuesta

    elif accion == 'rechazar':
        visita.estado = 'rechazada'

    elif accion == 'reprogramar':
        nueva_fecha = request.POST.get('nueva_fecha')
        visita.estado = 'reprogramar'
        visita.fecha_propuesta = nueva_fecha

    visita.save()

    return redirect('servicios:dashboard_profesional')


class Reprogramacion(models.Model):

    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)

    profesional = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    nueva_fecha = models.DateTimeField()

    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('aceptada', 'Aceptada'),
            ('rechazada', 'Rechazada'),
        ],
        default='pendiente'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
