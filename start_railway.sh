#!/bin/bash

# Script de inicialização para Railway
echo "🚂 Iniciando aplicação no Railway..."

# Configurar variáveis de ambiente para Railway
export PYTHONUNBUFFERED=1
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=500
export STREAMLIT_SERVER_MAX_MESSAGE_SIZE=500
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_ENABLE_CORS=false
export MPLBACKEND=Agg
export PIP_NO_CACHE_DIR=1

# Verificar memória disponível
echo "💾 Verificando recursos do sistema..."
free -h 2>/dev/null || echo "Sistema Windows detectado"

# Configurar porta do Railway
PORT=${PORT:-8080}
echo "🌐 Porta configurada: $PORT"

# Iniciar aplicação com configurações otimizadas para Railway
echo "🚀 Iniciando Streamlit com suporte a arquivos de 500MB..."

streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.maxUploadSize=500 \
    --server.maxMessageSize=500 \
    --browser.gatherUsageStats=false \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false