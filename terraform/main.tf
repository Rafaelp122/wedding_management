# terraform/main.tf
# Configurações globais de provedores e backend de estado remoto (GCS)
# para a infraestrutura do Wedding Management System.

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
    vercel = {
      source  = "vercel/vercel"
      version = "~> 1.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }

  # Estado remoto centralizado no Google Cloud Storage (GCS)
  # O bucket gcs-wedding-management-tfstate é criado para armazenar o estado criptografado.
  backend "gcs" {
    bucket = "gen-lang-client-0194045282-tfstate"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

provider "vercel" {
  api_token = var.vercel_api_token
  team      = var.vercel_team_id
}

provider "github" {
  owner = var.github_owner
  token = var.github_token
}
