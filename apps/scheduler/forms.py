# apps/scheduler/forms.py

from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    
    # Usamos campos específicos para data e hora para facilitar
    # o preenchimento no modal.
    start_date = forms.DateField(
        label='Data de Início', 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    start_time_input = forms.TimeField(
        label='Hora de Início',
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    
    # Opcional: Data/Hora de Fim
    end_date = forms.DateField(
        label='Data de Fim',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_time_input = forms.TimeField(
        label='Hora de Fim',
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )

    class Meta:
        model = Event
        fields = [
            'title', 'location', 'description', 'event_type', 
            'start_date', 'start_time_input', 'end_date', 'end_time_input'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Reunião com Decorador'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Escritório Decoração Fina'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'title': 'Título do Evento',
            'location': 'Local',
            'description': 'Descrição',
            'event_type': 'Tipo de Evento',
        }

    def __init__(self, *args, **kwargs):
        # Pega a data clicada que passaremos pela view
        clicked_date = kwargs.pop('clicked_date', None)
        super().__init__(*args, **kwargs)
        
        # Pré-preenche a data de início com o dia que o usuário clicou
        if clicked_date:
            self.fields['start_date'].initial = clicked_date
            
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time_input = cleaned_data.get('start_time_input')
        
        # Combina data e hora em um único campo DateTimeField
        if start_date and start_time_input:
            cleaned_data['start_time'] = f'{start_date} {start_time_input}'
        
        # Faz o mesmo para o fim (se houver)
        end_date = cleaned_data.get('end_date')
        end_time_input = cleaned_data.get('end_time_input')
        
        if end_date and end_time_input:
            cleaned_data['end_time'] = f'{end_date} {end_time_input}'
        elif end_date and not end_time_input:
            # Se só preencheu a data de fim, assume o dia todo
            cleaned_data['end_time'] = f'{end_date} 23:59:59'
            
        return cleaned_data