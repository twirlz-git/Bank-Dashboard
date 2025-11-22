"""
modules/chart_generator_enhanced.py - Enhanced chart generation with modern visualizations
"""

import logging
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class EnhancedChartGenerator:
    """Generate modern, interactive charts with wow-effect"""

    def __init__(self):
        # Modern color palette inspired by financial dashboards
        self.colors = {
            'primary': '#1e3a8a',  # Deep blue
            'secondary': '#3b82f6',  # Bright blue
            'success': '#10b981',  # Emerald green
            'warning': '#f59e0b',  # Amber
            'danger': '#ef4444',  # Red
            'info': '#06b6d4',  # Cyan
            'purple': '#8b5cf6',  # Purple
            'pink': '#ec4899',  # Pink
            'gradient_colors': [
                '#667eea',  # Purple-blue
                '#764ba2',  # Deep purple
                '#f093fb',  # Pink
                '#4facfe',  # Sky blue
                '#43e97b',  # Lime green
                '#fa709a',  # Rose
                '#fee140',  # Yellow
                '#30cfd0'   # Turquoise
            ],
            'gradient_pairs': [
                ['#667eea', '#764ba2'],  # Purple gradient
                ['#f093fb', '#f5576c'],  # Pink gradient
                ['#4facfe', '#00f2fe'],  # Blue gradient
                ['#43e97b', '#38f9d7'],  # Green gradient
            ]
        }
        
        # Modern template
        self.template = {
            'layout': {
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'white',
                'font': {'family': 'Inter, system-ui, sans-serif', 'size': 12, 'color': '#1f2937'},
                'title': {'font': {'size': 24, 'color': '#111827', 'family': 'Inter'}},
                'hoverlabel': {
                    'bgcolor': 'white',
                    'font_size': 13,
                    'font_family': 'Inter'
                },
                'xaxis': {
                    'showgrid': True,
                    'gridcolor': '#f3f4f6',
                    'linecolor': '#e5e7eb'
                },
                'yaxis': {
                    'showgrid': True,
                    'gridcolor': '#f3f4f6',
                    'linecolor': '#e5e7eb'
                }
            }
        }

    def generate_radar_comparison(self, comparison_data: Dict[str, Any]) -> go.Figure:
        """
        Generate radar/spider chart for product comparison.
        Perfect for visualizing multiple parameters at once.
        """
        
        comparison_table = comparison_data.get('comparison_table')
        if comparison_table is None or comparison_table.empty:
            return self._create_empty_chart("Нет данных для сравнения")
        
        # Extract numeric parameters
        parameters = []
        bank_values = {}
        
        banks = comparison_table.columns[1:].tolist()
        
        for idx, param in enumerate(comparison_table.iloc[:, 0].tolist()):
            try:
                import re
                values = []
                is_numeric = True
                
                for bank in banks:
                    value_str = str(comparison_table.iloc[idx, comparison_table.columns.get_loc(bank)])
                    num_match = re.search(r'(\d+\.?\d*)', value_str)
                    if num_match:
                        values.append(float(num_match.group(1)))
                    else:
                        is_numeric = False
                        break
                
                if is_numeric and values:
                    # Normalize values to 0-100 scale for better radar visualization
                    max_val = max(values)
                    if max_val > 0:
                        normalized_values = [(v / max_val) * 100 for v in values]
                        parameters.append(param)
                        for bank, norm_val in zip(banks, normalized_values):
                            if bank not in bank_values:
                                bank_values[bank] = []
                            bank_values[bank].append(norm_val)
            except:
                continue
        
        if not parameters:
            return self._create_empty_chart("Нет числовых параметров для визуализации")
        
        # Create radar chart
        fig = go.Figure()
        
        gradient_colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b']
        
        for idx, bank in enumerate(banks):
            color = gradient_colors[idx % len(gradient_colors)]
            
            fig.add_trace(go.Scatterpolar(
                r=bank_values[bank] + [bank_values[bank][0]],  # Close the radar
                theta=parameters + [parameters[0]],
                fill='toself',
                name=bank,
                line=dict(color=color, width=2),
                fillcolor=self._add_alpha(color, 0.3),
                hovertemplate='<b>%{fullData.name}</b><br>%{theta}: %{r:.1f}<extra></extra>'
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showticklabels=False,
                    gridcolor='#e5e7eb'
                ),
                angularaxis=dict(
                    gridcolor='#e5e7eb'
                )
            ),
            showlegend=True,
            title={
                'text': '🎯 Сравнение по ключевым параметрам',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'family': 'Inter', 'color': '#111827'}
            },
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='#e5e7eb',
                borderwidth=1
            ),
            height=600,
            paper_bgcolor='white',
            font={'family': 'Inter'}
        )
        
        return fig

    def generate_heatmap_comparison(self, comparison_data: Dict[str, Any]) -> go.Figure:
        """
        Generate heatmap for visual comparison of parameters.
        Great for spotting patterns quickly.
        """
        
        comparison_table = comparison_data.get('comparison_table')
        if comparison_table is None or comparison_table.empty:
            return self._create_empty_chart("Нет данных для сравнения")
        
        # Extract numeric data
        parameters = []
        banks = comparison_table.columns[1:].tolist()
        values_matrix = []
        
        for idx, param in enumerate(comparison_table.iloc[:, 0].tolist()):
            try:
                import re
                row_values = []
                is_numeric = True
                
                for bank in banks:
                    value_str = str(comparison_table.iloc[idx, comparison_table.columns.get_loc(bank)])
                    num_match = re.search(r'(\d+\.?\d*)', value_str)
                    if num_match:
                        row_values.append(float(num_match.group(1)))
                    else:
                        is_numeric = False
                        break
                
                if is_numeric and row_values:
                    parameters.append(param)
                    # Normalize row to 0-1 scale
                    max_val = max(row_values)
                    if max_val > 0:
                        values_matrix.append([v / max_val for v in row_values])
                    else:
                        values_matrix.append(row_values)
            except:
                continue
        
        if not values_matrix:
            return self._create_empty_chart("Нет числовых параметров")
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=values_matrix,
            x=banks,
            y=parameters,
            colorscale=[
                [0, '#fee2e2'],    # Light red
                [0.25, '#fde68a'], # Light yellow
                [0.5, '#d9f99d'],  # Light green
                [0.75, '#86efac'], # Medium green
                [1, '#10b981']     # Strong green
            ],
            text=values_matrix,
            texttemplate='%{text:.1%}',
            textfont={"size": 12},
            hoverongaps=False,
            hovertemplate='<b>%{y}</b><br>%{x}: %{z:.1%}<extra></extra>',
            colorbar=dict(
                title="Относительная<br>ценность",
                titleside="right",
                tickformat=".0%"
            )
        ))
        
        fig.update_layout(
            title={
                'text': '🔥 Тепловая карта сравнения',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'family': 'Inter', 'color': '#111827'}
            },
            xaxis_title='Банк',
            yaxis_title='Параметр',
            height=500,
            font={'family': 'Inter'},
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig

    def generate_waterfall_trends(self, timeline: List[Dict[str, Any]]) -> go.Figure:
        """
        Generate waterfall chart showing cumulative changes.
        Perfect for understanding how changes accumulate over time.
        """
        
        if not timeline or len(timeline) < 2:
            return self._create_empty_chart("Недостаточно данных")
        
        # Extract data
        dates = [self._parse_date(item.get('date', '')) for item in timeline]
        rates = [item.get('rate', 0) for item in timeline]
        reasons = [item.get('reason', 'Н/Д') for item in timeline]
        
        # Calculate changes
        changes = [rates[0]]  # Starting point
        for i in range(1, len(rates)):
            changes.append(rates[i] - rates[i-1])
        
        # Create waterfall chart
        measure = ['absolute'] + ['relative'] * (len(changes) - 1)
        
        # Color coding: green for decreases (good), red for increases (bad) in interest rates
        colors = []
        for change in changes[1:]:
            if change < 0:
                colors.append('#10b981')  # Green - rate decreased
            else:
                colors.append('#ef4444')  # Red - rate increased
        colors = ['#3b82f6'] + colors  # Blue for initial
        
        fig = go.Figure(go.Waterfall(
            name="Изменение ставки",
            orientation="v",
            measure=measure,
            x=[d.strftime('%d.%m.%Y') for d in dates],
            y=changes,
            text=[f"{c:+.2f}%" if i > 0 else f"{c:.2f}%" for i, c in enumerate(changes)],
            textposition="outside",
            connector={"line": {"color": "#9ca3af", "width": 2, "dash": "dot"}},
            decreasing={"marker": {"color": "#10b981"}},
            increasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#3b82f6"}},
            hovertemplate='<b>%{x}</b><br>Изменение: %{y:.2f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': '📊 Водопад изменений процентной ставки',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'family': 'Inter', 'color': '#111827'}
            },
            xaxis_title='Дата',
            yaxis_title='Процентная ставка (%)',
            showlegend=False,
            height=550,
            font={'family': 'Inter'},
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
            yaxis=dict(showgrid=True, gridcolor='#f3f4f6')
        )
        
        return fig

    def generate_animated_timeline(self, timeline: List[Dict[str, Any]], title: str = "Динамика ставки") -> go.Figure:
        """
        Generate animated line chart with smooth transitions.
        Creates a wow-effect with animation.
        """
        
        if not timeline:
            return self._create_empty_chart("Недостаточно данных")
        
        # Extract data
        dates = [self._parse_date(item.get('date', '')) for item in timeline]
        rates = [item.get('rate', 0) for item in timeline]
        reasons = [item.get('reason', 'Н/Д') for item in timeline]
        
        # Create dataframe for animation
        df = pd.DataFrame({
            'date': dates,
            'rate': rates,
            'reason': reasons
        })
        
        # Create figure with gradient fill
        fig = go.Figure()
        
        # Add area chart with gradient
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['rate'],
            mode='lines',
            name='Ставка',
            line=dict(
                color='#667eea',
                width=0
            ),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)',
            hoverinfo='skip'
        ))
        
        # Add main line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['rate'],
            mode='lines+markers',
            name='Ставка',
            line=dict(
                color='#667eea',
                width=4,
                shape='spline'
            ),
            marker=dict(
                size=14,
                color='#764ba2',
                line=dict(width=3, color='white'),
                symbol='circle'
            ),
            hovertemplate='<b>Дата:</b> %{x|%d.%m.%Y}<br><b>Ставка:</b> %{y:.2f}%<br><b>Причина:</b> %{text}<extra></extra>',
            text=df['reason']
        ))
        
        # Add annotations for key points
        if len(df) > 0:
            # Annotate first point
            fig.add_annotation(
                x=df['date'].iloc[0],
                y=df['rate'].iloc[0],
                text=f"Начало: {df['rate'].iloc[0]:.1f}%",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
                font=dict(size=11, color='#374151'),
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='#e5e7eb',
                borderwidth=1
            )
            
            # Annotate last point
            fig.add_annotation(
                x=df['date'].iloc[-1],
                y=df['rate'].iloc[-1],
                text=f"Сейчас: {df['rate'].iloc[-1]:.1f}%",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
                font=dict(size=11, color='#374151'),
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='#e5e7eb',
                borderwidth=1
            )
        
        fig.update_layout(
            title={
                'text': f'✨ {title}',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 22, 'family': 'Inter', 'color': '#111827'}
            },
            xaxis_title='Период',
            yaxis_title='Процентная ставка (%)',
            hovermode='x unified',
            showlegend=False,
            height=550,
            font={'family': 'Inter'},
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridcolor='#f3f4f6',
                linecolor='#e5e7eb'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#f3f4f6',
                linecolor='#e5e7eb',
                zeroline=True,
                zerolinecolor='#d1d5db'
            ),
            margin=dict(l=60, r=40, t=100, b=60)
        )
        
        return fig

    def generate_gauge_metric(self, current_rate: float, competitor_rate: float, 
                            bank_name: str = "Конкурент") -> go.Figure:
        """
        Generate gauge chart comparing rates.
        Visual indicator of competitiveness.
        """
        
        # Calculate delta
        delta = current_rate - competitor_rate
        
        # Determine color based on delta (lower is better for customers)
        if delta < -1:
            color = "#10b981"  # Green - much better
        elif delta < 0:
            color = "#6ee7b7"  # Light green - better
        elif delta < 1:
            color = "#fbbf24"  # Yellow - similar
        else:
            color = "#ef4444"  # Red - worse
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Ставка vs {bank_name}", 'font': {'size': 20, 'family': 'Inter'}},
            delta={'reference': competitor_rate, 'suffix': '%'},
            gauge={
                'axis': {'range': [None, max(current_rate, competitor_rate) * 1.5], 'ticksuffix': '%'},
                'bar': {'color': color, 'thickness': 0.8},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#e5e7eb",
                'steps': [
                    {'range': [0, competitor_rate], 'color': '#f3f4f6'},
                ],
                'threshold': {
                    'line': {'color': "#374151", 'width': 4},
                    'thickness': 0.75,
                    'value': competitor_rate
                }
            }
        ))
        
        fig.update_layout(
            height=400,
            font={'family': 'Inter', 'size': 14},
            paper_bgcolor='white'
        )
        
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
            font=dict(size=16, color="#9ca3af", family='Inter')
        )
        
        fig.update_layout(
            template='plotly_white',
            height=400,
            xaxis=dict(showticklabels=False, showgrid=False),
            yaxis=dict(showticklabels=False, showgrid=False),
            paper_bgcolor='white'
        )
        
        return fig

    def _add_alpha(self, hex_color: str, alpha: float) -> str:
        """Add alpha channel to hex color"""
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        # Convert to RGB
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f'rgba({r}, {g}, {b}, {alpha})'
