### Aprimorei meu pipeline de ETL! 🚀

Recentemente, compartilhei aqui sobre um pipeline de ETL em que estava trabalhando. Hoje trago uma atualização: o processo passou por uma grande otimização! Embora não seja 100% automático, reduzi drasticamente o trabalho braçal e o tempo de execução.

### ⏳ Como era antes?

O fluxo antigo demandava cerca de **10 minutos** diários de muita atenção. Eu precisava entrar no SharePoint, exportar a planilha, aguardar o download terminar, rodar o código de processamento e gerar o arquivo final. Depois disso, ainda precisava copiar as linhas manualmente, voltar ao SharePoint, apagar os dados antigos e só então colar a nova lista. Era um trabalho bem repetitivo.

### ⚡ Como funciona agora?

Para otimizar isso, desenvolvi duas automações utilizando o **Power Automate**, integradas com o meu script em **Python**:

- **Automação Matinal:** Todos os dias, às 6h da manhã, a primeira rotina exporta a planilha do SharePoint e a salva automaticamente na minha pasta local.
- **Ação Manual (O gatilho):** Quando inicio meu dia, só preciso me conectar à VPN e dar um clique para rodar o arquivo Python. O script faz todo o processamento do ETL e salva a planilha final.
- **Sincronização via OneDrive Business:** A segunda automação fica monitorando essa pasta. Assim que identifica que o arquivo final foi modificado pelo Python, ela aciona o SharePoint automaticamente e substitui os dados antigos pelas novas linhas processadas.

Vale ressaltar que eu poderia programar o Python para fazer essa busca totalmente sozinho, mas o proxy corporativo bloqueia requisições vindas de computadores que não são considerados seguros.

---

### ⏱️ O Resultado?

Com esse novo fluxo, eliminei o trabalho braçal e as esperas desnecessárias. Um processo que antes levava 10 minutos, agora exige apenas 3 minutos. E o maior ganho nem foi o tempo, mas a autonomia: o processo não depende mais ativamente de mim, permitindo que qualquer pessoa consiga executá-lo com facilidade.

### 💡 Vamos automatizar juntos?

Agora quero saber de vocês: será que existe algum processo aí na sua rotina que você gostaria de automatizar? Deixe nos comentários ou me mande uma mensagem, quem sabe eu posso te ajudar a encontrar a solução ideal!

#EngenhariaDeDados #PowerAutomate #SharePoint #Python #ETL #Automacao #Produtividade #DataEngineering

---

# 📡 Automação de Consolidação de Dados ERB & Backlog

Automação híbrida (Python + Power Automate) que centraliza, higieniza e consolida dados de estações rádio base (ERB) e status de backlog. O pipeline substitui um processo braçal de download, tratamento em planilhas Excel e upload manual, orquestrando a atualização direta no SharePoint.

## 🎯 Problema resolvido

Antes desta automação, a rotina demandava cerca de **10 minutos diários** de trabalho altamente repetitivo: era necessário entrar no SharePoint, exportar planilhas manualmente, aguardar downloads, rodar scripts de limpeza, copiar linhas e colar manualmente de volta no SharePoint substituindo os dados antigos.

Além disso, os relatórios de origem vinham em formatos inconsistentes (cabeçalhos deslocados ou inexistentes, dados zipados). Cruzar isso com a base de referência para identificar impactos e status de backlog consumia tempo e estava sujeito a erro humano.

**O novo fluxo reduziu esse tempo para apenas 3 minutos**, consistindo apenas na conexão à VPN e na execução do gatilho do script, descentralizando a tarefa e garantindo maior autonomia.

## ⚙️ Funcionalidades

- **Orquestração Matinal:** Um fluxo no Power Automate roda automaticamente às 6h da manhã, exportando a planilha do SharePoint e salvando na pasta local de processamento.
- **Sincronização Automática via OneDrive Business:** Após o processamento dos dados, um segundo fluxo detecta a modificação do arquivo final e atualiza o SharePoint de forma autônoma.
- **Tratamento de Dados com Python:**
  - Extração seletiva de planilhas dentro de `.zip`.
  - Normalização inteligente de cabeçalhos e preenchimento de células mescladas (`ffill`).
  - Consolidação de múltiplas fontes e cruzamento com base de referência de backlog.
  - Classificação automatizada de regras de negócio (Impacto Total/Parcial).
  - Geração de relatório visual (gráfico de barras) de modelos de equipamento.
- **Contorno de Restrições Corporativas:** O script Python foi desenhado para rodar localmente com a VPN ativada, resolvendo o bloqueio de proxy corporativo que impede requisições automatizadas diretas de computadores externos ao SharePoint.

## 🛠️ Stack técnica

| Tecnologia                | Uso                                                       |
| ------------------------- | --------------------------------------------------------- |
| **Python 3.12**           | Processamento de dados (ETL), limpeza e regras de negócio |
| **Power Automate**        | Orquestração de tarefas agendadas e gatilhos de nuvem     |
| **SharePoint / OneDrive** | Armazenamento de origem/destino e monitoramento de pastas |
| **pandas**                | Manipulação, limpeza e cruzamento de dados                |
| **openpyxl**              | Leitura/escrita de arquivos Excel                         |
| **matplotlib**            | Geração de gráficos do relatório                          |
| **python-dotenv**         | Gerenciamento de configuração via variáveis de ambiente   |

## 📁 Estrutura do fluxo

```text
⏰ [Power Automate] 06:00 AM
 └── Exporta a planilha do SharePoint para a pasta local mapeada.
       │
       ▼
💻 [Ação Manual - Gatilho]
 └── Conexão à VPN e execução do script Python (Necessário devido a bloqueio de Proxy Corporativo).
       │
       ▼
🐍 [Script Python - Processamento ETL]
 ├── Extração do arquivo compactado.
 ├── Padronização de cabeçalhos e tipos de dado.
 ├── Consolidação e agrupamento por chave (Regional/UF/Site/ERB).
 ├── Cruzamento com base de referência de backlog.
 └── Exportação: Arquivo Excel final tratado + gráficos.
       │
       ▼
☁️ [OneDrive Business / Power Automate]
 └── Gatilho detecta o novo arquivo processado pelo Python.
       │
       ▼
🔄 [Ação Automática]
 └── O Power Automate apaga os dados antigos no SharePoint e insere as novas linhas automaticamente.
```

## 🔐 Configuração

Crie um arquivo `.env` na raiz do projeto contendo as variáveis necessárias para a execução local do Python:

```env
CAMINHO_BASE=C:\caminho\para\base_referencia.xlsx
ARQUIVO_FINAL=C:\caminho\para\saida\relatorio_final.xlsx
```

_(Nota: O download do link fixo foi transferido para a etapa do Power Automate)_

## ▶️ Como executar

1. Certifique-se de que a automação do Power Automate das 06:00 AM já rodou e o arquivo base está na pasta.
2. Conecte-se à **VPN Corporativa**.
3. Execute o ambiente:

```bash
pip install -r requirements.txt
python main.py
```

4. O Power Automate e o OneDrive assumem o restante do processo enviando para a nuvem.

## 📌 Contexto e Resultados

Projeto desenvolvido para uso interno em rotina de acompanhamento de rede de telecomunicações.

**Resultados alcançados:**

- Redução de tempo operacional de **10 minutos para 3 minutos** diários.
- Fim da dependência ativa: qualquer membro da equipe com acesso à VPN pode acionar o script com 1 clique, sem precisar conhecer a estrutura do SharePoint ou regras de manipulação das planilhas.
- Maior integridade dos dados na tomada de decisão.

---

_Este é um projeto de automação real, adaptado para portfólio. Caminhos, links e nomes de arquivos sensíveis foram generalizados._
