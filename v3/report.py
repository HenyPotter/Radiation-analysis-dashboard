from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import json
import os
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle, Image, Paragraph
from reportlab.lib.enums import TA_CENTER
import csv

order_number = "123456789"
gras_version = "5.0.1"
generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
title = "Simulace zařízení UIEHTGUWEIFGHS298"
logo_path = "report/logo.png"
trapped_proton_name = "Trapped Proton"
trapped_electron_name = "Trapped Electron"
solar_proton_name = "Solar Proton"

ttf_folder = os.path.join(os.path.dirname(__file__), 'report')
pdfmetrics.registerFont(TTFont('ArialNarrow', os.path.join(ttf_folder, 'arialnarrow.ttf')))
pdfmetrics.registerFont(TTFont('ArialNarrowBold', os.path.join(ttf_folder, 'arialnarrow_bold.ttf')))
pdfmetrics.registerFont(TTFont('ArialNarrowBoldItalic', os.path.join(ttf_folder, 'arialnarrow_bolditalic.ttf')))

font_basic = "ArialNarrow"
font_bold = "ArialNarrowBold"
font_bolditalic = "ArialNarrowBoldItalic"

bold_italic = ParagraphStyle(name="BoldItalic", fontName=font_bolditalic, fontSize=14, alignment=TA_CENTER, textColor=colors.teal, leading=20)
bold_title = ParagraphStyle(name="BoldTitle", fontName=font_bold, fontSize=18, alignment=TA_CENTER, textColor=colors.teal, leading=24)
cell_style = ParagraphStyle(name="Cell", fontName=font_basic, fontSize=10, alignment=TA_CENTER, textColor=colors.teal, leading=14)
header_style = ParagraphStyle(name="Heading1", fontName=font_bold, fontSize=14, textColor=colors.black, spaceAfter=8)
normal_style = ParagraphStyle(name="Normal", fontName=font_basic, fontSize=10, leading=14)
highlight_style = ParagraphStyle(name="Highlight", fontName=font_basic, fontSize=10, textColor=colors.red)

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

content = [table, Spacer(1, 12)]
content.append(Paragraph("1. SCOPE OF THE SIMULATION", header_style))
content.append(Paragraph(
    f"This document presents the results of computer simulations for radiation analysis performed using a local <br/>"
    f"copy of GRAS <b><font>(version {gras_version})</font></b> in combination with Geant4 version 10.07 (patch 2) for L²SIM project <b><font style='italic'>{order_number}</font></b>.",
    normal_style
))
content.append(Spacer(1, 6))
content.append(Paragraph("The simulation was performed for the following analyzed volumes:", normal_style))

file_map_path = os.path.join(os.path.dirname(__file__), 'file_map.json')
with open(file_map_path, "r") as f:
    file_map = json.load(f)

props_path = os.path.join(os.path.dirname(__file__), 'properties.json')
with open(props_path, 'r') as pf:
    props_list = json.load(pf)

pv_map = {}
for item in props_list:
    base = os.path.dirname(item['file_path'])
    pv_map[base] = item.get('physical_volume', '')

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

    if len(raw_pv) >= 9 and raw_pv[3] == '-':
        physical_vol = f"{raw_pv[:3]}-{raw_pv[4:9]}"
    elif len(raw_pv) >= 8:
        physical_vol = f"{raw_pv[:3]}-{raw_pv[3:8]}"
    else:
        physical_vol = raw_pv

    spectrum_table_data.append([spectrum_label, event_count, physical_vol])

sorted_rows = [spectrum_table_data[0]] + sorted(spectrum_table_data[1:], key=lambda row: row[2])

spectrum_table = Table(sorted_rows, colWidths=[60*mm, 60*mm, 60*mm])

spectrum_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.teal),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]))
content.append(spectrum_table)


def parse_analysis_modules_from_csv(csv_path):
    """Parse GRAS_MODULE_TYPE and unit from CSV file."""
    module_type = None
    unit = None

    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            if row[0].strip("'\"") == "GRAS_MODULE_TYPE":
                if len(row) > 2:
                    module_type = row[2].strip("'\"")
            elif row[0].startswith("'") and row[0].endswith("'") and not row[0].startswith("'GRAS_"):
                if len(row) > 1 and row[1].strip("'\""):
                    unit_candidate = row[1].strip("'\"")
                    if any(c.isalpha() for c in unit_candidate):
                        unit = unit_candidate
                        break
    return module_type, unit

all_analysis_modules = {}

for file_key, files in file_map.items():
    for file_path in files:
        basename = os.path.basename(file_path).lower()
        if basename.endswith('.csv') and not basename.startswith('info'):
            mod_type, unit = parse_analysis_modules_from_csv(file_path)
            if mod_type and unit:
                all_analysis_modules[mod_type] = unit

analysis_table_data = [["ANALYSIS MODULE", "UNIT"]]
for mod, unit in sorted(all_analysis_modules.items()):
    analysis_table_data.append([mod, unit])

analysis_table = Table(analysis_table_data, colWidths=[80*mm, 80*mm])
analysis_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.teal),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]))
content.append(Spacer(1, 12))
content.append(Paragraph("Performed analysis is summarized in table <b><font color='gray'>[1.2]</font></b>.", normal_style))
content.append(Paragraph("<i>Table 1.2: Performed analysis parts of the spectrum used in the simulation</i>", normal_style))
content.append(analysis_table)
content.append(PageBreak())


def get_tid_result(tid_csv_path):
    try:
        with open(tid_csv_path, newline='') as f:
            reader = csv.reader(f)
            rows = [row for row in reader if row and not row[0].startswith("#")]

            for row in reversed(rows):
                if len(row) >= 2:
                    try:
                        result = float(row[0])
                        error = float(row[1])
                        return result, error
                    except ValueError:
                        continue
    except Exception:
        pass
    return None, None


tid_table_data = [["ANALYZED VOLUME", "SOLAR PROTON", "TRAPPED ELECTRON", "TRAPPED PROTON", "TOTAL"]]

volume_group = {}

for file_key, paths in file_map.items():
    spectrum_type = '_'.join(file_key.split('_')[:2])
    folder = os.path.dirname(paths[0])
    physical_vol = pv_map.get(folder, '')

    if len(physical_vol) >= 9 and physical_vol[3] == '-':
        physical_vol = f"{physical_vol[:3]}-{physical_vol[4:9]}"
    elif len(physical_vol) >= 8:
        physical_vol = f"{physical_vol[:3]}-{physical_vol[3:8]}"

    if physical_vol not in volume_group:
        volume_group[physical_vol] = {}
    volume_group[physical_vol][spectrum_type] = folder

for physical_vol, spectrums in sorted(volume_group.items()):
    row = [physical_vol]
    total_dose = 0.0
    total_error2 = 0.0

    for spectrum_type in ["solar_proton", "trapped_electron", "trapped_proton"]:
        folder = spectrums.get(spectrum_type)
        result_str = "-"
        if folder:
            tid_csv = os.path.join(folder, "total_dose.csv")
            result, error = get_tid_result(tid_csv)
            if result is not None and error is not None:
                result_str = f"{result:.3e} ± {error:.1e}"
                total_dose += result
                total_error2 += error**2
        row.append(result_str)

    if total_dose > 0:
        total_error = total_error2 ** 0.5
        total_str = f"{total_dose:.3e} ± {total_error:.1e}"
    else:
        total_str = "-"
    row.append(total_str)

    tid_table_data.append(row)

tid_table = Table(tid_table_data, colWidths=[38*mm, 38*mm, 38*mm, 38*mm, 38*mm])
tid_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.teal),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]))

content.append(Spacer(1, 12))
content.append(Paragraph("Table <b><font color='gray'>[1.3]</font></b> summarizes calculated Total Ionizing Dose (TID) per analyzed volume and spectrum.", normal_style))
content.append(Paragraph("<i>Table 1.3: Calculated TID per analyzed volume</i>", normal_style))
content.append(tid_table)


doc.build(content)