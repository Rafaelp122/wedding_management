# MENSAGEM: O EventForm (do modal) foi atualizado:
# 1. O campo 'end_time_input' (Hora de Fim) foi re-adicionado (required=False).
# 2. O campo 'event_date' permanece oculto (o label será removido no template).

from django import forms
from .models import Event
from apps.weddings.models import Wedding
from apps.core.utils.django_forms import add_placeholder
from apps.core.utils.mixins import FormStylingMixin
from django.utils import timezone

# -------------------------------------------------
# 1. O FORMULÁRIO DO MODAL (Com Hora de Fim)
# -------------------------------------------------
class EventForm(forms.ModelForm):
    """
    Formulário do modal.
    - 'event_date' é um campo oculto para guardar a data.
    - 'start_time_input' e 'end_time_input' são visíveis.
    """
    
    # Campo de data (continua oculto)
    event_date = forms.DateField(
        widget=forms.HiddenInput(),
        required=True
    )

    # Hora de início (obrigatório)
    start_time_input = forms.TimeField(
        label='Hora de Início',
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=True
    )
    
    # --- CAMPO ADICIONADO ---
    # Hora de fim (opcional)
    end_time_input = forms.TimeField(
        label='Hora de Fim',
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=False  # <--- Opcional
    )

    class Meta:
        model = Event
        # --- CAMPOS MODIFICADOS ---
        # Adicionamos 'end_time_input' de volta
        fields = [
            'title', 'location', 'description', 'event_type', 
            'event_date', 'start_time_input', 'end_time_input' 
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
        clicked_date = kwargs.pop('clicked_date', None) 
        instance = kwargs.get('instance')
        
        super().__init__(*args, **kwargs)
        
        if instance:
            # Se for EDITAR, preenche os campos com dados da instância
            if instance.start_time:
                local_start_time = timezone.localtime(instance.start_time)
                self.fields['event_date'].initial = local_start_time.date()
                self.fields['start_time_input'].initial = local_start_time.time()
            
            # --- LÓGICA ADICIONADA ---
            if instance.end_time:
                local_end_time = timezone.localtime(instance.end_time)
                self.fields['end_time_input'].initial = local_end_time.time()
        
        elif clicked_date:
            # Se for CRIAR, preenche a data com o clique do calendário
            self.fields['event_date'].initial = clicked_date
            

    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get('event_date')
        start_time_input = cleaned_data.get('start_time_input')
        
        # Combina data e hora no campo 'start_time' do modelo
        if event_date and start_time_input:
            cleaned_data['start_time'] = f'{event_date} {start_time_input}'
        
        # --- LÓGICA ADICIONADA ---
        end_time_input = cleaned_data.get('end_time_input')
        
        # Combina data e hora no campo 'end_time' do modelo
        if event_date and end_time_input:
            cleaned_data['end_time'] = f'{event_date} {end_time_input}'
        
        return cleaned_data

# -------------------------------------------------
# 2. O NOVO FORMULÁRIO (Para o CRUD) - Sem alterações
# -------------------------------------------------
class EventCrudForm(FormStylingMixin, forms.ModelForm):
    # ... (Este formulário permanece exatamente igual ao anterior) ...
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        if user:
            self.fields['wedding'].queryset = Wedding.objects.filter(planner=user)
        elif 'wedding' in self.fields:
             self.fields['wedding'].queryset = Wedding.objects.none()
        add_placeholder(self.fields['title'], 'Ex: Reunião com fornecedor')
        add_placeholder(self.fields['description'], 'Ex: Discutir flores e decoração')
        add_placeholder(self.fields['event_type'], 'Selecione um tipo')
        add_placeholder(self.fields['wedding'], 'Selecione um casamento (opcional)')
    class Meta:
        model = Event
        fields = ['title', 'wedding', 'start_time', 'end_time', 'event_type', 'description', 'location']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': 'Título do Evento',
            'wedding': 'Casamento Vinculado',
            'start_time': 'Data e Hora de Início',
            'end_time': 'Data e Hora de Fim',
            'event_type': 'Tipo de Evento',
            'description': 'Descrição',
            'location': 'Local',
        }