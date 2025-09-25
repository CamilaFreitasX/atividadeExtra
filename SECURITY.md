# 🔒 GUIA DE SEGURANÇA - Sistema de Análise CSV com IA

## ⚠️ INFORMAÇÕES CRÍTICAS DE SEGURANÇA

### 🚨 ANTES DE FAZER QUALQUER COMMIT

**NUNCA commite os seguintes arquivos:**
- `.env` (contém chaves API reais)
- `agent_memory.json` (pode conter dados sensíveis)
- Qualquer arquivo com dados pessoais ou confidenciais

### 📋 CHECKLIST DE SEGURANÇA

Antes de fazer upload para o GitHub, verifique:

- [ ] ✅ Arquivo `.env` está no `.gitignore`
- [ ] ✅ Chaves API foram removidas do código
- [ ] ✅ Arquivo `.env.example` está atualizado
- [ ] ✅ Dados sensíveis foram removidos
- [ ] ✅ Logs não contêm informações pessoais

---

## 🔧 CONFIGURAÇÃO SEGURA

### 1. Configuração da API Key

**❌ NUNCA faça isso:**
```python
# ERRADO - chave hardcoded no código
api_key = "sk-proj-abc123..."
```

**✅ Forma correta:**
```python
# CORRETO - usando variável de ambiente
api_key = os.getenv("OPENAI_API_KEY")
```

### 2. Arquivo .env

**Estrutura do arquivo `.env` (NÃO commitar):**
```env
# ATENÇÃO: Este arquivo contém informações sensíveis
OPENAI_API_KEY=sua_chave_real_aqui
```

**Arquivo `.env.example` (pode ser commitado):**
```env
# Exemplo de configuração - substitua pelos valores reais
OPENAI_API_KEY=sua_chave_openai_aqui
```

---

## 🛡️ PRÁTICAS DE SEGURANÇA IMPLEMENTADAS

### 1. Proteção de Chaves API
- ✅ Uso de variáveis de ambiente
- ✅ Validação de chaves antes do uso
- ✅ Modo demo quando chave não disponível
- ✅ Nunca exibir chaves nos logs

### 2. Proteção de Dados
- ✅ Cache local apenas (não persistente)
- ✅ Dados de exemplo são públicos
- ✅ Memória do agente pode ser limpa
- ✅ Sem armazenamento de dados pessoais

### 3. Controle de Acesso
- ✅ Interface web local apenas
- ✅ Sem autenticação externa necessária
- ✅ Processamento local dos dados
- ✅ Sem envio de dados para serviços externos (exceto OpenAI)

---

## 🚀 INSTRUÇÕES PARA DEPLOYMENT SEGURO

### Para GitHub Público:

1. **Verificar .gitignore:**
   ```bash
   git status
   # Verificar se .env NÃO aparece na lista
   ```

2. **Testar sem chave API:**
   - Sistema deve funcionar em modo demo
   - Não deve quebrar sem API key

3. **Documentar configuração:**
   - README com instruções claras
   - .env.example atualizado

### Para Uso Local:

1. **Clonar repositório:**
   ```bash
   git clone https://github.com/CamilaFreitasX/atividadeExtra
   cd atividadeExtra
   ```

2. **Configurar ambiente:**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Editar .env com sua chave real
   ```

3. **Executar aplicação:**
   ```bash
   streamlit run app.py
   ```

---

## 🔍 AUDITORIA DE SEGURANÇA

### Comandos para verificar segurança:

```bash
# Verificar se há chaves API no código
grep -r "sk-" . --exclude-dir=.git

# Verificar arquivos que serão commitados
git status

# Verificar se .env está sendo ignorado
git check-ignore .env
```

### Sinais de alerta:
- ❌ Chaves API visíveis no código
- ❌ Arquivo .env sendo commitado
- ❌ Dados pessoais nos arquivos
- ❌ Logs com informações sensíveis

---

## 📞 EM CASO DE VAZAMENTO

Se você acidentalmente commitou informações sensíveis:

1. **Imediatamente:**
   - Revogue a chave API na OpenAI
   - Gere uma nova chave

2. **Limpar histórico:**
   ```bash
   # Remover arquivo do histórico do Git
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch .env' \
   --prune-empty --tag-name-filter cat -- --all
   ```

3. **Forçar push:**
   ```bash
   git push origin --force --all
   ```

---

## ✅ VERIFICAÇÃO FINAL

Antes do upload final, confirme:

- [ ] Sistema funciona sem chave API (modo demo)
- [ ] Arquivo .env não está sendo commitado
- [ ] Documentação está completa
- [ ] Não há dados sensíveis no código
- [ ] .gitignore está configurado corretamente

---

## 📚 RECURSOS ADICIONAIS

- [Guia de Segurança do GitHub](https://docs.github.com/en/code-security)
- [Boas Práticas OpenAI](https://platform.openai.com/docs/guides/safety-best-practices)
- [Segurança em Python](https://python-security.readthedocs.io/)

**Lembre-se: A segurança é responsabilidade de todos! 🔒**