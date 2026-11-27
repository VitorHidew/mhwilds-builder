# MH Wilds Build Optimizer & Calculator

Calculadora, montador e otimizador de builds para Monster Hunter Wilds. O projeto compara dano por rotação, DPS prático, afinidade, elemento, hitzones, habilidades condicionais, armaduras transcendidas e recomendações de armas Gogartianas.

> Projeto de fã independente, sem vínculo com a Capcom. Nomes, imagens e marcas de Monster Hunter pertencem aos seus respectivos titulares.

## Principais recursos

- Montador livre com armas, armaduras, talismãs e adornos compatíveis por tipo de slot.
- Cálculo físico e elemental por monstro, parte atingida, ferida, afiamento e rotação.
- Otimizador com metas de habilidades, builds pré-calculadas e regras de progressão.
- Comparador para várias builds, combos, DPS, dano por minuto e explicação das diferenças.
- Editor de arma Gogartiana, reforços, habilidades embutidas e restrição para RC 100+.
- Wiki interna bilíngue, inventário de talismãs e lista de desejos com materiais.
- Temas inspirados nos biomas e interface em português do Brasil e inglês; a revisão editorial de alguns textos legados ainda está pendente.
- Backup restaurável dos dados pessoais, sem cadastro e sem conta online.
- Planejamento de caçada: alvo, recomendação, comparação no mesmo cenário e materiais faltantes.
- Comparação explicável por recálculo de habilidades, versão do motor e cobertura da busca.

## Privacidade

O aplicativo não possui cadastro. Builds, resultados, talismãs e preferências são salvos primeiro no navegador. Quando o servidor local está disponível, builds, resultados e talismãs também recebem uma cópia isolada por uma sessão anônima assinada.

- Não há senha, e-mail, rastreamento ou perfil público.
- Cada navegador recebe uma sessão privada diferente.
- O backup em `Configurações` permite migrar ou recuperar os dados.
- A sessão anônima não oferece sincronização automática entre dispositivos.

## Rodar localmente

Requer Python 3.12 ou mais recente.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

Acesse `http://127.0.0.1:8000`. O diagnóstico da aplicação fica em `http://127.0.0.1:8000/api/health`.

## Testes

```powershell
python -m pytest -q -p no:cacheprovider
node --check static/js/app.js
node --check static/js/planner.js
node --check static/js/material-plan.js
node --test --test-isolation=none tests/material-plan.test.js tests/planner-state.test.js tests/workspace-state.test.js tests/calculation-state.test.js
python -m compileall -q app tests
```

## Docker

Crie um `.env` baseado no arquivo `.env.example` e gere um segredo aleatório com pelo menos 32 caracteres. O contêiner de produção recusa iniciar sem esse segredo.

```powershell
Copy-Item .env.example .env
docker compose up --build
```

O volume `mhwilds-data` mantém os dados anônimos fora da imagem. A configuração remove capacidades do processo, impede elevação de privilégios e deixa o sistema de arquivos do contêiner somente leitura.

## Estrutura

```text
app/                    API, modelos, cálculo, otimização e dados versionados
static/index.html       Estrutura da aplicação
static/css/app.css      Temas e componentes visuais
static/js/app.js        Fluxos da interface e persistência local
tests/                  Testes do motor, API, segurança e integridade
docs/                   Arquitetura, segurança e documentação de publicação
.github/                CI, CodeQL, Dependabot e modelo de pull request
```

Veja [Arquitetura](docs/ARCHITECTURE.md), [Política de segurança](SECURITY.md), [fontes dos dados](docs/DATA-SOURCES.md) e [checklist de publicação](docs/GITHUB-CHECKLIST.md).

O [plano de evolução](docs/PLANO-EVOLUCAO.md) e o [registro de validação](docs/VALIDACAO-EVOLUCAO.md) detalham as etapas entregues, evidências e limitações restantes.

A remodelação da experiência está documentada no [plano de UI/UX](docs/PLANO-UI-UX-EXPERIENCIA.md) e na [validação de UI/UX](docs/VALIDACAO-UI-UX.md), incluindo navegação, retomada do rascunho, comparação, imagens e limites de cobertura.

## Dados e limites

A base principal é sincronizada da [MHDB Wilds API](https://docs.wilds.mhdb.io/). Fontes complementares e limitações estão registradas em [docs/DATA-SOURCES.md](docs/DATA-SOURCES.md). Os resultados são estimativas comparativas: fórmulas, tempos de rotação e efeitos especiais devem ser validados no jogo antes de serem tratados como valores oficiais.

## Licença

O código original está sob a licença MIT. Dados, imagens, nomes e demais materiais de terceiros não são relicenciados; consulte [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

