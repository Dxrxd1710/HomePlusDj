"""
HOME+ - Módulo de Gestión de Usuarios
Formularios de registro, login y recuperación de contraseña
"""

from django import forms
from .models import Usuario, PerfilProfesional


class RegistroForm(forms.ModelForm):
    """Formulario de registro de nuevos usuarios."""

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña'
        }),
        min_length=8,
        error_messages={'min_length': 'La contraseña debe tener al menos 8 caracteres.'}
    )
    confirmar_password = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña'
        })
    )

    class Meta:
        model = Usuario
        fields = [
            'nombre', 'apellido', 'correo',
            'telefono', 'direccion', 'tipo_usuario'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu apellido'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de teléfono'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tu dirección completa',
                'rows': 3
            }),
            'tipo_usuario': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def clean_correo(self):
        """Valida que el correo sea único."""
        correo = self.cleaned_data.get('correo')
        if Usuario.objects.filter(correo=correo).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return correo

    def clean_telefono(self):
        """Valida que el teléfono sea numérico."""
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            raise forms.ValidationError('El teléfono solo debe contener números.')
        return telefono

    def clean(self):
        """Valida que las contraseñas coincidan."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar = cleaned_data.get('confirmar_password')

        if password and confirmar and password != confirmar:
            self.add_error('confirmar_password', 'Las contraseñas no coinciden.')

        return cleaned_data


class LoginForm(forms.Form):
    """Formulario de inicio de sesión."""

    correo = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu contraseña'
        })
    )


class RecuperarPasswordForm(forms.Form):
    """Formulario para solicitar recuperación de contraseña."""

    correo = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )

    def clean_correo(self):
        """Verifica que el correo esté registrado."""
        correo = self.cleaned_data.get('correo')
        if not Usuario.objects.filter(correo=correo).exists():
            raise forms.ValidationError('No existe una cuenta con este correo.')
        return correo


class ResetPasswordForm(forms.Form):
    """Formulario para establecer nueva contraseña."""

    nueva_password = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        }),
        min_length=8,
        error_messages={'min_length': 'La contraseña debe tener al menos 8 caracteres.'}
    )
    confirmar_password = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma la nueva contraseña'
        })
    )

    def clean(self):
        """Valida que las contraseñas coincidan."""
        cleaned_data = super().clean()
        nueva = cleaned_data.get('nueva_password')
        confirmar = cleaned_data.get('confirmar_password')

        if nueva and confirmar and nueva != confirmar:
            self.add_error('confirmar_password', 'Las contraseñas no coinciden.')

        return cleaned_data


class PerfilProfesionalForm(forms.ModelForm):
    """Formulario para completar el perfil del profesional."""

    class Meta:
        model = PerfilProfesional
        fields = [
            'servicio', 'servicio_descripcion',
            'anos_experiencia', 'historial', 'certificaciones'
        ]
        widgets = {
            'servicio': forms.Select(attrs={
                'class': 'form-control'
            }),
            'servicio_descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe el servicio que ofreces (ej: instalación de tuberías, reparación de fugas, etc.)',
                'rows': 3
            }),
            'anos_experiencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 5',
                'min': 0,
                'max': 60
            }),
            'historial': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Cuéntanos sobre tu experiencia, empresas donde trabajaste, proyectos realizados...',
                'rows': 5
            }),
            'certificaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional: certificaciones, cursos técnicos, títulos relacionados...',
                'rows': 3
            }),
        }
        labels = {
            'servicio': 'Tipo de servicio que brindas',
            'servicio_descripcion': 'Descripción del servicio',
            'anos_experiencia': 'Años de experiencia',
            'historial': 'Historial profesional',
            'certificaciones': 'Certificaciones o estudios (opcional)',
        }

    def clean_anos_experiencia(self):
        """Valida que los años de experiencia sean un valor razonable."""
        anos = self.cleaned_data.get('anos_experiencia')
        if anos is not None and anos > 60:
            raise forms.ValidationError('Por favor ingresa un valor válido de años de experiencia.')
        return anos
