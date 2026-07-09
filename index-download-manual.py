import pandas as pd
import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

print("PLANILHA_INTERNA:", os.getenv("PLANILHA_INTERNA"))
print("CAMINHO_BASE:", os.getenv("CAMINHO_BASE"))
print("ARQUIVO_FINAL:", os.getenv("ARQUIVO_FINAL"))


# ===============================================================
# CONFIGURAÇÕES
# ===============================================================
PLANILHA_INTERNA = os.getenv("PLANILHA_INTERNA")
CAMINHO_BASE = os.getenv("CAMINHO_BASE")
ARQUIVO_FINAL = os.getenv("ARQUIVO_FINAL")

pd.set_option('future.no_silent_downcasting', True)


# ===============================================================
# FUNÇÕES UTILITÁRIAS
# ===============================================================

def limpar_valor(x):
    """
    Converte valores removendo .0 de floats inteiros
    """
    if pd.isna(x):
        return ""
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x).strip()


def forcar_colunas_para_string(df):
    """
    Força colunas textuais para string sem gerar 'None' ou 'nan'
    e remove .0 de números inteiros
    """
    colunas_texto = [
        'IMPACTO', 'AFETACAO', 'TA', 'ACOMPANHAMENTO', 'STATUS MACRO',
        'RESPONSÁVEL', 'PRAZO', 'MODELO', 'COD. MODELO',
        'FABRICANTE', 'SS', 'BACKLOG'
    ]

    for col in colunas_texto:
        if col in df.columns:
            df[col] = df[col].apply(limpar_valor)

    return df


def formatar_data_br(df, colunas_data):
    """
    Converte colunas de data para DD/MM/AAAA
    """
    for col in colunas_data:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors='coerce',
                dayfirst=True
            ).dt.strftime('%d/%m/%Y')

            df[col] = df[col].fillna("")

    return df


# ===============================================================
# PROCESSAMENTO DOS DADOS
# ===============================================================

def carregar_dados_maestro(caminho, aba='Sheet1'):
    print("Localizando cabeçalho e carregando dados...")

    df_temp = pd.read_excel(caminho, sheet_name=aba, engine='openpyxl', header=None)

    linha_cabecalho = None
    for i, row in df_temp.iterrows():
        if 'REGIONAL' in [str(val).upper() for val in row.values]:
            linha_cabecalho = i
            break

    if linha_cabecalho is None:
        raise ValueError("Coluna 'REGIONAL' não encontrada!")

    return pd.read_excel(
        caminho,
        sheet_name=aba,
        engine='openpyxl',
        header=linha_cabecalho
    )


def processar_filtros_e_agrupamento(df):
    print("Processando filtros e agrupamentos...")

    df.columns = df.columns.astype(str).str.strip().str.upper()

    cols_preencher = ['REGIONAL', 'UF', 'MUNICIPIO', 'CN', 'SITE', 'TECNOLOGIA', 'ERB']
    df[cols_preencher] = df[cols_preencher].ffill()

    # Filtros
    df = df[(df.iloc[:, -1] >= 500) & (df.iloc[:, -2] > 0)]

    colunas_chave = ['REGIONAL', 'UF', 'MUNICIPIO', 'CN', 'SITE', 'TECNOLOGIA', 'ERB']
    df_agrupado = df.groupby(colunas_chave).size().reset_index(name='TOTAL DE SETORES')

    return df_agrupado[df_agrupado['UF'] == 'BA'].copy()


def aplicar_base_e_regras(df_trabalho, caminho_base):
    colunas_extras = [
        'IMPACTO', 'AFETACAO', 'TA', 'ACOMPANHAMENTO', 'STATUS MACRO',
        'RESPONSÁVEL', 'PRAZO', 'MODELO', 'COD. MODELO',
        'FABRICANTE', 'SS', 'BACKLOG'
    ]

    for col in colunas_extras:
        df_trabalho[col] = None

    df_trabalho['BACKLOG'] = 'Não'

    if os.path.exists(caminho_base):
        print("Mesclando com a base de referência...")

        base_df = pd.read_excel(caminho_base, engine='openpyxl')
        base_df.columns = base_df.columns.astype(str).str.strip().str.upper()

        df_trabalho['ERB'] = df_trabalho['ERB'].astype(str).str.strip()
        base_df['ERB'] = base_df['ERB'].astype(str).str.strip()

        merged = pd.merge(
            df_trabalho,
            base_df,
            on='ERB',
            how='left',
            suffixes=('', '_BASE'),
            indicator=True
        )

        merged['BACKLOG'] = merged['_merge'].map({
            'both': 'Sim',
            'left_only': 'Não'
        })

        for col in colunas_extras + ['CN', 'MUNICIPIO', 'SITE', 'TECNOLOGIA']:
            if col == 'BACKLOG':
                continue

            col_base = f"{col}_BASE"
            if col_base in merged.columns:
                merged[col] = merged[col_base].fillna(merged[col])

        merged.drop(columns=['_merge'], inplace=True)
        df_trabalho = merged[df_trabalho.columns].copy()

    # Regras finais
    df_trabalho.loc[df_trabalho['STATUS MACRO'].isna(), 'STATUS MACRO'] = 'Em análise'
    df_trabalho.loc[df_trabalho['TOTAL DE SETORES'] == 3, 'IMPACTO'] = 'Total'
    df_trabalho.loc[df_trabalho['TOTAL DE SETORES'] != 3, 'IMPACTO'] = 'Parcial'

    return df_trabalho


# ===============================================================
# RELATÓRIO
# ===============================================================

def gerar_relatorio_geral(df):
    contagem = df['MODELO'].dropna()

    if contagem.empty:
        print("Nenhum valor em 'MODELO' para gerar gráfico.")
        return

    contagem = contagem.value_counts()
    num_modelos = len(contagem)

    altura = (num_modelos * 0.4) + 2
    fig, ax = plt.subplots(figsize=(12, altura))

    bars = ax.barh(contagem.index, contagem.values, color='skyblue', edgecolor='black')
    ax.invert_yaxis()
    ax.bar_label(bars, padding=5)

    plt.title('Quantidade Geral de Modelos')
    plt.tight_layout()

    caminho_grafico = r"C:\Users\40419159\OneDrive - Telefonica\Área de Trabalho\SetoresCelldowntime\Relatório de Modelos.png"
    plt.savefig(caminho_grafico)
    plt.close()

    print("Gráfico gerado com sucesso.")


# ===============================================================
# MAIN
# ===============================================================

def main():
    try:
        df_bruto = carregar_dados_maestro(PLANILHA_INTERNA)
        df_filtrado = processar_filtros_e_agrupamento(df_bruto)
        df_final = aplicar_base_e_regras(df_filtrado, CAMINHO_BASE)

        df_final = forcar_colunas_para_string(df_final)
        df_final = formatar_data_br(df_final, ['PRAZO'])

        print("\nResumo BACKLOG:")
        print(df_final['BACKLOG'].value_counts(dropna=False))

        gerar_relatorio_geral(df_final)

        df_final.to_excel(ARQUIVO_FINAL, index=False)

        print("\n--- SUCESSO! ---")
        print(f"Arquivo gerado: {ARQUIVO_FINAL}")

    except Exception as e:
        print("\n--- ERRO NO PROCESSAMENTO ---")
        print(f"Detalhes: {e}")


if __name__ == "__main__":
    main()
