# Fontes e Integridade dos Dados

## Fonte principal

- [MHDB Wilds API](https://docs.wilds.mhdb.io/): armas, armaduras, adornos, talismãs, habilidades, itens, locais e conjuntos.
- Versão registrada da base: `2026-04-14T22:28:18-03:00`.
- Manifesto auditável: `app/data_manifest.json`.

## Fontes complementares

- [Kiranico](https://mhwilds.kiranico.com/): perfis de monstros, hitzones e referência de status.
- [FextraLife](https://monsterhunterwilds.wiki.fextralife.com/Gogma+Artian+Weapons): nomes e referência visual de armas Gogartianas.
- [MathHunter](https://www.mathhunter.ca/): comparação conceitual de fórmulas, rotações e apresentação.

## Atualização

Os scripts `sync_mhdb.py` e `generate_meta_cache.py` atualizam partes diferentes da base. Após qualquer sincronização:

1. Revise diferenças em `app/game_data.json` e `app/game_data_pt.json`.
2. Atualize versão e contagens em `app/data_manifest.json`.
3. Execute todos os testes.
4. Abra `/api/data/version` e confirme `status: ok`.
5. Valide pelo menos uma build física, uma elemental e uma de arma Gogartiana.

## Limitações conhecidas

- Tempos de rotação e algumas interações especiais são aproximações comparativas.
- Imagens complementares podem depender da disponibilidade de fontes externas; a interface usa ícones locais como fallback.
- O manifesto detecta arquivos ausentes e divergência de contagem, mas não prova sozinho que cada valor está correto dentro do jogo.

