"""
Django management command to populate database with sample data.

Usage:
    python manage.py populate_db
    python manage.py populate_db --clear  # Clear existing data first
"""

from datetime import datetime, timedelta
from decimal import Decimal
from random import choice, randint, uniform

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.contracts.models import Contract
from apps.items.models import Item
from apps.scheduler.models import Event
from apps.weddings.models import Wedding

User = get_user_model()


class Command(BaseCommand):
    help = "Populate database with sample data for demo user"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing demo data before populating",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting database population..."))

        # Get or create demo user
        demo_user, created = self.get_or_create_demo_user()

        if created:
            self.stdout.write(self.style.SUCCESS("✓ Demo user created successfully!"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Using existing demo user: {demo_user.username}")
            )

        # Display credentials
        self.stdout.write(self.style.WARNING("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("📋 Demo User Credentials:"))
        self.stdout.write(self.style.SUCCESS("   Username: demo"))
        self.stdout.write(self.style.SUCCESS("   Password: demo123"))
        self.stdout.write(self.style.WARNING("=" * 60 + "\n"))

        # Clear data if requested
        if options["clear"]:
            self.clear_data(demo_user)

        # Populate data
        with transaction.atomic():
            weddings = self.create_weddings(demo_user)
            self.create_items(weddings)
            self.create_events(demo_user, weddings)

        self.stdout.write(self.style.SUCCESS("\n✅ Database populated successfully!"))
        self.stdout.write(
            self.style.SUCCESS("🚀 Access at http://localhost:8000 with demo/demo123")
        )

    def get_or_create_demo_user(self):
        """Get or create demo user with easy credentials."""
        username = "demo"
        email = "demo@wedding-management.com"
        password = "demo123"

        try:
            # Try to get existing demo user
            user = User.objects.get(username=username)
            return user, False
        except User.DoesNotExist:
            # Create new demo user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name="Demo",
                last_name="User",
            )
            return user, True

    def clear_data(self, demo_user):
        """Clear existing data for the demo user."""
        self.stdout.write(self.style.WARNING("\nClearing existing demo data..."))

        deleted_events = Event.objects.filter(planner=demo_user).delete()[0]
        deleted_items = Item.objects.filter(wedding__planner=demo_user).delete()[0]
        deleted_weddings = Wedding.objects.filter(planner=demo_user).delete()[0]

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Deleted: {deleted_weddings} weddings, "
                f"{deleted_items} items, {deleted_events} events"
            )
        )

    def create_weddings(self, demo_user):
        """Create sample weddings for demo user."""
        self.stdout.write(self.style.WARNING("\nCreating weddings..."))

        # Lists for generating varied data
        groom_names = [
            "João Silva",
            "Pedro Costa",
            "Carlos Mendes",
            "Lucas Almeida",
            "Rafael Santos",
            "Bruno Oliveira",
            "Felipe Rocha",
            "Gabriel Lima",
            "Thiago Martins",
        ]
        bride_names = [
            "Maria Santos",
            "Ana Oliveira",
            "Julia Ferreira",
            "Beatriz Costa",
            "Camila Souza",
            "Larissa Pereira",
            "Amanda Silva",
            "Isabela Rodrigues",
            "Fernanda Alves",
        ]
        locations = [
            "Hotel Fazenda Vista Alegre",
            "Espaço Green Garden",
            "Praia do Rosa",
            "Sítio Recanto das Flores",
            "Clube Náutico",
            "Chácara Bela Vista",
            "Mansão Colonial",
            "Jardim Botânico",
            "Casa de Eventos Sunset",
        ]

        # Generate budgets from 40k to 120k
        budgets = [Decimal(str(amount)) for amount in range(40000, 130000, 10000)]

        # Generate dates from Dec 2025 to Dec 2026
        base_month = 12
        base_year = 2025
        dates = []
        for i in range(9):
            month = (base_month + i) % 12 or 12
            year = base_year + ((base_month + i - 1) // 12)
            day = randint(5, 28)
            dates.append(datetime(year, month, day).date())

        weddings = []
        for i in range(9):
            wedding = Wedding.objects.create(
                planner=demo_user,
                groom_name=groom_names[i],
                bride_name=bride_names[i],
                date=dates[i],
                location=locations[i],
                budget=budgets[i],
                status=Wedding.StatusChoices.IN_PROGRESS,
            )
            weddings.append(wedding)
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ Created wedding: {wedding.groom_name} & {wedding.bride_name}"
                )
            )

        return weddings

    def create_items(self, weddings):
        """Create sample items and contracts for weddings."""
        self.stdout.write(self.style.WARNING("\nCreating items and contracts..."))

        # Define item categories with their properties
        item_categories = {
            "LOCAL": [
                ("Aluguel do Espaço", 8000, 1, "Eventos & Espaços Ltda"),
                ("Decoração do Espaço", 3500, 1, "Flores e Arte Decorações"),
            ],
            "BUFFET": [
                ("Buffet Completo", 150, 200, "Sabor & Cia Buffet"),
                ("Bolo de Casamento", 800, 1, "Confeitaria Doce Momento"),
                ("Bebidas Premium", 50, 200, "Adega Vinhos & Drinks"),
            ],
            "DECOR": [
                ("Arranjos Florais", 200, 20, "Floricultura Jardim Secreto"),
                ("Iluminação Especial", 2500, 1, "Light & Show Produções"),
            ],
            "PHOTO_VIDEO": [
                ("Fotografia Profissional", 5000, 1, "Studio Flash Fotografia"),
                ("Filmagem e Edição", 4500, 1, "Cine Wedding Films"),
                ("Drone para Filmagem", 1200, 1, "Sky View Productions"),
            ],
            "ATTIRE": [
                ("Vestido de Noiva", 6000, 1, "Atelier Branco e Brilho"),
                ("Terno do Noivo", 2500, 1, "Elegance Men's Fashion"),
            ],
            "MUSIC": [
                ("DJ Profissional", 3000, 1, "DJ Festa Total"),
                ("Banda ao Vivo", 5000, 1, "Banda Harmony Live"),
            ],
            "OTHERS": [
                ("Convites Personalizados", 15, 200, "Gráfica Arte & Papel"),
                ("Lembrancinhas", 12, 200, "Presentes & Mimos"),
                ("Cerimonial e Assessoria", 4000, 1, "Assessoria Premium Eventos"),
            ],
        }

        # Flatten all items into a single list
        all_items = [
            {
                "name": name,
                "category": category,
                "unit_price": Decimal(str(price)),
                "quantity": qty,
                "supplier": supplier,
            }
            for category, items in item_categories.items()
            for name, price, qty, supplier in items
        ]

        statuses = ["PENDING", "IN_PROGRESS", "DONE"]
        total_items = 0

        for wedding in weddings:
            # Each wedding gets 8-12 random items
            num_items = randint(8, 12)
            selected_templates = [choice(all_items) for _ in range(num_items)]

            for template in selected_templates:
                # Vary quantities and prices slightly (80-120% variation)
                quantity_variation = uniform(0.8, 1.2)
                price_variation = uniform(0.9, 1.1)

                # Create item and contract in atomic transaction
                with transaction.atomic():
                    item = Item.objects.create(
                        wedding=wedding,
                        name=template["name"],
                        description=(
                            f"Item para o casamento de "
                            f"{wedding.groom_name} & {wedding.bride_name}"
                        ),
                        category=template["category"],
                        quantity=max(1, int(template["quantity"] * quantity_variation)),
                        unit_price=Decimal(
                            str(float(template["unit_price"]) * price_variation)
                        ),
                        supplier=template["supplier"],
                        status=choice(statuses),
                    )
                    # Create contract for this item (following AddItemView pattern)
                    Contract.objects.create(item=item)

                total_items += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ Created {num_items} items with contracts for "
                    f"{wedding.groom_name} & {wedding.bride_name}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal items created: {total_items} (each with a contract)"
            )
        )

    def create_events(self, demo_user, weddings):
        """Create sample events in December 2025 for demo user."""
        self.stdout.write(self.style.WARNING("\nCreating events..."))

        # Base date: December 2025
        base_date = datetime(2025, 12, 1, tzinfo=timezone.get_current_timezone())

        # Define event templates as tuples:
        # (title, type, location, description, duration)
        event_templates = [
            (
                "Reunião com Fornecedor do Buffet",
                Event.TypeChoices.MEETING,
                "Escritório do Buffet",
                "Definir menu final e quantidade de convidados",
                2,
            ),
            (
                "Pagamento Fornecedor",
                Event.TypeChoices.PAYMENT,
                "Banco/Online",
                "Pagamento de entrada do fornecedor",
                1,
            ),
            (
                "Visita ao Local da Cerimônia",
                Event.TypeChoices.VISIT,
                "Local do Evento",
                "Vistoria final do espaço e detalhes da decoração",
                3,
            ),
            (
                "Degustação do Menu",
                Event.TypeChoices.TASTING,
                "Buffet",
                "Degustação do menu escolhido pelos noivos",
                2,
            ),
            (
                "Reunião de Alinhamento",
                Event.TypeChoices.MEETING,
                "Escritório",
                "Alinhamento geral de todos os fornecedores",
                1,
            ),
            (
                "Prova do Vestido",
                Event.TypeChoices.OTHER,
                "Atelier",
                "Última prova do vestido de noiva",
                2,
            ),
            (
                "Ensaio Fotográfico",
                Event.TypeChoices.OTHER,
                "Parque Municipal",
                "Ensaio pré-wedding",
                4,
            ),
        ]

        total_events = 0
        for wedding in weddings:
            # Create 5-8 events per wedding in December
            num_events = randint(5, 8)

            for _ in range(num_events):
                # Random day in December (1-31)
                day = randint(1, 31)
                try:
                    # Random hour between 9 AM and 6 PM
                    hour = randint(9, 18)
                    start_time = base_date.replace(
                        day=day, hour=hour, minute=0, second=0
                    )

                    # Unpack template tuple
                    template = choice(event_templates)
                    title, event_type, location, description, duration = template
                    end_time = start_time + timedelta(hours=duration)

                    Event.objects.create(
                        wedding=wedding,
                        planner=demo_user,
                        title=title,
                        event_type=event_type,
                        location=location,
                        description=description,
                        start_time=start_time,
                        end_time=end_time,
                    )
                    total_events += 1

                except ValueError:
                    # Skip invalid dates (e.g., December 31 doesn't exist in some cases)
                    continue

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ Created events for "
                    f"{wedding.groom_name} & {wedding.bride_name}"
                )
            )

        self.stdout.write(self.style.SUCCESS(f"\nTotal events created: {total_events}"))
        self.stdout.write(self.style.SUCCESS("All events scheduled for December 2025"))
