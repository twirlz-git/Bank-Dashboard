"""
modules/chart_generator.py - Generate charts for trends analysis
"""

import logging
from typing import Dict, Any, List
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io
import base64

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate interactive and static charts for trends analysis"""

    def __init__(self):
        self.colors = {
            'primary': '#366092',
            'secondary': '#4A90E2',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'info': '#17a2b8',
            'gradient_colors': [
                '#FF6B6B', '#FFA07A', '#FFD93D', '#6BCF7F', 
                '#4ECDC4', '#45B7D1', '#5E60CE', '#9B5DE5'
            ]
        }

    def generate_timeline_chart(self, timeline: List[Dict[str, Any]], title: str = "Динамика изменения ставки") -> go.Figure:
        """
        Generate line chart for timeline data.
        
        Args:
            timeline: List of data points with 'date' and 'rate' keys
            title: Chart title
            
        Returns:
            Plotly Figure object
        """
        
        if not timeline:
            return self._create_empty_chart("Недостаточно данных для построения графика")
        
        # Extract data
        dates = [self._parse_date(item.get('date', '')) for item in timeline]
        rates = [item.get('rate', 0) for item in timeline]
        reasons = [item.get('reason', 'Н/Д') for item in timeline]
        
        # Create figure
        fig = go.Figure()
        
        # Add line trace with gradient effect
        fig.add_trace(go.Scatter(
            x=dates,
            y=rates,
            mode='lines+markers',
            name='Ставка',
            line=dict(color=self.colors['primary'], width=3, shape='spline'),
            marker=dict(
                size=12, 
                color=self.colors['secondary'],
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>Дата:</b> %{x}<br><b>Ставка:</b> %{y:.2f}%<br><b>Причина:</b> %{text}<extra></extra>',
            text=reasons
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Arial, sans-serif', 'color': '#2C3E50'}
            },
            xaxis_title='Дата',
            yaxis_title='Процентная ставка (%)',
            hovermode='x unified',
            template='plotly_white',
            showlegend=False,
            height=500,
            font={'family': 'Arial, sans-serif'},
            margin=dict(l=60, r=40, t=80, b=60),
            plot_bgcolor='rgba(240, 240, 240, 0.3)'
        )
        
        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.3)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.3)')
        
        return fig

    def generate_comparison_chart(self, comparison_data: Dict[str, Any]) -> go.Figure:
        """
        Generate styled grouped bar chart comparing products.
        Works well with small number of data points.
        
        Args:
            comparison_data: Dictionary with comparison data
            
        Returns:
            Plotly Figure object
        """
        
        comparison_table = comparison_data.get('comparison_table')
        if comparison_table is None or comparison_table.empty:
            return self._create_empty_chart("Нет данных для сравнения")
        
        # Extract comparison metrics (assuming first column is parameter names)
        parameters = comparison_table.iloc[:, 0].tolist()
        
        # Get bank names from column headers (skip first column)
        banks = comparison_table.columns[1:].tolist()
        
        # Create grouped bar chart for numeric parameters only
        numeric_params = []
        bank_values = {bank: [] for bank in banks}
        
        for idx, param in enumerate(parameters):
            # Try to extract numeric values
            try:
                values = []
                is_numeric = True
                for bank in banks:
                    value_str = str(comparison_table.iloc[idx, comparison_table.columns.get_loc(bank)])
                    # Extract number from string (e.g., "18.5%" -> 18.5)
                    import re
                    num_match = re.search(r'(\d+\.?\d*)', value_str)
                    if num_match:
                        values.append(float(num_match.group(1)))
                    else:
                        is_numeric = False
                        break
                
                if is_numeric and values:
                    numeric_params.append(param)
                    for bank, value in zip(banks, values):
                        bank_values[bank].append(value)
            except:
                continue
        
        if not numeric_params:
            return self._create_empty_chart("Нет числовых параметров для визуализации")
        
        # Create figure with styled bars
        fig = go.Figure()
        
        # Use gradient colors for different banks
        colors = self.colors['gradient_colors']
        
        for idx, bank in enumerate(banks):
            # Create gradient effect for each bar
            bar_color = colors[idx % len(colors)]
            
            fig.add_trace(go.Bar(
                name=bank,
                x=numeric_params,
                y=bank_values[bank],
                marker=dict(
                    color=bar_color,
                    line=dict(color='rgba(255, 255, 255, 0.8)', width=1.5),
                    pattern=dict(shape="")  # Solid fill
                ),
                text=[f"{v:.1f}" for v in bank_values[bank]],
                textposition='outside',
                textfont=dict(size=11, color='#2C3E50', family='Arial'),
                hovertemplate='<b>%{fullData.name}</b><br>%{x}: %{y:.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            title={
                'text': 'Сравнение ключевых параметров',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Arial, sans-serif', 'color': '#2C3E50'}
            },
            xaxis_title='Параметр',
            yaxis_title='Значение',
            barmode='group',
            bargap=0.15,  # Gap between bars of adjacent location coordinates
            bargroupgap=0.1,  # Gap between bars of the same location coordinate
            template='plotly_white',
            height=500,
            font={'family': 'Arial, sans-serif'},
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='rgba(200, 200, 200, 0.5)',
                borderwidth=1
            ),
            margin=dict(l=60, r=40, t=100, b=80),
            plot_bgcolor='rgba(240, 240, 240, 0.3)'
        )
        
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.3)')
        
        return fig

    def generate_trend_analysis_chart(self, timeline: List[Dict[str, Any]], analysis: Dict[str, Any]) -> go.Figure:
        """
        Generate comprehensive trend analysis chart with histogram.
        Styled like the diamond dataset visualization.
        
        Args:
            timeline: Timeline data
            analysis: Analysis results
            
        Returns:
            Plotly Figure object
        """
        
        if not timeline:
            return self._create_empty_chart("Недостаточно данных для анализа")
        
        # Extract data
        dates = [self._parse_date(item.get('date', '')) for item in timeline]
        rates = [item.get('rate', 0) for item in timeline]
        
        # Create figure with subplots
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.65, 0.35],
            subplot_titles=("Динамика процентной ставки", "Распределение изменений"),
            vertical_spacing=0.12
        )
        
        # Main trend line with spline interpolation
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=rates,
                mode='lines+markers',
                name='Ставка',
                line=dict(color=self.colors['primary'], width=3, shape='spline'),
                marker=dict(
                    size=12, 
                    color=self.colors['secondary'],
                    line=dict(width=2, color='white')
                ),
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Add average line
        if analysis.get('average_value'):
            avg_value = analysis['average_value']
            fig.add_trace(
                go.Scatter(
                    x=[dates[0], dates[-1]],
                    y=[avg_value, avg_value],
                    mode='lines',
                    name=f'Среднее: {avg_value:.2f}%',
                    line=dict(color=self.colors['warning'], width=2, dash='dash'),
                    showlegend=True
                ),
                row=1, col=1
            )
        
        # Add histogram with gradient colors (like the diamond visualization)
        if len(rates) > 1:
            changes = [rates[i] - rates[i-1] for i in range(1, len(rates))]
            
            # Create gradient colors based on value
            colors_hist = []
            for c in changes:
                if c < -0.5:
                    colors_hist.append('#28a745')  # Strong green for big decrease
                elif c < 0:
                    colors_hist.append('#6BCF7F')  # Light green for small decrease
                elif c < 0.5:
                    colors_hist.append('#FFA07A')  # Light red for small increase
                else:
                    colors_hist.append('#dc3545')  # Strong red for big increase
            
            fig.add_trace(
                go.Bar(
                    x=dates[1:],
                    y=changes,
                    name='Изменение',
                    marker=dict(
                        color=colors_hist,
                        line=dict(color='rgba(255, 255, 255, 0.6)', width=1),
                        opacity=0.8
                    ),
                    hovertemplate='<b>Дата:</b> %{x}<br><b>Изменение:</b> %{y:.2f}%<extra></extra>',
                    showlegend=False
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'Детальный анализ трендов',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'family': 'Arial, sans-serif', 'color': '#2C3E50'}
            },
            template='plotly_white',
            height=700,
            font={'family': 'Arial, sans-serif'},
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='rgba(200, 200, 200, 0.5)',
                borderwidth=1
            ),
            margin=dict(l=60, r=40, t=120, b=60),
            plot_bgcolor='rgba(240, 240, 240, 0.3)'
        )
        
        # Update axes
        fig.update_xaxes(title_text="Дата", row=1, col=1, showgrid=True, gridcolor='rgba(200, 200, 200, 0.3)')
        fig.update_yaxes(title_text="Ставка (%)", row=1, col=1, showgrid=True, gridcolor='rgba(200, 200, 200, 0.3)')
        fig.update_xaxes(title_text="Дата", row=2, col=1, showgrid=False)
        fig.update_yaxes(
            title_text="Изменение (%)", 
            row=2, col=1, 
            showgrid=True, 
            gridcolor='rgba(200, 200, 200, 0.3)',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='rgba(100, 100, 100, 0.5)'
        )
        
        return fig

    def generate_multiple_banks_comparison(self, banks_data: List[Dict[str, Any]]) -> go.Figure:
        """
        Generate comparison chart for multiple banks.
        
        Args:
            banks_data: List of bank data with timeline
            
        Returns:
            Plotly Figure object
        """
        
        if not banks_data:
            return self._create_empty_chart("Нет данных для сравнения")
        
        fig = go.Figure()
        
        colors = self.colors['gradient_colors']
        
        for idx, bank_data in enumerate(banks_data):
            bank_name = bank_data.get('bank', f'Банк {idx + 1}')
            timeline = bank_data.get('timeline', [])
            
            if timeline:
                dates = [self._parse_date(item.get('date', '')) for item in timeline]
                rates = [item.get('rate', 0) for item in timeline]
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=rates,
                    mode='lines+markers',
                    name=bank_name,
                    line=dict(color=colors[idx % len(colors)], width=3, shape='spline'),
                    marker=dict(
                        size=10,
                        color=colors[idx % len(colors)],
                        line=dict(width=2, color='white')
                    )
                ))
        
        fig.update_layout(
            title={
                'text': 'Сравнение трендов нескольких банков',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Arial, sans-serif', 'color': '#2C3E50'}
            },
            xaxis_title='Дата',
            yaxis_title='Процентная ставка (%)',
            template='plotly_white',
            hovermode='x unified',
            height=600,
            font={'family': 'Arial, sans-serif'},
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='rgba(200, 200, 200, 0.5)',
                borderwidth=1
            ),
            margin=dict(l=60, r=150, t=80, b=60),
            plot_bgcolor='rgba(240, 240, 240, 0.3)'
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.3)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.3)')
        
        return fig

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return datetime.now()

    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create empty chart with message"""
        fig = go.Figure()
        
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        
        fig.update_layout(
            template='plotly_white',
            height=400,
            xaxis=dict(showticklabels=False, showgrid=False),
            yaxis=dict(showticklabels=False, showgrid=False)
        )
        
        return fig

    def save_chart_to_base64(self, fig: go.Figure, format: str = 'png') -> str:
        """
        Save chart to base64 string for embedding.
        
        Args:
            fig: Plotly figure
            format: Image format (png, jpeg, svg)
            
        Returns:
            Base64 encoded string
        """
        try:
            img_bytes = fig.to_image(format=format, engine='kaleido')
            img_base64 = base64.b64encode(img_bytes).decode()
            return f"data:image/{format};base64,{img_base64}"
        except Exception as e:
            logger.error(f"Failed to save chart to base64: {e}")
            return ""

    def save_chart_html(self, fig: go.Figure) -> str:
        """
        Save chart as HTML string.
        
        Args:
            fig: Plotly figure
            
        Returns:
            HTML string
        """
        return fig.to_html(include_plotlyjs='cdn', div_id='chart')
