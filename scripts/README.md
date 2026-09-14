# Scripts da Fase 3

| Script | Finalidade | Efeito |
| --- | --- | --- |
| `prepare-phase3.sh` | Testes de automação, Terraform validate, estrutura GitOps e Compose | Validação local |
| `check-cloud-prerequisites.sh` | Verifica ferramentas instaladas | Somente leitura |
| `configure-phase3-gitops.py` | Preenche identificadores não secretos e tags iniciais a partir dos outputs de core | Edita checkout GitOps local, sem push ou deploy |
| `smoke-oke.sh` | Verifica auth, flag, regra e avaliação pelo ingress | Cria/atualiza dados de demonstração |
| `ci/detect_changed_services.py` | Seleciona a matriz de serviços a partir do diff Git | Somente leitura |
| `ci/write_promotion.py` | Gera descritor da imagem publicada | Arquivo local |
| `ci/promote_gitops.py` | Atualiza tags dos serviços selecionados | Edita checkout GitOps local |
| `vendor-nginx-chart.py` | Reproduz chart NGINX com schema local e permissões restritas | Arquivo local |
| `export-diagrams.mjs` | Exporta fontes Draw.io para PNG | Arquivos locais |
| `render-report-pdf.mjs` | Gera o PDF da entrega a partir do HTML | `dist/delivery-report.pdf` |

A publicação das imagens pertence ao GitHub Actions. A instalação dos add-ons pertence ao Terraform platform. A aplicação dos manifests pertence ao Argo CD. Instruções de bootstrap e encerramento em [operações](../docs/phase3-operations.md).

## Smoke

Com o kubeconfig privado selecionado, executar `./scripts/smoke-oke.sh`. O script obtém a credencial de runtime sem imprimi-la, cria/atualiza a flag e a regra de demonstração e verifica uma avaliação pelo Load Balancer. Não executar com shell tracing (`set -x`).

## Bootstrap GitOps

`configure-phase3-gitops.py` lê os outputs de `infra/environments/homolog/core`. Utilizar somente para configurar a base inicial dos cinco serviços e revisar o diff antes de publicar. As promoções posteriores são feitas pelo CI, preservando as tags dos serviços inalterados.
