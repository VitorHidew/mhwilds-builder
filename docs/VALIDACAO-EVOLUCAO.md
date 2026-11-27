# Validação da evolução do planejador

Data: 24/09/2026. Motor: `2026.09.23.1`.

## Escopo entregue

1. Cálculo: separação entre elemento exibido e interno, bônus elementais por classe, Rajada, Coalescência, Absorção Elemental, Elemento Crítico e golpes carregados. Golpes físicos, disparos de lançarma e frascos recebem regras distintas. Peças em posições incorretas e partes inexistentes são rejeitadas.
2. Comparador: recálculo no mesmo alvo, parte e condições; modos por rotação salva, melhor rotação por build e combo selecionado. Compatibilidade de classe é validada. Snapshots pessoais não são sobrescritos. Remover uma habilidade isoladamente mede sua contribuição, mas as contribuições não são aditivas nem provam sozinhas a diferença entre duas builds.
3. Otimizador: distribuição do orçamento entre armas candidatas, requisitos verificados, duas alternativas por preset, número de avaliações e proveniência. A busca é limitada e não comprova ótimo global. Armas Gog usam atributos-base e reforços elementais específicos por classe; a recomendação não inventa bases diferentes para alto e baixo RNG.
4. Fluxo: alvo → build → comparação → materiais, sem login. Ao carregar uma recomendação, arma, adornos, parâmetros e uptimes são preservados. Os controles dos presets refletem as condições da build em cache. Respostas antigas não podem substituir uma busca mais recente.
5. Materiais: adornos repetidos têm quantidade, arma e talismã personalizados são incluídos juntos, estoque por identificador estável, total necessário e faltante. Adicionar novamente a mesma build não multiplica as quantidades. Estoque participa do backup local.
6. Entrega e UI: catálogo JSON serializado em cache, GZip, ETag e resposta 304; scripts e estilos revalidados após atualizações. Painel por golpe acompanha a build escolhida no comparador, não a última arma aberta no montador. Falha de imagem removida do DOM não causa exceção.

## Testes automatizados

- Python: **101 aprovados**, incluindo testes preexistentes de segurança, API e integridade.
- JavaScript: **10 aprovados**, cobrindo contagens, saldo não negativo, inventário inválido, idioma, nomes canônicos de habilidades, itens personalizados, cenário e descarte de comparação desatualizada.
- Sintaxe: os três arquivos JavaScript verificados sem erros.
- Cache: **224 presets / 448 alternativas**, versão atual, zero falhas na geração. Todas as alternativas foram recalculadas e comparadas ao DPS salvo; slots e requisitos registrados validados. Política Gog/progressão validada em todos os presets.
- CI: comandos dos novos testes adicionados ao workflow existente. Execução remota do GitHub e build Docker não foram realizados nesta etapa.
- Busca em cache: compara os resultados dos pools rápido e ampliado, deduplica equipamentos e conserva as duas maiores pontuações. A contagem de avaliações soma as duas buscas e pode incluir repetições; não representa combinações únicas.
- Comparação com o cache anterior desta etapa, no mesmo motor e cenário de cada preset: **33 presets melhoraram, 191 permaneceram iguais e zero pioraram** em DPS da primeira alternativa. Exemplo GS DPS Máximo: 140,4 → 145,6 DPS (+3,7%). Todos os 224 presets terminaram com duas alternativas e sem falhas de geração.
- Catálogo PT medido via HTTP local: 5.554.445 bytes em JSON, 678.549 bytes com GZip, redução de 87,8% no corpo transferido. Isso não é uma medição de FPS nem de latência de rede externa.

```powershell
python -m pytest -q -p no:cacheprovider
node --test tests/material-plan.test.js tests/planner-state.test.js
node --check static/js/app.js
node --check static/js/planner.js
node --check static/js/material-plan.js
```

No ambiente isolado desta validação, o Node exigiu `--test-isolation=none` por restrição de criação de subprocessos. `tests/conftest.py` agora define uma pasta temporária antes de importar a aplicação, de modo que a execução comum do pytest também não use o armazenamento pessoal. Os testes no navegador usaram uma pasta separada. Nenhum teste limpou o armazenamento pessoal do usuário.

Para regenerar os presets, execute `python -m app.generate_meta_cache`. A gravação usa arquivo intermediário e preserva o cache anterior se houver presets sem resultado. Reinicie o servidor após atualizar regras ou cache.

## Validação no navegador

| Fluxo | Evidência observada |
| --- | --- |
| Cache → montador | GS DPS Máximo: 140,4 DPS e 674,0 por ciclo em ambas as telas; 13 adornos preenchidos |
| Busca atual → montador | GS DPS Máximo: 145,6 DPS e 698,9 por ciclo; a métrica resumida do montador arredonda o ciclo para 699; 13 adornos preenchidos |
| Uptime do cache | Agitador 95%, Performance Máxima 0%, correspondendo aos parâmetros realmente usados no preset |
| Progressão RC41+ | Duas alternativas com Lamorak Robusto, sem recomendação de arma Gog |
| Comparação com três builds | Três linhas, gráfico com três barras e recálculo sem quebra |
| Troca de parte | Mesma GS: 127,7 DPS na média das partes do Ajarakan; 179,8 na cabeça, sob o cenário usado no teste |
| Combos | Offset, TCS e atalho Tackle exibidos e classificados, com detalhamento correspondente |
| Materiais | Build adicionada com 54 unidades faltantes; estoque de 3 reduziu para 51 |
| Persistência e idioma | Estoque continuou em 3 após recarregar e alternar PT/EN; nomes de materiais acompanharam o idioma |
| Layout | Inspeção visual em 1280×720 e 390×844; controles legíveis e tabelas contidas, sem rolagem horizontal da página |

Esses números são evidências de regressão no cenário de teste, não benchmarks medidos no jogo. Os testes de navegador cobrem os fluxos alterados, não cada combinação possível de equipamento ou cada botão da aplicação.

## Limites e próximos passos

1. **Precisão por classe:** calibrar tempos por frames e validar em jogo; expandir lançarma por tipo/nível de disparo, frascos elementais da CB e especificidades de munições, recarga e revestimentos. Ainda existem aproximações nesses caminhos.
2. **Alvos e uptime:** distinguir estados normais, feridas e variantes AT com dados específicos. A média das partes não representa uma distribuição real de acertos. Uptime probabilístico não simula a sequência temporal da luta.
3. **Busca Gog:** ampliar a busca conjunta de reforços, focos e pares de habilidades, em vez de partir de um modelo recomendado. Duas alternativas legais não garantem diversidade estratégica nem melhor build absoluta.
4. **Materiais:** completar receitas ausentes, etapas anteriores de upgrade e custos aleatórios Gog. Os totais incompletos são identificados como parciais. A lista reúne requisitos máximos por peça entre builds, não fabrica várias cópias automaticamente.
5. **Imagens:** URLs externas de monstros retornaram HTTP 403 na origem durante a revisão; há fallback visual e o erro de JavaScript foi corrigido, mas não se declara disponibilidade de todas as fotos. Próximo trabalho: catálogo local autorizado/licenciado, com origem e verificação de integridade, sem imagens geradas substituindo itens oficiais.
6. **Idioma:** os novos controles e materiais foram conferidos em PT/EN, mas nomes personalizados preservam o texto original e ainda há traduções legadas incompletas. Não foi realizada certificação integral da tradução do site.
7. **Publicação:** executar CI e Docker em ambiente de publicação, revisar licenças de ativos e fazer uma nova revisão de segurança antes de expor o servidor. Os testes locais não são uma certificação de ausência de vulnerabilidades.

## Referências mecânicas

- [Wycademie: habilidades](https://lescarnetsdelawycademie.fr/skills-wilds/).
- [Wiggler: cálculo intermediário de dano](https://wiggler.pet/other/guides/intermediate_damage_calculation).
- [Phantom Brawlers: Artian por classe](https://www.phantombrawlers.com/mhwilds/Artian).
- [Wycademie: armas Gogmazios](https://lescarnetsdelawycademie.fr/gogmazios-weapons/).

São referências comunitárias para as regras implementadas, não uma certificação oficial da Capcom. Catálogo de equipamentos e biblioteca de movimentos permanecem dados locais versionados separadamente do motor.
