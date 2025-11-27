import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.contracts.models import Contract
from apps.items.models import Item

# --------------------------------------------------------------------------
# Importe seus modelos
# --------------------------------------------------------------------------
from apps.weddings.models import Wedding

# --- Listas de dados de exemplo para aleatoriedade ---

GROOM_NAMES = ["Rafael", "Bruno", "Thiago", "Lucas", "Diogo", "Matheus", "Felipe"]
BRIDE_NAMES = [
    "Juliana",
    "Camila",
    "Fernanda",
    "Amanda",
    "Beatriz",
    "Larissa",
    "Gabriela",
]
ITEM_NAMES = [
    "Decoração Salão",
    "Buffet Completo",
    "Banda ao Vivo",
    "Fotografia e Vídeo",
    "Espaço (Aluguer)",
    "Cerimonialista",
    "Convites",
]
ITEM_CATEGORIES = ["DECORATION", "FOOD", "MUSIC", "PHOTO_VIDEO", "VENUE", "SERVICE"]
ITEM_STATUSES = ["DONE", "IN_PROGRESS", "PENDING"]
SUPPLIERS = [
    "Eventos Mágicos",
    "Delícias da Serra",
    "Som & Luz Pro",
    "Foto Eterna",
    "Recanto Feliz",
    "Detalhes & Cia",
]


class Command(BaseCommand):
    """
    Comando de gestão para popular o banco de dados com dados de teste.
    Cria Casamentos, Itens e Contratos (1 para cada item).
    """

    help = "Popula o banco com dados de teste para Casamentos, Itens e Contratos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--total",
            type=int,
            default=50,
            help="O número total de CASAMENTOS a serem criados.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """
        O ponto de entrada principal do comando.
        """
        User = get_user_model()
        total_weddings = options["total"]
        self.stdout.write(self.style.SUCCESS("Iniciando..."))

        # -----------------------------------------------------------------
        # Limpa os dados existentes para evitar duplicatas
        # -----------------------------------------------------------------
        self.stdout.write(self.style.WARNING("Limpando dados antigos..."))
        Contract.objects.all().delete()
        Item.objects.all().delete()
        Wedding.objects.all().delete()

        # -----------------------------------------------------------------
        # Busque um planner (usuário) para associar
        # -----------------------------------------------------------------
        planner_to_assign = User.objects.filter(is_superuser=True).first()
        if not planner_to_assign:
            planner_to_assign = User.objects.first()

        if not planner_to_assign:
            self.stdout.write(
                self.style.ERROR(
                    "Nenhum utilizador (planner) encontrado! "
                    "Crie um superuser (createsuperuser) antes de rodar este comando."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Usando o planner "{planner_to_assign}" para todos os novos casamentos.'
            )
        )

        self.stdout.write(
            f"Serão criados {total_weddings} casamentos (e seus itens/contratos)..."
        )

        items_to_create = []

        # --- 1. Criar os Casamentos e preparar os Itens ---
        for i in range(total_weddings):
            wedding = Wedding.objects.create(
                groom_name=f"{random.choice(GROOM_NAMES)} {i}",
                bride_name=f"{random.choice(BRIDE_NAMES)} {i}",
                date=timezone.now().date()
                + timezone.timedelta(days=random.randint(30, 730)),
                status=random.choice(["IN_PROGRESS", "DONE", "PENDING"]),
                budget=random.uniform(5000.0, 50000.0),
                planner=planner_to_assign,
            )

            # --- 2. Preparar Itens para este Casamento ---
            num_items = random.randint(3, len(ITEM_NAMES))
            shuffled_names = random.sample(ITEM_NAMES, num_items)

            for item_name in shuffled_names:
                items_to_create.append(
                    Item(
                        wedding=wedding,
                        name=item_name,
                        quantity=random.randint(1, 5),
                        unit_price=random.uniform(100.0, 5000.0),
                        description=f"Descrição de teste para {item_name}",
                        status=random.choice(ITEM_STATUSES),
                        category=random.choice(ITEM_CATEGORIES),
                        supplier=random.choice(SUPPLIERS),  # Fornecedor como CharField
                    )
                )
            if (i + 1) % (total_weddings // 5 or 1) == 0:
                self.stdout.write(
                    f"  -> {i + 1} / {total_weddings} casamentos preparados..."
                )

        # --- 3. Executar a Criação em Massa de Itens ---
        self.stdout.write(
            self.style.WARNING(f"\nInserindo {len(items_to_create)} itens no banco...")
        )
        # bulk_create retorna a lista de objetos criados
        created_items = Item.objects.bulk_create(items_to_create)

        # --- 4. Preparar e Criar Contratos para cada Item criado ---
        contracts_to_create = []
        for item in created_items:
            sig_date = item.created_at.date() - timezone.timedelta(
                days=random.randint(0, 30)
            )
            contracts_to_create.append(
                Contract(
                    item=item,
                    signature_date=sig_date,
                    status=random.choice(["PENDING", "SIGNED"]),
                )
            )

        self.stdout.write(
            self.style.WARNING(
                f"Inserindo {len(contracts_to_create)} contratos no banco..."
            )
        )
        Contract.objects.bulk_create(contracts_to_create)

        self.stdout.write(
            self.style.SUCCESS("\nConcluído! Banco de dados populado com sucesso.")
        )
