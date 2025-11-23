from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from apps.items.models import Item
from apps.items.web.forms import ItemForm


class ItemFormTest(SimpleTestCase):
    def test_form_valid_data(self):
        """
        Formulário deve ser válido com dados corretos.
        """
        data = {
            "name": "Cadeira",
            "category": "DECOR",
            "quantity": 10,
            "unit_price": "50.00",
            "supplier": "Loja A",
            "description": "Cadeiras brancas"
        }
        form = ItemForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_quantity_zero(self):
        """
        Quantidade zero deve ser inválida.
        """
        data = {
            "name": "Item",
            "category": "OTHERS",
            "quantity": 0,  # Inválido
            "unit_price": "10.00",
        }
        form = ItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)
        self.assertEqual(form.errors["quantity"][0], "A quantidade deve ser pelo menos 1.")

    def test_form_invalid_quantity_negative(self):
        """
        Quantidade negativa deve ser inválida.
        """
        data = {
            "name": "Item",
            "category": "OTHERS",
            "quantity": -5,  # Inválido
            "unit_price": "10.00",
        }
        form = ItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)

    def test_form_invalid_price_negative(self):
        """
        Preço negativo deve ser inválido.
        """
        data = {
            "name": "Item",
            "category": "OTHERS",
            "quantity": 1,
            "unit_price": "-10.00",  # Inválido
        }
        form = ItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("unit_price", form.errors)

    def test_widgets_attributes(self):
        """
        Verifica se os atributos de UX (min, rows) foram aplicados.
        """
        form = ItemForm()

        # Quantidade deve ter min="1"
        self.assertEqual(str(form.fields["quantity"].widget.attrs["min"]), "1")

        # Preço deve ter min="0" e step="0.01"
        self.assertEqual(str(form.fields["unit_price"].widget.attrs["min"]), "0")
        self.assertEqual(str(form.fields["unit_price"].widget.attrs["step"]), "0.01")

        # Descrição deve ter rows=3
        self.assertEqual(form.fields["description"].widget.attrs["rows"], 3)

        # Placeholder checado via utilitário (só pra garantir que o init rodou)
        self.assertEqual(form.fields["name"].widget.attrs["placeholder"], "Ex: Buffet Completo")

    @patch("apps.items.web.forms.logger")
    def test_logging_on_validation_error(self, mock_logger):
        """
        Deve logar warning quando a validação customizada falhar.
        """
        data = {
            "name": "Item",
            "category": "OTHERS",
            "quantity": 0,  # Erro
            "unit_price": "-5.00"  # Erro
        }
        form = ItemForm(data=data)
        form.is_valid()  # Dispara validação

        # Deve ter chamado o logger pelo menos uma vez (para qtd ou preço)
        self.assertTrue(mock_logger.warning.called)

        # Opcional: Verificar se chamou 2 vezes (uma pra cada erro)
        self.assertEqual(mock_logger.warning.call_count, 2)

    class ItemFormIntegrationTest(TestCase):
        def test_form_save_creates_item_in_db(self):
            """
            Teste de Integração: O form.save() deve criar um registro no banco.
            """
            data = {
                "name": "Item Teste Integração",
                "category": "BUFFET",
                "quantity": 5,
                "unit_price": "100.00",
                "supplier": "Teste Supplier",
                "description": "Descrição teste"
            }
            form = ItemForm(data=data)

            self.assertTrue(form.is_valid())

            # Salva
            item = form.save()

            # Verifica se persistiu
            self.assertIsNotNone(item.pk)
            self.assertTrue(Item.objects.filter(name="Item Teste Integração").exists())
            self.assertEqual(item.total_cost, 500.00) # 5 * 100
