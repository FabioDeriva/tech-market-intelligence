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
