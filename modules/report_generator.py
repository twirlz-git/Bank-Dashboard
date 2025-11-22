"""
modules/report_generator.py - Generate XLSX and JSON reports
"""

import logging
from typing import Dict, Any
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from io import BytesIO

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate XLSX and JSON format reports"""
    
    def generate_xlsx_comparison(self, comparison_data: Dict[str, Any]) -> BytesIO:
        """Generate XLSX file with comparison table"""
        
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
                    ws.cell(row=r_idx, column=c_idx, value=value)
            
            # Add headers
            headers = comparison_df.columns
            for c_idx, header in enumerate(headers, start=1):
                cell = ws.cell(row=3, column=c_idx, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # Add insights sheet
        insights_ws = wb.create_sheet("Анализ")
        insights_ws['A1'] = "Ключевые выводы"
        insights_ws['A1'].font = Font(size=12, bold=True)
        
        insights = comparison_data.get("insights", [])
        for idx, insight in enumerate(insights, start=2):
            insights_ws[f'A{idx}'] = insight
        
        # Add recommendation
        recommendation = comparison_data.get("recommendation", "Недостаточно данных")
        insights_ws['A10'] = "Рекомендация:"
        insights_ws['A10'].font = Font(bold=True)
        insights_ws['A11'] = recommendation
        
        # Auto-adjust column widths
        for ws in wb.sheetnames:
            worksheet = wb[ws]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
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
        """Generate XLSX file with trends analysis"""
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Тренды"
        
        # Add title
        ws['A1'] = "Анализ трендов"
        ws['A1'].font = Font(size=14, bold=True)
        ws.merge_cells('A1:D1')
        
        # Add timeline table if available
        timeline = trends_data.get("timeline", [])
        if timeline:
            ws['A3'] = "Дата"
            ws['B3'] = "Значение"
            ws['C3'] = "Причина"
            
            for idx, item in enumerate(timeline, start=4):
                ws[f'A{idx}'] = item.get("date", "Н/Д")
                ws[f'B{idx}'] = item.get("value", "Н/Д")
                ws[f'C{idx}'] = item.get("reason", "Н/Д")
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output
    
    def get_filename(self, mode: str, bank: str = "", product_type: str = "") -> str:
        """Generate filename for report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if mode == "urgent":
            return f"сравнение_{bank}_{timestamp}.xlsx"
        else:
            return f"тренды_{bank}_{product_type}_{timestamp}.xlsx"
