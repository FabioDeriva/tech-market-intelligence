# Diário de Aprendizado — Tech Market Intelligence

> Log incremental de decisões técnicas e conceitos aprendidos durante a construção do projeto.
> Serve de matéria-prima para o README final e para posts de LinkedIn.

---

## 2026-08-20 — Setup do ambiente e estrutura de pastas

**Contexto:** primeiro contato com o projeto, degrau 1 (Python puro + Postgres) ainda não começou o código.

**O que foi verificado:**
- Python 3.14.7 instalado corretamente (instalação real em `AppData\Local\Programs\Python`, não o stub da Microsoft Store).
- Docker já presente na máquina, mas **deliberadamente não usado ainda** — é ferramenta do degrau 5. Regra do projeto: uma tecnologia nova de cada vez.
- PostgreSQL ainda não instalado — correto para este ponto, só entra quando houver dado limpo pra carregar.

**Decisão de arquitetura — separação de camadas de dados:**
- `data/raw/` — ZIPs/CSVs originais dos surveys. **Nunca editado.** É a fonte da verdade; se uma transformação tiver bug, refaz-se a partir daqui.
- `data/staging/` — dados extraídos, ainda "crus" em significado, mas em formato utilizável.
- `src/ingestion/`, `src/transformation/`, `src/validation/`, `src/analytics/` — um módulo por responsabilidade (princípio de separação de responsabilidades). Evita virar um notebook monolítico de 400 células.

**Conceito aprendido — Git não versiona pastas vazias:**
Git rastreia conteúdo (blobs), não estrutura de diretórios. Uma pasta sem nenhum arquivo dentro simplesmente não aparece em `git status` nem é commitada. Solução comum: colocar um arquivo `.gitkeep` (convenção, não é uma feature nativa do Git) dentro de pastas que ainda estão vazias, só para dar a elas um arquivo para rastrear.

**Comando usado para criar a árvore de pastas (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path data/raw, data/staging, src/ingestion, src/transformation, src/validation, src/analytics, sql/staging, sql/intermediate, sql/marts, tests
```

**Por que não dá pra commitar uma pasta vazia (não é limitação artificial, é o modelo interno do Git):**
O Git só tem dois tipos de objeto relevantes aqui — `blob` (conteúdo de um arquivo) e `tree` (lista de entradas, cada uma apontando pra um blob ou outra tree). Uma entrada de tree sempre precisa apontar pra algo. Uma pasta vazia não tem nada pra apontar, então não existe objeto a ser criado — `git add` numa pasta vazia não tem o que registrar.

`.gitkeep` **não é uma feature do Git** — é convenção da comunidade: um arquivo qualquer, vazio, só para a pasta deixar de estar vazia e se tornar rastreável. O nome não tem significado especial para o Git.

**Comando para criar os `.gitkeep`:**
```powershell
"data/raw", "data/staging", "src/ingestion", "src/transformation", "src/validation", "src/analytics", "sql/staging", "sql/intermediate", "sql/marts", "tests" | ForEach-Object { New-Item -ItemType File -Force -Path "$_/.gitkeep" }
```

---

## 2026-08-20 (cont.) — Primeira surpresa real: a fonte de dados mudou de formato

**O plano original** (documento de contexto do projeto) previa baixar ZIPs contendo CSVs do site oficial `survey.stackoverflow.co`. **A realidade encontrada:** o Stack Overflow migrou a distribuição dos dados para um repositório GitHub (`StackExchange/Survey`), com um CSV puro por ano, hospedado via **Git LFS** (Large File Storage — mecanismo do Git para versionar arquivos grandes sem inchar o histórico do repositório).

**Por que isso é uma lição, não um contratempo:** planos de engenharia de dados quase sempre encontram uma realidade diferente do que foi documentado — fontes de dados mudam formato, local, protocolo de distribuição. Saber se adaptar (confirmar a nova fonte, validar que é confiável, ajustar o plano) é parte do trabalho, não uma exceção a ele. Isso inclusive já é a primeira instância de "evolução" que o projeto vai documentar — só que na camada de distribuição, antes mesmo de chegar nas colunas do CSV.

**Impacto prático:** como os dados já vêm em CSV puro (sem ZIP), a etapa de ingestão fica mais simples — não é necessário código de extração de ZIP, só leitura direta de CSV.

**URLs diretas dos 6 anos usados no projeto (2020–2025):**
```
https://github.com/StackExchange/Survey/raw/refs/heads/main/packages/archive/{ano}/results.csv
```

**Convenção de armazenamento no raw:** `data/raw/{ano}/results.csv` — um subdiretório por ano, mantendo a fonte auditável e o layout previsível para o script de ingestão.

---

## 2026-08-21 — Git: por que dado bruto não é versionado, `.gitignore`, e disciplina de commit

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
```

**Conceito: caminho completo, não nome, identifica um arquivo.** É possível (e correto) ter `data/raw/2020/results.csv` e `data/raw/2025/results.csv` com o mesmo nome — a pasta já desambigua. Renomear pra `results2025.csv` seria redundante (o ano já está codificado na pasta) e vai contra a boa prática de **manter o nome original do arquivo na camada raw**, que existe para preservar rastreabilidade até a fonte.

**Os três estados do Git (fluxo básico):**
```
diretório de trabalho  →  área de staging (index)  →  commit
     (git status olha aqui)   (git add move pra cá)      (git commit grava aqui)
```
`git status` é somente leitura — não precisa (nem faz sentido) rodar `git add` antes dele. Ele é o check-point de segurança que se roda **antes de qualquer commit**, para confirmar exatamente o que vai virar histórico permanente.

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

Commit de `.gitignore` + `schema.csv` + diário foi classificado como `chore`, não `feat`, porque nenhum dos arquivos entrega uma capacidade nova ao sistema — é configuração e dado bruto, não comportamento. `feat` fica reservado para quando o primeiro script de ingestão realmente fizer o sistema "ler CSV e carregar no banco" pela primeira vez.

**Decisão de idioma:** commits, código e README em inglês (convenção de mercado); `docs/APRENDIZADOS.md` em português (matéria-prima para conteúdo de LinkedIn).
