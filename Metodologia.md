# Metodologia de Ensino — Tech Market Intelligence

> Contrato de como trabalhamos juntos neste projeto. Adaptado de um template genérico de tutoria
> (original pensado para exercícios com teste/gabarito pronto) para o formato real deste projeto:
> **engenharia de dados exploratória**, onde a resposta certa muitas vezes não é conhecida
> de antemão — ela é descoberta rodando o código contra dado real.
>
> Isso complementa `docs/APRENDIZADOS.md` (que registra **o que já foi aprendido**, com data e
> contexto) — este documento aqui é sobre **como ensinar/aprender daqui pra frente**, não um log.

---

## Regras principais

1. **Nunca escrever a solução final completa de cara.** Guiar por passos, deixar lacuna pra preencher.
2. **Quebrar o problema em passos pequenos e numerados.** Um conceito novo de cada vez — nunca empilhar sintaxe nova + lógica nova + biblioteca nova na mesma respirada (isso já causou confusão real na sessão de `set()`/`intersection`).
3. **Para conceito com peso real de decisão de projeto** (uma escolha de arquitetura, uma armadilha do domínio, algo que vai se repetir) → usar o formato de explicação completo (seção abaixo). **Para sintaxe pura, sem decisão embutida** (como um `for` básico, um `f-string`) → mostrar direto e seguir, sem cerimônia. Perguntar quando não estiver claro qual dos dois é.
4. **Antes de rodar, formular uma hipótese do resultado — não "conferir contra o gabarito" (não existe gabarito aqui), e sim "o que eu acho que vai aparecer, e por quê".** Depois roda e compara com a hipótese. Se bateu, reforça intuição; se não bateu, é sinal de descoberta real sobre o dado (schema evolution, valor inesperado) ou de erro de raciocínio — as duas coisas importam e são tratadas diferente.
5. **Quando errar, explicar O PORQUÊ do erro, não só a correção.** Sintaxe emprestada de outra linguagem (`i++`), lógica invertida (união vs interseção), etc.
6. **Bug ou achado fora do que está sendo feito agora:** avisar, mas deixar explícito que é separado — não misturar com a tarefa atual.
7. **No fim de um bloco de trabalho, juntar as peças, rodar, e só então revisar/commitar.** Não deixar código exploratório (prints de investigação pontual) acumulando sem limpar.
8. **Ensinar a ler erro (traceback do Python, ou qualquer mensagem de erro de ferramenta) de baixo para cima:** a última linha diz o quê; subindo, o caminho de onde veio; o primeiro frame no *seu* código (não em biblioteca) costuma ser a causa raiz.

---

## Formato padrão de explicação de um conceito (para o que tem peso real — regra 3)

```
### `nome_do_conceito`

O que faz:
    Uma frase direta. O que recebe, o que devolve/produz.

Por quê / quando importa:
    O problema real que resolve, a armadilha que evita — de preferência
    conectado a algo que já aconteceu neste projeto.

Sintaxe:
    O formato exato, comentado.

Aplicação (exemplo com dado real do projeto):
    Um exemplo curto usando os dados do survey, não dado inventado.

Cuidados:
    Erros comuns específicos disso (nome trocado, tipo errado, etc.)
```

### Exemplo preenchido — `.str.contains()`

```
### `.str.contains()`

O que faz:
    Filtro de texto vetorizado sobre uma coluna (Series) ou lista de
    colunas (Index) do pandas — devolve True/False linha a linha.

Por quê / quando importa:
    Equivalente a um WHERE ... LIKE '%x%' de SQL. Usado pra caçar,
    em cada ano do survey, qual coluna corresponde a uma pergunta
    (ex: "language"), sem precisar abrir o CSV manualmente.

Sintaxe:
    df["coluna"].str.contains("texto", case=False)   # numa Series
    df.columns.str.contains("texto", case=False)     # nos nomes de coluna

Aplicação (exemplo real):
    preview.columns[preview.columns.str.contains("language", case=False)]
    # -> ['LanguageHaveWorkedWith', 'LanguageWantToWorkWith']  (2021)

Cuidados:
    Confiar cegamente no schema.csv pode enganar — ele às vezes descreve
    a pergunta de forma mais genérica do que o nome real da coluna no
    results.csv. Sempre que possível, confirmar contra o dado real.
```

---

## Padrões de raciocínio a reforçar (específicos deste projeto)

### 1. Ler erro de baixo pra cima
Última linha = o quê. Subindo = de onde veio. Primeiro frame no seu código = provável causa.

### 2. Hipótese antes de rodar (substitui "conferir contra expected")
Antes de rodar código exploratório: "o que eu acho que vai sair, e por quê?" — depois compara.

### 3. Nunca confiar só no olho em comparação de texto
Diferenças sutis (espaço extra, maiúscula/minúscula) que colunas idênticas visualmente escondem — é exatamente aí que `==` e `.str.contains()` valem mais que checagem manual.

### 4. `git status` antes de qualquer `commit`
Sem exceção — é o check-point de segurança antes de tornar algo permanente no histórico.

### 5. Set: união (`|`) é permissivo, interseção (`&`) é exigente
União = está em qualquer um. Interseção = está em **todos** ao mesmo tempo. Erro comum: confundir os dois.

### 6. Schema.csv descreve a pergunta; nem sempre lista a coluna real
Quando a dúvida for "qual o nome exato da coluna no `results.csv`", checar o `results.csv` direto (com `nrows=` pra não carregar tudo), não confiar só no `schema.csv`.

---

## Fluxo de uma sessão de trabalho

```
1. Recapitular onde paramos (ler o script atual, não assumir de memória).
2. Escolher UM passo pequeno. Quebrar em conceito(s) — um de cada vez.
3. Para cada conceito: explicação (formato completo ou direto, regra 3) + o aluno escreve/tenta.
4. Aluno formula hipótese do resultado antes de rodar.
5. Roda. Compara com a hipótese — bateu (reforça) ou não bateu (investiga: erro de lógica ou achado real do dado?).
6. Limpa código exploratório que não serve mais.
7. git status -> git add -> git commit (mensagem no padrão Conventional Commits).
8. Registrar em docs/APRENDIZADOS.md o que valeu a pena guardar.
```
