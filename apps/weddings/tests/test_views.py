from datetime import date, timedelta

from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.users.models import User
from apps.weddings.models import Wedding


class WeddingListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="planner", email="p@test.com", password="123"
        )

        # Cria 10 casamentos para garantir paginação
        for i in range(10):
            Wedding.objects.create(
                planner=cls.user,
                groom_name=f"Groom {i}",
                bride_name=f"Bride {i}",
                date=date(2025, 1, 1),
                location="Loc",
                budget=1000,
            )

        cls.url = reverse("weddings:my_weddings")
        cls.factory = RequestFactory()

    def setUp(self):
        self.client.force_login(self.user)

    def test_view_loads_full_page_on_standard_request(self):
        """
        Acesso normal (F5) deve renderizar o template base 'list.html'.
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "weddings/list.html")

        # Verifica se o contexto de paginação está presente
        self.assertIn("page_obj", response.context)
        self.assertIn("paginated_weddings", response.context)
        self.assertEqual(
            len(response.context["paginated_weddings"]), 6
        )  # Paginate by 6

    def test_view_renders_partial_on_htmx_request(self):
        """
        Acesso via HTMX deve renderizar APENAS o partial '_list_and_pagination.html'.
        """
        # Simulamos headers HTMX
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.get(self.url, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "weddings/partials/_list_and_pagination.html")
        self.assertTemplateNotUsed(
            response, "weddings/list.html"
        )  # Não deve renderizar o wrapper

    def test_pagination_preserves_state(self):
        """
        Testa se ir para a página 2 via HTMX funciona e traz os dados corretos.
        """
        headers = {"HTTP_HX-Request": "true"}
        # Simulamos o header HX-Current-Url com parâmetros
        headers["HTTP_HX-Current-Url"] = f"{self.url}?page=2"

        # O GET deve ser limpo, o mixin pega os params do header ou do GET
        # Na sua implementação atual (WeddingListView), ele pega do GET (request_params = self.request.GET.copy())
        # Então passamos no GET também
        response = self.client.get(f"{self.url}?page=2", **headers)

        self.assertEqual(response.status_code, 200)
        # Página 2 deve ter 4 itens (10 total - 6 na pág 1)
        self.assertEqual(len(response.context["paginated_weddings"]), 4)

    def test_view_integrates_search_param(self):
        """
        Testa se passar ?q=... na URL realmente filtra a lista visualizada.
        """
        # Cria um casamento com nome único
        Wedding.objects.create(
            planner=self.user,
            groom_name="UniqueNameXYZ", bride_name="Bride",
            date=date(2025, 12, 25), location="Loc", budget=1000
        )

        # Teste Integrado: Busca + HTMX (Simula digitação do usuário)
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.get(f"{self.url}?q=UniqueNameXYZ", **headers)

        weddings_context = response.context["paginated_weddings"]
        self.assertEqual(len(weddings_context), 1)

        # Melhoria: Validação desacoplada da estrutura do dicionário
        # Verifica se o nome está presente na lista de resultados
        found_names = [w["wedding"].groom_name for w in weddings_context]
        self.assertIn("UniqueNameXYZ", found_names)

    def test_view_integrates_sort_param(self):
        """
        Testa se o parâmetro ?sort=date_desc chega até o contexto.
        """
        # Cria um casamento no futuro distante
        future_w = Wedding.objects.create(
            planner=self.user,
            groom_name="Future", bride_name="F",
            date=date(2099, 1, 1), location="L", budget=1000
        )

        response = self.client.get(f"{self.url}?sort=date_desc")

        # O primeiro da lista deve ser o do futuro (2099)
        first_item = response.context["paginated_weddings"][0]["wedding"]
        self.assertEqual(first_item, future_w)


class WeddingDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="planner", email="p@test.com", password="123"
        )
        cls.other = User.objects.create_user(
            username="other", email="o@test.com", password="123"
        )

        cls.wedding = Wedding.objects.create(
            planner=cls.user,
            groom_name="Romeo",
            bride_name="Juliet",
            date=date(2025, 1, 1),
            location="Verona",
            budget=50000,
        )

        cls.url = reverse(
            "weddings:wedding_detail", kwargs={"wedding_id": cls.wedding.pk}
        )

    def test_owner_can_view_detail(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "weddings/detail.html")
        self.assertEqual(response.context["wedding"], self.wedding)

    def test_other_user_cannot_view_detail(self):
        """
        Testa se o PlannerOwnershipMixin está protegendo a View.
        """
        self.client.force_login(self.other)
        response = self.client.get(self.url)

        # O comportamento padrão do get_queryset filtrado é retornar 404
        # quando o objeto não é encontrado no filtro do usuário.
        self.assertEqual(response.status_code, 404)


class WeddingCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="planner", email="p@test.com", password="123")
        cls.url = reverse("weddings:create_wedding")

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_renders_form_modal(self):
        """GET deve retornar o formulário no template parcial."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/form_modal.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["modal_title"], "Novo Casamento")

    def test_post_creates_wedding_and_returns_list(self):
        """POST válido deve criar o objeto e retornar a lista atualizada (HTMX)."""
        data = {
            "groom_name": "New Groom",
            "bride_name": "New Bride",
            "date": "2025-12-25",
            "budget": "10000.00",
            "location": "Test Loc"
        }

        # Simula request HTMX
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(self.url, data, **headers)

        self.assertEqual(response.status_code, 200)

        # Verifica se criou no banco
        self.assertTrue(Wedding.objects.filter(groom_name="New Groom").exists())
        created_wedding = Wedding.objects.get(groom_name="New Groom")
        self.assertEqual(created_wedding.planner, self.user) # Planner atribuído automaticamente

        # Verifica se retornou a lista atualizada (Partial)
        self.assertTemplateUsed(response, "weddings/partials/_list_and_pagination.html")

        # Verifica Headers HTMX de resposta
        self.assertEqual(response["HX-Retarget"], "#wedding-list-container")
        self.assertEqual(response["HX-Trigger-After-Swap"], "listUpdated")

    def test_post_invalid_shows_form_errors(self):
        """POST inválido deve retornar o formulário com erros (não a lista)."""
        data = {}  # Vazio
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/form_modal.html")
        self.assertTrue(response.context["form"].errors)

    def test_post_invalid_via_htmx_returns_form_partial(self):
        """
        Se enviar dados inválidos via HTMX, deve retornar o HTML do form (modal)
        com os erros renderizados, e não a lista ou página completa.
        """
        data = {}  # Vazio = Inválido
        headers = {"HTTP_HX-Request": "true"}

        response = self.client.post(self.url, data, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/form_modal.html")

        # Confirma que tem erro no contexto
        self.assertTrue(response.context["form"].errors)


class WeddingUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="planner", email="p@test.com", password="123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="Old", bride_name="Old",
            date=date(2025, 1, 1), location="Loc", budget=1000
        )
        cls.url = reverse("weddings:edit_wedding", kwargs={"id": cls.wedding.pk})

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_renders_prefilled_form(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].instance, self.wedding)
        self.assertEqual(response.context["modal_title"], "Editar Casamento")

    def test_post_updates_wedding(self):
        future_date = timezone.now().date() + timedelta(days=365)

        data = {
            "groom_name": "Updated Groom",
            "bride_name": "Updated Bride",
            "date": future_date,
            "budget": "2000.00",
            "location": "Loc"
        }
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(self.url, data, **headers)

        self.assertEqual(response.status_code, 200)

        self.wedding.refresh_from_db()
        self.assertEqual(self.wedding.groom_name, "Updated Groom")
        self.assertEqual(self.wedding.budget, 2000.00)

        # Deve retornar a lista
        self.assertTemplateUsed(response, "weddings/partials/_list_and_pagination.html")

    def test_post_update_invalid_shows_form_errors(self):
        """
        Se enviar dados inválidos (ex: orçamento negativo) na edição,
        deve renderizar o formulário com erros e NÃO salvar.
        """
        data = {
            "groom_name": "Updated Groom",
            "bride_name": "Updated Bride",
            "date": "2025-12-25",
            "budget": "-100.00",  # Inválido!
            "location": "Loc"
        }
        # Simulamos HTMX pois a view retorna partials
        headers = {"HTTP_HX-Request": "true"} 
        response = self.client.post(self.url, data, **headers)

        self.assertEqual(response.status_code, 200)

        # Deve renderizar o form de novo, não a lista
        self.assertTemplateUsed(response, "partials/form_modal.html")
        self.assertTrue(response.context["form"].errors)
        self.assertIn("budget", response.context["form"].errors)

        # Garante que o banco NÃO mudou
        self.wedding.refresh_from_db()
        self.assertNotEqual(self.wedding.groom_name, "Updated Groom")


class WeddingDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="planner", email="p@test.com", password="123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="Del", bride_name="Del",
            date=date(2025, 1, 1), location="Loc", budget=1000
        )
        cls.url = reverse("weddings:delete_wedding", kwargs={"id": cls.wedding.pk})

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_renders_confirmation_modal(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/confirm_delete_modal.html")

    def test_post_deletes_wedding(self):
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(self.url, **headers)

        self.assertEqual(response.status_code, 200)

        # Verifica se apagou
        self.assertFalse(Wedding.objects.filter(pk=self.wedding.pk).exists())

        # Verifica retorno da lista
        self.assertTemplateUsed(response, "weddings/partials/_list_and_pagination.html")

    def test_post_delete_other_user_wedding_returns_404(self):
        """
        Um usuário não pode deletar o casamento de outro.
        O get_queryset do PlannerOwnershipMixin deve filtrar e gerar 404.
        """
        # Cria um usuário hacker e loga com ele
        hacker = User.objects.create_user(username="hacker", email="h@test.com", password="123")
        self.client.force_login(hacker)

        # Tenta deletar o casamento do 'planner' (criado no setUpTestData)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 404)

        # Garante que o casamento AINDA EXISTE
        self.assertTrue(Wedding.objects.filter(pk=self.wedding.pk).exists())


class UpdateWeddingStatusViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="planner", email="p@test.com", password="123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="Status", bride_name="Check",
            date=date(2025, 1, 1), location="Loc", budget=1000,
            status="IN_PROGRESS"
        )
        cls.url = reverse("weddings:update_wedding_status", kwargs={"id": cls.wedding.pk})

    def setUp(self):
        self.client.force_login(self.user)

    def test_post_updates_status_valid(self):
        """Deve atualizar status e retornar a lista."""
        data = {"status": "COMPLETED"}
        headers = {"HTTP_HX-Request": "true"}

        response = self.client.post(self.url, data, **headers)

        self.assertEqual(response.status_code, 200)

        self.wedding.refresh_from_db()
        self.assertEqual(self.wedding.status, "COMPLETED")

        self.assertTemplateUsed(response, "weddings/partials/_list_and_pagination.html")
        self.assertEqual(response["HX-Trigger-After-Swap"], "listUpdated")

    def test_post_invalid_status_returns_400(self):
        """Status inválido deve retornar Bad Request."""
        data = {"status": "INVALID_STATUS_XYZ"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Status inválido ou Model não atualizado.")

        # Status não deve mudar
        self.wedding.refresh_from_db()
        self.assertEqual(self.wedding.status, "IN_PROGRESS")

    def test_post_other_user_cannot_change_status(self):
        """Outro usuário não pode alterar status."""
        other_user = User.objects.create_user(username="hacker", email="h@test.com", password="123")
        self.client.force_login(other_user)

        data = {"status": "COMPLETED"}
        response = self.client.post(self.url, data)

        # View retorna 403 para acesso não autorizado (ownership check)
        self.assertEqual(response.status_code, 403)
        self.assertIn("Sem permissão", response.content.decode())

    def test_get_method_not_allowed(self):
        """
        Acessar essa view via GET deve retornar erro 405 (Method Not Allowed).
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class WeddingAccessControlTest(TestCase):
    """
    Testes de 'Sanidade' para garantir que regras globais (Login, 404)
    estão aplicadas às Views principais.
    """

    def setUp(self):
        # Usuário Logado
        self.user = User.objects.create_user(username="user", email="u@test.com", password="123")
        # URL de uma view protegida (ex: Lista)
        self.list_url = reverse("weddings:my_weddings")
        # URL de edição de algo que não existe
        self.update_404_url = reverse("weddings:edit_wedding", kwargs={"id": 99999})

    def test_unauthenticated_user_redirects_to_login(self):
        """
        Garante que quem não está logado é chutado para o login.
        Isso confirma que o LoginRequiredMixin está ativo na View.
        """
        response = self.client.get(self.list_url)

        # 302 = Found (Redirecionamento)
        self.assertEqual(response.status_code, 302)
        # Verifica se vai para /accounts/login/?next=...
        self.assertIn("/login", response.url)

    def test_access_non_existent_wedding_returns_404(self):
        """
        Garante que tentar editar/ver um ID que não existe retorna 404
        (e não Crash 500).
        """
        self.client.force_login(self.user)

        response = self.client.get(self.update_404_url)

        self.assertEqual(response.status_code, 404)
