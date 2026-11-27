# MH Wilds Build Optimizer & Calculator (Wilds Forge)

Calculadora, montador visual e otimizador de builds para **Monster Hunter Wilds** com suporte às **14 classes de arma**, **34 monstros** e **42 rotações de combate**. O sistema calcula dano físico e elemental em tempo real por parte atingida, afinidade, afiamento, *Element Cap*, feridas (*Modo Foco*) e habilidades condicionais.

> Projeto de fã independente, sem vínculo com a Capcom. Nomes, imagens e marcas de Monster Hunter pertencem aos seus respectivos titulares.

---

## Principais Recursos

- **Montador Visual de Builds:** seleção de arma, 5 peças de armadura, talismã e adornos com fotos locais, faixa visual de *loadout* e validação de slots por tipo (arma vs. armadura).
- **Motor de Dano Detalhado:**
  - Separação fiel de *True Raw* e *True Element* (`display / 10`).
  - Aplicação automática do **Element Cap** ($\max(\text{Base} + 350,\ \text{Base} \times 1.9)$ exibidos) com alerta visual.
  - Suporte a **Feridas / Modo Foco** com bônus de afinidade do *Weakness Exploit* e elevação configurável de Hitzone (`+HZV`).
  - Projeção de afiamento sustentado (*Handicraft*, *Razor Sharp*, *Master's Touch*, *Protective Polish*).
- **Galeria de Monstros & Hitzones:** catálogo visual dos 34 monstros com fraquezas físicas (`Corte`, `Impacto`, `Projétil`), elementais, status e ranking de partes.
- **Otimizador & Recomendações:** busca de sets por metas de habilidades, presets meta, regras de progressão e armas Gogartianas (RC 100+).
- **Comparador, Lista de Desejos e Wiki Interna:** compare até 4 builds lado a lado, acompanhe materiais faltantes e consulte definições em PT-BR e Inglês.
- **5 Temas de Biomas:** Planícies Zéfiras, Floresta Escarlate, Bacia Oleídea, Escarpas Frígidas e Ruínas de Wyveria.

---

## Como Instalar e Rodar (Passo a Passo)

### Pré-requisitos
- **Python 3.12+** (recomendado 3.12 ou 3.14)
- **Git** (opcional, para clonar)
- **Node.js 20+** (opcional, apenas para rodar os testes de frontend)

### Passo 1 — Clonar o repositório
```powershell
git clone https://github.com/VitorHidew/mhwilds-builder.git
cd mhwilds-builder
```

### Passo 2 — Criar e ativar o ambiente virtual
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(No Linux/macOS: `python3 -m venv .venv && source .venv/bin/activate`)*

### Passo 3 — Instalar as dependências
```powershell
python -m pip install -r requirements-dev.txt
```

### Passo 4 — Iniciar o servidor local
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Passo 5 — Acessar no navegador
- **Aplicação Web:** `http://127.0.0.1:8000/`
- **Documentação da API (Swagger):** `http://127.0.0.1:8000/docs`
- **Diagnóstico (Healthcheck):** `http://127.0.0.1:8000/api/health`

---

## Como Usar a Interface (Passo a Passo)

1. **Escolha o Alvo (`Alvo`):** selecione um dos 34 monstros na galeria visual, escolha a parte do corpo (ou *Média das partes*), marque **Ferida Ativa** (e o bônus `+HZV` desejado) e ajuste os *uptimes* das habilidades.
2. **Monte sua Build (`Build` → `Montar`):** clique em qualquer slot (ou na faixa visual no topo) para abrir o seletor com fotos e comparar o delta de habilidades antes de equipar.
3. **Otimize (`Build` → `Recomendar`):** defina sua arma, habilidades desejadas e execute a busca para receber recomendações ranqueadas.
4. **Compare e Planeje (`Comparar` / `Materiais`):** salve suas builds para comparar DPS, EFR e diferenças de peças, e envie as peças para a lista de materiais.

---

## Rodar com Docker

1. Crie o arquivo `.env` a partir do modelo e defina um segredo com pelo menos 32 caracteres em `MHWILDS_SESSION_SECRET`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Suba o contêiner:
   ```powershell
   docker compose up --build
   ```

---

## Testes

```powershell
python -m pytest -q -p no:cacheprovider
node --check static/js/app.js
node --check static/js/experience.js
node --test tests/*.test.js
```

---

## Estrutura do Projeto

```text
app/                        API FastAPI, motor de dano, otimizador, legalidade e catálogos JSON
static/index.html           Estrutura SPA da interface
static/css/                 Temas por bioma e estilos visuais (app.css, experience.css)
static/js/                  Lógica da interface, estado local e testes de unidade
static/assets/catalog/      Fotos locais de monstros, armas e armaduras + manifest.json
tests/                      Testes do motor, API, assets visuais, segurança e frontend
docs/                       Arquitetura, fontes de dados e auditoria do motor
```

---

## Privacidade, Dados e Licença

- **Sem conta obrigatória:** builds, talismãs e rascunhos ficam salvos localmente no navegador, com cópia isolada por sessão anônima assinada quando o servidor local está ativo.
- **Fontes e limites:** base sincronizada da [MHDB Wilds API](https://docs.wilds.mhdb.io/) e regras documentadas em [docs/DATA-SOURCES.md](docs/DATA-SOURCES.md) e [docs/production-readiness/01-motor.md](docs/production-readiness/01-motor.md).
- **Licença:** código original sob licença **MIT** ([LICENSE](LICENSE)). Ativos de terceiros documentados em [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
