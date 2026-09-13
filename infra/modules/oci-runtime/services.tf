resource "oci_artifacts_container_repository" "services" {
  for_each = local.service_names

  compartment_id = var.compartment_id
  display_name   = "${var.project_name}/${each.value}"
  is_immutable   = false
  is_public      = false
  freeform_tags  = local.common_tags
}

resource "oci_psql_db_system" "services" {
  for_each = local.database_names

  compartment_id              = var.compartment_id
  db_version                  = var.postgres_db_version
  display_name                = "${var.project_name}-${each.key}-db"
  instance_count              = var.postgres_instance_count
  instance_memory_size_in_gbs = var.postgres_memory_in_gbs[each.key]
  instance_ocpu_count         = var.postgres_ocpus[each.key]
  shape                       = var.postgres_shapes[each.key]
  system_type                 = "OCI_OPTIMIZED_STORAGE"
  freeform_tags               = merge(local.common_tags, { DatabaseName = each.value })

  credentials {
    username = var.postgres_admin_username

    password_details {
      password_type  = "VAULT_SECRET"
      secret_id      = oci_vault_secret.postgres_admin_password[each.key].id
      secret_version = oci_vault_secret.postgres_admin_password[each.key].current_version_number
    }
  }

  network_details {
    nsg_ids   = [oci_core_network_security_group.data.id]
    subnet_id = oci_core_subnet.data.id
  }

  source {
    source_type = "NONE"
  }

  storage_details {
    availability_domain   = var.postgres_regionally_durable ? null : local.selected_availability_domain
    is_regionally_durable = var.postgres_regionally_durable
    system_type           = "OCI_OPTIMIZED_STORAGE"
  }
}

resource "oci_redis_redis_cluster" "evaluation" {
  compartment_id     = var.compartment_id
  cluster_mode       = "NONSHARDED"
  display_name       = "${var.project_name}-evaluation-cache"
  node_count         = var.redis_node_count
  node_memory_in_gbs = var.redis_node_memory_in_gbs
  nsg_ids            = [oci_core_network_security_group.data.id]
  software_version   = var.redis_software_version
  subnet_id          = oci_core_subnet.data.id
  freeform_tags      = local.common_tags
}

resource "oci_queue_queue" "evaluations" {
  compartment_id                   = var.compartment_id
  display_name                     = "${var.project_name}-evaluation-events"
  retention_in_seconds             = var.queue_retention_in_seconds
  visibility_in_seconds            = var.queue_visibility_in_seconds
  timeout_in_seconds               = 20
  dead_letter_queue_delivery_count = 5
  freeform_tags                    = local.common_tags
}

resource "oci_nosql_table" "analytics" {
  compartment_id = var.compartment_id
  name           = var.nosql_table_name
  ddl_statement  = "CREATE TABLE IF NOT EXISTS ${var.nosql_table_name} (event_id STRING, user_id STRING, flag_name STRING, result BOOLEAN, occurred_at STRING, PRIMARY KEY(SHARD(event_id)))"
  freeform_tags  = local.common_tags

  table_limits {
    capacity_mode      = "PROVISIONED"
    max_read_units     = var.nosql_read_units
    max_storage_in_gbs = var.nosql_storage_in_gbs
    max_write_units    = var.nosql_write_units
  }
}
