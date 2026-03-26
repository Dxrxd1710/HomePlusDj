"""
URL configuration for homeplus project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from usuarios.views import landing

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),

    # Usuarios (login, registro, etc.)
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),

    # Landing
    path('', landing, name='landing'),

    # Servicios (dashboard)
    path('servicios/', include('servicios.urls', namespace='servicios')),
]

# 🔥 Esto SIEMPRE va después
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)