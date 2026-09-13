# Arquitetura — ToggleMaster Fase 3

Revisão de 13/09/2026: implementação local e planos preliminares backend/core aprovados. Não houve provisionamento; o fluxo integrado permanece pendente de execução real. OCI foi aceita pela disciplina conforme confirmação do responsável pelo projeto em 13/09/2026. Não apresentamos os recursos OCI como recursos AWS.

## Ambiente e organização Terraform

Usamos somente `homolog`, um ambiente temporário para demonstração. O enunciado não exige homologação e produção simultâneas. As três raízes separam responsabilidades, não duplicam ambientes:

| Raiz | Responsabilidade |
| --- | --- |
| `infra/environments/homolog/backend` | Bucket privado/versionado para states |
| `infra/environments/homolog/core` | Instancia o módulo `oci-runtime`, que contém rede, OKE, OCIR, dados, Vault e IAM |
| `infra/environments/homolog/platform` | Provider Helm instala CSI, provider OCI, Metrics Server, NGINX, Argo CD e bootstrap opcional |

`infra/modules/oci-runtime` é um módulo composto funcional, com arquivos separados por responsabilidade. Não são cinco submódulos independentes. A preferência do enunciado por módulos é atendida sem exigir um módulo por serviço cloud. Os antigos READMEs de módulos futuros foram movidos para a preparação fora do Git, para não aparentarem implementação inexistente.

`infra/oci` é a referência legada da Fase 2; não aplicar em paralelo com core. Cada recurso deve ter um único proprietário. States de backend, core e platform usam chaves distintas no Object Storage. `configured-at-init` é placeholder: o backend real ainda precisa ser configurado. O plano preliminar usou uma cópia isolada com state local vazio, pois o bucket antigo retornou BucketNotFound; não é o backend de operação nem um plano autorizado para apply.

## CI/CD e GitOps

1. PR e push na main selecionam serviços alterados; mudanças compartilhadas selecionam os cinco.
2. Cada serviço usa jobs de build/testes, lint, SAST/SCA e build/scan de imagem. A sequência é bloqueante. Trivy reprova CRITICAL; lint e SAST também não toleram falhas.
3. Somente push na main com `ENABLE_OCIR_PUBLISH=true` publica, após toda a matriz passar. Credenciais OCIR existem apenas no workflow separado de publicação. A imagem publicada é o artefato previamente escaneado.
4. Promoção, habilitada por `ENABLE_GITOPS_PROMOTION=true`, consolida tags `sha-<12 hex>` em um commit no repositório GitOps. CI não faz deploy e o gate agregado inclui publicação e promoção.
5. Argo CD monitora os overlays e reconcilia as aplicações quando auto-sync estiver autorizado e habilitado. A rastreabilidade é SHA fonte → tag/digest → commit GitOps → revisão Argo → imagem do pod.

O GitOps renderiza 32 recursos com dono único: 11 compartilhados e 21 dos serviços, incluindo cinco Deployments. Placeholders de IDs/endpoints/imagens permanecem até o bootstrap. `automated.enabled: false` e `bootstrap_gitops=false` são proteções de preparação; precisam ser ativados na janela autorizada para demonstrar sync automático.

## Runtime e segredos

OKE Enhanced com dois workers E5; três PostgreSQL independentes para auth, flag e targeting; Redis para evaluation; Queue e NoSQL para analytics. Cinco registries privados OCIR. O Service do NGINX solicita o Load Balancer OCI, que deve ser removido enquanto o controller e o cluster ainda existem.

Vault gera oito segredos e o provider CSI usa Workload Identity. ConfigMaps contêm configuração não secreta. Jobs inicializam bancos e usuários restritos antes dos serviços. O pull secret OCIR tem bootstrap próprio, pois a imagem precisa ser obtida antes de montar os volumes CSI. Credenciais e planos/state não pertencem ao Git.

Compose mantém o modo local herdado; sua validação não comprova integrações OCI. A saúde real de bancos, workload identity, fila, analytics, Ingress e Argo será verificada após a implantação autorizada.

## Diagramas e documentos

![Entrega](diagrams/overall-architecture.png)
![Runtime](diagrams/runtime-architecture.png)

As fontes `.drawio` são editáveis e `npm run diagrams:export` regenera os PNGs. Os desenhos representam a arquitetura; não são evidência de implantação.

- [Operação e encerramento](phase3-operations.md)
- [Estimativas AWS e OCI](costs/README.md)
- [Relatório da entrega](report.html)
- [Decisões](decisions/0001-repository-strategy.md)
