resource "oci_kms_vault" "application" {
  compartment_id = var.compartment_id
  display_name   = "${var.project_name}-vault"
  vault_type     = "DEFAULT"
  freeform_tags  = local.common_tags
}

resource "oci_kms_key" "application" {
  compartment_id      = var.compartment_id
  display_name        = "${var.project_name}-application-key"
  management_endpoint = oci_kms_vault.application.management_endpoint
  protection_mode     = "SOFTWARE"
  freeform_tags       = local.common_tags

  key_shape {
    algorithm = "AES"
    length    = 32
  }
}

resource "oci_vault_secret" "postgres_admin_password" {
  for_each = local.database_names

  compartment_id         = var.compartment_id
  vault_id               = oci_kms_vault.application.id
  key_id                 = oci_kms_key.application.id
  secret_name            = "${var.project_name}-${each.key}-postgres-admin-password"
  description            = "Generated administrator password for the ${each.key} PostgreSQL system."
  enable_auto_generation = true
  freeform_tags          = merge(local.common_tags, { Purpose = "PostgreSQLAdmin" })

  secret_generation_context {
    generation_type     = "PASSPHRASE"
    generation_template = "DBAAS_DEFAULT_PASSWORD"
    passphrase_length   = 30
  }
}

resource "oci_vault_secret" "postgres_app_password" {
  for_each = local.database_names

  compartment_id         = var.compartment_id
  vault_id               = oci_kms_vault.application.id
  key_id                 = oci_kms_key.application.id
  secret_name            = "${var.project_name}-${each.key}-app-password"
  description            = "Generated least-privilege application password for ${each.key}."
  enable_auto_generation = true
  freeform_tags          = merge(local.common_tags, { Purpose = "ApplicationDatabase" })

  secret_generation_context {
    generation_type     = "PASSPHRASE"
    generation_template = "SECRETS_DEFAULT_PASSWORD"
    passphrase_length   = 32
  }
}

resource "oci_vault_secret" "auth_master_key" {
  compartment_id         = var.compartment_id
  vault_id               = oci_kms_vault.application.id
  key_id                 = oci_kms_key.application.id
  secret_name            = "${var.project_name}-auth-master-key"
  description            = "Generated master key used by the authentication administration endpoint."
  enable_auto_generation = true
  freeform_tags          = merge(local.common_tags, { Purpose = "ApplicationKey" })

  secret_generation_context {
    generation_type     = "PASSPHRASE"
    generation_template = "SECRETS_DEFAULT_PASSWORD"
    passphrase_length   = 32
  }
}

resource "oci_vault_secret" "internal_api_key" {
  compartment_id         = var.compartment_id
  vault_id               = oci_kms_vault.application.id
  key_id                 = oci_kms_key.application.id
  secret_name            = "${var.project_name}-internal-api-key"
  description            = "Generated API key shared by the auth bootstrap and evaluation service."
  enable_auto_generation = true
  freeform_tags          = merge(local.common_tags, { Purpose = "ApplicationKey" })

  secret_generation_context {
    generation_type     = "PASSPHRASE"
    generation_template = "SECRETS_DEFAULT_PASSWORD"
    passphrase_length   = 32
  }
}
