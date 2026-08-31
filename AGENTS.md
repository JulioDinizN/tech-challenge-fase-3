# ToggleMaster Phase 3 Workspace Guide

## Scope

- This repository owns service sources, local Docker, Terraform, CI, scripts, and delivery documentation.
- Kubernetes desired state belongs in JulioDinizN/tech-challenge-fase-3-gitops.
- Preserve working Phase 2 behavior while Phase 3 automation is introduced.

## Hard boundaries

- Never run terraform apply/destroy, mutating OCI CLI commands, Helm installs, kubectl apply, Argo syncs, or image pushes without explicit authorization.
- Never commit OCI keys or tokens, database passwords, Vault secret contents, kubeconfigs, Terraform state, or saved plans.
- Service CI must not receive application runtime secrets.
- CI may publish only from main after all gates and only when ENABLE_OCIR_PUBLISH=true.
- CI must never deploy directly; promotion ends in a GitOps commit.
- Never add Co-Authored-By lines to commit messages.

## Monorepo rules

- Keep .ci/services.json synchronized with services/.
- Shared CI logic belongs in .github/workflows/_service-ci.yml.
- Test and publish only changed services unless a shared file changes.
- Consolidate promotions into one GitOps commit.
- Use immutable sha-<12 hex> tags; never deploy latest.

## Terraform migration

- infra/oci remains the functional Phase 2 root until deliberately migrated.
- Phase 3 roots are infra/environments/homolog/core and platform.
- core owns OCI resources; platform will own add-ons and Argo bootstrap.
- Use native OCI backends with distinct Object Storage keys.
- Never own the same OCI resource from legacy and modular states.

## Secrets

- OCI Vault remains the runtime source of truth.
- OKE workloads use dedicated ServiceAccounts and Workload Identity.
- OCIR image pull credentials are a separate bootstrap concern.
- GitOps may contain secret identifiers, never secret values.
