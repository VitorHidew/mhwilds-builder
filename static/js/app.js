let GAME_DATA = null;
        let CURRENT_RESULT = null;
        let SAVED_BUILDS = [];
        let CUSTOM_GOG = null;
        let CUSTOM_TALISMAN = null;
        let TALISMAN_INVENTORY = [];
        let OPTIMIZER_RESULTS = [];
        let META_PRESETS = [];
        let GOG_RECOMMENDATION = null;
        let BUILDER_GOG_RECOMMENDATION = null;
        let CURRENT_OPT_UPTIME_PRESET = 'realistic';
        let ROTATION_COMPARISONS = [];
        let CURRENT_ROTATION_ID = null;
        let SAVED_DAMAGE = [];
        let SITE_LOCALE = localStorage.getItem('mhwilds_locale') || 'pt';
        let VISUAL_THEME = localStorage.getItem('mhwilds_visual_theme') || 'windward';
        let RECALC_TIMER = null;
        let RECALC_CONTROLLER = null;
        let RECALC_VERSION = 0;
        let RECALC_WAITERS = [];
        let DECO_BY_KIND_LEVEL = { weapon: {}, armor: {} };
        let DECORATION_BY_ID = new Map();
        let WIKI_IMAGE_CACHE = {};
        let TRANSCENDED_ARMOR = new Set();
        let WISHLIST = [];
        const WISHLIST_STORAGE_KEY = 'mhwilds_wishlist';
        const TALISMAN_STORAGE_KEY = 'mhwilds_talisman_inventory';
        const BACKUP_APP_ID = 'mhwilds-builder';
        const BACKUP_SCHEMA_VERSION = 1;
        const BACKUP_MAX_BYTES = 5 * 1024 * 1024;

        const WEAPON_TYPE_PT_UI = {
            'Great Sword': 'Espadão', 'Long Sword': 'Espada Longa', 'Sword & Shield': 'Espada e Escudo',
            'Dual Blades': 'Duplas-Lâminas', 'Hammer': 'Martelo', 'Hunting Horn': 'Berrante de Caça',
            'Lance': 'Lança', 'Gunlance': 'Lançarma', 'Switch Axe': 'Transmachado',
            'Charge Blade': 'Lâmina Dínamo', 'Insect Glaive': 'Glaive Inseto',
            'Light Bowgun': 'Fuzilarco Leve', 'Heavy Bowgun': 'Fuzilarco Pesado', 'Bow': 'Arco'
        };
        const SLOT_PT_UI = { helm: 'Elmo', chest: 'Peitoral', arms: 'Braços', waist: 'Cintura', legs: 'Pernas' };
        const SLOT_EN_UI = { helm: 'Head', chest: 'Chest', arms: 'Arms', waist: 'Waist', legs: 'Legs' };
        const GOGMA_WEAPON_BY_TYPE = {
            'Great Sword': 'Ostrak Oblivion',
            'Long Sword': "Headsman's Hamus",
            'Sword & Shield': 'Kyrie Verd',
            'Dual Blades': 'Eternal Cusp',
            'Hammer': 'Bound Admonition',
            'Hunting Horn': 'Onyx Choros',
            'Lance': 'Aether Pike',
            'Gunlance': 'Auguring Omen',
            'Switch Axe': 'Wicked Regnum',
            'Charge Blade': 'Promised Abyss',
            'Insect Glaive': 'Limbo Llor',
            'Light Bowgun': 'Bethorned Agony',
            'Heavy Bowgun': 'Trembling Hels',
            'Bow': 'Calamitous Angel'
        };
        const UI_EN = {
            'Idioma / Language': 'Language', 'Bioma visual': 'Visual biome',
            'Planícies Zéfiras': 'Windward Plains', 'Floresta Escarlate': 'Scarlet Forest', 'Bacia Oleídea': 'Oilwell Basin', 'Escarpas Frígidas': 'Iceshard Cliffs', 'Ruínas de Wyveria': 'Ruins of Wyveria',
            'Forja': 'Forge', 'Análise': 'Analysis', 'Biblioteca': 'Library', 'Montador Livre': 'Build Builder', 'Lista de Desejos': 'Wishlist', 'Cenário & Monstro': 'Scenario & Monster', 'Editor Arma Gog': 'Artian Weapon Editor', 'Editor de Talismã': 'Talisman Editor', 'Otimizador de Builds': 'Build Optimizer', 'Comparador': 'Comparator', 'Sugestões': 'Suggestions', 'Visão Geral': 'Overview', 'Inventário de Talismãs': 'Talisman Inventory', 'Registro & Regras': 'Registry & Rules', 'Configurações': 'Settings', 'Fontes & Limites': 'Sources & Limits',
            'Mesa de Forja': 'Forge Bench', 'Cálculo ao vivo': 'Live calculation', 'Build não calculada': 'Build not calculated', 'Comissão de Pesquisa · Base de Expedição': 'Research Commission · Expedition Base', 'Prepare a próxima caçada.': 'Prepare for the next hunt.', 'Monte o equipamento, escolha o alvo e veja o impacto de cada habilidade antes de sair do acampamento.': 'Assemble your equipment, choose a target, and see every skill impact before leaving camp.', 'Montar build': 'Build loadout', 'Encontrar melhor set': 'Find best set', 'Comparar builds': 'Compare builds', 'DPS prático': 'Practical DPS', 'Dano por ciclo': 'Damage per cycle', 'Raw efetivo': 'Effective raw', 'Builds salvas': 'Saved builds', 'Alvo em análise': 'Target under analysis', 'Selecione um monstro': 'Select a monster', 'A escolha do alvo define hitzones, fraquezas e a recomendação de elemento.': 'Your target defines hitzones, weaknesses, and the element recommendation.', 'O que deseja preparar?': 'What would you like to prepare?', 'Aguardando uma build calculada.': 'Waiting for a calculated build.', 'Escolha arma, armadura, adornos e veja o resultado na hora.': 'Choose weapon, armor, decorations, and see the result immediately.', 'Planejar alvo': 'Plan target', 'Defina monstro, parte vulnerável, ferida e uptime realista.': 'Set the monster, weak part, wound, and realistic uptime.', 'Oficina de Otimização': 'Optimization Workshop', 'Encontre duas rotas de build para a situação escolhida.': 'Find two build routes for the selected situation.',
            'Montador Livre de Equipamentos': 'Free Equipment Builder', 'Equipamentos & Encaixes': 'Equipment & Slots', 'Arma': 'Weapon', 'Elmo': 'Head', 'Peitoral': 'Chest', 'Braços': 'Arms', 'Cintura': 'Waist', 'Pernas': 'Legs', 'Talismã': 'Talisman', 'Métricas de Dano em Tempo Real': 'Live Damage Metrics', 'Avisos Inteligentes': 'Smart Warnings', 'Habilidades Ativas Acumuladas': 'Active Skills', 'Cenário de Combate & Monstro Alvo': 'Combat Scenario & Target Monster', 'Seleção do Monstro & Hitzone': 'Monster & Hitzone Selection', 'Fraquezas do Monstro': 'Monster Weaknesses', 'Partes Mais Fracas': 'Weakest Parts', 'Uptimes de Habilidades Contextuais': 'Contextual Skill Uptimes', 'Padrão': 'Default', 'Realista': 'Realistic', 'Agressivo': 'Aggressive', 'Conforto': 'Comfort', 'Físico': 'Physical', 'Elemental': 'Elemental',
            'Otimizador Automático de Combinações': 'Automatic Combination Optimizer', 'Executar Otimização': 'Run Optimization', 'Critérios & Metas de Habilidades': 'Criteria & Skill Targets', 'Resultados Otimizados': 'Optimized Results', 'Comparador de Builds Salvas (Até 30 Builds)': 'Saved Build Comparator (Up to 30 Builds)', 'Combos e Motor por Golpe': 'Combos & Per-Hit Engine', 'Gráfico de Comparação': 'Comparison Chart', 'Tabela Geral Comparativa': 'General Comparison Table', 'Fontes e Limites': 'Sources and Limits', 'Dados Locais': 'Local Data', 'Presets Globais': 'Global Presets'
            , 'Selecione peças, configure jóias dinâmicas por nível de slot e acompanhe os cálculos ao vivo.': 'Select pieces, configure decorations by slot level, and follow calculations live.', 'Nome da Build...': 'Build name...', 'Build Card': 'Build Card', 'Limpar': 'Clear', 'Limpar Adornos': 'Clear Decorations', 'Recomendar Arma Gog': 'Recommend Gog Weapon', 'Materiais da Build': 'Build materials', 'Salvar Resultado': 'Save Result', 'Salvar Build': 'Save Build', 'Cálculo inválido': 'Invalid calculation', 'Cálculo atualizado': 'Calculation updated', 'Configure uma build para calcular': 'Configure a build to calculate',
            'Configuração de hitzones ponderadas, condições de ferida (Modo Foco) e uptimes de buffs contextuais.': 'Configure weighted hitzones, wound conditions (Focus Mode), and contextual buff uptimes.', 'Monstro': 'Monster', 'Parte do Corpo / Modo de Dano': 'Body Part / Damage Mode', 'Usar monstro customizado': 'Use custom monster', 'Nome do Monstro Customizado': 'Custom Monster Name', 'Aplicar Monstro Customizado': 'Apply Custom Monster', 'Ponto com Ferida Ativa / Modo Foco (+20% Afinidade Contextual)': 'Wounded Point / Focus Mode (+20% contextual affinity)', 'Por padrão, o cálculo usa zonas médias ponderadas do monstro. Escolha uma parte específica acima apenas quando quiser uma análise avançada focada em uma região.': 'By default, calculations use weighted average monster hitzones. Choose a specific part only for focused advanced analysis.',
            'Builds pré-prontas': 'Ready-made builds', 'Classe de Arma Alvo': 'Target Weapon Class', 'Arma Específica': 'Specific Weapon', 'Monstro do Otimizador': 'Optimizer Monster', 'Combo usado no cálculo': 'Combo used in calculation', 'Ordenar Resultado Por': 'Sort Results By', 'Usar talismãs do inventário': 'Use talismans from inventory', 'Esforço de Busca': 'Search Effort', 'Habilidades obrigatórias': 'Required Skills', 'Considerar todas as armaduras transcendidas': 'Consider all transcended armor', 'Uptime das habilidades de dano': 'Damage skill uptime', 'Rápido - menos combinações': 'Fast - fewer combinations', 'Balanceado': 'Balanced', 'Mais amplo': 'Deep search',
            'Compare ranking geral, DPS, dano por ciclo, dano/minuto, equipamentos e habilidades principais.': 'Compare overall ranking, DPS, cycle damage, damage per minute, equipment, and key skills.', 'Build analisada': 'Analyzed build', 'Comparar combos': 'Compare combos', 'Detalhamento do melhor combo': 'Best combo breakdown', 'Leitura rápida': 'Quick read', 'Tabela de decomposição golpe a golpe': 'Hit-by-hit breakdown', 'Builds no gráfico': 'Builds in chart', 'Melhores 6': 'Top 6', 'Todas': 'All', 'Resultados/Danos Salvos': 'Saved Results/Damage', 'Ordenar por': 'Sort by', 'Nome da Build': 'Build Name', 'Arma': 'Weapon', 'Afinidade': 'Affinity', 'Dano / Minuto': 'Damage / Minute', 'Combo calculado': 'Calculated combo', 'Nota Combinada': 'Combined Score', 'Dif. vs Melhor': 'Diff. vs Best', 'Ações': 'Actions',
            'Editor de Talismã Personalizado': 'Custom Talisman Editor', 'Equipar Talismã no Montador': 'Equip Talisman in Builder', 'Configuração do Talismã': 'Talisman Configuration', 'Slots do Talismã': 'Talisman Slots', 'Armadura': 'Armor', 'Talismãs avaliados podem ter encaixes de arma e de armadura. Cada espaço aceita somente o tipo indicado.': 'Appraised talismans may have weapon and armor slots. Each slot only accepts the indicated type.', 'Inventário Rápido': 'Quick Inventory', 'Adicionar ao Inventário': 'Add to Inventory', 'Próximas Melhorias': 'Next Improvements', 'Habilidades Modeladas': 'Modeled Skills', 'Pesquisar Habilidades': 'Search Skills', 'Lista de Desejos': 'Wishlist', 'Acompanhe as peças escolhidas e o total de materiais necessário para criá-las.': 'Track selected pieces and the total materials needed to craft them.', 'Limpar Lista': 'Clear wishlist', 'Peças salvas': 'Saved pieces', 'Materiais de craft': 'Crafting materials', 'Controles globais de uso, limpeza e exportação/importação simples.': 'Global controls for use, cleanup, and simple export/import.', 'Exportar JSON': 'Export JSON', 'Limpar Builds Locais': 'Clear Local Builds', 'Limpar Resultados Locais': 'Clear Local Results',
            'DPS Prático': 'Practical DPS', 'Raw Efetivo (EFR)': 'Effective Raw (EFR)', 'Dano por Ciclo': 'Damage per Cycle', 'Afinidade Efetiva': 'Effective Affinity', 'Nenhum': 'None', 'Nenhuma': 'None', '(Nenhum)': '(None)', '(Nenhuma)': '(None)', '(vazio)': '(empty)', 'Vazio': 'Empty', 'Raw Puro (Sem Elemento)': 'Pure Raw (No Element)', 'Sem foco (arma antiga/importada)': 'No focus (legacy/imported weapon)', 'Foco em Ataque (+10 Raw, -15% afinidade)': 'Attack Focus (+10 Raw, -15% affinity)', 'Foco Elemental (+50 elemento exibido, -5% afinidade)': 'Element Focus (+50 displayed element, -5% affinity)', 'Foco em Afinidade (+10% afinidade, -10 Raw, -10 elemento exibido)': 'Affinity Focus (+10% affinity, -10 Raw, -10 displayed element)',
            'Editor de Arma Gog / Gogartiana Personalizada': 'Custom Gog / Gog Artian Weapon Editor', 'Crie uma arma customizada com parâmetros sob medida. Ela fica disponível imediatamente como "ARMA GOG :: Editor".': 'Create a custom weapon with tailored parameters. It becomes available immediately as "GOG WEAPON :: Editor".', 'Aplicar & Equipar no Montador': 'Apply & Equip in Builder', 'Atributos Base': 'Base Attributes', 'Tipo de Arma': 'Weapon Type', 'Nome Personalizado': 'Custom Name', 'Ataque Raw True': 'True Raw Attack', 'Afinidade Base (%)': 'Base Affinity (%)', 'Elemento & Afiamento': 'Element & Sharpness', 'Natureza': 'Nature', 'Elemento / Status': 'Element / Status', 'Elemento / Status exibido no jogo': 'In-game displayed Element / Status', 'Melhor Fio': 'Best Sharpness', 'Unidades do Melhor Fio': 'Best Sharpness Units', 'Fio Anterior': 'Previous Sharpness', 'Foco & Reforços Gog': 'Gog Focus & Reinforcements', 'Foco do Dispositivo Alcatroado': 'Tarred Device Focus', '5 Reforços Gog': '5 Gog Reinforcements', 'Slots & Habilidades da Arma': 'Weapon Slots & Skills', 'Habilidade Embutida 1': 'Built-in Skill 1', 'Habilidade Embutida 2': 'Built-in Skill 2', 'Habilidade Embutida 3': 'Built-in Skill 3',
            'Resumo auditável das habilidades modeladas no motor atual e das que ainda são informativas.': 'Auditable summary of skills modeled by the current engine and those that remain informational.', 'Digite para filtrar...': 'Type to filter...', 'raw fixo e percentual conforme nível.': 'flat and percentage raw according to level.', 'afinidade fixa.': 'flat affinity.', 'afinidade ponderada pelo uptime configurado.': 'affinity weighted by configured uptime.', 'multiplicador crítico.': 'critical multiplier.', 'bônus ponderados por uptime.': 'bonuses weighted by uptime.', 'Ataques elementais:': 'Element Attacks:', 'bônus simples por nível para Fire/Water/Thunder/Ice/Dragon Attack.': 'simple per-level bonuses for Fire/Water/Thunder/Ice/Dragon Attack.',
            'DPS prático é o dano médio por segundo da rotação. Dano/min prático projeta esse DPS por 60 segundos. Dano por ciclo mede uma execução completa da rotação. Nota combinada mistura DPS, raw efetivo e afinidade para ranking geral. Raw, afinidade e elemento efetivos já incluem bônus ativos e afiamento.': 'Practical DPS is the average damage per second of the rotation. Practical damage/min projects that DPS over 60 seconds. Damage per cycle measures one full rotation. Combined score blends DPS, effective raw, and affinity for overall ranking. Effective raw, affinity, and element already include active bonuses and sharpness.',
            'Alvo e ponto de impacto': 'Target and impact point', 'Escolha a região que o cálculo deve considerar.': 'Choose the area that the calculation should consider.', 'Alvo em análise': 'Target under analysis', 'Dados do alvo selecionado.': 'Selected target data.',
            'Usar monstro customizado': 'Use custom monster', 'Nome do Monstro Customizado': 'Custom Monster Name', 'Corte': 'Sever', 'Impacto': 'Blunt', 'Projétil': 'Shot', 'Fogo': 'Fire', 'Água': 'Water', 'Raio': 'Thunder', 'Gelo': 'Ice', 'Dragão': 'Dragon', 'Aplicar Monstro Customizado': 'Apply Custom Monster',
            'Ponto com Ferida Ativa / Modo Foco (+20% Afinidade Contextual)': 'Active Wounded Point / Focus Mode (+20% contextual affinity)', 'A média ponderada é o padrão realista. Selecione uma parte somente quando sua estratégia mantiver golpes naquela região.': 'Weighted average is the realistic default. Select a part only when your strategy keeps attacks on that area.',
            'Abrir na Wiki interna': 'Open in internal Wiki', 'Dados completos no Kiranico': 'Full data on Kiranico', 'Perfil de vulnerabilidades': 'Vulnerability profile', 'Maior hitzone significa mais dano recebido naquele tipo de golpe.': 'A higher hitzone means more damage received from that attack type.',
            'Dano físico': 'Physical damage', 'Hitzone 0-100': 'Hitzone 0-100', 'Dano elemental': 'Elemental damage', 'Fraquezas a status': 'Status weaknesses', 'Escala 0-3: maior é melhor': 'Scale 0-3: higher is better', 'Melhores partes para dano físico': 'Best parts for physical damage', 'Maior hitzone entre corte, impacto e projétil': 'Highest hitzone among sever, blunt, and shot',
            'Dúvidas sobre os números? A explicação abre diretamente na página correspondente do Registro & Regras.': 'Questions about the numbers? The explanation opens directly on the related Registry & Rules page.', 'Entender hitzones': 'Understand hitzones', 'Entender elemento': 'Understand elements', 'Entender status': 'Understand status',
            'A tela de Cenário também aponta para a ficha correspondente no Kiranico para consulta de hitzones, partes e acúmulo de status.': 'The Scenario screen also links to the corresponding Kiranico entry for hitzones, parts, and status buildup.',
            'Talismãs salvos:': 'Saved talismans:', 'Itens na Lista de Desejos:': 'Wishlist items:',
            'Baixar Backup': 'Download Backup', 'Importar Backup': 'Import Backup',
            'Integridade da Base': 'Data Integrity', 'Verificando versão e integridade dos dados...': 'Checking data version and integrity...',
            'Use os presets de uptime na tela de cenário. O idioma, o bioma e seus dados ficam salvos neste navegador.': 'Use the uptime presets on the scenario screen. Language, biome, and your data are stored in this browser.',
            'Pesquisar arma...': 'Search weapons...', 'Pesquisar elmo/set/habilidade...': 'Search head/set/skill...',
            'Pesquisar peitoral/set/habilidade...': 'Search chest/set/skill...', 'Pesquisar braços/set/habilidade...': 'Search arms/set/skill...',
            'Pesquisar cintura/set/habilidade...': 'Search waist/set/skill...', 'Pesquisar pernas/set/habilidade...': 'Search legs/set/skill...',
            'Pesquisar talismã...': 'Search talismans...', 'Pesquisar arma do otimizador...': 'Search optimizer weapons...',
            'Pesquisar na wiki...': 'Search the wiki...', 'Parte alvo do Otimizador': 'Optimizer target part',
            'Define os HZ físico e elemental usados para escolher a arma e calcular a rotação.': 'Defines the physical and elemental hitzones used to choose the weapon and calculate the rotation.',
            'Defina as habilidades mínimas que deseja e o solver encontrará as melhores combinações ordenadas por DPS.': 'Set the minimum skills you want and the solver will find the best combinations ranked by DPS.',
            'Ranking geral': 'Overall ranking', 'Dano/min': 'Damage/min', 'Dano / Ciclo': 'Damage / Cycle',
            'Escolha uma build para recalcular todas as rotações disponíveis da arma no mesmo monstro, parte e uptime.': 'Choose a build to recalculate every available weapon rotation against the same monster, part, and uptime.',
            'Salve ou escolha uma build para comparar seus combos.': 'Save or choose a build to compare its combos.',
            'Explicação das Métricas': 'Metric Explanation',
            'Acerto / Golpe': 'Hit / Attack', 'Acertos': 'Hits', 'Físico normal': 'Normal physical',
            'Físico crítico': 'Critical physical', 'Dano esperado': 'Expected damage',
            'Selecione as builds que deseja confrontar. O gráfico suporta até 8 por vez para manter os valores legíveis.': 'Select builds to compare. The chart shows up to 8 at a time to keep values readable.'
        };

        function uiText(text) {
            return SITE_LOCALE === 'en' ? (UI_EN[text] || text) : text;
        }

        function translateStaticInterface() {
            document.documentElement.lang = SITE_LOCALE === 'en' ? 'en' : 'pt-BR';
            document.title = SITE_LOCALE === 'en'
                ? 'MH Wilds - Professional Build Calculator & Optimizer'
                : 'MH Wilds - Calculadora & Otimizador Profissional';
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            const nodes = [];
            while (walker.nextNode()) nodes.push(walker.currentNode);
            nodes.forEach(node => {
                if (['SCRIPT', 'STYLE'].includes(node.parentElement?.tagName)) return;
                if (node.parentElement?.closest('[data-ux-pt]')) return;
                if (node.__mhwildsOriginal === undefined) node.__mhwildsOriginal = node.nodeValue;
                const original = node.__mhwildsOriginal;
                const leading = original.match(/^\s*/)?.[0] || '';
                const trailing = original.match(/\s*$/)?.[0] || '';
                const key = original.trim();
                node.nodeValue = key ? `${leading}${uiText(key)}${trailing}` : original;
            });
            document.querySelectorAll('[placeholder], [title]').forEach(element => {
                ['placeholder', 'title'].forEach(attribute => {
                    if (!element.hasAttribute(attribute)) return;
                    const key = `__mhwilds_${attribute}`;
                    if (element.dataset[key] === undefined) element.dataset[key] = element.getAttribute(attribute);
                    element.setAttribute(attribute, uiText(element.dataset[key]));
                });
            });
            if (typeof translateExperience === 'function') translateExperience();
        }
        const SKILL_PT_UI = {
            'Attack Boost': 'Ataque', 'Critical Eye': 'Olho Crítico', 'Critical Boost': 'Impulso Crítico',
            'Weakness Exploit': 'Ponto Fraco', 'Agitator': 'Desafiante', 'Burst': 'Ímpeto',
            'Maximum Might': 'Poder Máximo', 'Peak Performance': 'Performance Máxima',
            'Offensive Guard': 'Guarda Ofensiva', 'Counterstrike': 'Contra-ataque',
            'Coalescence': 'Coalescência', 'Latent Power': 'Poder Latente', 'Resentment': 'Ressentimento',
            'Antivirus': 'Antivírus', 'Foray': 'Incursão', 'Fire Attack': 'Ataque de Fogo',
            'Water Attack': 'Ataque de Água', 'Thunder Attack': 'Ataque de Raio',
            'Ice Attack': 'Ataque de Gelo', 'Dragon Attack': 'Ataque de Dragão',
            'Speed Eating': 'Comer Rápido', 'Free Meal': 'Refeição Grátis',
            'Evade Window': 'Janela de Esquiva', 'Evade Extender': 'Extensor de Esquiva',
            'Constitution': 'Constituição', 'Stamina Surge': 'Recuperação de Vigor',
            'Partbreaker': 'Destruidor', 'Slugger': 'Nocauteador', 'Handicraft': 'Artesanato',
            'Razor Sharp': 'Afiação Navalha', "Master's Touch": 'Toque do Mestre',
            "Mind's Eye": 'Olho da Mente', 'Critical Draw': 'Saque Crítico',
            'Focus': 'Foco', 'Power Prolonger': 'Prolongador de Poder',
            'Rapid Morph': 'Transformação Rápida', 'Guard': 'Guarda', 'Guard Up': 'Guarda Reforçada',
            'Artillery': 'Artilharia', 'Load Shells': 'Carregar Projéteis',
            'Horn Maestro': 'Maestro do Berrante', 'Normal Shots': 'Tiros Normais',
            'Piercing Shots': 'Tiros Perfurantes', 'Spread/Power Shots': 'Tiros Espalhados/Poder',
            'Ballistics': 'Balística'
        };

        function weaponIcon(type = '') {
            return {
                'Great Sword': 'GS', 'Long Sword': 'LS', 'Sword & Shield': 'SnS', 'Dual Blades': 'DB',
                'Hammer': 'HM', 'Hunting Horn': 'HH', 'Lance': 'LA', 'Gunlance': 'GL',
                'Switch Axe': 'SA', 'Charge Blade': 'CB', 'Insect Glaive': 'IG',
                'Light Bowgun': 'LBG', 'Heavy Bowgun': 'HBG', 'Bow': 'BOW'
            }[type] || 'WP';
        }

        function armorIcon(slot = '') {
            return { helm: 'HEAD', chest: 'BODY', arms: 'ARM', waist: 'WAIST', legs: 'LEG' }[slot] || 'ARM';
        }

        function skillIcon(skill = '') {
            const s = skill.toLowerCase();
            if (s.includes('critical') || s.includes('weakness') || s.includes('affinity') || s.includes('eye')) return 'AFF';
            if (s.includes('attack') || s.includes('agitator') || s.includes('burst') || s.includes('resentment')) return 'ATK';
            if (s.includes('fire') || s.includes('water') || s.includes('thunder') || s.includes('ice') || s.includes('dragon')) return 'ELE';
            if (s.includes('guard') || s.includes('defense') || s.includes('resistance')) return 'DEF';
            if (s.includes('stamina') || s.includes('constitution') || s.includes('evade')) return 'STA';
            if (s.includes('eating') || s.includes('meal') || s.includes('recovery')) return 'ITM';
            if (s.includes('horn') || s.includes('maestro')) return 'HH';
            if (s.includes('shot') || s.includes('ammo') || s.includes('ballistics')) return 'RNG';
            if (s.includes('focus') || s.includes('charge') || s.includes('morph')) return 'TEC';
            return 'SKL';
        }

        const WIKI_FILE_URLS = {
            'Great Sword Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/c/c2/Great_Sword_Icon_White.png/revision/latest?cb=20151024184144',
            'Long Sword Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/1/1e/Long_Sword_Icon_White.png/revision/latest?cb=20151024170006',
            'Sword and Shield Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/e/e5/Sword_and_Shield_Icon_White.png/revision/latest?cb=20151025112102',
            'Dual Blades Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/7/74/Dual_Blades_Icon_White.png/revision/latest?cb=20151024183210',
            'Hammer Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/9/99/Hammer_Icon_White.png/revision/latest?cb=20151024190849',
            'Hunting Horn Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/4/46/Hunting_Horn_Icon_White.png/revision/latest?cb=20151025094318',
            'Lance Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/0/0b/Lance_Icon_White.png/revision/latest?cb=20151025102605',
            'Gunlance Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/1/17/Gunlance_Icon_White.png/revision/latest?cb=20151024185913',
            'Switch Axe Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/4/40/Switch_Axe_Icon_White.png/revision/latest?cb=20170719204530',
            'Charge Blade Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/6/6c/Charge_Blade_Icon_White.png/revision/latest?cb=20170719204606',
            'Insect Glaive Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/4/47/Insect_Glaive_Icon_White.png/revision/latest?cb=20170719204629',
            'Light Bowgun Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/0/09/Light_Bowgun_Icon_White.png/revision/latest?cb=20151025103728',
            'Heavy Bowgun Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/9/99/Heavy_Bowgun_Icon_White.png/revision/latest?cb=20151024192351',
            'Bow Icon White.png': 'https://static.wikia.nocookie.net/monsterhunter/images/a/a4/Bow_Icon_White.png/revision/latest?cb=20151024174635',
            'MH3icon-Helm.png': 'https://static.wikia.nocookie.net/monsterhunter/images/7/72/MH3icon-Helm.png/revision/latest?cb=20090919062424',
            'MH3icon-Plate.png': 'https://static.wikia.nocookie.net/monsterhunter/images/2/23/MH3icon-Plate.png/revision/latest?cb=20090919062438',
            'MH3icon-Gauntlets.png': 'https://static.wikia.nocookie.net/monsterhunter/images/a/a1/MH3icon-Gauntlets.png/revision/latest?cb=20090919062502',
            'MH3icon-Waist.png': 'https://static.wikia.nocookie.net/monsterhunter/images/7/76/MH3icon-Waist.png/revision/latest?cb=20090919062521',
            'MH3icon-Leggings.png': 'https://static.wikia.nocookie.net/monsterhunter/images/5/5b/MH3icon-Leggings.png/revision/latest?cb=20090919062536',
            'MH3icon-Accessory.png': 'https://static.wikia.nocookie.net/monsterhunter/images/d/d9/MH3icon-Accessory.png/revision/latest?cb=20090930072001'
        };

        const MONSTER_IMAGE_URLS = {
            'Zoh Shia': 'https://static.wikia.nocookie.net/monsterhunter/images/2/2e/MHWilds-Zoh_Shia_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250326022025',
            'Guardian Doshaguma': 'https://static.wikia.nocookie.net/monsterhunter/images/e/e1/MHWilds-Guardian_Doshaguma_Custom_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250704185728',
            'Rey Dau': 'https://static.wikia.nocookie.net/monsterhunter/images/5/56/MHWilds-Rey_Dau_Render_001.png/revision/latest/scale-to-width-down/220?cb=20240820200505',
            'Lala Barina': 'https://static.wikia.nocookie.net/monsterhunter/images/7/77/MHWilds-Lala_Barina_Render_001.png/revision/latest/scale-to-width-down/167?cb=20240820200135',
            'Congalala': 'https://static.wikia.nocookie.net/monsterhunter/images/6/64/MHWilds-Congalala_Render_001.png/revision/latest/scale-to-width-down/186?cb=20250205200933',
            'Nerscylla': 'https://static.wikia.nocookie.net/monsterhunter/images/0/09/MHWilds-Nerscylla_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250204230822',
            'Gore Magala': 'https://static.wikia.nocookie.net/monsterhunter/images/1/19/MHWilds-Gore_Magala_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250204234508',
            'Gravios': 'https://static.wikia.nocookie.net/monsterhunter/images/d/d0/MHWilds-Gravios_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250121213257',
            'Guardian Arkveld': 'https://static.wikia.nocookie.net/monsterhunter/images/7/7b/MHWilds-Guardian_Arkveld_Custom_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250326172906',
            'Quematrice': 'https://static.wikia.nocookie.net/monsterhunter/images/0/04/MHWilds-Quematrice_Render_001.png/revision/latest/scale-to-width-down/191?cb=20240925011001',
            'Doshaguma': 'https://static.wikia.nocookie.net/monsterhunter/images/a/a6/MHWilds-Doshaguma_Render_001.png/revision/latest/scale-to-width-down/220?cb=20240531055247',
            'Balahara': 'https://static.wikia.nocookie.net/monsterhunter/images/b/ba/MHWilds-Balahara_Render_001.png/revision/latest/scale-to-width-down/205?cb=20240607225801',
            'Rathian': 'https://static.wikia.nocookie.net/monsterhunter/images/5/52/RathianWilds.png/revision/latest/scale-to-width-down/220?cb=20250207223610',
            'Chatacabra': 'https://static.wikia.nocookie.net/monsterhunter/images/2/23/MHWilds-Chatacabra_Render_001.png/revision/latest/scale-to-width-down/220?cb=20240531055327',
            'Mizutsune': 'https://static.wikia.nocookie.net/monsterhunter/images/6/61/MHWilds-Mizutsune_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250325144419',
            'Guardian Fulgur Anjanath': 'https://static.wikia.nocookie.net/monsterhunter/images/b/b7/MHWilds-Guardian_Fulgur_Anjanath_Custom_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250413214828',
            'Hirabami': 'https://static.wikia.nocookie.net/monsterhunter/images/e/ec/MHWilds-Hirabami_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250204230627',
            'Yian Kut-Ku': 'https://static.wikia.nocookie.net/monsterhunter/images/7/7e/YianKutKuWilds.png/revision/latest/scale-to-width-down/188?cb=20250204233513',
            'Rompopolo': 'https://static.wikia.nocookie.net/monsterhunter/images/f/f1/MHWilds-Rompopolo_Render_001.png/revision/latest/scale-to-width-down/220?cb=20241023142128',
            'Arkveld': 'https://static.wikia.nocookie.net/monsterhunter/images/3/3a/MHWilds-Arkveld_Render_001.png/revision/latest/scale-to-width-down/220?cb=20240925010255',
            'Ajarakan': 'https://static.wikia.nocookie.net/monsterhunter/images/a/ae/MHWilds-Ajarakan_Render_001.png/revision/latest/scale-to-width-down/220?cb=20241023142115',
            'Gypceros': 'https://static.wikia.nocookie.net/monsterhunter/images/e/e4/MHWilds-Gypceros_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250108202039',
            'Xu Wu': 'https://static.wikia.nocookie.net/monsterhunter/images/7/7b/MHWilds-Xu_Wu_Render_001.png/revision/latest/scale-to-width-down/220?cb=20260513010353',
            'Guardian Rathalos': 'https://static.wikia.nocookie.net/monsterhunter/images/6/6d/MHWilds-Guardian_Rathalos_Custom_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250413160814',
            'Uth Duna': 'https://static.wikia.nocookie.net/monsterhunter/images/c/c1/MHWilds-Uth_Duna_Render_001.png/revision/latest/scale-to-width-down/220?cb=20240925012227',
            'Jin Dahaad': 'https://static.wikia.nocookie.net/monsterhunter/images/c/c1/MHWilds-Jin_Dahaad_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250212222640',
            'Nu Udra': 'https://static.wikia.nocookie.net/monsterhunter/images/c/cf/MHWilds-Nu_Udra_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250202192746',
            'Guardian Ebony Odogaron': 'https://static.wikia.nocookie.net/monsterhunter/images/0/07/MHWilds-Guardian_Ebony_Odogaron_Custom_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250414211515',
            'Rathalos': 'https://static.wikia.nocookie.net/monsterhunter/images/1/12/MHWilds-Rathalos_Render_001.png/revision/latest/scale-to-width-down/208?cb=20251112050049',
            'Blangonga': 'https://static.wikia.nocookie.net/monsterhunter/images/6/6b/MHWilds_Blangonga_Render_no_BG.png/revision/latest/scale-to-width-down/220?cb=20250218150750',
            'Lagiacrus': 'https://static.wikia.nocookie.net/monsterhunter/images/7/77/MHWilds-Lagiacrus_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250626232337',
            'Seregios': 'https://static.wikia.nocookie.net/monsterhunter/images/e/ed/MHWilds-Seregios_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250626233511',
            'Omega Planetes': 'https://static.wikia.nocookie.net/monsterhunter/images/4/48/MHWilds-Omega_Planetes_Render_001.png/revision/latest/scale-to-width-down/220?cb=20250925070012',
            'Gogmazios': 'https://static.wikia.nocookie.net/monsterhunter/images/3/36/MHWilds-Gogmazios_Render_001.png/revision/latest/scale-to-width-down/220?cb=20251211101930'
        };

        function wikiFileUrl(fileName) {
            if (Object.prototype.hasOwnProperty.call(WIKI_FILE_URLS, fileName)) {
                return `/assets/equipment-icons/${encodeURIComponent(fileName)}`;
            }
            return fileName;
        }

        function setIconBox(boxId, fileNames, fallbackText) {
            const box = document.getElementById(boxId);
            if (!box) return;
            const files = (Array.isArray(fileNames) ? fileNames : [fileNames]).filter(Boolean);
            box.innerHTML = '';
            if (!files.length) {
                box.innerHTML = `<span class="game-icon-fallback">${fallbackText}</span>`;
                return;
            }
            const img = document.createElement('img');
            img.className = 'game-icon';
            img.alt = fallbackText;
            let idx = 0;
            img.onerror = () => {
                idx += 1;
                if (idx < files.length) {
                    img.src = wikiFileUrl(files[idx]);
                } else {
                    box.innerHTML = `<span class="game-icon-fallback">${fallbackText}</span>`;
                }
            };
            img.src = wikiFileUrl(files[idx]);
            box.appendChild(img);
        }

        function weaponIconFiles(type = '') {
            return {
                'Great Sword': ['Great Sword Icon White.png'],
                'Long Sword': ['Long Sword Icon White.png'],
                'Sword & Shield': ['Sword and Shield Icon White.png'],
                'Dual Blades': ['Dual Blades Icon White.png'],
                'Hammer': ['Hammer Icon White.png'],
                'Hunting Horn': ['Hunting Horn Icon White.png'],
                'Lance': ['Lance Icon White.png'],
                'Gunlance': ['Gunlance Icon White.png'],
                'Switch Axe': ['Switch Axe Icon White.png'],
                'Charge Blade': ['Charge Blade Icon White.png'],
                'Insect Glaive': ['Insect Glaive Icon White.png'],
                'Light Bowgun': ['Light Bowgun Icon White.png'],
                'Heavy Bowgun': ['Heavy Bowgun Icon White.png'],
                'Bow': ['Bow Icon White.png']
            }[type] || [];
        }

        function armorIconFiles(slot = '') {
            return {
                helm: ['MH3icon-Helm.png'],
                chest: ['MH3icon-Plate.png'],
                arms: ['MH3icon-Gauntlets.png'],
                waist: ['MH3icon-Waist.png'],
                legs: ['MH3icon-Leggings.png']
            }[slot] || [];
        }

        function monsterIconFiles(monsterName = '') {
            if (typeof localAsset === 'function') {
                const local = localAsset('monster', monsterName);
                if (local) return [local];
            }
            if (!monsterName) return [];
            return [`/api/equipment-photo/monster?name=${encodeURIComponent(monsterName)}`];
        }

        function findSkillData(skillName = '') {
            return GAME_DATA?.skills?.find(s => s.name_en === skillName || s.name === skillName);
        }

        function skillIconKind(skillName = '') {
            const found = findSkillData(skillName);
            return (found?.icon?.kind || skillIcon(skillName)).slice(0, 3).toUpperCase();
        }

        function skillIconMarkup(skillName = '') {
            return `<span class="skill-kind-icon" title="Categoria MHDB: ${skillIconKind(skillName)}">${skillIconKind(skillName)}</span>`;
        }

        function activeSkillIconMarkup(skillName, idx) {
            const fallback = skillIconKind(skillName);
            return `
                <span class="skill-kind-icon" id="active-skill-icon-${idx}" title="${escapeHtml(skillDisplayName(skillName))}">
                    <img class="game-icon" src="/api/equipment-photo/skill?name=${encodeURIComponent(skillName)}" alt="${escapeHtml(skillDisplayName(skillName))}" onerror="handleSkillIconError(this, '${fallback}')">
                </span>
            `;
        }

        function handleSkillIconError(image, fallback) {
            const box = image?.parentElement;
            if (!box) return;
            box.innerHTML = `<span class="game-icon-fallback">${escapeHtml(fallback)}</span>`;
        }

        function handleEquipmentPhotoError(image) {
            const art = image?.parentElement;
            if (!art) return;
            image.remove();
            art.classList.remove('has-photo');
            art.classList.add('no-photo');
        }

        function skillDisplayName(skill) {
            const found = findSkillData(skill);
            if (!found) return skill;
            return SITE_LOCALE === 'pt' ? (found.name || skill) : (found.name_en || found.name || skill);
        }

        function skillRankDisplayName(skillName, rankName) {
            if (!rankName) return '';
            const skill = findSkillData(skillName);
            const rank = skill?.ranks?.find(item => item.name_en === rankName || item.name === rankName);
            return SITE_LOCALE === 'pt' ? (rank?.name || rankName) : (rank?.name_en || rankName);
        }

        function skillSourceIconMarkup(source) {
            const selectedWeapon = document.getElementById('sel-weapon')?.value === 'custom_gog_weapon' ? CUSTOM_GOG : getSelected('sel-weapon', GAME_DATA?.weapons || []);
            let files = [];
            let fallback = 'EQ';
            if (source.slot_type && armorIconFiles(source.slot_type).length) {
                files = armorIconFiles(source.slot_type);
                fallback = armorIcon(source.slot_type).slice(0, 2);
            } else if (source.kind === 'weapon') {
                files = weaponIconFiles(selectedWeapon?.weapon_type);
                fallback = weaponIcon(selectedWeapon?.weapon_type);
            } else if (source.kind === 'talisman') {
                files = ['MH3icon-Accessory.png'];
                fallback = 'TAL';
            } else if (source.kind === 'decoration') {
                files = ['MH3icon-Accessory.png'];
                fallback = 'JO';
            }
            const collections = source.kind === 'weapon'
                ? GAME_DATA?.weapons
                : source.kind === 'armor'
                    ? GAME_DATA?.armors
                    : source.kind === 'talisman'
                        ? GAME_DATA?.talismans
                        : source.kind === 'decoration'
                            ? GAME_DATA?.decorations
                            : [];
            const localizedSource = collections?.find(item => item.name_en === source.name || item.name === source.name);
            const title = `${displayName(localizedSource) || source.name || 'Equipamento'} (+${source.level || 1})`;
            const content = files.length
                ? `<img src="${wikiFileUrl(files[0])}" alt="${escapeHtml(fallback)}">`
                : `<span>${escapeHtml(fallback)}</span>`;
            return `<span class="skill-source-icon" title="${escapeHtml(title)}">${content}</span>`;
        }

        function skillSourcesMarkup(sources = []) {
            return `<span class="skill-sources">${sources.map(skillSourceIconMarkup).join('')}</span>`;
        }

        function skillRequirementText(detail) {
            if (!detail.required_pieces) return SITE_LOCALE === 'en' ? `Lv.${detail.level}` : `Nv.${detail.level}`;
            if (!detail.active) return SITE_LOCALE === 'en'
                ? `${detail.level}/${detail.required_pieces} pieces · Inactive`
                : `${detail.level}/${detail.required_pieces} peças · Inativa`;
            const rank = skillRankDisplayName(detail.name, detail.active_rank_name);
            return SITE_LOCALE === 'en'
                ? `${detail.level} pieces${rank ? ` · ${rank}` : ' · Active'}`
                : `${detail.level} peças${rank ? ` · ${rank}` : ' · Ativa'}`;
        }

        function weaponTypeDisplay(item) {
            const type = item?.weapon_type || '';
            if (SITE_LOCALE === 'pt') return item?.weapon_type_display || WEAPON_TYPE_PT_UI[type] || type;
            return type;
        }

        function optionLabel(item) {
            const name = displayName(item);
            if (item.weapon_type) return `${name} · ${weaponTypeDisplay(item)}`;
            if (item.slot_type) {
                const slotName = SITE_LOCALE === 'pt'
                    ? (item.slot_type_display || SLOT_PT_UI[item.slot_type] || item.slot_type)
                    : (SLOT_EN_UI[item.slot_type] || item.slot_type);
                return `${name} · ${slotName}`;
            }
            if (item.skill || item.skill_display) return `${name}`;
            if ((item.slots || []).length) return `✦ ${name}`;
            return name;
        }

        function escapeHtml(value) {
            return String(value ?? '').replace(/[&<>"']/g, ch => ({
                '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
            }[ch]));
        }

        function createUiElement(tag, className = '', text = null) {
            const element = document.createElement(tag);
            if (className) element.className = className;
            if (text !== null && text !== undefined) element.textContent = String(text);
            return element;
        }

        function createActionButton(label, className, handler) {
            const button = createUiElement('button', className, label);
            button.type = 'button';
            button.style.padding = '4px 8px';
            button.style.fontSize = '0.75rem';
            button.addEventListener('click', handler);
            return button;
        }

        function replaceWithMessage(container, message, className = 'mini-item muted') {
            container.replaceChildren(createUiElement('div', className, message));
        }

        function fallbackArtMarkup(kind, item) {
            const iconFiles = kind === 'weapon'
                ? weaponIconFiles(item?.weapon_type)
                : kind === 'talisman'
                    ? ['MH3icon-Accessory.png']
                    : armorIconFiles(item?.slot_type);
            const fallback = kind === 'weapon' ? weaponIcon(item?.weapon_type) : kind === 'talisman' ? 'TAL' : armorIcon(item?.slot_type);
            return `<div class="equipment-icon">${iconFiles.length ? `<img class="game-icon" src="${wikiFileUrl(iconFiles[0])}" alt="${fallback}">` : `<span class="game-icon-fallback">${fallback}</span>`}</div>`;
        }

        function englishName(item) {
            return item?.name_en || item?.name || '';
        }

        function armorSetTitle(name) {
            const cleaned = String(name || '')
                .replace(/\s+(Helm|Helmet|Crown|Mask|Headgear|Hat|Hood|Mail|Plate|Chest|Vest|Shroud|Jacket|Suit|Vambraces|Armguards|Braces|Guards|Coil|Waist|Faulds|Overlay|Coat|Tasset|Greaves|Boots|Leggings|Pants)\b/gi, '')
                .replace(/\s+/g, ' ')
                .trim();
            return cleaned ? `${cleaned} Armor (MHWilds)` : '';
        }

        function wikiImageCandidates(item, kind) {
            const name = englishName(item);
            if (!name || name === '(None)' || name === '(Nenhum)') return [];
            if (kind === 'weapon') return [`${name} (MHWilds)`, name];
            if (kind === 'armor') return [armorSetTitle(name), `${name} (MHWilds)`, name].filter(Boolean);
            return [];
        }

        async function fetchWikiImageForTitles(titles) {
            for (const title of titles) {
                if (WIKI_IMAGE_CACHE[title]) return WIKI_IMAGE_CACHE[title];
                try {
                    const url = `https://monsterhunter.fandom.com/api.php?action=query&titles=${encodeURIComponent(title)}&prop=pageimages&pithumbsize=260&format=json&origin=*`;
                    const res = await fetch(url);
                    if (!res.ok) continue;
                    const data = await res.json();
                    const page = Object.values(data.query?.pages || {})[0];
                    const image = page?.thumbnail?.source || '';
                    WIKI_IMAGE_CACHE[title] = image;
                    localStorage.setItem('mhwilds_wiki_image_cache', JSON.stringify(WIKI_IMAGE_CACHE));
                    if (image) return image;
                } catch {
                    WIKI_IMAGE_CACHE[title] = '';
                }
            }
            return '';
        }

        function cachedProxyImage(key) {
            const value = WIKI_IMAGE_CACHE[key] || '';
            return value.startsWith('/api/image-proxy') ? value : '';
        }

        async function fetchArmorEquipmentImage(item) {
            const name = englishName(item);
            if (!name || name === '(None)' || name === '(Nenhum)') return '';
            const key = `armor:${name}`;
            const cached = cachedProxyImage(key);
            if (cached) return cached;
            try {
                const res = await fetch(`/api/equipment-image/armor?name=${encodeURIComponent(name)}`);
                if (!res.ok) return '';
                const data = await res.json();
                const image = data.image_url || '';
                WIKI_IMAGE_CACHE[key] = image;
                localStorage.setItem('mhwilds_wiki_image_cache', JSON.stringify(WIKI_IMAGE_CACHE));
                return image;
            } catch {
                return '';
            }
        }

        async function fetchWeaponEquipmentImage(item) {
            const name = englishName(item);
            if (!name || name === '(None)' || name === '(Nenhum)') return '';
            const key = `weapon:${name}`;
            const cached = cachedProxyImage(key);
            if (cached) return cached;
            try {
                const res = await fetch(`/api/equipment-image/weapon?name=${encodeURIComponent(name)}`);
                if (!res.ok) return '';
                const data = await res.json();
                const image = data.image_url || '';
                WIKI_IMAGE_CACHE[key] = image;
                localStorage.setItem('mhwilds_wiki_image_cache', JSON.stringify(WIKI_IMAGE_CACHE));
                return image;
            } catch {
                return '';
            }
        }

        async function fetchSkillEquipmentImage(skillName) {
            const key = `skill:${skillName}`;
            const cached = cachedProxyImage(key);
            if (cached) return cached;
            try {
                const res = await fetch(`/api/equipment-image/skill?name=${encodeURIComponent(skillName)}`);
                if (!res.ok) return '';
                const data = await res.json();
                const image = data.image_url || '';
                WIKI_IMAGE_CACHE[key] = image;
                localStorage.setItem('mhwilds_wiki_image_cache', JSON.stringify(WIKI_IMAGE_CACHE));
                return image;
            } catch {
                return '';
            }
        }

        function equipmentPreviewItems() {
            const usingCustomGog = Boolean(CUSTOM_GOG && document.getElementById('sel-weapon')?.value === 'custom_gog_weapon');
            return [
                { kind: 'weapon', label: uiText('Arma'), is_gog: usingCustomGog, item: usingCustomGog ? CUSTOM_GOG : getSelected('sel-weapon', GAME_DATA?.weapons || []) },
                { kind: 'armor', slotType: 'helm', label: SITE_LOCALE === 'en' ? 'Head' : 'Elmo', item: getSelected('sel-helm', GAME_DATA?.armors || []) },
                { kind: 'armor', slotType: 'chest', label: SITE_LOCALE === 'en' ? 'Chest' : 'Peitoral', item: getSelected('sel-chest', GAME_DATA?.armors || []) },
                { kind: 'armor', slotType: 'arms', label: SITE_LOCALE === 'en' ? 'Arms' : 'Braços', item: getSelected('sel-arms', GAME_DATA?.armors || []) },
                { kind: 'armor', slotType: 'waist', label: SITE_LOCALE === 'en' ? 'Waist' : 'Cintura', item: getSelected('sel-waist', GAME_DATA?.armors || []) },
                { kind: 'armor', slotType: 'legs', label: SITE_LOCALE === 'en' ? 'Legs' : 'Pernas', item: getSelected('sel-legs', GAME_DATA?.armors || []) },
                { kind: 'talisman', label: SITE_LOCALE === 'en' ? 'Talisman' : 'Talismã', item: CUSTOM_TALISMAN && document.getElementById('sel-talisman')?.value === 'custom_talisman' ? CUSTOM_TALISMAN : getSelected('sel-talisman', GAME_DATA?.talismans || []) }
            ];
        }

        function equipmentPhotoSrc(entry) {
            if (entry.is_gog) {
                const gogWeapon = GOGMA_WEAPON_BY_TYPE[entry.item?.weapon_type] || GOGMA_WEAPON_BY_TYPE['Great Sword'];
                if (typeof localAsset === 'function' && localAsset('weapon', gogWeapon)) return localAsset('weapon', gogWeapon);
                return `/api/equipment-photo/weapon?name=${encodeURIComponent(gogWeapon)}`;
            }
            const name = englishName(entry.item);
            if (!name || name === '(None)' || name === '(Nenhum)' || entry.kind === 'talisman') return '';
            const route = entry.kind === 'armor' ? 'armor' : 'weapon';
            if (typeof localAsset === 'function') {
                const exact = localAsset(route, name);
                if (exact) return exact;
                if (route === 'armor') {
                    const base = name.replace(/\s+[αβγ]$/, '').trim();
                    for (const variant of [base, `${base} α`, `${base} β`, `${base} γ`]) {
                        const hit = localAsset('armor', variant);
                        if (hit) return hit;
                    }
                }
            }
            return `/api/equipment-photo/${route}?name=${encodeURIComponent(name)}`;
        }

        async function renderEquipmentPreviews() {
            if (typeof renderEquipmentRows === 'function') { renderEquipmentRows(); return; }
            const grid = document.getElementById('equipment-preview-grid');
            if (!grid || !GAME_DATA) return;
            const items = equipmentPreviewItems();
            grid.innerHTML = items.map((entry, idx) => {
                const name = displayName(entry.item) || entry.label;
                const armorType = SITE_LOCALE === 'en'
                    ? (SLOT_EN_UI[entry.item?.slot_type] || entry.label)
                    : (entry.item?.slot_type_display || SLOT_PT_UI[entry.item?.slot_type] || entry.label);
                const armorMeta = entry.kind === 'armor' && entry.item?.rarity
                    ? ` · R${entry.item.rarity}${TRANSCENDED_ARMOR.has(entry.slotType) ? (SITE_LOCALE === 'en' ? ' · Transcended' : ' · Transcendida') : ''}`
                    : '';
                const type = entry.kind === 'weapon' ? weaponTypeDisplay(entry.item) : entry.kind === 'armor' ? `${armorType}${armorMeta}` : (SITE_LOCALE === 'en' ? 'Talisman' : 'Talismã');
                const photoSrc = equipmentPhotoSrc(entry);
                const wikiType = entry.kind === 'talisman' ? 'talisman' : entry.kind;
                const wikiEntry = entry.item?.id ? findWikiEntry(wikiType, entry.item.id) : null;
                const wikiAction = wikiEntry
                    ? `onclick="openWikiEntry('${wikiType}', '${escapeHtml(String(entry.item.id))}')" title="${escapeHtml(SITE_LOCALE === 'en' ? 'Open this definition in the Hunter Wiki' : 'Abrir definição na Wiki do Caçador')}"`
                    : '';
                return `
                    <div class="equipment-preview-card" id="equipment-preview-${idx}" ${wikiAction} ${wikiEntry ? 'role="button" tabindex="0" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();this.click()}"' : ''}>
                        <div class="equipment-preview-art ${photoSrc ? 'has-photo' : 'no-photo'}">
                            ${photoSrc ? `<img src="${photoSrc}" alt="${escapeHtml(name)}" loading="lazy" onerror="handleEquipmentPhotoError(this)">` : ''}
                            ${fallbackArtMarkup(entry.kind, entry.item)}
                        </div>
                        <div class="equipment-preview-info">
                            <div class="equipment-preview-name" title="${escapeHtml(name)}">${escapeHtml(name)}</div>
                            <div class="equipment-preview-type">${escapeHtml(type)}</div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function updateEquipmentIconPreviews() {
            const weapon = CUSTOM_GOG && document.getElementById('sel-weapon')?.value === 'custom_gog_weapon'
                ? CUSTOM_GOG
                : getSelected('sel-weapon', GAME_DATA?.weapons || []);
            setIconBox('icon-box-weapon', weaponIconFiles(weapon?.weapon_type), weaponIcon(weapon?.weapon_type));
            setIconBox('icon-box-helm', armorIconFiles('helm'), armorIcon('helm'));
            setIconBox('icon-box-chest', armorIconFiles('chest'), armorIcon('chest'));
            setIconBox('icon-box-arms', armorIconFiles('arms'), armorIcon('arms'));
            setIconBox('icon-box-waist', armorIconFiles('waist'), armorIcon('waist'));
            setIconBox('icon-box-legs', armorIconFiles('legs'), armorIcon('legs'));
            setIconBox('icon-box-talisman', ['MH3icon-Accessory.png'], 'TAL');
        }

        function renderGogWeaponPreview() {
            const target = document.getElementById('gog-weapon-preview');
            const type = document.getElementById('gog-type')?.value || 'Great Sword';
            if (!target) return;
            const name = GOGMA_WEAPON_BY_TYPE[type] || GOGMA_WEAPON_BY_TYPE['Great Sword'];
            const typeLabel = weaponTypeDisplay({ weapon_type: type });
            const detail = SITE_LOCALE === 'en'
                ? 'Gogma Artian appearance used for this weapon class.'
                : 'Aparência Gogartiana usada para esta classe de arma.';
            const src = (typeof localAsset === 'function' && localAsset('weapon', name))
                || `/api/equipment-photo/weapon?name=${encodeURIComponent(name)}`;
            target.innerHTML = `
                <div class="gog-weapon-preview-art"><img src="${src}" alt="${escapeHtml(name)}" onerror="handleEquipmentPhotoError(this)"></div>
                <div><strong>${escapeHtml(name)}</strong><small>${escapeHtml(typeLabel)} · ${detail}</small></div>
            `;
        }

        function monsterDisplayName(monster) {
            return monster?.name || (SITE_LOCALE === 'en' ? 'Custom Monster' : 'Monstro Customizado');
        }

        function normalizedMonsterName(name = '') {
            return String(name).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase().trim();
        }

        function kiranicoMonsterUrl(monster) {
            if (!monster || monster.id === 'custom_monster') return '';
            const aliases = {
                'doshaguma guardiao': 'guardian-doshaguma', 'guardian doshaguma': 'guardian-doshaguma',
                'arkveld guardiao': 'guardian-arkveld', 'guardian arkveld': 'guardian-arkveld',
                'anjanath fulgurante guardiao': 'guardian-fulgur-anjanath', 'guardian fulgur anjanath': 'guardian-fulgur-anjanath',
                'rathalos guardiao': 'guardian-rathalos', 'guardian rathalos': 'guardian-rathalos',
                'odogaron negro guardiao': 'guardian-ebony-odogaron', 'guardian ebony odogaron': 'guardian-ebony-odogaron'
            };
            const key = normalizedMonsterName(monster.name_en || monster.name);
            const slug = aliases[key] || key.replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
            return slug ? `https://mhwilds.kiranico.com/data/monsters/${slug}` : '';
        }

        function renderMonsterHero(monster) {
            const art = document.getElementById('monster-hero-art');
            if (!art) return;
            if (typeof renderMonsterImage === 'function') { renderMonsterImage(art, monster); return; }
            const name = monsterDisplayName(monster);
            const fallback = name.split(/\s+/).map(word => word[0]).join('').slice(0, 3).toUpperCase();
            const source = monster?.id === 'custom_monster' ? '' : monsterIconFiles(monster?.name_en || monster?.name)[0];
            art.innerHTML = '';
            if (!source) {
                art.innerHTML = `<span class="game-icon-fallback">${escapeHtml(fallback)}</span>`;
                return;
            }
            const image = document.createElement('img');
            image.src = source;
            image.alt = name;
            image.onerror = () => {
                if (image.parentElement === art) art.innerHTML = `<span class="game-icon-fallback">${escapeHtml(fallback)}</span>`;
            };
            art.appendChild(image);
        }

        function renderMonsterIdentity(monster) {
            const name = monsterDisplayName(monster);
            const title = document.getElementById('monster-card-name');
            const meta = document.getElementById('monster-card-meta');
            const hz = monster?.weighted_hitzone || {};
            const bestPhysical = Math.max(Number(hz.sever || 0), Number(hz.blunt || 0), Number(hz.shot || 0));
            const bestElement = bestElementForPart(hz);
            if (title) title.innerText = name;
            if (meta) meta.innerText = SITE_LOCALE === 'en'
                ? `Best physical ${formatMonsterValue(bestPhysical)} · Best element ${bestElement?.[0] || '-'}`
                : `Melhor físico ${formatMonsterValue(bestPhysical)} · Melhor elemento ${bestElement?.[0] || '-'}`;
            renderMonsterHero(monster);
            const kiranicoLink = document.getElementById('monster-kiranico-link');
            const sourceUrl = kiranicoMonsterUrl(monster);
            if (kiranicoLink) {
                kiranicoLink.href = sourceUrl || '#';
                kiranicoLink.hidden = !sourceUrl;
            }
        }

        function openSelectedMonsterWiki() {
            const monster = currentMonsterForChart();
            if (monster?.id === 'custom_monster') return openWikiEntry('mechanic', 'hitzone');
            return openWikiEntry('monster', String(monster?.id || ''));
        }

        async function loadGameData(keepSelections = false) {
            try {
                document.getElementById('language-select').value = SITE_LOCALE;
                translateStaticInterface();
                updatePlannerUI();
                renderComparatorTable();
                const [res, presetRes] = await Promise.all([
                    fetch(`/api/data/all?locale=${SITE_LOCALE}`),
                    fetch('/api/meta-presets')
                ]);
                if (!res.ok) throw new Error('Catálogo indisponível.');
                GAME_DATA = await res.json();
                META_PRESETS = presetRes.ok ? await presetRes.json() : [];
                normalizeGameData();
                populateDropdowns(keepSelections);
                populateGogReinforcements();
                renderGogWeaponPreview();
                populateOptimizerSkills();
                updateEquipmentIconPreviews();
                renderEquipmentPreviews();
                renderSkillRegistryData();
                loadWishlist();
                onMonsterChange();
                renderMonsterIntel();
                recalculate();
                translateStaticInterface();
                  updatePlannerUI();
                  if (document.getElementById('screen-comparator').classList.contains('active')) refreshSharedComparison();
                if (typeof refreshUptimeVisibility === 'function') refreshUptimeVisibility();
            } catch (err) {
                console.error("Erro ao carregar dados:", err);
            }
        }

        function byName(items) {
            return [...items].sort((a, b) => (a.name || '').localeCompare(b.name || '', 'pt-BR', { sensitivity: 'base' }));
        }

        function normalizeGameData() {
            GAME_DATA.weapons = byName(GAME_DATA.weapons || []);
            GAME_DATA.armors = byName(GAME_DATA.armors || []);
            GAME_DATA.decorations = byName(GAME_DATA.decorations || []);
            GAME_DATA.talismans = byName(GAME_DATA.talismans || []);
            GAME_DATA.monsters = byName(GAME_DATA.monsters || []);
            DECORATION_BY_ID = new Map(GAME_DATA.decorations.map(decoration => [decoration.id, decoration]));
            DECO_BY_KIND_LEVEL = { weapon: {}, armor: {} };
            for (const kind of ['weapon', 'armor']) {
                for (let level = 1; level <= 4; level += 1) {
                    DECO_BY_KIND_LEVEL[kind][level] = GAME_DATA.decorations.filter(
                        decoration => decoration.kind === kind && decoration.level <= level
                    );
                }
            }
            try {
                WIKI_IMAGE_CACHE = JSON.parse(localStorage.getItem('mhwilds_wiki_image_cache') || '{}');
            } catch {
                WIKI_IMAGE_CACHE = {};
            }
        }

        function itemMatches(item, text, fields = []) {
            if (!text) return true;
            const haystack = [
                item.name, item.id, item.weapon_type, item.weapon_type_display, item.slot_type, item.slot_type_display, item.set_bonus_group,
                ...(Object.keys(item.skills || {})),
                ...Object.keys(item.skills_display || {}),
                item.skill, item.skill_display
            ].concat(fields.map(f => item[f])).filter(Boolean).join(' ').toLowerCase();
            return haystack.includes(text.toLowerCase());
        }

        function populateDropdowns(keepValues = false) {
            const current = keepValues ? {
                weapon: document.getElementById('sel-weapon')?.value,
                helm: document.getElementById('sel-helm')?.value,
                chest: document.getElementById('sel-chest')?.value,
                arms: document.getElementById('sel-arms')?.value,
                waist: document.getElementById('sel-waist')?.value,
                legs: document.getElementById('sel-legs')?.value,
                talisman: document.getElementById('sel-talisman')?.value,
                monster: document.getElementById('scenario-monster')?.value,
                optMonster: document.getElementById('opt-monster-id')?.value,
                optPart: document.getElementById('opt-target-part')?.value
            } : {};
            const weaponFilter = document.getElementById('filter-weapons')?.value || '';
            const weapons = GAME_DATA.weapons.filter(w => itemMatches(w, weaponFilter));
            const armorFor = (slot, inputId) => GAME_DATA.armors.filter(a => a.slot_type === slot && itemMatches(a, document.getElementById(inputId)?.value || ''));
            const talismanFilter = document.getElementById('filter-talisman')?.value || '';
            populateSelect('sel-weapon', [...weapons, { id: 'custom_gog_weapon', name: '⚡ ARMA GOG PERSONALIZADA :: Editor' }], current.weapon);
            populateSelect('sel-helm', armorFor('helm', 'filter-helm'), current.helm);
            populateSelect('sel-chest', armorFor('chest', 'filter-chest'), current.chest);
            populateSelect('sel-arms', armorFor('arms', 'filter-arms'), current.arms);
            populateSelect('sel-waist', armorFor('waist', 'filter-waist'), current.waist);
            populateSelect('sel-legs', armorFor('legs', 'filter-legs'), current.legs);
            populateSelect('sel-talisman', [...GAME_DATA.talismans.filter(t => itemMatches(t, talismanFilter)), { id: 'custom_talisman', name: '🔮 TALISMÃ PERSONALIZADO :: Editor' }], current.talisman);
            populateSelect('scenario-monster', GAME_DATA.monsters, current.monster);
            populateSelect('opt-monster-id', GAME_DATA.monsters, current.optMonster);
            populateOptimizerParts(current.optPart);
            populateOptimizerWeapons();
            updateEquipmentIconPreviews();
            if (keepValues) onEquipChange();
        }

        function populateOptimizerWeapons() {
            if (!GAME_DATA) return;
            const current = document.getElementById('opt-weapon-id')?.value;
            const type = document.getElementById('opt-weapon-type')?.value || 'Great Sword';
            const weaponFilter = document.getElementById('filter-opt-weapons')?.value || '';
            const weapons = GAME_DATA.weapons.filter(w => w.weapon_type === type && itemMatches(w, weaponFilter));
            populateSelect('opt-weapon-id', [{ id: '', name: '(Melhor arma do tipo)' }, ...weapons], current);
            populateOptimizerRotations();
            populateMetaPresets();
        }

        function populateOptimizerRotations() {
            if (!GAME_DATA) return;
            const select = document.getElementById('opt-rotation-id');
            if (!select) return;
            const current = select.value;
            const type = document.getElementById('opt-weapon-type')?.value || 'Great Sword';
            const rotations = (GAME_DATA.rotations || []).filter(rotation => rotation.weapon_type === type);
            select.innerHTML = rotations.map(rotation => `<option value="${escapeHtml(rotation.id)}">${escapeHtml(rotation.name)} · ${rotation.cycle_time_seconds}s</option>`).join('');
            if (rotations.some(rotation => rotation.id === current)) select.value = current;
        }

        function populateOptimizerParts(preferredValue = null) {
            const select = document.getElementById('opt-target-part');
            const monsterId = document.getElementById('opt-monster-id')?.value;
            if (!select || !GAME_DATA) return;
            const monster = (GAME_DATA.monsters || []).find(item => item.id === monsterId);
            const current = preferredValue || select.value || 'Media_Ponderada';
            const weightedLabel = SITE_LOCALE === 'en' ? 'Average of parts (approximation)' : 'Média das partes (aproximação)';
            const parts = (monster?.hitzones || []).filter(hitzone => !hitzone.is_wound);
            select.innerHTML = `<option value="Media_Ponderada">${weightedLabel}</option>` + parts.map(hitzone => (
                `<option value="${escapeHtml(hitzone.part_name)}">${escapeHtml(translatePart(hitzone.part_name))}</option>`
            )).join('');
            if (current === 'Media_Ponderada' || parts.some(hitzone => hitzone.part_name === current)) {
                select.value = current;
            }
        }

        function populateMetaPresets() {
            const select = document.getElementById('opt-meta-preset');
            if (!select) return;
            const current = select.value;
            const type = document.getElementById('opt-weapon-type')?.value || 'Great Sword';
            const presets = META_PRESETS.filter(preset => preset.weapon_type === type);
            const groups = [
                ['progression', 'Progressão'], ['normal', 'Builds gerais'], ['endgame', 'Alvos endgame']
            ];
            select.innerHTML = '<option value="">Personalizada</option>' + groups.map(([key, label]) => {
                const rows = presets.filter(preset => (preset.library_group || 'endgame') === key);
                if (!rows.length) return '';
                return `<optgroup label="${label}">${rows.map(preset => `<option value="${escapeHtml(preset.id)}">${escapeHtml(preset.name.split(' - ').slice(1).join(' - '))}</option>`).join('')}</optgroup>`;
            }).join('');
            if (presets.some(preset => preset.id === current)) select.value = current;
            syncWeaponRecommendationPolicy(META_PRESETS.find(preset => preset.id === select.value));
        }

        function skillEnglishName(skill) {
            return skill?.name_en || skill?.name || '';
        }

        function populateOptimizerSkills() {
            if (!GAME_DATA) return;
            const datalist = document.getElementById('opt-skill-options');
            if (datalist) {
                datalist.innerHTML = byName(GAME_DATA.skills || []).map(skill => {
                    const english = skillEnglishName(skill);
                    const translated = skill.name || english;
                    return `<option value="${escapeHtml(SITE_LOCALE === 'en' ? english : translated)}" label="${escapeHtml(english)}"></option>`;
                }).join('');
            }
            const box = document.getElementById('opt-skill-targets');
            if (box && !box.children.length) {
                addOptimizerSkillRow('Weakness Exploit', 5);
                addOptimizerSkillRow('Agitator', 5);
            }
        }

        function optimizerSkillMax(name) {
            const skill = (GAME_DATA?.skills || []).find(item => skillEnglishName(item) === name || item.name === name);
            const levels = (skill?.ranks || []).map(rank => Number(rank.level || 0));
            return Math.max(1, ...levels);
        }

        function updateOptimizerSkillRow(input) {
            const level = input.closest('.opt-skill-row')?.querySelector('.opt-skill-level');
            if (!level) return;
            const known = (GAME_DATA?.skills || []).some(item => skillEnglishName(item) === input.value || item.name === input.value);
            input.setCustomValidity(input.value.trim() && !known ? (SITE_LOCALE === 'en' ? 'Choose a skill from the catalog.' : 'Escolha uma habilidade do catálogo.') : '');
            level.max = optimizerSkillMax(input.value);
            if (Number(level.value) > Number(level.max)) level.value = level.max;
        }

        function addOptimizerSkillRow(skillName = '', level = 1) {
            const box = document.getElementById('opt-skill-targets');
            if (!box) return;
            const row = document.createElement('div');
            row.className = 'mini-item opt-skill-row';
            row.style.display = 'grid';
            row.style.gridTemplateColumns = 'minmax(0, 1fr) 78px 36px';
            row.style.gap = '8px';
            row.style.alignItems = 'center';
            row.innerHTML = `
                <input class="opt-skill-name" list="opt-skill-options" aria-label="${SITE_LOCALE === 'en' ? 'Skill' : 'Habilidade'}" placeholder="${SITE_LOCALE === 'en' ? 'Search skill...' : 'Pesquisar habilidade...'}" value="${escapeHtml(skillDisplayName(skillName))}">
                <input class="opt-skill-level" aria-label="${SITE_LOCALE === 'en' ? 'Required level' : 'Nível exigido'}" type="number" min="1" max="${optimizerSkillMax(skillName)}" value="${level}">
                <button class="btn btn-danger" type="button" aria-label="${SITE_LOCALE === 'en' ? 'Remove skill' : 'Remover habilidade'}" style="padding:7px;" onclick="this.closest('.opt-skill-row').remove();document.getElementById('opt-skill-targets').dispatchEvent(new Event('change',{bubbles:true}))">×</button>`;
            const input = row.querySelector('.opt-skill-name');
            input.addEventListener('change', () => updateOptimizerSkillRow(input));
            input.addEventListener('input', () => updateOptimizerSkillRow(input));
            box.appendChild(row);
        }

        function collectOptimizerSkills() {
            const targets = {};
            document.querySelectorAll('.opt-skill-row').forEach(row => {
                const name = row.querySelector('.opt-skill-name')?.value.trim();
                const level = Number(row.querySelector('.opt-skill-level')?.value || 0);
                const known = (GAME_DATA?.skills || []).find(skill => skillEnglishName(skill) === name || skill.name === name);
                if (name && level > 0 && known) targets[skillEnglishName(known)] = level;
            });
            return targets;
        }

        async function applyMetaPreset() {
            const requestId = ++OPTIMIZER_REQUEST_ID;
            OPTIMIZER_RESULTS = [];
            OPTIMIZER_SCENARIO_BASE = null;
            document.getElementById('btn-run-optimizer').disabled = false;
            document.getElementById('btn-run-optimizer').textContent = uiText('Executar Otimização');
            const id = document.getElementById('opt-meta-preset')?.value || '';
            const preset = META_PRESETS.find(item => item.id === id);
            const description = document.getElementById('opt-preset-description');
            if (!preset) {
                renderOptimizerResults();
                if (description) description.textContent = 'Escolha livre de habilidades, arma, monstro e combo.';
                hideGogRecommendation();
                hideProgressionWeaponRecommendation();
                syncWeaponRecommendationPolicy(null);
                return;
            }
            syncWeaponRecommendationPolicy(preset);
            if (description) description.textContent = preset.description;
            document.getElementById('opt-use-transcendence').checked = preset.use_transcendence !== false;
            applyOptimizerUptimePreset(preset.uptime_preset || 'realistic');
            setSelectValue('opt-monster-id', preset.monster_id);
            populateOptimizerParts('Media_Ponderada');
            const rotations = (GAME_DATA.rotations || []).filter(rotation => rotation.weapon_type === preset.weapon_type);
            const rotation = rotations.find(item => item.category === preset.rotation_category) || rotations[0];
            if (rotation) setSelectValue('opt-rotation-id', rotation.id);
            const box = document.getElementById('opt-skill-targets');
            if (box) box.innerHTML = '';
            Object.entries(preset.target_skills || {}).forEach(([skill, level]) => addOptimizerSkillRow(skill, level));
            const resultBox = document.getElementById('optimizer-results-container');
            if (resultBox) resultBox.innerHTML = '<div class="mini-item muted">Carregando build pré-calculada...</div>';
            const inputKey = optimizerInputKey();
            try {
                const response = await fetch(`/api/meta-builds/${encodeURIComponent(preset.id)}/candidates`);
                if (!response.ok) throw new Error('Cache não encontrado');
                const builds = await response.json();
                if (requestId !== OPTIMIZER_REQUEST_ID) return;
                if (inputKey !== optimizerInputKey()) throw new Error('Filtros alterados');
                OPTIMIZER_RESULTS = builds;
                if (builds[0]) {
                    OPTIMIZER_SCENARIO_BASE = structuredClone(builds[0].scenario);
                    restoreOptimizerUptimes(builds[0].scenario);
                }
                renderOptimizerResults();
                await refreshWeaponRecommendation();
                if (typeof updateWorkspaceContext === 'function') updateWorkspaceContext();
                if (requestId !== OPTIMIZER_REQUEST_ID) return;
                if (description) description.textContent = `${preset.description} As melhores variações da mesma categoria foram comparadas e carregadas do cache local.`;
            } catch {
                if (requestId !== OPTIMIZER_REQUEST_ID) return;
                if (resultBox) resultBox.innerHTML = '<div class="mini-item muted">O perfil foi aplicado. Execute a otimização para gerar uma build personalizada.</div>';
                await refreshWeaponRecommendation();
            }
        }


        function pct(id) {
            return (parseFloat(document.getElementById(id)?.value || '0') || 0) / 100.0;
        }

        function setPct(id, value) {
            const el = document.getElementById(id);
            if (el) el.value = value;
        }

        function uptimePresetValues(name) {
            const presets = {
                default: { agi: 80, burst: 90, wex: 85, maxmight: 0, peak: 0, og: 0, counter: 0, coal: 0, latent: 0, frenzy: 0, seed: 0, powder: 0, mantle: 0, resentment: 0, eleabsorb: 0, adrenaline: 0, foray: 0, ambush: 0, heroics: 0 },
                realistic: { agi: 75, burst: 85, wex: 80, maxmight: 35, peak: 45, og: 35, counter: 30, coal: 35, latent: 30, frenzy: 45, seed: 45, powder: 45, mantle: 35, resentment: 25, eleabsorb: 25, adrenaline: 35, foray: 45, ambush: 10, heroics: 0 },
                aggressive: { agi: 95, burst: 95, wex: 95, maxmight: 75, peak: 80, og: 70, counter: 70, coal: 70, latent: 65, frenzy: 75, seed: 75, powder: 75, mantle: 70, resentment: 60, eleabsorb: 60, adrenaline: 75, foray: 80, ambush: 35, heroics: 20 },
                comfort: { agi: 60, burst: 70, wex: 70, maxmight: 20, peak: 30, og: 20, counter: 20, coal: 25, latent: 20, frenzy: 30, seed: 40, powder: 35, mantle: 25, resentment: 10, eleabsorb: 20, adrenaline: 20, foray: 25, ambush: 5, heroics: 0 }
            };
            return presets[name] || presets.default;
        }

        function applyUptimePreset(name) {
            const p = uptimePresetValues(name);
            setPct('uptime-agi', p.agi); setPct('uptime-burst', p.burst); setPct('uptime-wex', p.wex);
            setPct('uptime-maxmight', p.maxmight); setPct('uptime-peak', p.peak); setPct('uptime-og', p.og);
            setPct('uptime-counter', p.counter); setPct('uptime-coal', p.coal); setPct('uptime-latent', p.latent);
            setPct('uptime-frenzy', p.frenzy); setPct('uptime-seed', p.seed); setPct('uptime-powder', p.powder);
            setPct('uptime-mantle', p.mantle); setPct('uptime-resentment', p.resentment); setPct('uptime-eleabsorb', p.eleabsorb);
            setPct('uptime-adrenaline', p.adrenaline); setPct('uptime-foray', p.foray); setPct('uptime-ambush', p.ambush); setPct('uptime-heroics', p.heroics);
            document.querySelectorAll('[data-builder-uptime]').forEach(button => button.classList.toggle('active', button.dataset.builderUptime === name));
            recalculate();
            if (typeof saveWorkspaceDraft === 'function') { useHuntScenarioInOptimizer(); invalidateComparison(); saveWorkspaceDraft(); }
        }

        function applyOptimizerUptimePreset(name) {
            const p = uptimePresetValues(name);
            CURRENT_OPT_UPTIME_PRESET = name;
            const fields = {
                agi: 'opt-up-agi', burst: 'opt-up-burst', wex: 'opt-up-wex', og: 'opt-up-og',
                foray: 'opt-up-foray', adrenaline: 'opt-up-adrenaline', ambush: 'opt-up-ambush',
                heroics: 'opt-up-heroics', frenzy: 'opt-up-frenzy', peak: 'opt-up-peak',
                resentment: 'opt-up-resentment', coal: 'opt-up-coal'
            };
            Object.entries(fields).forEach(([key, id]) => setPct(id, p[key] || 0));
            document.querySelectorAll('[data-opt-uptime]').forEach(button => button.classList.toggle('active', button.dataset.optUptime === name));
            if (typeof updateWorkspaceContext === 'function') updateWorkspaceContext();
        }

        function customMonsterPayload() {
            const hz = {
                part_name: 'Custom',
                sever: Number(document.getElementById('custom-hz-sever').value) || 0,
                blunt: Number(document.getElementById('custom-hz-blunt').value) || 0,
                shot: Number(document.getElementById('custom-hz-shot').value) || 0,
                fire: Number(document.getElementById('custom-hz-fire').value) || 0,
                water: Number(document.getElementById('custom-hz-water').value) || 0,
                thunder: Number(document.getElementById('custom-hz-thunder').value) || 0,
                ice: Number(document.getElementById('custom-hz-ice').value) || 0,
                dragon: Number(document.getElementById('custom-hz-dragon').value) || 0,
                is_wound: false
            };
            return {
                id: 'custom_monster',
                name: document.getElementById('custom-monster-name').value || 'Monstro Customizado',
                description: 'Monstro customizado definido manualmente pelo usuário.',
                weighted_hitzone: hz,
                hitzones: [hz]
            };
        }

        function toggleCustomMonster() {
            const enabled = document.getElementById('use-custom-monster').checked;
            document.getElementById('custom-monster-editor').style.display = enabled ? 'block' : 'none';
            if (enabled) document.getElementById('scenario-monster').value = GAME_DATA.monsters[0]?.id || '';
            renderMonsterIdentity(enabled ? customMonsterPayload() : currentMonsterForChart());
            renderMonsterIntel();
            renderDashboard();
            recalculate();
        }

        function applyCustomMonster() {
            renderMonsterIntel();
            recalculate();
        }

        function currentMonsterForChart() {
            if (document.getElementById('use-custom-monster')?.checked) return customMonsterPayload();
            const mId = document.getElementById('scenario-monster')?.value;
            return GAME_DATA?.monsters?.find(m => m.id === mId) || GAME_DATA?.monsters?.[0];
        }

        function elementIcon(label) {
            return {
                'Fogo': '🔥', 'Fire': '🔥', 'Água': '💧', 'Water': '💧', 'Raio': '⚡', 'Thunder': '⚡', 'Gelo': '❄️', 'Ice': '❄️', 'Dragão': '🐉', 'Dragon': '🐉',
                'Corte': '🗡️', 'Sever': '🗡️', 'Impacto': '🔨', 'Blunt': '🔨', 'Tiro': '🎯', 'Shot': '🎯'
            }[label] || '◆';
        }

        function partIcon(partName) {
            const p = (partName || '').toLowerCase();
            if (p.includes('head') || p.includes('horn') || p.includes('neck')) return '👤';
            if (p.includes('tail')) return '〰️';
            if (p.includes('wing')) return '🪽';
            if (p.includes('leg') || p.includes('foot')) return '🦵';
            if (p.includes('torso') || p.includes('body') || p.includes('chest')) return '◆';
            if (p.includes('arm')) return '💪';
            return '◇';
        }

        function translatePart(partName) {
            if (partName === 'Media_Ponderada') return SITE_LOCALE === 'en' ? 'Average of parts (approximation)' : 'Média das partes (aproximação)';
            if (SITE_LOCALE === 'en') return (partName || 'part').replaceAll('-', ' ');
            return (partName || 'parte')
                .replaceAll('-', ' ')
                .replace(/\bhead\b/g, 'cabeça')
                .replace(/\bneck\b/g, 'pescoço')
                .replace(/\btail\b/g, 'cauda')
                .replace(/\bwing\b/g, 'asa')
                .replace(/\bleft\b/g, 'esq.')
                .replace(/\bright\b/g, 'dir.')
                .replace(/\bfront\b/g, 'frontal')
                .replace(/\bhind\b/g, 'traseira')
                .replace(/\bleg\b/g, 'perna')
                .replace(/\barm\b/g, 'braço')
                .replace(/\btorso\b/g, 'torso')
                .replace(/\bwear\b/g, 'quebrada')
                .replace(/\bhide\b/g, 'exposta');
        }

        function hitzoneValueForMode(hz) {
            return Math.max(Number(hz.sever || 0), Number(hz.blunt || 0), Number(hz.shot || 0));
        }

        function bestElementForPart(hz) {
            const labels = SITE_LOCALE === 'en'
                ? ['Fire', 'Water', 'Thunder', 'Ice', 'Dragon']
                : ['Fogo', 'Água', 'Raio', 'Gelo', 'Dragão'];
            const values = [[`🔥 ${labels[0]}`, hz.fire], [`💧 ${labels[1]}`, hz.water], [`⚡ ${labels[2]}`, hz.thunder], [`❄️ ${labels[3]}`, hz.ice], [`🐉 ${labels[4]}`, hz.dragon]];
            return values.sort((a, b) => Number(b[1] || 0) - Number(a[1] || 0))[0];
        }

        function formatMonsterValue(value) {
            const numeric = Number(value || 0);
            return Number.isInteger(numeric) ? String(numeric) : numeric.toFixed(1);
        }

        function selectedHitzoneForMonster(monster) {
            const selectedPart = document.getElementById('scenario-part')?.value;
            if (!selectedPart || selectedPart === 'Media_Ponderada') return monster?.weighted_hitzone || {};
            return monster?.hitzones?.find(part => part.part_name === selectedPart) || monster?.weighted_hitzone || {};
        }

        function monsterMetricMarkup({ label, symbol, value, className, suffix = 'HZ', detail = '' }) {
            return `<article class="monster-metric ${className}">
                <div class="monster-metric-label"><span class="monster-metric-symbol">${escapeHtml(symbol)}</span><span>${escapeHtml(label)}</span></div>
                <div class="monster-metric-value"><strong>${formatMonsterValue(value)}</strong><span>${escapeHtml(suffix)}</span></div>
                ${detail ? `<small class="metric-note">${escapeHtml(detail)}</small>` : ''}
            </article>`;
        }

        function statusLevelLabel(level) {
            const localized = SITE_LOCALE === 'en'
                ? ['Resistant', 'Low', 'Medium', 'High']
                : ['Resistente', 'Baixa', 'Média', 'Alta'];
            return localized[Math.max(0, Math.min(3, Number(level || 0)))] || localized[0];
        }

        function renderMonsterIntel() {
            if (typeof renderPartTable === 'function') renderPartTable();
            const monster = currentMonsterForChart();
            const physical = document.getElementById('monster-physical-grid');
            const elemental = document.getElementById('monster-element-grid');
            const status = document.getElementById('monster-status-grid');
            const ranking = document.getElementById('monster-part-ranking');
            if (!monster || !physical || !elemental || !status || !ranking) return;
            const hz = selectedHitzoneForMonster(monster);
            const physicalRows = SITE_LOCALE === 'en'
                ? [{ label: 'Sever', symbol: 'CUT', value: hz.sever, className: 'metric-sever' }, { label: 'Blunt', symbol: 'IMP', value: hz.blunt, className: 'metric-blunt' }, { label: 'Shot', symbol: 'RNG', value: hz.shot, className: 'metric-shot' }]
                : [{ label: 'Corte', symbol: 'COR', value: hz.sever, className: 'metric-sever' }, { label: 'Impacto', symbol: 'IMP', value: hz.blunt, className: 'metric-blunt' }, { label: 'Projétil', symbol: 'DIS', value: hz.shot, className: 'metric-shot' }];
            const elementalRows = SITE_LOCALE === 'en'
                ? [{ label: 'Fire', symbol: 'FIR', value: hz.fire, className: 'metric-fire' }, { label: 'Water', symbol: 'WTR', value: hz.water, className: 'metric-water' }, { label: 'Thunder', symbol: 'THN', value: hz.thunder, className: 'metric-thunder' }, { label: 'Ice', symbol: 'ICE', value: hz.ice, className: 'metric-ice' }, { label: 'Dragon', symbol: 'DRG', value: hz.dragon, className: 'metric-dragon' }]
                : [{ label: 'Fogo', symbol: 'FOG', value: hz.fire, className: 'metric-fire' }, { label: 'Água', symbol: 'AGU', value: hz.water, className: 'metric-water' }, { label: 'Raio', symbol: 'RAI', value: hz.thunder, className: 'metric-thunder' }, { label: 'Gelo', symbol: 'GEL', value: hz.ice, className: 'metric-ice' }, { label: 'Dragão', symbol: 'DRA', value: hz.dragon, className: 'metric-dragon' }];
            const statusRows = SITE_LOCALE === 'en'
                ? [{ key: 'paralysis', label: 'Paralysis', symbol: 'PAR' }, { key: 'poison', label: 'Poison', symbol: 'PSN' }, { key: 'sleep', label: 'Sleep', symbol: 'SLP' }, { key: 'blastblight', label: 'Blast', symbol: 'BST' }]
                : [{ key: 'paralysis', label: 'Paralisia', symbol: 'PAR' }, { key: 'poison', label: 'Veneno', symbol: 'VEN' }, { key: 'sleep', label: 'Sono', symbol: 'SON' }, { key: 'blastblight', label: 'Explosão', symbol: 'EXP' }];
            physical.innerHTML = physicalRows.map(row => monsterMetricMarkup({ ...row, suffix: 'HZ' })).join('');
            elemental.innerHTML = elementalRows.map(row => monsterMetricMarkup({ ...row, suffix: 'HZ' })).join('');
            status.innerHTML = statusRows.map(row => {
                const value = Number(monster.status_weaknesses?.[row.key] || 0);
                return monsterMetricMarkup({ label: row.label, symbol: row.symbol, value, className: `metric-status level-${value}`, suffix: '/3', detail: statusLevelLabel(value) });
            }).join('');

            const parts = (monster.hitzones && monster.hitzones.length ? monster.hitzones : [monster.weighted_hitzone])
                .filter(part => !part.is_wound)
                .map(part => ({ part, score: hitzoneValueForMode(part) }))
                .sort((a, b) => b.score - a.score)
                .slice(0, 6);
            ranking.innerHTML = parts.length ? parts.map(({ part, score }, index) => `
                <div class="monster-part-row">
                    <span class="monster-part-index">${index + 1}</span>
                    <div class="monster-part-copy"><strong>${escapeHtml(translatePart(part.part_name))}</strong><small>${SITE_LOCALE === 'en' ? `Sever ${formatMonsterValue(part.sever)} · Blunt ${formatMonsterValue(part.blunt)} · Shot ${formatMonsterValue(part.shot)}` : `Corte ${formatMonsterValue(part.sever)} · Impacto ${formatMonsterValue(part.blunt)} · Projétil ${formatMonsterValue(part.shot)}`}</small></div>
                    <span class="monster-part-score">${formatMonsterValue(score)}</span>
                </div>
            `).join('') : `<span class="metric-note">${SITE_LOCALE === 'en' ? 'No parts recorded.' : 'Nenhuma parte cadastrada.'}</span>`;
        }


        function displayName(item) {
            if (!item) return '';
            if (item.name && item.name !== 'None' && item.name !== 'undefined') return item.name;
            if (item.skill_display) return item.skill_display;
            if (item.skill) return item.skill;
            return item.id || '(sem nome)';
        }

        function populateSelect(elemId, items, selectedValue = null) {
            const el = document.getElementById(elemId);
            if (!el) return;
            el.innerHTML = '';
            items.forEach(i => {
                const opt = document.createElement('option');
                opt.value = i.id;
                opt.innerText = optionLabel(i);
                el.appendChild(opt);
            });
            if (selectedValue && items.some(i => i.id === selectedValue)) el.value = selectedValue;
        }

        function showScreen(screenId, fromHistory = false) {
            if (typeof openEditor === 'function' && ['gog', 'talisman'].includes(screenId)) { openEditor(screenId); return; }
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            const screen = document.getElementById(`screen-${screenId}`);
            if (!screen) return;
            screen.classList.add('active');
            const nav = Array.from(document.querySelectorAll('.nav-item')).find(item => item.getAttribute('onclick')?.includes(`'${screenId}'`));
            if (nav) nav.classList.add('active');
            renderDashboard();
            if (screenId === 'registry') renderWikiIndex();
            onPlannerScreen(screenId);
            if (typeof routeChanged === 'function') routeChanged(screenId, fromHistory);
        }

        function onMonsterChange() {
            const mId = document.getElementById('scenario-monster').value;
            const monster = GAME_DATA.monsters.find(m => m.id === mId) || GAME_DATA.monsters[0];
            document.getElementById('monster-desc').innerText = monster.description || (SITE_LOCALE === 'en' ? 'No description available.' : 'Sem descrição disponível.');
            renderMonsterIdentity(monster);

            const partSelect = document.getElementById('scenario-part');
            partSelect.innerHTML = `<option value="Media_Ponderada">${SITE_LOCALE === 'en' ? 'Average of parts (approximation)' : 'Média das partes (aproximação)'}</option>`;
            monster.hitzones.forEach(hz => {
                const opt = document.createElement('option');
                opt.value = hz.part_name;
                opt.innerText = translatePart(hz.part_name || 'Parte');
                partSelect.appendChild(opt);
            });
            renderMonsterIntel();
            recalculate();
        }


        function customGogPreview() {
            if (!CUSTOM_GOG) return null;
            return {
                id: 'custom_gog_weapon',
                name: `${SITE_LOCALE === 'en' ? 'GOG WEAPON' : 'ARMA GOG'} :: ${CUSTOM_GOG.name || (SITE_LOCALE === 'en' ? 'Editor' : 'Editor')}`,
                slots: (CUSTOM_GOG.slots || []).filter(s => Number(s) > 0)
            };
        }

        function customTalismanPreview() {
            if (!CUSTOM_TALISMAN) return null;
            const pairs = (CUSTOM_TALISMAN.slots || []).map((level, index) => ({
                level: Number(level) || 0,
                kind: CUSTOM_TALISMAN.slot_kinds?.[index] || 'armor',
            })).filter(slot => slot.level > 0);
            return {
                id: 'custom_talisman',
                name: `${SITE_LOCALE === 'en' ? 'TALISMAN' : 'TALISMÃ'} :: ${CUSTOM_TALISMAN.name || 'Editor'}`,
                slots: pairs.map(slot => slot.level),
                slot_kinds: pairs.map(slot => slot.kind),
            };
        }

        function onEquipChange() {
            const sources = {weapon:[customGogPreview(), ...GAME_DATA.weapons], talisman:[customTalismanPreview(), ...GAME_DATA.talismans]};
            ['weapon', 'helm', 'chest', 'arms', 'waist', 'legs', 'talisman'].forEach(slot => {
                const selected = [...document.querySelectorAll(`#slots-${slot} .deco-select`)].map(select => select.value);
                renderSlots(slot, getSelected(`sel-${slot}`, sources[slot] || GAME_DATA.armors), selected);
            });
            updateEquipmentIconPreviews();
            renderEquipmentPreviews();
            recalculate();
        }

        function populateGogReinforcements() {
            const choices = SITE_LOCALE === 'en'
                ? [['', '(empty)'], ['attack_i', 'Attack I (+5 Raw)'], ['attack_ii', 'Attack II (+6 Raw)'], ['attack_iii', 'Attack III (+9 Raw)'], ['attack_ex', 'Attack EX (+12 Raw)'], ['affinity_i', 'Affinity I (+5%)'], ['affinity_ii', 'Affinity II (+6%)'], ['affinity_iii', 'Affinity III (+8%)'], ['affinity_ex', 'Affinity EX (+10%)'], ['element_i', 'Element I (+50 displayed)'], ['element_ii', 'Element II (+60 displayed)'], ['element_ex', 'Element EX (+90 displayed)'], ['sharpness_i', 'Sharpness (+30)'], ['sharpness_ex', 'Sharpness EX (+50)'], ['capacity_i', 'Capacity (+1)'], ['capacity_ex', 'Capacity EX (+2)']]
                : [['', '(vazio)'], ['attack_i', 'Ataque I (+5 Raw)'], ['attack_ii', 'Ataque II (+6 Raw)'], ['attack_iii', 'Ataque III (+9 Raw)'], ['attack_ex', 'Ataque EX (+12 Raw)'], ['affinity_i', 'Afinidade I (+5%)'], ['affinity_ii', 'Afinidade II (+6%)'], ['affinity_iii', 'Afinidade III (+8%)'], ['affinity_ex', 'Afinidade EX (+10%)'], ['element_i', 'Elemento I (+50 exibido)'], ['element_ii', 'Elemento II (+60 exibido)'], ['element_ex', 'Elemento EX (+90 exibido)'], ['sharpness_i', 'Afiamento (+30)'], ['sharpness_ex', 'Afiamento EX (+50)'], ['capacity_i', 'Capacidade (+1)'], ['capacity_ex', 'Capacidade EX (+2)']];
            document.querySelectorAll('.gog-reinforcement').forEach(select => {
                const selected = select.value;
                const kind = document.getElementById('gog-type').value;
                const rolls = GAME_DATA?.artian_rules?.element_rolls?.[kind];
                const labels = choices.map(([value, label]) => {
                    const index = ['element_i', 'element_ii', 'element_ex'].indexOf(value);
                    if (index >= 0 && rolls) label = label.replace(/\+\d+/, `+${rolls[index]}`);
                    if (value === 'sharpness_i' && kind === 'Insect Glaive') label = label.replace('+30', '+20');
                    return [value, label];
                });
                select.innerHTML = labels.map(([value, label]) => `<option value="${value}">${label}</option>`).join('');
                select.value = selected;
            });
        }

        function getSelected(elemId, list) {
            const val = document.getElementById(elemId).value;
            return list.find(x => x && x.id === val);
        }

        function effectiveArmorSlots(piece, transcended) {
            const base = [...(piece?.slots || [])];
            const affected = transcended ? ({ 5: 3, 6: 2 }[Number(piece?.rarity)] || 0) : 0;
            if (!affected) return base;
            while (base.length < affected) base.push(0);
            for (let index = 0; index < affected; index += 1) base[index] = Math.min(3, base[index] + 1);
            return base.filter(level => level > 0);
        }

        function isArmorSlot(type) {
            return ['helm', 'chest', 'arms', 'waist', 'legs'].includes(type);
        }

        function renderTranscendToggle(container, type, piece) {
            if (!isArmorSlot(type)) return;
            const rarity = Number(piece?.rarity || 0);
            if (rarity < 5) return;
            const affected = ({ 5: 3, 6: 2 }[rarity] || 0);
            const eligible = affected > 0 && !String(piece?.id || '').endsWith('_none');
            if (!eligible) TRANSCENDED_ARMOR.delete(type);

            const label = document.createElement('label');
            label.className = `transcend-toggle ${eligible ? '' : 'disabled'}`;
            label.title = eligible
                ? (SITE_LOCALE === 'en' ? `Rarity ${rarity}: upgrades ${affected} slot positions from left to right.` : `Raridade ${rarity}: melhora ${affected} posições de slot da esquerda para a direita.`)
                : rarity >= 7 ? (SITE_LOCALE === 'en' ? `Rarity ${rarity}: transcendence improves defense only.` : `Raridade ${rarity}: a transcendência melhora apenas a defesa.`) : (SITE_LOCALE === 'en' ? 'This piece receives no slots from transcendence.' : 'Esta peça não recebe slots por transcendência.');
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.id = `transcend-${type}`;
            input.disabled = !eligible;
            input.checked = eligible && TRANSCENDED_ARMOR.has(type);
            input.onchange = () => {
                const selectedDecos = Array.from(container.querySelectorAll('.deco-select')).map(select => select.value);
                if (input.checked) TRANSCENDED_ARMOR.add(type); else TRANSCENDED_ARMOR.delete(type);
                renderSlots(type, piece, selectedDecos);
                renderEquipmentPreviews();
                recalculate();
            };
            const text = document.createElement('span');
            text.textContent = eligible
                ? (SITE_LOCALE === 'en' ? `Transcended · R${rarity} · ${affected} positions` : `Transcendida · R${rarity} · ${affected} posições`)
                : (SITE_LOCALE === 'en' ? `R${rarity} · unchanged slots` : `R${rarity} · slots inalterados`);
            label.append(input, text);
            container.appendChild(label);
        }

        function slotKindFor(type, piece, index) {
            if (type === 'weapon') return 'weapon';
            if (type === 'talisman') return piece?.slot_kinds?.[index] || 'armor';
            return 'armor';
        }

        function renderSlots(type, piece, selectedDecos = []) {
            const container = document.getElementById(`slots-${type}`);
            if (!container) return;
            container.innerHTML = '';
            if (!piece) return;
            renderTranscendToggle(container, type, piece);
            const slots = isArmorSlot(type)
                ? effectiveArmorSlots(piece, TRANSCENDED_ARMOR.has(type))
                : [...(piece.slots || [])];
            if (slots.length === 0) return;

            slots.forEach((sLevel, idx) => {
                const slotKind = slotKindFor(type, piece, idx);
                const slotDiv = document.createElement('div');
                slotDiv.className = `deco-slot ${slotKind}`;
                const header = document.createElement('div');
                header.className = 'deco-slot-head';
                const kindBadge = document.createElement('span');
                kindBadge.className = 'deco-kind-badge';
                kindBadge.textContent = slotKind === 'weapon'
                    ? (SITE_LOCALE === 'en' ? 'Weapon decoration' : 'Adorno de arma')
                    : (SITE_LOCALE === 'en' ? 'Armor decoration' : 'Adorno de armadura');
                const levelBadge = document.createElement('span');
                levelBadge.className = 'deco-level-badge';
                levelBadge.textContent = `Lv${sLevel}`;
                header.append(kindBadge, levelBadge);
                const select = document.createElement('select');
                select.className = 'deco-select';
                select.dataset.slotLevel = String(sLevel);
                select.dataset.slotKind = slotKind;
                select.onchange = () => recalculate();

                const validDecos = [
                    { id: '', name: SITE_LOCALE === 'pt' ? `Lv${sLevel} vazio` : `Empty Lv${sLevel}` },
                    ...(DECO_BY_KIND_LEVEL[slotKind]?.[sLevel] || []),
                ];
                validDecos.forEach(d => {
                    const opt = document.createElement('option');
                    opt.value = d.id;
                    opt.innerText = optionLabel(d);
                    select.appendChild(opt);
                });
                if (selectedDecos[idx] && Array.from(select.options).some(option => option.value === selectedDecos[idx])) {
                    select.value = selectedDecos[idx];
                }
                const decoSearch = document.createElement('input');
                decoSearch.type = 'text';
                decoSearch.className = 'inline-select-filter';
                decoSearch.placeholder = SITE_LOCALE === 'pt'
                    ? `Filtrar adornos de ${slotKind === 'weapon' ? 'arma' : 'armadura'}...`
                    : `Filter ${slotKind} decorations...`;
                decoSearch.oninput = () => {
                    const term = decoSearch.value.toLowerCase();
                    Array.from(select.options).forEach(opt => {
                        opt.hidden = term && !opt.text.toLowerCase().includes(term);
                    });
                };
                slotDiv.append(header, decoSearch, select);
                container.appendChild(slotDiv);
            });
        }

        function recalculate(delay = 120) {
            clearTimeout(RECALC_TIMER);
            RECALC_VERSION += 1;
            if (RECALC_CONTROLLER) RECALC_CONTROLLER.abort();
            if (typeof setCalculationStatus === 'function') setCalculationStatus(SITE_LOCALE === 'en' ? 'Calculation pending' : 'Cálculo pendente', 'busy');
            return new Promise(resolve => {
                RECALC_WAITERS.push(resolve);
                RECALC_TIMER = setTimeout(async () => {
                    const waiters = RECALC_WAITERS.splice(0);
                    const result = await runRecalculate();
                    waiters.forEach(done => done(result));
                }, Number.isFinite(delay) ? delay : 120);
            });
        }

        function setCalculationStatus(label, state = '') {
            const status = document.getElementById('calculation-status');
            if (!status) return;
            status.textContent = label;
            status.className = `live-indicator ${state}`.trim();
        }

        async function runRecalculate() {
            clearTimeout(RECALC_TIMER);
            const pending = RECALC_WAITERS.splice(0);
            // A direct save/restore also settles callers waiting on the debounce.
            if (pending.length) {
                const result = await runRecalculate();
                pending.forEach(resolve => resolve(result));
                return result;
            }
            if (!GAME_DATA) return null;
            const version = ++RECALC_VERSION;
            setCalculationStatus(SITE_LOCALE === 'en' ? 'Updating calculation' : 'Atualizando cálculo', 'busy');

            const decos = Array.from(document.querySelectorAll('.deco-select')).map(s => s.value).filter(v => v !== '');
            const payload = {
                weapon_id: document.getElementById('sel-weapon').value,
                helm_id: document.getElementById('sel-helm').value,
                chest_id: document.getElementById('sel-chest').value,
                arms_id: document.getElementById('sel-arms').value,
                waist_id: document.getElementById('sel-waist').value,
                legs_id: document.getElementById('sel-legs').value,
                talisman_id: document.getElementById('sel-talisman').value,
                decorations: decos,
                transcended_armor: Array.from(TRANSCENDED_ARMOR),
                custom_weapon: CUSTOM_GOG,
                custom_talisman: CUSTOM_TALISMAN,
                scenario: currentScenarioPayload()
            };

            if (RECALC_CONTROLLER) RECALC_CONTROLLER.abort();
            RECALC_CONTROLLER = new AbortController();
            let res;
            try {
                res = await fetch('/api/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                    signal: RECALC_CONTROLLER.signal
                });
            } catch (err) {
                if (err.name === 'AbortError') return null;
                document.getElementById('slot-warnings-container').innerText = 'Erro de conexão ao calcular a build.';
                setCalculationStatus('Falha no cálculo', 'error');
                return null;
            }

            if (!res.ok) {
                const err = await res.json();
                if (version !== RECALC_VERSION) return null;
                document.getElementById('slot-warnings-container').innerText = err.detail || 'Erro ao calcular a build.';
                setCalculationStatus('Cálculo inválido', 'error');
                return null;
            }
            const result = await res.json();
            if (version !== RECALC_VERSION) return null;
            CURRENT_RESULT = result;
            updateUI(CURRENT_RESULT);
            setCalculationStatus(uiText('Cálculo atualizado'));
            if (typeof onWorkspaceResult === 'function') onWorkspaceResult(CURRENT_RESULT);
            return CURRENT_RESULT;
        }

        function updateUI(res) {
            document.getElementById('stat-dps').innerText = res.practical_dps.toFixed(1);
            document.getElementById('stat-efr').innerText = res.effective_raw.toFixed(1);
            document.getElementById('stat-aff').innerText = `${res.capped_affinity}%`;
            document.getElementById('stat-cycle').innerText = res.damage_per_cycle.toFixed(0);

            const skillsDiv = document.getElementById('active-skills-container');
            const skillDetails = res.skill_details?.length
                ? res.skill_details
                : Object.entries(res.active_skills).map(([name, level]) => ({ name, level, active:true, sources:[] }));
            skillsDiv.innerHTML = skillDetails.map((detail, idx) => {
                const requirement = detail.required_pieces
                    ? (SITE_LOCALE === 'en' ? ` (min. ${detail.required_pieces} pieces)` : ` (mín. ${detail.required_pieces} peças)`)
                    : '';
                const skill = findSkillData(detail.name);
                const wikiAction = skill ? `onclick="openWikiEntry('skill', '${escapeHtml(String(skill.id))}')" role="button" tabindex="0" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();this.click()}" title="${escapeHtml(SITE_LOCALE === 'en' ? 'Open skill definition in Hunter Wiki' : 'Abrir definição na Wiki do Caçador')}"` : '';
                return `
                    <span class="skill-tag ${detail.active ? '' : 'inactive'}" ${wikiAction}>
                        ${activeSkillIconMarkup(detail.name, idx)}
                        <span><strong>${escapeHtml(skillDisplayName(detail.name) + requirement)}</strong><small>${escapeHtml(skillRequirementText(detail))}</small></span>
                        ${skillSourcesMarkup(detail.sources)}
                    </span>
                `;
            }).join('');

            const warnDiv = document.getElementById('slot-warnings-container');
            const warningNodes = [];
            (res.slot_warnings || []).forEach((warning, index) => {
                if (index) warningNodes.push(document.createElement('br'));
                warningNodes.push(document.createTextNode(String(warning)));
            });
            warnDiv.replaceChildren(...warningNodes);
            renderDashboard();
            renderSuggestions();

        }

        function renderHitBreakdown(res) {
            const title = document.getElementById('hit-engine-title');
            if (title) title.textContent = res.rotation_name
                ? `${SITE_LOCALE === 'en' ? 'Breakdown' : 'Detalhamento'}: ${res.rotation_name}`
                : (SITE_LOCALE === 'en' ? 'Combo breakdown' : 'Detalhamento do combo');
            const tbody = document.getElementById('hits-table-body');
            if (!tbody) return;
            tbody.innerHTML = res.hits_breakdown.map(h => `
                    <tr>
                        <td><strong>${escapeHtml(h.hit_name)}</strong></td>
                        <td>${h.hit_count || 1}</td>
                        <td>${h.motion_value}</td>
                        <td>${h.physical_damage}</td>
                        <td style="color:var(--crit-color); font-weight:bold;">${h.crit_physical_damage}</td>
                        <td style="color:var(--ele-color);">${h.elemental_damage}</td>
                        <td style="color:var(--accent); font-weight:800;">${h.expected_damage}</td>
                    </tr>
                `).join('');
        }



        function renderSmartWarnings(res) {
            const box = document.getElementById('smart-warnings-container');
            if (!box || !res) return;
            const warnings = [];
            if (res.capped_affinity >= 100 && res.total_affinity > 100) warnings.push(`Afinidade passa de 100%: ${res.total_affinity}%. Parte do investimento pode estar desperdiçada.`);
            if ((res.slot_warnings || []).length) warnings.push(...res.slot_warnings);
            if (document.getElementById('sel-weapon').value === 'custom_gog_weapon' && !CUSTOM_GOG) warnings.push('Arma Gog customizada selecionada, mas não foi aplicada no editor.');
            if (document.getElementById('sel-talisman').value === 'custom_talisman' && !CUSTOM_TALISMAN) warnings.push('Talismã customizado selecionado, mas não foi aplicado no editor.');
            if (res.effective_element <= 0 && Number(res.total_element || 0) > 0) warnings.push('Elemento existe, mas está rendendo pouco contra o HZV atual.');
            if ((res.informational_skills || []).length) warnings.push(`${res.informational_skills.length} habilidade(s) desta build ainda aparecem apenas como informação; confira a seção de cobertura do motor.`);
            const items = warnings.length
                ? warnings.map(warning => createUiElement('div', 'mini-item', warning))
                : [createUiElement('div', 'mini-item muted', 'Nenhum aviso crítico para a build atual.')];
            box.replaceChildren(...items);
        }

        function clearCurrentEquipment() {
            if (typeof saveWorkspaceDraft === 'function') saveWorkspaceDraft();
            if (typeof EDITING_BUILD_ID !== 'undefined') EDITING_BUILD_ID = null;
            ['sel-weapon','sel-helm','sel-chest','sel-arms','sel-waist','sel-legs','sel-talisman'].forEach(id => {
                const el = document.getElementById(id);
                if (el && el.options.length) el.selectedIndex = 0;
            });
            CUSTOM_GOG = null;
            BUILDER_GOG_RECOMMENDATION = null;
            CUSTOM_TALISMAN = null;
            TRANSCENDED_ARMOR.clear();
            document.getElementById('build-name-input').value = '';
            const gogPanel = document.getElementById('builder-gog-recommendation');
            if (gogPanel) { gogPanel.style.display = 'none'; gogPanel.innerHTML = ''; }
            onEquipChange();
            setSaveStatus('Montador limpo.', true);
        }

        function clearBuilderDecorations() {
            if (typeof saveWorkspaceDraft === 'function') saveWorkspaceDraft();
            document.querySelectorAll('.deco-select').forEach(select => { select.value = ''; });
            if (typeof refreshSlotPickers === 'function') refreshSlotPickers();
            recalculate(0);
            setSaveStatus(SITE_LOCALE === 'en' ? 'All decorations removed.' : 'Todos os adornos foram removidos.', true);
        }

        function selectedEquipmentSummary() {
            return [
                [uiText('Arma'), equipmentName(document.getElementById('sel-weapon').value), weaponIcon(CUSTOM_GOG?.weapon_type || getSelected('sel-weapon', GAME_DATA.weapons)?.weapon_type)],
                [SITE_LOCALE === 'en' ? 'Head' : 'Elmo', equipmentName(document.getElementById('sel-helm').value), armorIcon('helm')],
                [SITE_LOCALE === 'en' ? 'Chest' : 'Peitoral', equipmentName(document.getElementById('sel-chest').value), armorIcon('chest')],
                [SITE_LOCALE === 'en' ? 'Arms' : 'Braços', equipmentName(document.getElementById('sel-arms').value), armorIcon('arms')],
                [SITE_LOCALE === 'en' ? 'Waist' : 'Cintura', equipmentName(document.getElementById('sel-waist').value), armorIcon('waist')],
                [SITE_LOCALE === 'en' ? 'Legs' : 'Pernas', equipmentName(document.getElementById('sel-legs').value), armorIcon('legs')],
                [SITE_LOCALE === 'en' ? 'Talisman' : 'Talismã', equipmentName(document.getElementById('sel-talisman').value), '✦']
            ];
        }

        function renderNerdStats(res) {
            const box = document.getElementById('nerd-stats-container');
            if (!box || !res) return;
            const hitTotal = res.hits_breakdown.reduce((sum, h) => sum + h.expected_damage, 0) || 1;
            const labels = SITE_LOCALE === 'en'
                ? { rotation:'Rotation', time:'Time', raw:'Effective raw', element:'Effective element', displayed:'displayed in-game', affinity:'Total affinity', capped:'Capped affinity', crit:'Critical', immediate:'immediate', sustained:'sustained', dpm:'sustained damage/min', sharpness:'Sharpness', defense:'Defense', resist:'Resistances', survival:'Survivability', status:'Status', largest:'Largest hit in rotation', modeled:'Modeled skills', informational:'Informational', weapon:'Weapon', distribution:'Distribution', hits:'hits', average:'average', perHit:'per hit', none:'None', target:'Target', physical:'physical', cycle:'cycle' }
                : { rotation:'Rotação', time:'Tempo', raw:'Raw efetivo', element:'Elemento efetivo', displayed:'exibido no jogo', affinity:'Afinidade total', capped:'Afinidade limitada', crit:'Crítico', immediate:'imediato', sustained:'sustentado', dpm:'dano/min sustentado', sharpness:'Afiamento', defense:'Defesa', resist:'Resistências', survival:'Sobrevivência', status:'Status', largest:'Maior golpe da rotação', modeled:'Habilidades calculadas', informational:'Informativas', weapon:'Arma', distribution:'Distribuição', hits:'acertos', average:'média', perHit:'por acerto', none:'Nenhuma', target:'Alvo', physical:'físico', cycle:'ciclo' };
            box.innerHTML = [
                `<div class="mini-item"><strong>${SITE_LOCALE === 'en' ? 'Engine' : 'Motor'} ${escapeHtml(res.engine_version || 'legacy')}</strong> · ${SITE_LOCALE === 'en' ? 'Estimated rotation; some mechanics remain approximate.' : 'Rotação estimada; algumas mecânicas ainda são aproximadas.'}</div>`,
                `<div class="mini-item"><strong>${labels.rotation}:</strong> ${escapeHtml(res.rotation_name || '-')} | <strong>${labels.time}:</strong> ${res.cycle_time_seconds || 0}s</div>`,
                `<div class="mini-item"><strong>${labels.raw}:</strong> ${res.effective_raw} | <strong>${labels.element}:</strong> ${res.effective_element_display ?? ((res.effective_element || 0) * 10)} ${labels.displayed}</div>`,
                `<div class="mini-item"><strong>${labels.target}:</strong> ${escapeHtml(translatePart(res.target_part_name || ''))} · HZ ${labels.physical} ${res.physical_hitzone ?? 0} · HZ elemental ${res.elemental_hitzone ?? 0} · ${labels.cycle}: ${labels.physical} ${res.physical_damage_per_cycle ?? 0} + elemental ${res.elemental_damage_per_cycle ?? 0}</div>`,
                `<div class="mini-item"><strong>${labels.affinity}:</strong> ${res.total_affinity}% | <strong>${labels.capped}:</strong> ${res.capped_affinity}% | <strong>${labels.crit}:</strong> ${res.crit_multiplier}x</div>`,
                `<div class="mini-item"><strong>DPS:</strong> ${labels.immediate} ${res.practical_dps} | ${labels.sustained} ${res.sustained_dps ?? res.practical_dps} | ${labels.dpm} ${res.sustained_damage_per_min ?? res.damage_per_min}</div>`,
                `<div class="mini-item"><strong>${labels.sharpness}:</strong> ${SITE_LOCALE === 'en' ? 'current' : 'atual'} raw ${res.sharpness_raw_mult}x / ${SITE_LOCALE === 'en' ? 'element' : 'elemento'} ${res.sharpness_ele_mult}x · ${SITE_LOCALE === 'en' ? 'long average' : 'média longa'} raw ${res.average_sharpness_raw_mult ?? res.sharpness_raw_mult}x / ${SITE_LOCALE === 'en' ? 'element' : 'elemento'} ${res.average_sharpness_ele_mult ?? res.sharpness_ele_mult}x · ${res.sharpness_consumed_per_cycle ?? 0} ${SITE_LOCALE === 'en' ? 'consumed per rotation' : 'de consumo por rotação'}</div>`,
                `<div class="mini-item"><strong>${labels.defense}:</strong> ${res.total_defense ?? 0} ${SITE_LOCALE === 'en' ? 'base' : 'base'} / ${res.max_defense ?? 0} ${SITE_LOCALE === 'en' ? 'maximum' : 'máxima'} · <strong>${labels.resist}:</strong> ${SITE_LOCALE === 'en' ? 'Fire' : 'Fogo'} ${res.total_resistances?.fire ?? 0}, ${SITE_LOCALE === 'en' ? 'Water' : 'Água'} ${res.total_resistances?.water ?? 0}, ${SITE_LOCALE === 'en' ? 'Thunder' : 'Trovão'} ${res.total_resistances?.thunder ?? 0}, ${SITE_LOCALE === 'en' ? 'Ice' : 'Gelo'} ${res.total_resistances?.ice ?? 0}, ${SITE_LOCALE === 'en' ? 'Dragon' : 'Dragão'} ${res.total_resistances?.dragon ?? 0}</div>`,
                `<div class="mini-item"><strong>${labels.survival}:</strong> ${res.survivability_score ?? 0} · <strong>${labels.status}:</strong> ${res.status_buildup_per_cycle ?? 0} ${SITE_LOCALE === 'en' ? 'buildup/rotation' : 'de acúmulo/rotação'}${res.estimated_status_damage_per_cycle ? ` · ${res.estimated_status_damage_per_cycle} ${SITE_LOCALE === 'en' ? 'estimated damage' : 'dano estimado'}` : ''}</div>`,
                `<div class="mini-item"><strong>${labels.largest}:</strong> ${escapeHtml([...res.hits_breakdown].sort((a,b) => b.expected_damage - a.expected_damage)[0]?.hit_name || '-')} (${Math.max(...res.hits_breakdown.map(h => h.expected_damage), 0).toFixed(1)})</div>`,
                `<div class="mini-item"><strong>${labels.modeled} (${(res.modeled_skills || []).length}):</strong> ${escapeHtml((res.modeled_skills || []).map(skillDisplayName).join(', ') || labels.none)}</div>`,
                `<div class="mini-item"><strong>${labels.informational} (${(res.informational_skills || []).length}):</strong> ${escapeHtml((res.informational_skills || []).map(skillDisplayName).join(', ') || labels.none)}</div>`,
                ...((res.weapon_mechanics || []).map(note => `<div class="mini-item"><strong>${labels.weapon}:</strong> ${escapeHtml(note)}</div>`)),
                ...((res.audit_notes || []).map(note => `<div class="mini-item">${escapeHtml(note)}</div>`)),
                `<div class="mini-item"><strong>${labels.distribution}:</strong> ${res.hits_breakdown.reduce((sum, h) => sum + (h.hit_count || 1), 0)} ${labels.hits}, ${labels.average} ${(hitTotal / Math.max(res.hits_breakdown.reduce((sum, h) => sum + (h.hit_count || 1), 0), 1)).toFixed(1)} ${labels.perHit}.</div>`
            ].join('');
        }

        async function generateBuildCard() {
            if (!CURRENT_RESULT) await recalculate();
            if (!CURRENT_RESULT) return;
            const panel = document.getElementById('build-card-panel');
            const box = document.getElementById('build-card-content');
            const monster = currentMonsterForChart();
            const topSkills = summarizeSkills(CURRENT_RESULT.active_skills);
            const heading = createUiElement('div', 'mini-item');
            heading.append(
                createUiElement('strong', '', document.getElementById('build-name-input').value || 'Build Atual'),
                document.createElement('br'),
                createUiElement('span', 'metric-note', monster?.name || 'Monstro não selecionado')
            );

            const equipment = createUiElement('div', 'equipment-summary');
            selectedEquipmentSummary().forEach(([label, value, icon]) => {
                const item = createUiElement('div', 'mini-item');
                const copy = document.createElement('span');
                copy.append(
                    createUiElement('strong', '', `${label}:`),
                    document.createElement('br'),
                    createUiElement('span', 'metric-note', value)
                );
                item.append(createUiElement('span', 'skill-icon', icon), copy);
                equipment.appendChild(item);
            });

            const stats = createUiElement('div', 'mini-item');
            stats.append(
                createUiElement('strong', '', 'DPS:'),
                document.createTextNode(` ${CURRENT_RESULT.practical_dps} | `),
                createUiElement('strong', '', 'Ciclo:'),
                document.createTextNode(` ${CURRENT_RESULT.damage_per_cycle} | `),
                createUiElement('strong', '', 'Nota:'),
                document.createTextNode(` ${CURRENT_RESULT.combined_score}`)
            );

            const skills = createUiElement('div', 'mini-item');
            skills.append(createUiElement('strong', '', 'Habilidades principais:'), document.createTextNode(` ${topSkills}`));
            box.replaceChildren(heading, equipment, stats, skills);
            panel.style.display = 'block';
        }


        function applyGogWeapon() {
            CUSTOM_GOG = {
                ...(CUSTOM_GOG?.weapon_type === document.getElementById('gog-type').value ? CUSTOM_GOG : {}),
                name: document.getElementById('gog-name').value,
                weapon_type: document.getElementById('gog-type').value,
                raw: parseFloat(document.getElementById('gog-raw').value),
                affinity: parseFloat(document.getElementById('gog-aff').value),
                element_nature: document.getElementById('gog-nature').value,
                element_type: document.getElementById('gog-ele-type').value,
                element_val: parseFloat(document.getElementById('gog-ele-val').value) / 10,
                element_display: parseFloat(document.getElementById('gog-ele-val').value),
                gog_focus: document.getElementById('gog-focus').value,
                reinforcements: Array.from(document.querySelectorAll('.gog-reinforcement')).map(field => field.value).filter(Boolean),
                slots: [
                    parseInt(document.getElementById('gog-s1').value) || 0,
                    parseInt(document.getElementById('gog-s2').value) || 0,
                    parseInt(document.getElementById('gog-s3').value) || 0
                ],
                best_sharpness: document.getElementById('gog-sharp').value,
                sharpness_units: parseInt(document.getElementById('gog-sharp-units').value) || 40,
                prev_sharpness: document.getElementById('gog-prev-sharp').value,
                skill_1: document.getElementById('gog-sk1-name').value || null,
                skill_1_lvl: parseInt(document.getElementById('gog-sk1-lvl').value) || 0,
                skill_2: document.getElementById('gog-sk2-name').value || null,
                skill_2_lvl: parseInt(document.getElementById('gog-sk2-lvl').value) || 0,
                skill_3: document.getElementById('gog-sk3-name').value || null,
                skill_3_lvl: parseInt(document.getElementById('gog-sk3-lvl').value) || 0
            };
            document.getElementById('sel-weapon').value = 'custom_gog_weapon';
            onEquipChange();
            if (typeof closeWorkspaceDialog === 'function') closeWorkspaceDialog();
            showScreen('builder');
        }

        function customTalismanPayload() {
            return {
                name: document.getElementById('tali-name').value,
                skill_1: document.getElementById('tali-s1-name').value || null,
                skill_1_lvl: parseInt(document.getElementById('tali-s1-lvl').value) || 0,
                skill_2: document.getElementById('tali-s2-name').value || null,
                skill_2_lvl: parseInt(document.getElementById('tali-s2-lvl').value) || 0,
                skill_3: document.getElementById('tali-s3-name').value || null,
                skill_3_lvl: parseInt(document.getElementById('tali-s3-lvl').value) || 0,
                slots: [
                    parseInt(document.getElementById('tali-slot1').value) || 0,
                    parseInt(document.getElementById('tali-slot2').value) || 0,
                    parseInt(document.getElementById('tali-slot3').value) || 0
                ],
                slot_kinds: [
                    document.getElementById('tali-slot-kind1').value,
                    document.getElementById('tali-slot-kind2').value,
                    document.getElementById('tali-slot-kind3').value,
                ],
            };
        }

        function applyCustomTalisman() {
            CUSTOM_TALISMAN = customTalismanPayload();
            document.getElementById('sel-talisman').value = 'custom_talisman';
            onEquipChange();
            if (typeof closeWorkspaceDialog === 'function') closeWorkspaceDialog();
            showScreen('builder');
        }

        function currentBuildPayload(id = `build_${Date.now()}`) {
            return {
                id,
                name: (document.getElementById('build-name-input').value || '').trim() || `Build #${SAVED_BUILDS.length + 1}`,
                equipment: {
                    weapon_id: document.getElementById('sel-weapon').value,
                    helm_id: document.getElementById('sel-helm').value,
                    chest_id: document.getElementById('sel-chest').value,
                    arms_id: document.getElementById('sel-arms').value,
                    waist_id: document.getElementById('sel-waist').value,
                    legs_id: document.getElementById('sel-legs').value,
                    talisman_id: document.getElementById('sel-talisman').value,
                    decorations: Array.from(document.querySelectorAll('.deco-select')).map(s => s.value).filter(v => v !== ''),
                    transcended_armor: Array.from(TRANSCENDED_ARMOR),
                    custom_weapon: CUSTOM_GOG,
                    custom_talisman: CUSTOM_TALISMAN
                },
                scenario: currentScenarioPayload(),
                result: CURRENT_RESULT
            };
        }

        function currentScenarioPayload() {
            const weapon = document.getElementById('sel-weapon')?.value === 'custom_gog_weapon' ? CUSTOM_GOG : getSelected('sel-weapon', GAME_DATA?.weapons || []);
            const validRotation = (GAME_DATA?.rotations || []).some(rotation => rotation.id === CURRENT_ROTATION_ID && rotation.weapon_type === weapon?.weapon_type);
            return {
                ...SCENARIO_BASE,
                monster_id: document.getElementById('use-custom-monster').checked ? 'custom_monster' : document.getElementById('scenario-monster').value,
                target_part: document.getElementById('use-custom-monster').checked ? 'Media_Ponderada' : document.getElementById('scenario-part').value,
                wound_active: document.getElementById('scenario-wound').checked,
                wound_hitzone_bonus: document.getElementById('scenario-wound').checked ? Number(document.getElementById('scenario-wound-bonus')?.value || 0) : 0,
                agitator_uptime: parseFloat(document.getElementById('uptime-agi').value) / 100.0,
                burst_uptime: parseFloat(document.getElementById('uptime-burst').value) / 100.0,
                weakness_exploit_uptime: parseFloat(document.getElementById('uptime-wex').value) / 100.0,
                maximum_might_uptime: pct('uptime-maxmight'),
                peak_performance_uptime: pct('uptime-peak'),
                offensive_guard_uptime: pct('uptime-og'),
                counterstrike_uptime: pct('uptime-counter'),
                coalescence_uptime: pct('uptime-coal'),
                latent_power_uptime: pct('uptime-latent'),
                frenzy_antivirus_uptime: pct('uptime-frenzy'),
                might_seed_uptime: pct('uptime-seed'),
                demon_powder_uptime: pct('uptime-powder'),
                mantle_uptime: pct('uptime-mantle'),
                resentment_uptime: pct('uptime-resentment'),
                elemental_absorption_uptime: pct('uptime-eleabsorb'),
                adrenaline_rush_uptime: pct('uptime-adrenaline'),
                foray_uptime: pct('uptime-foray'),
                ambush_uptime: pct('uptime-ambush'),
                heroics_uptime: pct('uptime-heroics'),
                rotation_id: validRotation ? CURRENT_ROTATION_ID : null,
                custom_monster: document.getElementById('use-custom-monster').checked ? customMonsterPayload() : null
            };
        }

        function setSaveStatus(message, ok = true) {
            const el = document.getElementById('save-status');
            if (!el) return;
            el.textContent = message;
            el.className = `status-line ${ok ? 'status-ok' : 'status-error'}`;
        }

        function localBuilds() {
            try { return JSON.parse(localStorage.getItem('mhwilds_saved_builds') || '[]'); }
            catch { return []; }
        }

        function saveBuildLocal(build) {
            const builds = localBuilds().filter(b => b.id !== build.id);
            builds.push(build);
            localStorage.setItem('mhwilds_saved_builds', JSON.stringify(builds.slice(-30)));
        }

        async function ensureCurrentResult() {
            clearTimeout(RECALC_TIMER);
            const result = await runRecalculate();
            if (!result) {
                setSaveStatus(SITE_LOCALE === 'en' ? 'The build has not been calculated yet. Check the weapon, talisman, and scenario.' : 'A build ainda não foi calculada. Verifique arma, talismã e cenário.', false);
                return false;
            }
            return true;
        }

        async function saveCurrentBuild() {
            if (!(await ensureCurrentResult())) return;
            const nameInput = document.getElementById('build-name-input');
            const buildObj = currentBuildPayload((typeof EDITING_BUILD_ID !== 'undefined' && EDITING_BUILD_ID) || `build_${Date.now()}`);
            const name = buildObj.name;

            let savedOnServer = false;
            try {
                const res = await fetch('/api/builds/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(buildObj)
                });
                savedOnServer = res.ok;
                if (!res.ok) {
                    const err = await res.json();
                    setSaveStatus(err.detail || (SITE_LOCALE === 'en' ? 'Server save failed. Saving locally.' : 'Falha ao salvar no servidor. Salvando localmente.'), false);
                }
            } catch (err) {
                setSaveStatus(SITE_LOCALE === 'en' ? 'Server unavailable. Saving a local browser copy.' : 'Servidor indisponível. Salvando cópia local no navegador.', false);
            }
            let savedLocally = false;
            try { saveBuildLocal(buildObj); savedLocally = true; }
            catch {
                setSaveStatus(SITE_LOCALE === 'en' ? 'Browser storage unavailable. Export a backup.' : 'Armazenamento do navegador indisponível. Exporte um backup.', false);
                if (!savedOnServer) return;
            }
            if (typeof EDITING_BUILD_ID !== 'undefined') EDITING_BUILD_ID = buildObj.id;
            nameInput.value = name;
            await loadSavedBuilds();
            setSaveStatus(SITE_LOCALE === 'en'
                ? `Build "${name}" saved ${savedOnServer ? (savedLocally ? 'locally and on the server' : 'on the server') : 'locally'}.`
                : `Build "${name}" salva ${savedOnServer ? (savedLocally ? 'no servidor e localmente' : 'no servidor') : 'localmente'}.`, true);
            if (typeof saveWorkspaceDraft === 'function') { saveWorkspaceDraft(); uxMessage(SITE_LOCALE === 'en' ? 'Build saved.' : 'Build salva.'); }
        }

        function localDamage() {
            try { return JSON.parse(localStorage.getItem('mhwilds_saved_damage') || '[]'); }
            catch { return []; }
        }

        function localTalismans() {
            try {
                const items = JSON.parse(localStorage.getItem(TALISMAN_STORAGE_KEY) || '[]');
                return Array.isArray(items) ? items : [];
            } catch { return []; }
        }

        function saveTalismansLocal(items) {
            localStorage.setItem(TALISMAN_STORAGE_KEY, JSON.stringify(items.slice(-100)));
        }

        function mergeRecordsById(base, incoming, limit) {
            const merged = new Map();
            [...base, ...incoming].forEach(item => {
                if (!item || typeof item !== 'object' || typeof item.id !== 'string' || !item.id.trim()) return;
                merged.set(item.id, item);
            });
            return Array.from(merged.values()).slice(-limit);
        }

        function saveDamageLocal(damage) {
            const rows = localDamage().filter(d => d.id !== damage.id);
            rows.push(damage);
            localStorage.setItem('mhwilds_saved_damage', JSON.stringify(rows.slice(-60)));
        }

        async function saveCurrentDamage() {
            if (!(await ensureCurrentResult())) return;
            const build = currentBuildPayload(`damage_build_${Date.now()}`);
            const monster = currentMonsterForChart();
            const damage = {
                id: `damage_${Date.now()}`,
                name: `${build.name} vs ${monster?.name || (SITE_LOCALE === 'en' ? 'Monster' : 'Monstro')}`,
                build_name: build.name,
                equipment: build.equipment,
                scenario: build.scenario,
                result: build.result
            };
            try {
                await fetch('/api/damage/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(damage)
                });
            } catch {}
            saveDamageLocal(damage);
            await loadSavedDamage();
            setSaveStatus(SITE_LOCALE === 'en' ? `Result "${damage.name}" saved.` : `Resultado "${damage.name}" salvo.`, true);
            if (typeof uxMessage === 'function') uxMessage(SITE_LOCALE === 'en' ? 'Damage result saved.' : 'Resultado de dano salvo.');
        }

        async function loadSavedBuilds() {
            let serverBuilds = [];
            try {
                const res = await fetch('/api/builds');
                serverBuilds = res.ok ? await res.json() : [];
            } catch {
                serverBuilds = [];
            }
            const merged = new Map();
            [...serverBuilds, ...localBuilds()].forEach(b => merged.set(b.id, b));
            SAVED_BUILDS = Array.from(merged.values()).slice(-30);
            SHARED_COMPARISON = null;
            renderComparatorTable();
            renderDashboard();
            updatePlannerUI();
            if (document.getElementById('screen-comparator').classList.contains('active')) refreshSharedComparison();
        }


        async function loadSavedDamage() {
            let serverDamage = [];
            try {
                const res = await fetch('/api/damage');
                serverDamage = res.ok ? await res.json() : [];
            } catch {
                serverDamage = [];
            }
            const merged = new Map();
            [...serverDamage, ...localDamage()].forEach(d => merged.set(d.id, d));
            SAVED_DAMAGE = Array.from(merged.values()).slice(-60);
            renderSavedDamage();
            renderSettingsCounts();
        }

        function renderSavedDamage() {
            const box = document.getElementById('saved-damage-container');
            if (!box) return;
            if (!SAVED_DAMAGE.length) {
                replaceWithMessage(box, SITE_LOCALE === 'en' ? 'No saved results yet.' : 'Nenhum resultado salvo ainda.');
                return;
            }
            const records = SAVED_DAMAGE.slice().reverse().map(d => {
                const result = d.result || {};
                const item = createUiElement('div', 'mini-item');
                const actions = document.createElement('div');
                actions.style.marginTop = '8px';
                const button = createActionButton(SITE_LOCALE === 'en' ? 'Delete Result' : 'Excluir Resultado', 'btn btn-danger', () => deleteSavedDamage(d.id));
                button.style.padding = '5px 9px';
                actions.appendChild(button);
                item.append(
                    createUiElement('strong', '', d.name || d.build_name || d.id || (SITE_LOCALE === 'en' ? 'Result' : 'Resultado')),
                    document.createElement('br'),
                    createUiElement('span', 'metric-note', `DPS ${result.practical_dps ?? 0} | ${SITE_LOCALE === 'en' ? 'Cycle' : 'Ciclo'} ${result.damage_per_cycle ?? 0} | ${SITE_LOCALE === 'en' ? 'Score' : 'Nota'} ${result.combined_score ?? 0}`),
                    actions
                );
                return item;
            });
            box.replaceChildren(...records);
        }

        async function deleteSavedDamage(id) {
            try { await fetch(`/api/damage/${encodeURIComponent(id)}`, { method: 'DELETE' }); } catch {}
            const rows = localDamage().filter(d => d.id !== id);
            localStorage.setItem('mhwilds_saved_damage', JSON.stringify(rows));
            await loadSavedDamage();
        }

        function renderSettingsCounts() {
            const b = document.getElementById('settings-build-count');
            const d = document.getElementById('settings-damage-count');
            const t = document.getElementById('settings-talisman-count');
            const w = document.getElementById('settings-wishlist-count');
            if (b) b.innerText = SAVED_BUILDS.length;
            if (d) d.innerText = SAVED_DAMAGE.length;
            if (t) t.innerText = TALISMAN_INVENTORY.length;
            if (w) w.innerText = WISHLIST.length;
        }

        function exportLocalData() {
            const data = {
                app: BACKUP_APP_ID,
                schema_version: BACKUP_SCHEMA_VERSION,
                exported_at: new Date().toISOString(),
                builds: SAVED_BUILDS,
                damage: SAVED_DAMAGE,
                talismans: TALISMAN_INVENTORY,
                wishlist: WISHLIST,
                material_inventory: loadMaterialInventory(),
                workspace: typeof snapshotWorkspace === 'function' ? snapshotWorkspace() : null,
                favorites: typeof favoriteIds === 'function' ? favoriteIds() : [],
                preferences: {
                    locale: SITE_LOCALE,
                    visual_theme: VISUAL_THEME
                }
            };
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `mhwilds-builder-backup-${new Date().toISOString().slice(0, 10)}.json`;
            a.click();
            setTimeout(() => URL.revokeObjectURL(a.href), 0);
            const status = document.getElementById('backup-status');
            if (status) {
                status.textContent = SITE_LOCALE === 'en' ? 'Backup downloaded successfully.' : 'Backup baixado com sucesso.';
                status.className = 'status-line status-ok';
            }
        }

        function backupArray(data, key) {
            const value = data[key];
            if (value === undefined) return [];
            if (!Array.isArray(value)) throw new Error(`Campo inválido no backup: ${key}.`);
            return value;
        }

        async function importLocalData(event) {
            const input = event.currentTarget;
            const file = input.files?.[0];
            const status = document.getElementById('backup-status');
            if (!file) return;
            try {
                if (file.size > BACKUP_MAX_BYTES) throw new Error('O backup excede o limite de 5 MB.');
                const data = JSON.parse(await file.text());
                if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('O arquivo não contém um backup válido.');
                if (data.app && data.app !== BACKUP_APP_ID) throw new Error('Este backup pertence a outro aplicativo.');
                const schemaVersion = Number(data.schema_version || 1);
                if (!Number.isInteger(schemaVersion) || schemaVersion < 1 || schemaVersion > BACKUP_SCHEMA_VERSION) {
                    throw new Error('A versão deste backup não é compatível com o aplicativo atual.');
                }

                const builds = mergeRecordsById(localBuilds(), backupArray(data, 'builds'), 30);
                const damage = mergeRecordsById(localDamage(), backupArray(data, 'damage'), 60);
                const talismans = mergeRecordsById(localTalismans(), backupArray(data, 'talismans'), 100);
                const wishlist = mergeRecordsById(WISHLIST, backupArray(data, 'wishlist'), 250);
                const materialInventory = MaterialPlan.normalizeInventory({...loadMaterialInventory(), ...MaterialPlan.normalizeInventory(data.material_inventory)});
                const workspace = data.workspace && typeof WorkspaceState !== 'undefined' ? WorkspaceState.decodeDraft(JSON.stringify(data.workspace)) : null;
                if (data.workspace && !workspace) throw new Error(SITE_LOCALE === 'en' ? 'Invalid draft in backup.' : 'Rascunho inválido no backup.');
                localStorage.setItem('mhwilds_saved_builds', JSON.stringify(builds));
                localStorage.setItem('mhwilds_saved_damage', JSON.stringify(damage));
                saveTalismansLocal(talismans);
                localStorage.setItem(WISHLIST_STORAGE_KEY, JSON.stringify(wishlist));
                localStorage.setItem('mhwilds_material_inventory', JSON.stringify(materialInventory));
                if(Array.isArray(data.favorites))localStorage.setItem('mhwilds_favorites',JSON.stringify([...new Set([...(typeof favoriteIds==='function'?favoriteIds():[]),...data.favorites.filter(id=>typeof id==='string')])].slice(-100)));

                const preferences = data.preferences || {};
                const locale = preferences.locale || data.locale;
                const theme = preferences.visual_theme;
                if (['pt', 'en'].includes(locale)) localStorage.setItem('mhwilds_locale', locale);
                if (['windward', 'scarlet', 'oilwell', 'iceshard', 'wyveria'].includes(theme)) switchVisualTheme(theme);

                WISHLIST = wishlist;
                await Promise.all([loadSavedBuilds(), loadSavedDamage(), loadTalismanInventory()]);
                renderWishlist();
                renderSettingsCounts();
                if (locale && locale !== SITE_LOCALE) await switchSiteLocale(locale);
                if (workspace && confirm(SITE_LOCALE === 'en' ? 'Also restore the draft from this backup? Your saved builds will remain.' : 'Restaurar também o rascunho deste backup? Suas builds salvas serão mantidas.')) {
                    await restoreWorkspaceSnapshot(workspace); saveWorkspaceDraft();
                }
                if (status) {
                    status.textContent = SITE_LOCALE === 'en'
                        ? `Backup imported: ${builds.length} builds, ${damage.length} results, and ${talismans.length} talismans.`
                        : `Backup importado: ${builds.length} builds, ${damage.length} resultados e ${talismans.length} talismãs.`;
                    status.className = 'status-line status-ok';
                }
            } catch (error) {
                if (status) {
                    status.textContent = error.message || 'Não foi possível importar o backup.';
                    status.className = 'status-line status-error';
                }
            } finally {
                input.value = '';
            }
        }

        async function loadDataVersion() {
            const element = document.getElementById('settings-data-version');
            if (!element) return;
            try {
                const response = await fetch('/api/data/version');
                if (!response.ok) throw new Error('Diagnóstico indisponível.');
                const data = await response.json();
                const counts = data.counts || {};
                element.textContent = SITE_LOCALE === 'en'
                    ? `Data ${data.status === 'ok' ? 'verified' : 'needs attention'} · version ${data.game_data_version || 'unknown'} · ${counts.weapons || 0} weapons · ${counts.armors || 0} armor pieces · ${counts.monsters || 0} monsters.`
                    : `Base ${data.status === 'ok' ? 'verificada' : 'requer atenção'} · versão ${data.game_data_version || 'desconhecida'} · ${counts.weapons || 0} armas · ${counts.armors || 0} armaduras · ${counts.monsters || 0} monstros.`;
                element.className = `status-line ${data.status === 'ok' ? 'status-ok' : 'status-error'}`;
            } catch (error) {
                element.textContent = error.message || 'Não foi possível verificar a base de dados.';
                element.className = 'status-line status-error';
            }
        }

        async function clearLocalBuildData() {
            if (!confirm(SITE_LOCALE === 'en' ? 'Remove this browser\'s build copies? Server copies and the draft will remain.' : 'Remover as cópias de builds deste navegador? Cópias do servidor e o rascunho serão mantidos.')) return;
            localStorage.removeItem('mhwilds_saved_builds');
            await loadSavedBuilds();
            document.getElementById('settings-status').innerText = 'Builds locais limpas.';
        }

        async function clearLocalDamageData() {
            if (!confirm(SITE_LOCALE === 'en' ? 'Remove this browser\'s saved result copies?' : 'Remover as cópias de resultados salvos deste navegador?')) return;
            localStorage.removeItem('mhwilds_saved_damage');
            await loadSavedDamage();
            document.getElementById('settings-status').innerText = 'Resultados locais limpos.';
        }

        function metricValue(build, metric) {
            return Number(build.result[metric] || 0);
        }

        function renderRankingCards(sorted) {
            const box = document.getElementById('comparator-ranking-cards');
            if (!box) return;
            if (!sorted.length) { box.replaceChildren(); return; }
            const bestDps = [...sorted].sort((a,b) => b.result.practical_dps - a.result.practical_dps)[0];
            const bestCycle = [...sorted].sort((a,b) => b.result.damage_per_cycle - a.result.damage_per_cycle)[0];
            const bestMinute = [...sorted].sort((a,b) => b.result.damage_per_min - a.result.damage_per_min)[0];
            const bestScore = [...sorted].sort((a,b) => b.result.survivability_score - a.result.survivability_score)[0];
            const cards = [
                [SITE_LOCALE === 'en' ? 'Survivability index' : 'Índice de sobrevivência', bestScore.name, bestScore.result.survivability_score],
                [uiText('DPS prático'), bestDps.name, bestDps.result.practical_dps],
                [uiText('Dano por ciclo'), bestCycle.name, bestCycle.result.damage_per_cycle],
                [uiText('Dano/min'), bestMinute.name, bestMinute.result.damage_per_min]
            ].map(([title, name, value]) => {
                const card = createUiElement('div', 'stat-badge');
                const metric = createUiElement('div', 'stat-val', value);
                metric.style.fontSize = '1.1rem';
                card.append(createUiElement('div', 'stat-lbl', title), metric, createUiElement('div', 'metric-note', name));
                return card;
            });
            box.replaceChildren(...cards);
        }

        function renderComparatorTable() {
            const builds = comparedBuilds();
            if (typeof updateComparisonExperience === 'function') updateComparisonExperience(builds);
            const tbody = document.getElementById('comparator-table-body');
            tbody.replaceChildren();
            populateComboBuildSelect();
            if (builds.length === 0) {
                const row = document.createElement('tr');
                const cell = createUiElement('td', '', SAVED_BUILDS.length ? plannerText('Comparação aguardando recálculo.', 'Comparison awaiting recalculation.') : plannerText('Nenhuma build salva.', 'No saved builds.'));
                cell.colSpan = 11;
                cell.style.textAlign = 'center';
                cell.style.color = 'var(--text-muted)';
                row.appendChild(cell);
                tbody.appendChild(row);
                renderRankingCards([]);
                populateComparisonBuildSelect([]);
                renderComparisonChart([]);
                return;
            }

            const sortMetric = document.getElementById('comparator-sort')?.value || 'combined_score';
            const sorted = [...builds].sort((a, b) => metricValue(b, sortMetric) - metricValue(a, sortMetric));
            renderRankingCards(sorted);
            populateComparisonBuildSelect(sorted);
            const metrics = ['effective_raw', 'practical_dps', 'damage_per_min', 'damage_per_cycle', 'combined_score'];
            const best = Object.fromEntries(metrics.map(m => [m, Math.max(...builds.map(b => metricValue(b, m)))]));
            const worst = Object.fromEntries(metrics.map(m => [m, Math.min(...builds.map(b => metricValue(b, m)))]));

            renderComparisonChart(sorted);
            sorted.forEach((b) => {
                const cls = (metric, value) => value === best[metric] ? 'best-cell' : (value === worst[metric] && builds.length > 1 ? 'worst-cell' : '');
                const reference = typeof COMPARISON_BASELINE !== 'undefined' ? builds.find(item => item.id === COMPARISON_BASELINE) : null;
                const baseDps = reference?.result.practical_dps ?? best.practical_dps;
                const diffPct = baseDps > 0 ? ((b.result.practical_dps / baseDps) - 1) * 100 : null;
                const row = document.createElement('tr');
                const nameCell = document.createElement('td');
                nameCell.append(
                    createUiElement('strong', '', b.name),
                    document.createElement('br'),
                    createUiElement('span', 'metric-note', skillContribution(b))
                );
                row.appendChild(nameCell);
                row.appendChild(createUiElement('td', '', equipmentName(b.equipment.weapon_id, b.equipment)));
                row.appendChild(createUiElement('td', cls('effective_raw', b.result.effective_raw), b.result.effective_raw));
                row.appendChild(createUiElement('td', '', `${b.result.capped_affinity}%`));
                row.appendChild(createUiElement('td', cls('practical_dps', b.result.practical_dps), b.result.practical_dps));
                row.appendChild(createUiElement('td', cls('damage_per_min', b.result.damage_per_min), b.result.damage_per_min));
                row.appendChild(createUiElement('td', cls('damage_per_cycle', b.result.damage_per_cycle), b.result.damage_per_cycle));
                row.appendChild(createUiElement('td', '', b.result.rotation_name || (SITE_LOCALE === 'en' ? 'Default combo' : 'Combo padrão')));
                const scoreCell = createUiElement('td', cls('combined_score', b.result.combined_score));
                scoreCell.appendChild(createUiElement('span', 'tag', b.result.combined_score));
                row.appendChild(scoreCell);
                row.appendChild(createUiElement('td', '', diffPct === null ? '-' : `${diffPct > 0 ? '+' : ''}${diffPct.toFixed(1)}%`));

                const actions = document.createElement('td');
                actions.append(
                    createActionButton(SITE_LOCALE === 'en' ? 'Load' : 'Carregar', 'btn btn-secondary', () => loadBuildIntoBuilder(b.id)),
                    createActionButton(SITE_LOCALE === 'en' ? 'Rename' : 'Renomear', 'btn btn-secondary', () => renameBuild(b.id)),
                    createActionButton(SITE_LOCALE === 'en' ? 'Combos' : 'Combos', 'btn btn-secondary', () => compareBuildRotations(b.id)),
                    createActionButton(SITE_LOCALE === 'en' ? 'Delete' : 'Excluir', 'btn btn-danger', () => { if (confirm(SITE_LOCALE === 'en' ? `Delete "${b.name}"?` : `Excluir "${b.name}"?`)) deleteBuild(b.id); })
                );
                row.appendChild(actions);
                tbody.appendChild(row);
            });
        }

        function populateComboBuildSelect() {
            const select = document.getElementById('combo-build-select');
            if (!select) return;
            const current = select.value;
            select.innerHTML = SAVED_BUILDS.length
                ? SAVED_BUILDS.map(build => `<option value="${escapeHtml(build.id)}">${escapeHtml(build.name)}</option>`).join('')
                : `<option value="">${SITE_LOCALE === 'en' ? 'No saved builds' : 'Nenhuma build salva'}</option>`;
            if (SAVED_BUILDS.some(build => build.id === current)) select.value = current;
        }

        function populateComparisonBuildSelect(sorted) {
            const select = document.getElementById('comparison-build-select');
            if (!select) return;
            const current = Array.from(select.selectedOptions).map(option => option.value);
            select.innerHTML = sorted.map((build, index) => `<option value="${escapeHtml(build.id)}">${index + 1}. ${escapeHtml(build.name)}</option>`).join('');
            const valid = current.filter(id => sorted.some(build => build.id === id));
            const selected = valid.length ? valid : sorted.slice(0, Math.min(6, sorted.length)).map(build => build.id);
            Array.from(select.options).forEach(option => { option.selected = selected.includes(option.value); });
        }

        function selectComparisonBuilds(mode) {
            const select = document.getElementById('comparison-build-select');
            if (!select) return;
            const options = Array.from(select.options);
            options.forEach((option, index) => { option.selected = mode === 'all' || index < 6; });
            renderComparatorTable();
        }

        function compareBuildRotations(buildId) {
            setSelectValue('combo-build-select', buildId);
            showScreen('comparator');
            compareSelectedBuildRotations();
        }

        async function compareSelectedBuildRotations() {
            const buildId = document.getElementById('combo-build-select')?.value;
            const build = SAVED_BUILDS.find(item => item.id === buildId);
            const container = document.getElementById('rotation-ranking-container');
            const button = document.getElementById('btn-compare-rotations');
            if (!build || !container) return;
            clearComparedRotations();
            const requestId = ++ROTATION_REQUEST_ID;
            const scenario = currentScenarioPayload();
            const scenarioKey = JSON.stringify(scenario);
            button.disabled = true;
            button.textContent = SITE_LOCALE === 'en' ? 'Comparing...' : 'Comparando...';
            container.innerHTML = `<div class="mini-item muted">${SITE_LOCALE === 'en' ? 'Recalculating every combo for this weapon in the same scenario...' : 'Recalculando todos os combos desta arma no mesmo cenário...'}</div>`;
            try {
                const response = await fetch('/api/rotations/compare', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ equipment: build.equipment, scenario })
                });
                if (!response.ok) {
                    const error = await response.json().catch(() => ({}));
                    throw new Error(error.detail || (SITE_LOCALE === 'en' ? 'Could not compare combos.' : 'Não foi possível comparar os combos.'));
                }
                const rows = await response.json();
                if (requestId !== ROTATION_REQUEST_ID || buildId !== document.getElementById('combo-build-select').value || scenarioKey !== JSON.stringify(currentScenarioPayload())) return;
                ROTATION_COMPARISONS = rows.sort((left, right) =>
                    Number(right.result.practical_dps || 0) - Number(left.result.practical_dps || 0)
                );
                renderRotationComparisons(build);
            } catch (error) {
                if (requestId !== ROTATION_REQUEST_ID) return;
                container.innerHTML = `<div class="mini-item" style="color:var(--danger);">${escapeHtml(error.message)}</div>`;
            } finally {
                if (requestId === ROTATION_REQUEST_ID) {
                    button.disabled = false;
                    button.textContent = SITE_LOCALE === 'en' ? 'Compare combos' : 'Comparar combos';
                }
            }
        }

        function renderRotationComparisons(build) {
            const container = document.getElementById('rotation-ranking-container');
            if (!ROTATION_COMPARISONS.length) {
                container.innerHTML = `<div class="mini-item muted">${SITE_LOCALE === 'en' ? 'No rotations are available for this weapon.' : 'Nenhuma rotação disponível para esta arma.'}</div>`;
                return;
            }
            const bestDps = Math.max(...ROTATION_COMPARISONS.map(row => Number(row.result.practical_dps || 0)), 1);
            container.innerHTML = ROTATION_COMPARISONS.map((row, index) => {
                const percent = Number(row.result.practical_dps || 0) / bestDps * 100;
                const difference = percent - 100;
                return `<button class="mini-item" style="width:100%; text-align:left; cursor:pointer; color:inherit;" onclick="showRotationComparison(${index})">
                    <div style="display:flex; justify-content:space-between; gap:12px; align-items:center;">
                        <span><strong>${index + 1}. ${escapeHtml(row.rotation.name)}</strong><br><span class="metric-note">${row.rotation.category} · ${row.rotation.cycle_time_seconds}s · ${row.result.damage_per_cycle} ${SITE_LOCALE === 'en' ? 'per rotation' : 'por rotação'}</span></span>
                        <span style="text-align:right;"><strong style="color:${index === 0 ? 'var(--success)' : 'var(--accent)'};">${row.result.practical_dps} DPS</strong><br><span class="metric-note">${row.result.damage_per_min} DPM · ${index === 0 ? (SITE_LOCALE === 'en' ? 'Best' : 'Melhor') : difference.toFixed(1) + '%'}</span></span>
                    </div>
                    <div style="height:5px; background:#172231; margin-top:8px;"><div style="height:100%; width:${Math.max(2, percent)}%; background:${index === 0 ? 'var(--success)' : 'var(--accent)'};"></div></div>
                </button>`;
            }).join('');
            const best = ROTATION_COMPARISONS[0];
            const second = ROTATION_COMPARISONS[1];
            const lead = second ? ((best.result.practical_dps / Math.max(second.result.practical_dps, 0.01)) - 1) * 100 : 0;
            document.getElementById('rotation-explanation').innerHTML = `
                <div class="mini-item">${SITE_LOCALE === 'en' ? `<strong>${escapeHtml(best.rotation.name)}</strong> is the most efficient combo for <strong>${escapeHtml(build.name)}</strong>, with ${best.result.damage_per_cycle} damage per rotation.` : `<strong>${escapeHtml(best.rotation.name)}</strong> é o combo mais eficiente para <strong>${escapeHtml(build.name)}</strong>, com ${best.result.damage_per_cycle} de dano por rotação.`}</div>
                <div class="mini-item">${SITE_LOCALE === 'en' ? 'Output' : 'Produção'}: <strong>${best.result.practical_dps} DPS</strong> ${SITE_LOCALE === 'en' ? 'and' : 'e'} <strong>${best.result.damage_per_min} DPM</strong>${second ? `, ${lead.toFixed(1)}% ${SITE_LOCALE === 'en' ? 'above the second combo' : 'acima do segundo combo'}` : ''}.</div>
                <div class="mini-item">${SITE_LOCALE === 'en' ? 'Execution times are explicit estimates; motion values are versioned in the local library.' : 'Os tempos de execução são estimativas explícitas; os valores de movimento ficam versionados na biblioteca local.'}</div>`;
            showRotationComparison(0);
        }

        function showRotationComparison(index) {
            const row = ROTATION_COMPARISONS[index];
            if (!row) return;
            renderNerdStats(row.result);
            renderHitBreakdown(row.result);
        }



        function strongestSkillDifference(bestBuild, otherBuild) {
            return skillContribution(bestBuild);
        }

        function renderComparisonChart(sorted) {
            const canvas = document.getElementById('build-comparison-chart');
            const explanation = document.getElementById('comparison-explanation');
            const legend = document.getElementById('comparison-legend');
            if (!canvas || !explanation || !legend) return;
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (!sorted.length) {
                legend.replaceChildren();
                replaceWithMessage(explanation, 'Salve builds para gerar o gráfico.');
                return;
            }
            const metric = document.getElementById('comparator-sort')?.value || 'combined_score';
            const selectedIds = Array.from(document.getElementById('comparison-build-select')?.selectedOptions || []).map(option => option.value);
            const selected = sorted.filter(build => selectedIds.includes(build.id));
            const top = (selected.length ? selected : sorted.slice(0, 6)).slice(0, 8);
            const maxVal = Math.max(...top.map(b => metricValue(b, metric)), 1);
            const chartWidth = 650;
            const gap = 14;
            const barW = Math.max(42, Math.floor((chartWidth - gap * (top.length - 1)) / top.length));
            const baseY = 330;
            const colors = ['#22c55e', '#d4a359', '#4ca7e8', '#e879f9', '#fb7185', '#2dd4bf', '#f97316', '#a3e635'];
            top.forEach((b, idx) => {
                const value = metricValue(b, metric);
                const h = Math.max(4, (value / maxVal) * 250);
                const x = 55 + idx * (barW + gap);
                ctx.fillStyle = colors[idx];
                ctx.fillRect(x, baseY - h, barW, h);
                ctx.fillStyle = '#f0f4f8';
                ctx.font = '12px Segoe UI';
                ctx.textAlign = 'center';
                ctx.fillText(String(value), x + barW / 2, baseY - h - 8);
                ctx.save();
                ctx.translate(x + barW / 2, baseY + 14);
                ctx.fillStyle = '#8ca0b8';
                ctx.fillText(`${idx + 1}. ${b.name.slice(0, 12)}`, 0, 0);
                ctx.restore();
            });
            ctx.strokeStyle = '#26354a';
            ctx.beginPath();
            ctx.moveTo(35, baseY);
            ctx.lineTo(700, baseY);
            ctx.stroke();

            const legendItems = top.map((build, index) => {
                const item = createUiElement('span', 'tag', `${index + 1}. ${build.name}: ${metricValue(build, metric)}`);
                item.style.borderColor = colors[index];
                return item;
            });
            legend.replaceChildren(...legendItems);
            const best = top[0];
            const second = top[1];
            if (!second) {
                replaceWithMessage(explanation, `${best.name} é a única build salva para comparação.`, 'mini-item');
                return;
            }
            const diff = ((metricValue(best, metric) / Math.max(metricValue(second, metric), 1)) - 1) * 100;
            const reason = strongestSkillDifference(best, second);
            const lead = createUiElement('div', 'mini-item');
            lead.append(
                createUiElement('strong', '', best.name),
                document.createTextNode(SITE_LOCALE === 'en'
                    ? ` leads by ${diff.toFixed(1)}% in ${document.getElementById('comparator-sort').selectedOptions[0].text} over the runner-up.`
                    : ` lidera por ${diff.toFixed(1)}% em ${document.getElementById('comparator-sort').selectedOptions[0].text} contra a segunda colocada.`)
            );
            const reasonBox = createUiElement('div', 'mini-item');
            reasonBox.append(
                document.createTextNode(SITE_LOCALE === 'en' ? 'Largest isolated skill contribution: ' : 'Maior contribuição isolada de habilidade: '),
                createUiElement('strong', '', reason),
                document.createTextNode(`.${selected.length > 8 ? ' O gráfico mostra as 8 melhores entre as selecionadas; a tabela continua exibindo todas.' : ''}`)
            );
            explanation.replaceChildren(lead, reasonBox);
        }


        function equipmentName(id, equipment = null) {
            if (!GAME_DATA) return id;
            if (id === 'custom_gog_weapon' && equipment?.custom_weapon) return `ARMA GOG :: ${equipment.custom_weapon.name}`;
            if (id === 'custom_talisman' && equipment?.custom_talisman) return `TALISMÃ :: ${equipment.custom_talisman.name || 'Editor'}`;
            const all = [...GAME_DATA.weapons, ...GAME_DATA.armors, ...GAME_DATA.talismans];
            return displayName(all.find(x => x.id === id)) || id;
        }

        function summarizeSkills(skills) {
            const entries = Object.entries(skills || {}).sort((a, b) => b[1] - a[1]).slice(0, 4);
            return entries.length ? entries.map(([s, l]) => `${skillIcon(s)} ${skillDisplayName(s)} ${l}`).join(' · ') : 'Sem habilidades relevantes';
        }

        function renderDashboard() {
            const savedCounter = document.getElementById('dash-saved');
            if (savedCounter) savedCounter.innerText = SAVED_BUILDS.length;

            const monsterId = document.getElementById('scenario-monster')?.value;
            const monster = GAME_DATA?.monsters?.find(item => item.id === monsterId);
            const monsterTitle = document.getElementById('home-monster');
            const monsterBrief = document.getElementById('home-brief');
            const monsterArt = document.getElementById('home-monster-art');
            if (monsterTitle) monsterTitle.textContent = monster?.name || 'Selecione um monstro';
            if (monsterBrief) monsterBrief.textContent = monster
                ? (monster.description || 'Ajuste a parte atingida e as condições da caçada para avaliar a build.')
                : 'A escolha do alvo define hitzones, fraquezas e a recomendação de elemento.';
            if (monsterArt) {
                const image = monster ? monsterIconFiles(monster.name_en || monster.name)[0] : '';
                const fallback = (monster?.name || 'MH').split(/\s+/).map(word => word[0]).join('').slice(0, 3).toUpperCase();
                monsterArt.innerHTML = image
                    ? `<img src="${escapeHtml(image)}" alt="" onerror="if(this.parentElement)this.parentElement.innerHTML='<span class=&quot;monster-art-fallback&quot;>${escapeHtml(fallback)}</span>'">`
                    : `<span class="monster-art-fallback">${escapeHtml(fallback)}</span>`;
            }

            const topbarBuild = document.getElementById('topbar-build');
            if (!CURRENT_RESULT) {
                if (topbarBuild) topbarBuild.textContent = uiText('Configure uma build para calcular');
                return;
            }

            document.getElementById('dash-dps').innerText = CURRENT_RESULT.practical_dps.toFixed(1);
            document.getElementById('dash-cycle').innerText = CURRENT_RESULT.damage_per_cycle.toFixed(1);
            document.getElementById('dash-raw').innerText = CURRENT_RESULT.effective_raw.toFixed(1);
            const alerts = document.getElementById('dash-alerts');
            const warnings = CURRENT_RESULT.slot_warnings || [];
            if (warnings.length) {
                const lines = [];
                warnings.forEach((warning, index) => {
                    if (index) lines.push(document.createElement('br'));
                    lines.push(document.createTextNode(String(warning)));
                });
                alerts.replaceChildren(...lines);
            } else {
                alerts.textContent = SITE_LOCALE === 'en' ? 'Build calculated with no slot warnings.' : 'Build calculada sem alertas de encaixe.';
            }

            if (topbarBuild) {
                const weaponId = document.getElementById('sel-weapon')?.value;
                const weaponName = equipmentName(weaponId, { custom_weapon: CUSTOM_GOG, custom_talisman: CUSTOM_TALISMAN });
                topbarBuild.textContent = `${weaponName} · ${CURRENT_RESULT.practical_dps.toFixed(1)} DPS`;
            }
        }

        function renderSuggestions() {
            const box = document.getElementById('suggestions-list');
            if (!box || !CURRENT_RESULT) return;
            const skills = CURRENT_RESULT.active_skills || {};
            const suggestions = [];
            if ((skills['Weakness Exploit'] || 0) < 3) suggestions.push('Aumentar Weakness Exploit até Nv.3 costuma melhorar muito a afinidade contra pontos fracos.');
            if ((skills['Critical Boost'] || 0) < 3 && CURRENT_RESULT.capped_affinity > 40) suggestions.push('Com boa afinidade, Critical Boost ganha prioridade.');
            if ((skills['Attack Boost'] || 0) < 4) suggestions.push('Attack Boost Nv.4 destrava bônus percentual de raw.');
            if (CURRENT_RESULT.slot_warnings.length) suggestions.push('Há joias inválidas ou sem espaço. Revise os encaixes destacados no Montador.');
            box.innerHTML = (suggestions.length ? suggestions : ['A build atual não tem lacunas óbvias pelos critérios simples atuais.']).map(t => `<div class="mini-item">${t}</div>`).join('');
        }

        async function saveTalismanToInventory() {
            CUSTOM_TALISMAN = customTalismanPayload();
            const item = { id: `inv_tali_${Date.now()}`, talisman: CUSTOM_TALISMAN };
            const status = document.getElementById('talisman-inventory-status');
            saveTalismansLocal(mergeRecordsById(localTalismans(), [item], 100));
            let savedOnServer = false;
            try {
                const res = await fetch('/api/talismans/inventory', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(item)
                });
                if (!res.ok) throw new Error('Não foi possível salvar o talismã no inventário.');
                savedOnServer = true;
            } catch {}
            await loadTalismanInventory();
            showScreen('inventory');
            if (status) {
                status.textContent = SITE_LOCALE === 'en'
                    ? (savedOnServer ? 'Talisman saved in the browser and on the local server.' : 'Talisman saved in this browser.')
                    : (savedOnServer ? 'Talismã salvo no navegador e no servidor local.' : 'Talismã salvo neste navegador.');
                status.className = 'status-line status-ok';
            }
        }

        function renderTalismanInventory() {
            const box = document.getElementById('talisman-inventory-list');
            if (!box) return;
            if (!TALISMAN_INVENTORY.length) {
                replaceWithMessage(box, SITE_LOCALE === 'en' ? 'No talismans saved yet.' : 'Nenhum talismã cadastrado ainda.');
                return;
            }
            const sorted = [...TALISMAN_INVENTORY].sort((a, b) => a.talisman.name.localeCompare(b.talisman.name, 'pt-BR', { sensitivity: 'base' }));
            const records = sorted.map(item => {
                const t = item.talisman;
                const slotLabels = (t.slots || []).map((level, index) => {
                    const kind = t.slot_kinds?.[index] || 'armor';
                    const label = kind === 'weapon'
                        ? (SITE_LOCALE === 'en' ? 'Weapon' : 'Arma')
                        : (SITE_LOCALE === 'en' ? 'Armor' : 'Armadura');
                    return `${label} Lv${level}`;
                }).join(' · ');
                const record = createUiElement('div', 'mini-item');
                const equip = createActionButton(SITE_LOCALE === 'en' ? 'Equip' : 'Equipar', 'btn btn-secondary', () => equipInventoryTalisman(item.id));
                const remove = createActionButton(SITE_LOCALE === 'en' ? 'Remove' : 'Remover', 'btn btn-danger', () => removeInventoryTalisman(item.id));
                equip.style.marginTop = remove.style.marginTop = '8px';
                equip.style.padding = remove.style.padding = '5px 9px';
                record.append(
                    createUiElement('strong', '', t.name || t.id || (SITE_LOCALE === 'en' ? 'Talisman' : 'Talismã')),
                    document.createElement('br'),
                    createUiElement('span', 'metric-note', `${[t.skill_1, t.skill_2, t.skill_3].filter(Boolean).join(' · ')} | ${slotLabels}`),
                    document.createElement('br'),
                    equip,
                    remove
                );
                return record;
            });
            box.replaceChildren(...records);
        }

        function equipInventoryTalisman(id) {
            const item = TALISMAN_INVENTORY.find(t => t.id === id);
            if (!item) return;
            CUSTOM_TALISMAN = { ...item.talisman };
            document.getElementById('sel-talisman').value = 'custom_talisman';
            onEquipChange();
            showScreen('builder');
        }

        async function removeInventoryTalisman(id) {
            saveTalismansLocal(localTalismans().filter(item => item.id !== id));
            try { await fetch(`/api/talismans/inventory/${encodeURIComponent(id)}`, { method: 'DELETE' }); } catch {}
            await loadTalismanInventory();
        }

        async function loadTalismanInventory() {
            let serverTalismans = [];
            try {
                const res = await fetch('/api/talismans/inventory');
                serverTalismans = res.ok ? await res.json() : [];
            } catch {}
            TALISMAN_INVENTORY = mergeRecordsById(serverTalismans, localTalismans(), 100);
            renderTalismanInventory();
            renderSettingsCounts();
        }


        function setSelectValue(id, value) {
            const el = document.getElementById(id);
            if (!el) return;
            el.value = value;
            if (el.value !== value && el.options.length) el.selectedIndex = 0;
        }

        function assignBuildDecorations(decorationIds = []) {
            const selects = Array.from(document.querySelectorAll('.deco-select'));
            selects.forEach(select => { select.value = ''; });
            const available = selects
                .map((select, index) => ({
                    select, index,
                    level: Number(select.dataset.slotLevel || 0),
                    kind: select.dataset.slotKind || 'armor',
                }))
                .sort((a, b) => a.level - b.level || a.index - b.index);
            const decorations = decorationIds
                .map((id, index) => {
                    const decoration = DECORATION_BY_ID.get(id);
                    return { id, index, level: Number(decoration?.level || 99), kind: decoration?.kind || 'armor' };
                })
                .sort((a, b) => b.level - a.level || a.index - b.index);
            const unassigned = [];
            decorations.forEach(decoration => {
                const slotIndex = available.findIndex(slot =>
                    slot.kind === decoration.kind
                    &&
                    slot.level >= decoration.level
                    && Array.from(slot.select.options).some(option => option.value === decoration.id)
                );
                if (slotIndex < 0) {
                    unassigned.push(decoration.id);
                    return;
                }
                const [slot] = available.splice(slotIndex, 1);
                slot.select.value = decoration.id;
            });
            return unassigned;
        }

        async function loadBuildIntoBuilder(id) {
            const build = SAVED_BUILDS.find(b => b.id === id);
            if (!build) return;
            let keepScenario = false;
            if (typeof chooseBuildScenario === 'function') {
                const choice = await chooseBuildScenario(build.scenario);
                if (choice === null) return;
                keepScenario = choice;
            }
            await applyBuildEquipment(build, keepScenario);
            if (typeof EDITING_BUILD_ID !== 'undefined') EDITING_BUILD_ID = id.startsWith('__') ? null : id;
            showScreen('builder');
            if (typeof saveWorkspaceDraft === 'function') saveWorkspaceDraft();
        }

        async function applyBuildEquipment(build, keepScenario = false) {
            const scenario = keepScenario ? currentScenarioPayload() : build.scenario;
            CUSTOM_GOG = build.equipment.custom_weapon || null;
            CUSTOM_TALISMAN = build.equipment.custom_talisman || null;
            CURRENT_ROTATION_ID = scenario.rotation_id || build.result?.rotation_id || null;
            TRANSCENDED_ARMOR = new Set(build.equipment.transcended_armor || []);
            ['filter-weapons', 'filter-helm', 'filter-chest', 'filter-arms', 'filter-waist', 'filter-legs', 'filter-talisman'].forEach(filterId => {
                const filter = document.getElementById(filterId);
                if (filter) filter.value = '';
            });
            populateDropdowns(false);
            setSelectValue('sel-weapon', build.equipment.weapon_id);
            setSelectValue('sel-helm', build.equipment.helm_id);
            setSelectValue('sel-chest', build.equipment.chest_id);
            setSelectValue('sel-arms', build.equipment.arms_id);
            setSelectValue('sel-waist', build.equipment.waist_id);
            setSelectValue('sel-legs', build.equipment.legs_id);
            setSelectValue('sel-talisman', build.equipment.talisman_id);
            setSelectValue('scenario-monster', scenario.monster_id);
            onMonsterChange();
            setSelectValue('scenario-part', scenario.target_part || 'Media_Ponderada');
            document.getElementById('scenario-wound').checked = !!scenario.wound_active;
            document.getElementById('uptime-agi').value = Math.round((build.scenario.agitator_uptime ?? 0.8) * 100);
            document.getElementById('uptime-burst').value = Math.round((build.scenario.burst_uptime ?? 0.9) * 100);
            document.getElementById('uptime-wex').value = Math.round((build.scenario.weakness_exploit_uptime ?? 0.85) * 100);
            document.getElementById('uptime-adrenaline').value = Math.round((build.scenario.adrenaline_rush_uptime ?? 0) * 100);
            document.getElementById('uptime-foray').value = Math.round((build.scenario.foray_uptime ?? 0) * 100);
            document.getElementById('uptime-ambush').value = Math.round((build.scenario.ambush_uptime ?? 0) * 100);
            document.getElementById('uptime-heroics').value = Math.round((build.scenario.heroics_uptime ?? 0) * 100);
            restoreScenarioDetails(scenario);
            onEquipChange();
            await new Promise(resolve => setTimeout(resolve, 0));
            document.querySelectorAll('.deco-select').forEach(select => { select.value = ''; });
            const unassignedDecorations = assignBuildDecorations(build.equipment.decorations || []);
            document.getElementById('build-name-input').value = build.name;
            await recalculate();
            if (unassignedDecorations.length) {
                setSaveStatus(`${unassignedDecorations.length} adorno(s) não puderam ser encaixados nos slots desta build.`, false);
            }
            if (typeof refreshSlotPickers === 'function') refreshSlotPickers();
        }

        function requestBuildName(currentName) {
            return new Promise(resolve => {
                const overlay = createUiElement('div', 'dialog-overlay');
                const dialog = createUiElement('section', 'app-dialog');
                dialog.setAttribute('role', 'dialog');
                dialog.setAttribute('aria-modal', 'true');
                dialog.setAttribute('aria-labelledby', 'rename-build-title');

                const title = createUiElement('h3', '', SITE_LOCALE === 'en' ? 'Rename build' : 'Renomear build');
                title.id = 'rename-build-title';
                const description = createUiElement(
                    'p',
                    '',
                    SITE_LOCALE === 'en' ? 'Choose a clear name for the comparator.' : 'Escolha um nome claro para o comparador.'
                );
                const input = document.createElement('input');
                input.type = 'text';
                input.maxLength = 120;
                input.value = currentName || '';
                input.setAttribute('aria-label', SITE_LOCALE === 'en' ? 'New build name' : 'Novo nome da build');

                const actions = createUiElement('div', 'app-dialog-actions');
                const close = value => {
                    overlay.remove();
                    resolve(value);
                };
                const cancel = createActionButton(SITE_LOCALE === 'en' ? 'Cancel' : 'Cancelar', 'btn btn-secondary', () => close(null));
                const save = createActionButton(SITE_LOCALE === 'en' ? 'Save' : 'Salvar', 'btn', () => close(input.value.trim() || null));
                actions.append(cancel, save);
                dialog.append(title, description, input, actions);
                overlay.appendChild(dialog);
                overlay.addEventListener('click', event => { if (event.target === overlay) close(null); });
                input.addEventListener('keydown', event => {
                    if (event.key === 'Escape') close(null);
                    if (event.key === 'Enter') close(input.value.trim() || null);
                });
                document.body.appendChild(overlay);
                input.focus();
                input.select();
            });
        }

        async function renameBuild(id) {
            const build = SAVED_BUILDS.find(b => b.id === id);
            if (!build) return;
            const name = await requestBuildName(build.name);
            if (!name) return;
            const renamed = { ...build, name };
            try {
                const response = await fetch('/api/builds/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(renamed)
                });
                if (!response.ok) {
                    const error = await response.json().catch(() => ({}));
                    throw new Error(error.detail || 'Não foi possível renomear a build.');
                }
                saveBuildLocal(renamed);
                await loadSavedBuilds();
                setSaveStatus(SITE_LOCALE === 'en' ? 'Build renamed.' : 'Build renomeada.', true);
            } catch (error) {
                setSaveStatus(error.message || 'Não foi possível renomear a build.', false);
            }
        }


        async function switchSiteLocale(locale) {
            const workspace = typeof snapshotWorkspace === 'function' && GAME_DATA ? snapshotWorkspace() : null;
            const optimizerState = typeof snapshotOptimizer === 'function' && GAME_DATA ? snapshotOptimizer() : null;
            const search = document.getElementById('wiki-search');
            const selectedEntry = WIKI_SELECTED_KEY ? findWikiEntry(...WIKI_SELECTED_KEY.split(':')) : null;
            const selectedTitle = selectedEntry ? wikiEntryTitle(selectedEntry) : '';
            const queryWasSelectedTitle = Boolean(search && selectedTitle && search.value.trim() === selectedTitle);
            SITE_LOCALE = locale;
            localStorage.setItem('mhwilds_locale', SITE_LOCALE);
            translateStaticInterface();
            await loadGameData(true);
            if (workspace && typeof restoreWorkspaceSnapshot === 'function') await restoreWorkspaceSnapshot(workspace);
            if (optimizerState && typeof restoreOptimizerSnapshot === 'function') restoreOptimizerSnapshot(optimizerState);
            await loadDataVersion();
            if (queryWasSelectedTitle && search) {
                const localizedEntry = WIKI_SELECTED_KEY ? findWikiEntry(...WIKI_SELECTED_KEY.split(':')) : null;
                search.value = localizedEntry ? wikiEntryTitle(localizedEntry) : '';
                renderWikiIndex();
            }
            setSaveStatus(SITE_LOCALE === 'pt' ? 'Idioma alterado para Português.' : 'Language changed to English.', true);
            if (typeof translateExperience === 'function') { translateExperience(); refreshUptimeVisibility(); updateWorkspaceContext(); renderBuildLibrary(); routeChanged(ACTIVE_SCREEN, true); }
        }

        function switchVisualTheme(theme) {
            const themes = ['windward', 'scarlet', 'oilwell', 'iceshard', 'wyveria'];
            VISUAL_THEME = themes.includes(theme) ? theme : 'windward';
            document.body.dataset.theme = VISUAL_THEME;
            localStorage.setItem('mhwilds_visual_theme', VISUAL_THEME);
            const select = document.getElementById('appearance-select');
            if (select) select.value = VISUAL_THEME;
        }

        let WIKI_SELECTED_KEY = '';

        const WIKI_MECHANICS = [
            {
                id: 'calculator',
                title_pt: 'Como o calculador funciona',
                title_en: 'How the calculator works',
                description_pt: 'O cálculo combina a arma, as cinco peças de armadura, talismã, adornos válidos, habilidades ativas, cenário, hitzone escolhida e a rotação da arma. Os valores mostram uma estimativa comparável entre builds, e não substituem testes dentro do jogo.',
                description_en: 'The calculation combines the weapon, five armor pieces, talisman, valid decorations, active skills, scenario, selected hitzone, and weapon rotation. Values are comparable build estimates and do not replace in-game testing.',
            },
            {
                id: 'raw', title_pt: 'Dano raw', title_en: 'Raw damage',
                description_pt: 'Raw é o ataque físico da arma antes de hitzones, afiamento, afinidade e modificadores de habilidade. O Raw Efetivo (EFR) exibido pelo app já aplica os bônus ativos relevantes.',
                description_en: 'Raw is a weapon’s physical attack before hitzones, sharpness, affinity, and skill modifiers. The app’s Effective Raw (EFR) already applies relevant active bonuses.',
            },
            {
                id: 'affinity', title_pt: 'Afinidade e dano crítico', title_en: 'Affinity and critical damage',
                description_pt: 'Afinidade é a chance percentual de um golpe crítico. Bônus condicionais, como Ponto Fraco, são ponderados pelo uptime configurado para não presumir que toda a caçada acontece em uma condição perfeita.',
                description_en: 'Affinity is the percentage chance for a critical hit. Conditional bonuses such as Weakness Exploit are weighted by configured uptime instead of assuming the entire hunt occurs under perfect conditions.',
            },
            {
                id: 'element', title_pt: 'Dano elemental e status', title_en: 'Elemental damage and status',
                description_pt: 'Elemento é avaliado contra a fraqueza elemental da parte atingida; status mede acúmulo e usa a modelagem de status do motor. O valor exibido na arma é mantido separado do valor interno usado pelo cálculo quando necessário.',
                description_en: 'Element is evaluated against the struck part’s elemental weakness; status measures buildup and uses the engine’s status model. The value displayed on a weapon remains separate from the internal calculation value when needed.',
            },
            {
                id: 'status', title_pt: 'Fraquezas a status', title_en: 'Status weaknesses',
                description_pt: 'Paralisia, veneno, sono e explosão são exibidos na escala 0–3 da base local: 0 significa resistente e 3 indica a maior vulnerabilidade registrada. Esses valores orientam a escolha de arma e munição, mas não são multiplicadores diretos de dano.',
                description_en: 'Paralysis, poison, sleep, and blast are shown on the local data’s 0–3 scale: 0 means resistant and 3 is the highest recorded vulnerability. These values guide weapon and ammo choice, but are not direct damage multipliers.',
            },
            {
                id: 'hitzone', title_pt: 'Hitzones e partes do monstro', title_en: 'Hitzones and monster parts',
                description_pt: 'Cada parte possui valores próprios para corte, impacto, projétil e elementos. A média das partes é uma aproximação sem distribuição real de acertos; selecione uma parte para analisar uma estratégia focada.',
                description_en: 'Each part has distinct sever, blunt, shot, and elemental values. The average of parts is an approximation without actual hit distribution; select a part to analyze a focused strategy.',
            },
            {
                id: 'uptime', title_pt: 'Uptime de habilidades', title_en: 'Skill uptime',
                description_pt: 'Uptime representa a parcela esperada da rotação em que uma condição está ativa, como monstro enfurecido, Ímpeto, ferida ou vida máxima. Os modos Padrão, Realista e Agressivo alteram essas hipóteses.',
                description_en: 'Uptime represents the expected share of a rotation during which a condition is active, such as enraged monster, Burst, wound, or full health. Default, Realistic, and Aggressive modes change those assumptions.',
            },
            {
                id: 'gog', title_pt: 'Armas Gogartianas e reforços', title_en: 'Gog Artian weapons and reinforcements',
                description_pt: 'Armas Gogartianas são tratadas como armas personalizadas: tipo, raw, afinidade, elemento, afiamento, foco, reforços, slots e habilidades embutidas entram no cálculo. A recomendação de Gog só é indicada para RC 100 ou superior.',
                description_en: 'Gog Artian weapons are treated as custom weapons: type, raw, affinity, element, sharpness, focus, reinforcements, slots, and built-in skills enter the calculation. Gog recommendations are only shown for HR 100 or higher.',
            },
            {
                id: 'rules', title_pt: 'Regras e limites', title_en: 'Rules and limits',
                description_pt: 'O montador rejeita adornos que não cabem nos slots e mantém habilidades de conjunto inativas até alcançar a quantidade mínima de peças. Resultados dependem da base de dados local, das fórmulas implementadas e das condições selecionadas.',
                description_en: 'The builder rejects decorations that do not fit their slots and keeps set skills inactive until the minimum number of pieces is reached. Results depend on the local database, implemented formulas, and selected conditions.',
            },
        ];

        function wikiText(pt, en) { return SITE_LOCALE === 'en' ? en : pt; }

        function wikiCategoryLabel(type) {
            return {
                weapon: wikiText('Armas', 'Weapons'), armor: wikiText('Armaduras', 'Armor'),
                skill: wikiText('Habilidades', 'Skills'), decoration: wikiText('Adornos', 'Decorations'),
                talisman: wikiText('Talismãs', 'Talismans'), monster: wikiText('Monstros', 'Monsters'),
                mechanic: wikiText('Mecânicas e regras', 'Mechanics & rules'),
            }[type] || type;
        }

        function wikiEntryTitle(entry) {
            if (entry.type === 'mechanic') return wikiText(entry.item.title_pt, entry.item.title_en);
            return displayName(entry.item) || entry.item.name || entry.item.name_en || entry.id;
        }

        function wikiEntries() {
            if (!GAME_DATA) return [];
            const withType = (items, type) => (items || [])
                .filter(item => !String(item.id || '').includes('_none'))
                .map(item => ({ type, id: String(item.id), item }));
            return [
                ...withType(GAME_DATA.weapons, 'weapon'),
                ...withType(GAME_DATA.armors, 'armor'),
                ...withType(GAME_DATA.skills, 'skill'),
                ...withType(GAME_DATA.decorations, 'decoration'),
                ...withType(GAME_DATA.talismans, 'talisman'),
                ...withType(GAME_DATA.monsters, 'monster'),
                ...WIKI_MECHANICS.map(item => ({ type: 'mechanic', id: item.id, item })),
            ];
        }

        function findWikiEntry(type, id) {
            return wikiEntries().find(entry => entry.type === type && String(entry.id) === String(id));
        }

        function wikiEntryKey(entry) { return `${entry.type}:${entry.id}`; }

        function wikiSkillLinks(skills = {}) {
            const seen = new Set();
            const links = Object.entries(skills)
                .map(([name, level]) => ({ skill: findSkillData(name), level }))
                .filter(row => row.skill && !seen.has(row.skill.id) && seen.add(row.skill.id));
            if (!links.length) return `<span class="metric-note">${wikiText('Nenhuma habilidade nesta peça.', 'No skills on this piece.')}</span>`;
            return links.map(({ skill, level }) => `<button class="wiki-link" type="button" onclick="openWikiEntry('skill', '${escapeHtml(String(skill.id))}')">${escapeHtml(skillDisplayName(skill.name || skill.name_en))} ${level > 1 ? `${wikiText('Nv.','Lv.')}${level}` : ''}</button>`).join(' · ');
        }

        function wikiEntryIcon(entry) {
            const item = entry.item;
            if (entry.type === 'monster') {
                const source = monsterIconFiles(item.name_en || item.name)[0];
                return source ? `<img src="${escapeHtml(source)}" alt="">` : `<span>${escapeHtml((wikiEntryTitle(entry).match(/\b\w/g) || []).slice(0, 2).join(''))}</span>`;
            }
            if (entry.type === 'weapon') {
                const source = weaponIconFiles(item.weapon_type)[0];
                return source ? `<img src="${wikiFileUrl(source)}" alt="">` : `<span>${escapeHtml(weaponIcon(item.weapon_type))}</span>`;
            }
            if (entry.type === 'armor') {
                const source = armorIconFiles(item.slot_type)[0];
                return source ? `<img src="${wikiFileUrl(source)}" alt="">` : `<span>${escapeHtml(armorIcon(item.slot_type))}</span>`;
            }
            if (entry.type === 'skill' || entry.type === 'decoration') {
                const skill = entry.type === 'skill' ? item.name_en || item.name : item.skill;
                return `<img src="/api/equipment-photo/skill?name=${encodeURIComponent(skill)}" alt="" onerror="this.remove()">`;
            }
            if (entry.type === 'talisman') return `<img src="${wikiFileUrl('MH3icon-Accessory.png')}" alt="">`;
            return '<span>?</span>';
        }

        function wikiFacts(entry) {
            const item = entry.item;
            const fact = (label, value) => ({ label, value });
            if (entry.type === 'weapon') return [
                fact(wikiText('Tipo', 'Type'), weaponTypeDisplay(item)), fact(wikiText('Raridade', 'Rarity'), `R${item.rarity || '-'}`),
                fact('Raw', item.raw ?? '-'), fact(wikiText('Afinidade', 'Affinity'), `${item.affinity || 0}%`),
                fact(wikiText('Elemento / status', 'Element / status'), `${item.element_type || wikiText('Nenhum', 'None')} ${item.element_display || item.element_val || ''}`.trim()),
                fact('Slots', (item.slots || []).join(' · ') || wikiText('Nenhum', 'None')), fact(wikiText('Afiamento', 'Sharpness'), item.sharpness || '-'),
            ];
            if (entry.type === 'armor') return [
                fact(wikiText('Parte', 'Part'), SITE_LOCALE === 'en' ? (SLOT_EN_UI[item.slot_type] || item.slot_type) : (item.slot_type_display || SLOT_PT_UI[item.slot_type] || item.slot_type)), fact(wikiText('Raridade', 'Rarity'), `R${item.rarity || '-'}`),
                fact(wikiText('Defesa', 'Defense'), `${item.defense || 0} / ${item.defense_max || item.defense || 0}`), fact('Slots', (item.slots || []).join(' · ') || wikiText('Nenhum', 'None')),
                fact(wikiText('Conjunto', 'Set'), item.set_bonus_group || wikiText('Sem bônus de conjunto', 'No set bonus')),
            ];
            if (entry.type === 'decoration') return [
                fact(wikiText('Nível de slot', 'Slot level'), item.level || '-'), fact(wikiText('Habilidade', 'Skill'), skillDisplayName(item.skill || '')), fact(wikiText('Pontos', 'Points'), item.points || 1),
            ];
            if (entry.type === 'talisman') return [fact('Slots', (item.slots || []).join(' · ') || wikiText('Nenhum', 'None'))];
            if (entry.type === 'skill') return [
                fact(wikiText('Categoria', 'Category'), item.kind || '-'), fact(wikiText('Níveis', 'Levels'), (item.ranks || []).length || '-'),
            ];
            if (entry.type === 'monster') {
                const hz = item.weighted_hitzone || {};
                return [
                    fact(wikiText('Vida base', 'Base health'), item.base_health || '-'),
                    fact(wikiText('Melhor corte', 'Best sever'), hz.sever ?? '-'),
                    fact(wikiText('Melhor impacto', 'Best blunt'), hz.blunt ?? '-'),
                    fact(wikiText('Melhor projétil', 'Best shot'), hz.shot ?? '-'),
                    fact(wikiText('Paralisia', 'Paralysis'), `${item.status_weaknesses?.paralysis || 0}/3`),
                    fact(wikiText('Veneno', 'Poison'), `${item.status_weaknesses?.poison || 0}/3`),
                    fact(wikiText('Sono', 'Sleep'), `${item.status_weaknesses?.sleep || 0}/3`),
                    fact(wikiText('Explosão', 'Blast'), `${item.status_weaknesses?.blastblight || 0}/3`)
                ];
            }
            return [fact(wikiText('Escopo', 'Scope'), wikiText('Motor de cálculo', 'Calculation engine'))];
        }

        function wikiDescription(entry) {
            const item = entry.item;
            if (entry.type === 'mechanic') return wikiText(item.description_pt, item.description_en);
            if (item.description) return item.description;
            if (entry.type === 'weapon') return wikiText(
                `${wikiEntryTitle(entry)} é uma ${weaponTypeDisplay(item)} de raridade ${item.rarity || '-'} cadastrada na base local. Seus atributos e encaixes abaixo entram diretamente nas comparações de build.`,
                `${wikiEntryTitle(entry)} is a rarity ${item.rarity || '-'} ${weaponTypeDisplay(item)} in the local database. Its attributes and slots below directly feed build comparisons.`
            );
            if (entry.type === 'armor') return wikiText(
                `${wikiEntryTitle(entry)} é uma peça de ${item.slot_type_display || item.slot_type} da base local. Defesa, resistências, slots e habilidades desta peça são considerados ao montar uma build.`,
                `${wikiEntryTitle(entry)} is a ${item.slot_type_display || item.slot_type} armor piece in the local database. Its defense, resistances, slots, and skills are considered when assembling a build.`
            );
            if (entry.type === 'decoration') return wikiText(
                `${wikiEntryTitle(entry)} ocupa um slot de nível ${item.level || 1} e concede ${item.points || 1} ponto(s) de ${skillDisplayName(item.skill || '')}.`,
                `${wikiEntryTitle(entry)} occupies a level ${item.level || 1} slot and grants ${item.points || 1} point(s) of ${skillDisplayName(item.skill || '')}.`
            );
            if (entry.type === 'talisman') return wikiText(
                `${wikiEntryTitle(entry)} é um talismã da base local. Suas habilidades e slots são somados ao equipamento selecionado.`,
                `${wikiEntryTitle(entry)} is a talisman in the local database. Its skills and slots are added to the selected equipment.`
            );
            return wikiText('Sem descrição disponível na base atual.', 'No description is available in the current database.');
        }

        function itemHasWikiSkill(item, skill) {
            return Object.keys(item.skills || {}).some(name => {
                const candidate = findSkillData(name);
                return candidate?.id === skill.id || name === skill.name || name === skill.name_en;
            });
        }

        function wikiRelatedEquipment(skill) {
            const entries = [
                ...(GAME_DATA?.weapons || []).filter(item => itemHasWikiSkill(item, skill)).map(item => ({ type: 'weapon', item })),
                ...(GAME_DATA?.armors || []).filter(item => itemHasWikiSkill(item, skill)).map(item => ({ type: 'armor', item })),
            ].sort((a, b) => displayName(a.item).localeCompare(displayName(b.item), SITE_LOCALE === 'en' ? 'en' : 'pt-BR'));
            const title = SITE_LOCALE === 'en'
                ? `Weapons and armor with this skill (${entries.length})`
                : `Armas e armaduras com esta habilidade (${entries.length})`;
            if (!entries.length) return `<details class="wiki-expand"><summary>${title}</summary><p class="metric-note">${wikiText('Nenhum equipamento cadastrado com esta habilidade.', 'No equipment with this skill is recorded.')}</p></details>`;
            const cards = entries.map(({ type, item }) => {
                const photo = equipmentPhotoSrc({ kind: type, item });
                const meta = type === 'weapon'
                    ? `${weaponTypeDisplay(item)} · R${item.rarity || '-'}`
                    : `${SITE_LOCALE === 'en' ? (SLOT_EN_UI[item.slot_type] || item.slot_type) : (item.slot_type_display || SLOT_PT_UI[item.slot_type] || item.slot_type)} · R${item.rarity || '-'}`;
                return `<div class="wiki-related-item"><div class="wiki-related-photo">${photo ? `<img src="${photo}" alt="" loading="lazy" onerror="this.remove()">` : '<span>?</span>'}</div><div><button class="wiki-link wiki-related-name" type="button" onclick="openWikiEntry('${type}', '${escapeHtml(String(item.id))}')">${escapeHtml(displayName(item))}</button><div class="wiki-related-meta">${escapeHtml(meta)}</div><button class="btn btn-secondary" type="button" style="padding:4px 7px; font-size:.72rem;" onclick="addWishlistItem('${type}', '${escapeHtml(String(item.id))}')">${wikiText('Adicionar à lista', 'Add to wishlist')}</button></div></div>`;
            }).join('');
            return `<details class="wiki-expand"><summary>${title}</summary><div class="wiki-related-grid">${cards}</div></details>`;
        }

        function wikiDetailSections(entry) {
            const item = entry.item;
            const sections = [];
            if (['armor', 'decoration', 'talisman'].includes(entry.type)) sections.push({ title: wikiText('Habilidades relacionadas', 'Related skills'), body: wikiSkillLinks(item.skills || (item.skill ? { [item.skill]: item.points || 1 } : {})) });
            if (entry.type === 'skill' && (item.ranks || []).length) {
                const ranks = item.ranks.map(rank => `<div class="wiki-rank"><span class="wiki-rank-level">${wikiText('Nv.', 'Lv.')} ${rank.level}</span><span>${escapeHtml(rank.description || wikiText('Sem detalhe adicional.', 'No additional detail.'))}${rank.setPiecesRequired ? `<small class="metric-note"><br>${wikiText(`Ativa com ${rank.setPiecesRequired} peças do conjunto.`, `Activates with ${rank.setPiecesRequired} set pieces.`)}</small>` : ''}</span></div>`).join('');
                sections.push({ title: wikiText('Níveis da habilidade', 'Skill levels'), body: `<div class="wiki-rank-list">${ranks}</div>` });
            }
            if (entry.type === 'monster') {
                const parts = (item.hitzones || []).filter(part => !part.is_wound).sort((a, b) => Math.max(b.sever || 0, b.blunt || 0, b.shot || 0) - Math.max(a.sever || 0, a.blunt || 0, a.shot || 0)).slice(0, 12);
                const body = parts.length ? `<div class="wiki-rank-list">${parts.map(part => `<div class="wiki-rank"><span class="wiki-rank-level">${escapeHtml(translatePart(part.part_name || ''))}</span><span>${wikiText('Corte', 'Sever')} ${part.sever || 0} · ${wikiText('Impacto', 'Blunt')} ${part.blunt || 0} · ${wikiText('Projétil', 'Shot')} ${part.shot || 0} · ${wikiText('Melhor elemento', 'Best element')} ${escapeHtml(bestElementForPart(part)?.[0] || '-')}</span></div>`).join('')}</div>` : `<span class="metric-note">${wikiText('Sem hitzones cadastradas.', 'No hitzones recorded.')}</span>`;
                sections.push({ title: wikiText('Partes e hitzones', 'Parts and hitzones'), body });
                const statusRows = SITE_LOCALE === 'en'
                    ? [['Paralysis', 'paralysis'], ['Poison', 'poison'], ['Sleep', 'sleep'], ['Blast', 'blastblight']]
                    : [['Paralisia', 'paralysis'], ['Veneno', 'poison'], ['Sono', 'sleep'], ['Explosão', 'blastblight']];
                const statusBody = `<div class="wiki-fact-grid">${statusRows.map(([label, key]) => {
                    const level = Number(item.status_weaknesses?.[key] || 0);
                    return `<div class="wiki-fact"><span>${escapeHtml(label)}</span><strong>${level}/3 · ${escapeHtml(statusLevelLabel(level))}</strong></div>`;
                }).join('')}</div>`;
                sections.push({ title: wikiText('Fraquezas a status', 'Status weaknesses'), body: statusBody });
            }
            if (entry.type === 'weapon' && Object.keys(item.skills || {}).length) sections.push({ title: wikiText('Habilidades da arma', 'Weapon skills'), body: wikiSkillLinks(item.skills) });
            if (entry.type === 'skill') sections.push({ title: wikiText('Equipamentos relacionados', 'Related equipment'), body: wikiRelatedEquipment(item) });
            return sections;
        }

        function renderWikiArticle() {
            const target = document.getElementById('wiki-article');
            if (!target || !GAME_DATA) return;
            let entry = WIKI_SELECTED_KEY ? findWikiEntry(...WIKI_SELECTED_KEY.split(':')) : null;
            if (!entry) entry = findWikiEntry('mechanic', 'calculator') || wikiEntries()[0];
            if (!entry) return;
            WIKI_SELECTED_KEY = wikiEntryKey(entry);
            const facts = wikiFacts(entry).map(row => `<div class="wiki-fact"><span>${escapeHtml(row.label)}</span><strong>${escapeHtml(String(row.value))}</strong></div>`).join('');
            const sections = wikiDetailSections(entry).map(section => `<section class="wiki-section"><h3>${escapeHtml(section.title)}</h3>${section.body}</section>`).join('');
            const sourceLabel = entry.type === 'mechanic'
                ? wikiText('Baseado nas regras implementadas por este calculador.', 'Based on rules implemented by this calculator.')
                : wikiText('Dados e descrições da base MH Wilds Database; termos complementados por referências da comunidade.', 'Data and descriptions from the MH Wilds Database; terms supplemented by community references.');
            const kiranicoUrl = entry.type === 'monster' ? kiranicoMonsterUrl(entry.item) : '';
            target.innerHTML = `
                <div class="wiki-crumb"><span>${escapeHtml(wikiCategoryLabel(entry.type))}</span><span>/</span><span>${escapeHtml(wikiEntryTitle(entry))}</span></div>
                <div class="wiki-title-row"><div><h2>${escapeHtml(wikiEntryTitle(entry))}</h2></div><div class="wiki-icon">${wikiEntryIcon(entry)}</div></div>
                <p class="wiki-summary">${escapeHtml(wikiDescription(entry))}</p>
                <section class="wiki-section"><h3>${wikiText('Ficha técnica', 'Reference data')}</h3><div class="wiki-fact-grid">${facts}</div></section>
                ${sections}
                <div class="wiki-sources">${escapeHtml(sourceLabel)} <a href="https://docs.wilds.mhdb.io/" target="_blank" rel="noopener">MH Wilds Database</a> · <a href="https://monsterhunterwilds.wiki.fextralife.com/" target="_blank" rel="noopener">Monster Hunter Wilds Wiki</a>${kiranicoUrl ? ` · <a href="${escapeHtml(kiranicoUrl)}" target="_blank" rel="noopener">Kiranico</a>` : ''}</div>
            `;
        }

        function renderWikiIndex() {
            const box = document.getElementById('wiki-results');
            const category = document.getElementById('wiki-category');
            if (!box || !category || !GAME_DATA) return;
            const categoryLabels = ['all', 'weapon', 'armor', 'skill', 'decoration', 'talisman', 'monster', 'mechanic'];
            Array.from(category.options).forEach(option => { option.textContent = option.value === 'all' ? wikiText('Tudo', 'All') : wikiCategoryLabel(option.value); });
            const query = (document.getElementById('wiki-search')?.value || '').trim().toLocaleLowerCase();
            const entries = wikiEntries().filter(entry => {
                const matchesCategory = category.value === 'all' || entry.type === category.value;
                const haystack = `${wikiEntryTitle(entry)} ${entry.item.description || ''} ${entry.item.name_en || ''}`.toLocaleLowerCase();
                return matchesCategory && (!query || haystack.includes(query));
            }).sort((a, b) => wikiEntryTitle(a).localeCompare(wikiEntryTitle(b), SITE_LOCALE === 'en' ? 'en' : 'pt-BR')).slice(0, 100);
            box.innerHTML = entries.length ? entries.map(entry => {
                const key = wikiEntryKey(entry);
                const subtitle = entry.type === 'weapon' ? weaponTypeDisplay(entry.item) : entry.type === 'armor' ? (entry.item.slot_type_display || entry.item.slot_type) : wikiCategoryLabel(entry.type);
                return `<button class="wiki-result ${key === WIKI_SELECTED_KEY ? 'active' : ''}" type="button" onclick="openWikiEntry('${entry.type}', '${escapeHtml(entry.id)}')"><strong>${escapeHtml(wikiEntryTitle(entry))}</strong><small>${escapeHtml(subtitle)}</small></button>`;
            }).join('') : `<div class="wiki-empty">${wikiText('Nenhum verbete encontrado.', 'No entries found.')}</div>`;
            renderWikiArticle();
        }

        function openWikiEntry(type, id) {
            if (typeof openContextWiki === 'function' && (ACTIVE_SCREEN !== 'registry' || document.getElementById('workspace-dialog').open)) { openContextWiki(type, id); return; }
            const entry = findWikiEntry(type, id);
            if (!entry) return;
            WIKI_SELECTED_KEY = wikiEntryKey(entry);
            const category = document.getElementById('wiki-category');
            const search = document.getElementById('wiki-search');
            if (category) category.value = entry.type;
            if (search) search.value = wikiEntryTitle(entry);
            showScreen('registry');
            renderWikiIndex();
            document.getElementById('wiki-article')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        // Mantém compatibilidade com chamadas antigas após a migração para a wiki.
        function renderSkillRegistryData() { renderWikiIndex(); }

        function wishlistCollection(type) {
            return ({ weapon: GAME_DATA?.weapons, armor: GAME_DATA?.armors, decoration: GAME_DATA?.decorations, talisman: GAME_DATA?.talismans })[type] || [];
        }

        function wishlistItem(entry) {
            if (entry.type === 'custom_gog') return { ...entry, name: entry.name || 'Arma Gogartiana', custom: true, crafting_materials: [] };
            if (entry.type === 'custom_talisman') return { ...entry, name: entry.name || 'Talismã Personalizado', custom: true, crafting_materials: [] };
            return wishlistCollection(entry.type).find(item => item.id === entry.id) || null;
        }

        function wishlistKey(entry) { return `${entry.type}:${entry.id}`; }

        function loadWishlist() {
            try {
                const stored = JSON.parse(localStorage.getItem(WISHLIST_STORAGE_KEY) || '[]');
                WISHLIST = Array.isArray(stored) ? stored.filter(entry => entry?.type && entry?.id) : [];
            } catch { WISHLIST = []; }
            renderWishlist();
        }

        function saveWishlist() {
            localStorage.setItem(WISHLIST_STORAGE_KEY, JSON.stringify(WISHLIST));
            renderWishlist();
            renderSettingsCounts();
        }

        function wishlistTypeLabel(type) {
            return ({ weapon: wikiText('Arma', 'Weapon'), armor: wikiText('Armadura', 'Armor'), decoration: wikiText('Adorno', 'Decoration'), talisman: wikiText('Talismã', 'Talisman'), custom_gog: wikiText('Arma Gogartiana', 'Gog Artian weapon'), custom_talisman: wikiText('Talismã personalizado', 'Custom talisman') })[type] || type;
        }

        function wishlistPhoto(entry, item) {
            if (entry.type === 'weapon') return equipmentPhotoSrc({ kind: 'weapon', item });
            if (entry.type === 'armor') return equipmentPhotoSrc({ kind: 'armor', item });
            if (entry.type === 'decoration') return `/api/equipment-photo/skill?name=${encodeURIComponent(item.skill || '')}`;
            if (entry.type === 'talisman') return wikiFileUrl('MH3icon-Accessory.png');
            if (entry.type === 'custom_gog') return `/api/equipment-photo/weapon?name=${encodeURIComponent(GOGMA_WEAPON_BY_TYPE[item.weapon_type] || 'Ostrak Oblivion')}`;
            return '';
        }

        function addWishlistItem(type, id, options = {}) {
            const collection = wishlistCollection(type);
            const item = collection.find(candidate => candidate.id === id);
            if (!item) return false;
            const entry = { type, id, quantity: Math.max(1, MaterialPlan.quantity(options.quantity, 1)) };
            const existing = WISHLIST.find(existing => wishlistKey(existing) === wishlistKey(entry));
            if (existing) {
                if ((existing.quantity || 1) >= entry.quantity) return false;
                existing.quantity = entry.quantity;
            } else WISHLIST.push(entry);
            if (!options.defer) saveWishlist();
            return true;
        }

        function addWishlistCustom(type, item, options = {}) {
            if (!item) return false;
            const id = `${type}_${String(item.name || 'item').toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
            const entry = { type, id, name: item.name, weapon_type: item.weapon_type };
            if (WISHLIST.some(existing => wishlistKey(existing) === wishlistKey(entry))) return false;
            WISHLIST.push(entry);
            if (!options.defer) saveWishlist();
            return true;
        }

        function wishlistEntriesFromEquipment(equipment = {}) {
            const entries = MaterialPlan.equipmentEntries(equipment);
            const added = entries.reduce((count, {type, id, quantity}) => count + Number(addWishlistItem(type, id, {defer: true, quantity})), 0);
            let customAdded = 0;
            if (equipment.weapon_id === 'custom_gog_weapon') customAdded += Number(addWishlistCustom('custom_gog', equipment.custom_weapon, {defer: true}));
            if (equipment.talisman_id === 'custom_talisman') customAdded += Number(addWishlistCustom('custom_talisman', equipment.custom_talisman, {defer: true}));
            if (added || customAdded) saveWishlist();
            return added + Number(customAdded);
        }

        function currentBuilderEquipment() {
            return {
                weapon_id: document.getElementById('sel-weapon')?.value || '', helm_id: document.getElementById('sel-helm')?.value || '', chest_id: document.getElementById('sel-chest')?.value || '',
                arms_id: document.getElementById('sel-arms')?.value || '', waist_id: document.getElementById('sel-waist')?.value || '', legs_id: document.getElementById('sel-legs')?.value || '',
                talisman_id: document.getElementById('sel-talisman')?.value || '', decorations: Array.from(document.querySelectorAll('.deco-select')).map(select => select.value).filter(Boolean),
                custom_weapon: CUSTOM_GOG, custom_talisman: CUSTOM_TALISMAN,
            };
        }

        function addCurrentBuildToWishlist() {
            const added = wishlistEntriesFromEquipment(currentBuilderEquipment());
            setSaveStatus(added ? `${added} ${added === 1 ? 'item adicionado' : 'itens adicionados'} à Lista de Desejos.` : 'Todos os itens da build já estão na Lista de Desejos.', Boolean(added));
            showScreen('wishlist');
        }

        function addOptimizerResultToWishlist(idx) {
            const build = OPTIMIZER_RESULTS[idx];
            if (!build) return;
            const selected = build;
            if (!selected) return;
            const added = wishlistEntriesFromEquipment(selected.equipment || {});
            const container = document.getElementById('optimizer-results-container');
            if (container && added) container.querySelector(`[data-wishlist-status="${idx}"]`)?.replaceChildren(document.createTextNode(SITE_LOCALE === 'en' ? 'Added to wishlist.' : 'Adicionada à Lista de Desejos.'));
            showScreen('wishlist');
        }

        function removeWishlistItem(index) {
            WISHLIST.splice(index, 1);
            saveWishlist();
        }

        function clearWishlist() {
            if (WISHLIST.length && !confirm(SITE_LOCALE === 'en' ? 'Remove every item from the wishlist? Your material inventory will remain.' : 'Remover todos os itens da lista de desejos? Seu estoque de materiais será mantido.')) return;
            WISHLIST = [];
            saveWishlist();
        }

        function renderWishlist() {
            const itemsBox = document.getElementById('wishlist-items');
            const materialsBox = document.getElementById('wishlist-materials');
            const navCount = document.getElementById('wishlist-nav-count');
            if (navCount) navCount.textContent = String(WISHLIST.length);
            if (!itemsBox || !materialsBox || !GAME_DATA) return;
            const records = WISHLIST.map((entry, index) => ({ entry, item: wishlistItem(entry), index })).filter(record => record.item);
            const clearButton = document.querySelector('#screen-wishlist .btn-danger');
            if (clearButton) clearButton.hidden = !records.length;
            if (!records.length) {
                const message = wikiText('Nenhum item salvo ainda. Use a Wiki, o Montador ou uma recomendação do Otimizador.', 'No items saved yet. Use the Wiki, Builder, or an Optimizer recommendation.');
                if (typeof emptyState === 'function') itemsBox.replaceChildren(emptyState(wikiText('Sua lista está vazia', 'Your list is empty'),wikiText('Escolher uma build','Choose a build'),()=>showScreen('builds')));
                else itemsBox.innerHTML = `<div class="mini-item muted">${message}</div>`;
                materialsBox.replaceChildren();
                return;
            }
            itemsBox.innerHTML = records.map(({ entry, item, index }) => {
                const photo = wishlistPhoto(entry, item);
                const materials = item.crafting_materials || [];
                const recipe = item.custom
                    ? wikiText('Receita personalizada: reforços Gog não possuem lista fixa de materiais.', 'Custom recipe: Gog reinforcements do not have a fixed material list.')
                    : materials.length
                        ? wikiText(`${materials.length} material(is) de craft`, `${materials.length} crafting material(s)`)
                        : wikiText('Sem receita disponível na base', 'No recipe available in the database');
                return `<div class="wishlist-item"><div class="wishlist-photo">${photo ? `<img src="${photo}" alt="" loading="lazy" onerror="this.remove()">` : '<span>?</span>'}</div><div><strong>${escapeHtml(displayName(item) || item.name || entry.name || entry.id)}</strong><div class="metric-note">${Math.max(1, MaterialPlan.quantity(entry.quantity, 1))}x · ${escapeHtml(wishlistTypeLabel(entry.type))} · ${escapeHtml(recipe)}</div></div><button class="btn btn-secondary" type="button" style="padding:5px 8px;" onclick="removeWishlistItem(${index})">${wikiText('Remover', 'Remove')}</button></div>`;
            }).join('');

            renderMaterialPlan(records, materialsBox);
        }

        async function deleteBuild(id) {
            try { await fetch(`/api/builds/${encodeURIComponent(id)}`, { method: 'DELETE' }); } catch {}
            const builds = localBuilds().filter(build => build.id !== id);
            localStorage.setItem('mhwilds_saved_builds', JSON.stringify(builds));
            await loadSavedBuilds();
        }

        function applyOptimizerPreset(name) {
            const presets = {
                fast: { ab: 0, wex: 0, cb: 0, sort: 'practical_dps', mode: 'fast' },
                raw: { ab: 4, wex: 2, cb: 1, sort: 'practical_dps', mode: 'fast' },
                affinity: { ab: 0, wex: 3, cb: 1, sort: 'combined_score', mode: 'fast' },
                cycle: { ab: 4, wex: 0, cb: 0, sort: 'damage_per_cycle', mode: 'fast' }
            };
            const preset = presets[name] || presets.fast;
            document.getElementById('opt-req-ab').value = preset.ab;
            document.getElementById('opt-req-wex').value = preset.wex;
            document.getElementById('opt-req-cb').value = preset.cb;
            document.getElementById('opt-sort-by').value = preset.sort;
            document.getElementById('opt-search-mode').value = preset.mode;
        }

        function optimizerLimits() {
            const mode = document.getElementById('opt-search-mode').value;
            if (mode === 'deep') return { search_limit: 6000, armor_pool_limit: 18, weapon_pool_limit: 8, talisman_pool_limit: 20, max_results: 15 };
            if (mode === 'balanced') return { search_limit: 2500, armor_pool_limit: 14, weapon_pool_limit: 5, talisman_pool_limit: 12, max_results: 10 };
            return { search_limit: 900, armor_pool_limit: 8, weapon_pool_limit: 2, talisman_pool_limit: 6, max_results: 5 };
        }

        async function runOptimization() {
            if (![...document.querySelectorAll('#screen-optimizer input')].every(input => input.reportValidity())) return;
            const requestId = ++OPTIMIZER_REQUEST_ID;
            const inputKey = optimizerInputKey();
            OPTIMIZER_RESULTS = [];
            const button = document.getElementById('btn-run-optimizer');
            const container = document.getElementById('optimizer-results-container');
            if (button) button.disabled = true;
            if (button) button.innerText = SITE_LOCALE === 'en' ? 'Optimizing...' : 'Otimizando...';
            if (document.getElementById('cancel-optimizer')) document.getElementById('cancel-optimizer').hidden = false;
            if (container) container.innerHTML = `<div class="mini-item muted">${SITE_LOCALE === 'en' ? 'Calculating combinations. This may take a few seconds...' : 'Calculando combinações. Aguarde alguns segundos...'}</div>`;
            const weaponId = document.getElementById('opt-weapon-id').value;
            const payload = {
                weapon_type: document.getElementById('opt-weapon-type').value,
                weapon_id: weaponId || null,
                target_skills: collectOptimizerSkills(),
                monster_id: document.getElementById('opt-monster-id').value,
                rotation_id: document.getElementById('opt-rotation-id').value || null,
                preset_id: document.getElementById('opt-meta-preset').value || null,
                use_transcendence: document.getElementById('opt-use-transcendence').checked,
                scenario: {
                    ...(OPTIMIZER_SCENARIO_BASE || currentScenarioPayload()),
                    custom_monster: null,
                    monster_id: document.getElementById('opt-monster-id').value,
                    rotation_id: document.getElementById('opt-rotation-id').value || null,
                    target_part: document.getElementById('opt-target-part').value || 'Media_Ponderada',
                    agitator_uptime: pct('opt-up-agi'),
                    burst_uptime: pct('opt-up-burst'),
                    weakness_exploit_uptime: pct('opt-up-wex'),
                    offensive_guard_uptime: pct('opt-up-og'),
                    foray_uptime: pct('opt-up-foray'),
                    adrenaline_rush_uptime: pct('opt-up-adrenaline'),
                    ambush_uptime: pct('opt-up-ambush'),
                    heroics_uptime: pct('opt-up-heroics'),
                    frenzy_antivirus_uptime: pct('opt-up-frenzy'),
                    peak_performance_uptime: pct('opt-up-peak'),
                    resentment_uptime: pct('opt-up-resentment'),
                    coalescence_uptime: pct('opt-up-coal')
                },
                sort_by: document.getElementById('opt-sort-by').value,
                talismans: document.getElementById('opt-use-inventory').checked ? TALISMAN_INVENTORY : [],
                ...optimizerLimits()
            };

            try {
                const res = await fetch('/api/optimizer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || 'Erro ao otimizar.');
                }
                const builds = await res.json();
                if (requestId !== OPTIMIZER_REQUEST_ID) return;
                if (inputKey !== optimizerInputKey()) throw new Error(SITE_LOCALE === 'en' ? 'Filters changed. Run a new search.' : 'Filtros alterados. Execute uma nova busca.');
                OPTIMIZER_RESULTS = builds;
                renderOptimizerResults();
                await refreshWeaponRecommendation();
            } catch (error) {
                if (requestId !== OPTIMIZER_REQUEST_ID) return;
                if (container) {
                    container.innerHTML = `<div class="mini-item" style="color:var(--danger);">${escapeHtml(error.message || (SITE_LOCALE === 'en' ? 'Could not run the optimizer.' : 'Não foi possível executar o otimizador.'))}</div>`;
                }
            } finally {
                if (button && requestId === OPTIMIZER_REQUEST_ID) {
                    button.disabled = false;
                    button.innerText = uiText('Executar Otimização');
                    if (document.getElementById('cancel-optimizer')) document.getElementById('cancel-optimizer').hidden = true;
                }
            }
        }

        function renderOptimizerResults() {
            if (typeof renderRecommendationCards === 'function') { renderRecommendationCards(); return; }
            const container = document.getElementById('optimizer-results-container');
            container.innerHTML = '';
            if (!OPTIMIZER_RESULTS.length) {
                container.innerHTML = `<p style="color:var(--text-muted);">${SITE_LOCALE === 'en' ? 'No combinations found for these filters.' : 'Nenhuma combinação encontrada com esses filtros.'}</p>`;
                return;
            }
            const presetId = document.getElementById('opt-meta-preset')?.value || '';
            const preset = META_PRESETS.find(item => item.id === presetId);
            const isGogCategory = preset?.weapon_recommendation_mode === 'gog';
            const bestDps = Math.max(...OPTIMIZER_RESULTS.map(build => Number(build.result?.practical_dps || 0)));
            const resultCards = OPTIMIZER_RESULTS.map((b, idx) => {
                const currentDps = Number(b.result?.practical_dps || 0);
                const gap = bestDps ? (1 - currentDps / bestDps) * 100 : 0;
                const weapon = (GAME_DATA.weapons || []).find(item => item.id === b.equipment.weapon_id);
                const armorIds = [b.equipment.helm_id, b.equipment.chest_id, b.equipment.arms_id, b.equipment.waist_id, b.equipment.legs_id];
                const armorNames = armorIds.map(id => (GAME_DATA.armors || []).find(item => item.id === id)?.name).filter(Boolean);
                const elementShare = Number(b.result.damage_per_cycle || 0) > 0
                    ? (Number(b.result.elemental_damage_per_cycle || 0) / Number(b.result.damage_per_cycle || 1)) * 100
                    : 0;
                const weaponSummary = isGogCategory
                    ? `${SITE_LOCALE === 'en' ? 'Gog Artian weapon already calculated with the armor' : 'GogmaArtiana já calculada com a armadura'}: ${(b.equipment?.custom_weapon?.skill_1 && b.equipment?.custom_weapon?.skill_2) ? `${escapeHtml(skillDisplayName(b.equipment.custom_weapon.skill_1))} + ${escapeHtml(skillDisplayName(b.equipment.custom_weapon.skill_2))}` : (SITE_LOCALE === 'en' ? 'reduced RNG route' : 'rotação de RNG reduzido')}.`
                    : `<strong>${escapeHtml(weapon?.name || (SITE_LOCALE === 'en' ? 'Weapon' : 'Arma'))}</strong>`;
                return `
                    <div style="background:#0d141e; border:1px solid var(--card-border); padding:12px; border-radius:6px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:10px;">
                            <div><strong>${idx + 1}. ${escapeHtml(b.name || b.id || (SITE_LOCALE === 'en' ? 'Optimized build' : 'Build otimizada'))}</strong>${currentDps === bestDps ? ` <span class="tag">${SITE_LOCALE === 'en' ? 'Highest DPS found' : 'Maior DPS encontrado'}</span>` : ''}</div>
                            <span style="color:${idx === 0 ? 'var(--accent)' : 'var(--text-muted)'}; font-weight:bold;">${b.result.practical_dps} DPS${idx ? ` · -${gap.toFixed(1)}%` : ''}</span>
                        </div>
                        <p style="font-size:0.8rem; color:var(--text-muted); margin-top:4px;">${escapeHtml(b.description || (SITE_LOCALE === 'en' ? 'No description.' : 'Sem descrição.'))}</p>
                        <div class="metric-note">${escapeHtml(optimizerEvidence(b))}</div>
                        <div class="metric-note">${weaponSummary} · ${armorNames.map(escapeHtml).join(' · ')}</div>
                        <div class="metric-note">${SITE_LOCALE === 'en' ? 'Cycle' : 'Ciclo'} ${b.result.damage_per_cycle} | Min ${b.result.damage_per_min} | ${SITE_LOCALE === 'en' ? 'Score' : 'Nota'} ${b.result.combined_score}</div>
                        <div class="metric-note">${escapeHtml(translatePart(b.result.target_part_name || ''))} · HZ ${SITE_LOCALE === 'en' ? 'physical' : 'físico'} ${b.result.physical_hitzone ?? 0} · HZ elemental ${b.result.elemental_hitzone ?? 0} · ${SITE_LOCALE === 'en' ? 'physical/cycle' : 'físico/ciclo'} ${b.result.physical_damage_per_cycle ?? 0} · ${SITE_LOCALE === 'en' ? 'elemental/cycle' : 'elemental/ciclo'} ${b.result.elemental_damage_per_cycle ?? 0} (${elementShare.toFixed(1)}%)</div>
                        <div class="optimizer-actions">
                            <button class="btn btn-secondary" style="padding:5px 9px;" onclick="loadOptimizerResult(${idx})">${plannerText('Carregar no Montador', 'Load in Builder')}</button>
                            <button class="btn" style="padding:5px 9px;" onclick="saveOptimizerResult(${idx})">${plannerText('Salvar no Comparador', 'Save to Comparator')}</button>
                            <button class="btn btn-secondary" style="padding:5px 9px;" onclick="addOptimizerResultToWishlist(${idx})">${SITE_LOCALE === 'en' ? 'Add to wishlist' : 'Adicionar à Lista'}</button>
                        </div>
                        <div class="metric-note" data-wishlist-status="${idx}" style="margin-top:6px;"></div>
                    </div>
                `;
            });
            container.innerHTML = resultCards.join('');
        }

        function gogOptionMarkup(option, kind, context = 'optimizer') {
            const weapon = option.weapon;
            const skills = (option.desired_skills || []).map(skill => skillDisplayName(skill)).join(' + ');
            const elementLabels = { Fire: 'Fogo', Water: 'Água', Thunder: 'Trovão', Ice: 'Gelo', Dragon: 'Dragão', None: 'Sem elemento' };
            return `<div class="gog-option ${kind === 'perfect' ? 'gog-option-perfect' : ''}">
                <div style="display:flex; justify-content:space-between; gap:10px; align-items:flex-start;">
                    <div><h4>${escapeHtml(option.label)}</h4><div class="metric-note">${escapeHtml(option.rng_level)} · ${escapeHtml(option.focus)}</div></div>
                    <span class="tag">${kind === 'perfect' ? 'Alto RNG' : '1 habilidade-alvo'}</span>
                </div>
                <div class="gog-statline">
                    <span class="tag">Raw ${weapon.raw}</span><span class="tag">Afinidade ${weapon.affinity}%</span>
                    <span class="tag">${escapeHtml(elementLabels[weapon.element_type] || weapon.element_type)} ${weapon.element_display ?? ((weapon.element_val || 0) * 10)}</span>
                    <span class="tag">Slots ${weapon.slots.join('-')}</span>
                </div>
                <p class="metric-note"><strong>Habilidades:</strong> ${escapeHtml(skills)}. ${escapeHtml(skillDisplayName(option.acceptable_second_skill))}</p>
                <p class="metric-note">${escapeHtml(option.rationale)}</p>
                <div class="metric-note"><strong>Reforços:</strong> ${option.artian_reinforcements.map(escapeHtml).join(' · ')}</div>
                <ol class="gog-steps">${option.crafting_steps.map(step => `<li>${escapeHtml(step)}</li>`).join('')}</ol>
                <button class="btn ${kind === 'perfect' ? '' : 'btn-secondary'}" type="button" onclick="${context === 'builder' ? 'applyBuilderGog' : 'applyRecommendedGog'}('${kind}')">${kind === 'perfect' ? (SITE_LOCALE === 'en' ? 'Use high RNG weapon' : 'Usar arma de alto RNG') : (SITE_LOCALE === 'en' ? 'Use reduced RNG weapon' : 'Usar arma de RNG reduzido')}</button>
            </div>`;
        }

        async function recommendGogForCurrentBuild() {
            const panel = document.getElementById('builder-gog-recommendation');
            const selectedWeapon = document.getElementById('sel-weapon')?.value === 'custom_gog_weapon'
                ? CUSTOM_GOG
                : getSelected('sel-weapon', GAME_DATA?.weapons || []);
            if (!panel || !selectedWeapon?.weapon_type) {
                setSaveStatus(SITE_LOCALE === 'en' ? 'Select a weapon class first.' : 'Selecione primeiro uma classe de arma.', false);
                return;
            }
            const scenario = currentScenarioPayload();
            const candidates = META_PRESETS.filter(preset =>
                preset.weapon_type === selectedWeapon.weapon_type
                && preset.weapon_recommendation_mode === 'gog'
                && Number(preset.hunter_rank_min || 0) >= 100
            );
            const targetPreset = candidates.find(preset =>
                preset.monster_id === scenario.monster_id
                && (String(preset.profile).startsWith('at_') || preset.profile === 'gogmazios')
            ) || candidates.find(preset => preset.profile === 'geral') || candidates[0];
            if (!targetPreset) {
                setSaveStatus(SITE_LOCALE === 'en' ? 'No RC100+ Gog route is available for this class.' : 'Não há uma rota Gog RC100+ para esta classe.', false);
                return;
            }
            panel.style.display = 'block';
            panel.innerHTML = `<div class="muted">${SITE_LOCALE === 'en' ? 'Calculating a Gog weapon for the current monster and rotation...' : 'Calculando uma arma Gog para o monstro e a rotação atuais...'}</div>`;
            try {
                const response = await fetch('/api/gog-recommendation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        weapon_type: selectedWeapon.weapon_type,
                        monster_id: scenario.monster_id,
                        rotation_id: CURRENT_ROTATION_ID || CURRENT_RESULT?.rotation_id || null,
                        preset_id: targetPreset.id,
                        target_part: scenario.target_part || 'Media_Ponderada',
                    }),
                });
                if (!response.ok) {
                    const error = await response.json().catch(() => ({}));
                    throw new Error(error.detail || 'Não foi possível recomendar a arma Gog.');
                }
                BUILDER_GOG_RECOMMENDATION = await response.json();
                panel.innerHTML = `
                    <div class="header-bar" style="margin-bottom:12px;"><div><h3 style="margin:0;">${SITE_LOCALE === 'en' ? 'Gog Weapon Recommendation' : 'Recomendação de Arma Gog'}</h3><div class="metric-note">${escapeHtml(BUILDER_GOG_RECOMMENDATION.situation)} · ${SITE_LOCALE === 'en' ? 'best element' : 'melhor elemento'}: ${escapeHtml(BUILDER_GOG_RECOMMENDATION.best_element)} · HZ ${BUILDER_GOG_RECOMMENDATION.element_hitzone ?? 0}</div></div><span class="tag">RC 100+</span></div>
                    <div class="gog-options-grid">${gogOptionMarkup(BUILDER_GOG_RECOMMENDATION.perfect, 'perfect', 'builder')}${gogOptionMarkup(BUILDER_GOG_RECOMMENDATION.accessible, 'accessible', 'builder')}</div>`;
            } catch (error) {
                BUILDER_GOG_RECOMMENDATION = null;
                panel.innerHTML = `<div style="color:var(--danger);">${escapeHtml(error.message)}</div>`;
            }
        }

        function applyBuilderGog(kind) {
            const option = BUILDER_GOG_RECOMMENDATION?.[kind];
            if (!option) return;
            CUSTOM_GOG = JSON.parse(JSON.stringify(option.weapon));
            fillGogEditor(CUSTOM_GOG);
            document.getElementById('sel-weapon').value = 'custom_gog_weapon';
            onEquipChange();
            setSaveStatus(`${option.label} aplicada ao Montador Livre.`, true);
        }

        async function loadGogRecommendation() {
            const panel = document.getElementById('gog-recommendation-panel');
            if (!panel) return;
            const presetId = document.getElementById('opt-meta-preset')?.value || '';
            const preset = META_PRESETS.find(item => item.id === presetId);
            if (!preset || preset.weapon_recommendation_mode !== 'gog' || Number(preset.hunter_rank_min || 0) < 100) {
                hideGogRecommendation();
                return;
            }
            panel.style.display = 'block';
            panel.innerHTML = '<div class="muted">Calculando a arma Gog mais adequada para este monstro e combo...</div>';
            const payload = {
                weapon_type: document.getElementById('opt-weapon-type').value,
                monster_id: document.getElementById('opt-monster-id').value,
                rotation_id: document.getElementById('opt-rotation-id').value || null,
                preset_id: presetId,
                target_part: document.getElementById('opt-target-part').value || 'Media_Ponderada'
            };
            try {
                const response = await fetch('/api/gog-recommendation', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
                });
                if (!response.ok) {
                    const error = await response.json().catch(() => ({}));
                    throw new Error(error.detail || 'Não foi possível recomendar a arma Gog.');
                }
                GOG_RECOMMENDATION = await response.json();
                panel.innerHTML = `
                    <div class="header-bar" style="margin-bottom:12px;">
                        <div><h3 style="margin:0;">Recomendação de Arma Gog</h3><div class="metric-note">${escapeHtml(GOG_RECOMMENDATION.situation)} · melhor elemento: ${escapeHtml(GOG_RECOMMENDATION.best_element)} · HZ ${GOG_RECOMMENDATION.element_hitzone ?? 0}</div></div>
                    </div>
                    <div class="gog-options-grid">${gogOptionMarkup(GOG_RECOMMENDATION.perfect, 'perfect')}${gogOptionMarkup(GOG_RECOMMENDATION.accessible, 'accessible')}</div>
                    <p class="metric-note" style="margin-top:10px;">Os atributos são uma aproximação calculável da rota de reforço indicada. A opção perfeita exige as duas habilidades listadas e a build otimizada reserva peças para ativar ambas; a rota acessível exige somente a primeira habilidade.</p>`;
            } catch (error) {
                GOG_RECOMMENDATION = null;
                panel.innerHTML = `<div style="color:var(--danger);">${escapeHtml(error.message)}</div>`;
            }
        }

        function hideGogRecommendation() {
            GOG_RECOMMENDATION = null;
            const panel = document.getElementById('gog-recommendation-panel');
            if (panel) {
                panel.style.display = 'none';
                panel.innerHTML = '';
            }
        }

        function hideProgressionWeaponRecommendation() {
            const panel = document.getElementById('progression-weapon-recommendation-panel');
            if (panel) {
                panel.style.display = 'none';
                panel.innerHTML = '';
            }
        }

        function syncWeaponRecommendationPolicy(preset) {
            const specificWeapon = document.getElementById('opt-specific-weapon-group');
            const isGogCategory = preset?.weapon_recommendation_mode === 'gog';
            if (specificWeapon) specificWeapon.style.display = isGogCategory ? 'none' : '';
            if (isGogCategory) {
                const select = document.getElementById('opt-weapon-id');
                if (select) select.value = '';
            }
        }

        function showProgressionWeaponRecommendation(preset) {
            const panel = document.getElementById('progression-weapon-recommendation-panel');
            if (!panel) return;
            if (!OPTIMIZER_RESULTS.length) {
                hideProgressionWeaponRecommendation();
                return;
            }
            const build = OPTIMIZER_RESULTS[0];
            const weapon = (GAME_DATA?.weapons || []).find(item => item.id === build.equipment.weapon_id);
            if (!weapon) return;
            const guideUrl = preset.source_urls?.[0];
            const guideLink = guideUrl
                ? `<a href="${escapeHtml(guideUrl)}" target="_blank" rel="noreferrer">Abrir guia da arma</a>`
                : '';
            panel.style.display = 'block';
            panel.innerHTML = `
                <div class="header-bar" style="margin-bottom:8px;">
                    <div><h3 style="margin:0;">Recomendação de Arma de Progressão</h3><div class="metric-note">Apenas armas normais da árvore indicada pelo guia são sugeridas nesta etapa.</div></div>
                    <span class="tag">RC ${preset.hunter_rank_min}+</span>
                </div>
                <div class="metric-note"><strong>${escapeHtml(weapon.name)}</strong>${weapon.series ? ` · árvore ${escapeHtml(weapon.series)}` : ''}</div>
                <div class="metric-note">${escapeHtml(build.result.rotation_name)} · ${build.result.practical_dps} DPS · ${build.result.damage_per_cycle} dano por rotação · HZ físico ${build.result.physical_hitzone ?? 0} · HZ elemental ${build.result.elemental_hitzone ?? 0}</div>
                <div class="action-strip" style="margin-top:10px;"><button class="btn" type="button" onclick="loadOptimizerResult(0)">Usar build de progressão</button>${guideLink}</div>`;
        }

        async function refreshWeaponRecommendation() {
            const presetId = document.getElementById('opt-meta-preset')?.value || '';
            const preset = META_PRESETS.find(item => item.id === presetId);
            if (!preset) {
                hideGogRecommendation();
                hideProgressionWeaponRecommendation();
                return;
            }
            if (preset.weapon_recommendation_mode === 'progression') {
                hideGogRecommendation();
                showProgressionWeaponRecommendation(preset);
                return;
            }
            hideProgressionWeaponRecommendation();
            await loadGogRecommendation();
        }

        function fillGogEditor(weapon) {
            const fields = {
                'gog-name': weapon.name, 'gog-type': weapon.weapon_type, 'gog-raw': weapon.raw,
                'gog-aff': weapon.affinity, 'gog-nature': weapon.element_nature,
                'gog-ele-type': weapon.element_type, 'gog-ele-val': weapon.element_display ?? ((weapon.element_val || 0) * 10),
                'gog-focus': weapon.gog_focus || 'none',
                'gog-sharp': weapon.best_sharpness, 'gog-sharp-units': weapon.sharpness_units,
                'gog-prev-sharp': weapon.prev_sharpness, 'gog-sk1-name': weapon.skill_1 || '',
                'gog-sk1-lvl': weapon.skill_1_lvl || 1, 'gog-sk2-name': weapon.skill_2 || '',
                'gog-sk2-lvl': weapon.skill_2_lvl || 1, 'gog-sk3-name': weapon.skill_3 || '',
                'gog-sk3-lvl': weapon.skill_3_lvl || 1
            };
            Object.entries(fields).forEach(([id, value]) => {
                const field = document.getElementById(id);
                if (!field) return;
                if (field.tagName === 'SELECT' && value && !Array.from(field.options).some(option => option.value === String(value))) {
                    field.add(new Option(skillDisplayName(String(value)), String(value)));
                }
                field.value = value;
            });
            (weapon.slots || []).forEach((slot, index) => { const field = document.getElementById(`gog-s${index + 1}`); if (field) field.value = slot; });
            Array.from(document.querySelectorAll('.gog-reinforcement')).forEach((field, index) => {
                field.value = (weapon.reinforcements || [])[index] || '';
            });
            renderGogWeaponPreview();
        }

        function optimizerBuildWithGog(kind, resultIndex = 0) {
            const option = GOG_RECOMMENDATION?.[kind];
            const base = OPTIMIZER_RESULTS[resultIndex];
            if (kind === 'perfect' && base?.equipment?.custom_weapon) return structuredClone(base);
            if (!option || !base) return null;
            const build = JSON.parse(JSON.stringify(base));
            build.id = '__optimizer_gog_preview';
            build.name = `${base.name.split(' #')[0]} · ${option.label}`;
            build.equipment.weapon_id = 'custom_gog_weapon';
            build.equipment.custom_weapon = option.weapon;
            return build;
        }

        async function applyRecommendedGog(kind, resultIndex = 0) {
            const presetId = document.getElementById('opt-meta-preset')?.value || '';
            const preset = META_PRESETS.find(item => item.id === presetId);
            if (!preset || preset.weapon_recommendation_mode !== 'gog' || Number(preset.hunter_rank_min || 0) < 100) {
                setSaveStatus('Armas GogmaArtianas só podem ser usadas em builds RC100+.', false);
                return;
            }
            const option = GOG_RECOMMENDATION?.[kind];
            const build = optimizerBuildWithGog(kind, resultIndex);
            if (!option || !build) return;
            fillGogEditor(option.weapon);
            SAVED_BUILDS = SAVED_BUILDS.filter(item => item.id !== build.id);
            SAVED_BUILDS.push(build);
            await loadBuildIntoBuilder(build.id);
            SAVED_BUILDS = SAVED_BUILDS.filter(item => item.id !== build.id);
            setSaveStatus(`${option.label} aplicada. O resultado foi recalculado no Montador.`, true);
        }

        async function loadOptimizerResult(idx) {
            const build = OPTIMIZER_RESULTS[idx];
            if (!build) return;
            const preview = JSON.parse(JSON.stringify(build));
            SAVED_BUILDS = SAVED_BUILDS.filter(b => b.id !== '__optimizer_preview');
            preview.id = '__optimizer_preview';
            SAVED_BUILDS.push(preview);
            await loadBuildIntoBuilder('__optimizer_preview');
            SAVED_BUILDS = SAVED_BUILDS.filter(b => b.id !== '__optimizer_preview');
        }

        async function saveOptimizerResult(idx) {
            const build = OPTIMIZER_RESULTS[idx];
            if (!build) return;
            const saved = structuredClone(build);
            if (!saved) {
                setSaveStatus('Aguarde a recomendação da arma Gog antes de salvar esta build.', false);
                return;
            }
            saved.id = `build_${Date.now()}`;
            saved.name = saved.name.replace(/^Opt /, 'Otimizada ');
            try {
                const calculated = await fetch('/api/calculate', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ...saved.equipment, scenario: saved.scenario })
                });
                if (calculated.ok) saved.result = await calculated.json();
            } catch {}
            try {
                await fetch('/api/builds/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(saved)
                });
            } catch {}
            try { saveBuildLocal(saved); } catch { if (typeof uxMessage === 'function') uxMessage(SITE_LOCALE === 'en' ? 'Could not save locally.' : 'Não foi possível salvar localmente.'); return; }
            await loadSavedBuilds();
            setSaveStatus(SITE_LOCALE === 'en' ? 'Optimized build saved to the Comparator.' : 'Build otimizada salva no Comparador.', true);
            if (typeof uxMessage === 'function') uxMessage(SITE_LOCALE === 'en' ? 'Build saved in My builds.' : 'Build salva em Minhas builds.');
        }

        window.onload = async () => {
            if (typeof initializeExperience === 'function') initializeExperience();
            switchVisualTheme(VISUAL_THEME);
            try {
                const session = await fetch('/api/session', { credentials: 'same-origin' });
                if (!session.ok) throw new Error('Sessão local indisponível.');
            } catch (error) {
                setSaveStatus(error.message || 'Não foi possível iniciar a sessão local.', false);
            }
            if (typeof loadVisualAssets === 'function') await loadVisualAssets();
            await Promise.all([
                loadGameData(),
                loadSavedBuilds(),
                loadSavedDamage(),
                loadTalismanInventory(),
                loadDataVersion()
            ]);
            if (typeof startWorkspace === 'function') await startWorkspace();
        };

        document.addEventListener('keydown', event => {
            if ((event.key !== 'Enter' && event.key !== ' ') || !event.target.classList.contains('nav-item')) return;
            event.preventDefault();
            event.target.click();
        });
