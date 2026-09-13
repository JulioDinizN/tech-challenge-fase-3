# OCI runtime module

Phase 3 runtime: network, OKE, PostgreSQL, Cache, Queue, NoSQL, OCIR, Vault and workload policies. Resources are separated by responsibility into Terraform files and composed by `infra/environments/homolog/core`. Provider configuration stays in the root.

Derived from the Phase 2 root. Use only one state owner per resource. Existing Phase 2 resources must be inventoried and explicitly migrated/imported before applying Phase 3 to their compartment. This preparation does not move state or provision resources.
