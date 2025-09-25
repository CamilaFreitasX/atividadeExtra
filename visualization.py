import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st
from scipy import stats
from scipy.stats import gaussian_kde
import warnings
warnings.filterwarnings('ignore')

class DataVisualizer:
    """Classe responsável pela geração de visualizações dos dados"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Configurar estilo
        plt.style.use('default')
        sns.set_palette("husl")
    
    def plot_distribution(self, column, plot_type='histogram'):
        """Cria gráfico de distribuição para uma coluna"""
        if column not in self.df.columns:
            return None
        
        if plot_type == 'histogram' and column in self.numeric_columns:
            fig = px.histogram(
                self.df, 
                x=column, 
                title=f'Distribuição de {column}',
                nbins=30,
                marginal="box"
            )
            fig.update_layout(
                xaxis_title=column,
                yaxis_title='Frequência',
                showlegend=False
            )
            return fig
        
        elif plot_type == 'box' and column in self.numeric_columns:
            fig = px.box(
                self.df, 
                y=column, 
                title=f'Box Plot de {column}'
            )
            return fig
        
        elif column in self.categorical_columns:
            value_counts = self.df[column].value_counts().head(20)
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=f'Distribuição de {column}',
                labels={'x': column, 'y': 'Frequência'}
            )
            fig.update_xaxes(tickangle=45)
            return fig
        
        return None
    
    def plot_correlation_matrix(self):
        """Cria heatmap da matriz de correlação"""
        if len(self.numeric_columns) < 2:
            return None
        
        correlation_matrix = self.df[self.numeric_columns].corr()
        
        fig = px.imshow(
            correlation_matrix,
            title='Matriz de Correlação',
            color_continuous_scale='RdBu_r',
            aspect='auto'
        )
        
        fig.update_layout(
            width=800,
            height=600
        )
        
        return fig
    
    def plot_scatter(self, x_col, y_col, color_col=None):
        """Cria gráfico de dispersão"""
        if x_col not in self.numeric_columns or y_col not in self.numeric_columns:
            return None
        
        fig = px.scatter(
            self.df,
            x=x_col,
            y=y_col,
            color=color_col if color_col and color_col in self.df.columns else None,
            title=f'Relação entre {x_col} e {y_col}'
        )
        
        return fig
    
    def plot_numeric_by_categorical(self, numeric_col, categorical_col):
        """Cria box plot de variável numérica por categórica"""
        if numeric_col not in self.numeric_columns or categorical_col not in self.categorical_columns:
            return None
        
        fig = px.box(
            self.df,
            x=categorical_col,
            y=numeric_col,
            title=f'{numeric_col} por {categorical_col}'
        )
        
        return fig
    
    def plot_advanced_scatter(self, x_col, y_col, color_col=None, add_trendline=True, alpha=0.6):
        """Gráfico de dispersão avançado com cor por classe, transparência e linha de tendência"""
        if x_col not in self.df.columns or y_col not in self.df.columns:
            return None
            
        # Criar figura base
        if color_col and color_col in self.df.columns:
            fig = px.scatter(
                self.df, 
                x=x_col, 
                y=y_col, 
                color=color_col,
                title=f'Dispersão Avançada: {y_col} vs {x_col} (por {color_col})',
                opacity=alpha,
                hover_data=[col for col in self.df.columns if col in [x_col, y_col, color_col]]
            )
            
            # Adicionar linha de tendência por classe se solicitado
            if add_trendline:
                for class_val in self.df[color_col].unique():
                    if pd.notna(class_val):
                        class_data = self.df[self.df[color_col] == class_val]
                        if len(class_data) > 1:
                            # Calcular linha de tendência
                            x_vals = class_data[x_col].dropna()
                            y_vals = class_data[y_col].dropna()
                            if len(x_vals) > 1 and len(y_vals) > 1:
                                z = np.polyfit(x_vals, y_vals, 1)
                                p = np.poly1d(z)
                                x_trend = np.linspace(x_vals.min(), x_vals.max(), 100)
                                y_trend = p(x_trend)
                                
                                fig.add_trace(go.Scatter(
                                    x=x_trend,
                                    y=y_trend,
                                    mode='lines',
                                    name=f'Tendência {class_val}',
                                    line=dict(dash='dash'),
                                    showlegend=True
                                ))
        else:
            fig = px.scatter(
                self.df, 
                x=x_col, 
                y=y_col,
                title=f'Dispersão Avançada: {y_col} vs {x_col}',
                opacity=alpha
            )
            
            # Adicionar linha de tendência geral
            if add_trendline:
                x_vals = self.df[x_col].dropna()
                y_vals = self.df[y_col].dropna()
                if len(x_vals) > 1 and len(y_vals) > 1:
                    z = np.polyfit(x_vals, y_vals, 1)
                    p = np.poly1d(z)
                    x_trend = np.linspace(x_vals.min(), x_vals.max(), 100)
                    y_trend = p(x_trend)
                    
                    fig.add_trace(go.Scatter(
                        x=x_trend,
                        y=y_trend,
                        mode='lines',
                        name='Tendência',
                        line=dict(dash='dash'),
                        showlegend=True
                    ))
        
        # Melhorar layout
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            hovermode='closest',
            template='plotly_white'
        )
        
        return fig
    
    def plot_hexbin_density(self, x_col, y_col, color_col=None, gridsize=20):
        """Gráfico Hexbin (2D histogram) para mostrar densidade de pontos"""
        if x_col not in self.df.columns or y_col not in self.df.columns:
            return None
            
        if color_col and color_col in self.df.columns:
            # Criar subplots para cada classe
            classes = self.df[color_col].unique()
            classes = [c for c in classes if pd.notna(c)]
            
            if len(classes) <= 4:  # Máximo 4 classes para visualização clara
                # Calcular layout de subplots
                if len(classes) == 1:
                    rows, cols = 1, 1
                elif len(classes) == 2:
                    rows, cols = 1, 2
                elif len(classes) == 3:
                    rows, cols = 2, 2
                else:  # 4 classes
                    rows, cols = 2, 2
                
                fig = make_subplots(
                    rows=rows, cols=cols,
                    subplot_titles=[f'Classe: {c}' for c in classes],
                    shared_xaxes=True,
                    shared_yaxes=True
                )
                
                for i, class_val in enumerate(classes):
                    if len(classes) <= 2:
                        row = 1
                        col = i + 1
                    else:
                        row = (i // 2) + 1
                        col = (i % 2) + 1
                    
                    class_data = self.df[self.df[color_col] == class_val]
                    x_vals = class_data[x_col].dropna()
                    y_vals = class_data[y_col].dropna()
                    
                    if len(x_vals) > 0 and len(y_vals) > 0:
                        # Criar histograma 2D
                        hist, x_edges, y_edges = np.histogram2d(x_vals, y_vals, bins=gridsize)
                        
                        fig.add_trace(
                            go.Heatmap(
                                z=hist.T,
                                x=x_edges[:-1],
                                y=y_edges[:-1],
                                colorscale='Viridis',
                                showscale=i == 0,  # Mostrar escala apenas no primeiro
                                name=f'Densidade {class_val}'
                            ),
                            row=row, col=col
                        )
                
                fig.update_layout(
                    title=f'Densidade Hexbin: {y_col} vs {x_col} por {color_col}',
                    template='plotly_white'
                )
            else:
                # Muitas classes - usar densidade geral com cor
                fig = go.Figure()
                
                x_vals = self.df[x_col].dropna()
                y_vals = self.df[y_col].dropna()
                
                if len(x_vals) > 0 and len(y_vals) > 0:
                    hist, x_edges, y_edges = np.histogram2d(x_vals, y_vals, bins=gridsize)
                    
                    fig.add_trace(
                        go.Heatmap(
                            z=hist.T,
                            x=x_edges[:-1],
                            y=y_edges[:-1],
                            colorscale='Viridis',
                            name='Densidade'
                        )
                    )
                
                fig.update_layout(
                    title=f'Densidade Hexbin: {y_col} vs {x_col}',
                    xaxis_title=x_col,
                    yaxis_title=y_col,
                    template='plotly_white'
                )
        else:
            # Densidade geral sem separação por classe
            fig = go.Figure()
            
            x_vals = self.df[x_col].dropna()
            y_vals = self.df[y_col].dropna()
            
            if len(x_vals) > 0 and len(y_vals) > 0:
                hist, x_edges, y_edges = np.histogram2d(x_vals, y_vals, bins=gridsize)
                
                fig.add_trace(
                    go.Heatmap(
                        z=hist.T,
                        x=x_edges[:-1],
                        y=y_edges[:-1],
                        colorscale='Viridis',
                        name='Densidade'
                    )
                )
            
            fig.update_layout(
                title=f'Densidade Hexbin: {y_col} vs {x_col}',
                xaxis_title=x_col,
                yaxis_title=y_col,
                template='plotly_white'
            )
        
        return fig
    
    def plot_kde_bivariate(self, x_col, y_col, color_col=None, n_levels=8):
        """KDE bivariado com contornos de densidade por classe"""
        if x_col not in self.df.columns or y_col not in self.df.columns:
            return None
            
        fig = go.Figure()
        
        if color_col and color_col in self.df.columns:
            # KDE por classe
            classes = self.df[color_col].unique()
            classes = [c for c in classes if pd.notna(c)]
            colors = px.colors.qualitative.Set1[:len(classes)]
            
            for i, class_val in enumerate(classes):
                class_data = self.df[self.df[color_col] == class_val]
                x_vals = class_data[x_col].dropna()
                y_vals = class_data[y_col].dropna()
                
                if len(x_vals) > 5 and len(y_vals) > 5:  # Mínimo para KDE
                    try:
                        # Criar grid para KDE
                        x_min, x_max = x_vals.min(), x_vals.max()
                        y_min, y_max = y_vals.min(), y_vals.max()
                        
                        # Expandir um pouco os limites
                        x_range = x_max - x_min
                        y_range = y_max - y_min
                        x_min -= 0.1 * x_range
                        x_max += 0.1 * x_range
                        y_min -= 0.1 * y_range
                        y_max += 0.1 * y_range
                        
                        xx, yy = np.mgrid[x_min:x_max:50j, y_min:y_max:50j]
                        positions = np.vstack([xx.ravel(), yy.ravel()])
                        
                        # Calcular KDE
                        values = np.vstack([x_vals, y_vals])
                        kernel = gaussian_kde(values)
                        f = np.reshape(kernel(positions).T, xx.shape)
                        
                        # Adicionar contornos
                        fig.add_trace(go.Contour(
                            x=xx[0],
                            y=yy[:, 0],
                            z=f,
                            name=f'KDE {class_val}',
                            colorscale=[[0, 'rgba(255,255,255,0)'], [1, colors[i]]],
                            showscale=False,
                            ncontours=n_levels,
                            line=dict(color=colors[i], width=2)
                        ))
                        
                        # Adicionar pontos originais com transparência
                        fig.add_trace(go.Scatter(
                            x=x_vals,
                            y=y_vals,
                            mode='markers',
                            name=f'Dados {class_val}',
                            marker=dict(
                                color=colors[i],
                                size=4,
                                opacity=0.3
                            ),
                            showlegend=False
                        ))
                        
                    except Exception as e:
                        # Fallback para scatter simples se KDE falhar
                        fig.add_trace(go.Scatter(
                            x=x_vals,
                            y=y_vals,
                            mode='markers',
                            name=f'{class_val}',
                            marker=dict(color=colors[i], size=6, opacity=0.6)
                        ))
            
            title = f'KDE Bivariado: {y_col} vs {x_col} por {color_col}'
        else:
            # KDE geral
            x_vals = self.df[x_col].dropna()
            y_vals = self.df[y_col].dropna()
            
            if len(x_vals) > 5 and len(y_vals) > 5:
                try:
                    # Criar grid para KDE
                    x_min, x_max = x_vals.min(), x_vals.max()
                    y_min, y_max = y_vals.min(), y_vals.max()
                    
                    # Expandir um pouco os limites
                    x_range = x_max - x_min
                    y_range = y_max - y_min
                    x_min -= 0.1 * x_range
                    x_max += 0.1 * x_range
                    y_min -= 0.1 * y_range
                    y_max += 0.1 * y_range
                    
                    xx, yy = np.mgrid[x_min:x_max:50j, y_min:y_max:50j]
                    positions = np.vstack([xx.ravel(), yy.ravel()])
                    
                    # Calcular KDE
                    values = np.vstack([x_vals, y_vals])
                    kernel = gaussian_kde(values)
                    f = np.reshape(kernel(positions).T, xx.shape)
                    
                    # Adicionar contornos
                    fig.add_trace(go.Contour(
                        x=xx[0],
                        y=yy[:, 0],
                        z=f,
                        name='KDE',
                        colorscale='Viridis',
                        ncontours=n_levels,
                        line=dict(width=2)
                    ))
                    
                    # Adicionar pontos originais
                    fig.add_trace(go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode='markers',
                        name='Dados',
                        marker=dict(
                            color='rgba(0,0,0,0.3)',
                            size=4
                        ),
                        showlegend=False
                    ))
                    
                except Exception as e:
                    # Fallback para scatter simples
                    fig.add_trace(go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode='markers',
                        name='Dados',
                        marker=dict(size=6, opacity=0.6)
                    ))
            
            title = f'KDE Bivariado: {y_col} vs {x_col}'
        
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            template='plotly_white',
            hovermode='closest'
        )
        
        return fig
    
    def plot_pair_matrix(self, columns=None, color_col=None, max_cols=4):
        """Matriz de dispersão (pair plot) com distribuições marginais"""
        if columns is None:
            # Selecionar colunas numéricas automaticamente
            numeric_cols = [col for col in self.numeric_columns if col != color_col]
            columns = numeric_cols[:max_cols]  # Limitar para performance
        
        if len(columns) < 2:
            return None
            
        # Limitar número de colunas para performance
        if len(columns) > max_cols:
            columns = columns[:max_cols]
        
        n_cols = len(columns)
        
        # Criar subplots
        fig = make_subplots(
            rows=n_cols, 
            cols=n_cols,
            subplot_titles=[f'{col}' for col in columns] if n_cols <= 3 else None,
            shared_xaxes=False,
            shared_yaxes=False,
            vertical_spacing=0.05,
            horizontal_spacing=0.05
        )
        
        colors = px.colors.qualitative.Set1 if color_col else ['blue']
        
        for i, col_y in enumerate(columns):
            for j, col_x in enumerate(columns):
                row = i + 1
                col = j + 1
                
                if i == j:
                    # Diagonal: histogramas/distribuições
                    if color_col and color_col in self.df.columns:
                        # Histograma por classe
                        classes = self.df[color_col].unique()
                        classes = [c for c in classes if pd.notna(c)]
                        
                        for k, class_val in enumerate(classes):
                            class_data = self.df[self.df[color_col] == class_val]
                            values = class_data[col_x].dropna()
                            
                            if len(values) > 0:
                                fig.add_trace(
                                    go.Histogram(
                                        x=values,
                                        name=f'{class_val}' if i == 0 else None,
                                        opacity=0.7,
                                        marker_color=colors[k % len(colors)],
                                        showlegend=(i == 0),
                                        nbinsx=20
                                    ),
                                    row=row, col=col
                                )
                    else:
                        # Histograma geral
                        values = self.df[col_x].dropna()
                        if len(values) > 0:
                            fig.add_trace(
                                go.Histogram(
                                    x=values,
                                    name=col_x if i == 0 else None,
                                    opacity=0.7,
                                    showlegend=False,
                                    nbinsx=20
                                ),
                                row=row, col=col
                            )
                else:
                    # Off-diagonal: scatter plots
                    if color_col and color_col in self.df.columns:
                        # Scatter por classe
                        classes = self.df[color_col].unique()
                        classes = [c for c in classes if pd.notna(c)]
                        
                        for k, class_val in enumerate(classes):
                            class_data = self.df[self.df[color_col] == class_val]
                            x_vals = class_data[col_x].dropna()
                            y_vals = class_data[col_y].dropna()
                            
                            # Garantir que x e y tenham o mesmo tamanho
                            common_idx = class_data.dropna(subset=[col_x, col_y]).index
                            x_vals = class_data.loc[common_idx, col_x]
                            y_vals = class_data.loc[common_idx, col_y]
                            
                            if len(x_vals) > 0:
                                fig.add_trace(
                                    go.Scatter(
                                        x=x_vals,
                                        y=y_vals,
                                        mode='markers',
                                        name=f'{class_val}' if i == 0 and j == 1 else None,
                                        marker=dict(
                                            color=colors[k % len(colors)],
                                            size=4,
                                            opacity=0.6
                                        ),
                                        showlegend=(i == 0 and j == 1)
                                    ),
                                    row=row, col=col
                                )
                    else:
                        # Scatter geral
                        x_vals = self.df[col_x].dropna()
                        y_vals = self.df[col_y].dropna()
                        
                        # Garantir que x e y tenham o mesmo tamanho
                        common_idx = self.df.dropna(subset=[col_x, col_y]).index
                        x_vals = self.df.loc[common_idx, col_x]
                        y_vals = self.df.loc[common_idx, col_y]
                        
                        if len(x_vals) > 0:
                            fig.add_trace(
                                go.Scatter(
                                    x=x_vals,
                                    y=y_vals,
                                    mode='markers',
                                    name=f'{col_y} vs {col_x}' if i == 0 and j == 1 else None,
                                    marker=dict(size=4, opacity=0.6),
                                    showlegend=False
                                ),
                                row=row, col=col
                            )
                
                # Atualizar eixos
                fig.update_xaxes(title_text=col_x if i == n_cols - 1 else "", row=row, col=col)
                fig.update_yaxes(title_text=col_y if j == 0 else "", row=row, col=col)
        
        # Layout geral
        title = f'Matriz de Dispersão'
        if color_col:
            title += f' por {color_col}'
        if len(columns) > 2:
            title += f' ({", ".join(columns[:3])}{"..." if len(columns) > 3 else ""})'
        
        fig.update_layout(
            title=title,
            template='plotly_white',
            height=150 * n_cols,
            showlegend=True if color_col else False
        )
        
        return fig
    
    def plot_univariate_by_class(self, columns=None, color_col=None, plot_type='violin'):
        """Gráficos univariados por classe (violin/box + rug)"""
        if not color_col or color_col not in self.df.columns:
            return None
            
        if columns is None:
            # Selecionar colunas numéricas automaticamente
            numeric_cols = [col for col in self.numeric_columns if col != color_col]
            columns = numeric_cols[:4]  # Limitar para performance
        
        if not columns:
            return None
            
        # Limitar número de colunas
        if len(columns) > 4:
            columns = columns[:4]
        
        n_cols = len(columns)
        
        # Criar subplots
        fig = make_subplots(
            rows=1, 
            cols=n_cols,
            subplot_titles=columns,
            shared_yaxes=False,
            horizontal_spacing=0.08
        )
        
        classes = self.df[color_col].unique()
        classes = [c for c in classes if pd.notna(c)]
        colors = px.colors.qualitative.Set1[:len(classes)]
        
        for j, column in enumerate(columns):
            col_pos = j + 1
            
            for i, class_val in enumerate(classes):
                class_data = self.df[self.df[color_col] == class_val]
                values = class_data[column].dropna()
                
                if len(values) > 0:
                    if plot_type == 'violin':
                        # Violin plot
                        fig.add_trace(
                            go.Violin(
                                y=values,
                                name=f'{class_val}',
                                side='positive',
                                line_color=colors[i],
                                fillcolor=colors[i],
                                opacity=0.6,
                                showlegend=(j == 0),  # Mostrar legenda apenas na primeira coluna
                                box_visible=True,
                                meanline_visible=True
                            ),
                            row=1, col=col_pos
                        )
                    elif plot_type == 'box':
                        # Box plot
                        fig.add_trace(
                            go.Box(
                                y=values,
                                name=f'{class_val}',
                                marker_color=colors[i],
                                showlegend=(j == 0),
                                boxpoints='outliers'
                            ),
                            row=1, col=col_pos
                        )
                    
                    # Adicionar rug plot (pontos na base)
                    if len(values) <= 1000:  # Limitar para performance
                        # Criar posições x ligeiramente diferentes para cada classe
                        x_positions = np.full(len(values), i * 0.8) + np.random.normal(0, 0.05, len(values))
                        
                        fig.add_trace(
                            go.Scatter(
                                x=x_positions,
                                y=values,
                                mode='markers',
                                name=f'Rug {class_val}',
                                marker=dict(
                                    color=colors[i],
                                    size=3,
                                    opacity=0.4,
                                    symbol='line-ns'
                                ),
                                showlegend=False
                            ),
                            row=1, col=col_pos
                        )
            
            # Atualizar eixos
            fig.update_yaxes(title_text=column, row=1, col=col_pos)
            fig.update_xaxes(title_text=color_col, row=1, col=col_pos)
        
        # Layout geral
        plot_name = 'Violin' if plot_type == 'violin' else 'Box'
        title = f'{plot_name} Plots por {color_col}'
        if len(columns) > 1:
            title += f' ({", ".join(columns[:3])}{"..." if len(columns) > 3 else ""})'
        
        fig.update_layout(
            title=title,
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        return fig
    
    def plot_enhanced_correlation_heatmap(self, columns=None, method='pearson'):
        """Mapa de calor da matriz de correlação melhorado"""
        if columns is None:
            columns = self.numeric_columns
        
        if len(columns) < 2:
            return None
            
        # Calcular matriz de correlação
        corr_data = self.df[columns].corr(method=method)
        
        # Criar máscara para triângulo superior
        mask = np.triu(np.ones_like(corr_data, dtype=bool))
        
        # Aplicar máscara
        corr_masked = corr_data.copy()
        corr_masked[mask] = np.nan
        
        # Criar heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_masked.values,
            x=corr_masked.columns,
            y=corr_masked.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_masked.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False,
            colorbar=dict(
                title="Correlação",
                titleside="right"
            )
        ))
        
        # Adicionar anotações para valores significativos
        annotations = []
        for i, row in enumerate(corr_masked.index):
            for j, col in enumerate(corr_masked.columns):
                if not pd.isna(corr_masked.iloc[i, j]):
                    value = corr_masked.iloc[i, j]
                    if abs(value) > 0.7:  # Correlações fortes
                        annotations.append(
                            dict(
                                x=j, y=i,
                                text=f"<b>{value:.2f}</b>",
                                showarrow=False,
                                font=dict(color="white" if abs(value) > 0.8 else "black", size=12)
                            )
                        )
        
        fig.update_layout(
            title=f'Matriz de Correlação ({method.title()})',
            template='plotly_white',
            annotations=annotations,
            xaxis=dict(side='bottom'),
            yaxis=dict(autorange='reversed'),
            height=max(400, len(columns) * 40)
        )
        
        return fig
    
    def plot_outliers(self, column):
        """Visualiza outliers usando box plot e scatter plot"""
        if column not in self.numeric_columns:
            return None
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=[f'Box Plot - {column}', f'Scatter Plot - {column}'],
            vertical_spacing=0.1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(y=self.df[column], name=column),
            row=1, col=1
        )
        
        # Scatter plot
        fig.add_trace(
            go.Scatter(
                x=list(range(len(self.df))),
                y=self.df[column],
                mode='markers',
                name='Valores',
                marker=dict(size=4)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f'Análise de Outliers - {column}',
            height=600,
            showlegend=False
        )
        
        return fig
    
    def plot_time_series(self, time_col, value_col):
        """Cria gráfico de série temporal"""
        if time_col not in self.df.columns or value_col not in self.df.columns:
            return None
        
        # Tentar converter coluna de tempo
        try:
            df_temp = self.df.copy()
            df_temp[time_col] = pd.to_datetime(df_temp[time_col])
            df_temp = df_temp.sort_values(time_col)
            
            fig = px.line(
                df_temp,
                x=time_col,
                y=value_col,
                title=f'Série Temporal - {value_col} ao longo do tempo'
            )
            
            return fig
        except:
            return None
    
    def plot_categorical_analysis(self, column, top_n=15):
        """Análise visual de variável categórica"""
        if column not in self.categorical_columns:
            return None
        
        value_counts = self.df[column].value_counts().head(top_n)
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=['Frequência Absoluta', 'Frequência Relativa (%)'],
            specs=[[{"type": "bar"}, {"type": "pie"}]]
        )
        
        # Gráfico de barras
        fig.add_trace(
            go.Bar(
                x=value_counts.index,
                y=value_counts.values,
                name='Frequência'
            ),
            row=1, col=1
        )
        
        # Gráfico de pizza
        fig.add_trace(
            go.Pie(
                labels=value_counts.index,
                values=value_counts.values,
                name='Proporção'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title=f'Análise de {column}',
            height=500,
            showlegend=False
        )
        
        return fig
    
    def plot_comparison_by_target(self, feature_col, target_col):
        """Compara distribuição de uma feature por classes do target"""
        if feature_col not in self.df.columns or target_col not in self.df.columns:
            return None
        
        if feature_col in self.numeric_columns:
            fig = px.box(
                self.df,
                x=target_col,
                y=feature_col,
                title=f'Distribuição de {feature_col} por {target_col}'
            )
        else:
            # Crosstab para variáveis categóricas
            crosstab = pd.crosstab(self.df[feature_col], self.df[target_col])
            fig = px.bar(
                crosstab,
                title=f'Relação entre {feature_col} e {target_col}',
                barmode='group'
            )
        
        return fig
    
    def create_dashboard_overview(self):
        """Cria visão geral do dataset"""
        figs = []
        
        # Informações básicas
        info_text = f"""
        **Informações do Dataset:**
        - Linhas: {len(self.df):,}
        - Colunas: {len(self.df.columns)}
        - Colunas Numéricas: {len(self.numeric_columns)}
        - Colunas Categóricas: {len(self.categorical_columns)}
        - Valores Faltantes: {self.df.isnull().sum().sum():,}
        """
        
        # Distribuições das principais variáveis numéricas
        if self.numeric_columns:
            for col in self.numeric_columns[:4]:  # Primeiras 4 colunas
                fig = self.plot_distribution(col)
                if fig:
                    figs.append(fig)
        
        # Matriz de correlação se houver colunas numéricas suficientes
        if len(self.numeric_columns) >= 2:
            corr_fig = self.plot_correlation_matrix()
            if corr_fig:
                figs.append(corr_fig)
        
        return info_text, figs
    
    def generate_visualization_for_question(self, question, relevant_columns):
        """Gera visualização baseada na pergunta e colunas relevantes"""
        question_lower = question.lower()
        
        # Verificar se é pergunta sobre correlação
        correlation_keywords = ['correlação', 'correlações', 'correlation', 'correlations', 'relação', 'relações', 'relationship', 'relationships']
        is_correlation_question = any(keyword in question_lower for keyword in correlation_keywords)
        
        # Detectar coluna de classe/categoria para coloração
        class_col = None
        if 'class' in self.df.columns:
            class_col = 'class'
        elif 'Class' in self.df.columns:
            class_col = 'Class'
        elif self.categorical_columns:
            class_col = self.categorical_columns[0]
        
        # 1. Prioridade máxima: Palavras-chave específicas com colunas relevantes
        if relevant_columns:
            numeric_relevant = [col for col in relevant_columns if col in self.numeric_columns]
            categorical_relevant = [col for col in relevant_columns if col in self.categorical_columns]
            
            # Gráficos avançados específicos
            if any(word in question_lower for word in ['scatter', 'dispersão', 'avançado', 'advanced', 'tendência', 'trend']):
                if len(numeric_relevant) >= 2:
                    return self.plot_advanced_scatter(numeric_relevant[0], numeric_relevant[1], class_col)
                elif len(numeric_relevant) == 1 and len(self.numeric_columns) >= 2:
                    other_numeric = [col for col in self.numeric_columns if col != numeric_relevant[0]][0]
                    return self.plot_advanced_scatter(numeric_relevant[0], other_numeric, class_col)
            
            # Hexbin para muitos pontos
            if any(word in question_lower for word in ['hexbin', 'densidade', 'density', 'overplotting', 'muitos pontos']):
                if len(numeric_relevant) >= 2:
                    return self.plot_hexbin_density(numeric_relevant[0], numeric_relevant[1], class_col)
                elif len(numeric_relevant) == 1 and len(self.numeric_columns) >= 2:
                    other_numeric = [col for col in self.numeric_columns if col != numeric_relevant[0]][0]
                    return self.plot_hexbin_density(numeric_relevant[0], other_numeric, class_col)
            
            # KDE bivariado
            if any(word in question_lower for word in ['kde', 'contorno', 'contour', 'probabilidade', 'probability', 'elegante']):
                if len(numeric_relevant) >= 2:
                    return self.plot_kde_bivariate(numeric_relevant[0], numeric_relevant[1], class_col)
                elif len(numeric_relevant) == 1 and len(self.numeric_columns) >= 2:
                    other_numeric = [col for col in self.numeric_columns if col != numeric_relevant[0]][0]
                    return self.plot_kde_bivariate(numeric_relevant[0], other_numeric, class_col)
            
            # Matriz de dispersão (pair plot)
            if any(word in question_lower for word in ['matriz', 'matrix', 'pair', 'pairplot', 'marginal', 'overview', 'exploratória']):
                cols_for_matrix = numeric_relevant[:4] if len(numeric_relevant) <= 4 else numeric_relevant[:3]
                return self.plot_pair_matrix(cols_for_matrix, class_col)
            
            # Gráficos univariados por classe
            if any(word in question_lower for word in ['violin', 'box', 'univariado', 'univariate', 'distribuição por classe', 'distribution by class']):
                cols_for_univariate = numeric_relevant[:3] if len(numeric_relevant) <= 3 else numeric_relevant[:2]
                return self.plot_univariate_by_class(cols_for_univariate, class_col)
            
            # Distribuição - priorizar colunas relevantes
            if any(word in question_lower for word in ['distribuição', 'distribution', 'histograma', 'histogram']):
                if numeric_relevant:
                    return self.plot_distribution(numeric_relevant[0])
                elif categorical_relevant:
                    return self.plot_categorical_analysis(categorical_relevant[0])
            
            # Scatter plot padrão - usar colunas relevantes
            if any(word in question_lower for word in ['compare', 'comparar', 'relação simples']):
                if len(numeric_relevant) >= 2:
                    return self.plot_scatter(numeric_relevant[0], numeric_relevant[1], class_col)
                elif len(numeric_relevant) == 1 and len(self.numeric_columns) >= 2:
                    other_numeric = [col for col in self.numeric_columns if col != numeric_relevant[0]][0]
                    return self.plot_scatter(numeric_relevant[0], other_numeric, class_col)
            
            # Análise categórica
            if any(word in question_lower for word in ['categoria', 'categórica', 'categorical', 'frequência', 'frequency', 'contagem', 'count']):
                if categorical_relevant:
                    return self.plot_categorical_analysis(categorical_relevant[0])
            
            # Análise específica baseada no tipo das colunas relevantes
            if len(numeric_relevant) >= 2:
                # Se pergunta sobre correlação ou comparação
                if is_correlation_question:
                    return self.plot_enhanced_correlation_heatmap(numeric_relevant)
                else:
                    # Usar scatter avançado como padrão para 2+ colunas numéricas
                    return self.plot_advanced_scatter(numeric_relevant[0], numeric_relevant[1], class_col)
            
            elif len(numeric_relevant) == 1:
                # Uma coluna numérica - distribuição ou comparação
                if categorical_relevant:
                    # Comparar numérica por categórica
                    if any(word in question_lower for word in ['por', 'by', 'média', 'mean', 'average', 'comparar', 'compare', 'padrão', 'pattern']):
                        return self.plot_numeric_by_categorical(numeric_relevant[0], categorical_relevant[0])
                    else:
                        return self.plot_distribution(numeric_relevant[0])
                elif any(word in question_lower for word in ['análise', 'analysis', 'comportamento', 'behavior', 'padrão', 'pattern']):
                    return self.plot_distribution(numeric_relevant[0])
                else:
                    return self.plot_distribution(numeric_relevant[0])
            
            elif len(categorical_relevant) >= 1:
                return self.plot_categorical_analysis(categorical_relevant[0])
        
        # 2. Análise de correlação (mesmo sem colunas específicas)
        if is_correlation_question:
            if len(self.numeric_columns) >= 2:
                return self.plot_enhanced_correlation_heatmap()
            else:
                return self.plot_correlation_matrix()
        
        # 3. Fallback inteligente baseado na pergunta
        return self._generate_smart_default_visualization(question_lower)
    
    def _generate_smart_default_visualization(self, question_lower):
        """Gera uma visualização inteligente padrão baseada na estrutura dos dados"""
        
        # Detectar coluna de classe/categoria para coloração
        class_col = None
        if 'class' in self.df.columns:
            class_col = 'class'
        elif 'Class' in self.df.columns:
            class_col = 'Class'
        elif self.categorical_columns:
            class_col = self.categorical_columns[0]
        
        # Prioridade 1: Gráficos avançados específicos baseados em palavras-chave
        if any(word in question_lower for word in ['scatter', 'dispersão', 'avançado', 'advanced', 'tendência', 'trend']):
            if len(self.numeric_columns) >= 2:
                return self.plot_advanced_scatter(self.numeric_columns[0], self.numeric_columns[1], class_col)
        
        if any(word in question_lower for word in ['hexbin', 'densidade', 'density', 'overplotting', 'muitos pontos']):
            if len(self.numeric_columns) >= 2:
                return self.plot_hexbin_density(self.numeric_columns[0], self.numeric_columns[1], class_col)
        
        if any(word in question_lower for word in ['kde', 'contorno', 'contour', 'probabilidade', 'probability', 'elegante']):
            if len(self.numeric_columns) >= 2:
                return self.plot_kde_bivariate(self.numeric_columns[0], self.numeric_columns[1], class_col)
        
        if any(word in question_lower for word in ['matriz', 'matrix', 'pair', 'pairplot', 'marginal', 'overview', 'exploratória']):
            cols_for_matrix = self.numeric_columns[:4] if len(self.numeric_columns) <= 4 else self.numeric_columns[:3]
            return self.plot_pair_matrix(cols_for_matrix, class_col)
        
        if any(word in question_lower for word in ['violin', 'box', 'univariado', 'univariate', 'distribuição por classe', 'distribution by class']):
            cols_for_univariate = self.numeric_columns[:3] if len(self.numeric_columns) <= 3 else self.numeric_columns[:2]
            return self.plot_univariate_by_class(cols_for_univariate, class_col)
        
        # Prioridade 2: Análises específicas tradicionais
        if any(word in question_lower for word in ['distribuição', 'distribution', 'histograma', 'frequência']):
            if self.numeric_columns:
                return self.plot_distribution(self.numeric_columns[0])
        
        if any(word in question_lower for word in ['categoria', 'categórica', 'categorical', 'tipo', 'class', 'grupo']):
            if self.categorical_columns:
                return self.plot_categorical_analysis(self.categorical_columns[0])
        
        if any(word in question_lower for word in ['comparar', 'compare', 'relação', 'relationship']):
            if len(self.numeric_columns) >= 2:
                # Usar scatter avançado como padrão para comparações
                return self.plot_advanced_scatter(self.numeric_columns[0], self.numeric_columns[1], class_col)
            elif len(self.numeric_columns) >= 1:
                return self.plot_enhanced_correlation_heatmap()
        
        # Prioridade 3: Estratégia inteligente baseada na estrutura dos dados
        
        # Se há muitas colunas numéricas (>= 4), mostrar matriz de dispersão
        if len(self.numeric_columns) >= 4:
            return self.plot_pair_matrix(self.numeric_columns[:4], class_col)
        
        # Se há 3 colunas numéricas, mostrar correlação melhorada
        elif len(self.numeric_columns) == 3:
            return self.plot_enhanced_correlation_heatmap()
        
        # Se há 2 colunas numéricas, fazer scatter avançado
        elif len(self.numeric_columns) == 2:
            return self.plot_advanced_scatter(self.numeric_columns[0], self.numeric_columns[1], class_col)
        
        # Se há 1 coluna numérica, mostrar distribuição
        elif len(self.numeric_columns) == 1:
            return self.plot_distribution(self.numeric_columns[0])
        
        # Se há colunas categóricas, mostrar análise da primeira
        elif self.categorical_columns:
            return self.plot_categorical_analysis(self.categorical_columns[0])
        
        # Último recurso: overview do dataset
        else:
            return self.create_dashboard_overview()