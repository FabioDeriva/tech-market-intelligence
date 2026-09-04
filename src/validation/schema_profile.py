import pandas as pd

def normalize_schema(df, ano):
    if ano == 2020:
        df = df.rename(columns={"Column": "question_code", "QuestionText": "question_text"})
    else:
        df = df.rename(columns={"qname": "question_code", "question": "question_text"})
    return df[["question_code", "question_text"]]

schemas = {}

for ano in range(2020,2026):
    schemas[ano] = pd.read_csv(f"data/raw/{ano}/schema.csv")

schemas_normalizados = {ano: normalize_schema(df, ano) for ano, df in schemas.items()}
print(schemas_normalizados[2020].head())
print(schemas_normalizados[2025].head())

for ano, df in schemas_normalizados.items():
    print(ano, df.columns.tolist())


codigos_por_ano = {ano: set(df["question_code"]) for ano, df in schemas_normalizados.items()}

listas_de_codigos = list(codigos_por_ano.values())
nucleo_estavel = listas_de_codigos[0].intersection(*listas_de_codigos[1:])

print(nucleo_estavel)

for ano, df in schemas_normalizados.items():
    encontrados = df[df["question_code"].str.contains("Language", case=False)]
    print(ano)
    print(encontrados)
    print()

preview_2021 = pd.read_csv("data/raw/2021/results.csv", nrows=5)
colunas_language = preview_2021.columns[preview_2021.columns.str.contains("language", case=False)]
print(colunas_language.tolist())

for ano in range(2020, 2026):
    preview = pd.read_csv(f"data/raw/{ano}/results.csv", nrows=5)
    colunas_language = preview.columns[preview.columns.str.contains("language", case=False)]
    print(ano, colunas_language.tolist())

for ano in range(2020, 2026):
    preview = pd.read_csv(f"data/raw/{ano}/results.csv", nrows=5)
    colunas_salario = preview.columns[preview.columns.str.contains("comp", case=False)]
    print(ano, colunas_salario.tolist())