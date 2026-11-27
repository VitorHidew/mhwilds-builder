# Correções de segurança aplicadas

## Modelo de proteção atual

O projeto usa uma sessão anônima assinada e armazenada em cookie `HttpOnly` com
`SameSite=Strict`. Builds, talismãs e resultados de dano recebem internamente um
proprietário e todas as operações de listar, salvar e excluir são filtradas por
essa sessão. O identificador interno não é devolvido pela API.

Dados JSON criados antes desta mudança são vinculados ao primeiro navegador que
abrir a aplicação localmente. A migração automática é desativada em produção.

## Configuração de produção

Defina estas variáveis no serviço de hospedagem:

- `MHWILDS_ENV=production`
- `MHWILDS_SESSION_SECRET`: segredo aleatório com pelo menos 32 caracteres.
- `MHWILDS_ALLOWED_ORIGINS`: origens HTTPS permitidas, separadas por vírgula.
- `MHWILDS_STORAGE_DIR`: diretório persistente e privado da aplicação.

O servidor recusa a inicialização em produção quando o segredo está ausente ou
é curto. O valor `*` também é recusado na lista de origens.

## Proteções adicionais

- Limites de tamanho para IDs, nomes e descrições salvas.
- Gravação atômica dos arquivos JSON e trava durante alterações concorrentes.
- Cabeçalhos de proteção contra iframe, MIME sniffing, permissões indevidas e
  carregamento de recursos fora da aplicação.
- Renderização de nomes, habilidades e alertas com `textContent`/elementos DOM.
- Botões de registros dinâmicos conectados por eventos, sem JavaScript montado
  a partir de IDs fornecidos pelo cliente.
- Janela interna acessível para renomear builds, sem depender de `prompt()`.
- Backup local versionado, com validação de origem, limite de 5 MB e importação
  por mesclagem para evitar apagar dados existentes.
- Manifesto de integridade com contagens e SHA-256 dos arquivos da base.
- Contêiner executado sem root, sem capacidades extras, sem elevação de
  privilégios e com sistema de arquivos somente leitura.
- CI, CodeQL e Dependabot preparados em `.github/`.

## Modelo definitivo sem cadastro

A sessão anônima protege dados entre navegadores, mas não é uma conta de usuário
e não sincroniza builds entre dispositivos. Essa é uma decisão de produto: a
recuperação e a migração são feitas pelo backup disponível em `Configurações`.
Perder ao mesmo tempo os dados do navegador, o cookie e o arquivo de backup
impede a recuperação das builds.

## Verificação atual

- 62 testes automatizados aprovados.
- Sintaxe Python e JavaScript validada.
- Fluxos de cálculo, filtros, uptime, cenário, salvamento, talismãs, otimizador,
  comparador com múltiplas builds, idioma, tema, exportação e importação
  verificados no navegador.
- Varredura local sem segredos hardcoded encontrados.
