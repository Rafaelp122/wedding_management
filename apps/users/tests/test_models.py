from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from apps.users.models import User


class UserModelTest(TestCase):
    def test_create_user_with_valid_data(self):
        """
        Deve criar um usuário com email, username e senha criptografada.
        """
        email = "normal@user.com"
        username = "normaluser"
        password = "secret_password"

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_with_valid_data(self):
        """
        Deve criar um superusuário com is_staff e is_superuser True.
        """
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="123"
        )

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)

    def test_create_user_raises_error_without_email(self):
        """
        Deve lançar ValueError se não passar email.
        """
        with self.assertRaisesMessage(ValueError, "O campo de E-mail é obrigatório"):
            User.objects.create_user(username="teste", email="", password="123")

    def test_create_user_raises_error_without_username(self):
        """
        Deve lançar ValueError se não passar username.
        """
        with self.assertRaisesMessage(ValueError, "O campo de Username é obrigatório"):
            # Passamos None ou string vazia
            User.objects.create_user(username="", email="test@test.com", password="123")

    def test_create_superuser_validates_permissions(self):
        """
        Deve impedir criação de superuser se is_staff ou is_superuser forem False.
        """
        # Tenta criar superuser sem ser staff
        with self.assertRaisesMessage(ValueError, "Superuser must have is_staff=True."):
            User.objects.create_superuser(
                username="admin1", email="a1@test.com", password="123", is_staff=False
            )

        # Tenta criar superuser sem ser superuser (parece redundante, mas valida a lógica)
        with self.assertRaisesMessage(ValueError, "Superuser must have is_superuser=True."):
            User.objects.create_superuser(
                username="admin2", email="a2@test.com", password="123", is_superuser=False
            )

    def test_email_normalization(self):
        """
        O Manager deve normalizar o email (domínio em minúsculo).
        """
        email = "TESTE@EXAMPLE.COM"
        user = User.objects.create_user(username="test", email=email, password="123")

        # A parte antes do @ pode ser case-sensitive, mas o domínio o Django normaliza.
        self.assertEqual(user.email, "TESTE@example.com")

    def test_string_representation(self):
        """
        O __str__ do modelo deve retornar o email.
        """
        user = User.objects.create_user(username="strtest", email="str@test.com", password="123")
        self.assertEqual(str(user), "str@test.com")


class UserModelIntegrationTest(TestCase):
    """
    Testes de Integração com o Banco de Dados.
    Verifica Constraints (Unique, MaxLength) que o Manager não pega sozinho.
    """

    def test_email_must_be_unique(self):
        """
        CAMINHO TRISTE: Tentar criar dois usuários com o mesmo e-mail deve falhar no DB.
        """
        email = "duplicate@test.com"
        User.objects.create_user(username="user1", email=email, password="123")

        # Tenta criar o segundo com o mesmo email
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="user2", email=email, password="123")

    def test_username_must_be_unique(self):
        """
        CAMINHO TRISTE: Tentar criar dois usuários com o mesmo username deve falhar no DB.
        """
        username = "unique_dude"
        User.objects.create_user(username=username, email="u1@test.com", password="123")

        with self.assertRaises(IntegrityError):
            User.objects.create_user(username=username, email="u2@test.com", password="123")

    def test_username_max_length_validation(self):
        """
        CAMINHO TRISTE: Username com mais de 255 caracteres deve falhar na validação.
        """
        long_username = "a" * 256  # 256 caracteres
        user = User(username=long_username, email="long@test.com")

        # O full_clean() roda as validações do model (validators=[MaxLengthValidator])
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_direct_instantiation_validation(self):
        """
        CAMINHO TRISTE: Se alguém criar User() direto sem passar pelo Manager,
        o full_clean() deve pegar os campos obrigatórios vazios.
        """
        # Cria um usuário vazio, ignorando o create_user do Manager
        user = User()

        # Ao validar, o Django deve gritar que email e username são obrigatórios
        with self.assertRaises(ValidationError) as cm:
            user.full_clean()

        errors = cm.exception.message_dict
        self.assertIn("email", errors)
        self.assertIn("username", errors)
        self.assertIn("password", errors)  # AbstractUser exige senha também
