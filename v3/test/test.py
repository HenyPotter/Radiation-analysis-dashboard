from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import json
import os
from reportlab.platypus import Spacer
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Image, Paragraph
)
from reportlab.lib.enums import TA_CENTER

order_number = "123456789"
gras_version = "5.0.1"
generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
title = "Simulace zařízení UIEHTGUWEIFGHS298"
logo_path = "logo.png"

pdfmetrics.registerFont(TTFont('ArialNarrow', 'fonts/arialnarrow.ttf'))
pdfmetrics.registerFont(TTFont('ArialNarrowBold', 'fonts/arialnarrow_bold.ttf'))
pdfmetrics.registerFont(TTFont('ArialNarrowBoldItalic', 'fonts/arialnarrow_bolditalic.ttf'))

font_basic = "ArialNarrow"
font_bold = "ArialNarrowBold"
font_bolditalic = "ArialNarrowBoldItalic"

bold_italic = ParagraphStyle("Cell", fontName=font_bolditalic, fontSize=14, alignment=TA_CENTER, textColor=colors.teal, leading=20)
bold_title = ParagraphStyle("Cell", fontName=font_bold, fontSize=18, alignment=TA_CENTER, textColor=colors.teal, leading=24)
cell_style = ParagraphStyle("Cell", fontName=font_basic, fontSize=10, alignment=TA_CENTER, textColor=colors.teal, leading=14)
header_style = ParagraphStyle("Heading1", fontName=font_bold, fontSize=14, textColor=colors.black, spaceAfter=8)
normal_style = ParagraphStyle("Normal", fontName=font_basic, fontSize=10, leading=14)
highlight_style = ParagraphStyle("Highlight", fontName=font_basic, fontSize=10, textColor=colors.red)

doc = SimpleDocTemplate(
    "report_header_stretched.pdf",
    pagesize=A4,
    leftMargin=20*mm, rightMargin=20*mm,
    topMargin=20*mm, bottomMargin=20*mm
)

img_reader = ImageReader(logo_path)
orig_width, orig_height = img_reader.getSize()
pixel_to_mm = 25.4 / 72
orig_width_mm = orig_width * pixel_to_mm
orig_height_mm = orig_height * pixel_to_mm
col_width = 68 * mm
new_width = col_width * 0.40
new_height = orig_height_mm / orig_width_mm * new_width

logo = Image(logo_path)
logo.drawWidth = new_width
logo.drawHeight = new_height

data = [
    [logo, Paragraph("GRAS SIMULATION SUMMARY ", bold_italic), Paragraph("Order number:<br/>" + order_number, cell_style)],
    ["", Paragraph(title, bold_title), Paragraph("Generated on:<br/>" + generated_date, cell_style)],
]
col_widths = [34 * mm, 102 * mm, 34 * mm]
table = Table(data, colWidths=col_widths)
table.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 1, colors.teal),
    ("SPAN", (0, 0), (0, 1)),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))

content = [table]
content.append(Spacer(1, 12))
content.append(Paragraph("1. SCOPE OF THE SIMULATION", header_style))
content.append(Paragraph(
    f"This document presents the results of computer simulations for radiation analysis performed using a local copy of GRAS "
    f"<b><font color='green'>(version " + gras_version+ ")</font></b> in combination with Geant4 version "
    f"<b><font color='orange'>10.07 (patch 2)</font></b> for L²SIM project "
    f"<b><font color='orange'>{order_number}</font></b>.", normal_style))
content.append(Spacer(1, 6))
content.append(Paragraph("The simulation was performed for the following analyzed volumes:", normal_style))

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
file_map_path = os.path.join(parent_dir, 'file_map.json')

with open(file_map_path, "r") as f:
    file_map = json.load(f)

def transform_filename(filename):
    parts = filename.split('_')
    if len(parts) > 2:
        transformed = '_'.join(parts[2:])
    else:
        transformed = filename
    if len(transformed) > 4:
        transformed = transformed[:-4]
    return transformed

analyzed_files = sorted(file_map.keys())

if analyzed_files:
    for file in analyzed_files:
        display_name = transform_filename(file)
        bullet = Paragraph(f"&nbsp;&nbsp;&nbsp;&bull;&nbsp;<font color='orange'>{display_name}</font>", normal_style)
        content.append(bullet)
else:
    content.append(Paragraph("<font color='red'>No analyzed volumes found in the input.</font>", highlight_style))

content.append(Spacer(1, 12))
content.append(Paragraph("Table <b><font color='red'>1.1</font></b> shows parts of the spectrum used in the simulation.", normal_style))
content.append(Paragraph("<i>Table 1.1: Parts of the spectrum used in the simulation</i>", normal_style))

spectrum_table_data = [
    ["PART OF THE SPECTRUM", "NUMBER OF EVENTS"],
    ["{Part of the spectrum – SP, TP, TE = podle názvu souboru}", "{NoE – GRAS mod. COMMON}"]
]
spectrum_table = Table(spectrum_table_data, colWidths=[80*mm, 80*mm])
spectrum_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.teal),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]))
content.append(spectrum_table)

content.append(Spacer(1, 12))
content.append(Paragraph("Performed analysis is summarized in table <b><font color='red'>1.2</font></b>.", normal_style))
content.append(Paragraph("<i>Table 1.2: Performed analysis parts of the spectrum used in the simulation</i>", normal_style))
analysis_table_data = [
    ["ANALYSIS MODULE", "UNIT"],
    ["{Analysis module – GRAS module type}", "{Unit – ? always same for all output of 1 analysis module?}"]
]
analysis_table = Table(analysis_table_data, colWidths=[80*mm, 80*mm])
analysis_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.teal),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]))
content.append(analysis_table)

content.append(Spacer(1, 12))
content.append(Paragraph("{Analysis module – GRAS_MODULE_TYPE}", normal_style))
content.append(Paragraph("DOSE … TID analysis<br/>NIEL … TNID analysis<br/>LET … LET analysis<br/>FLUENCE … Fluence analysis", normal_style))

doc.build(content)
print("PDF generated as report_header_stretched.pdf")
