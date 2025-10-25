# -------------------------------------------------------------------
# MENSAGEM IMPORTANTE:
# Este ficheiro 'forms.py' foi totalmente corrigido.
# 1. Ele agora importa 'Event' do 'models.py' que acabámos de criar.
# 2. Ele contém o seu 'EventForm' original (para o modal).
# 3. Ele contém o novo 'EventCrudForm' (para as páginas de CRUD).
# 4. Ambos os formulários usam 'model = Event'.
# -------------------------------------------------------------------

from django import forms
from .models import Event  # <--- Importa o modelo Event que criámos
from apps.weddings.models import Wedding
from apps.core.utils.django_forms import add_placeholder
from apps.core.utils.mixins import FormStylingMixin

# -------------------------------------------------
# 1. O SEU FORMULÁRIO ORIGINAL (Para o Modal)
# -------------------------------------------------
class EventForm(forms.ModelForm):
    """
    Este é o seu formulário original, usado no modal interativo.
    Ele usa campos separados de data/hora para facilitar o preenchimento.
    """
    
    # Campos separados para data e hora (para o modal)
    start_date = forms.DateField(
        label='Data de Início', 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    start_time_input = forms.TimeField(
        label='Hora de Início',
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
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
        model = Event  # <--- CORRIGIDO
        # Estes são os campos que o seu formulário tentava usar
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
        clicked_date = kwargs.pop('clicked_date', None)
        super().__init__(*args, **kwargs)
        
        if clicked_date:
            self.fields['start_date'].initial = clicked_date
            
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time_input = cleaned_data.get('start_time_input')
        
        # Combina data e hora no campo 'start_time' do modelo
        if start_date and start_time_input:
            cleaned_data['start_time'] = f'{start_date} {start_time_input}'
        
        end_date = cleaned_data.get('end_date')
        end_time_input = cleaned_data.get('end_time_input')
        
        # Combina data e hora no campo 'end_time' do modelo
        if end_date and end_time_input:
            cleaned_data['end_time'] = f'{end_date} {end_time_input}'
        elif end_date and not end_time_input:
            cleaned_data['end_time'] = f'{end_date} 23:59:59'
            
        return cleaned_data

# -------------------------------------------------
# 2. O NOVO FORMULÁRIO (Para o CRUD)
# -------------------------------------------------
class EventCrudForm(FormStylingMixin, forms.ModelForm):
    """
    Este é o novo formulário para as páginas de CRUD (Criar e Editar).
    Ele usa os campos 'start_time' e 'end_time' diretamente.
    """

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        # Filtra o dropdown 'wedding' para mostrar apenas os do planner logado
        if user:
            self.fields['wedding'].queryset = Wedding.objects.filter(planner=user)
        elif 'wedding' in self.fields:
             self.fields['wedding'].queryset = Wedding.objects.none()

        # Adicionar placeholders
        add_placeholder(self.fields['title'], 'Ex: Reunião com fornecedor')
        add_placeholder(self.fields['description'], 'Ex: Discutir flores e decoração')
        add_placeholder(self.fields['event_type'], 'Selecione um tipo')
        add_placeholder(self.fields['wedding'], 'Selecione um casamento (opcional)')

    class Meta:
        model = Event  # <--- CORRIGIDO
        # Usamos os campos reais do modelo
        fields = ['title', 'wedding', 'start_time', 'end_time', 'event_type', 'description', 'location']
        
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
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

