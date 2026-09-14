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

# Oracle platform images can remain available after leaving the OKE suggestions list.
data "oci_core_image" "worker" {
  image_id = var.node_image_id
}

data "oci_core_shapes" "worker_image" {
  compartment_id = var.compartment_id
  image_id       = var.node_image_id
  shape          = var.node_shape
}

data "oci_core_image" "oke_catalog_reference" {
  image_id = data.oci_containerengine_node_pool_option.oke.sources[0].image_id
}
