# Core OCI — Fase 3

Root da infraestrutura, compondo `../../../modules/oci-runtime`. Copiar e preencher `terraform.tfvars.example` e `backend.hcl.example` em arquivos ignorados pelo Git. Usar backend remoto privado/versionado e a chave core.tfstate.

`init -backend=false` e `validate` são verificações locais. Antes de plan/apply, confirmar imagem, Kubernetes, quotas e dono dos recursos. Não aplicar em paralelo com o legado `infra/oci`. A preparação não migrou state. A imagem do exemplo foi confirmada na OCI em 2026-09-13; disponibilidade deve ser reconfirmada antes de aplicar. Procedimento completo em `docs/phase3-operations.md` na raiz do repositório.
