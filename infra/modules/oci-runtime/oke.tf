resource "oci_containerengine_cluster" "main" {
  compartment_id     = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name               = "${var.project_name}-oke"
  type               = var.oke_cluster_type
  vcn_id             = oci_core_vcn.main.id
  freeform_tags      = local.common_tags

  cluster_pod_network_options {
    cni_type = "FLANNEL_OVERLAY"
  }

  endpoint_config {
    is_public_ip_enabled = true
    nsg_ids              = [oci_core_network_security_group.api.id]
    subnet_id            = oci_core_subnet.api.id
  }

  options {
    service_lb_subnet_ids = [oci_core_subnet.load_balancer.id]

    add_ons {
      is_kubernetes_dashboard_enabled = false
      is_tiller_enabled               = false
    }

    kubernetes_network_config {
      pods_cidr     = "10.244.0.0/16"
      services_cidr = "10.96.0.0/16"
    }
  }

  lifecycle {
    precondition {
      condition     = contains(data.oci_containerengine_cluster_option.oke.kubernetes_versions, var.kubernetes_version)
      error_message = "kubernetes_version is not supported by OKE in the selected region."
    }
  }
}

resource "oci_containerengine_node_pool" "main" {
  cluster_id         = oci_containerengine_cluster.main.id
  compartment_id     = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name               = coalesce(var.node_pool_name, "${var.project_name}-workers")
  node_shape         = var.node_shape
  ssh_public_key     = var.ssh_public_key
  freeform_tags      = local.common_tags

  initial_node_labels {
    key   = "app.kubernetes.io/part-of"
    value = var.project_name
  }

  node_config_details {
    is_pv_encryption_in_transit_enabled = false
    nsg_ids                             = [oci_core_network_security_group.workers.id]
    size                                = var.node_pool_size

    dynamic "placement_configs" {
      for_each = slice(
        data.oci_identity_availability_domains.available.availability_domains,
        var.node_availability_domain_start_index,
        var.node_availability_domain_start_index + coalesce(
          var.node_availability_domain_count,
          length(data.oci_identity_availability_domains.available.availability_domains) - var.node_availability_domain_start_index,
        ),
      )

      content {
        availability_domain = placement_configs.value.name
        subnet_id           = oci_core_subnet.workers.id
      }
    }
  }

  node_shape_config {
    memory_in_gbs = var.node_memory_in_gbs
    ocpus         = var.node_ocpus
  }

  node_source_details {
    boot_volume_size_in_gbs = tostring(var.node_boot_volume_size_in_gbs)
    image_id                = var.node_image_id
    source_type             = "IMAGE"
  }

  dynamic "node_pool_cycling_details" {
    for_each = var.oke_cluster_type == "ENHANCED_CLUSTER" ? [1] : []

    content {
      cycle_modes             = ["INSTANCE_REPLACE"]
      is_node_cycling_enabled = true
      maximum_surge           = "1"
      maximum_unavailable     = "0"
    }
  }

  lifecycle {
    create_before_destroy = true

    precondition {
      condition     = contains(data.oci_containerengine_node_pool_option.oke.shapes, var.node_shape)
      error_message = "node_shape is not supported for this OKE node-pool configuration."
    }

    precondition {
      condition = contains(
        data.oci_containerengine_node_pool_option.oke.sources[*].image_id,
        var.node_image_id,
      )
      error_message = "node_image_id is not an OKE image compatible with kubernetes_version."
    }

    precondition {
      condition = (
        var.node_availability_domain_start_index < length(data.oci_identity_availability_domains.available.availability_domains) &&
        (
          var.node_availability_domain_count == null ||
          var.node_availability_domain_start_index + var.node_availability_domain_count <= length(data.oci_identity_availability_domains.available.availability_domains)
        )
      )
      error_message = "The configured worker availability-domain range exceeds the availability domains in the selected region."
    }
  }
}
