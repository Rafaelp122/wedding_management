# terraform/cloudflare_r2.tf
# Configuração do Armazenamento de Objetos S3-Compatible no Cloudflare R2
# Utilizado para o upload seguro de contratos e mídias via Presigned URLs (ADR-004 / contract-pdf-upload-r2-flow.md).

# Bucket R2 para Contratos e Anexos em PDF
resource "cloudflare_r2_bucket" "contracts_bucket" {
  account_id = var.cloudflare_account_id
  name       = var.environment == "production" ? "wedding-contracts-r2" : "wedding-contracts-r2-${var.environment}"
}

# Exemplo de Bloco de Importação (para adotar bucket R2 existente no Cloudflare)
# import {
#   to = cloudflare_r2_bucket.contracts_bucket
#   id = "${var.cloudflare_account_id}/wedding-contracts-r2"
# }
