# Plano de evolução: planejador de caçadas

Objetivo: conectar cenário, build, comparação explicável e materiais, sem cadastro.
Data de início: 23/09/2026.

## Etapas e critérios de aceite

1. Motor verificável: unidades de elemento, condições de habilidades, tipos de golpe e validação de peças. Testes numéricos de GS, GL e CB; nenhuma regressão nos testes existentes. Expor versão e limitações do motor.
2. Comparação justa: recalcular builds sob o mesmo cenário, sem alterar snapshots pessoais; separar DPS de conforto; medir contribuição de habilidades por recálculo. Testes de equivalência e cenário compartilhado.
3. Recomendação contextual: distribuir orçamento entre armas, preservar requisitos, retornar duas alternativas com cobertura e proveniência; recalcular/inutilizar cache antigo por versão. Testes de cobertura, legalidade e progressão sem Gog.
4. Caçada até o farm: compartilhar cenário entre telas, ações para comparar e planejar materiais, inventário de materiais no navegador com saldo faltante. Testes de persistência e quantidades; inspeção desktop/mobile.
5. Revisão integrada: suíte completa, sintaxe JS, fluxos no navegador, documentação de resultados e limitações. Não declarar exatidão do jogo para regras aproximadas.

## Regras de execução

- Preservar dados pessoais e APIs existentes quando possível.
- Não adicionar login ou dependência obrigatória de conta.
- Validar cada etapa antes de avançar e registrar os resultados aqui.
- Não apresentar busca limitada como ótimo global nem tempos estimados como benchmark do jogo.
- Fontes mecânicas: https://lescarnetsdelawycademie.fr/skills-wilds/ e https://wiggler.pet/other/guides/intermediate_damage_calculation ; catálogos/movimentos locais continuam versionados separadamente.

## Registro de validação

Etapas implementadas e validadas em 23-24/09/2026. Escopo: primeira entrega do planejador; não significa cobertura de todas as mecânicas do jogo.

| Etapa | Resultado | Validação |
| --- | --- | --- |
| Motor verificável | Unidades de elemento, regras por classe, condições de habilidades e tipos de golpe | 78 testes Python na primeira etapa |
| Comparação justa | Cenário compartilhado, snapshots preservados, contribuição isolada e modos de combo | 81 testes Python após a segunda etapa |
| Recomendação contextual | Orçamento distribuído entre armas, proveniência e reforços Gog por classe | 96 testes Python após a terceira etapa |
| Caçada até o farm | Navegação integrada, quantidades de adornos, estoque local e faltantes | Fluxos desktop/mobile e testes JavaScript |
| Revisão integrada | Regressões, cache completo, entrega HTTP, concorrência e preservação de parâmetros | 101 testes Python e 10 JavaScript aprovados |

Base recalculada: 224 presets e 448 alternativas. Cada alternativa foi recalculada novamente nos testes, sem avisos de slots, com os requisitos registrados satisfeitos. Presets de progressão permanecem sem Gog; os demais usam Gog.

O gerador agora compara duas configurações de busca por preset, remove equipamentos duplicados e mantém as duas melhores alternativas encontradas entre elas.

Resultados detalhados, reprodução e pendências: [VALIDACAO-EVOLUCAO.md](VALIDACAO-EVOLUCAO.md).
