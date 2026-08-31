# Requisitos e critérios de aceite da Fase 3

Fonte autoritativa: o PDF da Fase 3 mantido fora do repositório Git.

## Infraestrutura como código

- [ ] VCN, subnets, gateways e rotas em módulos Terraform.
- [ ] OKE e node pool em Terraform.
- [ ] Três PostgreSQL, OCI Cache, Queue e NoSQL.
- [ ] Cinco repositórios privados no OCIR.
- [ ] Vault, segredos gerados e Workload Identity.
- [ ] Backend OCI privado e versionado, com state separado para core e platform.

## CI e DevSecOps

- [x] Catálogo dos cinco serviços e matriz dinâmica.
- [x] Scaffold de testes, lint, SAST, SCA, build e scan.
- [ ] Baseline de achados corrigido.
- [ ] Security gate crítico ativado.
- [ ] Publicação no OCIR validada com tag imutável.
- [ ] Falha intencional e correção demonstradas.

## GitOps

- [x] Repositório independente estruturado por serviço.
- [x] ApplicationSet com cinco aplicações.
- [x] Promoção centralizada em um commit.
- [ ] Manifests da Fase 2 migrados.
- [ ] Argo CD instalado por Terraform.
- [ ] Auto-sync, prune e self-heal ativados após autorização.

## Entrega

- [ ] Documentação, diagrama, estimativa OCI, vídeo e relatório finais.
- [ ] Teardown validado depois da gravação.
