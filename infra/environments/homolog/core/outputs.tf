output "oke_cluster" {
  value = module.runtime.oke_cluster
}

output "deployment_context" {
  value = module.runtime.deployment_context
}

output "kubeconfig_command" {
  value = module.runtime.kubeconfig_command
}

output "ocir_repositories" {
  value = module.runtime.ocir_repositories
}

output "postgresql_systems" {
  value = module.runtime.postgresql_systems
}

output "vault" {
  value = module.runtime.vault
}

output "redis" {
  value = module.runtime.redis
}

output "evaluation_queue" {
  value = module.runtime.evaluation_queue
}

output "analytics_table" {
  value = module.runtime.analytics_table
}

output "network" {
  value = module.runtime.network
}

output "workload_identity_policy_id" {
  value = module.runtime.workload_identity_policy_id
}
