import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

class DataAnalyzer:
    """Classe responsável pela análise exploratória de dados CSV"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.analysis_results = {}
    
    def get_basic_info(self):
        """Retorna informações básicas sobre o dataset"""
        info = {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'numeric_columns': self.numeric_columns,
            'categorical_columns': self.categorical_columns,
            'missing_values': self.df.isnull().sum().to_dict(),
            'data_types': self.df.dtypes.to_dict()
        }
        self.analysis_results['basic_info'] = info
        return info
    
    def get_descriptive_statistics(self):
        """Calcula estatísticas descritivas para variáveis numéricas"""
        if not self.numeric_columns:
            return "Nenhuma coluna numérica encontrada no dataset."
        
        stats_dict = {}
        for col in self.numeric_columns:
            stats_dict[col] = {
                'count': self.df[col].count(),
                'mean': self.df[col].mean(),
                'median': self.df[col].median(),
                'std': self.df[col].std(),
                'var': self.df[col].var(),
                'min': self.df[col].min(),
                'max': self.df[col].max(),
                'q25': self.df[col].quantile(0.25),
                'q75': self.df[col].quantile(0.75),
                'skewness': self.df[col].skew(),
                'kurtosis': self.df[col].kurtosis()
            }
        
        self.analysis_results['descriptive_stats'] = stats_dict
        return stats_dict
    
    def detect_outliers(self, method='iqr'):
        """Detecta outliers usando método IQR ou Z-score"""
        outliers_info = {}
        
        for col in self.numeric_columns:
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
            
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(self.df[col].dropna()))
                outliers = self.df[z_scores > 3]
            
            outliers_info[col] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(self.df)) * 100,
                'values': outliers[col].tolist() if len(outliers) < 20 else outliers[col].head(20).tolist()
            }
        
        self.analysis_results['outliers'] = outliers_info
        return outliers_info
    
    def calculate_correlations(self):
        """Calcula matriz de correlação para variáveis numéricas"""
        if len(self.numeric_columns) < 2:
            return "Necessário pelo menos 2 colunas numéricas para calcular correlações."
        
        correlation_matrix = self.df[self.numeric_columns].corr()
        
        # Encontra correlações mais fortes
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.5:  # Correlação considerada forte
                    strong_correlations.append({
                        'var1': correlation_matrix.columns[i],
                        'var2': correlation_matrix.columns[j],
                        'correlation': corr_value
                    })
        
        correlation_info = {
            'matrix': correlation_matrix.to_dict(),
            'strong_correlations': strong_correlations
        }
        
        self.analysis_results['correlations'] = correlation_info
        return correlation_info
    
    def analyze_categorical_variables(self):
        """Analisa variáveis categóricas"""
        if not self.categorical_columns:
            return "Nenhuma variável categórica encontrada."
        
        categorical_analysis = {}
        for col in self.categorical_columns:
            value_counts = self.df[col].value_counts()
            categorical_analysis[col] = {
                'unique_values': self.df[col].nunique(),
                'most_frequent': value_counts.index[0] if len(value_counts) > 0 else None,
                'most_frequent_count': value_counts.iloc[0] if len(value_counts) > 0 else 0,
                'value_counts': value_counts.head(10).to_dict()
            }
        
        self.analysis_results['categorical_analysis'] = categorical_analysis
        return categorical_analysis
    
    def detect_patterns_and_trends(self):
        """Detecta padrões e tendências nos dados"""
        patterns = {}
        
        # Análise temporal se houver coluna de tempo
        time_columns = [col for col in self.df.columns if 'time' in col.lower() or 'date' in col.lower()]
        if time_columns:
            patterns['temporal_analysis'] = f"Colunas temporais detectadas: {time_columns}"
        
        # Clustering simples para detectar agrupamentos
        if len(self.numeric_columns) >= 2:
            # Preparar dados para clustering
            data_for_clustering = self.df[self.numeric_columns].dropna()
            if len(data_for_clustering) > 10:
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(data_for_clustering)
                
                # K-means com 3 clusters
                kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(scaled_data)
                
                patterns['clustering'] = {
                    'n_clusters': 3,
                    'cluster_sizes': np.bincount(clusters).tolist(),
                    'inertia': kmeans.inertia_
                }
        
        self.analysis_results['patterns'] = patterns
        return patterns
    
    def generate_comprehensive_analysis(self):
        """Gera análise completa do dataset"""
        analysis = {
            'basic_info': self.get_basic_info(),
            'descriptive_stats': self.get_descriptive_statistics(),
            'outliers': self.detect_outliers(),
            'correlations': self.calculate_correlations(),
            'categorical_analysis': self.analyze_categorical_variables(),
            'patterns': self.detect_patterns_and_trends()
        }
        
        return analysis
    
    def get_data_quality_report(self):
        """Gera relatório de qualidade dos dados"""
        total_rows = len(self.df)
        missing_data = self.df.isnull().sum()
        
        quality_report = {
            'total_rows': total_rows,
            'total_columns': len(self.df.columns),
            'missing_data_percentage': (missing_data.sum() / (total_rows * len(self.df.columns))) * 100,
            'columns_with_missing_data': missing_data[missing_data > 0].to_dict(),
            'duplicate_rows': self.df.duplicated().sum(),
            'data_completeness': ((total_rows * len(self.df.columns) - missing_data.sum()) / (total_rows * len(self.df.columns))) * 100
        }
        
        return quality_report