import random
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.contrib.auth import get_user_model

# --------------------------------------------------------------------------
# Importe seus modelos
# --------------------------------------------------------------------------
from apps.weddings.models import Wedding
from apps.items.models import Item
from apps.contracts.models import Contract
from apps.supplier.models import Supplier

# --- Listas de dados de exemplo para aleatoriedade ---

GROOM_NAMES = ['Rafael', 'Bruno', 'Thiago', 'Lucas', 'Diogo', 'Matheus', 'Felipe']
BRIDE_NAMES = ['Juliana', 'Camila', 'Fernanda', 'Amanda', 'Beatriz', 'Larissa', 'Gabriela']
# Esta lista será usada para o 'name' do Item
ITEM_NAMES = ['Decoração Salão', 'Buffet Completo', 'Banda ao Vivo', 'Fotografia e Vídeo', 'Espaço (Aluguer)', 'Cerimonialista', 'Convites']
ITEM_STATUSES = ['DONE', 'IN_PROGRESS', 'PENDING']
SUPPLIERS = ['Eventos Mágicos', 'Delícias da Serra', 'Som & Luz Pro', 'Foto Eterna', 'Recanto Feliz']


class Command(BaseCommand):
    """
    Comando de gestão para popular o banco de dados com dados de teste.
    Cria Casamentos, e Itens/Contratos relacionados para cada um.
    """
    
    help = 'Popula o banco com dados de teste para Casamentos, Itens e Contratos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--total',
            type=int,
            default=50,
            help='O número total de CASAMENTOS a serem criados.'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """
        O ponto de entrada principal do comando.
        """
        
        User = get_user_model()
        total_weddings = options['total']
        self.stdout.write(self.style.SUCCESS(f'Iniciando...'))

        # -----------------------------------------------------------------
        # Busque um planner (usuário) para associar
        # -----------------------------------------------------------------
        try:
            planner_to_assign = User.objects.filter(is_superuser=True).first()
            if not planner_to_assign:
                planner_to_assign = User.objects.first()
            if not planner_to_assign:
                self.stdout.write(self.style.ERROR(
                    'Nenhum utilizador (planner) encontrado! '
                    'Por favor, crie um superuser (python manage.py createsuperuser) antes de rodar este comando.'
                ))
                return 
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao buscar planner: {e}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Usando o planner "{planner_to_assign}" para todos os novos casamentos.'))
        
        # -----------------------------------------------------------------
        # Obter ou Criar Fornecedores
        # -----------------------------------------------------------------
        self.stdout.write(self.style.WARNING('Preparando fornecedores...'))
        suppliers_in_db = []
        
        for i, supplier_name in enumerate(SUPPLIERS):
            fake_email_name = supplier_name.lower().replace(' ', '_').replace('&', 'e')
            fake_email = f"{fake_email_name}_{i}@fake.com"
            fake_cnpj = f"00.000.000/0001-{i:02d}"
            
            defaults = {
                'email': fake_email,
                'cpf_cnpj': fake_cnpj,
                'phone': "(00) 00000-0000",
                'offered_services': f"Serviços de teste para {supplier_name}"
            }

            try:
                supplier, created = Supplier.objects.get_or_create(
                    name=supplier_name,
                    defaults=defaults
                )
                if created:
                    self.stdout.write(f'  -> Fornecedor "{supplier_name}" criado.')
                suppliers_in_db.append(supplier)
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Erro de integridade: {e}'))
                return
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro desconhecido: {e}'))
                return

        self.stdout.write(f'Serão criados {total_weddings} casamentos (e seus itens/contratos)...')
        items_to_create = []
        contracts_to_create = []

        # --- 2. Criar os Casamentos ---
        for i in range(total_weddings):
            
            groom = f"{random.choice(GROOM_NAMES)} {i}"
            bride = f"{random.choice(BRIDE_NAMES)} {i}"
            date = timezone.now().date() + timezone.timedelta(days=random.randint(30, 730))
            
            wedding = Wedding.objects.create(
                groom_name=groom,
                bride_name=bride,
                date=date,
                status='IN_PROGRESS',
                budget=random.uniform(5000.0, 50000.0), 
                planner=planner_to_assign
            )

            # -----------------------------------------------------------------
            # ✨ CORREÇÃO: Preparar Itens para este Casamento
            # -----------------------------------------------------------------
            num_items = random.randint(3, len(ITEM_NAMES))
            # Usa a lista 'ITEM_NAMES'
            shuffled_names = random.sample(ITEM_NAMES, num_items) 
            
            for item_name in shuffled_names:
                items_to_create.append(
                    Item(
                        wedding=wedding,
                        # Campos obrigatórios adicionados:
                        name=item_name,
                        quantity=random.randint(1, 5),
                        unit_price=random.uniform(100.0, 5000.0),
                        # Campo opcional (mas bom ter)
                        description=f"Descrição de teste para {item_name}",
                        # Status (baseado no seu modelo)
                        status=random.choice(ITEM_STATUSES)
                    )
                )

            # --- 4. Preparar Contratos para este Casamento ---
            num_contracts = random.randint(1, 3)
            shuffled_suppliers = random.sample(suppliers_in_db, num_contracts) 
            
            for supplier_obj in shuffled_suppliers:
                sig_date = timezone.now().date() - timezone.timedelta(days=random.randint(0, 30))
                
                contracts_to_create.append(
                    Contract(
                        wedding=wedding,
                        supplier=supplier_obj,
                        signature_date=sig_date
                    )
                )
            
            if (i + 1) % (total_weddings // 5 or 1) == 0:
                self.stdout.write(f'  -> {i + 1} / {total_weddings} casamentos criados...')

        # --- 5. Executar a Criação em Massa (Bulk Create) ---
        
        self.stdout.write(self.style.WARNING(f'\nInserindo {len(items_to_create)} itens no banco...'))
        Item.objects.bulk_create(items_to_create)

        self.stdout.write(self.style.WARNING(f'Inserindo {len(contracts_to_create)} contratos no banco...'))
        Contract.objects.bulk_create(contracts_to_create)

        self.stdout.write(self.style.SUCCESS('\nConcluído! Banco de dados populado com sucesso.'))
