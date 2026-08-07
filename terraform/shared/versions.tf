terraform {
  required_version = "= 1.7.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "= 5.45.2"
    }
    vercel = {
      source  = "vercel/vercel"
      version = "= 1.14.1"
    }
  }

  backend "gcs" {
    bucket = "gen-lang-client-0194045282-tfstate"
    prefix = "terraform/shared"
  }
}

provider "google" {
  project = local.gcp_project_id
  region  = local.gcp_region
}

provider "vercel" {
  api_token = var.vercel_api_token
  team      = var.vercel_team_id
}
