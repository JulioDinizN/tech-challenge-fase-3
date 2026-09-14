# ADR 0002: Matriz dinâmica e promoção centralizada

## Status

Implementada.

## Decisão

Um orquestrador detecta diretórios alterados e chama um workflow reutilizável para cada serviço. Cada serviço percorre jobs bloqueantes de testes, lint, SAST/SCA e build/scan de imagem. Na main, após toda a matriz passar, um workflow separado recebe credenciais e publica os artefatos escaneados. Um único job cria o commit GitOps com todas as promoções.

## Consequências

- Um serviço alterado não reconstrói os outros.
- Arquivos compartilhados selecionam todos.
- Pull Requests nunca recebem secrets ou publicam.
- A promoção única evita corridas de push.
- Cada serviço possui tag independente.
