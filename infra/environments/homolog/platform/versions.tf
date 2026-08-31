terraform {
  required_version = ">= 1.12.0, < 2.0.0"
  backend "oci" {
    bucket    = "configured-at-init"
    namespace = "configured-at-init"
    key       = "togglemaster/phase3/homolog/platform.tfstate"
  }
}
