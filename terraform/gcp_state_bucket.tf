# terraform/gcp_state_bucket.tf
# Definição do Bucket GCS para Armazenamento do Estado do Terraform (tfstate)
# Inclui Versionamento (para recuperação em caso de sobrescrita acidental) e Bloqueio de Acesso Público.
#
# NOTA DE BOOTSTRAP (Ovo e Galinha):
# O backend remoto "gcs" no main.tf exige que o bucket já exista ANTES de rodar terraform init.
# Para inicializar o projeto do zero:
# 1. Crie o bucket via gcloud CLI: gcloud storage buckets create gs://<PROJECT_ID>-tfstate --location=us-central1
# 2. Ou execute terraform init com backend local primeiro, rode terraform apply para criar este bucket, e depois descomente o backend gcs.

resource "google_storage_bucket" "tfstate" {
  name                     = "${var.gcp_project_id}-tfstate"
  location                 = var.gcp_region
  force_destroy            = false
  public_access_prevention = "enforced"

  versioning {
    enabled = true
  }
}

# Exemplo de Bloco de Importação (se o bucket de estado foi criado via gcloud CLI ou no GCP Console)
# import {
#   to = google_storage_bucket.tfstate
#   id = "${var.gcp_project_id}-tfstate"
# }
