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
import numpy as np

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
            'gradient_start': '#667eea',
            'gradient_end': '#764ba2'
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
        
        # Add line trace
        fig.add_trace(go.Scatter(
            x=dates,
            y=rates,
            mode='lines+markers',
            name='Ставка',
            line=dict(color=self.colors['primary'], width=3),
            marker=dict(size=10, color=self.colors['secondary']),
            hovertemplate='<b>Дата:</b> %{x}<br><b>Ставка:</b> %{y:.2f}%<br><b>Причина:</b> %{text}<extra></extra>',
            text=reasons
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Arial, sans-serif'}
            },
            xaxis_title='Дата',
            yaxis_title='Процентная ставка (%)',
            hovermode='x unified',
            template='plotly_white',
            showlegend=False,
            height=500,
            font={'family': 'Arial, sans-serif'},
            margin=dict(l=60, r=40, t=80, b=60)
        )
        
        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        return fig

    def generate_comparison_chart(self, comparison_data: Dict[str, Any]) -> go.Figure:
        """
        Generate radar/spider chart comparing two products.
        Replaced bar chart with more visually appealing radar chart.
        
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
        
        # Extract numeric parameters for radar chart
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
        
        # Normalize values to 0-100 scale for better radar chart display
        normalized_values = {bank: [] for bank in banks}
        for param_idx in range(len(numeric_params)):
            param_values = [bank_values[bank][param_idx] for bank in banks]
            max_val = max(param_values) if max(param_values) > 0 else 1
            
            for bank in banks:
                normalized_values[bank].append((bank_values[bank][param_idx] / max_val) * 100)
        
        # Create radar chart
        fig = go.Figure()
        
        colors = [
            self.colors['primary'], 
            self.colors['secondary'], 
            self.colors['info'],
            self.colors['success']
        ]
        
        for idx, bank in enumerate(banks):
            fig.add_trace(go.Scatterpolar(
                r=normalized_values[bank] + [normalized_values[bank][0]],  # Close the loop
                theta=numeric_params + [numeric_params[0]],
                fill='toself',
                fillcolor=colors[idx % len(colors)],
                opacity=0.6,
                name=bank,
                line=dict(color=colors[idx % len(colors)], width=2),
                marker=dict(size=8, color=colors[idx % len(colors)])
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showticklabels=False,
                    ticks='',
                    gridcolor='lightgray'
                ),
                angularaxis=dict(
                    gridcolor='lightgray'
                )
            ),
            title={
                'text': 'Сравнение ключевых параметров',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Arial, sans-serif'}
            },
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            template='plotly_white',
            height=600,
            font={'family': 'Arial, sans-serif'},
            margin=dict(l=80, r=80, t=100, b=80)
        )
        
        return fig

    def generate_trend_analysis_chart(self, timeline: List[Dict[str, Any]], analysis: Dict[str, Any]) -> go.Figure:
        """
        Generate comprehensive trend analysis chart with annotations.
        Replaced bar chart with area chart for smoother visualization.
        
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
            row_heights=[0.7, 0.3],
            subplot_titles=("Динамика процентной ставки", "Градиент изменений"),
            vertical_spacing=0.15
        )
        
        # Main trend line
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=rates,
                mode='lines+markers',
                name='Ставка',
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=10, color=self.colors['secondary']),
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
        
        # Add smooth area chart for changes (instead of bar chart)
        if len(rates) > 1:
            changes = [rates[i] - rates[i-1] for i in range(1, len(rates))]
            
            # Create color gradient based on change direction
            colors_area = []
            for c in changes:
                if c < 0:
                    colors_area.append(self.colors['success'])  # Green for decrease
                else:
                    colors_area.append(self.colors['danger'])  # Red for increase
            
            # Area chart with gradient fill
            fig.add_trace(
                go.Scatter(
                    x=dates[1:],
                    y=changes,
                    mode='lines',
                    name='Изменение',
                    line=dict(color=self.colors['info'], width=2),
                    fill='tozeroy',
                    fillcolor='rgba(23, 162, 184, 0.3)',
                    showlegend=False
                ),
                row=2, col=1
            )
            
            # Add markers for significant changes
            significant_changes = [(i, c) for i, c in enumerate(changes) if abs(c) > 0.5]
            if significant_changes:
                sig_dates = [dates[1:][i] for i, _ in significant_changes]
                sig_values = [c for _, c in significant_changes]
                sig_colors = [self.colors['success'] if c < 0 else self.colors['danger'] for c in sig_values]
                
                fig.add_trace(
                    go.Scatter(
                        x=sig_dates,
                        y=sig_values,
                        mode='markers',
                        marker=dict(size=12, color=sig_colors, symbol='diamond', line=dict(width=2, color='white')),
                        name='Значительные изменения',
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
                'font': {'size': 20, 'family': 'Arial, sans-serif'}
            },
            template='plotly_white',
            height=700,
            font={'family': 'Arial, sans-serif'},
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=60, r=40, t=120, b=60)
        )
        
        # Update axes
        fig.update_xaxes(title_text="Дата", row=1, col=1, showgrid=True, gridcolor='lightgray')
        fig.update_yaxes(title_text="Ставка (%)", row=1, col=1, showgrid=True, gridcolor='lightgray')
        fig.update_xaxes(title_text="Дата", row=2, col=1, showgrid=True, gridcolor='lightgray')
        fig.update_yaxes(
            title_text="Изменение (%)", 
            row=2, col=1, 
            showgrid=True, 
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='gray'
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
        
        colors = [self.colors['primary'], self.colors['secondary'], 
                  self.colors['info'], self.colors['success'], self.colors['warning']]
        
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
                    line=dict(color=colors[idx % len(colors)], width=2),
                    marker=dict(size=8)
                ))
        
        fig.update_layout(
            title={
                'text': 'Сравнение трендов нескольких банков',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Arial, sans-serif'}
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
                x=1.02
            ),
            margin=dict(l=60, r=150, t=80, b=60)
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
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
