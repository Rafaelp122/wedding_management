import base64
import hashlib
import uuid
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.core.models import BaseModel
from apps.items.models import Item


class Contract(BaseModel):
    """
    Modelo de Contrato Tripartite.
    """
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="contract")
    description = models.TextField(blank=True, help_text="Cláusulas específicas ou descrição do serviço.")

    STATUS_CHOICES = (
        ("DRAFT", "Rascunho"),
        ("WAITING_PLANNER", "Aguardando Cerimonialista"),
        ("WAITING_SUPPLIER", "Aguardando Fornecedor"),
        ("WAITING_COUPLE", "Aguardando Noivos"),
        ("COMPLETED", "Concluído"),
        ("CANCELED", "Cancelado"),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="WAITING_PLANNER")

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Assinaturas - Cerimonialista
    planner_signature = models.FileField(upload_to="signatures/planner/", null=True, blank=True)
    planner_signed_at = models.DateTimeField(null=True, blank=True)
    planner_ip = models.GenericIPAddressField(null=True, blank=True)

    # Assinaturas - Fornecedor
    supplier_signature = models.FileField(upload_to="signatures/supplier/", null=True, blank=True)
    supplier_signed_at = models.DateTimeField(null=True, blank=True)
    supplier_ip = models.GenericIPAddressField(null=True, blank=True)

    # Assinaturas - Noivos
    couple_signature = models.FileField(upload_to="signatures/couple/", null=True, blank=True)
    couple_signed_at = models.DateTimeField(null=True, blank=True)
    couple_ip = models.GenericIPAddressField(null=True, blank=True)

    # Auditoria e Arquivos Finais
    integrity_hash = models.CharField(max_length=64, blank=True, null=True)
    final_pdf = models.FileField(upload_to="contracts_pdf/", null=True, blank=True)
    external_pdf = models.FileField(upload_to="contracts_external/", null=True, blank=True)

    def __str__(self):
        return f"Contrato {self.status} - {self.item.name}"

    @property
    def supplier(self):
        # Retorna o nome do fornecedor (string) do item
        return self.item.supplier

    @property
    def wedding(self):
        return self.item.wedding

    @property
    def contract_value(self):
        """
        Retorna o custo total do item usando a propriedade do modelo Item.
        """
        if not self.item:
            return 0
        # Usa a propriedade total_cost definida no Item (unit_price * quantity)
        return self.item.total_cost

    def get_absolute_url(self):
        return reverse("contracts:sign_contract", kwargs={"token": self.token})

    def save(self, *args, **kwargs):
        if not self.status:
            self.status = "WAITING_PLANNER"
        super().save(*args, **kwargs)

    def process_signature(self, signature_b64: str, client_ip: str) -> bool:
        """
        Processa e salva uma assinatura digital.
        """
        if not signature_b64 or ';base64,' not in signature_b64:
            raise ValueError("Assinatura inválida ou vazia")

        # Validações de segurança
        MAX_SIGNATURE_SIZE = 500 * 1024  # 500KB
        ALLOWED_FORMATS = ['png', 'jpg', 'jpeg']

        try:
            format_part, imgstr = signature_b64.split(';base64,')
            ext = format_part.split('/')[-1].lower()

            if ext not in ALLOWED_FORMATS:
                raise ValueError(f"Formato {ext} não permitido.")

            decoded_data = base64.b64decode(imgstr)
            if len(decoded_data) > MAX_SIGNATURE_SIZE:
                raise ValueError("Assinatura muito grande. Máximo: 500KB")

            signature_file = ContentFile(
                decoded_data,
                name=f'sig_{self.status}_{self.token}.{ext}'
            )

        except (ValueError, TypeError) as e:
            raise ValueError(f"Erro ao decodificar assinatura: {str(e)}")

        # Processa conforme o status atual
        if self.status == "WAITING_PLANNER":
            self.planner_signature = signature_file
            self.planner_signed_at = timezone.now()
            self.planner_ip = client_ip
            self.status = "WAITING_SUPPLIER"

        elif self.status == "WAITING_SUPPLIER":
            self.supplier_signature = signature_file
            self.supplier_signed_at = timezone.now()
            self.supplier_ip = client_ip
            self.status = "WAITING_COUPLE"

        elif self.status == "WAITING_COUPLE":
            self.couple_signature = signature_file
            self.couple_signed_at = timezone.now()
            self.couple_ip = client_ip
            self.status = "COMPLETED"
            self._generate_integrity_hash()

        else:
            raise RuntimeError(f"Não é possível assinar contrato com status: {self.status}")

        self.save()
        return True

    def _generate_integrity_hash(self) -> None:
        """
        Gera hash de integridade para o contrato completado.
        """
        # Garante que as datas não sejam None antes de formatar
        planner_dt = self.planner_signed_at.isoformat() if self.planner_signed_at else ""
        supplier_dt = self.supplier_signed_at.isoformat() if self.supplier_signed_at else ""
        couple_dt = self.couple_signed_at.isoformat() if self.couple_signed_at else ""

        hash_components = [
            str(self.id),
            planner_dt,
            str(self.planner_ip or ""),
            supplier_dt,
            str(self.supplier_ip or ""),
            couple_dt,
            str(self.couple_ip or ""),
            str(self.token),
        ]
        hash_input = '|'.join(hash_components)
        self.integrity_hash = hashlib.sha256(
            hash_input.encode('utf-8')
        ).hexdigest()

    def get_next_signer_info(self) -> dict:
        """
        Retorna informações sobre o próximo assinante.
        """
        if self.status == "WAITING_PLANNER":
            return {'role': 'Cerimonialista', 'name': 'Você (Cerimonialista)'}

        elif self.status == "WAITING_SUPPLIER":
            supplier_name = self.supplier or "Não vinculado"
            return {'role': 'Fornecedor', 'name': f"Fornecedor ({supplier_name})"}

        elif self.status == "WAITING_COUPLE":
            if self.wedding:
                bride = self.wedding.bride_name
                groom = self.wedding.groom_name
                return {'role': 'Noivos', 'name': f"Noivos ({bride} e {groom})"}
            return {'role': 'Noivos', 'name': 'Noivos'}

        return {'role': 'Desconhecido', 'name': 'Alguém'}

    def is_fully_signed(self) -> bool:
        """
        Verifica se o contrato foi assinado por todas as partes.
        """
        return (
            self.status == "COMPLETED" and
            bool(self.planner_signature) and
            bool(self.supplier_signature) and
            bool(self.couple_signature)
        )

    def get_signatures_status(self) -> dict:
        """
        Retorna o status de cada assinatura.
        """
        return {
            'planner': {
                'signed': bool(self.planner_signature),
                'signed_at': self.planner_signed_at,
                'ip': self.planner_ip
            },
            'supplier': {
                'signed': bool(self.supplier_signature),
                'signed_at': self.supplier_signed_at,
                'ip': self.supplier_ip
            },
            'couple': {
                'signed': bool(self.couple_signature),
                'signed_at': self.couple_signed_at,
                'ip': self.couple_ip
            }
        }