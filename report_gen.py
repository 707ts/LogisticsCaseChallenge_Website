# report_gen.py

import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    PageBreak, Image as RLImage, KeepTogether
)
from reportlab.lib import colors
from reportlab.pdfgen import canvas


# ============================================================================
# CONFIGURATION
# ============================================================================
PARQUET_PATH = r"ship_report_imo_2024.parquet"
OUTPUT_DIR = ""
COVER_IMAGE_PATH = "logo.png"
# ============================================================================


class NumberedCanvas(canvas.Canvas):
    """Canvas with page numbers"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        self.drawRightString(
            A4[0] - 1.5*cm,
            1*cm,
            f"Page {self._pageNumber} of {page_count}"
        )


class ShipReportGenerator:
    """Professional PDF Generator for Ship Reports"""
    
    def __init__(self):
        self.parquet_path = Path(PARQUET_PATH)
        self.output_dir = Path(OUTPUT_DIR) if OUTPUT_DIR else Path(".")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cover_image_path = Path(COVER_IMAGE_PATH) if COVER_IMAGE_PATH else None
        
        self.df = pd.read_parquet(self.parquet_path)
        self.styles = self._initialize_styles()
        
        # Colors
        self.primary_color = colors.HexColor('#1a4d7a')
        self.secondary_color = colors.HexColor('#2e7ab8')
        self.accent_color = colors.HexColor('#f39c12')
        self.success_color = colors.HexColor('#27ae60')
        self.danger_color = colors.HexColor('#e74c3c')
    
    def _initialize_styles(self):
        styles = getSampleStyleSheet()
        
        # Custom Styles
        custom_styles = {
            'CoverTitle': ParagraphStyle(
                name='CoverTitle',
                parent=styles['Heading1'],
                fontSize=32,
                textColor=colors.HexColor('#1a4d7a'),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                leading=40
            ),
            'CoverSubtitle': ParagraphStyle(
                name='CoverSubtitle',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=colors.HexColor('#2e7ab8'),
                spaceAfter=10,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ),
            'SectionHeader': ParagraphStyle(
                name='SectionHeader',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1a4d7a'),
                spaceAfter=15,
                spaceBefore=10,
                fontName='Helvetica-Bold',
                borderWidth=2,
                borderColor=colors.HexColor('#2e7ab8'),
                borderPadding=8,
                backColor=colors.HexColor('#e8f4f8')
            ),
            'BodyText': ParagraphStyle(
                name='BodyText',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_JUSTIFY,
                spaceAfter=12,
                leading=16,
                textColor=colors.HexColor('#333333')
            ),
            'TableHeader': ParagraphStyle(
                name='TableHeader',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.whitesmoke,
                fontName='Helvetica-Bold',
                alignment=TA_LEFT
            ),
            'TableCell': ParagraphStyle(
                name='TableCell',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                alignment=TA_LEFT
            )
        }
        
        for name, style in custom_styles.items():
            try:
                styles.add(style)
            except:
                pass
        
        return styles
    
    def _format_flag_reason(self, flag_reason: str) -> str:
        """
        Konvertiere technische Flag Reasons in lesbare Texte
        
        Args:
            flag_reason: Roher flag_reason Wert
            
        Returns:
            Formatierter, lesbarer Text
        """
        if pd.isna(flag_reason) or flag_reason == 'N/A':
            return 'No reason specified'
        
        # Konvertiere zu String falls es ein anderer Typ ist
        reason = str(flag_reason).strip()
        
        # Mapping von technischen Codes zu lesbaren Texten
        reason_map = {
            'ok': 'Within normal parameters',
            'rel_residual>30%': 'Relative deviation exceeds 30% threshold',
            'abs_residual>p95': 'Absolute deviation exceeds 95th percentile',
            'rel_residual>30': 'Relative deviation exceeds 30% threshold',
            'abs_residual>95': 'Absolute deviation exceeds 95th percentile',
        }
        
        # Wenn exakte Übereinstimmung gefunden wird
        if reason in reason_map:
            return reason_map[reason]
        
        # Versuche Teilübereinstimmungen
        if 'rel_residual' in reason.lower() and '30' in reason:
            return 'Relative deviation exceeds 30% threshold'
        if 'abs_residual' in reason.lower() and ('p95' in reason or '95' in reason):
            return 'Absolute deviation exceeds 95th percentile'
        if reason.lower() == 'ok':
            return 'Within normal parameters'
        
        # Falls nichts matched, gebe formatierten Original-Text zurück
        # Ersetze technische Symbole durch lesbarere Versionen
        formatted = reason.replace('_', ' ').replace('>', ' exceeds ')
        formatted = formatted.replace('p95', '95th percentile')
        formatted = formatted.replace('rel residual', 'Relative deviation')
        formatted = formatted.replace('abs residual', 'Absolute deviation')
        
        # Capitalize first letter
        if formatted:
            formatted = formatted[0].upper() + formatted[1:]
        
        return formatted
    
    def _get_ship_record(self, imo: str):
        ship_data = self.df[self.df['IMO'].astype(str).str.strip() == str(imo).strip()]
        if ship_data.empty:
            raise ValueError(f"No data found for IMO {imo}")
        return ship_data.iloc[0].to_dict()
    
    def _create_cover_page(self, story, ship_data, imo):
        """Modern cover design"""
        # Logo centered
        if self.cover_image_path and self.cover_image_path.exists():
            try:
                img = RLImage(
                    str(self.cover_image_path), 
                    width=12*cm,
                    height=6*cm,
                    kind='proportional'
                )
                story.append(Spacer(1, 3*cm))
                story.append(img)
            except Exception as e:
                print(f"Warning: Logo not loaded: {e}")
        
        story.append(Spacer(1, 3*cm))
        
        # Title
        story.append(Paragraph("Emissions Analysis Report", self.styles['CoverTitle']))
        story.append(Spacer(1, 1*cm))
        
        # Ship information
        ship_name = ship_data.get('ship_name', 'N/A')
        story.append(Paragraph(ship_name, self.styles['CoverSubtitle']))
        story.append(Spacer(1, 0.3*cm))
        
        info_text = f"<font size=12>IMO: <b>{imo}</b></font>"
        story.append(Paragraph(info_text, self.styles['Normal']))
        
        story.append(Spacer(1, 0.5*cm))
        
        vessel_type = ship_data.get('mrv_ship_type', 'N/A')
        type_text = f"<font size=10 color='#666666'>{vessel_type}</font>"
        story.append(Paragraph(type_text, self.styles['Normal']))
        
        # Date at bottom
        story.append(Spacer(1, 4*cm))
        today = datetime.now().strftime("%B %d, %Y")
        date_text = f"<font size=10><i>Generated on {today}</i></font>"
        story.append(Paragraph(date_text, self.styles['Normal']))
        
        story.append(PageBreak())
    
    def _create_styled_table(self, data, col_widths=None, highlight_last_rows=None):
        """
        Create professionally styled table
        
        Args:
            data: Table data
            col_widths: Column widths
            highlight_last_rows: 'green', 'red' or None for last 2 rows
        """
        if col_widths is None:
            col_widths = [8*cm, 8*cm]
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        base_style = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
            ('TOPPADDING', (0, 0), (-1, 0), 14),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.secondary_color),
            
            # Alternating rows (except last 2)
            ('ROWBACKGROUNDS', (0, 1), (-1, -3), [colors.white, colors.HexColor('#f8f9fa')]),
        ]
        
        # Highlight for last 2 rows (assessment)
        if highlight_last_rows == 'red':
            base_style.extend([
                ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#ffe6e6')),
                ('TEXTCOLOR', (0, -2), (-1, -1), colors.HexColor('#721c24')),
                ('FONTNAME', (0, -2), (0, -2), 'Helvetica-Bold'),
                ('FONTNAME', (1, -2), (1, -2), 'Helvetica-Bold'),
                ('LINEABOVE', (0, -2), (-1, -2), 2, colors.HexColor('#e74c3c')),
            ])
        elif highlight_last_rows == 'green':
            base_style.extend([
                ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#d4edda')),
                ('TEXTCOLOR', (0, -2), (-1, -1), colors.HexColor('#155724')),
                ('FONTNAME', (0, -2), (0, -2), 'Helvetica-Bold'),
                ('FONTNAME', (1, -2), (1, -2), 'Helvetica-Bold'),
                ('LINEABOVE', (0, -2), (-1, -2), 2, colors.HexColor('#27ae60')),
            ])
        
        table.setStyle(TableStyle(base_style))
        return table
    
    def generate_pdf_report(self, imo: str, report_text: str) -> str:
        ship_data = self._get_ship_record(imo)
        
        output_filename = f"Ship_Report_{imo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = self.output_dir / output_filename
        
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2.5*cm
        )
        
        story = []
        
        # === COVER PAGE ===
        self._create_cover_page(story, ship_data, imo)
        
        # === ANALYSIS REPORT (2nd page) ===
        story.append(Paragraph("1. Analysis Report", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.5*cm))
        
        for para in report_text.split('\n\n'):
            if para.strip():
                story.append(Paragraph(para.strip(), self.styles['BodyText']))
                story.append(Spacer(1, 0.3*cm))
        
        # Footer after report text on same page
        story.append(Spacer(1, 1*cm))
        timestamp = datetime.now().strftime("%B %d, %Y at %H:%M")
        footer = f"<font size=9 color='#888888'><i>Automatically generated on {timestamp}</i></font>"
        story.append(Paragraph(footer, self.styles['Normal']))
        
        story.append(PageBreak())
        
        # === MASTER DATA ===
        story.append(Paragraph("2. Master Data", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.5*cm))
        
        master_data = [['Attribute', 'Value']]
        for label, key in [
            ('IMO', 'IMO'),
            ('Ship Name', 'ship_name'),
            ('Vessel Type (AIS)', 'VesselType'),
            ('Vessel Type (MRV)', 'mrv_ship_type'),
            ('Report Year', 'report_year')
        ]:
            value = ship_data.get(key, 'N/A')
            if isinstance(value, float) and key != 'VesselType':
                value = f"{int(value)}"
            master_data.append([label, str(value)])
        
        story.append(self._create_styled_table(master_data))
        story.append(PageBreak())
        
        # === AIS DATA ===
        story.append(Paragraph("3. AIS Data", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.5*cm))
        
        ais_data = [['Parameter', 'Value']]
        for label, key in [
            ('Total Distance', 'ais_distance_nm_total'),
            ('Operating Time', 'ais_time_hours_total'),
            ('AIS Messages', 'ais_points'),
            ('Average Speed', 'sog_mean_kn'),
            ('Median Speed', 'sog_p50_kn'),
            ('95th Percentile Speed', 'sog_p95_kn'),
            ('Navigation Activity', 'moving_share'),
            ('Ship Length', 'Length'),
            ('Ship Width', 'Width'),
            ('Draft (Median)', 'draft_m_median')
        ]:
            value = ship_data.get(key, 'N/A')
            if isinstance(value, float):
                if 'share' in key:
                    value = f"{value*100:.1f} %"
                elif 'distance' in key:
                    value = f"{value:,.0f} nm"
                elif 'time_hours' in key:
                    value = f"{value:.1f} h"
                elif 'points' in key:
                    value = f"{int(value):,}"
                elif 'Length' == key or 'Width' == key or 'draft' in key:
                    value = f"{value:.1f} m"
                elif 'sog' in key:
                    value = f"{value:.2f} kn"
                else:
                    value = f"{value:.2f}"
            ais_data.append([label, str(value)])
        
        story.append(self._create_styled_table(ais_data))
        story.append(PageBreak())
        
        # === EMISSIONS DATA ===
        story.append(Paragraph("4. Emissions and Assessment Data", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.5*cm))
        
        emissions_data = [['Parameter', 'Value']]
        for label, key in [
            ('MRV CO2 Intensity', 'y_mrv_co2_per_nm_kg'),
            ('Modeled CO2 Intensity', 'y_pred_co2_per_nm_kg'),
            ('Deviation (Absolute)', 'residual_kg'),
            ('Deviation (Relative)', 'residual_pct')
        ]:
            value = ship_data.get(key, 'N/A')
            if isinstance(value, float):
                if 'pct' in key:
                    value = f"{value*100:.1f} %"
                else:
                    value = f"{value:.2f} kg/nm"
            emissions_data.append([label, str(value)])
        
        # Assessment mit formatierter Reason
        flag_color = ship_data.get('flag_color', 'N/A')
        flag_reason = ship_data.get('flag_reason', 'N/A')
        flag_display = 'COMPLIANT' if flag_color == 'GREEN' else 'ALERT'
        
        # Formatiere die Reason schön
        formatted_reason = self._format_flag_reason(flag_reason)
        
        emissions_data.append(['Assessment Status', flag_display])
        emissions_data.append(['Reason', formatted_reason])
        
        # Create table with highlight
        highlight_color = 'green' if flag_color == 'GREEN' else 'red'
        emissions_table = self._create_styled_table(emissions_data, highlight_last_rows=highlight_color)
        
        story.append(emissions_table)
        
        # Build with page numbers
        doc.build(story, canvasmaker=NumberedCanvas)
        
        print(f"PDF created: {output_path}")
        return str(output_path)


# ============================================================================
# API
# ============================================================================

_generator = None

def init_generator():
    global _generator
    if _generator is None:
        _generator = ShipReportGenerator()
    return _generator

def generate_report_pdf(imo: str, report_text: str) -> str:
    generator = init_generator()
    return generator.generate_pdf_report(imo, report_text)


# ============================================================================
# TERMINAL
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python report_gen.py <imo> '<report_text>'")
        print("\nExample:")
        print("  python report_gen.py 1014618 'Ship shows anomalies...'")
        sys.exit(1)
    
    imo = sys.argv[1]
    report_text = sys.argv[2]
    
    try:
        pdf_path = generate_report_pdf(imo, report_text)
        print(f"Report: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
