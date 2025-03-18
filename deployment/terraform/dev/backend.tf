terraform {
  backend "gcs" {
    bucket = "qwiklabs-gcp-04-8896ad3a0df8-terraform-state"
    prefix = "dev"
  }
}
