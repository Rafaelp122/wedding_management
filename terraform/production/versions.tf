terraform {
  required_version = "= 1.7.5"

  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "= 4.52.8"
    }
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
    prefix = "terraform/production"
  }
}

provider "google" {
  project = local.gcp_project_id
  region  = local.gcp_region
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

provider "vercel" {
  api_token = var.vercel_api_token
  team      = var.vercel_team_id
}

data "terraform_remote_state" "shared" {
  backend = "gcs"
  config = {
    bucket = "gen-lang-client-0194045282-tfstate"
    prefix = "terraform/shared"
  }
}
