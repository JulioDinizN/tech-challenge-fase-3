# ADR 0002: Matriz dinâmica e promoção centralizada

## Status

Aceita para o scaffold.

## Decisão

Um orquestrador detecta diretórios alterados e chama um workflow reutilizável para cada serviço. Na main, cada job pode publicar uma imagem e gerar um descritor; um único job cria um commit GitOps com todas as promoções.

## Consequências

- Um serviço alterado não reconstrói os outros.
- Arquivos compartilhados selecionam todos.
- Pull Requests nunca recebem secrets ou publicam.
- A promoção única evita corridas de push.
- Cada serviço possui tag independente.
