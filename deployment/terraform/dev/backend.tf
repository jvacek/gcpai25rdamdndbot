terraform {
  backend "gcs" {
    bucket = "qwiklabs-gcp-00-f40a98878280-terraform-state"
    prefix = "gcpai25rdamdndbot/dev"
  }
}
