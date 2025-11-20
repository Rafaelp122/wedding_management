from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

# Se Contracts já existir, precisamos dele para testar a criação automática
from apps.contracts.models import Contract
from apps.items.models import Item
from apps.users.models import User
from apps.weddings.models import Wedding


class ItemListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("planner", "p@t.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="G", bride_name="B",
            date=timezone.now().date() + timedelta(days=365),
            location="Loc", budget=1000
        )
        # Cria 7 itens para testar paginação (paginate_by=6)
        for i in range(7):
            Item.objects.create(
                wedding=cls.wedding, name=f"Item {i}",
                quantity=1, unit_price=10
            )
        cls.url = reverse("items:partial_items", kwargs={"wedding_id": cls.wedding.id})

    def setUp(self):
        self.client.force_login(self.user)

    def test_full_page_load(self):
        """Acesso normal (F5) renderiza a aba inteira."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "items/item_list.html")
        self.assertIn("items", response.context)
        self.assertEqual(len(response.context["items"]), 6)

    def test_htmx_partial_load(self):
        """Acesso HTMX com target específico renderiza apenas a lista."""
        headers = {
            "HTTP_HX-Request": "true",
            "HTTP_HX-Target": "item-list-container"
        }
        response = self.client.get(self.url, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "items/partials/_list_and_pagination.html")
        self.assertTemplateNotUsed(response, "items/item_list.html")

    def test_other_user_cannot_access(self):
        """Outro usuário deve receber 404 (devido ao get_object_or_404 no Mixin)."""
        other = User.objects.create_user("other", "o@t.com", "123")
        self.client.force_login(other)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_view_integrates_search_param(self):
        """
        Testa se passar ?q=... na URL realmente filtra a lista visualizada.
        """
        # Cria um item com nome único
        Item.objects.create(
            wedding=self.wedding, name="UniqueItemXYZ",
            quantity=1, unit_price=10
        )

        # Faz o GET com busca (simulando HTMX)
        headers = {"HTTP_HX-Request": "true", "HTTP_HX-Target": "item-list-container"}
        response = self.client.get(f"{self.url}?q=UniqueItemXYZ", **headers)

        # A lista paginada deve conter apenas 1 item
        items = response.context["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, "UniqueItemXYZ")

    def test_view_integrates_sort_param(self):
        """
        Testa se passar ?sort=price_desc ordena corretamente.
        """
        # Item barato
        Item.objects.create(
            wedding=self.wedding, name="Barato",
            quantity=1, unit_price=1.00
        )
        # Item caro
        Item.objects.create(
            wedding=self.wedding, name="Caro",
            quantity=1, unit_price=9999.00
        )

        headers = {"HTTP_HX-Request": "true", "HTTP_HX-Target": "item-list-container"}
        response = self.client.get(f"{self.url}?sort=price_desc", **headers)

        items = response.context["items"]
        # O primeiro deve ser o Caro
        self.assertEqual(items[0].name, "Caro")


class AddItemViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("planner", "p@t.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="G", bride_name="B",
            date=timezone.now().date() + timedelta(days=365),
            location="Loc", budget=1000
        )
        cls.url = reverse("items:add_item", kwargs={"wedding_id": cls.wedding.id})

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_renders_modal(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/form_modal.html")
        self.assertEqual(response.context["wedding"], self.wedding)

    def test_post_valid_creates_item_and_contract(self):
        """
        O POST válido deve criar o Item E o Contrato associado.
        """
        data = {
            "name": "Novo Item",
            "category": "DECOR",
            "quantity": 10,
            "unit_price": "5.00",
            "supplier": "Loja X",
            "description": "Desc"
        }
        headers = {"HTTP_HX-Request": "true"}

        response = self.client.post(self.url, data, **headers)

        self.assertEqual(response.status_code, 200)

        # Verifica Item
        item = Item.objects.get(name="Novo Item")
        self.assertEqual(item.wedding, self.wedding)

        # Verifica Contrato (Regra de Negócio Crítica)
        self.assertTrue(Contract.objects.filter(item=item).exists())

    def test_post_invalid_returns_form_with_errors(self):
        """POST inválido deve retornar o modal com erros (UX)."""
        data = {"name": ""}  # Inválido
        headers = {"HTTP_HX-Request": "true"}

        response = self.client.post(self.url, data, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/form_modal.html")
        self.assertTrue(response.context["form"].errors)


class UpdateItemStatusViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("planner", "p@t.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="G", bride_name="B",
            date=timezone.now().date() + timedelta(days=365),
            location="Loc", budget=1000
        )
        cls.item = Item.objects.create(
            wedding=cls.wedding, name="Item", quantity=1, unit_price=10,
            status="PENDING"
        )
        cls.url = reverse("items:update_status", kwargs={"pk": cls.item.pk})

    def setUp(self):
        self.client.force_login(self.user)

    def test_post_updates_status(self):
        data = {"status": "DONE"}
        headers = {"HTTP_HX-Request": "true"}

        response = self.client.post(self.url, data, **headers)

        self.assertEqual(response.status_code, 200)

        self.item.refresh_from_db()
        self.assertEqual(self.item.status, "DONE")

    def test_get_method_not_allowed(self):
        """GET deve ser proibido (405)."""
        response = self.client.get(self.url)
        # Se sua view não tratar explicitamente, pode retornar 200 (vazio) ou 405
        # O ideal é que retorne 405. Se falhar, precisaremos ajustar a View.
        self.assertEqual(response.status_code, 405)

    def test_post_invalid_status_returns_400(self):
        """
        Enviar um status que não existe nos choices deve retornar erro 400.
        """
        data = {"status": "INVALID_STATUS_XYZ"}
        headers = {"HTTP_HX-Request": "true"}

        response = self.client.post(self.url, data, **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Status inválido")

        # Garante que o status no banco NÃO mudou
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, "PENDING")


class EditItemViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("planner", "p@t.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="G", bride_name="B",
            date=timezone.now().date() + timedelta(days=365),
            location="Loc", budget=1000
        )
        cls.item = Item.objects.create(
            wedding=cls.wedding, name="Item Original",
            quantity=1, unit_price=10.00
        )
        cls.url = reverse("items:edit_item", kwargs={"pk": cls.item.pk})

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_renders_prefilled_modal(self):
        """GET deve retornar o modal com os dados atuais."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/form_modal.html")
        self.assertEqual(response.context["form"].instance, self.item)
        self.assertEqual(response.context["modal_title"], "Editar Item")

    def test_post_updates_item_valid(self):
        """POST válido deve atualizar o item e retornar a lista."""
        data = {
            "name": "Item Editado",
            "category": "BUFFET",
            "quantity": 2,
            "unit_price": "20.00",
            "supplier": "Supplier Y",
            "description": "Desc Editada"
        }
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(self.url, data, **headers)

        self.assertEqual(response.status_code, 200)

        # Verifica Banco
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, "Item Editado")
        self.assertEqual(self.item.unit_price, 20.00)

        # Verifica Retorno (Lista atualizada)
        self.assertTemplateUsed(response, "items/partials/_list_and_pagination.html")

    def test_post_invalid_returns_form_errors(self):
        """POST inválido (preço negativo) deve retornar erro no modal."""
        data = {
            "name": "Item Editado",
            "category": "BUFFET",
            "quantity": 2,
            "unit_price": "-50.00",  # Inválido
        }
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(self.url, data, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/form_modal.html")
        self.assertTrue(response.context["form"].errors)

        # Banco não deve mudar
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, "Item Original")


class ItemDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("planner", "p@t.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="G", bride_name="B",
            date=timezone.now().date() + timedelta(days=365),
            location="Loc", budget=1000
        )
        cls.item = Item.objects.create(
            wedding=cls.wedding, name="Para Deletar",
            quantity=1, unit_price=10
        )
        cls.url = reverse("items:delete_item", kwargs={"pk": cls.item.pk})

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_renders_confirmation_modal(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/confirm_delete_modal.html")
        self.assertIn("Para Deletar", response.context["object_name"])

    def test_post_deletes_item(self):
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(self.url, **headers)

        self.assertEqual(response.status_code, 200)

        # Verifica se apagou
        self.assertFalse(Item.objects.filter(pk=self.item.pk).exists())

        # Verifica retorno da lista
        self.assertTemplateUsed(response, "items/partials/_list_and_pagination.html")


class ItemSecurityTest(TestCase):
    def test_cannot_add_item_to_other_user_wedding(self):
        """
        Tentar adicionar item num casamento que não é meu deve retornar 404.
        """
        # Usuário Hacker
        hacker = User.objects.create_user("hacker", "h@h.com", "123")

        # Casamento da Vítima
        victim_user = User.objects.create_user("victim", "v@v.com", "123")
        victim_wedding = Wedding.objects.create(
            planner=victim_user, groom_name="V", bride_name="V",
            date=timezone.now().date(), location="Loc", budget=1000
        )

        # Hacker loga
        self.client.force_login(hacker)

        # Tenta acessar a URL de adicionar item no casamento da vítima
        url = reverse("items:add_item", kwargs={"wedding_id": victim_wedding.id})
        response = self.client.get(url)

        # O get_object_or_404(Wedding, planner=request.user) deve falhar
        self.assertEqual(response.status_code, 404)


class ItemAccessControlTest(TestCase):
    def test_anonymous_user_redirected_to_login(self):
        """
        Usuário não logado deve ser redirecionado para o login
        ao tentar acessar qualquer view de itens.
        """
        # Tenta acessar a URL de adicionar item (que exige login)
        url = reverse("items:add_item", kwargs={"wedding_id": 1})

        response = self.client.get(url)

        # 302 Found -> Redirecionamento
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)
