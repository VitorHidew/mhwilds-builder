# Wilds Forge: plano de UI/UX orientado à experiência

Data do planejamento: 24/09/2026. Atualização: 25/09/2026. Status: núcleo das etapas 0 a 4 implementado; validação técnica da etapa 5 executada, com pendências de validação humana e cobertura editorial descritas em `VALIDACAO-UI-UX.md`. As observações abaixo preservam a linha de base anterior à implementação.

## 1. Decisão central

Organizar o produto em torno de uma caçada: escolher o alvo, montar ou encontrar uma build, comparar alternativas e reunir materiais. A interface deve sempre deixar claro qual cenário está valendo, o que mudou e qual decisão pode ser tomada agora.

A prioridade é a confiança na decisão. Depois vêm a redução do esforço de edição e o refinamento visual. O diferencial será explicar uma recomendação e permitir transformá-la em equipamento obtido no jogo, preservando o contexto durante todo o percurso.

Este plano complementa `PLANO-EVOLUCAO.md`. A integração técnica anterior permanece; agora o trabalho é tornar essa integração compreensível e consistente para quem usa.

## 2. Escopo e método

- Inspeção da interface local em `http://127.0.0.1:8012/`, incluindo navegação, visão geral, cenário, montador, otimizador, comparador, materiais, registro e configurações.
- Observação em viewport desktop de 1440 x 900 e em largura estreita; a validação responsiva completa fica definida adiante.
- Leitura de `static/index.html`, `static/css/app.css`, `static/js/app.js`, `static/js/planner.js`, dependências e documentação de evolução.
- Stack relevante: Python/FastAPI/Pydantic, HTML/CSS/JavaScript sem framework de frontend, persistência local no navegador e APIs existentes. Não adicionar cadastro ou login.
- Referências externas de interação, acessibilidade e ferramentas do domínio, listadas na seção 14.
- Esta é uma avaliação heurística com evidências de código e interface, não uma pesquisa com usuários. Não foram medidos tempos reais de conclusão, conversão ou conformidade WCAG integral.
- Não foi refeita a auditoria matemática nem executada novamente a suíte funcional nesta etapa de planejamento. Os resultados anteriores estão em `VALIDACAO-EVOLUCAO.md`.

## 3. O que preservar

- Montagem livre, otimização, comparação de combos, condições de combate, materiais e wiki integrados.
- Duas alternativas por categoria, histórico/proveniência das recomendações e distinção entre estimativas e regras modeladas.
- Comparação recalculada no cenário compartilhado sem sobrescrever os snapshots salvos, já separada em `planner.js:1` e `planner.js:45`.
- Proteção contra respostas antigas em comparação e otimização; os estados visuais novos devem refletir essas proteções.
- Ícones e imagens reais do jogo; temas por bioma e nomes localizados, sem gerar substitutos para armas ou armaduras.
- Habilidades com origem por peça e limiar de ativação; separação entre adornos de arma e armadura; transcendência e reforços Gog.
- Uso sem conta, backup/importação e estoque de materiais persistente. A troca de interface não pode apagar dados existentes.

## 4. Problemas observados e prioridade

P0 significa que a experiência pode induzir uma decisão errada ou comprometer a continuidade; P1 é atrito importante no fluxo; P2 é refinamento. Não são classificações de segurança.

| ID | Prioridade | Evidência | Efeito na experiência | Decisão proposta |
| --- | --- | --- | --- | --- |
| UX-01 | P0 | Na sessão inspecionada, o topo mostrava Ajarakan enquanto o otimizador trabalhava com Arkveld. `planner.js:102` lê o cenário global; `app.js:955` altera o alvo do preset; `app.js:3178` usa o alvo do otimizador. | A pessoa pode interpretar os números como se fossem do mesmo alvo. Não é prova de erro na fórmula. | Cenário único por padrão; qualquer cenário diferente deve aparecer como exceção explícita com ação para aplicar ou recalcular. |
| UX-02 | P0 | `app.js:1212` troca classes de tela sem atualizar URL ou histórico. O recarregamento observado retornou à visão geral. | Perda de localização e dificuldade para retomar o trabalho. | Rotas leves, histórico do navegador e rascunho local versionado, separados das builds salvas. |
| UX-03 | P1 | Treze destinos laterais em `index.html:33`, quatro etapas em `index.html:52`, seis atalhos repetidos na visão geral em `index.html:70` e `index.html:90`. | Três caminhos concorrentes para a mesma tarefa; “Build” abre o otimizador, não o montador. | Uma navegação principal; Montar e Recomendar como modos da mesma área Build. |
| UX-04 | P1 | A visão geral começa com hero, texto introdutório, três botões e métricas zeradas (`index.html:64`). | Grande parte da primeira tela não entrega uma decisão útil. | Início operacional: caçada atual, rascunho recente e ação principal; sem hero promocional. |
| UX-05 | P1 | Montador com galeria de sete peças e seletores separados; oito comandos além do nome em `index.html:124`. Área com cerca de 1771 px de altura no estado desktop observado. | Imagem, edição e consequência ficam distantes. | Uma linha editável por peça, com imagem, nome, habilidades e encaixes juntos. |
| UX-06 | P1 | `saveCurrentBuild()` navega ao comparador (`app.js:1833`); “Salvar Resultado” também (`app.js:1889`). | Salvar muda de contexto sem que o comando indique isso; os dois tipos de registro são pouco distintos. | Salvar mantém a tela. Comparar é uma ação separada; snapshot de cálculo fica em opções avançadas. |
| UX-07 | P1 | Painel Gog longo antes dos critérios/resultados; “Usar arma perfeita” em `app.js:3300`; nomes internos e instruções de reforço aparecem no resumo. | A explicação antecede a escolha e sugere certeza maior que uma busca limitada permite. | Resultados primeiro; detalhes Gog dentro da alternativa; linguagem “alto RNG” e “RNG reduzido”. |
| UX-08 | P1 | Comparador vazio ainda exibe controles de combos, tabelas e áreas de resultado. `index.html:678` e `index.html:706`. | Não fica claro o que falta para começar; comandos sem insumos parecem quebrados. | Estado vazio único com seleção de builds; revelar análise quando houver dados válidos. |
| UX-09 | P1 | Na tela de cenário: fallback de imagem “A”, partes com nomes misturados, opções “exposta” repetidas e 19 campos de uptime. `index.html:334` em diante. | Dificuldade para reconhecer o alvo, a parte e as condições realmente relevantes. | Imagem/fallback identificáveis, partes com estado, condições agrupadas e habilidades equipadas em primeiro plano. |
| UX-10 | P1 | Texto “média ponderada ... padrão realista” em `index.html:284`; opção “Média das partes (aproximação)” em `app.js:1232`. | A mesma configuração recebe duas promessas diferentes. | Vocabulário único; explicar que média de partes não representa automaticamente a distribuição real dos golpes. |
| UX-11 | P1 | Vários labels sem `for` em cenário e configurações; menu usa `li` com `onclick` (`index.html:33`); barra de etapas sem `aria-current`. | Associação de campos e navegação atual insuficientemente explícitas para tecnologias assistivas. | Elementos semânticos, labels associados, foco visível, retorno de foco e identificação da tela atual. |
| UX-12 | P1 | No modo estreito, idioma/bioma ocupam o topo e a navegação horizontal fica parcialmente fora da área visível. | O acesso às tarefas principais exige descobrir uma rolagem lateral. | Navegação móvel própria, sem transportar a lateral desktop inteira para o topo. |
| UX-13 | P2 | Nomes longos truncados na galeria; `app.css:440` aplica elipse. Algumas partes, habilidades e valores técnicos continuam em inglês no modo PT. | Equipamentos parecidos ficam difíceis de distinguir; alternância de idioma perde credibilidade. | Nome completo na seleção/detalhe; dicionário único de apresentação, mantendo IDs estáveis. |
| UX-14 | P2 | Lista vazia com duas mensagens equivalentes e “Limpar Lista” destacado (`index.html:102`); configurações aproximam limpar e backup (`index.html:838`). | Ruído e risco de comando acidental. | Estado vazio orientado à próxima ação; ações destrutivas em grupo separado, com confirmação contextual. |

Observação de entrega: a barra de etapas apareceu com estilos nativos no navegador (fundo RGB 240/240/240), embora `app.css:789` contenha regras para ela. Validar versão servida/cache antes de atribuir a causa à ausência de CSS. A reestruturação não deve esconder esse diagnóstico.

## 5. Jornadas prioritárias

| Jornada | Entrada | Caminho principal | Resultado esperado |
| --- | --- | --- | --- |
| Encontrar uma build | Arma, progressão, alvo e objetivo | Recomendar > escolher uma das alternativas > ajustar | Build viável, com custo de RNG, conforto e condições compreensíveis. |
| Ajustar uma build conhecida | Rascunho ou build salva | Montar > trocar peça/adorno > avaliar diferença > salvar | Mudança reversível e impacto visível sem perder o restante da montagem. |
| Escolher entre alternativas | Duas ou mais builds | Comparar > fixar referência > escolher combo/contexto | Entender quanto muda e quais diferenças justificam a escolha. |
| Jogar e farmar | Build escolhida | Materiais > somente faltantes > atualizar estoque | Lista legível no celular e progresso persistente. |
| Esclarecer uma dúvida | Habilidade, HZ, material ou equipamento | Abrir definição contextual > voltar à tarefa | Entender a regra sem perder seleção, rolagem ou rascunho. |

Hipótese de uso: desktop para montagem e análise detalhada; celular para consulta e farm, mas todas as ações essenciais devem funcionar nos dois. Validar essa hipótese em teste com usuários.

## 6. Arquitetura de informação

Navegação principal no desktop: **Caçada**, **Minhas builds**, **Biblioteca**. Configurações, idioma, tema e backup ficam em uma área utilitária compacta. A página inicial é a própria Caçada, com retomada do trabalho anterior.

Dentro da Caçada: **Alvo | Build | Comparar | Materiais**. São áreas acessíveis em qualquer ordem, não um assistente que bloqueia o usuário experiente.

Dentro de Build: controle segmentado **Montar | Recomendar**. Editores Gog e de talismã abrem a partir do equipamento correspondente. O inventário de talismãs permanece acessível também na Biblioteca. Sugestões entram junto da build a que se referem; Fontes & Limites permanece como destino da Biblioteca e como detalhe contextual dos cálculos.

No celular: navegação inferior **Caçada | Builds | Biblioteca**, com os quatro destinos da Caçada em uma linha curta no conteúdo. Preferências ficam no menu utilitário. Evitar mais uma fileira concorrente de atalhos.

### Contrato de contexto

- A caçada guarda arma/classe, progressão, monstro, parte/estado, ferida, condições e estratégia de combo. Uma barra compacta expõe os campos decisivos e permite editá-los.
- O rascunho de equipamentos é independente da caçada. Trocar de alvo pode recalcular a build, mas não troca suas peças silenciosamente.
- A biblioteca guarda snapshots explícitos; recalcular no cenário atual não altera os originais.
- Ao abrir preset com outro alvo/condição, mostrar a diferença e oferecer “Usar cenário da build” ou “Recalcular na caçada atual”. Não perguntar novamente quando os contextos forem idênticos.
- Cada resultado carrega uma assinatura do cenário, versão do motor e estado de atualização. Resultado antigo nunca aparece como atual durante uma nova requisição.
- Alterações pequenas de peça recalculam automaticamente com atraso curto; mudanças de restrição de busca exigem o comando Recomendar. Não reiniciar otimizações caras a cada tecla.
- Rascunho salvo automaticamente não substitui a build nomeada. Falhas de armazenamento devem ser visíveis; não anunciar sucesso antes da persistência.

### Esquema de layout proposto

```text
DESKTOP
Wilds Forge       Caçada / Minhas builds / Biblioteca       Preferências
Espadão | RC 100+ | Arkveld | Cabeça | Realista               Editar alvo
Alvo              Build              Comparar               Materiais

Montar / Recomendar                         Nome da build       Salvar
-----------------------------------------------------------+----------
Arma       imagem + nome completo + atributos + encaixes    | Resultado
Elmo       imagem + nome completo + habilidades + encaixes  | DPS
Peitoral   imagem + nome completo + habilidades + encaixes  | Rotação
Braços     imagem + nome completo + habilidades + encaixes | Diferença
Cintura    imagem + nome completo + habilidades + encaixes | Habilidades
Pernas     imagem + nome completo + habilidades + encaixes | Validade
Talismã    imagem + nome completo + habilidades + encaixes | Comparar

CELULAR
Wilds Forge                                      Preferências
Espadão / Arkveld / Cabeça                        Editar alvo
Alvo       Build       Comparar       Materiais
Montar / Recomendar
Resultado compacto expansível
Linhas de equipamento ou duas recomendações empilhadas
Comando principal fixo, sem encobrir o conteúdo
Caçada                 Builds                 Biblioteca
```

Esquema estrutural, não mockup visual aprovado. Os números e nomes do exemplo não representam uma recomendação calculada.

## 7. Especificação por área

### 7.1 Início e retomada

- Sem rascunho: campos operacionais para arma, progressão e alvo, com objetivo inicial sugerido e editável. Oferecer Montar ou Recomendar sem uma página promocional intermediária.
- Com rascunho: abrir o último trabalho e exibir sua situação de salvamento. Minhas builds mostra recentes e favoritas, não estatísticas zeradas.
- Manter monstro e arma como sinais visuais reconhecíveis. Evitar imagem decorativa de grande altura quando ainda não há alvo.
- Não mostrar “Cálculo ao vivo” quando a carga inicial falhou ou ainda não existe resultado válido.

### 7.2 Alvo e condições

- Foto real centralizada, sem cortar o monstro, em região sem moldura decorativa. Altura inicial de referência: 220-280 px no desktop e 160-220 px no celular, ajustada ao espaço disponível.
- Nome, variante e estado ao lado dos dados essenciais; no celular, composição vertical compacta. O alvo deve ser reconhecível antes dos detalhes numéricos.
- Tabela de partes com Corte, Impacto, Projétil e os cinco elementos. Destacar a coluna física da classe e a parte selecionada, sem ocultar as demais.
- Ordenação por fraqueza relevante ou nome; nomes de partes repetidas recebem estado distintivo. HZ permanece um valor de hitzone, não uma porcentagem de vantagem entre builds.
- Status em seção separada: dados de veneno, paralisia, sono e explosão com suas unidades e disponibilidade. Ausência de dado nunca vira resistência zero.
- Presets Padrão, Realista e Agressivo próximos das condições; edição individual muda o estado para Personalizado. Mostrar inicialmente as habilidades presentes e permitir consultar todas.
- Separar condições do monstro, condições das habilidades e consumíveis. Uptime fica com nome oficial, valor numérico editável e unidade %, sem exigir conhecimento de IDs internos.
- Definições de HZ, estado e habilidade abrem ajuda contextual com fonte, sem abandonar a caçada.

### 7.3 Montador livre

- Cada peça é uma unidade editável: imagem com dimensão estável, nome legível, slots, habilidades e transcendência na mesma linha. Peça vazia é uma linha compacta de seleção, não uma foto gigante vazia.
- Seletor com pesquisa dentro do próprio controle; busca por nome, habilidade e alias PT/EN. Ordenação alfabética por locale, com filtros de categoria/raridade/slot quando aplicáveis.
- Ao pesquisar, não aplicar automaticamente a primeira opção. Prévia mostra ganhos/perdas e confirmar aplica; cancelar preserva a peça.
- Adornos inválidos nunca aparecem como opções válidas. Após trocar uma peça, listar os adornos removidos por incompatibilidade e oferecer desfazer a troca inteira.
- Transcendência é toggle por peça elegível, com antes/depois dos slots. Não duplicar todo o catálogo com variantes artificiais.
- Gog abre editor contextual: atributos finais, reforços, duas habilidades e sinergia com o set. Talismã permite alternar entre catálogo, inventário e edição, sem perder a build.
- Resumo de resultado acompanha a edição: DPS estimado, dano por rotação, duração e diferença para a versão anterior. DPM, EFR e decomposição ficam em detalhes.
- Habilidades em linhas compactas: ícone oficial, nome, nível/limite, origens por peça e condição. Inativas usam texto e estado visual discreto, sem depender apenas de cinza; limiar de set aparece junto da contagem.
- Uma ação primária Salvar; Comparar e Materiais como secundárias. Exportar cartão, snapshot de cálculo e limpar ficam em menu de opções. Desfazer/refazer usam ícones com rótulos acessíveis.
- Build incompleta pode ser editada e analisada, mas recebe estado Parcial; seus números não aparentam uma recomendação final validada.

### 7.4 Recomendações

- Ordem: contexto e objetivo > requisitos essenciais > Recomendar > duas alternativas. Esforço de busca, inventário restritivo, condições detalhadas e travas ficam em filtros avançados, com resumo das restrições aplicadas.
- Progressão mostra equipamentos disponíveis naquela etapa; manter a política existente de Gog nas categorias finais e impedir sugestão Gog antes da disponibilidade indicada pelo RC. Não mudar regras de domínio incidentalmente no redesign.
- Cada alternativa mostra arma, equipamentos, DPS estimado, dano/tempo da rotação, conforto relevante, custo de RNG e requisitos atendidos. Dois blocos repetidos simples, sem cartões dentro de cartões.
- Três ações claras: Usar no montador, Comparar e Adicionar materiais. Salvar recomendação é ação explícita e não muda a tela.
- “Por que esta opção” resume poucas diferenças verificáveis e as condições necessárias. Número de avaliações, fonte, data e versão do motor ficam em detalhe de evidência.
- Alto RNG e RNG reduzido são opções da arma dentro da alternativa. Expor quanto a troca altera dano e quais habilidades deixam de ser garantidas; não chamar uma busca limitada de arma perfeita.
- Sem solução: separar restrição impossível comprovada de “não encontrada no esforço atual”. Exibir requisitos não atendidos e permitir ajustar individualmente, nunca relaxar silenciosamente.
- Cache: identificar resultado pré-calculado e cenário de origem; recalcular quando necessário. A apresentação de resultado rápido não pode simular que uma busca nova terminou.

### 7.5 Comparador e combos

- Estado vazio mostra seleção/importação de builds; com uma build, análise individual e ação para adicionar a segunda. Controles de comparação não disponíveis explicam sua dependência de modo acessível.
- Lista de builds separada da área de análise. Foco inicial em 2-4 selecionadas, mantendo o acesso a todas as salvas e a uma tabela geral quando houver mais.
- Fixar uma build de referência; diferenças percentuais usam sempre essa referência, com denominador definido. Referência sem dano válido produz valor indisponível, nunca infinito.
- Usar o mesmo cenário para comparar, exibindo-o acima da tabela. Trocar alvo/uptime invalida o resultado anterior até o novo cálculo terminar.
- Separar “Mesmo combo” de “Melhor combo por build”. O modo escolhido aparece no cabeçalho e nas linhas; melhor combo é apenas entre os combos disponíveis/modelados.
- Primeiro: dano, DPS, duração, diferença e conforto. Depois: equipamentos/habilidades diferentes. Por último: gráfico, matriz de combos e golpe a golpe.
- Gráfico de barras alinhado com a tabela, e tabela acessível sempre disponível. Não exigir seleção múltipla nativa difícil de descobrir para controlar o gráfico.
- Realçar habilidade cuja contribuição foi medida, nomeando a medida como contribuição isolada. Não somar contribuições como se fossem independentes nem atribuir toda a vantagem entre builds a uma única habilidade.
- Separar ganho estimado de dano de facilidade de execução e sobrevivência. Uma nota composta pode existir como modo adicional, com pesos visíveis, não como definição implícita de melhor build.

### 7.6 Materiais e lista de desejos

- Abrir em materiais faltantes, com acesso às peças de origem. Quantidades necessárias, possuídas e faltantes na mesma linha.
- Filtro somente faltantes, edição numérica e controles de incremento/decremento com alvo de toque adequado; mudanças preservam foco e posição.
- Adicionar uma build apresenta as peças/quantidades incluídas e a política para duplicatas, evitando multiplicar requisitos sem intenção.
- Associar os materiais às builds selecionadas; manter o inventário global do navegador. Decidir por item se as peças são compartilhadas entre builds alternativas ou se serão fabricadas múltiplas cópias.
- Não mostrar 100% de completude sem ressalva quando há receitas ausentes ou upgrades não contabilizados.
- Agrupamento por monstro de obtenção somente quando a base tiver essa relação verificada. Não inferir uma origem pelo nome do material.
- Remover/limpar exige consequência clara; operações reversíveis oferecem desfazer. Lista vazia tem uma única próxima ação, sem botão destrutivo destacado.

### 7.7 Biblioteca, wiki e dados locais

- Pesquisa unificada por categoria, termos localizados e aliases, mantendo índice de resultados separado do artigo escolhido.
- Definições abertas na caçada usam painel lateral no desktop e diálogo de altura disponível no celular. Histórico local de definições permite seguir links e voltar ao ponto anterior.
- Página de habilidade mantém equipamentos associados, expansíveis, com imagem e adicionar aos desejos. Evidência, fonte e limitações ficam estruturadas, sem parágrafos técnicos misturados aos comandos.
- Minhas builds distingue build editável de snapshot de resultado. Renomear, duplicar, comparar e exportar são comandos explícitos; salvar não muda o nome de outra build por acidente.
- Configurações agrupa aparência, idioma e dados. Importação mostra resumo e conflitos antes de aplicar; backup continua disponível sem conta.
- Comunicar armazenamento local no contexto de salvar/backup. Nenhuma mudança visual deve sugerir sincronização entre dispositivos que não existe.

## 8. Direção visual

Conceito: uma mesa de planejamento de Monster Hunter Wilds com hierarquia de ferramenta profissional. A identidade vem de monstros, equipamentos, iconografia real e pequenas diferenças de bioma, não de grandes fundos ornamentais.

### Sistema base

- Estrutura neutra grafite, texto claro e superfícies distinguíveis; evitar banhar tudo em verde, marrom ou azul escuro.
- Papéis iniciais de cor para prototipar: fundo `#151719`, superfície `#202427`, superfície elevada `#2A3033`, texto `#F3F5F6`, texto secundário `#BBC3C9`, borda `#596269`, referência `#8CB9FA`, ganho `#73D3B0`, atenção `#F0C56A`, erro `#FF8C96`.
- Estes valores são candidatos de design, não uma certificação de contraste. Medir todos os pares usados, incluindo hover, seleção, desabilitado e os cinco temas.
- Temas preservam os nomes localizados do catálogo. Planícies Zéfiras: acento dourado moderado; Floresta Escarlate: acento coral; Bacia Oleídea: cobre; Escarpas Frígidas: ciano; Ruínas de Wyveria: jade. Fundo/superfícies podem variar levemente por tema sem prejudicar contraste. Cor de ganho/erro não muda com o bioma.
- Tipografia: corpo 14-16 px, labels 12-14 px, títulos de tela 26-30 px, títulos de seção 18-20 px; espaçamento entre letras zero. Sem tamanho de fonte baseado na largura da viewport.
- Números com alinhamento tabular e precisão coerente com o cálculo. Nome de equipamento quebra linha; não diminuir tudo para caber em uma célula estreita.
- Espaçamento em escala 4/8/12/16/24/32 px. Seções abertas e divisores; cartões apenas para alternativas repetidas, itens ou ferramentas realmente delimitadas. Raios de até 8 px.
- Lucide para comandos genéricos, ícones do jogo para classes, elementos, peças e habilidades. Ícone sem texto precisa de nome acessível e tooltip; nunca confundir ícone decorativo com controle.
- Imagens com proporção e área reservadas, `object-fit: contain` para equipamento/monstro e fundo consistente. Nome fora da área que precisa permitir inspeção do objeto; em miniaturas compactas, legenda pode usar faixa própria sem cobrir características relevantes.
- Fallback: ícone correto de categoria/monstro quando disponível e nome legível. Não usar outra arma como se fosse a peça real. Ausência de foto não bloqueia edição ou cálculo.
- Animação curta apenas para feedback de estado; respeitar movimento reduzido. Sem animações decorativas contínuas na área de análise.

## 9. Estados e comportamento

| Estado | Comportamento esperado |
| --- | --- |
| Carga inicial | Estrutura estável; selecionar dados apenas quando disponíveis; erro de catálogo oferece tentar novamente. |
| Calculando | Resultado anterior marcado desatualizado; status próximo da métrica; nova seleção permanece responsiva. |
| Otimizando | Comando impede duplicação; cancelamento de interface invalida respostas antigas. Cancelar trabalho no servidor depende de suporte real e não deve ser prometido sem ele. |
| Salvo | Confirmação curta com nome e destino; foco permanece onde estava. |
| Rascunho alterado | Indicação discreta; salvar explicitamente continua disponível; recarregar restaura rascunho válido. |
| Erro de rede | Preservar entradas; oferecer repetir; nunca substituir resultado válido por zero como se fosse cálculo. |
| Sem imagem | Fallback estável e nome; sem colapso de layout nem cadeia infinita de novas tentativas. |
| Sem resultado | Mensagem específica à causa e ação aplicável; não exibir tabelas vazias de análise avançada. |
| Requisito inválido | Mensagem no campo, associação acessível e resumo do que bloqueia a busca. |
| Dado aproximado/ausente | Estado textual junto da métrica; fonte e limite no detalhe. Ausente não equivale a zero. |
| Falha ao persistir | Manter rascunho em memória e oferecer exportar; não dizer Salvo. |
| Limpar/excluir | Mostrar o alcance da ação e preservar foco; confirmação para perda permanente, desfazer quando implementado. |

Textos visíveis devem ser nomes, valores, estados e consequências relevantes. Evitar parágrafos que descrevem a própria interface. Ajuda técnica fica contextual e aberta sob demanda.

## 10. Acessibilidade, idiomas e responsividade

- Meta de conformidade: WCAG 2.2 AA, a verificar, não uma declaração de conformidade atual.
- Associar todos os campos a labels; usar links/botões para navegação e ações, `aria-current` para localização e semântica correta no seletor pesquisável.
- Teclado: Tab percorre controles, setas navegam opções, Enter confirma e Escape cancela. Diálogos devolvem foco ao disparador; atualização de valores não rouba foco.
- Foco visível e não encoberto por barras fixas. Mensagens assíncronas relevantes são anunciadas sem reler tabelas inteiras.
- Contraste mínimo aplicável: 4,5:1 para texto comum, 3:1 para texto grande e componentes visuais essenciais. Nunca depender só de cor para ganho, erro, seleção ou habilidade inativa.
- Adotar 44 x 44 px como alvo de projeto para toque. O critério AA de tamanho mínimo da WCAG 2.2 é 24 x 24 CSS px, com exceções; não confundir as duas metas.
- Testar 320, 390, 768, 1280 e 1440 px; zoom de texto de 200%; textos longos em PT e EN; teclado virtual e orientação horizontal.
- Sem rolagem horizontal da página. Tabelas genuinamente bidimensionais podem ter rolagem interna identificável e alternativa resumida, preservando nome e referência visíveis.
- Pesquisa aceita acentos/sem acentos e aliases sem mudar os nomes oficiais exibidos. IDs, enums e chaves de cálculo não são traduzidos.
- Centralizar apresentação PT/EN; testar menus, estados vazios, mensagens, dados, partes, descrições e unidades, não apenas títulos.

Base: [WCAG 2.2](https://www.w3.org/TR/wcag/) e [padrão de combobox WAI-ARIA](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/).

## 11. Implementação em ordem

| Etapa | Entrega | Principais pontos do código | Critério de saída |
| --- | --- | --- | --- |
| 0. Contratos e linha de base | Inventário de telas/ações, estados de caçada/rascunho/snapshot, medidas atuais e casos de teste | `app.js`, `planner.js`, `tests/`, docs de validação | Fluxos atuais registrados; dados pessoais preservados; distinção de cenário definida sem ambiguidade. |
| 1. Contexto e navegação | Barra única de contexto, estrutura Caçada, modos Montar/Recomendar, rota/histórico e retomada | `index.html`, `app.js:1212`, `planner.js:98` | Trocar tela, voltar e recarregar preserva contexto; divergência de preset é explícita; nenhum destino funcional fica inacessível. |
| 2. Sistema visual e montador | Tokens, controles acessíveis, linhas de equipamento, seletor pesquisável, resumo e salvamento previsível | `app.css`, renderização de equipamentos/habilidades e salvamento em `app.js` | Trocar peça/adorno, desfazer, transcender, salvar e reabrir funciona em PT/EN, desktop/mobile; nomes e slots legíveis. |
| 3. Recomendar e comparar | Duas alternativas resumidas, Gog contextual, seleção/baseline, combos e diferenças | Rotinas optimizer/comparator em `app.js`, `planner.js`, contratos de respostas existentes | Resultados no mesmo cenário; alternar combos muda números corretos; 0/1/2/3/6 builds sem quebra; snapshots preservados. |
| 4. Alvo, ajuda e farm | Fraquezas numéricas, uptimes relevantes, imagens estáveis, wiki contextual e materiais faltantes | Tela scenario, wiki/wishlist, `planner.js`, `material-plan.js` | Navegar por definições e voltar sem perda; estoque persiste; receitas incompletas e limites permanecem visíveis. |
| 5. Validação e liberação | Revisão integral de idiomas, temas, acessibilidade, desempenho e jornadas | Toda a interface, testes e documentação | Nenhuma regressão funcional bloqueadora; testes de usuário e revisão visual resolvidos; rollback e backup conferidos. |

Acessibilidade, i18n e mobile entram em cada etapa, não ficam adiados para a etapa 5. Essa última etapa é uma revisão transversal.

Primeira entrega demonstrável: uma caçada com Espadão, alvo e parte explícitos, duas alternativas, edição de uma peça, comparação sob as mesmas condições e materiais da escolha. Usar isso para validar a estrutura; não lançar suporte limitado a essa arma como se cobrisse todas as 14 classes.

Não migrar para React/Vue ou reescrever o motor apenas para viabilizar o redesign. Separar gradualmente estado de caçada, navegação e componentes repetidos no JavaScript existente. Reutilizar contratos e helpers locais antes de criar novos.

## 12. Plano de validação por etapa

### Testes automatizados e regressão

- Manter as suítes Python e JavaScript existentes aprovadas; não alterar expectativas matemáticas para acomodar mudanças meramente visuais.
- Adicionar testes de estado para rota, rascunho, migração de armazenamento e separação entre snapshot e cenário atual.
- Testar igualdade dos payloads de cálculo antes/depois do redesign para entradas equivalentes; exceções exigem mudança funcional documentada.
- Fluxo E2E: definir alvo > recomendar > abrir no montador > trocar peça > salvar > comparar > escolher combo > adicionar materiais > atualizar estoque > recarregar.
- Cobrir progressão sem Gog, endgame Gog, as duas habilidades de arma/set, limites de adornos, transcendência e habilidades de set inativas/ativas.
- Cobrir troca rápida de alvo/combo durante requisição, erro HTTP, catálogo indisponível, cache antigo, armazenamento cheio/bloqueado e importação inválida.
- Testar nomes e entradas importadas como texto, preservando os escapes/validações existentes; componentes novos não devem reintroduzir HTML inseguro.
- Usar dados de teste isolados. Nunca limpar a biblioteca real do usuário para facilitar um teste.

### Inspeção visual e acessível

- Matriz: cinco temas x dois idiomas; telas principais em desktop e celular; casos de nome longo, peça vazia, erro de imagem e dados incompletos.
- Conferir captura de tela e DOM: cortes, sobreposição, foco, ordem de leitura e scroll interno. Complementar automação com teclado e leitor de tela.
- Medir proporção/legibilidade de imagens sem confundir redimensionamento da captura com defeito de renderização do site.
- Confirmar que a versão CSS/JS servida corresponde aos arquivos revisados e que não há controles com estilo nativo inesperado.

### Metas mensuráveis propostas, ainda não medidas

| Área | Meta de aceite |
| --- | --- |
| Contexto | 100% dos resultados apresentados como atuais correspondem ao cenário visível; overrides são explícitos. |
| Continuidade | Nenhuma perda de rascunho válido ao navegar/recarregar nos testes; falha de persistência anunciada. |
| Busca local | Latência p95 de filtragem até 150 ms na base completa, em máquina e navegador registrados; medir antes de virtualizar. |
| Feedback | Estado visual de ação até 100 ms no ambiente de teste; tempo do solver medido separadamente, sem promessa artificial. |
| Layout | Zero sobreposições e zero scroll horizontal da página nos tamanhos definidos; exceção apenas para tabela interna identificada. |
| Primeiro uso | Em teste formativo, pelo menos 4 de 5 participantes chegam a uma recomendação sem ajuda; registrar tempo e obstáculos. |
| Compreensão | Pelo menos 4 de 5 identificam o alvo, o combo e uma razão válida para preferir uma alternativa. |
| Farm | Participantes adicionam a build escolhida e registram estoque sem confundir quantidade necessária com faltante. |

Teste formativo proposto: cinco participantes, incluindo iniciantes no builder e jogadores experientes. Tarefas: escolher build de progressão, ajustar um set endgame, comparar duas rotações, interpretar habilidade inativa e preparar materiais. Perguntar o que esperam antes de agir e o que entendem depois. Essa amostra serve para encontrar problemas, não para declarar significância estatística.

## 13. Riscos e limites

- Uma UI mais clara não torna a fórmula exata. Manter limitações de tipos de golpe, tempos, status e habilidades informativas acessíveis onde afetam a decisão.
- Fotos remotas podem falhar. Reaproveitar assets locais disponíveis com proveniência registrada; qualquer novo espelhamento depende de permissões de uso, sem afrouxar restrições de proxy ou rede.
- Evitar duas interfaces permanentes com estados diferentes. Migração incremental deve ter uma única fonte de dados e retirada planejada dos controles antigos.
- Novos rascunhos precisam de esquema versionado, migração não destrutiva e exportação de recuperação. Limites de armazenamento devem ser testados.
- Não somar automaticamente materiais de duas builds alternativas como se ambas precisassem ser fabricadas. A política de peças compartilhadas precisa ser explícita.
- Tema e idioma não podem alterar valores, ordenação de IDs ou regras do motor. Apenas ordenação de apresentação e textos dependem do locale.
- Não incluir login, sincronização em nuvem, rede social, conquistas ou nova landing page nesta remodelação. O foco é completar as tarefas atuais com menos esforço e mais clareza.

## 14. Referências e aplicação prática

Consultadas em 24/09/2026. As aplicações abaixo são propostas para este projeto, não resultados comprovados de testes nesses sites.

| Referência | Observado/consultado | Aplicação no Wilds Forge |
| --- | --- | --- |
| [Math Hunter: Great Sword](https://www.mathhunter.ca/greatsword.html) | Controles específicos de arma, reforço, transcendência e combos; detalhes técnicos separados. | Preservar profundidade por classe e tornar seus parâmetros acessíveis no contexto da peça/combo. Não copiar toda a densidade para a primeira tela. |
| [Linear: redesign da interface](https://linear.app/now/how-we-redesigned-the-linear-ui) | Relato de refinamento de hierarquia, alinhamento, navegação visual, variáveis de tema e testes de diferentes layouts. | Tokens consistentes, cabeçalhos previsíveis e validação em estados extremos; identidade visual própria de Wilds. |
| [NN/g: Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/) | Separação entre comandos frequentes e opções especializadas. | Critérios essenciais antes dos resultados; evidências e filtros avançados sob demanda, sem esconder restrições ativas. |
| [WCAG 2.2](https://www.w3.org/TR/wcag/) | Critérios de contraste, foco, semântica, reflow e tamanho de alvo. | Critérios de aceite verificáveis para todos os temas e modos. |
| [WAI-ARIA: Combobox](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/) | Contrato de teclado, nome acessível e popup de seleção pesquisável. | Pesquisa dentro do seletor com escolha explícita e cancelamento previsível. |

Limitações da pesquisa: a página oficial de ambientes da Capcom retornou HTTP 403; o extrator do wiki-db exibiu apenas o carregamento, sem o formulário completo. Não foram usados como evidência de comportamento ou de qualidade visual. Os temas e assets deste plano partem do projeto existente; sua localização/proveniência deve continuar sendo verificada na base.

## 15. Definição de concluído

O redesign estará pronto quando uma pessoa conseguir escolher uma build, entender sua vantagem e suas condições, ajustá-la, comparar outra opção e levar os itens para o farm sem perder contexto ou dados. Todas as funções anteriores precisam permanecer acessíveis, com estados confiáveis, PT/EN consistente, teclado e mobile utilizáveis, e resultados numéricos equivalentes para entradas equivalentes.

Registro da implementação e próximos critérios de liberação: consultar `VALIDACAO-UI-UX.md`. Não tratar a aprovação dos testes automatizados como certificação da precisão matemática integral, da acessibilidade ou da usabilidade com jogadores.
