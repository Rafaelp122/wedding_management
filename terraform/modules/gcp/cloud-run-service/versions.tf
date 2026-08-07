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
}
