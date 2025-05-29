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
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle, Image, Paragraph
from reportlab.lib.enums import TA_CENTER
import csv

# Configuration
order_number = "123456789"
gras_version = "5.0.1"
generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
title = "Simulace zařízení UIEHTGUWEIFGHS298"
logo_path = "logo.png"
trapped_proton_name = "Trapped Proton"
trapped_electron_name = "Trapped Electron"
solar_proton_name = "Solar Proton"

# Register fonts
ttf_folder = os.path.join(os.path.dirname(__file__), 'fonts')
pdfmetrics.registerFont(TTFont('ArialNarrow', os.path.join(ttf_folder, 'arialnarrow.ttf')))
pdfmetrics.registerFont(TTFont('ArialNarrowBold', os.path.join(ttf_folder, 'arialnarrow_bold.ttf')))
pdfmetrics.registerFont(TTFont('ArialNarrowBoldItalic', os.path.join(ttf_folder, 'arialnarrow_bolditalic.ttf')))

# Styles
font_basic = "ArialNarrow"
font_bold = "ArialNarrowBold"
font_bolditalic = "ArialNarrowBoldItalic"

bold_italic = ParagraphStyle(name="BoldItalic", fontName=font_bolditalic, fontSize=14, alignment=TA_CENTER, textColor=colors.teal, leading=20)
bold_title = ParagraphStyle(name="BoldTitle", fontName=font_bold, fontSize=18, alignment=TA_CENTER, textColor=colors.teal, leading=24)
cell_style = ParagraphStyle(name="Cell", fontName=font_basic, fontSize=10, alignment=TA_CENTER, textColor=colors.teal, leading=14)
header_style = ParagraphStyle(name="Heading1", fontName=font_bold, fontSize=14, textColor=colors.black, spaceAfter=8)
normal_style = ParagraphStyle(name="Normal", fontName=font_basic, fontSize=10, leading=14)
highlight_style = ParagraphStyle(name="Highlight", fontName=font_basic, fontSize=10, textColor=colors.red)

# Create document
doc = SimpleDocTemplate(
    "report_header_stretched.pdf",
    pagesize=A4,
    leftMargin=20*mm, rightMargin=20*mm,
    topMargin=20*mm, bottomMargin=20*mm
)

# Logo resizing
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

# Header table data
data = [
    [logo, Paragraph("GRAS SIMULATION SUMMARY", bold_italic), Paragraph(f"Order number:<br/>{order_number}", cell_style)],
    ["", Paragraph(title, bold_title), Paragraph(f"Generated on:<br/>{generated_date}", cell_style)],
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

# Build content
content = [table, Spacer(1, 12)]
content.append(Paragraph("1. SCOPE OF THE SIMULATION", header_style))
content.append(Paragraph(
    f"This document presents the results of computer simulations for radiation analysis performed using a local <br/>"
    f"copy of GRAS <b><font>(version {gras_version})</font></b> in combination with Geant4 version 10.07 (patch 2) for L²SIM project <b><font style='italic'>{order_number}</font></b>.",
    normal_style
))
content.append(Spacer(1, 6))
content.append(Paragraph("The simulation was performed for the following analyzed volumes:", normal_style))

# Load file map
file_map_path = os.path.join(os.path.dirname(__file__), 'file_map.json')
with open(file_map_path, "r") as f:
    file_map = json.load(f)

# Load properties for physical volumes
props_path = os.path.join(os.path.dirname(__file__), 'properties.json')
with open(props_path, 'r') as pf:
    props_list = json.load(pf)

# Build a map from info.csv path to physical volume
pv_map = {}
for item in props_list:
    base = os.path.dirname(item['file_path'])
    pv_map[base] = item.get('physical_volume', '')

# List analyzed volumes
analyzed_files = sorted(file_map.keys())
if analyzed_files:
    for file_key in analyzed_files:
        display_name = file_key.split('_', 2)[-1].rsplit('_', 1)[0]
        bullet = Paragraph(f"&nbsp;&nbsp;&nbsp;&bull;&nbsp;<font color='orange'>{display_name}</font>", normal_style)
        content.append(bullet)
else:
    content.append(Paragraph("<font color='red'>No analyzed volumes found in the input.</font>", highlight_style))

content.append(Spacer(1, 12))
content.append(Paragraph("Table <b><font color='gray'>[1.1]</font></b> shows parts of the spectrum used in the simulation.", normal_style))
content.append(Paragraph("<i>Table 1.1: Parts of the spectrum used in the simulation</i>", normal_style))

# Build spectrum table with physical volume
spectrum_table_data = [["PART OF THE SPECTRUM", "NUMBER OF EVENTS", "PHYSICAL VOLUME"]]
label_map = {"solar_proton": solar_proton_name, "trapped_proton": trapped_proton_name, "trapped_electron": trapped_electron_name}
for file_key in analyzed_files:
    spectrum_type = '_'.join(file_key.split('_')[:2])
    paths = file_map[file_key]
    folder = os.path.dirname(paths[0]) if paths else ""
    info_path = next((p for p in paths if p.endswith('info.csv')), None)
    event_count = 'N/A'
    if info_path and os.path.exists(info_path):
        with open(info_path, 'r', newline='') as f_csv:
            reader = csv.reader(f_csv)
            rows = [row for row in reader if row]
            last_row = rows[-1]
            event_count = last_row[0].strip().strip("'\"")
    spectrum_label = label_map.get(spectrum_type, spectrum_type)
    raw_pv = pv_map.get(folder, '')

    # Format PV as XXX-YYYYY
    if len(raw_pv) >= 9 and raw_pv[3] == '-':
        physical_vol = f"{raw_pv[:3]}-{raw_pv[4:9]}"
    elif len(raw_pv) >= 8:
        physical_vol = f"{raw_pv[:3]}-{raw_pv[3:8]}"
    else:
        physical_vol = raw_pv

    spectrum_table_data.append([spectrum_label, event_count, physical_vol])

spectrum_table = Table(spectrum_table_data, colWidths=[60*mm, 60*mm, 60*mm])
spectrum_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.teal),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]))
content.append(spectrum_table)

# Analysis table
content.append(Spacer(1, 12))
content.append(Paragraph("Performed analysis is summarized in table <b><font color='gray'>[1.2]</font></b>.", normal_style))
content.append(Paragraph("<i>Table 1.2: Performed analysis parts of the spectrum used in the simulation</i>", normal_style))
analysis_table_data = [
    ["ANALYSIS MODULE", "UNIT"],
    ["{Analysis module – GRAS module type}", "{Unit – same for all outputs?}"]
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
content.append(Paragraph(
    "DOSE … TID analysis<br/>NIEL … TNID analysis<br/>LET … LET analysis<br/>FLUENCE … Fluence analysis",
    normal_style
))

# Build PDF
doc.build(content)
print("PDF generated as report_header_stretched.pdf")
