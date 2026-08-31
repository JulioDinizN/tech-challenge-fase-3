# ADR 0003: Preservar OCI Vault e Workload Identity

## Status

Aceita para o scaffold.

## Decisão

Preservar OCI Vault e Secrets Store CSI para runtime. O CI não recebe segredos de aplicação. O imagePullSecret do OCIR será um bootstrap separado porque a imagem é baixada antes do volume CSI existir.

## Consequências

- Senhas, MASTER_KEY e chave interna não entram no CI ou GitOps.
- Queue e NoSQL continuam com Workload Identity.
- Publicação CI e leitura do cluster usam identidades distintas.
