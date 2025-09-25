import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from csv_agent import CSVAgent
from data_analyzer import DataAnalyzer
from visualization import DataVisualizer
import os
from io import StringIO
import traceback
import matplotlib
import tempfile

# Configurações para produção (Render)
matplotlib.use('Agg')  # Backend não-interativo para matplotlib
os.environ['MPLBACKEND'] = 'Agg'

# Configurar diretório temporário para matplotlib
temp_dir = tempfile.mkdtemp()
os.environ['MPLCONFIGDIR'] = temp_dir

# Configuração da página
st.set_page_config(
    page_title="Agente de Análise CSV",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e8b57;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .conclusion-box {
        background-color: #f0f8e8;
        padding: 1rem;
        border-left: 4px solid #2e8b57;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Inicializa variáveis de sessão"""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'insights_generated' not in st.session_state:
        st.session_state.insights_generated = False
    if 'visualization_cache' not in st.session_state:
        st.session_state.visualization_cache = {}

def load_csv_file(uploaded_file):
    """Carrega arquivo CSV"""
    try:
        st.info(f"🔍 Processando arquivo: {uploaded_file.name}")
        st.info(f"📊 Tamanho do arquivo: {uploaded_file.size} bytes")
        
        # Ler o arquivo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.info(f"✅ Arquivo lido com sucesso! Shape: {df.shape}")
            st.info(f"📋 Colunas: {list(df.columns)}")
        else:
            st.error("Por favor, faça upload de um arquivo CSV.")
            return None
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        st.error(f"Detalhes: {traceback.format_exc()}")
        return None

def display_dataset_overview(df):
    """Exibe visão geral do dataset"""
    st.markdown('<div class="section-header">📋 Visão Geral do Dataset</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Linhas", f"{len(df):,}")
    with col2:
        st.metric("Colunas", len(df.columns))
    with col3:
        st.metric("Valores Faltantes", f"{df.isnull().sum().sum():,}")
    with col4:
        st.metric("Tamanho (MB)", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f}")
    
    # Informações das colunas
    st.markdown("**Informações das Colunas:**")
    col_info = pd.DataFrame({
        'Coluna': df.columns,
        'Tipo': df.dtypes.astype(str),
        'Valores Únicos': [df[col].nunique() for col in df.columns],
        'Valores Faltantes': [df[col].isnull().sum() for col in df.columns],
        '% Faltantes': [f"{(df[col].isnull().sum() / len(df)) * 100:.1f}%" for col in df.columns]
    })
    st.dataframe(col_info, use_container_width=True)
    
    # Amostra dos dados
    st.markdown("**Amostra dos Dados:**")
    st.dataframe(df.head(10), use_container_width=True)

def display_automatic_analysis(agent):
    """Exibe análise automática do dataset"""
    st.markdown('<div class="section-header">🔍 Análise Automática</div>', unsafe_allow_html=True)
    
    try:
        overview = agent.get_dataset_overview()
        
        if 'data_quality' in overview:
            quality = overview['data_quality']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Qualidade dos Dados:**")
                st.metric("Completude dos Dados", f"{quality.get('data_completeness', 0):.1f}%")
                st.metric("Linhas Duplicadas", quality.get('duplicate_rows', 0))
            
            with col2:
                st.markdown("**Distribuição de Tipos:**")
                if agent.analyzer:
                    st.metric("Colunas Numéricas", len(agent.analyzer.numeric_columns))
                    st.metric("Colunas Categóricas", len(agent.analyzer.categorical_columns))
        
        # Gerar insights automáticos
        if not st.session_state.insights_generated:
            with st.spinner("Gerando insights automáticos..."):
                insights = agent.generate_insights()
                if insights:
                    st.markdown("**Insights Automáticos:**")
                    for i, insight in enumerate(insights, 1):
                        st.markdown(f'<div class="insight-box"><strong>Insight {i}:</strong> {insight}</div>', 
                                  unsafe_allow_html=True)
                st.session_state.insights_generated = True
    
    except Exception as e:
        st.error(f"Erro na análise automática: {str(e)}")

def display_visualizations(agent):
    """Exibe visualizações automáticas"""
    st.markdown('<div class="section-header">📊 Visualizações Automáticas</div>', unsafe_allow_html=True)
    
    try:
        if agent.visualizer:
            # Visão geral do dashboard
            info_text, figs = agent.visualizer.create_dashboard_overview()
            
            st.markdown(info_text)
            
            # Exibir gráficos
            for i, fig in enumerate(figs):
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"dashboard_chart_{i}")
                    
                    # Limitar número de gráficos para não sobrecarregar
                    if i >= 3:
                        break
    
    except Exception as e:
        st.error(f"Erro ao gerar visualizações: {str(e)}")

def handle_user_question(agent, question):
    """Processa pergunta do usuário"""
    try:
        # Verificar cache de visualizações
        question_hash = hash(question.lower().strip())
        if question_hash in st.session_state.visualization_cache:
            response, visualization = st.session_state.visualization_cache[question_hash]
            st.info("📋 Resposta recuperada do cache (mais rápido!)")
        else:
            with st.spinner("Analisando sua pergunta..."):
                response, visualization = agent.ask_question(question)
                # Salvar no cache
                st.session_state.visualization_cache[question_hash] = (response, visualization)
        
        # Exibir resposta
        st.markdown("**Resposta:**")
        st.write(response)
        
        # Exibir visualização se disponível
        if visualization:
            st.markdown("**Visualização:**")
            import time
            st.plotly_chart(visualization, use_container_width=True, key=f"question_chart_{int(time.time() * 1000)}")
        else:
            st.info("ℹ️ Nenhuma visualização foi gerada para esta pergunta.")
        
        # Adicionar ao histórico
        st.session_state.analysis_history.append({
            'question': question,
            'response': response,
            'has_visualization': visualization is not None
        })
        
        return True
    
    except Exception as e:
        st.error(f"Erro ao processar pergunta: {str(e)}")
        st.error(f"Detalhes: {traceback.format_exc()}")
        return False

def display_conclusions(agent):
    """Exibe conclusões do agente"""
    st.markdown('<div class="section-header">💡 Conclusões do Agente</div>', unsafe_allow_html=True)
    
    try:
        conclusions = agent.generate_conclusions()
        
        if conclusions:
            for i, conclusion in enumerate(conclusions, 1):
                st.markdown(f'<div class="conclusion-box"><strong>Conclusão {i}:</strong> {conclusion}</div>', 
                          unsafe_allow_html=True)
        else:
            st.info("Faça algumas perguntas para que o agente possa gerar conclusões baseadas nas análises.")
    
    except Exception as e:
        st.error(f"Erro ao gerar conclusões: {str(e)}")

def main():
    """Função principal da aplicação"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🤖 Agente Inteligente de Análise CSV</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Upload de arquivo
        st.subheader("📁 Upload de Arquivo")
        uploaded_file = st.file_uploader(
            "Escolha um arquivo CSV",
            type=['csv'],
            help="Faça upload de um arquivo CSV para análise"
        )
        
        # Configuração da API
        st.subheader("🔑 Configuração da API")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Insira sua chave da API OpenAI"
        )
        
        if st.button("🔄 Reiniciar Sessão"):
            st.session_state.clear()
            st.rerun()
    
    # Verificar se API key está configurada
    effective_api_key = api_key or os.getenv("OPENAI_API_KEY")
    
    # Validar se a API key tem formato válido (começa com sk-)
    def is_valid_key(key):
        return key and key.startswith("sk-") and len(key) > 20
    
    # Configurar agente com API key ou modo demonstração (apenas se não existir)
    if st.session_state.agent is None:
        if effective_api_key and is_valid_key(effective_api_key):
            try:
                st.session_state.agent = CSVAgent(api_key=effective_api_key)
                st.success("✅ API Key configurada com sucesso!")
            except Exception as e:
                st.warning(f"⚠️ Erro ao conectar com OpenAI: {str(e)}")
                st.info("🎯 Ativando modo de demonstração...")
                st.session_state.agent = CSVAgent(demo_mode=True)
        else:
            if effective_api_key:
                st.warning("⚠️ API Key inválida. Ativando modo de demonstração...")
            else:
                st.info("ℹ️ API Key não configurada. Ativando modo de demonstração...")
            st.session_state.agent = CSVAgent(demo_mode=True)
    
    # Processar upload de arquivo (apenas se for um arquivo novo)
    if uploaded_file is not None:
        # Verificar se é um arquivo novo
        current_file_info = f"{uploaded_file.name}_{uploaded_file.size}"
        if 'current_file_info' not in st.session_state or st.session_state.current_file_info != current_file_info:
            st.info(f"📁 Arquivo detectado: {uploaded_file.name}")
            df = load_csv_file(uploaded_file)
            
            if df is not None:
                st.success(f"✅ CSV carregado com sucesso! Shape: {df.shape}")
                st.session_state.df = df
                st.session_state.current_file_info = current_file_info
                
                # Carregar dados no agente se já inicializado
                if st.session_state.agent is not None:
                    try:
                        with st.spinner("Carregando dados no agente..."):
                            st.session_state.agent.load_csv(df=df)
                            st.success("✅ Dados carregados no agente com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao carregar dados no agente: {str(e)}")
                        st.error(f"Detalhes: {traceback.format_exc()}")
            else:
                st.error("❌ Erro ao carregar o arquivo CSV")
    
    # Interface principal
    if st.session_state.df is not None:
        
        # Tabs para organizar conteúdo
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Visão Geral", 
            "🔍 Análise Automática", 
            "📊 Visualizações", 
            "❓ Perguntas", 
            "💡 Conclusões"
        ])
        
        with tab1:
            display_dataset_overview(st.session_state.df)
        
        with tab2:
            if st.session_state.agent is not None:
                display_automatic_analysis(st.session_state.agent)
            else:
                st.warning("⚠️ Funcionalidade requer agente inicializado com API key válida")
        
        with tab3:
            if st.session_state.agent is not None:
                display_visualizations(st.session_state.agent)
            else:
                st.warning("⚠️ Funcionalidade requer agente inicializado com API key válida")
        
        with tab4:
            st.markdown('<div class="section-header">❓ Faça Perguntas sobre os Dados</div>', unsafe_allow_html=True)
            
            if st.session_state.agent is not None:
                # Exemplos de perguntas
                st.markdown("**Exemplos de perguntas que você pode fazer:**")
                examples = [
                    "Qual a distribuição da variável Class?",
                    "Existem correlações fortes entre as variáveis?",
                    "Quais são os outliers na coluna Amount?",
                    "Qual a média e mediana de cada variável numérica?",
                    "Existem padrões temporais nos dados?",
                    "Quais são as principais características do dataset?"
                ]
                
                for example in examples:
                    if st.button(f"💡 {example}", key=f"example_{hash(example)}"):
                        handle_user_question(st.session_state.agent, example)
                
                st.markdown("---")
                
                # Input para pergunta personalizada
                user_question = st.text_input(
                    "Sua pergunta:",
                    placeholder="Digite sua pergunta sobre os dados...",
                    key="user_question"
                )
                
                if st.button("🚀 Analisar", type="primary"):
                    if user_question:
                        handle_user_question(st.session_state.agent, user_question)
                    else:
                        st.warning("Por favor, digite uma pergunta.")
                
                # Histórico de perguntas
                if st.session_state.analysis_history:
                    st.markdown("---")
                    st.markdown("**📚 Histórico de Análises:**")
                    
                    for i, item in enumerate(reversed(st.session_state.analysis_history[-5:]), 1):
                        with st.expander(f"Pergunta {len(st.session_state.analysis_history) - i + 1}: {item['question'][:50]}..."):
                            st.write(f"**Pergunta:** {item['question']}")
                            st.write(f"**Resposta:** {item['response']}")
                            if item['has_visualization']:
                                st.write("📊 *Visualização gerada*")
            else:
                st.warning("⚠️ Funcionalidade requer agente inicializado com API key válida")
                st.info("Configure uma API key válida da OpenAI para usar as funcionalidades de IA")
        
        with tab5:
            if st.session_state.agent is not None:
                display_conclusions(st.session_state.agent)
            else:
                st.warning("⚠️ Funcionalidade requer agente inicializado com API key válida")
    
    else:
        # Tela inicial
        st.markdown("""
        ## 🚀 Bem-vindo ao Agente de Análise CSV!
        
        Este agente inteligente pode analisar qualquer arquivo CSV e responder perguntas sobre seus dados.
        
        ### 🎯 Funcionalidades:
        - **Análise Exploratória Automática**: Estatísticas, distribuições, correlações
        - **Detecção de Outliers**: Identificação de valores atípicos
        - **Visualizações Interativas**: Gráficos automáticos baseados nas perguntas
        - **Processamento de Linguagem Natural**: Faça perguntas em português
        - **Sistema de Memória**: O agente lembra das análises anteriores
        - **Geração de Insights**: Conclusões automáticas sobre os dados
        
        ### 📝 Como usar:
        1. Configure sua OpenAI API Key na barra lateral
        2. Faça upload de um arquivo CSV
        3. Explore as análises automáticas
        4. Faça perguntas sobre os dados
        5. Veja as conclusões geradas pelo agente
        
        ### 🔧 Configuração:
        - Crie um arquivo `.env` com sua `OPENAI_API_KEY`
        - Ou insira a chave diretamente na barra lateral
        """)

if __name__ == "__main__":
    main()