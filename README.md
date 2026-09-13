# POSTECH Tech Challenge - Fase 3

Repositório principal do ToggleMaster para a Fase 3. Ele preserva a implementação validada na Fase 2 e acrescenta a implementação de infraestrutura como código, CI/DevSecOps e promoção GitOps.

## Estado atual

Esta primeira entrega contém somente código e estrutura local. Nenhuma infraestrutura OCI foi criada, alterada ou removida.

Revisão local de 13/09/2026: **planos preliminares backend/core e validação local aprovados; demonstração integrada ainda pendente**. Veja os [diagramas de entrega e runtime](docs/architecture.md). O relatório da Fase 3 está preparado como rascunho, pendente do vídeo e das evidências reais.

| Área | Estado |
| --- | --- |
| Microsserviços, Docker e Compose da Fase 2 | Preservados |
| Terraform OCI da Fase 2 | Preservado em infra/oci durante a migração |
| Estrutura Terraform modular da Fase 3 | Roots backend/core/platform e módulo funcional oci-runtime |
| CI de monorepo | Detecção, matriz, gates obrigatórios e publicação isolada |
| Publicação no OCIR | Desabilitada por padrão |
| Promoção para o GitOps | Desabilitada por padrão |
| Deploy no OKE | Não executado |

## Repositórios

- Código, infraestrutura e CI: JulioDinizN/tech-challenge-fase-3
- Estado desejado Kubernetes: JulioDinizN/tech-challenge-fase-3-gitops

O repositório GitOps é separado para que o CI publique imagens e altere somente tags. O Argo CD será o único responsável por reconciliar os workloads no OKE.

## Fluxo planejado

~~~text
Pull Request
  -> detectar serviços alterados
  -> testes, lint, SAST, SCA, build e scan da imagem
  -> sem credenciais OCI e sem push

Push na main
  -> repetir todos os gates
  -> publicar somente as imagens alteradas no OCIR com tag sha-*
  -> gerar descritores de promoção
  -> atualizar todas as tags afetadas em um único commit GitOps
  -> Argo CD sincronizar somente as aplicações alteradas
~~~

## Estrutura

~~~text
.ci/                         # Catálogo e versões das ferramentas de CI
.github/workflows/           # CI de serviços e validação de Terraform
services/                    # Cinco microsserviços importados na Fase 2
docker/                      # Inicialização do ambiente local
docker-compose.yml           # Topologia local de nove contêineres
infra/oci/                   # Terraform funcional herdado da Fase 2
infra/environments/homolog/  # Roots backend, core e platform
infra/modules/               # Módulo funcional oci-runtime
scripts/ci/                  # Detecção e promoção sem dependências externas
docs/decisions/              # ADRs da arquitetura da Fase 3
~~~

## Controles de ativação

- Lint/SAST/SCA e scan de imagem são bloqueantes; não dependem de SECURITY_GATE_ENABLED.
- ENABLE_OCIR_PUBLISH=true permite push ao OCIR somente na main.
- ENABLE_GITOPS_PROMOTION=true permite atualizar o GitOps depois da publicação.

Enquanto essas variáveis estiverem ausentes ou diferentes de true, os workflows não publicam imagens nem alteram o GitOps. Deploy continua fora do CI mesmo após a ativação.

## Segredos e identidades

OCI Vault continua como fonte dos segredos de runtime, consumidos no OKE por Workload Identity e Secrets Store CSI. O CI não lê senhas de banco, MASTER_KEY ou chaves internas.

A publicação futura utilizará OCIR_USERNAME e OCIR_AUTH_TOKEN limitados ao OCIR, além de GITOPS_TOKEN limitado ao repositório GitOps. OCIR_REGISTRY, OCIR_NAMESPACE e OCIR_REPOSITORY_PREFIX serão GitHub Variables não secretas.

## Validação local

~~~bash
python3 scripts/ci/detect_changed_services.py --base HEAD --head HEAD
python3 -m unittest discover -s scripts/ci -p 'test_*.py'
terraform fmt -check -recursive infra
terraform -chdir=infra/oci init -backend=false
terraform -chdir=infra/oci validate
~~~

Esses comandos não fazem deploy.

## Proveniência

Base derivada de JulioDinizN/tech-challenge-fase-2 no commit 00bc8a4565aeaba4dc65212251c98f7df465d0f1.

## Ambiente de demonstração

Somente `homolog` será usado. O enunciado não exige ambientes separados de homologação e produção. `backend`, `core` e `platform` separam responsabilidades e states, não ambientes duplicados. O módulo `oci-runtime` compõe os recursos OCI, separados em arquivos por responsabilidade; não há cinco submódulos independentes. Procedimento de ativação e encerramento em [operações](docs/phase3-operations.md).
