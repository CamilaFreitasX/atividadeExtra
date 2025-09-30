#!/bin/bash

# Script de inicialização otimizado para o Render
echo "🚀 Iniciando AI CSV Analyzer (Otimizado para arquivos grandes)..."

# Configurar variáveis de ambiente para performance
export PYTHONUNBUFFERED=1
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
export STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_ENABLE_CORS=false

# Verificar se as dependências estão instaladas
echo "📦 Verificando dependências..."
python -c "import streamlit, pandas, openai, plotly" || {
    echo "❌ Erro: Dependências não encontradas. Instalando..."
    pip install -r requirements.txt
}

# Verificar variáveis de ambiente
echo "🔑 Verificando configuração..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ Aviso: OPENAI_API_KEY não configurada"
fi

# Verificar memória disponível
echo "💾 Verificando recursos do sistema..."
python -c "
import psutil
mem = psutil.virtual_memory()
print(f'Memória disponível: {mem.available / (1024**3):.1f}GB de {mem.total / (1024**3):.1f}GB')
"

# Criar diretórios necessários
mkdir -p /tmp/streamlit
mkdir -p /tmp/matplotlib

echo "✅ Diretórios temporários criados"

# Configurar matplotlib para usar backend não-interativo
export MPLBACKEND=Agg

# Configurar cache do matplotlib
export MPLCONFIGDIR=/tmp/matplotlib

echo "✅ Configurações de matplotlib aplicadas"

# Iniciar aplicação com configurações otimizadas
echo "✅ Iniciando aplicação com suporte a arquivos de até 200MB..."
streamlit run app.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.maxUploadSize=200 \
    --server.maxMessageSize=200 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --server.fileWatcherType=none \
    --browser.gatherUsageStats=false