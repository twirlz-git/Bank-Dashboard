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
            'hist_palette': [
                '#FF6B6B', '#FFA07A', '#FFD93D', '#6BCF7F', 
                '#4ECDC4', '#45B7D1', '#5E60CE', '#9B5DE5', '#D0F4DE', '#FEC8D8', '#FF9A8B'
            ]
        }

    def generate_timeline_chart(self, timeline: List[Dict[str, Any]], title: str = "Динамика изменения ставки") -> go.Figure:
        # ... (same as before)
        pass

    def generate_comparison_chart(self, comparison_data: Dict[str, Any]) -> go.Figure:
        # ... (same as before)
        pass

    def generate_trend_analysis_chart(self, timeline: List[Dict[str, Any]], analysis: Dict[str, Any]) -> go.Figure:
        if not timeline:
            return self._create_empty_chart("Недостаточно данных для анализа")
        
        dates = [self._parse_date(item.get('date', '')) for item in timeline]
        rates = [item.get('rate', 0) for item in timeline]
        
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.65, 0.35],
            subplot_titles=("Динамика процентной ставки", "Распределение изменений"),
            vertical_spacing=0.12
        )
        
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
        
        if len(rates) > 1:
            changes = [rates[i] - rates[i-1] for i in range(1, len(rates))]
            # Palette with a lot of colors for smooth transition
            bar_colors = []
            palette = self.colors['hist_palette']
            for idx, c in enumerate(changes):
                bar_colors.append(palette[idx % len(palette)])
            
            fig.add_trace(
                go.Bar(
                    x=dates[1:],
                    y=changes,
                    name='Изменение',
                    marker=dict(
                        color=bar_colors,
                        line=dict(color='rgba(255,255,255,0.6)', width=1),
                        opacity=0.95
                    ),
                    hovertemplate='<b>Дата:</b> %{x}<br><b>Изменение:</b> %{y:.2f}%<extra></extra>',
                    width=0.3, # This makes bars thinner
                    offset=0.2 # Slight shift to separate visually
                ),
                row=2, col=1
            )
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
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(200,200,200,0.5)',
                borderwidth=1
            ),
            margin=dict(l=60, r=40, t=120, b=60),
            plot_bgcolor='rgba(240,240,240,0.3)'
        )
        fig.update_xaxes(title_text="Дата", row=1, col=1, showgrid=True, gridcolor='rgba(200,200,200,0.3)')
        fig.update_yaxes(title_text="Ставка (%)", row=1, col=1, showgrid=True, gridcolor='rgba(200,200,200,0.3)')
        fig.update_xaxes(title_text="Дата", row=2, col=1, showgrid=False)
        fig.update_yaxes(title_text="Изменение (%)", row=2, col=1, showgrid=True, gridcolor='rgba(200,200,200,0.3)', zeroline=True, zerolinewidth=2, zerolinecolor='rgba(100,100,100,0.5)')
        return fig

    def generate_multiple_banks_comparison(self, banks_data: List[Dict[str, Any]]) -> go.Figure:
        # ... (same as before)
        pass

    def _parse_date(self, date_str: str) -> datetime:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return datetime.now()

    def _create_empty_chart(self, message: str) -> go.Figure:
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
        try:
            img_bytes = fig.to_image(format=format, engine='kaleido')
            img_base64 = base64.b64encode(img_bytes).decode()
            return f"data:image/{format};base64,{img_base64}"
        except Exception as e:
            logger.error(f"Failed to save chart to base64: {e}")
            return ""

    def save_chart_html(self, fig: go.Figure) -> str:
        return fig.to_html(include_plotlyjs='cdn', div_id='chart')
