# Bloco 1: auditoria e validação do motor de dano

Auditoria: **25 e 26/09/2026**. Motor entregue: **2026.09.25.1**.

## Parecer

**Validação parcial. O projeto ainda não pode afirmar precisão completa no patch atual nas 14 armas.**

O núcleo aritmético foi corrigido e ganhou referências numéricas independentes. Foram exercitadas as 14 classes, as 42 rotações expostas pela API e as 448 alternativas do cache. Isso prova integração e consistência das regras testadas; **não prova que todos os MVs, multiplicadores específicos e tempos locais reproduzem o jogo atual**.

Última atualização localizada no feed oficial consultado: **1.042.00.02, de 14/08/2026**. O snapshot MHDB tem revisão **2026-04-15T01:28:18+00:00**, também retornada pelo endpoint de versão na consulta. Revisão da API não é versão do jogo. A origem secundária dos ataques declara mudanças da 1.040 ainda não conferidas. Não há capturas de ensaios neste repositório que certifiquem as rotações na 1.042.

Nenhuma build foi removida, substituída ou regenerada. Nenhum login, redesign, nova busca de otimização ou implementação de outro bloco foi realizado.

## Escopo e método

Leitura anterior às alterações: `README.md`, `docs/DATA-SOURCES.md`, `docs/ARCHITECTURE.md`, `docs/VALIDACAO-EVOLUCAO.md`; modelos, importação e catálogo; `app/engine.py`, `app/combat_rules.py`, `app/artian_rules.py`, `app/rotations.py`; consumidores no comparador/otimizador, carregamento de cache e testes. A apresentação de raw/elemento foi rastreada em `static/js/app.js` e `static/js/experience.js`, sem editar a interface.

Stack relevante: Python 3.14, FastAPI, Pydantic, catálogos JSON e frontend JavaScript. Os cálculos são funções Python. Não há necessidade de alterar banco, autenticação ou deploy neste bloco.

- **Implementado (I):** existe caminho executável e teste da regra. Não significa validação experimental de todos os parâmetros.
- **Aproximado (A):** média de uptime, hipótese de estado, dado legado ou tempo não medido.
- **Ausente (M):** não há modelo suficiente. Não foi preenchido com números inventados.
- Referências numéricas usam entradas sintéticas controladas e expectativas calculadas fora das funções/tabelas de produção, com regras atribuídas a fontes independentes.
- Testes de API/cache certificam integração, não o comportamento do jogo. Outra calculadora foi usada para rastrear origem e divergências, nunca como prova definitiva.

## Fontes e versões

Consultas: **25–26/09/2026**. Páginas comunitárias sem versão declarada não foram promovidas a fontes certificadas para o patch atual.

| ID | Fonte e URL | Versão/data | Uso e ressalvas |
| --- | --- | --- | --- |
| S1 | [Capcom: anúncio oficial na Steam](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1840944183778483) | 1.042.00.02; 14/08/2026, 03:26:59 UTC | Identifica a atualização localizada. Anúncio de correção de desempenho, não tabela de dano. |
| S2 | [MHDB: documentação](https://docs.wilds.mhdb.io/), [Handicraft](https://docs.wilds.mhdb.io/#handicraft), [habilidades](https://wilds.mhdb.io/en/skills), [versão](https://wilds.mhdb.io/version) | Revisão 2026-04-15T01:28:18+00:00; sem vínculo explícito com patch | Contrato raw/display, extensão de fio e descrições numéricas. Ailments e motion values são declarados não implementados. |
| S3 | [Wiggler: Intermediate Damage Calculation](https://wiggler.pet/other/guides/intermediate_damage_calculation) | Guia de Wilds sem patch fixado | Fórmula por golpe, percentuais/fixos, afinidade negativa, status, shelling e Echo Waves. Há divergências internas de afiamento. |
| S4 | [Wycadémie: habilidades de Wilds](https://lescarnetsdelawycademie.fr/skills-wilds/) | Página atualizável, sem revisão de jogo fixada | Tabelas por classe de Burst, Coalescence, Critical Element/Status, Charge Master, absorção, munições e Artillery. |
| S5 | [Phantom Brawlers: Artian](https://www.phantombrawlers.com/mhwilds/Artian) | Contém Gogma/TU4; sem certificação explícita para 1.042 | Valores por classe de infusão, foco e reforços; consultados fatos numéricos pontuais. |
| S6 | [Wycadémie: armas Gogmazios](https://lescarnetsdelawycademie.fr/gogmazios-weapons/) | Gogma/TU4; sem patch fixado | Corrobora foco, quantidade e repetição dos reforços. Exemplo genérico não substitui tabelas por classe. |
| S7 | [Origem secundária dos ataques](https://github.com/chanleyou/mhwilds-calculator/tree/bf5f6cf78386e374ee5d15c8d9193ff31532e8b1/src/data/attacks), [README da mesma revisão](https://github.com/chanleyou/mhwilds-calculator/blob/bf5f6cf78386e374ee5d15c8d9193ff31532e8b1/README.md) | Commit `bf5f6cf78386e374ee5d15c8d9193ff31532e8b1`, 15/01/2026 | Repositório em manutenção; mudanças 1.040 não marcadas como conferidas. Usado para proveniência, não certificação de MVs. |

A página direta de atualizações da Capcom retornou HTTP 403; foi usado o feed oficial do publicador na Steam. Não foi obtida evidência experimental independente para resolver todos os MVs legados.

### Divergências

1. O cabeçalho das rotações locais afirmava origem na 1.040. S7 não sustenta isso. Corrigido o cabeçalho e fixado o link em commit, sem `main` mutável.
2. **DB Sixfold:** `14 + 22 + 80` foi agrupado em três contatos elementais locais. S7 decompõe os dois últimos ataques em múltiplos contatos. Igualar soma física não preserva elemento/fio. Blade Dance e Screw Slicer também divergem. Não troquei sequências com base apenas em outra calculadora. **DB não está certificada para ranking elemental.**
3. **Fio:** S3 apresenta branco raw 1,32 em uma seção e 1,25 em outra; azul elemental 1,05 difere do 1,0625 local. Não substituí a tabela existente por outra contraditória. A validação completa das cores permanece aberta, especialmente azul elemental.
4. **Status Attack:** fontes secundárias divergem; foi usada a descrição numérica explícita de S2, com a ressalva de versão registrada.
5. **Gog:** foco/reforços genéricos de S6 não valem igualmente para todas as classes. S5 distingue foco de CB para status (+40 exibidos) e elemento (+50).
6. Nenhuma fonte consultada comprova os 42 tempos locais. Não foram apresentados como frames medidos nem substituídos por estimativas novas.

## Unidades e resultados

`Weapon.raw` é ataque verdadeiro, importado de `damage.raw`, sem multiplicador visual. Exemplo de S2: Hope Blade I, 90 internos e 432 exibidos. A interface apresenta Raw/ataque base; o modelo não mantém `raw_display`. Não reaplicar 4,8 ao dano de GS.

Multiplicadores visuais observados nas armas Hope de S2, apenas para interpretação: GS 4,8; LS 3,3; SnS/DB 1,4; Hammer 5,2; HH 4,2; Lance/GL 2,3; SA 3,5; CB 3,6; IG 3,1; LBG 1,3; HBG 1,5; Bow 1,2. Não foram introduzidos na fórmula.

`element_val` é interno; `element_display = element_val * 10`. Os **1.188 registros** foram comparados ao snapshot bruto, sem desvio de raw ou elemento/display. Isso valida a importação, não a atualidade de cada arma no jogo. O snapshot não contém specials múltiplos/ocultos; o importador usa o primeiro special.

Para um contato convencional, sem fatores especiais:

```text
Raw esperado = raw com bônus * fio raw * MV/100 * HZ físico/100 * crítico esperado
Elemento = elemento interno com bônus * fio elemental * multiplicador do golpe * HZ elemental/100
Crítico esperado, afinidade >= 0 = 1 + afinidade * (multiplicador crítico - 1)
Crítico esperado, afinidade < 0  = 1 + afinidade * 0,25
```

Afinidade é fração limitada a [-1,1]. Golpes sem crítico não recebem esse fator. Elemento crítico exige habilidade; Charge Master exige contato carregado e uptime informado. Shelling/frasco não devem herdar automaticamente a fórmula de lâmina.

| Campo | Significado |
| --- | --- |
| `total_raw`, `total_element` | Atributos internos após bônus modelados. |
| `effective_raw`, `effective_element` | Indicadores intermediários com fio e, no raw, afinidade média. Não são dano por golpe. Status não recebe fio. |
| `hits_breakdown[].expected_damage` | Dano esperado da linha inteira. Quando `hit_count > 1`, inclui todos os contatos agrupados; dividir pela contagem para um contato homogêneo. |
| `physical_damage`, `crit_physical_damage` | Cenários normal/crítico positivo da linha, não parcelas para somar. Crítico negativo é aplicado separadamente ao esperado. |
| `damage_per_cycle` | Soma dos contatos; não inclui dano de procs de status não modelados. |
| `practical_dps` | Dano da rotação / tempo estimado. Não é medição de caçada. |
| `damage_per_min` | `practical_dps * 60`, sem simulação adicional de um minuto. |
| `sustained_dps` | Projeção de perda de fio no horizonte informado, sem afiar/recuperar recursos. Nos projéteis pode coincidir com DPS estimado porque não há recarga simulada. |
| `sustained_damage_per_cycle` | Dano médio de uma rotação nessa projeção, não total da caçada. |
| `combined_score` | Índice heurístico dano/sobrevivência, não dano nem percentual real de eficiência. |

API: `calculation_status="partial"`, `motion_values_verified=false`, `status_damage_modeled=false`, `sustained_model="sharpness_only_no_recovery"` e notas por classe. Nomes antigos foram mantidos para compatibilidade. Zero no campo legado de dano de status significa parcela não incluída, não ausência de dano de Explosão/Veneno no jogo.

As saídas são arredondadas a partir de valores fracionários esperados. O arredondamento por componente/contato do jogo não está certificado; um único crítico observado não deve ser comparado diretamente à média esperada.

## Correções implementadas

Linhas da versão entregue. Não foram alterados resultados numéricos esperados dos testes existentes.

| Correção | Local | Evidência/teste |
| --- | --- | --- |
| Percentuais de raw multiplicados antes dos bônus fixos; HH deixa de ser parcela fixa | `app/engine.py:569` | S3; 200 × 1,04 × 1,15 × 1,30 + 9 + 10 = 329,96. Magnitude de 5% do HH continua hipótese manual. |
| Coalescence não multiplica bônus elementais fixos | `app/engine.py:619`, `app/combat_rules.py:38` | S3/S4; teste Fire Attack + Burst + Coalescence. |
| Tabela própria para Poison/Paralysis/Sleep/Blast Attack | `app/combat_rules.py:38` | S2; 5% + 1, 10% + 2, 20% + 5 internos. Doze casos. |
| Critical Status por classe, Charge Master e afinidade elegível por contato | `app/combat_rules.py:45`, `app/engine.py:701` | S4; status sem multiplicador de fio. |
| Removido dano artificial de Explosão a partir de estrelas | `app/engine.py:725`, `app/models.py:495` | S3; faltam limiares e dano por proc. Mantido acúmulo estimado. |
| Razor Sharp 10/25/50%, Master's Touch 80% no crítico, Polish sem perda durante uptime | `app/engine.py:280` | S2; custo fracionário/zero. Combinação usa expectativa probabilística, não eventos simulados. |
| Handicraft respeita extensão de cores por arma e muda fio inicial | `app/engine.py:256`, `app/engine.py:524` | Contrato S2, exemplo [1,4]. Metadado ausente não cria barra extra. |
| Traços explícitos de munições/flechas e bônus corretos no breakdown inteiro | `app/rotations.py:15`, `app/engine.py:678` | S2/S4: famílias 5%, Rapid Fire 5%, Special Ammo 10/20%. Qualificação fina dos movimentos legados requer ensaio. |
| Airborne 10% em contatos marcados aéreos | `app/engine.py:686` | Valor explícito S2; sem heurística pelo nome traduzido. Traços atuais cobrem a rotação aérea de IG. |
| Constitution/Stamina Surge não aceleram animações | `app/engine.py:625`, `app/engine.py:750` | S2: vigor não é velocidade. Benefício sustentado ainda ausente. |
| Burst Boost exige Burst ativo além das peças | `app/engine.py:563` | S2; testes 1/2/4 peças, com/sem Burst. |
| Echo Wave Slash de HH sem multiplicador/consumo de fio | `app/rotations.py:23` | S3 corroborada por S7; MV/tempo ainda legados. |
| Foco de CB Gog distingue status/elemento | `app/artian_rules.py:29`, `app/models.py:200` | S5; status 150 + 40 = 190, elemento 300 + 50 = 350 exibidos. |
| MV zero respeitado; negativos/não finitos rejeitados | `app/models.py:433`, `app/engine.py:138`, `app/engine.py:667` | Contrato matemático. Corrigido também no escore-base consumido pelo otimizador. |
| Proveniência e limitações explícitas; remoção de falsas indicações de efeito modelado | `app/rotations.py:1`, `app/engine.py:173`, `app/engine.py:742` | Conferência dos caminhos executáveis. Sem redesign. |

## Cobertura por arma

Todas: **I** no núcleo aritmético/HZ configurado; **A** em MVs, tempos e uptimes. Nenhuma certificada ponta a ponta no patch atual. Três rotações por classe preservadas.

| Arma | Implementado | Aproximado | Ausente/incompatibilidade |
| --- | --- | --- | --- |
| Espadão (GS) | Corte, Tackle contundente, carga, Critical Element/Charge Master | TCS/offset e primeiro acerto pressupostos; Focus global | Frames, hitstop, preparação e ocorrência do offset; fio/crítico do Tackle requerem confirmação |
| Espada Longa (LS) | Corte, Crimson/Helmbreaker/Iai, afinidade por contato | Vermelho e counter bem-sucedido; Quick Sheathe global | Gerar/manter aura, falhas, cancelamentos, hitstop |
| Espada e Escudo (SnS) | Corte/contundente, escudo sem consumo de fio, Charged Chop | Perfect Rush ideal e modificadores legados | Guarda, KO, movimentação, qualificação completa das cargas |
| Duplas-Lâminas (DB) | Núcleo e bônus por classe | Contatos agrupados distorcem elemento/fio e divergem da origem | Sequências elementais validadas, vigor, modos Demon/Archdemon |
| Martelo | HZ contundente e cargas | Mighty/Big Bang/offset completos | KO, exaustão, interrupções, frames, posicionamento |
| Berrante (HH) | Contundente; Echo Wave Slash como corte sem fio | Performances e bônus externo genérico de 5% | Canções/bolhas, Self Improvement, ondas elementais, manutenção das melodias |
| Lança | Corte, carga, contra-ataques | Counter ideal e janela ofensiva | Espera pelo ataque, bloqueio/recuo, dano residual |
| Lançarma (GL) | Shell separado, fogo fixo, Artillery, sem crit/HZ físico no shell | Exemplos Normal/Long/Wide Nv.3 independentes da arma | Tipo/nível real, Gog Nv.4, recarga/capacidade, fio real dos shells, Wyrmstake completo |
| Transmachado (SA) | Sequências de axe/sword e fórmula comum | Rapid Morph só no tempo global; explosões legadas | Multiplicadores de phial, amplificação, medidores, bônus específico de dano de morph |
| Lâmina-Dínamo (CB) | Impact phial sem crit/fio/HZ físico, Artillery | AED/SAED de impacto e ticks fixos | Element phial usa indevidamente sequência de impacto; carga de escudo/espada, frascos disponíveis |
| Glaive Inseto (IG) | Corte, carga marcada e Airborne na sequência aérea | Triple Up pressuposto nos movimentos | Kinsecto, bônus/renovação de extratos, vigor, recursos de Rising Spiral |
| Fuzilarco Leve (LBG) | HZ projétil, sem fio, Normal/Pierce/Rapid Fire | Ticks/acertos/Chaser fixos | Munição elemental/status, distância, recarga, capacidade, compatibilidade da munição e medidor |
| Fuzilarco Pesado (HBG) | HZ projétil, sem fio, Normal/Spread/Wyvernheart | Pellets/ticks e aquecimento pressupostos | Munição elemental/status, distância, recarga, capacidade, cooldown/ignição |
| Arco | HZ projétil, sem fio, bônus de flechas, crítico elemental/carga | Carga e contatos de Tracer fixos | Revestimentos, distância, vigor, medidor e viabilidade do loop |

Armazenar/exibir `ammo`, `phial`, `melody`, `coatings` ou `kinsect_level` não implementa seu efeito. Avisos antigos que sugeriam suporte completo a frascos/extratos foram corrigidos.

### Tempos legados, não medidos

Nenhum dos tempos abaixo foi alterado ou promovido a referência experimental.

| Classe | IDs e segundos |
| --- | --- |
| GS | `gs_tcs` 8,2; `gs_offset` 4,8; `gs_tackle_tcs` 5,7 |
| LS | `ls_red_loop` 4,7; `ls_helmbreaker` 5,5; `ls_iai` 3,5 |
| SnS | `sns_lateral` 5,3; `sns_perfect_rush` 5,9; `sns_counter` 3,2 |
| DB | `db_blade_dance` 7,0; `db_sixfold` 3,7; `db_perfect_evade` 3,9 |
| Hammer | `hammer_mighty` 4,8; `hammer_big_bang` 7,2; `hammer_offset` 4,3 |
| HH | `hh_echo` 5,2; `hh_performance` 5,7; `hh_offset` 4,1 |
| Lance | `lance_triple` 3,0; `lance_charge_counter` 3,8; `lance_retribution` 3,5 |
| GL | `gl_full_burst` 5,1; `gl_wyrmstake` 6,0; `gl_shell_loop` 4,0 |
| SA | `sa_morph_loop` 4,2; `sa_full_release` 5,2; `sa_offset` 4,4 |
| CB | `cb_savage_axe` 5,0; `cb_aed` 4,5; `cb_saed` 6,2 |
| IG | `ig_tornado` 4,4; `ig_rising_spiral` 5,2; `ig_aerial` 4,8 |
| LBG | `lbg_normal` 2,0; `lbg_rapid` 2,3; `lbg_pierce` 2,5 |
| HBG | `hbg_normal` 3,0; `hbg_spread` 3,2; `hbg_wyvernheart` 5,0 |
| Bow | `bow_power_loop` 3,2; `bow_tracer` 3,4; `bow_thousand` 4,2 |

## Condicionais, sets, alvo e Gog

### Habilidades

- Testados: afinidade positiva/negativa/teto, Critical Boost, WEX no limiar físico 45 e por contato. Wound é estado informado: não cria automaticamente um HZ de ferida. Elegibilidade exata por estado do monstro ainda requer confirmação.
- Agitator, Burst, Maximum Might, Peak Performance, Counterstrike, Coalescence, Latent Power, Antivirus, Foray, Resentment, Adrenaline Rush, Offensive Guard, Ambush e Heroics usam uptimes médios. Burst presume bônus completo, sem contar golpes de ativação/expiração.
- Produto de médias e limite de afinidade aplicado após a média não equivalem a simular buffs correlacionados. Falta sequência temporal, probabilidade de acerto e janela de fraqueza.
- O catálogo contém 25 skills de set e 17 de grupo. Limiares/fontes são agregados; efeito inativo é excluído. **Reconhecer peças não implementa o buff.**
- Doshaguma: +10/+25 com ativação presumida durante toda rotação `offset`; faltam Power Clash, duração e primeiro golpe. Ebony Odogaron: +8/+18 condicionado a Burst. Gogmapocalypse: +10/+20 internos e uptime de Agitator como aproximação, sem certificação de magnitude/cronologia por arma.
- Os outros sets/grupos não têm efeitos particulares de dano implementados. Frenzy basal, efeitos adicionais de sets, restauração de fio e bolhas não podem ser inferidos da lista de habilidades ativas.
- Comida, sementes, pó, manto, Fortify e HH são entradas externas. Fortify usa stacks informados, sem validar desmaio; manto/HH mantêm magnitudes genéricas. Não há simulação de elegibilidade/inventário.
- Guard/Guard Up/Divine Blessing/Stun Resistance entram em índice heurístico, não simulação defensiva validada. Constitution/Stamina Surge são informativas até haver modelo de vigor.

### Hitzones

HZ 20 significa fator 0,20, não dano fixo, estrela ou chance de status. O contato escolhe corte/contundente/projétil; o elemento escolhe seu próprio HZ. Shell/impact phial ignoram HZ físico; fogo do shell ainda usa HZ de fogo.

`Media_Ponderada` é nome legado: `sync_mhdb.py:283` calcula média aritmética das linhas de partes, não pesos reais de acerto. Gogmazios tem seis linhas `hide` de HZ dragão 55, além de partes com 0/5. A média mistura partes/estados e não prova superioridade universal de dragão. Para ensaio, usar parte conhecida.

Partes com nomes duplicados selecionam a primeira correspondência. Não há ciclo completo de estados, distribuição de acertos nem diferenças de missão/AT. O núcleo foi validado com HZ controlado; **não foram certificados todos os HZ/estados dos 34 monstros contra o jogo**. Catálogo não foi alterado sem evidência.

### Gog

Implementados: foco, reforços por classe, soma exibida antes da conversão, até cinco rolls/dois idênticos, skills de arma contando para set. Exemplo de S5: GS 480 + Element II 90 = **570 exibidos / 57 internos**, não limite máximo de elemento.

Limitações: editor aceita bases manuais e não certifica todas as combinações legais; `capacity_i/ex` não altera DPS; foco em revestimentos/munição/frascos está incompleto. Gog customizada guarda só cor superior/unidades, sem barra inferior completa nem extensão Handicraft. A projeção usa os segmentos conhecidos e depois vermelho, portanto não é previsão confiável de manutenção dessa arma. Legalidade completa de montagem não foi implementada neste bloco.

## Testes de referência

Arquivo novo: `tests/test_motor_reference.py`, **83 casos parametrizados**. Expectativas literais, sem importar tabelas de produção para derivá-las.

| Ensaio | Cálculo independente | Fonte |
| --- | --- | --- |
| Contato | 200 × 1,32 × 1 × 0,5 = 132 raw; 20 × 1,15 × 0,2 = 4,6 elemento; total 136,6 | S3; fixture sintética |
| Afinidade -100% | 132 × 0,75 = 99; Critical Boost não melhora crítico negativo | S3 |
| Percentuais raw | 200 × 1,04 × 1,15 × 1,30 + 9 + 10 = 329,96; saída 330,0 | S2/S3 |
| Elemento composto | 20 × 1,20 × 1,10 + 6 + 8 = 40,4 / 404 exibidos | S3/S4 |
| Status Attack 3 | 20 × 1,20 + 5 = 29 internos, sem fio | S2/S3 |
| Status crítico carregado GS | 24 / 3 × 1,40 × 1,25 = 14 acúmulo, não HP removido | S3/S4 |
| Normal rápido | 200 × 0,10 × 1,05 × 1,05 = 22,05; saída 22,1 | S2/S4 |
| Fio esperado | Razor Sharp 3: 0,5/contato; Master's Touch com 100% afinidade: 0,2; Polish ativo: zero | S2 |
| Handicraft [1,4] | Azul base 50; HC1 azul 60; HC2 azul 60/branco 10; HC5 azul 60/branco 40 | S2 |
| Rotação/DPS/DPM | 3 × 136,6 = 409,8/rotação; tempo sintético 2s: 204,9 DPS e 12.294 DPM | Definição dimensional |
| Gog | GS 480 + 90 = 570 exibidos; CB status foco +40 e elemento +50 | S5 |

Também cobertos: núcleo das 14 classes, HZ por contato, WEX 44/45, limiar de set, inputs imutáveis, contato sem crítico, MV zero/não finitos, snapshot de 1.188 armas e API de 42 rotações. Os MVs 100 e tempos 2s sintéticos não substituem movimentos reais. O teste elemental sintético de bowgun não declara suporte a munição elemental.

### Execução

Baseline: **104 testes Python passando**. Entrega validada em 26/09/2026:

```powershell
python -m pytest -q -p no:cacheprovider
# 187 passed in 11.80s

node --test --test-isolation=none tests/material-plan.test.js tests/planner-state.test.js tests/workspace-state.test.js tests/calculation-state.test.js
# 21 passed, 0 failed
```

Armazenamento temporário: `tests/conftest.py`. A API foi exercitada via FastAPI `TestClient`, não contra o servidor aberto na porta 8012. Esse servidor não foi reiniciado nem houve publicação; um processo já aberto precisa recarregar o código para usar o motor novo. Testes JavaScript verificam estado/persistência/comparação, não inspeção visual completa de botões. Não houve alteração visual. Nenhuma biblioteca foi instalada.

### Preservação e cache

`app/main.py:214` já recalcula em memória resultados de versão antiga. A versão nova aciona esse caminho: mesmas alternativas, reordenadas, com `needs_search_refresh=true`. **Não foi feita nova busca para afirmar que sejam as melhores builds.**

O teste do cache agora exige equipamentos preservados, resultado integral igual ao recálculo, versão atual em memória, slots/requisitos válidos, ordenação e bytes do arquivo intactos. Antes exigia regenerar o arquivo a cada versão. Isso valida o contrato existente sem regravar builds; não troca expectativa numérica para mascarar falha. Permanecem 224 categorias e 448 alternativas.

SHA-256 idênticos antes/depois:

```text
app/game_data.json
0653d4023eee882dd33cdfe2f0435b68eff838ad8a1462d410f756655c69fae9
app/game_data_pt.json
bc5aff71a9cbd821f342b3d70f6e7212f064e0ea31fdee4abc9b3bebc7c2d020
app/meta_build_cache.json
59eedaaeea0c5ec410ab3309efb63a3da9fcc68cd6397f3c4d071f0f10f15ea8
```

## Revisão do diff

A pasta não tem Git. Foram guardadas cópias anteriores e revisadas diferenças unificadas contra `C:\Users\vitor\Documents\Codex\2026-08-23\anal\motor-baseline-20260925`. Sem reset, checkout ou sobrescrita de trabalho externo.

Produção alterada: `app/engine.py`, `app/combat_rules.py`, `app/models.py`, `app/rotations.py`, `app/artian_rules.py`. Testes: novo `tests/test_motor_reference.py` e ajuste do contrato em `tests/test_generated_cache.py`. Documento: este arquivo. `app/main.py`, comparador, algoritmo de busca, frontend, imagens e JSONs de builds não foram alterados neste bloco.

Revisados: unidades, fatores por contato, breakdown, fio zero/fracionário, Handicraft, metadados de cálculo parcial, serialização e versão do cache. As suítes passaram após revisão.

## Validação pendente no jogo

1. **MVs/contatos atuais:** registrar versão, arma, estado, carga, raw, elemento, afinidade, fio e HZ; priorizar DB, SA, CB, HH e GL. Não usar o ranking atual dessas classes como prova de meta.
2. **Frames por ação:** medir começo/fim, hitstop, cancelamento, preparação, recarga e espera pelo counter. Só então substituir tempos/ajustes globais de Focus, Rapid Morph e Quick Sheathe.
3. **Fórmula e arredondamento:** sem buffs, afinidade 0% e 100%, raw/elemento isolados, cores de fio e contatos especiais. Determinar arredondamento antes de adotar tolerância de erro.
4. **Estados/sets:** registrar gatilho, duração, cooldown, limiar e interação com Gog; testar Powerhouse, Hostility e Frenzy isoladamente antes de compor uptimes.
5. **Sustentação:** medir vigor, munições/revestimentos, medidores, frascos, recarga e afiação. Sem isso, a projeção não é DPS real de caçada.
6. **Status/monstros:** obter limiares inicial/incremental/teto, decaimento, duração, dano do proc e escala da missão/jogadores; conferir partes/estados/AT. Não deduzir esses dados de estrelas ou médias.

Cada evidência futura deve incluir URL/captura, origem, data, versão, plataforma/FPS, equipamento, cenário, repetições e diferença entre esperado/observado. **Nenhum teste no jogo foi executado nesta auditoria.**

Resultado: correções e núcleo cobertos por testes, integração operacional; precisão experimental completa e sustentação real pendentes. **O próximo bloco não foi iniciado.**
