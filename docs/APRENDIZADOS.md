# Diário de Aprendizado — Tech Market Intelligence

> Log incremental de decisões técnicas e conceitos aprendidos durante a construção do projeto.
> Serve de matéria-prima para o README final e para posts de LinkedIn.
> Organizado por **etapa**, seguindo a ordem de construção degrau a degrau definida no início do projeto.

---

## Guia rápido de sintaxe Python (consulta, cresce conforme aparece coisa nova)

| Símbolo / termo | O que é | Exemplo |
|---|---|---|
| `[]` | **Lista** — coleção ordenada, permite duplicatas, acessa por posição (`lista[0]`) | `[1, 2, 2, 3]` |
| `{}` com `chave: valor` | **Dicionário** — pares chave→valor, acessa por chave (`dic["ano"]`) | `{"2020": 61, "2021": 48}` |
| `{}` só com valores | **Set** — coleção sem ordem e **sem duplicatas**, usada pra comparar (união, interseção, diferença) | `{1, 2, 3}` |
| `()` | **Tupla** (parecida com lista, mas imutável) ou chamada de função | `pd.read_csv(...)` |
| `:` no fim de `for`/`if`/`def`/`while` | Abre um **bloco** — tudo indentado abaixo pertence a ele. Python usa indentação, não `{ }` | `for x in y:` |
| `f"texto {variavel}"` | **f-string** — insere valor de variável dentro de um texto | `f"data/raw/{ano}/schema.csv"` |
| `*lista` | **Unpacking** — "espalha" os itens de uma lista como argumentos separados | `func(*[1,2,3])` = `func(1,2,3)` |
| `.items()` | Percorre um dicionário pegando **chave e valor** ao mesmo tempo | `for k, v in dic.items():` |
| `{k: v for k, v in x}` | **Dict comprehension** — constrói um dicionário novo a partir de outro, numa linha só | — |
| `a & b` / `.intersection()` | **Interseção de sets** — só o que está em **todos** ao mesmo tempo (mais restritivo) | — |
| `a \| b` / `.union()` | **União de sets** — tudo que está em **qualquer um** deles (menos restritivo) | — |
| `a - b` | **Diferença de sets** — o que está em `a` mas não em `b` | — |
| `.str.contains("x")` | Filtro de texto em coluna do pandas — parecido com `LIKE '%x%'` do SQL | `df[df["col"].str.contains("x")]` |

---

# ETAPA 1 — Python Puro + PostgreSQL

> Degrau 1 do roadmap: ingestão dos surveys, profiling de schema, normalização, carga no Postgres. Sem dbt, sem Docker ainda.
> **Status:** em andamento. Concluído até aqui: ambiente, controle de versão, dados brutos, ambiente virtual Python. Pendente: profiling/schema evolution, script de ingestão, modelagem e carga no Postgres.

## 1.1 — 2026-08-20 — Setup do ambiente e estrutura de pastas

**Contexto:** primeiro contato com o projeto, degrau 1 ainda não começou o código.

**O que foi verificado:**
- Python 3.14.7 instalado corretamente (instalação real em `AppData\Local\Programs\Python`, não o stub da Microsoft Store).
- Docker já presente na máquina, mas **deliberadamente não usado ainda** — é ferramenta do degrau 5. Regra do projeto: uma tecnologia nova de cada vez.
- PostgreSQL ainda não instalado — correto para este ponto, só entra quando houver dado limpo pra carregar.

**Decisão de arquitetura — separação de camadas de dados:**
- `data/raw/` — ZIPs/CSVs originais dos surveys. **Nunca editado.** É a fonte da verdade; se uma transformação tiver bug, refaz-se a partir daqui.
- `data/staging/` — dados extraídos, ainda "crus" em significado, mas em formato utilizável.
- `src/ingestion/`, `src/transformation/`, `src/validation/`, `src/analytics/` — um módulo por responsabilidade (princípio de separação de responsabilidades). Evita virar um notebook monolítico de 400 células.
- Esse padrão (Raw → Staging → Intermediate → Gold, um pipeline de mão única) tem nome na indústria: **Medallion Architecture** (Bronze/Silver/Gold na nomenclatura da Databricks). Dado nunca flui de volta pra uma camada anterior — garante que um bug numa transformação nunca corrompe a fonte, e que cada camada tem um contrato claro do que promete entregar.
- A divisão de `sql/` em `staging/intermediate/marts` já imita a convenção de pastas do **dbt** (degrau 3) — o modelo mental já fica pronto antes mesmo de aprender a ferramenta.

**Conceito aprendido — Git não versiona pastas vazias:**
Git rastreia conteúdo (blobs), não estrutura de diretórios. Uma pasta sem nenhum arquivo dentro simplesmente não aparece em `git status` nem é commitada. Solução comum: colocar um arquivo `.gitkeep` (convenção, não é uma feature nativa do Git) dentro de pastas que ainda estão vazias, só para dar a elas um arquivo para rastrear.

**Por que não dá pra commitar uma pasta vazia (não é limitação artificial, é o modelo interno do Git):**
O Git só tem dois tipos de objeto relevantes aqui — `blob` (conteúdo de um arquivo) e `tree` (lista de entradas, cada uma apontando pra um blob ou outra tree). Uma entrada de tree sempre precisa apontar pra algo. Uma pasta vazia não tem nada pra apontar, então não existe objeto a ser criado — `git add` numa pasta vazia não tem o que registrar.

`.gitkeep` **não é uma feature do Git** — é convenção da comunidade: um arquivo qualquer, vazio, só para a pasta deixar de estar vazia e se tornar rastreável. O nome não tem significado especial para o Git.

**Comandos usados (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path data/raw, data/staging, src/ingestion, src/transformation, src/validation, src/analytics, sql/staging, sql/intermediate, sql/marts, tests

"data/raw", "data/staging", "src/ingestion", "src/transformation", "src/validation", "src/analytics", "sql/staging", "sql/intermediate", "sql/marts", "tests" | ForEach-Object { New-Item -ItemType File -Force -Path "$_/.gitkeep" }
```

---

## 1.2 — 2026-08-20 — Primeira surpresa real: a fonte de dados mudou de formato

**O plano original** (documento de contexto do projeto) previa baixar ZIPs contendo CSVs do site oficial `survey.stackoverflow.co`. **A realidade encontrada:** o Stack Overflow migrou a distribuição dos dados para um repositório GitHub (`StackExchange/Survey`), com um CSV puro por ano, hospedado via **Git LFS** (Large File Storage — mecanismo do Git para versionar arquivos grandes sem inchar o histórico do repositório).

**Por que isso é uma lição, não um contratempo:** planos de engenharia de dados quase sempre encontram uma realidade diferente do que foi documentado — fontes de dados mudam formato, local, protocolo de distribuição. Saber se adaptar (confirmar a nova fonte, validar que é confiável, ajustar o plano) é parte do trabalho, não uma exceção a ele. Isso inclusive já é a primeira instância de "evolução" que o projeto vai documentar — só que na camada de distribuição, antes mesmo de chegar nas colunas do CSV.

**Impacto prático:** como os dados já vêm em CSV puro (sem ZIP), a etapa de ingestão fica mais simples — não é necessário código de extração de ZIP, só leitura direta de CSV.

**Dois arquivos por ano, papéis diferentes:**
- `results.csv` — o dado de verdade, uma linha por resposta.
- `schema.csv` — o dicionário de dados: o que cada coluna do `results.csv` significa. Peça central para provar schema evolution entre anos.

**URLs diretas dos 6 anos usados no projeto (2020–2025):**
```
https://github.com/StackExchange/Survey/raw/refs/heads/main/packages/archive/{ano}/results.csv
https://github.com/StackExchange/Survey/raw/refs/heads/main/packages/archive/{ano}/schema.csv
```

**Convenção de armazenamento no raw:** `data/raw/{ano}/results.csv` e `data/raw/{ano}/schema.csv` — um subdiretório por ano, mantendo a fonte auditável e o layout previsível para o script de ingestão. Nomes de arquivo mantidos **idênticos ao original** (sem incluir o ano no nome) — a pasta já desambigua, e preservar o nome original da fonte é boa prática de rastreabilidade na camada raw.

---

## 1.3 — 2026-08-21 — Git: por que dado bruto não é versionado, `.gitignore`, e disciplina de commit

**Contexto:** ao baixar os 6 anos do survey, `results.csv` variou entre 80 MB e 160 MB por ano — 4 dos 6 arquivos já estouram o limite de 100 MB do GitHub por push.

**Por que dado bruto grande não deve ir pro Git:**
- GitHub recusa qualquer arquivo acima de 100 MB num push normal.
- Mesmo cabendo, seria errado: Git guarda o **histórico inteiro** de cada versão de cada arquivo, para sempre — commitar um CSV grande uma vez já infla o repositório permanentemente, mesmo se o arquivo for deletado depois (ele continua existindo no histórico).
- Prática de mercado: dado bruto grande fica de fora do Git; o que fica versionado é o **código que sabe buscar/reproduzir o dado**.

**`.gitignore`:** arquivo de texto na raiz do projeto com um padrão por linha, dizendo ao Git o que nunca rastrear. Decisão tomada: ignorar `results.csv` (grande, reproduzível a partir da fonte) mas **manter rastreado** `schema.csv` (pequeno, poucos KB, e é a evidência direta da evolução de schema — o diferencial técnico do projeto).

```gitignore
# Large raw survey files - reproducible from source, not tracked in Git.
# schema.csv (small, documents schema evolution) IS tracked on purpose.
data/raw/**/results.csv
venv/
```

**Conceito: caminho completo, não nome, identifica um arquivo.** É possível (e correto) ter `data/raw/2020/results.csv` e `data/raw/2025/results.csv` com o mesmo nome — a pasta já desambigua.

**Os três estados do Git (fluxo básico):**
```
diretório de trabalho  →  área de staging (index)  →  commit
     (git status olha aqui)   (git add move pra cá)      (git commit grava aqui)
```
`git status` é somente leitura — não precisa (nem faz sentido) rodar `git add` antes dele. É o check-point de segurança que se roda **antes de qualquer commit**, para confirmar exatamente o que vai virar histórico permanente. Um arquivo só aparece em `git status` quando tem diferença em relação ao último commit (novo, modificado ou removido) — o `.gitignore` não é especial nesse sentido, é um arquivo de texto versionado como qualquer outro.

**`git add .` / `git add -A` vs. listar caminhos explícitos:** ambos respeitam o `.gitignore`, então no dia a dia costumam dar no mesmo resultado. Mas `git add .` confia cegamente nas regras de ignore — se algo sensível (`.env`, credencial, arquivo grande) não estiver no `.gitignore` por esquecimento, ele entra silenciosamente no staging. Listar caminhos à mão força uma decisão consciente sobre o que está indo pro commit. Hábito recomendado em projeto novo, ainda calibrando o `.gitignore`.

**Taxonomia de Conventional Commits usada no projeto:**

| Prefixo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade — código que faz o sistema fazer algo novo |
| `fix` | Correção de bug |
| `chore` | Manutenção, configuração, tooling — nada que mude comportamento |
| `docs` | Só documentação |
| `refactor` | Reorganiza código existente, sem mudar comportamento |
| `test` | Só testes |

Commits de infraestrutura (`.gitignore`, `schema.csv`, `requirements.txt`) foram classificados como `chore`, não `feat`, porque nenhum entrega uma capacidade nova ao sistema — é configuração e dado bruto, não comportamento. `feat` fica reservado para quando o primeiro script de ingestão realmente fizer o sistema "ler CSV e carregar no banco" pela primeira vez.

**Decisão de idioma:** commits, código e README em inglês (convenção de mercado); `docs/APRENDIZADOS.md` em português (matéria-prima para conteúdo de LinkedIn).

---

## 1.4 — 2026-08-21 — Ambiente virtual Python (`venv`) e gerenciamento de dependências

**O conceito, antes da ferramenta:** instalar bibliotecas com `pip install` por padrão afeta o Python **global** da máquina. Isso quebra quando dois projetos precisam de versões diferentes da mesma biblioteca. Um **ambiente virtual** é uma cópia isolada do Python — interpretador + pacotes próprios — restrita a um projeto, sem interferir no resto da máquina.

**`venv` vs `Conda`:** `venv` vem embutido na biblioteca padrão do Python (não precisa instalar nada) e gerencia só pacotes Python via `pip` — suficiente para esse projeto (pandas, driver de Postgres, pytest, nada de binário exótico tipo CUDA). `Conda` é mais pesado, usado em ciência de dados/ML quando há dependências não-Python complexas. Times de **engenharia de dados/backend** normalmente usam `venv`/`pip` (ou `poetry`); `Conda` é mais associado a notebook de ML — escolher `venv` sinaliza o perfil profissional certo pro portfólio.

**Criar o ambiente:**
```powershell
python -m venv venv
```
Sintaxe: `-m venv` roda o **módulo** `venv` da biblioteca padrão; o segundo `venv` é só um **argumento** — o nome da pasta a criar. É coincidência de convenção, não obrigação de sintaxe (poderia ser `python -m venv qualquer_nome`).

**Ativar o ambiente — um script por tipo de shell**, porque "ativar" significa mexer em variáveis de ambiente (como o `PATH`), e cada shell tem sua própria sintaxe:

| Arquivo | Shell |
|---|---|
| `Activate.ps1` | PowerShell (prompt `PS ...>`) |
| `activate.bat` | Prompt de Comando clássico (`cmd.exe`) |
| `activate` | Bash/Zsh (Linux, Mac, Git Bash) |
| `activate.fish` | Fish shell |

```powershell
.\venv\Scripts\Activate.ps1
```
Sinal de sucesso: o prompt ganha o prefixo `(venv)`.

**Obstáculo real encontrado — Execution Policy do PowerShell:** por padrão, o PowerShell bloqueia a execução de qualquer script `.ps1`, inclusive inofensivos, como proteção contra scripts maliciosos baixados da internet. Solução:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
- `-Scope CurrentUser`: afeta a conta de usuário do Windows inteira (todos os projetos, não só esse), não precisa de admin. Não existe (nem faria sentido existir) uma execution policy "por projeto" — é configuração de sistema operacional, feita uma única vez na vida do desenvolvedor.
- `RemoteSigned`: scripts locais (criados na própria máquina, como o do `venv`) rodam livremente; scripts baixados da internet continuam bloqueados sem assinatura digital. Segurança preservada, não desligada.

**Importante: o venv não isola o terminal inteiro, só as ferramentas Python.** `git` e outros programas continuam funcionando normalmente com `(venv)` ativo — o venv só reescreve a parte do `PATH` que aponta para `python`/`pip`.

**Instalar biblioteca e travar versões:**
```powershell
pip install pandas
pip freeze > requirements.txt
```
`pip install pandas` trouxe automaticamente as dependências do próprio pandas (`numpy`, `python-dateutil`, `six`, `tzdata`) — resolução de árvore de dependências feita pelo `pip`. `pip freeze` lista tudo que está instalado no ambiente ativo com a versão exata, redirecionado para `requirements.txt` — arquivo que permite qualquer pessoa (ou você, em outra máquina) recriar o ambiente idêntico com um único comando (`pip install -r requirements.txt`), sem precisar adivinhar versões.

**Por que `venv/` também vai para o `.gitignore`:** mesma lógica do `results.csv` — grande, específico da máquina (caminhos absolutos internos) e 100% reproduzível a partir do `requirements.txt`. Nunca se commita o ambiente, só a receita para recriá-lo.

---

## 1.5 — 2026-08-21 — Primeiro script real: `src/validation/schema_profile.py`

**Fundamentos de Python revisados na prática:** blocos definidos por `:` + indentação (não `{ }` como em C/Java/JS); `for x in range(a, b):` (limite superior exclusivo) em vez de `while` com contador manual; f-strings (`f"texto {variavel}"`) para montar caminhos dinâmicos; dicionários (`{}`, `dict[chave] = valor`, `.items()` para iterar chave+valor); **dict comprehension** (`{chave: transformação for chave, valor in algo.items()}`) como forma compacta de construir um dicionário novo a partir de outro.

**Conceito: `DataFrame` do pandas.** Estrutura de tabela em memória (linhas + colunas rotuladas), devolvida por `pd.read_csv(caminho)`. `nrows=N` no `read_csv` lê só as N primeiras linhas sem carregar o arquivo inteiro — essencial para espiar arquivos grandes (100+ MB) sem gastar memória à toa.

**Profiling dos 6 `schema.csv` — achado real de schema evolution, não hipotético:**
```
2020        (61, 2)  colunas: ['Column', 'QuestionText']
2021–2024   (~48-87, 6)  colunas: ['qid', 'qname', 'question', 'force_resp', 'type', 'selector']
2025        (139, 6)  colunas: ['qid', 'qname', 'question', 'type', 'sub', 'sq_id']
```
**Não são 2 formatos, são 3** — 2021-2024 têm as mesmas 6 colunas entre si, mas 2025 trocou `force_resp`/`selector` por `sub`/`sq_id`. Checar só a *contagem* de colunas (6 == 6) teria escondido essa mudança; só comparar os *nomes* revelou.

**Decisão de normalização:** mapear para um contrato canônico mínimo — `question_code` (de `qname`/`Column`) e `question_text` (de `question`/`QuestionText`) — as duas únicas colunas semanticamente equivalentes nos 3 formatos. `type`, `force_resp`, `selector`, `sub`, `sq_id` ficam de fora deliberadamente: não têm correspondência 1:1 entre todos os anos (ex.: `force_resp` e `sub` são conceitos diferentes, não a mesma coisa renomeada), e nenhuma métrica do projeto depende deles hoje. Regra aplicada: normalizar só o que atende uma necessidade concreta já identificada, não especular.

```python
def normalize_schema(df, ano):
    if ano == 2020:
        df = df.rename(columns={"Column": "question_code", "QuestionText": "question_text"})
    else:
        df = df.rename(columns={"qname": "question_code", "question": "question_text"})
    return df[["question_code", "question_text"]]
```

**Espiada no `results.csv` de 2025** (via `nrows=5`, sem carregar os 140 MB inteiros): mais de 150 colunas — uma por pergunta do questionário. Confirma visualmente o padrão de "sub-pergunta" identificado no schema (`TechEndorse_1` a `TechEndorse_13`, `JobSatPoints_1` a `JobSatPoints_16` — uma coluna por opção de resposta de perguntas de múltipla escolha). Colunas-chave já localizadas para as métricas do projeto: `ConvertedCompYearly` (salário anual convertido, provavelmente para USD) e `LanguageHaveWorkedWith` (linguagens usadas).

---

## 1.6 — 2026-08-21 — Comparando os 6 anos com `set()`: o "núcleo estável" de perguntas

**Conceito: `set()`.** Coleção sem ordem e sem duplicatas, com três operações principais: `&`/`.intersection()` (o que está em **todos** ao mesmo tempo — mais restritivo), `|`/`.union()` (o que está em **qualquer um** — menos restritivo), `-` (o que está num mas não no outro). Erro comum cometido e corrigido na prática: confundir união com interseção — testado com um exemplo de brinquedo (`a={1,2,3}`, `b={2,3,4}`, `c={3,4,5}`) até fechar que só o `3` (presente nos três ao mesmo tempo) é a interseção; `{1,2,3,4,5}` seria a união.

**Pipeline construído:**
```python
codigos_por_ano = {ano: set(df["question_code"]) for ano, df in schemas_normalizados.items()}
listas_de_codigos = list(codigos_por_ano.values())
nucleo_estavel = listas_de_codigos[0].intersection(*listas_de_codigos[1:])
```
`list(dic.values())` transforma os 6 sets guardados no dicionário numa lista indexável; `*lista[1:]` espalha "todos menos o primeiro" como argumentos separados para `.intersection()`.

**Resultado — só 14 códigos de pergunta sobrevivem idênticos nos 6 anos (2020–2025):**
```
SOAccount, YearsCode, SOVisitFreq, Employment, CompTotal, SOPartFreq,
Country, DevType, OpSys, OrgSize, EdLevel, SOComm, MainBranch, Age
```
**Por que o número é baixo e isso é esperado, não bug:** a interseção nunca passa do menor set (2020 já tem só 61 códigos no total); e boa parte das perguntas restantes são sub-opções de múltipla escolha (`TechEndorse_N`, `AIAgent*`) que a Stack Overflow renomeia/renumera com frequência a cada redesign do survey. O núcleo de 14 é composto majoritariamente por perguntas demográficas/estruturais básicas — exatamente o que se esperaria ser mais estável ano a ano.

**Achado crítico para o projeto:** `LanguageHaveWorkedWith` (a pergunta mais importante do projeto — linguagens usadas) **não está** no núcleo estável — o nome dessa coluna mudou em algum(ns) dos 6 anos. Vai precisar de mapeamento manual específico, ano a ano, assim como possivelmente `ConvertedCompYearly` (salário convertido — `CompTotal`, o valor bruto não convertido, está estável, mas o convertido ainda não foi checado).

**Próximo passo planejado:** usar `.str.contains("Language", case=False)` (filtro de texto em coluna do pandas, equivalente a `LIKE '%Language%'` do SQL) para caçar, em cada ano, qual(is) código(s) de pergunta correspondem a linguagem — e repetir para salário.

---

## 1.7 — 2026-08-22 — `schema.csv` não é confiável para nome de coluna real; mapeamento definitivo de linguagem

**Descoberta importante de metodologia:** ao buscar "language" dentro do `schema.csv` normalizado de 2021, apareceu só **um** código genérico (`Language`) — mas o `results.csv` real daquele ano tem **duas** colunas (`LanguageHaveWorkedWith`, `LanguageWantToWorkWith`). Ou seja: **o `schema.csv` nem sempre lista cada coluna do `results.csv` individualmente** — às vezes descreve a pergunta de forma mais genérica/agrupada. Conclusão prática: para saber o nome exato de uma coluna, checar o `results.csv` real (via `pd.read_csv(..., nrows=5)`, sem carregar o arquivo inteiro) é mais confiável do que confiar no `schema.csv`.

**Mapeamento real, coluna a coluna, direto do `results.csv` dos 6 anos:**
```
2020        LanguageDesireNextYear, LanguageWorkedWith            (2 colunas)
2021–2023   LanguageHaveWorkedWith, LanguageWantToWorkWith        (2 colunas, estável 3 anos)
2024        + LanguageAdmired                                     (3 colunas)
2025        + LanguageChoice, LanguagesHaveEntry, LanguagesWantEntry  (6 colunas)
```

**Contrato canônico para "linguagem usada" (peça central do Opportunity Score/adoção):**

| Ano | Coluna real |
|---|---|
| 2020 | `LanguageWorkedWith` |
| 2021–2025 | `LanguageHaveWorkedWith` (nome estável 5 anos seguidos) |

Só 2020 diverge; o resto do intervalo do projeto usa nome uniforme. Essa tabela é o que o script de ingestão vai usar para saber, em cada ano, qual coluna ler.

**Próximo passo:** repetir a mesma caça para a coluna de salário (`ConvertedCompYearly` ou equivalente).