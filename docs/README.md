# Documentação — Fase 3

Comece por:

- [Estimativas AWS e OCI](costs/README.md): PDFs, prints oficiais, links e memória de cálculo para a entrega.
- [Arquitetura](architecture.md): fluxo de entrega e runtime OCI, distinguindo implementação de arquitetura alvo.
- [Decisões](decisions/0001-repository-strategy.md): estratégia de dois repositórios; demais ADRs na mesma pasta.
- [Desenvolvimento local](local-development.md) e [correções dos serviços](fixes.md): material herdado da Fase 2.

## Diagramas

| Visão | Fonte editável | Exportação |
| --- | --- | --- |
| Terraform, CI/DevSecOps, GitOps e Argo CD | [overall-architecture.drawio](diagrams/overall-architecture.drawio) | [PNG](diagrams/overall-architecture.png) |
| Runtime OCI, no estilo da Fase 2 | [runtime-architecture.drawio](diagrams/runtime-architecture.drawio) | [PNG](diagrams/runtime-architecture.png) |

Os `.drawio` são a fonte de verdade. `npm run diagrams:export` regenera os dois PNGs com o CLI do draw.io Desktop. O script procura `/Applications/draw.io.app/Contents/MacOS/draw.io` e aceita `DRAWIO_BIN` para outro caminho. Não editar exports manualmente.

## Relatório da Fase 3

[HTML com prints](report.html) e [TXT](report.txt) preparados. Ainda são rascunhos: preencher vídeo e evidências reais, conferir identificação e testar acesso aos links antes da submissão. Nenhum resultado da Fase 2 é tratado como implantação da Fase 3.

Após a gravação, `npm run report:pdf` exporta o HTML para `dist/delivery-report.pdf`, ignorado pelo Git. Revisar o PDF e anexar as estimativas de `costs/`. O relatório exige PDF ou TXT; o HTML é a fonte para impressão.
