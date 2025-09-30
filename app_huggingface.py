#!/usr/bin/env python3
"""
🤗 Versão otimizada para Hugging Face Spaces (GRATUITO)
Suporte a creditcard.csv sem erro 502
"""

import streamlit as st
import os

# Configuração específica para Hugging Face Spaces
st.set_page_config(
    page_title="🤖 Analisador CSV com IA - Hugging Face",
    page_icon="🤗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos principais
from app import main

if __name__ == "__main__":
    # Configurações específicas para Hugging Face
    os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', 'true')
    os.environ.setdefault('STREAMLIT_SERVER_MAX_UPLOAD_SIZE', '200')
    os.environ.setdefault('STREAMLIT_BROWSER_GATHER_USAGE_STATS', 'false')
    
    # Executar aplicação principal
    main()