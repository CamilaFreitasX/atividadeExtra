# Agente de Análise de Dados CSV

Este projeto implementa um agente inteligente capaz de analisar qualquer arquivo CSV, gerar gráficos e apresentar conclusões através de uma interface web interativa.

## Características

- **Análise Exploratória de Dados (EDA)** automatizada
- **Geração de gráficos** interativos
- **Processamento de linguagem natural** para perguntas sobre os dados
- **Sistema de memória** para manter contexto das análises
- **Interface web** intuitiva com Streamlit

## 🔒 Segurança e Configuração

### ⚠️ IMPORTANTE - Antes de usar:

1. **NUNCA commite o arquivo `.env`** - ele contém sua chave API
2. **Use sempre o `.env.example`** como referência
3. **Leia o arquivo `SECURITY.md`** para práticas de segurança

### Instalação Segura

1. Clone o repositório:
```bash
git clone https://github.com/CamilaFreitasX/atividadeExtra
cd atividadeExtra
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure suas variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com sua chave REAL da OpenAI
```

4. **Verifique se o .env está sendo ignorado:**
```bash
git status
# O arquivo .env NÃO deve aparecer na lista
```

## Uso

Execute a aplicação:
```bash
streamlit run app.py
```

Acesse `http://localhost:8501` no seu navegador.

## Funcionalidades

- Upload de arquivos CSV
- Análise automática de tipos de dados
- Geração de estatísticas descritivas
- Detecção de outliers
- Análise de correlações
- Visualizações interativas
- Respostas a perguntas em linguagem natural

## Estrutura do Projeto

- `app.py` - Interface principal Streamlit
- `csv_agent.py` - Agente de análise de dados
- `data_analyzer.py` - Módulo de análise de dados
- `visualization.py` - Módulo de visualizações
- `memory_system.py` - Sistema de memória do agente