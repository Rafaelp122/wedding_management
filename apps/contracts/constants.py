"""
Constantes utilizadas no app contracts.
Centraliza valores usados em múltiplos lugares para facilitar
manutenção.
"""

# Status de Contratos
STATUS_DRAFT = "DRAFT"
STATUS_WAITING_PLANNER = "WAITING_PLANNER"
STATUS_WAITING_SUPPLIER = "WAITING_SUPPLIER"
STATUS_WAITING_COUPLE = "WAITING_COUPLE"
STATUS_COMPLETED = "COMPLETED"
STATUS_CANCELED = "CANCELED"

# Grupos de Status
EDITABLE_STATUSES = [STATUS_DRAFT, STATUS_WAITING_PLANNER]
PENDING_SIGNATURE_STATUSES = [
    STATUS_WAITING_PLANNER,
    STATUS_WAITING_SUPPLIER,
    STATUS_WAITING_COUPLE
]

# Configurações de Assinatura
MAX_SIGNATURE_SIZE = 500 * 1024  # 500KB
ALLOWED_SIGNATURE_FORMATS = ['png', 'jpg', 'jpeg']

# Mensagens de Hash para Contratos Externos
EXTERNAL_CONTRACT_HASH = "UPLOAD_MANUAL_EXTERNO"

# Formatos de Imagem
IMAGE_FORMAT_PNG = "PNG"

# Roles de Signatários
ROLE_PLANNER = "Cerimonialista"
ROLE_SUPPLIER = "Fornecedor"
ROLE_COUPLE = "Noivos"
ROLE_UNKNOWN = "Desconhecido"

# Nomes de Display para Signatários
SIGNER_NAME_PLANNER = "Você (Cerimonialista)"
SIGNER_NAME_SUPPLIER_TEMPLATE = "Fornecedor ({supplier})"
SIGNER_NAME_COUPLE_TEMPLATE = "Noivos ({bride} e {groom})"
SIGNER_NAME_COUPLE_DEFAULT = "Noivos"
SIGNER_NAME_UNKNOWN = "Alguém"
SIGNER_NAME_NOT_FOUND = "Contrato não encontrado"
SIGNER_NAME_SUPPLIER_UNLINKED = "Não vinculado"
