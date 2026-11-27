# Como Contribuir

## Preparação

1. Crie um ambiente virtual Python.
2. Instale `requirements-dev.txt`.
3. Abra uma branch curta a partir de `main`.
4. Não use dados pessoais reais nos testes.

## Padrão para mudanças

- Preserve os nomes internos em inglês usados pelo motor e use os dados localizados somente para apresentação.
- Toda mudança em fórmula deve incluir teste e registrar a fonte ou hipótese.
- Mudanças de interface precisam funcionar em português e inglês.
- Não adicione segredos, backups, conteúdo de `app/storage/` ou arquivos `.env`.
- Prefira alterações pequenas, com uma finalidade clara por pull request.

## Verificação obrigatória

```powershell
python -m pytest -q -p no:cacheprovider
node --check static/js/app.js
python -m compileall -q app tests
```

Use o checklist automático do pull request e descreva o cenário testado no navegador.

