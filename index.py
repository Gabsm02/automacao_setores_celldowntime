import pandas as pd
import zipfile
import tempfile
import shutil
import os
import matplotlib.pyplot as plt
import requests
import time
import urllib3
from dotenv import load_dotenv

load_dotenv()


# ===============================================================
# CONFIGURAÇÕES
# ===============================================================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
PLANILHA_INTERNA = os.getenv("PLANILHA_INTERNA")
CAMINHO_BASE = os.getenv("CAMINHO_BASE")
ARQUIVO_FINAL = os.getenv("ARQUIVO_FINAL")
LINK_DOWNLOAD_ZIP = os.getenv("LINK_DOWNLOAD_ZIP")

pd.set_option('future.no_silent_downcasting', True)


# ===============================================================
# FUNÇÕES UTILITÁRIAS
# ===============================================================

def limpar_valor(x):
    if pd.isna(x):
        return ""
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x).strip()


def forcar_colunas_para_string(df):
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
    for col in colunas_data:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors='coerce',
                dayfirst=True
            ).dt.strftime('%d/%m/%Y')

            df[col] = df[col].fillna("")

    return df

def baixar_zip(url, pasta_destino):
    print('Iniciando download...')
    response = requests.get(url, stream=True, timeout=60, verify=False)
    response.raise_for_status()

    nome_arquivo = None
    content_disposition = response.headers.get('content-disposition')

    if content_disposition and 'filename=' in content_disposition:
        nome_arquivo = content_disposition.split('filename=')[-1].strip('";')

    if not nome_arquivo: 
        nome_arquivo = f"setores_celldowntime_hmm_{int(time.time())}.zip"

    caminho_zip = os.path.join(pasta_destino, nome_arquivo)

    with open(caminho_zip, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print("Download finalizado !")
    
    return caminho_zip

def extrair_planilhas(caminho_zip, pasta_destino):
    nomes_esperados = ["Setores_CellDowntime_HMM_NE_0", "Setores_CellDowntime_HMM_NE_1"]

    caminhos_extraidos = {}

    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
        arquivos_no_zip = zip_ref.namelist()

        for nome_esperado in nomes_esperados:
            arquivo_encontrado = next((a for a in arquivos_no_zip if nome_esperado in a), None)

            if arquivo_encontrado is None:
                raise FileNotFoundError (
                    f"Arquivo '{nome_esperado}' não encontrado"
                )
            zip_ref.extract(arquivo_encontrado, pasta_destino)
            caminhos_extraidos[nome_esperado] = os.path.join(pasta_destino, arquivo_encontrado)

    return caminhos_extraidos


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

def carregar_planilha_sem_cabecalho(caminho, colunas_referencia, aba='Sheet1'):
    df = pd.read_excel(caminho, sheet_name=aba, engine='openpyxl', header=None)

    df.columns = colunas_referencia
    return df

def processar_filtros_e_agrupamento(df):
    print("Processando filtros e agrupamentos...")

    df.columns = df.columns.astype(str).str.strip().str.upper()

    cols_preencher = ['REGIONAL', 'UF', 'MUNICIPIO', 'CN', 'SITE', 'TECNOLOGIA', 'ERB']
    df[cols_preencher] = df[cols_preencher].ffill()

    df_para_filtro = df.drop(columns=['ORIGEM_ARQUIVO'], errors='ignore')
    df = df[(df_para_filtro.iloc[:,-1] >= 500) & (df_para_filtro.iloc[:, -2] > 0)]

    colunas_chave = ['REGIONAL', 'UF', 'MUNICIPIO', 'CN', 'SITE', 'TECNOLOGIA', 'ERB']
    df_agrupado = df.groupby(colunas_chave).size().reset_index(name='TOTAL DE SETORES')

    return df_agrupado[df_agrupado['UF'] == 'BA'].copy()

def carregar_dados_maestro_combinado(caminhos_planilhas):
    dfs=[]
    colunas_referencia = None

    caminho_0 = caminhos_planilhas["Setores_CellDowntime_HMM_NE_0"]
    df_0 = carregar_dados_maestro(caminho_0)
    colunas_referencia = df_0.columns.tolist()
    df_0['ORIGEM_ARQUIVO'] = "Setores_CellDowntime_HMM_NE_0"
    dfs.append(df_0)

    caminho_1 = caminhos_planilhas["Setores_CellDowntime_HMM_NE_1"]
    df_1 = carregar_planilha_sem_cabecalho(caminho_1, colunas_referencia)
    df_1['ORIGEM_ARQUIVO'] = "Setores_CellDowntime_HMM_NE_1"
    dfs.append(df_1)
    
    return pd.concat(dfs, ignore_index=True)

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
    pasta_temp = tempfile.mkdtemp()

    try:

        caminho_zip_baixado = baixar_zip(LINK_DOWNLOAD_ZIP, pasta_temp)
        caminhos_planilhas = extrair_planilhas(caminho_zip_baixado, pasta_temp)
        df_bruto = carregar_dados_maestro_combinado(caminhos_planilhas)

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

    finally:
        shutil.rmtree(pasta_temp, ignore_errors=True)

if __name__ == "__main__":
    main()
