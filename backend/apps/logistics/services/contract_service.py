from django.core.exceptions import ValidationError
from django.db import transaction

from apps.logistics.models import Contract, Supplier
from apps.weddings.models import Wedding


class ContractService:
    """
    Camada de serviço para gestão de contratos.
    Garante a integridade entre fornecedores, casamentos e arquivos (ADR-010).
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Contract:
        """
        Cria um contrato garantindo que o fornecedor e o casamento pertencem ao mesmo
        Planner.
        """
        # 1. Recuperamos as instâncias usando o filtro de segurança for_user
        wedding_uuid = data.pop("wedding", None)
        supplier_uuid = data.pop("supplier", None)

        try:
            wedding = Wedding.objects.all().for_user(user).get(uuid=wedding_uuid)
            supplier = Supplier.objects.all().for_user(user).get(uuid=supplier_uuid)
        except (Wedding.DoesNotExist, Supplier.DoesNotExist):
            raise ValidationError(
                "Casamento ou Fornecedor não encontrado ou acesso negado."
            ) from (Wedding.DoesNotExist, Supplier.DoesNotExist)

        # 2. Injetamos o contexto de posse
        data["planner"] = user
        data["wedding"] = wedding
        data["supplier"] = supplier

        # 3. Criação direta
        return Contract.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update(instance: Contract, user, data: dict) -> Contract:
        """
        Atualiza o contrato protegendo vínculos de propriedade e campos imutáveis.
        """
        # Impedimos a troca de Casamento ou Planner via update
        data.pop("wedding", None)
        data.pop("planner", None)

        # Se houver tentativa de trocar o fornecedor, validamos a posse do novo
        if "supplier" in data:
            supplier_uuid = data.pop("supplier")
            try:
                instance.supplier = (
                    Supplier.objects.all().for_user(user).get(uuid=supplier_uuid)
                )
            except Supplier.DoesNotExist:
                raise ValidationError({
                    "supplier": "Fornecedor inválido ou acesso negado."
                }) from Supplier.DoesNotExist

        # Atualização dinâmica de campos (total_amount, dates, description, etc)
        for field, value in data.items():
            # Preserva o arquivo se o campo estiver vazio no patch
            if field == "pdf_file" and value is None:
                continue
            setattr(instance, field, value)

        # Validação de Datas (Regra de Negócio):
        # Exemplo: Expiração não pode ser anterior à assinatura.
        if instance.expiration_date and instance.signed_date:
            if instance.expiration_date < instance.signed_date:
                raise ValidationError(
                    "A data de expiração não pode ser anterior à assinatura."
                )

        instance.full_clean()  # Dispara validações de mixins (Cross-Wedding)
        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Contract) -> None:
        """
        Executa a deleção real do contrato.
        Limpa as referências nos itens vinculados para evitar dados órfãos.
        """
        # Se você quer manter os itens de logística mas desvinculá-los do contrato:
        instance.item_records.update(contract=None)

        # Deleção definitiva (Hard Delete)
        instance.delete()
