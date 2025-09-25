#!/bin/bash

# Script de inicialização para Render
echo "🚀 Iniciando AI CSV Analyzer no Render..."

# Verificar se as variáveis de ambiente estão configuradas
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERRO: OPENAI_API_KEY não configurada!"
    echo "Configure a variável de ambiente no painel do Render."
    exit 1
fi

echo "✅ Variáveis de ambiente verificadas"

# Criar diretórios necessários
mkdir -p /tmp/streamlit
mkdir -p /tmp/matplotlib

echo "✅ Diretórios temporários criados"

# Configurar matplotlib para usar backend não-interativo
export MPLBACKEND=Agg

# Configurar cache do matplotlib
export MPLCONFIGDIR=/tmp/matplotlib

echo "✅ Configurações de matplotlib aplicadas"

# Iniciar aplicação Streamlit
echo "🌟 Iniciando Streamlit..."
streamlit run app.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --server.fileWatcherType=none \
    --browser.gatherUsageStats=false