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
    """Carrega arquivo CSV com otimizações para arquivos grandes e prevenção de erro 502"""
    try:
        st.info(f"🔍 Processando arquivo: {uploaded_file.name}")
        
        # Verificar tamanho do arquivo
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.info(f"📊 Tamanho do arquivo: {file_size_mb:.2f}MB")
        
        # Verificações de segurança para evitar erro 502
        if file_size_mb > 20:
            st.error(f"❌ Arquivo muito grande ({file_size_mb:.1f}MB). Limite máximo: 20MB")
            st.info("💡 Para arquivos grandes, use uma amostra representativa dos dados.")
            return None
        
        # Ler o arquivo
        if not uploaded_file.name.endswith('.csv'):
            st.error("❌ Por favor, faça upload de um arquivo CSV.")
            return None
        
        # Processamento inteligente baseado no tamanho
        if file_size_mb > 3:
            st.warning(f"⚠️ Arquivo grande detectado ({file_size_mb:.1f}MB). Aplicando processamento otimizado...")
            
            # Ler amostra primeiro para detectar estrutura
            try:
                sample_df = pd.read_csv(uploaded_file, nrows=500, low_memory=False)
                st.info(f"📋 Estrutura detectada: {sample_df.shape[1]} colunas")
                
                # Resetar ponteiro do arquivo
                uploaded_file.seek(0)
                
                # Ler com otimizações de memória
                df = pd.read_csv(uploaded_file, 
                               low_memory=False,
                               engine='c',  # Engine mais rápida
                               memory_map=True)  # Usar memory mapping
                
                # Limitar linhas para evitar timeout (especialmente no Render)
                max_rows = 3000 if file_size_mb > 5 else 5000
                if len(df) > max_rows:
                    st.warning(f"⚠️ Dataset grande ({len(df):,} linhas). Usando amostra estratificada de {max_rows:,} linhas.")
                    # Amostra estratificada para manter representatividade
                    df = df.sample(n=max_rows, random_state=42).reset_index(drop=True)
                    
            except Exception as e:
                st.error(f"❌ Erro ao processar arquivo grande: {str(e)}")
                return None
        else:
            # Arquivos pequenos - processamento normal
            df = pd.read_csv(uploaded_file, low_memory=False)
        
        st.success(f"✅ Arquivo carregado! Shape: {df.shape}")
        st.info(f"📋 Colunas: {list(df.columns[:8])}{'...' if len(df.columns) > 8 else ''}")
        
        # Otimizar tipos de dados para economizar memória
        original_memory = df.memory_usage(deep=True).sum() / (1024**2)
        
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # Converter para categoria se tiver poucos valores únicos
                    unique_ratio = df[col].nunique() / len(df)
                    if unique_ratio < 0.5 and df[col].nunique() < 1000:
                        df[col] = df[col].astype('category')
                except:
                    pass
            elif df[col].dtype in ['int64', 'float64']:
                try:
                    # Otimizar tipos numéricos
                    if df[col].dtype == 'int64':
                        if df[col].min() >= 0 and df[col].max() <= 255:
                            df[col] = df[col].astype('uint8')
                        elif df[col].min() >= -128 and df[col].max() <= 127:
                            df[col] = df[col].astype('int8')
                        elif df[col].min() >= -32768 and df[col].max() <= 32767:
                            df[col] = df[col].astype('int16')
                        elif df[col].min() >= -2147483648 and df[col].max() <= 2147483647:
                            df[col] = df[col].astype('int32')
                    elif df[col].dtype == 'float64':
                        # Tentar converter para float32 se não houver perda de precisão
                        if df[col].equals(df[col].astype('float32').astype('float64')):
                            df[col] = df[col].astype('float32')
                except:
                    pass
        
        optimized_memory = df.memory_usage(deep=True).sum() / (1024**2)
        reduction = ((original_memory - optimized_memory) / original_memory) * 100
        
        st.info(f"💾 Memória otimizada: {optimized_memory:.1f}MB (redução de {reduction:.1f}%)")
        
        return df
        
    except pd.errors.EmptyDataError:
        st.error("❌ Arquivo CSV está vazio.")
        return None
    except pd.errors.ParserError as e:
        st.error(f"❌ Erro ao analisar CSV: {str(e)}")
        st.info("💡 Verifique se o arquivo está no formato CSV correto.")
        return None
    except MemoryError:
        st.error("❌ Erro de memória: Arquivo muito grande para processar.")
        st.info("💡 Tente usar uma amostra menor do dataset.")
        return None
    except Exception as e:
        st.error(f"❌ Erro inesperado ao carregar arquivo: {str(e)}")
        st.error(f"🔍 Detalhes técnicos: {traceback.format_exc()}")
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
    try:
        initialize_session_state()
        
        # Header
        st.markdown('<div class="main-header">🤖 Agente Inteligente de Análise CSV</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Verificar recursos do sistema (opcional)
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 85:
                st.warning(f"⚠️ Uso de memória alto ({memory_percent:.1f}%). Performance pode ser afetada.")
        except ImportError:
            # psutil não disponível, continuar sem monitoramento
            pass
        except Exception:
            # Erro ao acessar informações do sistema, continuar normalmente
            pass
    
    except Exception as e:
        st.error(f"Erro na inicialização da aplicação: {str(e)}")
        st.error("Tente recarregar a página ou reiniciar a sessão.")
        return
    
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
            
            # Verificar tamanho antes do processamento
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > 20:
                st.error(f"❌ Arquivo muito grande ({file_size_mb:.1f}MB). Limite máximo: 20MB")
                st.info("💡 Para análise de arquivos grandes, use uma amostra representativa dos dados.")
                st.info("🔧 Sugestão: Exporte apenas as primeiras 10.000-20.000 linhas do seu dataset.")
                return
            
            # Mostrar progresso para arquivos grandes
            if file_size_mb > 2:
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("Iniciando processamento...")
            
            try:
                import time
                
                if file_size_mb > 3:
                    st.warning(f"⏱️ Arquivo grande ({file_size_mb:.1f}MB). Aplicando otimizações para evitar timeout.")
                
                start_time = time.time()
                
                # Atualizar progresso
                if file_size_mb > 2:
                    progress_bar.progress(20)
                    status_text.text("Carregando arquivo...")
                
                df = load_csv_file(uploaded_file)
                
                if file_size_mb > 2:
                    progress_bar.progress(80)
                    status_text.text("Finalizando...")
                
                processing_time = time.time() - start_time
                
                if file_size_mb > 2:
                    progress_bar.progress(100)
                    status_text.text("Concluído!")
                    time.sleep(0.5)  # Mostrar conclusão brevemente
                    progress_bar.empty()
                    status_text.empty()
                
                if df is not None:
                    st.success(f"✅ CSV carregado com sucesso! Shape: {df.shape}")
                    st.info(f"⏱️ Tempo de processamento: {processing_time:.2f}s")
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
                    
            except TimeoutError:
                st.error("⏱️ Timeout: Arquivo muito grande para processar. Tente uma amostra menor.")
            except MemoryError:
                st.error("💾 Erro de memória: Arquivo muito grande. Tente uma amostra menor.")
            except Exception as e:
                st.error(f"❌ Erro inesperado ao processar arquivo: {str(e)}")
                st.error("💡 Tente recarregar a página ou usar um arquivo menor.")
    
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