# Documentação — Fase 3

- [Arquitetura](architecture.md): Terraform, fluxo CI/GitOps e runtime OCI.
- [Operação](phase3-operations.md): validação, bootstrap, acesso e encerramento.
- [Decisões](decisions/0001-repository-strategy.md): estratégia de repositórios, CI e segredos.
- [Desenvolvimento local](local-development.md): execução dos serviços com Docker Compose.
- [Estimativas AWS e OCI](costs/README.md): PDFs, capturas, links e memória de cálculo.
- [Scripts](../scripts/README.md): automação mantida nesta entrega.

## Diagramas

| Visão | Fonte editável | Exportação |
| --- | --- | --- |
| Infraestrutura e entrega | [Draw.io](diagrams/overall-architecture.drawio) | [PNG](diagrams/overall-architecture.png) |
| Runtime OCI | [Draw.io](diagrams/runtime-architecture.drawio) | [PNG](diagrams/runtime-architecture.png) |

As fontes `.drawio` são editáveis. `npm run diagrams:export` regenera os PNGs com draw.io Desktop; `DRAWIO_BIN` permite indicar outro caminho para o executável.

## Relatório

[PDF de entrega](../dist/delivery-report.pdf), [HTML com anexos](report.html) e [TXT](report.txt). O relatório inclui o link do vídeo de demonstração.

`npm run report:pdf` gera `dist/delivery-report.pdf`, versionado junto com o HTML e o TXT. O HTML é a fonte de impressão; o PDF inclui diagramas e capturas das estimativas. O PDF é gerado a partir da versão atual do HTML.
