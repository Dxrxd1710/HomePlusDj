from django import forms
from .models import Servicio


class ServicioForm(forms.ModelForm):

    class Meta:
        model = Servicio
        fields = [
            'categoria',
            'titulo',
            'descripcion',
            'ciudad',
            'direccion',
            'referencia',
            'urgencia',
            'requiere_visita',
            'fecha_visita',
            'imagen'
        ]

        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_visita': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.fecha_visita:
            self.initial['fecha_visita'] = self.instance.fecha_visita.strftime('%Y-%m-%dT%H:%M')

        self.fields['imagen'].required = False

    def clean(self):
        cleaned_data = super().clean()

        requiere_visita = cleaned_data.get('requiere_visita')
        fecha_visita = cleaned_data.get('fecha_visita')
        imagen = cleaned_data.get('imagen')

        if requiere_visita and not fecha_visita:
            raise forms.ValidationError(
                "Debes seleccionar una fecha y hora para la visita."
            )

        if not imagen and not self.instance.imagen:
            raise forms.ValidationError(
                "Debes subir una imagen para el servicio."
            )

        return cleaned_data