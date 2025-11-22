"""
modules/report_generator.py - Generate XLSX and JSON reports with chart support
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.cell import MergedCell
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as XLImage
from io import BytesIO
import tempfile
import os
import json

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate XLSX and JSON format reports with chart visualization"""
    
    def __init__(self):
        """Initialize report generator"""
        try:
            from modules.chart_generator import ChartGenerator
            self.chart_generator = ChartGenerator()
            self.charts_enabled = True
        except ImportError:
            logger.warning("ChartGenerator not available, charts will be disabled")
            self.chart_generator = None
            self.charts_enabled = False
    
    def _convert_value_for_excel(self, value: Any) -> Any:
        """
        Convert complex data types to Excel-compatible formats.
        
        Args:
            value: Value to convert
            
        Returns:
            Excel-compatible value (str, int, float, bool, or None)
        """
        # Handle None
        if value is None:
            return "Н/Д"
        
        # Handle dict - convert to readable string
        if isinstance(value, dict):
            try:
                # Format dict as key: value pairs
                items = [f"{k}: {v}" for k, v in value.items()]
                return "; ".join(items)
            except:
                return str(value)
        
        # Handle list/tuple - convert to comma-separated string
        if isinstance(value, (list, tuple)):
            try:
                return ", ".join(str(item) for item in value)
            except:
                return str(value)
        
        # Handle bool
        if isinstance(value, bool):
            return "Да" if value else "Нет"
        
        # Handle datetime
        if isinstance(value, datetime):
            return value.strftime("%d.%m.%Y %H:%M")
        
        # Handle numeric types - return as is
        if isinstance(value, (int, float)):
            return value
        
        # Handle str - return as is
        if isinstance(value, str):
            return value
        
        # For any other type - convert to string
        try:
            return str(value)
        except:
            return "Н/Д"
    
    def generate_xlsx_comparison(self, comparison_data: Dict[str, Any]) -> BytesIO:
        """Generate XLSX file with comparison table and optional chart"""
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Сравнение"
        
        # Add title
        ws['A1'] = "Сравнение банковских продуктов"
        ws['A1'].font = Font(size=14, bold=True)
        ws.merge_cells('A1:D1')
        
        # Add timestamp
        ws['A2'] = f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        ws.merge_cells('A2:D2')
        
        # Add comparison table
        comparison_df = comparison_data.get("comparison_table")
        if comparison_df is not None:
            for r_idx, row in enumerate(comparison_df.values, start=4):
                for c_idx, value in enumerate(row, start=1):
                    # Convert value to Excel-compatible format
                    excel_value = self._convert_value_for_excel(value)
                    ws.cell(row=r_idx, column=c_idx, value=excel_value)
            
            # Add headers
            headers = comparison_df.columns
            for c_idx, header in enumerate(headers, start=1):
                cell = ws.cell(row=3, column=c_idx, value=str(header))
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # Add insights sheet
        insights_ws = wb.create_sheet("Анализ")
        insights_ws['A1'] = "Ключевые выводы"
        insights_ws['A1'].font = Font(size=12, bold=True)
        
        insights = comparison_data.get("insights", [])
        for idx, insight in enumerate(insights, start=2):
            insights_ws[f'A{idx}'] = str(insight)
        
        # Add recommendation
        recommendation = comparison_data.get("recommendation", "Недостаточно данных")
        insights_ws['A10'] = "Рекомендация:"
        insights_ws['A10'].font = Font(bold=True)
        insights_ws['A11'] = str(recommendation)
        
        # Add chart if available
        if self.charts_enabled and self.chart_generator:
            try:
                chart_ws = wb.create_sheet("График")
                chart_ws['A1'] = "Визуализация сравнения"
                chart_ws['A1'].font = Font(size=12, bold=True)
                
                # Generate comparison chart
                fig = self.chart_generator.generate_comparison_chart(comparison_data)
                
                # Save chart as image and embed
                img_path = self._save_chart_temp(fig)
                if img_path:
                    img = XLImage(img_path)
                    chart_ws.add_image(img, 'A3')
                    os.unlink(img_path)  # Clean up temp file
                    
            except Exception as e:
                logger.error(f"Failed to add comparison chart: {e}")
        
        # Auto-adjust column widths
        for sheet_name in wb.sheetnames:
            worksheet = wb[sheet_name]
            for col_idx, column in enumerate(worksheet.columns, start=1):
                max_length = 0
                column_letter = get_column_letter(col_idx)
                for cell in column:
                    if isinstance(cell, MergedCell):
                        continue
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output
    
    def generate_xlsx_trends(self, trends_data: Dict[str, Any]) -> BytesIO:
        """Generate XLSX file with trends analysis and charts"""
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Тренды"
        
        # Add title
        ws['A1'] = "Анализ трендов"
        ws['A1'].font = Font(size=14, bold=True)
        ws.merge_cells('A1:D1')
        
        # Add period info
        bank = trends_data.get('bank', 'Н/Д')
        product_type = trends_data.get('product_type', 'Н/Д')
        start_date = trends_data.get('start_date', 'Н/Д')
        end_date = trends_data.get('end_date', 'Н/Д')
        
        ws['A2'] = f"Банк: {bank}"
        ws['A3'] = f"Продукт: {product_type}"
        ws['A4'] = f"Период: {start_date} - {end_date}"
        
        # Add timeline table if available
        timeline = trends_data.get("timeline", [])
        if timeline:
            # Headers with better styling
            headers = ["Дата", "Ставка (%)", "Причина", "Достоверность", "Источник"]
            for c_idx, header in enumerate(headers, start=1):
                cell = ws.cell(row=6, column=c_idx, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            # Data rows
            for r_idx, item in enumerate(timeline, start=7):
                ws[f'A{r_idx}'] = item.get("date", "Н/Д")
                ws[f'B{r_idx}'] = item.get("rate", "Н/Д")
                ws[f'C{r_idx}'] = item.get("reason", "Н/Д")
                ws[f'D{r_idx}'] = f"{item.get('confidence', 0.5):.0%}"
                ws[f'E{r_idx}'] = item.get("source", "Н/Д")
        
        # Add analysis sheet
        analysis = trends_data.get('analysis', {})
        if analysis and analysis.get('status') == 'success':
            analysis_ws = wb.create_sheet("Статистика")
            analysis_ws['A1'] = "Статистический анализ"
            analysis_ws['A1'].font = Font(size=12, bold=True)
            
            stats = [
                ("Начальное значение", f"{analysis.get('start_value', 0):.2f}%"),
                ("Конечное значение", f"{analysis.get('end_value', 0):.2f}%"),
                ("Среднее значение", f"{analysis.get('average_value', 0):.2f}%"),
                ("Минимум", f"{analysis.get('min_value', 0):.2f}%"),
                ("Максимум", f"{analysis.get('max_value', 0):.2f}%"),
                ("Общее изменение", f"{analysis.get('total_change', 0):+.2f}%"),
                ("Изменение (%)", f"{analysis.get('change_percentage', 0):+.1f}%"),
                ("Точек данных", str(analysis.get('data_points', 0))),
                ("Точек изменения", str(analysis.get('change_points', 0))),
                ("Средняя достоверность", f"{analysis.get('average_confidence', 0):.0%}")
            ]
            
            for idx, (label, value) in enumerate(stats, start=3):
                analysis_ws[f'A{idx}'] = label
                analysis_ws[f'A{idx}'].font = Font(bold=True)
                analysis_ws[f'B{idx}'] = value
        
        # Add summary sheet
        summary_ws = wb.create_sheet("Выводы")
        summary_ws['A1'] = "Итоговый анализ"
        summary_ws['A1'].font = Font(size=12, bold=True)
        
        summary = trends_data.get('summary', 'Недостаточно данных')
        # Split summary by lines and add to cells
        summary_lines = summary.split('\n')
        for idx, line in enumerate(summary_lines, start=3):
            summary_ws[f'A{idx}'] = line
            summary_ws[f'A{idx}'].alignment = Alignment(wrap_text=True)
        
        # Add charts if available
        if self.charts_enabled and self.chart_generator and timeline:
            try:
                # Create charts sheet
                charts_ws = wb.create_sheet("Графики")
                charts_ws['A1'] = "Визуализация трендов"
                charts_ws['A1'].font = Font(size=12, bold=True)
                
                # Generate timeline chart
                fig1 = self.chart_generator.generate_timeline_chart(timeline, f"Динамика {product_type} - {bank}")
                img_path1 = self._save_chart_temp(fig1)
                if img_path1:
                    img1 = XLImage(img_path1)
                    img1.width = 800
                    img1.height = 400
                    charts_ws.add_image(img1, 'A3')
                    os.unlink(img_path1)
                
                # Generate detailed analysis chart if analysis available
                if analysis and analysis.get('status') == 'success':
                    fig2 = self.chart_generator.generate_trend_analysis_chart(timeline, analysis)
                    img_path2 = self._save_chart_temp(fig2)
                    if img_path2:
                        img2 = XLImage(img_path2)
                        img2.width = 800
                        img2.height = 600
                        charts_ws.add_image(img2, 'A28')  # Place below first chart
                        os.unlink(img_path2)
                        
            except Exception as e:
                logger.error(f"Failed to add trend charts: {e}")
        
        # Auto-adjust column widths
        for sheet_name in wb.sheetnames:
            worksheet = wb[sheet_name]
            for col_idx, column in enumerate(worksheet.columns, start=1):
                max_length = 0
                column_letter = get_column_letter(col_idx)
                for cell in column:
                    if isinstance(cell, MergedCell):
                        continue
                    try:
                        if cell.value and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                worksheet.column_dimensions[column_letter].width = min(max_length + 2, 80)
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output
    
    def _save_chart_temp(self, fig) -> Optional[str]:
        """Save chart to temporary file and return path"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Save chart as PNG
            fig.write_image(temp_path, format='png', width=800, height=500)
            
            return temp_path
        except Exception as e:
            logger.error(f"Failed to save chart to temp file: {e}")
            return None
    
    def get_filename(self, mode: str, bank: str = "", product_type: str = "") -> str:
        """Generate filename for report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if mode == "urgent":
            return f"сравнение_{bank}_{timestamp}.xlsx"
        else:
            return f"тренды_{bank}_{product_type}_{timestamp}.xlsx"
