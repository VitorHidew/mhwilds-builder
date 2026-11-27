# Checklist para Publicação no GitHub

## Antes do primeiro commit

- [ ] Revisar nome, descrição e licença do projeto.
- [ ] Confirmar que `.env`, `.session_secret`, `app/storage/*.json` e backups não aparecem no commit.
- [ ] Remover arquivos temporários sem uso.
- [ ] Executar testes de Python, JavaScript e interface.
- [ ] Conferir `/api/health` com `status: ok`.
- [ ] Revisar direitos de distribuição de imagens e dados de terceiros.

## Configuração do repositório

- [ ] Usar `main` como branch padrão.
- [ ] Exigir o workflow **Testes e build** antes de mesclar mudanças.
- [ ] Ativar secret scanning e push protection.
- [ ] Ativar private vulnerability reporting.
- [ ] Manter CodeQL e Dependabot habilitados.
- [ ] Bloquear force push e exclusão da branch `main`.

## Apresentação de portfólio

- [ ] Adicionar uma captura real da tela principal ao README.
- [ ] Publicar uma demonstração somente após configurar HTTPS e origens CORS.
- [ ] Criar uma release `v0.1.0` com escopo, limitações e passos de teste.
- [ ] Adicionar tópicos: `fastapi`, `monster-hunter-wilds`, `build-optimizer`, `python`, `javascript`.

