# 📡 Automação de Consolidação de Dados ERB & Backlog

Automação em Python que centraliza, higieniza e consolida dados de estações rádio base (ERB) e status de backlog, eliminando um processo antes feito manualmente em planilhas Excel.

## 🎯 Problema resolvido

A equipe recebia periodicamente relatórios de setores/ERBs em formato inconsistente (planilhas com cabeçalhos deslocados, outras sem cabeçalho algum, dados zipados e distribuídos em múltiplos arquivos). Cruzar isso manualmente com a base de referência de backlog para identificar impacto (total/parcial) e status de tratativa consumia um tempo considerável por ciclo e estava sujeito a erro humano.

Este projeto automatiza o pipeline: **download → extração → padronização → cruzamento → geração de relatório**.

## ⚙️ Funcionalidades

- **Download automático** do arquivo compactado de origem via `requests`, com tratamento de nome de arquivo dinâmico
- **Extração seletiva** de planilhas dentro do `.zip`, localizando arquivos por padrão de nome (parte fixa), independente de sufixos variáveis
- **Normalização de cabeçalho**: localização automática da linha de cabeçalho em uma planilha, e reaproveitamento dessa estrutura para uma segunda planilha que não possui cabeçalho próprio
- **Consolidação de múltiplas fontes** em um único DataFrame, com rastreabilidade da origem de cada registro
- **Preenchimento de células mescladas** (`ffill`) para reconstruir hierarquias de Regional/UF/Município/Site
- **Cruzamento com base de referência** (merge) para identificar status de backlog (`Sim`/`Não`) por ERB
- **Regras de negócio automatizadas**: classificação de impacto (Total/Parcial) por quantidade de setores afetados
- **Geração de relatório visual** (gráfico de barras horizontal com `matplotlib`) da distribuição de modelos de equipamento
- **Exportação para Excel** já tratado, com valores formatados (datas em `DD/MM/AAAA`, remoção de `.0` de inteiros, sem `NaN`/`None` literais)
- **Configuração via `.env`**, sem caminhos ou credenciais hardcoded no código-fonte

## 🛠️ Stack técnica

| Tecnologia             | Uso                                                     |
| ---------------------- | ------------------------------------------------------- |
| **Python 3.12**        | Linguagem principal                                     |
| **pandas**             | Manipulação, limpeza e cruzamento de dados              |
| **openpyxl**           | Leitura/escrita de arquivos Excel                       |
| **matplotlib**         | Geração de gráficos do relatório                        |
| **requests**           | Download automatizado do arquivo de origem              |
| **python-dotenv**      | Gerenciamento de configuração via variáveis de ambiente |
| **zipfile / tempfile** | Extração segura de planilhas em pasta temporária        |

## 📁 Estrutura do fluxo

```
Link fixo (HTTPS)
      │
      ▼
 Download do .zip ──► Extração das planilhas por padrão de nome
      │
      ▼
 Padronização de cabeçalho e tipos de dado
      │
      ▼
 Consolidação (concat) + agrupamento por chave (Regional/UF/Site/ERB)
      │
      ▼
 Cruzamento com base de referência de backlog (merge)
      │
      ▼
 Aplicação de regras de negócio (impacto, status)
      │
      ▼
 Exportação: Excel tratado + gráfico de modelos
```

## 🔐 Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
LINK_DOWNLOAD_ZIP=https://...
CAMINHO_BASE=C:\caminho\para\base_referencia.xlsx
ARQUIVO_FINAL=C:\caminho\para\saida\relatorio_final.xlsx
```

## ▶️ Como executar

```bash
pip install -r requirements.txt
python main.py
```

## 📌 Contexto

Projeto desenvolvido para uso interno em rotina de acompanhamento de rede de telecomunicações, com foco em reduzir trabalho manual repetitivo e padronizar a qualidade dos dados usados na tomada de decisão da equipe.

---

_Este é um projeto de automação real, adaptado para portfólio. Caminhos, links e nomes de arquivos sensíveis foram generalizados._
