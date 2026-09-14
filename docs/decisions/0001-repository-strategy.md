# ADR 0001: Dois repositórios para código e GitOps

## Status

Adotada.

## Decisão

Manter os cinco serviços, Terraform, CI e documentação em um monorepo. Manter o estado desejado Kubernetes em um segundo repositório GitOps.

## Consequências

- Preserva as adaptações integradas da Fase 2.
- Separa código-fonte da autorização de deploy.
- Exige uma credencial cross-repository de escopo mínimo.
- Cinco repositórios de serviço ficam fora do escopo.
