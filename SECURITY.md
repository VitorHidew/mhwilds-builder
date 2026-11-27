# Política de Segurança

## Versões suportadas

A branch `main` é a única versão que recebe correções de segurança até a criação de releases estáveis.

## Como relatar uma vulnerabilidade

Não abra uma issue pública com detalhes de exploração. Use a opção **Security > Report a vulnerability** do repositório no GitHub. Inclua o fluxo afetado, impacto, passos mínimos para reproduzir e, quando possível, uma sugestão de correção.

## Modelo de segurança

- O projeto não usa cadastro, login ou papéis administrativos.
- A persistência do servidor é isolada por uma sessão anônima assinada em cookie `HttpOnly` e `SameSite=Strict`.
- Dados do usuário também ficam no `localStorage`; não inclua backups em issues ou commits.
- Em produção, `MHWILDS_SESSION_SECRET` é obrigatório e deve possuir pelo menos 32 caracteres.
- `MHWILDS_ALLOWED_ORIGINS` deve listar somente origens HTTPS controladas pelo responsável pela implantação.
- Arquivos em `app/storage/`, `.env` e `.session_secret` nunca devem ser versionados.

## Antes de publicar

Execute a suíte de testes, confira `git status`, revise os arquivos preparados para commit e ative proteção da branch, Dependabot, CodeQL e secret scanning no GitHub.

