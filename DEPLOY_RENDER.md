# 🚀 Deploy no Render - AI CSV Analyzer

Este guia explica como fazer deploy da aplicação AI CSV Analyzer no Render.

## 📋 Pré-requisitos

1. **Conta no Render**: Crie uma conta gratuita em [render.com](https://render.com)
2. **Repositório GitHub**: Seu código deve estar em um repositório público no GitHub
3. **OpenAI API Key**: Chave de API válida da OpenAI

## 🔧 Configuração do Deploy

### 1. Conectar Repositório

1. Acesse o [Dashboard do Render](https://dashboard.render.com)
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Selecione o repositório `atividadeExtra`

### 2. Configurações do Serviço

**Configurações Básicas:**
- **Name**: `ai-csv-analyzer` (ou nome de sua escolha)
- **Environment**: `Python 3`
- **Region**: `Oregon (US West)` (recomendado para melhor performance)
- **Branch**: `main`

**Comandos de Build e Start:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false`

### 3. Variáveis de Ambiente

Configure as seguintes variáveis de ambiente no painel do Render:

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `OPENAI_API_KEY` | `sk-proj-...` | Sua chave de API da OpenAI |
| `PYTHONUNBUFFERED` | `1` | Para logs em tempo real |
| `STREAMLIT_SERVER_HEADLESS` | `true` | Modo headless |
| `STREAMLIT_SERVER_ENABLE_CORS` | `false` | Desabilitar CORS |
| `STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION` | `false` | Desabilitar XSRF |

### 4. Configurações Avançadas

**Plano:** Free (suficiente para testes e uso acadêmico)
**Auto-Deploy:** Habilitado (deploy automático a cada push)

## 📁 Arquivos de Configuração

O projeto já inclui os arquivos necessários para o Render:

- **`render.yaml`**: Configuração automática do serviço
- **`start.sh`**: Script de inicialização (opcional)
- **`.streamlit/config.toml`**: Configurações do Streamlit
- **`requirements.txt`**: Dependências com versões flexíveis

## 🚀 Processo de Deploy

1. **Push para GitHub**: Certifique-se de que todas as alterações estão no repositório
2. **Criar Serviço**: Configure o serviço no Render conforme instruções acima
3. **Aguardar Build**: O processo de build leva cerca de 3-5 minutos
4. **Configurar Variáveis**: Adicione a `OPENAI_API_KEY` nas configurações
5. **Testar Aplicação**: Acesse a URL fornecida pelo Render

## 🔍 Monitoramento

### Logs
- Acesse **"Logs"** no painel do serviço para ver logs em tempo real
- Logs incluem informações de inicialização e erros

### Métricas
- **CPU e Memória**: Monitore o uso de recursos
- **Requests**: Acompanhe o tráfego da aplicação

## 🛠️ Troubleshooting

### Problemas Comuns

**1. Erro de Build**
```
ERROR: Could not find a version that satisfies the requirement...
```
**Solução**: Verifique se todas as dependências estão corretas no `requirements.txt`

**2. Aplicação não inicia**
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solução**: Verifique se o comando de build está correto

**3. Erro de API Key**
```
OpenAI API key not found
```
**Solução**: Configure a variável `OPENAI_API_KEY` nas configurações do serviço

**4. Timeout na inicialização**
**Solução**: O Render pode levar alguns minutos para inicializar. Aguarde ou reinicie o serviço.

### Comandos Úteis

**Reiniciar Serviço:**
- No painel do Render: **"Manual Deploy"** → **"Deploy latest commit"**

**Ver Logs em Tempo Real:**
- No painel do Render: **"Logs"** → Logs automáticos

## 📊 Performance

### Otimizações Implementadas

- **Backend matplotlib**: Configurado para `Agg` (não-interativo)
- **Cache desabilitado**: Para evitar problemas de memória
- **Configurações Streamlit**: Otimizadas para produção
- **Dependências flexíveis**: Versões mínimas para compatibilidade

### Limites do Plano Free

- **CPU**: 0.1 vCPU
- **RAM**: 512 MB
- **Bandwidth**: 100 GB/mês
- **Build time**: 500 minutos/mês

## 🔐 Segurança

### Variáveis de Ambiente
- ✅ **API Keys**: Configuradas como variáveis de ambiente
- ✅ **Arquivo .env**: Não incluído no repositório
- ✅ **Logs**: Não expõem informações sensíveis

### HTTPS
- ✅ **SSL/TLS**: Automático no Render
- ✅ **Domínio seguro**: `https://seu-app.onrender.com`

## 🌐 URL da Aplicação

Após o deploy, sua aplicação estará disponível em:
```
https://ai-csv-analyzer.onrender.com
```
(substitua pelo nome do seu serviço)

## 📞 Suporte

- **Documentação Render**: [docs.render.com](https://docs.render.com)
- **Comunidade**: [community.render.com](https://community.render.com)
- **Status**: [status.render.com](https://status.render.com)

---

**✅ Deploy Concluído!** Sua aplicação AI CSV Analyzer está agora rodando na nuvem! 🎉