# Arquitetura

## Visão geral

O projeto usa FastAPI no servidor e HTML, CSS e JavaScript sem framework no navegador. A aplicação é entregue pelo mesmo processo, portanto não depende de um segundo servidor de frontend.

## Camadas

- `app/main.py`: rotas HTTP, sessão anônima, persistência e entrega dos arquivos da interface.
- `app/models.py`: contratos Pydantic e validação dos dados de entrada.
- `app/engine.py`: cálculo da build, habilidades, afinidade, elemento, hitzones e rotação.
- `app/optimizer.py`: busca e ordenação de combinações.
- `app/rotations.py`: combos e valores de movimento usados pelo motor.
- `app/data.py`: carga da base versionada.
- `static/`: documento, aparência e comportamento do navegador.

## Persistência sem conta

O navegador é a fonte primária para os dados pessoais. Builds, resultados, talismãs, lista de desejos e preferências são armazenados em `localStorage`. Builds, resultados e talismãs também podem ser copiados para JSON no servidor.

O servidor associa cada registro a um identificador aleatório. Esse identificador fica em cookie assinado, `HttpOnly` e `SameSite=Strict`; ele não é retornado no corpo da API. Toda listagem, gravação e exclusão filtra pelo dono da sessão.

Esse modelo oferece isolamento local sem cadastro, mas não promete recuperação caso cookie, armazenamento do navegador e backup sejam perdidos ao mesmo tempo.

## Dados do jogo

`app/data_manifest.json` registra versão, origem, arquivos esperados e contagens mínimas. `/api/data/version` recalcula contagens e SHA-256 dos arquivos, enquanto `/api/health` incorpora esse diagnóstico para implantação e monitoramento.

## Produção

O processo exige um segredo de sessão explícito quando `MHWILDS_ENV=production`. O Docker executa como usuário sem privilégios, usa `/data` para persistência e fornece health check. Origens CORS são configuráveis e curingas são recusados.

