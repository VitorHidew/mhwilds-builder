# Validacao da experiencia: Wilds Forge

Data: 25/09/2026. Interface: 20260925. Motor preservado: 2026.09.23.1.

## Entrega

O nucleo das etapas 0 a 4 de `PLANO-UI-UX-EXPERIENCIA.md` foi implementado na stack existente, sem login, migracao de framework ou alteracao das expectativas matematicas dos testes. A etapa 5 recebeu validacao tecnica; nao equivale a uma certificacao de usabilidade ou acessibilidade.

| Area | Mudanca implementada |
| --- | --- |
| Navegacao | Cacada, Minhas builds e Biblioteca; Alvo, Build, Comparar e Materiais dentro da cacada; Montar/Recomendar como modos da build. Rotas por hash e historico do navegador. |
| Continuidade | Rascunho local versionado, preservacao dos encaixes vazios, restauracao da tela e dos criterios do otimizador, desfazer/refazer e exportacao do rascunho/favoritos no backup. |
| Contexto | Alvo e parte visiveis; divergencia entre recomendacao e cacada explicitada; escolha de manter a cacada ou adotar as condicoes ao abrir uma build. |
| Montador | Foto, nome, habilidades e adornos agrupados por peca. Pesquisa no seletor, previa de troca, controle por teclado e preservacao de adornos compativeis. Salvar nao muda de tela. |
| Recomendacao | Duas alternativas resumidas, dano por rotacao/DPS/DPM, equipamento e evidencia expandiveis, criterios avancados recolhidos, descarte de busca obsoleta. |
| Comparacao | Referencia selecionavel, ate quatro builds no grafico e todas na tabela, diferenca percentual, comparacao de pecas/habilidades/atributos de arma e combos no mesmo cenario. |
| Monstros | Imagens centralizadas, valores numericos de vulnerabilidade e tabela de todas as partes selecionaveis; filtro de uptimes das habilidades equipadas. |
| Biblioteca e farm | Pesquisa/favoritos nas builds, wiki contextual com retorno, materiais faltantes e estoque local; receitas incompletas continuam identificadas. |
| Interface | Paleta grafite com acentos dos cinco biomas, navegacao inferior no celular, resumo compacto de dano, foco visivel, dialogs nativos e movimentos reduzidos. |

## Correcoes encontradas na implementacao

- Respostas antigas de calculo nao podem substituir a resposta mais recente. Salvar diretamente tambem resolve os pedidos pendentes do debounce.
- Trocar idioma preserva o equipamento, os adornos e os criterios/alvo do otimizador; este ultimo voltava ao primeiro monstro ao repopular o catalogo.
- Preferencias temporarias sao removidas ao fechar a janela, sem deixar um formulario solto na pagina.
- Botoes de aplicar dos editores continuam visiveis e fecham a janela depois de aplicar.
- Adornos nao ficam comprimidos em colunas com uma letra por linha no celular.
- A abertura nao exibe por um instante o painel antigo com metricas zeradas.
- Diferencas de ataque entre duas armas personalizadas de mesmo nome aparecem no comparador.

## Imagens

O manifesto local tem 152 imagens: 34 monstros, 14 armas Gogartianas e 104 armaduras usadas pelo catalogo de recomendacoes. Total dos arquivos referenciados: 15.976.205 bytes.

Foram verificados assinatura de arquivo, SHA-256, existencia, atribuicao e decodificacao das 152 imagens com Pillow. A maior imagem referenciada tem 2.999 x 3.549 pixels. O render de Gogmazios de 132 megapixels foi substituido por uma ilustracao existente do mesmo monstro na fonte, adequada para a interface. Nenhuma arma ou skin foi gerada por IA.

`docs/cache_visual_assets.py --equipment` permite atualizar o cache a partir das fontes registradas. O backend valida o caminho antes de servir fotos locais. Imagens de equipamentos fora desse conjunto ainda dependem do fluxo remoto anterior, com icone de fallback. Nao se afirma que todas as imagens do catalogo completo estejam disponiveis offline nem que todas tenham passado por verificacao visual individual.

As fontes e hashes ficam em `static/assets/catalog/manifest.json`. Atribuicao nao concede licenca de redistribuicao; revisar os direitos dos binarios antes de publicar no GitHub. Ver `THIRD_PARTY_NOTICES.md`.

## Testes automatizados

Executados na pasta do projeto, sem instalar dependencias globais:

```powershell
python -m pytest -q -p no:cacheprovider
node --test --test-isolation=none tests/material-plan.test.js tests/planner-state.test.js tests/workspace-state.test.js tests/calculation-state.test.js
```

- Python: **104 testes aprovados**.
- JavaScript: **21 testes aprovados**.
- Verificacao sintatica de todos os arquivos em `static/js`: aprovada.
- Cobertura adicional: rotas, rascunhos invalidos, encaixes vazios, historico, divisao por zero, identidade do cenario, respostas fora de ordem, preservacao de criterios ao traduzir, imagens locais e rejeicao de caminho fora do catalogo.
- As expectativas existentes do motor nao foram alteradas para acomodar o redesign.

## Jornadas verificadas no navegador

Servidor de teste em `127.0.0.1:8020`, com armazenamento separado em `%TEMP%/mhwilds-ux-validation` e origem de navegador distinta. A biblioteca real do usuario nao foi limpa nem substituida por builds de QA.

| Jornada | Evidencia observada |
| --- | --- |
| Recomendacao endgame | Duas alternativas de Espadao/conforto; escolha de cenario; equipamento Gog, armadura e 12 adornos carregados. |
| Progressao | Duas alternativas de Ranque Baixo; a primeira exibiu Nu Krake I, nao arma Gog. Este teste e de integracao da interface, nao uma auditoria da disponibilidade de cada peca no jogo. |
| Trocar e desfazer | Busca por Rey, previa da mudanca, troca com variacao de DPS e restauracao do elmo/adornos ao desfazer. |
| Editor Gog | Ataque base 205 para 210: DPS 186,4 para 189,6 e indicacao de +1,7%; aplicacao fechou o dialog e manteve a montagem. |
| Salvar e retomar | Salvamento sem sair do montador; recarregamento preservou nome, alvo e adornos. |
| Comparador | Seis builds na tabela, quatro no grafico; 189,6 / 187,4 / 186,4 DPS com deltas 0 / -1,2% / -1,7%. Troca de referencia e analise de combos funcionaram. |
| Combos | Offset, TCS e atalho via tackle produziram valores distintos; detalhamento por golpe exibido. |
| Wiki | Habilidade Agitador, equipamento relacionado, voltar a definicao anterior e fechar por Escape. |
| Materiais | Build adicionada com duplicidade de adornos preservada; estoque de dois certificados reduziu faltantes de 41 para 39, com progresso de 5%. |
| Alvo e uptimes | Selecao da cabeca de Arkveld, HZ 45/48/45; perfil Realista alterou calculo e tabela das partes permaneceu acessivel. |
| Idioma e biomas | PT/EN preservaram a montagem; apos a correcao, Arkveld/cabeca permaneceram no otimizador ao mudar para EN. Os cinco biomas alteraram fundo e acentos. |

Larguras conferidas no DOM do montador: 320, 390, 768, 1280 e 1440 pixels, sem overflow horizontal da pagina e sem imagens visiveis quebradas nesses estados. Capturas revisadas em 390 x 844 e 1440 x 900. Tabelas extensas mantem rolagem interna. Nao houve erros JavaScript nos fluxos inspecionados.

## Limites e proximos criterios de liberacao

1. Revisao editorial integral PT/EN ainda pendente: nomes de presets/combo e algumas explicacoes antigas do motor permanecem no idioma original. Nomes dados pelo usuario nao devem ser traduzidos automaticamente.
2. Cache de fotos nao cobre todos os equipamentos. Revisar visualmente os demais assets e seus direitos antes de distribui-los.
3. A pesquisa usa nome e habilidades e respeita a compatibilidade dos adornos; filtros dedicados de raridade/numero de slots e virtualizacao completa continuam possiveis refinamentos.
4. Nao foram realizados teste com cinco jogadores, auditoria com leitor de tela, certificacao WCAG ou medicao formal de p95. Nao ha promessa de melhoria percentual de performance.
5. Os fluxos principais foram exercitados, mas nao todas as combinacoes das 14 armas, cinco temas e dois idiomas em cada tela. Cobertura exaustiva de falha de armazenamento e importacao/reversao no navegador continua pendente.
6. A camada visual preserva estimativas e limites existentes do motor. Esta entrega nao prova disponibilidade de cada build em cada RC nem equivalencia de dano com todos os testes dentro do jogo.
7. Cancelar uma busca descarta sua resposta na interface; nao interrompe necessariamente o trabalho ja iniciado no servidor.

Para publicar: revisar os direitos das imagens, concluir a revisao editorial e repetir as jornadas com dados de teste no ambiente de hospedagem, mantendo as restricoes de rede e isolamento existentes.

## Arquivos principais

- `static/js/experience.js`: componentes e integracao das jornadas.
- `static/js/workspace-state.js`: contratos testaveis de rascunho, rota, historico e comparacao.
- `static/css/experience.css`: sistema visual e responsividade.
- `static/index.html`, `static/js/app.js`, `static/js/planner.js`: integracao com os fluxos existentes.
- `app/main.py`: preferencia por imagens locais com validacao de caminho.
- `tests/workspace-state.test.js`, `tests/calculation-state.test.js`, `tests/planner-state.test.js`, `tests/test_visual_assets.py`, `tests/test_security.py`: cobertura de regressao.
- `docs/cache_visual_assets.py`, `static/assets/catalog/manifest.json`, `static/js/LUCIDE-LICENSE`: manutencao e proveniencia dos recursos.
