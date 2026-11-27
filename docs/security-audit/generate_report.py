from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.doughnut import Doughnut
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


PROJECT_NAME = "MH Wilds Builder"
REPORT_TITLE = f"Relatório de Auditoria de Segurança — {PROJECT_NAME}"
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
OUTPUT_PATH = HERE / "relatorio-auditoria-seguranca.pdf"

CRITICAL = HexColor("#B91C1C")
HIGH = HexColor("#EA580C")
MEDIUM = HexColor("#D97706")
LOW = HexColor("#2563EB")
STRONG = HexColor("#059669")
INK = HexColor("#172033")
MUTED = HexColor("#596579")
LINE = HexColor("#D9DEE7")
SURFACE = HexColor("#F5F7FA")
PALE_RED = HexColor("#FFF2EE")
PALE_GREEN = HexColor("#ECFDF5")
WHITE = colors.white

SEVERITY_COLORS = {
    "Crítica": CRITICAL,
    "Alta": HIGH,
    "Média": MEDIUM,
    "Baixa": LOW,
    "Informativa": MUTED,
}


@dataclass(frozen=True)
class Finding:
    finding_id: str
    category: str
    severity: str
    title: str
    location: str
    description: str
    exploitability: str
    impact: str
    evidence: str


FINDINGS = [
    Finding(
        "F-01",
        "1. Banco sem tranca / isolamento",
        "Alta",
        "Persistência global sem autenticação ou isolamento de dono",
        "app/main.py:33-39, 41-51, 126-176, 749-815; app/models.py:477-497",
        (
            "Builds, talismãs e resultados de dano são carregados em dicionários globais e gravados "
            "em três arquivos JSON. Os modelos persistidos não contêm user_id, organization_id, "
            "workspace_id ou tenant_id. Todas as rotas retornam ou alteram o conjunto global."
        ),
        (
            "Verificado dinamicamente: uma requisição com Origin https://attacker.example recebeu "
            "Access-Control-Allow-Origin para essa origem; o preflight de POST/DELETE também foi "
            "aceito. Assim, enquanto o serviço estiver em execução, uma página de outra origem pode "
            "ler e alterar os dados. Políticas de Private Network Access do navegador podem exigir "
            "uma permissão adicional em alguns ambientes, mas não restauram autenticação ou posse."
        ),
        "Divulgação, sobrescrita e exclusão de todos os dados salvos pelo processo, sem distinção de usuário.",
        """033 app.add_middleware(
034     CORSMiddleware,
035     allow_origins=["*"],
036     allow_credentials=True,
037     allow_methods=["*"],
038     allow_headers=["*"],
039 )
049 SAVED_BUILDS_STORAGE: dict[str, SavedBuild] = {}
050 SAVED_DAMAGE_STORAGE: dict[str, SavedDamage] = {}
051 TALISMAN_INVENTORY_STORAGE: dict[str, InventoryTalisman] = {}
477 class SavedBuild(BaseModel):
478     id: str
479     name: str
481     equipment: BuildEquipment
482     scenario: ScenarioSettings
483     result: BuildResult""",
    ),
    Finding(
        "F-02",
        "3. IDOR",
        "Alta",
        "IDOR e sobrescrita por ID em builds salvas",
        "app/main.py:749-769",
        (
            "GET lista todas as builds; POST usa build.id fornecido pelo cliente como chave e "
            "sobrescreve uma entrada existente; DELETE remove qualquer entrada cujo ID seja conhecido. "
            "Nenhum handler recebe principal autenticado ou valida a posse do objeto."
        ),
        (
            "Qualquer cliente que alcance a API pode obter os IDs por GET /api/builds e, em seguida, "
            "sobrescrever por POST /api/builds/save ou excluir por DELETE /api/builds/{build_id}."
        ),
        "Leitura, adulteração e perda de builds de outros usuários do mesmo processo.",
        """749 @app.get("/api/builds", response_model=list[SavedBuild])
750 def list_saved_builds():
751     return list(SAVED_BUILDS_STORAGE.values())
754 @app.post("/api/builds/save", response_model=SavedBuild)
755 def save_build_endpoint(build: SavedBuild):
758     SAVED_BUILDS_STORAGE[build.id] = build
763 @app.delete("/api/builds/{build_id}")
764 def delete_build_endpoint(build_id: str):
765     if build_id in SAVED_BUILDS_STORAGE:
766         del SAVED_BUILDS_STORAGE[build_id]""",
    ),
    Finding(
        "F-03",
        "3. IDOR",
        "Alta",
        "IDOR e sobrescrita por ID no inventário de talismãs",
        "app/main.py:773-791",
        (
            "O inventário inteiro é público para o processo. O POST confia em item.id e o DELETE "
            "confia no talisman_id do caminho, sem vincular o registro a um dono."
        ),
        (
            "GET /api/talismans/inventory revela todos os IDs. O mesmo chamador pode reutilizar um ID "
            "no POST para sobrescrever ou no DELETE para remover o talismã."
        ),
        "Exposição e manipulação do inventário de talismãs salvo.",
        """773 @app.get("/api/talismans/inventory", response_model=list[InventoryTalisman])
774 def list_talisman_inventory():
775     return list(TALISMAN_INVENTORY_STORAGE.values())
778 @app.post("/api/talismans/inventory", response_model=InventoryTalisman)
779 def save_talisman_inventory(item: InventoryTalisman):
780     TALISMAN_INVENTORY_STORAGE[item.id] = item
785 @app.delete("/api/talismans/inventory/{talisman_id}")
786 def delete_talisman_inventory(talisman_id: str):
787     if talisman_id in TALISMAN_INVENTORY_STORAGE:
788         del TALISMAN_INVENTORY_STORAGE[talisman_id]""",
    ),
    Finding(
        "F-04",
        "3. IDOR",
        "Alta",
        "IDOR e sobrescrita por ID em resultados de dano",
        "app/main.py:795-815",
        (
            "Resultados são listados globalmente, indexados pelo ID enviado pelo cliente e excluídos "
            "somente pela existência desse ID, sem autenticação ou predicado de posse."
        ),
        (
            "GET /api/damage fornece os IDs necessários para substituir um resultado via POST "
            "/api/damage/save ou removê-lo via DELETE /api/damage/{damage_id}."
        ),
        "Exposição, falsificação e exclusão de resultados salvos.",
        """795 @app.get("/api/damage", response_model=list[SavedDamage])
796 def list_saved_damage():
797     return list(SAVED_DAMAGE_STORAGE.values())
800 @app.post("/api/damage/save", response_model=SavedDamage)
801 def save_damage_endpoint(damage: SavedDamage):
804     SAVED_DAMAGE_STORAGE[damage.id] = damage
809 @app.delete("/api/damage/{damage_id}")
810 def delete_damage_endpoint(damage_id: str):
811     if damage_id in SAVED_DAMAGE_STORAGE:
812         del SAVED_DAMAGE_STORAGE[damage_id]""",
    ),
    Finding(
        "F-05",
        "5. Inputs sem tratamento / XSS",
        "Alta",
        "XSS armazenado por nomes e IDs de builds",
        "static/index.html:3384-3397, 3476-3489, 3492-3536, 4861-4867; app/main.py:754-760",
        (
            "Nomes de builds e IDs vindos da API entram em innerHTML e em atributos onclick sem "
            "escape. loadSavedBuilds é executado no window.onload e renderiza automaticamente os "
            "registros persistidos. O backend aceita strings arbitrárias nesses campos."
        ),
        (
            "Um cliente grava uma build válida com name contendo HTML executável, por exemplo uma tag "
            "img com onerror. Na próxima abertura do aplicativo, o registro é buscado e inserido no DOM. "
            "A CORS permissiva de F-01 permite plantar o payload a partir de outra origem."
        ),
        "Execução de JavaScript no contexto do aplicativo e acesso aos dados/localStorage disponíveis à página.",
        """3384 async function loadSavedBuilds() {
3387     const res = await fetch('/api/builds');
3394     SAVED_BUILDS = Array.from(merged.values()).slice(-30);
3395     renderComparatorTable();
3484 box.innerHTML = [
3485     ['Ranking geral', bestScore.name, bestScore.result.combined_score],
3489 ].map(([title, name, value]) => `...${name}...`).join('');
3517 tbody.innerHTML += `
3519     <td><strong>${b.name}</strong>...</td>
3530     <button ... onclick="loadBuildIntoBuilder('${b.id}')">...`;
4861 window.onload = () => {
4864     loadSavedBuilds();""",
    ),
    Finding(
        "F-06",
        "5. Inputs sem tratamento / XSS",
        "Alta",
        "XSS armazenado em resultados de dano",
        "static/index.html:3400-3428, 4861-4867; app/main.py:800-806",
        (
            "d.name, d.build_name e d.id são concatenados em innerHTML; d.id também é injetado em "
            "onclick. loadSavedDamage é chamado automaticamente ao carregar a página."
        ),
        (
            "Um SavedDamage com name ou id malicioso pode ser persistido pela API. Ao abrir o site, "
            "renderSavedDamage insere a string sem escape e dispara o payload."
        ),
        "Execução persistente de script no navegador do usuário que abrir a aplicação.",
        """3400 async function loadSavedDamage() {
3403     const res = await fetch('/api/damage');
3411     renderSavedDamage();
3422 box.innerHTML = SAVED_DAMAGE.slice().reverse().map(d => `
3424     <strong>${d.name || d.build_name || d.id}</strong><br>
3426     <button ... onclick="deleteSavedDamage('${d.id}')">...`;
4865     loadSavedDamage();""",
    ),
    Finding(
        "F-07",
        "5. Inputs sem tratamento / XSS",
        "Alta",
        "XSS armazenado no inventário de talismãs",
        "static/index.html:3808-3830, 3847-3850, 4861-4867; app/main.py:778-782",
        (
            "Nome, habilidades, rótulos derivados dos slots e ID do talismã são montados em innerHTML "
            "sem escape; IDs também entram em onclick. A lista é carregada automaticamente."
        ),
        (
            "O modelo Pydantic aceita, sem transformação, um nome como <img src=x onerror=...>. Depois "
            "do POST, qualquer abertura da aplicação busca o item e o renderiza como HTML."
        ),
        "Execução persistente de JavaScript e adulteração da interface de inventário.",
        """3813 const sorted = [...TALISMAN_INVENTORY].sort(...);
3814 box.innerHTML = sorted.map(item => {
3825     <strong>${t.name || t.id || 'Talismã'}</strong><br>
3826     <span ...>${[t.skill_1, t.skill_2, t.skill_3]...}</span>
3827     <button ... onclick="equipInventoryTalisman('${item.id}')">...
3847 async function loadTalismanInventory() {
3848     const res = await fetch('/api/talismans/inventory');
3850     renderTalismanInventory();""",
    ),
    Finding(
        "F-08",
        "5. Inputs sem tratamento / XSS",
        "Média",
        "DOM XSS na geração do cartão da build",
        "static/index.html:3161-3175",
        (
            "O nome digitado da build, o nome do monstro, o resumo dos equipamentos e as habilidades "
            "são interpolados diretamente em box.innerHTML. Não existe sanitizador no projeto."
        ),
        (
            "Exige que a vítima tenha conteúdo malicioso nos campos atuais, por digitação/colagem ou "
            "por carregar um item controlado, e então acione a geração do cartão. A interação adicional "
            "reduz a severidade em relação aos três fluxos armazenados automáticos."
        ),
        "Execução de JavaScript no contexto da página após a ação de gerar o cartão.",
        """3161 async function generateBuildCard() {
3168     box.innerHTML = `
3169         <div ...><strong>${document.getElementById('build-name-input').value || 'Build Atual'}</strong>
3170         <div ...>${selectedEquipmentSummary().map(([label, value, icon]) => `<div ...>${value}...</div>`).join('')}</div>
3172         <div ...>${topSkills}</div>
3173     `;
3174     panel.style.display = 'block';""",
    ),
]


ROUTES = [
    ("GET", "/", "Público; entrega o frontend, sem objeto de dono."),
    ("GET", "/api/data/all", "Público; catálogo estático, locale validado."),
    ("GET", "/api/meta-presets", "Público; catálogo estático."),
    ("GET", "/api/meta-builds/{preset_id}", "Público; preset estático, sem dado do usuário."),
    ("GET", "/api/meta-builds/{preset_id}/candidates", "Público; candidatos estáticos."),
    ("POST", "/api/rotations/compare", "Cálculo sem persistência; corpo validado por Pydantic."),
    ("GET", "/api/skill-icon/{icon_index}", "Público; índice limitado de 0 a 13 e caminho fixo."),
    ("GET", "/api/equipment-image/armor", "Público; resolução de imagem do catálogo."),
    ("GET", "/api/equipment-image/weapon", "Público; resolução de imagem do catálogo."),
    ("GET", "/api/equipment-image/skill", "Público; resolução de imagem do catálogo."),
    ("GET", "/api/image-proxy", "Público; HTTPS e allowlist exata de hosts."),
    ("GET", "/api/equipment-photo/weapon", "Público; fotografia do catálogo."),
    ("GET", "/api/equipment-photo/armor", "Público; fotografia do catálogo."),
    ("GET", "/api/equipment-photo/skill", "Público; fotografia do catálogo."),
    ("POST", "/api/calculate", "Cálculo sem persistência; corpo validado por Pydantic."),
    ("POST", "/api/optimizer", "Cálculo sem persistência; limites de busca validados."),
    ("POST", "/api/gog-recommendation", "Cálculo sem persistência; corpo validado por Pydantic."),
    ("GET", "/api/builds", "FALHA F-01/F-02: lista global sem principal ou posse."),
    ("POST", "/api/builds/save", "FALHA F-01/F-02/F-05: escrita global e ID do cliente."),
    ("DELETE", "/api/builds/{build_id}", "FALHA F-01/F-02: exclusão só por ID."),
    ("GET", "/api/talismans/inventory", "FALHA F-01/F-03: lista global."),
    ("POST", "/api/talismans/inventory", "FALHA F-01/F-03/F-07: escrita global e ID do cliente."),
    ("DELETE", "/api/talismans/inventory/{talisman_id}", "FALHA F-01/F-03: exclusão só por ID."),
    ("GET", "/api/damage", "FALHA F-01/F-04: lista global."),
    ("POST", "/api/damage/save", "FALHA F-01/F-04/F-06: escrita global e ID do cliente."),
    ("DELETE", "/api/damage/{damage_id}", "FALHA F-01/F-04: exclusão só por ID."),
]


ISSUES = [
    """--- ISSUE 1 ---
Título: [Segurança] Implementar autenticação e isolamento dos dados persistidos
Labels sugeridas: security, severidade-alta

Descrição
Builds, talismãs e resultados de dano são mantidos em coleções globais e os modelos não possuem campo de dono ou tenant. As rotas GET retornam todos os registros e as rotas de escrita não recebem um principal autenticado. Além disso, a política CORS aceita qualquer origem, método e cabeçalho.

Por que é explorável
Com o serviço em execução, qualquer cliente que alcance a API consegue ler e modificar o conjunto global. O teste com Origin https://attacker.example confirmou Access-Control-Allow-Origin para a origem arbitrária e um preflight bem-sucedido para POST/DELETE. Uma página maliciosa pode atingir uma API local em navegadores/ambientes que permitam a requisição; se o serviço for exposto na rede, o ataque é direto.

Evidência
app/main.py:33-39
```
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

app/main.py:49-51
```
SAVED_BUILDS_STORAGE: dict[str, SavedBuild] = {}
SAVED_DAMAGE_STORAGE: dict[str, SavedDamage] = {}
TALISMAN_INVENTORY_STORAGE: dict[str, InventoryTalisman] = {}
```

app/models.py:477-497
```
class SavedBuild(BaseModel):
    id: str
    name: str
    equipment: BuildEquipment
    scenario: ScenarioSettings
    result: BuildResult
```

Impacto
Divulgação, adulteração e exclusão integral dos dados salvos; também facilita o plantio remoto dos payloads XSS descritos em outras issues.

Sugestão de correção
Definir primeiro o modo de implantação. Para modo multiusuário, adicionar autenticação obrigatória, owner_id/tenant_id derivado somente do principal do servidor e persistência com consulta sempre escopada. Para modo local de usuário único, exigir token aleatório por instalação, vincular estritamente a origem permitida e negar startup/configuração insegura. Substituir allow_origins=["*"] por uma allowlist explícita.

Critérios de aceite
- [ ] Todas as rotas persistentes exigem um principal autenticado.
- [ ] owner_id/tenant_id é atribuído pelo servidor e não pode ser escolhido no corpo.
- [ ] Listagens retornam somente registros do principal/tenant atual.
- [ ] CORS aceita somente as origens configuradas e necessárias.
- [ ] O startup falha quando uma configuração de autenticação/CORS insegura é usada fora do modo de desenvolvimento.
- [ ] Testes provam que dois usuários/tenants não leem nem alteram dados entre si.
--- FIM ISSUE 1 ---""",
    """--- ISSUE 2 ---
Título: [Segurança] Eliminar IDOR nas rotas de builds, talismãs e danos
Labels sugeridas: security, severidade-alta

Descrição
Os nove handlers de estado listam, sobrescrevem e excluem objetos por IDs fornecidos pelo cliente sem verificar a posse. O GET revela os IDs e o POST faz upsert direto no dicionário global.

Por que é explorável
Um chamador obtém o ID pela rota de listagem e o reutiliza no POST ou DELETE. Não há predicado owner_id/tenant_id nem dependência FastAPI de autorização.

Evidência
app/main.py:749-769, 773-791, 795-815
```
return list(SAVED_BUILDS_STORAGE.values())
SAVED_BUILDS_STORAGE[build.id] = build
del SAVED_BUILDS_STORAGE[build_id]

return list(TALISMAN_INVENTORY_STORAGE.values())
TALISMAN_INVENTORY_STORAGE[item.id] = item
del TALISMAN_INVENTORY_STORAGE[talisman_id]

return list(SAVED_DAMAGE_STORAGE.values())
SAVED_DAMAGE_STORAGE[damage.id] = damage
del SAVED_DAMAGE_STORAGE[damage_id]
```

Impacto
Leitura, sobrescrita e exclusão de objetos de outro usuário/tenant.

Sugestão de correção
Gerar IDs no servidor e executar cada leitura/escrita com chave composta (owner_id, object_id) ou predicado equivalente. Em DELETE/UPDATE, retornar 404 quando o objeto não existir dentro do escopo do chamador. Evitar fluxo "buscar globalmente e depois autorizar".

Critérios de aceite
- [ ] IDs de novos registros são gerados pelo servidor.
- [ ] GET de coleção aplica filtro por dono/tenant.
- [ ] GET/POST/PUT/DELETE por ID inclui dono/tenant na mesma operação de persistência.
- [ ] Um ID válido de outro usuário resulta em 404 e não revela existência.
- [ ] Há testes negativos para as nove operações de builds, talismãs e danos.
--- FIM ISSUE 2 ---""",
    """--- ISSUE 3 ---
Título: [Segurança] Corrigir XSS armazenado em builds, resultados e talismãs
Labels sugeridas: security, severidade-alta

Descrição
Dados persistidos controláveis pelo cliente são interpolados em innerHTML e em handlers onclick. Os três conjuntos são carregados no window.onload, portanto o payload é executado sem ação específica da vítima depois que o registro é salvo.

Por que é explorável
Os modelos Pydantic validam os campos como str, mas não os tornam seguros para HTML. Um name contendo uma tag img com onerror é salvo e posteriormente interpretado pelo navegador. A política CORS atual permite que outra origem tente plantar o registro.

Evidência
static/index.html:3484-3489, 3517-3536
```
box.innerHTML = [... bestScore.name ...].map(... `${name}` ...).join('');
tbody.innerHTML += `<td><strong>${b.name}</strong>...</td>`;
```

static/index.html:3422-3428
```
box.innerHTML = SAVED_DAMAGE.map(d => `
    <strong>${d.name || d.build_name || d.id}</strong>
    <button onclick="deleteSavedDamage('${d.id}')">...</button>`).join('');
```

static/index.html:3813-3830
```
box.innerHTML = sorted.map(item => `
    <strong>${item.talisman.name}</strong>
    <button onclick="removeInventoryTalisman('${item.id}')">...</button>`).join('');
```

Impacto
Execução persistente de JavaScript, leitura/modificação do localStorage e ações em nome do usuário dentro da aplicação.

Sugestão de correção
Construir conteúdo dinâmico com createElement e textContent. Registrar eventos com addEventListener e data attributes, eliminando strings onclick. Onde HTML rico for realmente necessário, aplicar um sanitizador consolidado com allowlist restrita. Adicionar Content-Security-Policy sem unsafe-inline após remover handlers inline.

Critérios de aceite
- [ ] Nenhum campo de builds, danos ou talismãs chega a innerHTML sem sanitização contextual.
- [ ] IDs não são interpolados em atributos/JavaScript inline.
- [ ] Handlers inline são substituídos por addEventListener.
- [ ] Payloads de teste com tags, atributos onerror e aspas são exibidos como texto.
- [ ] Uma CSP restritiva é enviada e testada sem unsafe-inline.
- [ ] Há testes de regressão para os três fluxos carregados no window.onload.
--- FIM ISSUE 3 ---""",
    """--- ISSUE 4 ---
Título: [Segurança] Remover DOM XSS da geração do cartão de build
Labels sugeridas: security, severidade-média

Descrição
generateBuildCard interpola o nome digitado, nomes de equipamento/monstro e habilidades diretamente em box.innerHTML.

Por que é explorável
Se um desses valores contiver marcação executável e o usuário clicar para gerar o cartão, o navegador interpreta a marcação. A interação adicional é necessária, mas não há sanitizador nem codificação contextual nesse ponto.

Evidência
static/index.html:3161-3175
```
box.innerHTML = `
    <strong>${document.getElementById('build-name-input').value || 'Build Atual'}</strong>
    ${selectedEquipmentSummary().map(([label, value, icon]) => `<div>${value}</div>`).join('')}
    ${topSkills}
`;
```

Impacto
Execução de JavaScript no contexto da aplicação após a ação de gerar o cartão.

Sugestão de correção
Criar a estrutura do cartão com nós DOM e preencher todo conteúdo textual com textContent. Se os ícones precisarem de HTML controlado, selecionar o ícone a partir de uma tabela interna de valores permitidos, sem aceitar marcação arbitrária.

Critérios de aceite
- [ ] Nome da build, equipamento, monstro e habilidades são inseridos com textContent.
- [ ] Ícones vêm de uma allowlist interna e não de HTML controlável.
- [ ] Testes com <img onerror>, <svg onload> e quebra de atributo não executam código.
- [ ] A geração do cartão mantém o layout e os dados esperados.
--- FIM ISSUE 4 ---""",
]


def build_styles():
    sample = getSampleStyleSheet()
    styles = {}
    styles["Body"] = ParagraphStyle(
        "Body",
        parent=sample["BodyText"],
        fontName="Helvetica",
        fontSize=9.1,
        leading=13,
        textColor=INK,
        spaceAfter=5,
    )
    styles["Small"] = ParagraphStyle(
        "Small",
        parent=styles["Body"],
        fontSize=7.7,
        leading=10.2,
        textColor=MUTED,
    )
    styles["Title"] = ParagraphStyle(
        "Title",
        parent=sample["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=31,
        textColor=INK,
        alignment=TA_LEFT,
        spaceAfter=14,
    )
    styles["Subtitle"] = ParagraphStyle(
        "Subtitle",
        parent=styles["Body"],
        fontSize=11.5,
        leading=16,
        textColor=MUTED,
    )
    styles["H1"] = ParagraphStyle(
        "H1",
        parent=sample["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=INK,
        spaceBefore=4,
        spaceAfter=9,
    )
    styles["H2"] = ParagraphStyle(
        "H2",
        parent=sample["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=INK,
        spaceBefore=8,
        spaceAfter=5,
    )
    styles["H3"] = ParagraphStyle(
        "H3",
        parent=sample["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.2,
        leading=13,
        textColor=INK,
        spaceBefore=4,
        spaceAfter=4,
    )
    styles["Callout"] = ParagraphStyle(
        "Callout",
        parent=styles["Body"],
        fontSize=9.2,
        leading=13,
        leftIndent=3,
        rightIndent=3,
    )
    styles["Code"] = ParagraphStyle(
        "Code",
        parent=sample["Code"],
        fontName="Courier",
        fontSize=7.0,
        leading=9.0,
        textColor=HexColor("#263246"),
        wordWrap="CJK",
        splitLongWords=True,
        leftIndent=5,
        rightIndent=5,
        spaceBefore=4,
        spaceAfter=7,
    )
    styles["Issue"] = ParagraphStyle(
        "Issue",
        parent=styles["Code"],
        fontSize=7.1,
        leading=9.2,
        leftIndent=6,
        rightIndent=6,
        borderWidth=0.5,
        borderColor=LINE,
        borderPadding=7,
        backColor=SURFACE,
        wordWrap="CJK",
        splitLongWords=True,
    )
    styles["Table"] = ParagraphStyle(
        "Table",
        parent=styles["Small"],
        fontSize=7.2,
        leading=9.4,
        textColor=INK,
    )
    styles["TableHead"] = ParagraphStyle(
        "TableHead",
        parent=styles["Table"],
        fontName="Helvetica-Bold",
        textColor=WHITE,
    )
    styles["Chip"] = ParagraphStyle(
        "Chip",
        parent=styles["Table"],
        fontName="Helvetica-Bold",
        textColor=WHITE,
        alignment=TA_CENTER,
    )
    return styles


STYLES = build_styles()


def p(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(text, STYLES[style])


def literal_block(text: str, style: str) -> Paragraph:
    lines = []
    for raw_line in text.splitlines():
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        content = ("&nbsp;" * indent) + escape(raw_line.lstrip(" "))
        lines.append(content or "&nbsp;")
    return Paragraph("<br/>".join(lines), STYLES[style])


def bullet(text: str, color: str = "#172033") -> Paragraph:
    return Paragraph(
        f'<font color="{color}">●</font>&nbsp;&nbsp;{text}',
        STYLES["Body"],
    )


def section_header(number: str, title: str) -> list[Flowable]:
    return [p(f'<font color="#059669">{number}</font> {title}', "H1")]


def callout(text: str, background: colors.Color, border: colors.Color) -> Table:
    table = Table([[p(text, "Callout")]], colWidths=[170 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.8, border),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


class Rule(Flowable):
    def __init__(self, width: float, color: colors.Color = LINE, thickness: float = 0.7):
        super().__init__()
        self.width = width
        self.height = thickness + 2
        self.color = color
        self.thickness = thickness

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 1, self.width, 1)


def severity_summary() -> Drawing:
    drawing = Drawing(232, 162)
    chart = Doughnut()
    chart.x = 13
    chart.y = 30
    chart.width = 105
    chart.height = 105
    chart.data = [7, 1]
    chart.labels = ["", ""]
    chart.slices.strokeWidth = 0
    chart.slices[0].fillColor = HIGH
    chart.slices[1].fillColor = MEDIUM
    chart.innerRadiusFraction = 0.63
    drawing.add(chart)
    drawing.add(String(65, 88, "8", fontName="Helvetica-Bold", fontSize=21, fillColor=INK, textAnchor="middle"))
    drawing.add(String(65, 72, "achados", fontName="Helvetica", fontSize=8, fillColor=MUTED, textAnchor="middle"))
    legend = [(HIGH, "Alta", "7"), (MEDIUM, "Média", "1"), (CRITICAL, "Crítica", "0"), (LOW, "Baixa", "0")]
    y = 119
    for color, label, count in legend:
        drawing.add(Rect(137, y - 7, 9, 9, rx=2, ry=2, fillColor=color, strokeColor=None))
        drawing.add(String(152, y - 5, label, fontName="Helvetica", fontSize=8, fillColor=INK))
        drawing.add(String(215, y - 5, count, fontName="Helvetica-Bold", fontSize=8, fillColor=INK, textAnchor="end"))
        y -= 23
    drawing.add(String(10, 148, "Achados por severidade", fontName="Helvetica-Bold", fontSize=9, fillColor=INK))
    return drawing


def category_summary() -> Drawing:
    drawing = Drawing(232, 162)
    chart = VerticalBarChart()
    chart.x = 35
    chart.y = 42
    chart.height = 88
    chart.width = 180
    chart.data = [[1, 0, 3, 0, 4]]
    chart.bars[0].fillColor = STRONG
    chart.bars[0].strokeColor = None
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 4.5
    chart.valueAxis.valueStep = 1
    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 6.5
    chart.valueAxis.strokeColor = LINE
    chart.valueAxis.gridStrokeColor = HexColor("#E8ECF2")
    chart.valueAxis.visibleGrid = True
    chart.categoryAxis.categoryNames = ["Isolam.", "Perm. UI", "IDOR", "Segredos", "XSS"]
    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 6.2
    chart.categoryAxis.labels.angle = 22
    chart.categoryAxis.labels.dy = -9
    chart.categoryAxis.strokeColor = LINE
    drawing.add(chart)
    drawing.add(String(10, 148, "Achados por categoria", fontName="Helvetica-Bold", fontSize=9, fillColor=INK))
    drawing.add(String(10, 14, "Categorias sem achado continuam documentadas na cobertura.", fontName="Helvetica", fontSize=6.6, fillColor=MUTED))
    return drawing


def finding_table() -> Table:
    data = [[p("Severidade", "TableHead"), p("Arquivo:linha", "TableHead"), p("Descrição", "TableHead")]]
    for finding in FINDINGS:
        severity = p(finding.severity, "Chip")
        location = p(escape(finding.location), "Table")
        description = p(f"<b>{finding.finding_id} — {escape(finding.title)}</b><br/>{escape(finding.description)}", "Table")
        data.append([severity, location, description])
    table = Table(data, colWidths=[22 * mm, 52 * mm, 96 * mm], repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    for row, finding in enumerate(FINDINGS, start=1):
        style.append(("BACKGROUND", (0, row), (0, row), SEVERITY_COLORS[finding.severity]))
        if row % 2 == 0:
            style.append(("BACKGROUND", (1, row), (-1, row), SURFACE))
    table.setStyle(TableStyle(style))
    return table


def route_table() -> Table:
    data = [[p("Método", "TableHead"), p("Rota", "TableHead"), p("Resultado da revisão", "TableHead")]]
    for method, route, result in ROUTES:
        data.append([p(method, "Table"), p(escape(route), "Table"), p(escape(result), "Table")])
    table = Table(data, colWidths=[17 * mm, 64 * mm, 89 * mm], repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for row, (_, _, result) in enumerate(ROUTES, start=1):
        if "FALHA" in result:
            style.append(("BACKGROUND", (0, row), (-1, row), PALE_RED))
        elif row % 2 == 0:
            style.append(("BACKGROUND", (0, row), (-1, row), SURFACE))
    table.setStyle(TableStyle(style))
    return table


def stat_cards() -> Table:
    cells = [
        ("26", "operações FastAPI revisadas", INK),
        ("8", "achados verificados", HIGH),
        ("0", "segredos no estado atual", STRONG),
        ("4", "issues consolidadas", MEDIUM),
    ]
    row = []
    for value, label, color in cells:
        content = Paragraph(
            f'<font name="Helvetica-Bold" size="18" color="{color.hexval()}">{value}</font><br/>'
            f'<font size="7.4" color="#596579">{label}</font>',
            ParagraphStyle("Stat", parent=STYLES["Body"], alignment=TA_CENTER, leading=12),
        )
        row.append(content)
    table = Table([row], colWidths=[42.5 * mm] * 4)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.6, LINE),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return table


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    if doc.page > 1:
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, height - 14 * mm, width - doc.rightMargin, height - 14 * mm)
        canvas.setFont("Helvetica", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(doc.leftMargin, height - 11 * mm, "Relatório de Auditoria de Segurança")
        canvas.drawRightString(width - doc.rightMargin, height - 11 * mm, PROJECT_NAME)
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 13 * mm, width - doc.rightMargin, 13 * mm)
    canvas.setFont("Helvetica", 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, 9 * mm, "Uso interno • revisão estática e validação dinâmica local")
    canvas.drawRightString(width - doc.rightMargin, 9 * mm, f"Página {doc.page}")
    canvas.restoreState()


def add_cover(story: list[Flowable], report_date: str):
    story.append(Spacer(1, 24 * mm))
    accent = Drawing(170 * mm, 14)
    accent.add(Rect(0, 0, 44 * mm, 5, fillColor=STRONG, strokeColor=None))
    accent.add(Rect(44 * mm, 0, 28 * mm, 5, fillColor=HIGH, strokeColor=None))
    accent.add(Rect(72 * mm, 0, 18 * mm, 5, fillColor=MEDIUM, strokeColor=None))
    story.append(accent)
    story.append(Spacer(1, 10 * mm))
    story.append(p("RELATÓRIO TÉCNICO", "Subtitle"))
    story.append(p(REPORT_TITLE, "Title"))
    story.append(p("Revisão de isolamento, autorização, IDOR, segredos e XSS", "Subtitle"))
    story.append(Spacer(1, 17 * mm))

    cover_data = [
        [p("Data", "Small"), p(report_date)],
        [p("Escopo", "Small"), p("Código-fonte Python/FastAPI, frontend estático, arquivos de dados, scripts utilitários, configurações presentes e superfície HTTP local.")],
        [p("Raiz auditada", "Small"), p(escape(str(PROJECT_ROOT)))],
        [p("Fora do escopo", "Small"), p("Infraestrutura externa não presente no diretório; histórico de commits indisponível porque a cópia auditada não contém .git.")],
    ]
    cover_table = Table(cover_data, colWidths=[31 * mm, 139 * mm])
    cover_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(cover_table)
    story.append(Spacer(1, 15 * mm))
    story.append(
        callout(
            "<b>Nota metodológica.</b> As cinco categorias foram adaptadas à stack real: o equivalente de RLS é o escopo de dono/tenant nas coleções JSON; gates de UI foram cruzados com dependências FastAPI; todos os handlers foram enumerados para IDOR; a árvore atual e artefatos presentes foram pesquisados por segredos; e os sinks DOM/HTML foram rastreados até suas fontes.",
            PALE_GREEN,
            STRONG,
        )
    )
    story.append(PageBreak())


def add_stack_and_method(story: list[Flowable]):
    story.extend(section_header("01", "Stack detectada e método"))
    stack_data = [
        [p("Camada", "TableHead"), p("Tecnologia detectada", "TableHead"), p("Mapeamento de segurança", "TableHead")],
        [p("Backend", "Table"), p("Python 3, FastAPI, Pydantic, Uvicorn", "Table"), p("Dependências FastAPI, handlers e modelos de entrada/saída", "Table")],
        [p("Persistência", "Table"), p("Arquivos JSON + dicts globais; sem ORM/query builder", "Table"), p("Escopo por owner/tenant teria de ser implementado na camada de serviço/persistência", "Table")],
        [p("Autenticação", "Table"), p("Nenhuma", "Table"), p("Nenhum principal, sessão, token, role ou middleware de tenant", "Table")],
        [p("Frontend", "Table"), p("HTML/CSS/JavaScript vanilla em static/index.html", "Table"), p("innerHTML, handlers inline, URLs, eval e sanitização", "Table")],
        [p("Deploy", "Table"), p("Sem Docker, CI, Helm ou Terraform na cópia", "Table"), p("Categoria de segredos limitada aos arquivos realmente presentes", "Table")],
        [p("Git", "Table"), p("Diretório .git ausente", "Table"), p("Histórico não verificável nesta cópia; não tratado como resultado limpo", "Table")],
    ]
    table = Table(stack_data, colWidths=[30 * mm, 61 * mm, 79 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("GRID", (0, 0), (-1, -1), 0.45, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("BACKGROUND", (0, 2), (-1, 2), SURFACE),
                ("BACKGROUND", (0, 4), (-1, 4), SURFACE),
                ("BACKGROUND", (0, 6), (-1, 6), SURFACE),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 4 * mm))
    story.append(p("Cobertura executada", "H2"))
    story.append(bullet("Enumeração programática de <b>26 operações</b> registradas no objeto FastAPI; nenhuma declarou dependências de autenticação e o OpenAPI não contém securitySchemes."))
    story.append(bullet("Rastreamento de todos os nove handlers de estado e dos fluxos GET → armazenamento → renderização no navegador."))
    story.append(bullet("Busca por chaves, tokens, senhas, chaves privadas, JWTs, credenciais padrão e expansão ${VAR:-default} nos arquivos não binários presentes."))
    story.append(bullet("Teste HTTP local de CORS com origem arbitrária e preflight de escrita; validação de que strings HTML permanecem inalteradas nos modelos Pydantic."))
    story.append(bullet("Busca por innerHTML, eval, new Function, renderizadores Markdown/HTML, URLs controláveis e sanitizadores; revisão dos sinks encontrados."))
    story.append(PageBreak())


def add_executive_summary(story: list[Flowable]):
    story.extend(section_header("02", "Resumo executivo"))
    story.append(stat_cards())
    story.append(Spacer(1, 5 * mm))
    charts = Table([[severity_summary(), category_summary()]], colWidths=[85 * mm, 85 * mm])
    charts.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(charts)
    story.append(Spacer(1, 3 * mm))
    story.append(
        callout(
            "<b>Risco central:</b> o aplicativo foi estruturado como ferramenta local de usuário único, mas oferece operações HTTP persistentes sem qualquer fronteira de confiança. A combinação de dados globais, CORS arbitrário e renderização com innerHTML transforma uma limitação arquitetural em leitura/escrita remota e XSS armazenado verificável.",
            PALE_RED,
            HIGH,
        )
    )
    story.append(Spacer(1, 5 * mm))
    story.append(p("Pontos fracos centrais", "H2"))
    story.append(bullet("Ausência total de principal autenticado e de campos de dono/tenant nos três modelos persistidos.", "#EA580C"))
    story.append(bullet("Nove operações de coleção/ID permitem listar, sobrescrever e excluir registros globais.", "#EA580C"))
    story.append(bullet("Três fluxos de XSS armazenado são renderizados automaticamente no carregamento; um quarto sink exige clique.", "#EA580C"))
    story.append(PageBreak())


def add_strengths(story: list[Flowable]):
    story.extend(section_header("03", "Pontos fortes e resultados corretos"))
    strengths = [
        ("Proxy de imagem com fronteira explícita", "app/main.py:640-668 valida scheme HTTPS, host em allowlist exata, Content-Type image/* e limita a quantidade de entradas do cache."),
        ("Caminho de ícone não controlável", "app/main.py:555-562 aceita somente icon_index inteiro entre 0 e 13 e monta um nome de arquivo fixo."),
        ("Validação numérica de cenários e otimização", "app/models.py:364-398 e 500-516 aplicam limites Pydantic para uptimes, duração, quantidades e tamanhos de busca."),
        ("Locale restrito", "app/main.py:433-437 limita locale por regex a en ou pt."),
        ("Escape reutilizável existente", "static/index.html:2023-2026 define escapeHtml e ele é aplicado corretamente em diversos fluxos da wiki e do otimizador; os achados são os sinks onde essa disciplina não foi mantida."),
        ("Sem execução dinâmica encontrada", "Não foram encontrados eval, new Function ou renderizador Markdown/HTML no frontend, nem templates de e-mail/HTML no backend."),
        ("Sem segredos no estado atual", "A busca na árvore presente não encontrou API keys, tokens, senhas, chaves privadas, JWTs ou defaults ${VAR:-valor}. O frontend também não contém credenciais embutidas."),
        ("Rotas públicas de catálogo/cálculo", "As 17 operações que não persistem objetos de usuário tratam catálogos estáticos, arquivos internos ou cálculos Pydantic; não foi forçada uma exigência de posse onde ela não se aplica."),
    ]
    for title, detail in strengths:
        box = Table([[p(f'<font color="#059669"><b>✓</b></font>&nbsp; <b>{title}</b><br/>{escape(detail)}')]], colWidths=[170 * mm])
        box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE_GREEN), ("BOX", (0, 0), (-1, -1), 0.45, HexColor("#A7E6CF")), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        story.append(box)
        story.append(Spacer(1, 2.5 * mm))
    story.append(p("Categorias sem achado específico", "H2"))
    story.append(p("<b>Permissão definida no navegador.</b> Não há isAdmin, canEdit, role, permission ou gate equivalente no frontend; também não há autenticação no backend. Portanto, não existe um gate de papel para cruzar e não foi criado um achado artificial de divergência frontend/backend. A falta de proteção das escritas está documentada em F-01 a F-04."))
    story.append(p("<b>Chaves expostas.</b> Nenhum segredo hardcoded foi encontrado nos arquivos presentes. Não há Docker/CI/Helm/Terraform para auditar. Como .git está ausente, o histórico não pôde ser examinado e permanece uma limitação, não uma confirmação de ausência histórica."))
    story.append(PageBreak())


def add_findings(story: list[Flowable]):
    story.extend(section_header("04", "Achados detalhados"))
    story.append(finding_table())
    story.append(PageBreak())
    for index, finding in enumerate(FINDINGS):
        color = SEVERITY_COLORS[finding.severity]
        chip = Table([[p(finding.severity.upper(), "Chip")]], colWidths=[24 * mm])
        chip.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), color), ("BOX", (0, 0), (-1, -1), 0.3, color), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        heading = Table([[chip, p(f"<b>{finding.finding_id}</b> &nbsp; {escape(finding.title)}", "H2")]], colWidths=[27 * mm, 143 * mm])
        heading.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        story.append(heading)
        story.append(p(f"<b>Categoria:</b> {escape(finding.category)}<br/><b>Arquivo:linha:</b> {escape(finding.location)}", "Small"))
        story.append(p(f"<b>Descrição.</b> {escape(finding.description)}"))
        story.append(p(f"<b>Por que é explorável.</b> {escape(finding.exploitability)}"))
        story.append(p(f"<b>Impacto.</b> {escape(finding.impact)}"))
        story.append(p("Evidência de código", "H3"))
        story.append(literal_block(finding.evidence, "Code"))
        if index != len(FINDINGS) - 1:
            story.append(Rule(170 * mm))
            story.append(Spacer(1, 4 * mm))
    story.append(PageBreak())


def add_route_coverage(story: list[Flowable]):
    story.extend(section_header("05", "Cobertura completa dos handlers"))
    story.append(p("A tabela abaixo registra todas as 26 operações da aplicação, não uma amostra. Rotas públicas sem objeto de usuário foram classificadas como não aplicáveis a IDOR; os nove handlers persistentes estão vinculados aos achados correspondentes."))
    story.append(route_table())
    story.append(PageBreak())


def add_recommendations(story: list[Flowable]):
    story.extend(section_header("06", "Recomendações priorizadas"))
    recommendations = [
        ("P1", HIGH, "Definir a fronteira de confiança", "Escolher formalmente entre modo local de usuário único e serviço multiusuário. Em ambos, exigir autenticação nas rotas persistentes; no modo local, usar token aleatório por instalação e origem estrita; no multiusuário, adotar owner_id/tenant_id derivado do principal."),
        ("P1", HIGH, "Eliminar IDOR na operação de persistência", "Gerar IDs no servidor e combinar owner_id/tenant_id com o ID em listagem, atualização e exclusão. O filtro deve fazer parte da mesma operação de leitura/escrita, retornando 404 para objetos fora do escopo."),
        ("P1", HIGH, "Remover XSS armazenado", "Substituir templates innerHTML por createElement/textContent, retirar onclick inline e usar addEventListener. Reservar sanitização allowlist para os raros pontos que realmente precisem aceitar HTML."),
        ("P1", HIGH, "Restringir CORS", "Trocar curingas por allowlist explícita de origem, métodos e cabeçalhos. Não confiar em bind localhost como controle de autorização."),
        ("P2", MEDIUM, "Adicionar testes de segurança", "Criar dois principals/tenants nos testes e provar isolamento em cada operação. Adicionar payloads XSS de regressão para builds, danos, talismãs e cartão da build, além de testes de CORS negativo."),
        ("P2", MEDIUM, "Aplicar Content-Security-Policy", "Depois de remover handlers inline, enviar CSP sem unsafe-inline e restringir script-src, img-src e connect-src aos recursos realmente usados."),
        ("P3", LOW, "Endurecer operação e dependências", "Fixar versões reproduzíveis, automatizar secret scanning/SCA quando o repositório Git estiver disponível e documentar variáveis obrigatórias com validação de startup."),
    ]
    for priority, color, title, detail in recommendations:
        priority_cell = Paragraph(f'<font color="white"><b>{priority}</b></font>', ParagraphStyle("Priority", parent=STYLES["Body"], alignment=TA_CENTER))
        table = Table([[priority_cell, p(f"<b>{escape(title)}</b><br/>{escape(detail)}")]], colWidths=[15 * mm, 155 * mm])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), color), ("BACKGROUND", (1, 0), (1, 0), SURFACE), ("BOX", (0, 0), (-1, -1), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
        story.append(table)
        story.append(Spacer(1, 3 * mm))
    story.append(PageBreak())


def add_issues(story: list[Flowable]):
    story.extend(section_header("07", "ISSUES PARA O GITHUB"))
    story.append(p("Os oito achados foram consolidados em quatro issues acionáveis para evitar tickets repetidos. Cada bloco abaixo está em Markdown e inclui evidência, impacto, correção e critérios de aceite."))
    story.append(Spacer(1, 3 * mm))
    for index, issue in enumerate(ISSUES):
        if index:
            story.append(PageBreak())
        for block in issue.split("\n\n"):
            story.append(literal_block(block, "Issue"))
            story.append(Spacer(1, 1.4 * mm))


def build_pdf(output_path: Path = OUTPUT_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_date = datetime.now().strftime("%d/%m/%Y")
    doc = BaseDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title=REPORT_TITLE,
        author="Codex",
        subject="Auditoria de segurança de aplicação FastAPI e frontend JavaScript",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="audit", frames=[frame], onPage=header_footer)])

    story: list[Flowable] = []
    add_cover(story, report_date)
    add_stack_and_method(story)
    add_executive_summary(story)
    add_strengths(story)
    add_findings(story)
    add_route_coverage(story)
    add_recommendations(story)
    add_issues(story)
    doc.build(story)
    return output_path


if __name__ == "__main__":
    generated = build_pdf()
    print(generated)
