# 🚂 Deploy no Railway.com

## 🚨 **Migração do Render → Railway**

**Problema no Render:** AxiosError 502 com creditcard.csv (143.8MB)
**Solução:** Railway suporta arquivos grandes sem erro 502!

## 📋 Pré-requisitos

- Conta no [Railway.com](https://railway.app)
- Repositório GitHub com o código
- Chave da API OpenAI

## 🚀 Passos para Deploy

### 1. Conectar Repositório

1. Acesse [Railway.app](https://railway.app)
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Escolha o repositório `atividadeExtra`

### 2. Configurar Variáveis de Ambiente

No painel do Railway, vá em **Variables** e adicione:

```bash
OPENAI_API_KEY=sua_chave_aqui
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=500
STREAMLIT_SERVER_MAX_MESSAGE_SIZE=500
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
PYTHONUNBUFFERED=1
PORT=8080
```

### 3. Configurações Automáticas

O Railway detectará automaticamente:
- ✅ **railway.json** - Configurações do projeto
- ✅ **Procfile** - Comando de inicialização
- ✅ **requirements.txt** - Dependências Python
- ✅ **runtime.txt** - Versão do Python

## 🎯 Vantagens do Railway vs Render

| Recurso | Railway | Render |
|---------|---------|--------|
| **Limite de Upload** | 500MB+ | 200MB (com erros) |
| **Timeout** | Flexível | 30s (problemas) |
| **Memória** | Até 8GB | Limitada |
| **Deploy** | Instantâneo | Lento |
| **Logs** | Detalhados | Básicos |
| **Preço** | $5/mês | $7/mês |

## 📊 Suporte a Arquivos Grandes

### ✅ Configurações Otimizadas:

- **Limite máximo:** 500MB (vs 200MB no Render)
- **Processamento:** Chunks inteligentes
- **Memória:** Otimizada para arquivos grandes
- **Timeout:** Sem limitações rígidas

### 🔧 Processamento por Tamanho:

```python
# Arquivos > 100MB: 2000 linhas/partição
# Arquivos 50-100MB: 3000 linhas/partição  
# Arquivos 20-50MB: 5000 linhas/partição
# Arquivos < 20MB: Processamento normal
```

## 🐛 Resolução de Problemas

### Erro 502 (Bad Gateway)
- ❌ **Render:** Comum com arquivos > 100MB
- ✅ **Railway:** Raro, melhor infraestrutura

### Timeout de Deploy
- ❌ **Render:** 30 segundos (muito restritivo)
- ✅ **Railway:** Flexível, sem timeouts rígidos

### Memória Insuficiente
- ❌ **Render:** 512MB padrão
- ✅ **Railway:** Até 8GB disponível

## 📱 Monitoramento

### Logs em Tempo Real
```bash
# No painel do Railway
railway logs --follow
```

### Métricas de Performance
- CPU usage
- Memory usage  
- Network I/O
- Response times

## 🔒 Segurança

- ✅ HTTPS automático
- ✅ Variáveis de ambiente seguras
- ✅ Isolamento de containers
- ✅ Backups automáticos

## 🎉 Resultado Final

Após o deploy, sua aplicação estará disponível em:
```
https://seu-projeto.railway.app
```

**Suporte completo para:**
- ✅ Arquivos até 500MB
- ✅ creditcard.csv (143.8MB) 
- ✅ Processamento rápido
- ✅ Interface responsiva
- ✅ Sem erros 502

---

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs no Railway
2. Confirme as variáveis de ambiente
3. Teste localmente primeiro
4. Contate o suporte do Railway (excelente!)

**Railway > Render para arquivos grandes! 🚂💨**