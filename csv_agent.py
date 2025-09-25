import pandas as pd
import numpy as np
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
import re
from typing import Dict, List, Any, Tuple
from data_analyzer import DataAnalyzer
from visualization import DataVisualizer
from memory_system import MemorySystem

# Carregar variáveis de ambiente
load_dotenv()

class CSVAgent:
    """Agente inteligente para análise de dados CSV usando LangChain"""
    
    def __init__(self, api_key: str = None, demo_mode: bool = False):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.demo_mode = demo_mode
        
        # Inicializar componentes
        if demo_mode or not self.api_key or not self.api_key.startswith("sk-"):
            print("Modo de demonstração ativado - usando respostas simuladas")
            self.llm = None
            self.test_mode = True
        else:
            try:
                self.llm = ChatOpenAI(
                    openai_api_key=self.api_key,
                    model_name=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
                    temperature=float(os.getenv("TEMPERATURE", "0.1"))
                )
                self.test_mode = False
                print("Modo OpenAI ativado com sucesso")
            except Exception as e:
                print(f"Erro ao conectar com OpenAI, ativando modo de demonstração: {e}")
                self.llm = None
                self.test_mode = True
        
        self.memory_system = MemorySystem()
        self.conversation_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.df = None
        self.analyzer = None
        self.visualizer = None
        self.session_id = None
        self.analysis_cache = {}
        
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Configura os prompts para diferentes tipos de análise"""
        
        # Prompt principal para análise de dados
        self.analysis_prompt = PromptTemplate(
            input_variables=["question", "dataset_info", "context", "analysis_results"],
            template="""
            Você é um especialista em análise de dados e ciência de dados. Você está analisando um dataset CSV.

            INFORMAÇÕES DO DATASET:
            {dataset_info}

            CONTEXTO DE ANÁLISES ANTERIORES:
            {context}

            RESULTADOS DE ANÁLISE DISPONÍVEIS:
            {analysis_results}

            PERGUNTA DO USUÁRIO:
            {question}

            INSTRUÇÕES:
            1. Analise a pergunta do usuário e determine que tipo de análise é necessária
            2. Use os resultados de análise disponíveis para responder
            3. Seja específico e técnico, mas mantenha a linguagem acessível
            4. Se necessário, sugira visualizações que seriam úteis
            5. Identifique insights importantes e padrões nos dados
            6. Se a pergunta for sobre conclusões, sintetize os principais achados

            RESPOSTA:
            """
        )
        
        # Prompt para geração de insights
        self.insight_prompt = PromptTemplate(
            input_variables=["analysis_summary", "dataset_info"],
            template="""
            Baseado na análise completa do dataset, gere insights importantes e conclusões.

            INFORMAÇÕES DO DATASET:
            {dataset_info}

            RESUMO DAS ANÁLISES:
            {analysis_summary}

            Gere 3-5 insights principais sobre os dados, incluindo:
            1. Características gerais do dataset
            2. Padrões identificados
            3. Anomalias ou outliers importantes
            4. Relações entre variáveis
            5. Recomendações para análises futuras

            INSIGHTS:
            """
        )
    
    def load_csv(self, file_path: str = None, df: pd.DataFrame = None) -> bool:
        """Carrega arquivo CSV ou DataFrame"""
        try:
            if df is not None:
                self.df = df.copy()
            elif file_path:
                self.df = pd.read_csv(file_path)
            else:
                return False
            
            # Inicializar componentes de análise
            self.analyzer = DataAnalyzer(self.df)
            self.visualizer = DataVisualizer(self.df)
            
            # Criar sessão na memória
            self.session_id = f"session_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
            dataset_info = {
                "shape": self.df.shape,
                "columns": list(self.df.columns),
                "dtypes": self.df.dtypes.to_dict()
            }
            self.memory_system.create_session(self.session_id, dataset_info)
            
            # Executar análise inicial
            self._perform_initial_analysis()
            
            return True
            
        except Exception as e:
            print(f"Erro ao carregar CSV: {e}")
            return False
    
    def _perform_initial_analysis(self):
        """Executa análise inicial do dataset"""
        if self.analyzer is None:
            return
        
        # Análise básica
        basic_info = self.analyzer.get_basic_info()
        self.analysis_cache['basic_info'] = basic_info
        
        # Estatísticas descritivas
        desc_stats = self.analyzer.get_descriptive_statistics()
        self.analysis_cache['descriptive_stats'] = desc_stats
        
        # Detecção de outliers
        outliers = self.analyzer.detect_outliers()
        self.analysis_cache['outliers'] = outliers
        
        # Correlações
        correlations = self.analyzer.calculate_correlations()
        self.analysis_cache['correlations'] = correlations
        
        # Análise categórica
        categorical = self.analyzer.analyze_categorical_variables()
        self.analysis_cache['categorical'] = categorical
        
        # Padrões e tendências
        patterns = self.analyzer.detect_patterns_and_trends()
        self.analysis_cache['patterns'] = patterns
        
        # Salvar na memória
        self.memory_system.add_analysis_result(
            self.session_id, 
            "initial_analysis", 
            self.analysis_cache
        )
    
    def _extract_relevant_columns(self, question: str) -> List[str]:
        """Extrai colunas relevantes baseado na pergunta"""
        question_lower = question.lower()
        relevant_columns = []
        
        # Procurar nomes de colunas na pergunta
        for col in self.df.columns:
            if col.lower() in question_lower:
                relevant_columns.append(col)
        
        # Se não encontrou colunas específicas, usar heurísticas
        if not relevant_columns:
            if any(word in question_lower for word in ['target', 'classe', 'class', 'label']):
                # Procurar coluna target
                target_candidates = ['class', 'target', 'label', 'y']
                for candidate in target_candidates:
                    matching_cols = [col for col in self.df.columns if candidate in col.lower()]
                    relevant_columns.extend(matching_cols)
            
            if any(word in question_lower for word in ['valor', 'amount', 'price', 'cost']):
                amount_candidates = ['amount', 'value', 'price', 'cost']
                for candidate in amount_candidates:
                    matching_cols = [col for col in self.df.columns if candidate in col.lower()]
                    relevant_columns.extend(matching_cols)
        
        return list(set(relevant_columns))
    
    def _determine_analysis_type(self, question: str) -> str:
        """Determina o tipo de análise baseado na pergunta"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['correlação', 'correlation', 'relação', 'relationship']):
            return 'correlation'
        elif any(word in question_lower for word in ['distribuição', 'distribution', 'histograma']):
            return 'distribution'
        elif any(word in question_lower for word in ['outlier', 'atípico', 'anomalia', 'outliers']):
            return 'outliers'
        elif any(word in question_lower for word in ['estatística', 'statistics', 'média', 'mean']):
            return 'statistics'
        elif any(word in question_lower for word in ['categoria', 'categorical', 'categórica']):
            return 'categorical'
        elif any(word in question_lower for word in ['padrão', 'pattern', 'tendência', 'trend']):
            return 'patterns'
        elif any(word in question_lower for word in ['conclusão', 'conclusion', 'insight', 'resumo']):
            return 'conclusions'
        else:
            return 'general'
    
    def ask_question(self, question: str) -> Tuple[str, Any]:
        """Processa pergunta do usuário e retorna resposta com visualização"""
        if self.df is None:
            return "Por favor, carregue um arquivo CSV primeiro.", None
        
        # Extrair informações da pergunta
        relevant_columns = self._extract_relevant_columns(question)
        analysis_type = self._determine_analysis_type(question)
        
        # Obter contexto da memória
        context = self.memory_system.get_relevant_context(question, self.session_id)
        
        # Preparar informações do dataset
        dataset_info = f"""
        Formato: {self.df.shape[0]} linhas, {self.df.shape[1]} colunas
        Colunas: {', '.join(self.df.columns)}
        Tipos de dados: {', '.join([f"{col}: {dtype}" for col, dtype in self.df.dtypes.items()])}
        """
        
        # Preparar resultados de análise
        analysis_results = self._format_analysis_results(analysis_type, relevant_columns)
        
        # Gerar resposta usando LLM ou modo de teste
        if self.test_mode:
            # Análise básica dos dados para resposta mais útil focada nas colunas relevantes
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
            
            # Filtrar colunas baseado nas relevantes identificadas
            if relevant_columns:
                relevant_numeric = [col for col in relevant_columns if col in numeric_cols]
                relevant_categorical = [col for col in relevant_columns if col in categorical_cols]
            else:
                relevant_numeric = numeric_cols[:2]  # Fallback para as primeiras 2
                relevant_categorical = categorical_cols[:2]  # Fallback para as primeiras 2
            
            # Gerar insights básicos baseados na pergunta
            insights = []
            question_lower = question.lower()
            
            # Análises específicas baseadas nas colunas relevantes
            if any(word in question_lower for word in ['média', 'average', 'mean']):
                for col in relevant_numeric:
                    mean_val = self.df[col].mean()
                    insights.append(f"• Média de {col}: {mean_val:.2f}")
            
            if any(word in question_lower for word in ['máximo', 'max', 'maior']):
                for col in relevant_numeric:
                    max_val = self.df[col].max()
                    insights.append(f"• Valor máximo de {col}: {max_val}")
            
            if any(word in question_lower for word in ['mínimo', 'min', 'menor']):
                for col in relevant_numeric:
                    min_val = self.df[col].min()
                    insights.append(f"• Valor mínimo de {col}: {min_val}")
            
            if any(word in question_lower for word in ['distribuição', 'distribution', 'contagem', 'count', 'frequência', 'frequency']):
                for col in relevant_categorical:
                    value_counts = self.df[col].value_counts().head(3)
                    insights.append(f"• Top 3 valores em {col}:")
                    for val, count in value_counts.items():
                        insights.append(f"  - {val}: {count} ocorrências")
                
                # Se não há categóricas relevantes, mas há numéricas, mostrar estatísticas
                if not relevant_categorical and relevant_numeric:
                    for col in relevant_numeric:
                        insights.append(f"• Estatísticas de {col}:")
                        insights.append(f"  - Média: {self.df[col].mean():.2f}")
                        insights.append(f"  - Desvio padrão: {self.df[col].std():.2f}")
            
            if any(word in question_lower for word in ['correlação', 'correlation', 'relação', 'relationship']):
                if len(relevant_numeric) >= 2:
                    corr_matrix = self.df[relevant_numeric].corr()
                    insights.append(f"• Correlações entre variáveis numéricas:")
                    for i, col1 in enumerate(relevant_numeric):
                        for col2 in relevant_numeric[i+1:]:
                            corr_val = corr_matrix.loc[col1, col2]
                            insights.append(f"  - {col1} vs {col2}: {corr_val:.3f}")
                elif len(relevant_numeric) == 1 and len(numeric_cols) > 1:
                    # Se só uma coluna relevante, correlacionar com outras numéricas
                    col1 = relevant_numeric[0]
                    other_numeric = [col for col in numeric_cols if col != col1][:2]
                    for col2 in other_numeric:
                        corr_val = self.df[col1].corr(self.df[col2])
                        insights.append(f"  - {col1} vs {col2}: {corr_val:.3f}")
            
            # Análise específica por coluna mencionada
            if relevant_columns:
                for col in relevant_columns:
                    if col in numeric_cols:
                        insights.append(f"• Análise de {col}:")
                        insights.append(f"  - Valores únicos: {self.df[col].nunique()}")
                        insights.append(f"  - Faixa: {self.df[col].min():.2f} a {self.df[col].max():.2f}")
                    elif col in categorical_cols:
                        insights.append(f"• Análise de {col}:")
                        insights.append(f"  - Categorias únicas: {self.df[col].nunique()}")
                        top_category = self.df[col].value_counts().index[0]
                        insights.append(f"  - Categoria mais frequente: {top_category}")
            
            # Fallback se nenhum insight específico foi gerado
            if not insights:
                if relevant_columns:
                    insights.append(f"• Análise focada em: {', '.join(relevant_columns)}")
                    for col in relevant_columns:
                        if col in numeric_cols:
                            insights.append(f"  - {col}: coluna numérica com {self.df[col].nunique()} valores únicos")
                        elif col in categorical_cols:
                            insights.append(f"  - {col}: coluna categórica com {self.df[col].nunique()} categorias")
                else:
                    insights = [
                        f"• Dataset contém {len(self.df)} registros",
                        f"• {len(numeric_cols)} colunas numéricas disponíveis",
                        f"• {len(categorical_cols)} colunas categóricas disponíveis"
                    ]
            
            response = f"""
            **🎯 Análise de Demonstração**
            
            **Pergunta:** "{question}"
            
            **📊 Insights Encontrados:**
            {chr(10).join(insights)}
            
            **📈 Estatísticas Gerais:**
            - Total de registros: {len(self.df):,}
            - Colunas disponíveis: {len(self.df.columns)}
            - Dados numéricos: {len(numeric_cols)} colunas
            - Dados categóricos: {len(categorical_cols)} colunas
            
            **⚠️ Modo de Demonstração Ativo**
            Esta análise usa algoritmos básicos. Para análises avançadas com IA, 
            configure uma API key válida da OpenAI no arquivo .env
            """
        else:
            chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)
            response = chain.run(
                question=question,
                dataset_info=dataset_info,
                context=context,
                analysis_results=analysis_results
            )
        
        # Gerar visualização automaticamente para TODAS as perguntas
        visualization = None
        if self.visualizer:
            # Sempre gerar visualização para qualquer pergunta
            visualization = self.visualizer.generate_visualization_for_question(
                question, relevant_columns
            )
        
        # Salvar na memória
        self.memory_system.add_question(
            self.session_id, question, response, analysis_type
        )
        
        return response, visualization
    
    def _format_analysis_results(self, analysis_type: str, relevant_columns: List[str]) -> str:
        """Formata resultados de análise para o prompt"""
        results = []
        
        if analysis_type == 'statistics' or analysis_type == 'general':
            if 'descriptive_stats' in self.analysis_cache:
                stats = self.analysis_cache['descriptive_stats']
                if relevant_columns:
                    for col in relevant_columns:
                        if col in stats:
                            results.append(f"Estatísticas de {col}: {stats[col]}")
                else:
                    results.append(f"Estatísticas descritivas disponíveis para: {list(stats.keys())}")
        
        if analysis_type == 'correlation':
            if 'correlations' in self.analysis_cache:
                corr_info = self.analysis_cache['correlations']
                if 'strong_correlations' in corr_info:
                    results.append(f"Correlações fortes encontradas: {corr_info['strong_correlations']}")
        
        if analysis_type == 'outliers':
            if 'outliers' in self.analysis_cache:
                outliers_info = self.analysis_cache['outliers']
                if relevant_columns:
                    for col in relevant_columns:
                        if col in outliers_info:
                            results.append(f"Outliers em {col}: {outliers_info[col]}")
                else:
                    results.append(f"Informações de outliers: {outliers_info}")
        
        if analysis_type == 'categorical':
            if 'categorical' in self.analysis_cache:
                cat_info = self.analysis_cache['categorical']
                results.append(f"Análise categórica: {cat_info}")
        
        if analysis_type == 'patterns':
            if 'patterns' in self.analysis_cache:
                patterns_info = self.analysis_cache['patterns']
                results.append(f"Padrões identificados: {patterns_info}")
        
        return "\\n".join(results) if results else "Análise básica do dataset disponível."
    
    def generate_insights(self) -> List[str]:
        """Gera insights automáticos sobre o dataset"""
        if self.df is None:
            return []
        
        # Preparar resumo das análises
        analysis_summary = f"""
        Dataset com {self.df.shape[0]} registros e {self.df.shape[1]} variáveis.
        Análises realizadas: {list(self.analysis_cache.keys())}
        Colunas numéricas: {len(self.analyzer.numeric_columns)}
        Colunas categóricas: {len(self.analyzer.categorical_columns)}
        """
        
        dataset_info = f"Colunas: {', '.join(self.df.columns)}"
        
        # Gerar insights usando LLM ou modo de teste
        if self.test_mode:
            insights_text = f"""
            [MODO DE TESTE] Insights automáticos:
            1. Dataset contém {self.df.shape[0]} registros e {self.df.shape[1]} variáveis
            2. Análises disponíveis: {list(self.analysis_cache.keys())}
            3. Variáveis numéricas: {len(self.analyzer.numeric_columns)}
            4. Variáveis categóricas: {len(self.analyzer.categorical_columns)}
            5. Esta é uma análise simulada para demonstração
            """
        else:
            chain = LLMChain(llm=self.llm, prompt=self.insight_prompt)
            insights_text = chain.run(
                analysis_summary=analysis_summary,
                dataset_info=dataset_info
            )
        
        # Processar insights
        insights = [insight.strip() for insight in insights_text.split('\\n') if insight.strip()]
        
        # Salvar insights na memória
        for insight in insights:
            self.memory_system.add_insight(self.session_id, insight)
        
        return insights
    
    def generate_conclusions(self) -> List[str]:
        """Gera conclusões baseadas em todas as análises realizadas"""
        if self.session_id is None:
            return []
        
        # Conclusões automáticas baseadas na memória
        auto_conclusions = self.memory_system.generate_session_conclusions(self.session_id)
        
        # Conclusões baseadas nos dados
        data_conclusions = []
        
        if 'correlations' in self.analysis_cache:
            corr_info = self.analysis_cache['correlations']
            if isinstance(corr_info, dict) and 'strong_correlations' in corr_info:
                strong_corrs = corr_info['strong_correlations']
                if strong_corrs:
                    data_conclusions.append(
                        f"Identificadas {len(strong_corrs)} correlações fortes entre variáveis, "
                        f"indicando relacionamentos significativos nos dados."
                    )
        
        if 'outliers' in self.analysis_cache:
            outliers_info = self.analysis_cache['outliers']
            if isinstance(outliers_info, dict):
                total_outliers = sum(info.get('count', 0) for info in outliers_info.values() 
                                   if isinstance(info, dict))
                if total_outliers > 0:
                    data_conclusions.append(
                        f"Detectados {total_outliers} outliers no dataset, "
                        f"que podem representar casos especiais ou erros nos dados."
                    )
        
        all_conclusions = auto_conclusions + data_conclusions
        
        # Salvar conclusões na memória
        for conclusion in all_conclusions:
            self.memory_system.add_conclusion(self.session_id, conclusion)
        
        return all_conclusions
    
    def get_dataset_overview(self) -> Dict:
        """Retorna visão geral do dataset"""
        if self.df is None:
            return {}
        
        return {
            "basic_info": self.analysis_cache.get('basic_info', {}),
            "data_quality": self.analyzer.get_data_quality_report(),
            "session_summary": self.memory_system.get_session_summary(self.session_id)
        }
    
    def reset_session(self):
        """Reinicia a sessão atual"""
        if self.session_id:
            self.memory_system.clear_session(self.session_id)
        self.conversation_memory.clear()
        self.analysis_cache = {}
        self.session_id = None