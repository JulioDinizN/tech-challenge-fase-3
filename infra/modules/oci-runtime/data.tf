data "oci_identity_availability_domains" "available" {
  compartment_id = var.tenancy_ocid
}

data "oci_core_services" "oracle_services" {
  filter {
    name   = "name"
    regex  = true
    values = ["All .* Services In Oracle Services Network"]
  }
}

data "oci_containerengine_cluster_option" "oke" {
  cluster_option_id              = "all"
  compartment_id                 = var.compartment_id
  should_list_all_patch_versions = true
}

data "oci_containerengine_node_pool_option" "oke" {
  node_pool_option_id            = "all"
  compartment_id                 = var.compartment_id
  node_pool_k8s_version          = var.kubernetes_version
  should_list_all_patch_versions = true
}
