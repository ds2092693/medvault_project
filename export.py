import os
import time
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER

EXPORT_DIR = os.path.join(os.path.dirname(__file__), 'exports')
os.makedirs(EXPORT_DIR, exist_ok=True)

# Brand colors
GREEN_DARK  = colors.HexColor('#1a2e22')
GREEN_MID   = colors.HexColor('#2d6a4f')
GREEN_LIGHT = colors.HexColor('#52b788')
GOLD        = colors.HexColor('#c9a84c')
CREAM       = colors.HexColor('#f7f4ef')
GRAY_TEXT   = colors.HexColor('#5a5a6e')
GRAY_LIGHT  = colors.HexColor('#ede9e1')


def _base_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='AppTitle',
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=GREEN_DARK,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name='SubTitle',
        fontName='Helvetica',
        fontSize=10,
        textColor=GRAY_TEXT,
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name='SectionHead',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=GREEN_MID,
        spaceBefore=14,
        spaceAfter=6,
        borderPad=4,
    ))
    styles.add(ParagraphStyle(
        name='BodyText2',
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#1a1a1e'),
        leading=16,
    ))
    styles.add(ParagraphStyle(
        name='SmallGray',
        fontName='Helvetica',
        fontSize=9,
        textColor=GRAY_TEXT,
    ))
    return styles


def _divider():
    return HRFlowable(width="100%", thickness=0.5, color=GRAY_LIGHT, spaceAfter=8, spaceBefore=4)


def export_record_pdf(record, patient):
    """Export a single record's metadata as PDF."""
    ts = int(time.time())
    filename = f"record_{record['id']}_{ts}.pdf"
    path = os.path.join(EXPORT_DIR, filename)

    doc = SimpleDocTemplate(path, pagesize=A4,
                            topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2.5*cm, rightMargin=2.5*cm)
    styles = _base_styles()
    story = []

    # Header
    story.append(Paragraph("MedVault", styles['AppTitle']))
    story.append(Paragraph("Health Record Management System", styles['SubTitle']))
    story.append(_divider())
    story.append(Spacer(1, 0.3*cm))

    # Patient info
    if patient:
        story.append(Paragraph("Patient Information", styles['SectionHead']))
        pdata = [
            ['Name', patient['name'] or '—'],
            ['Age', str(patient['age']) + ' years' if patient['age'] else '—'],
            ['Gender', patient['gender'] or '—'],
            ['Blood Group', patient['blood_group'] or '—'],
            ['Emergency Contact', patient['emergency_contact'] or '—'],
        ]
        pt = Table(pdata, colWidths=[5*cm, 10*cm])
        pt.setStyle(TableStyle([
            ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME',  (1,0), (1,-1), 'Helvetica'),
            ('FONTSIZE',  (0,0), (-1,-1), 10),
            ('TEXTCOLOR', (0,0), (0,-1), GRAY_TEXT),
            ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor('#1a1a1e')),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [CREAM, colors.white]),
            ('TOPPADDING',  (0,0), (-1,-1), 6),
            ('BOTTOMPADDING',(0,0),(-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(pt)
        story.append(Spacer(1, 0.5*cm))

    # Record details
    story.append(_divider())
    story.append(Paragraph("Record Details", styles['SectionHead']))

    rdata = [
        ['Record Name',  record['file_name'] or '—'],
        ['Category',     record['cat_name'] or '—'],
        ['File',         record['file_path'] or '—'],
        ['File Type',    record['file_type'] or '—'],
        ['Upload Date',  str(record['upload_date']) if record['upload_date'] else '—'],
    ]
    rt = Table(rdata, colWidths=[5*cm, 10*cm])
    rt.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), GRAY_TEXT),
        ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor('#1a1a1e')),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [CREAM, colors.white]),
        ('TOPPADDING',  (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(rt)

    # Footer
    story.append(Spacer(1, 1*cm))
    story.append(_divider())
    story.append(Paragraph(
        f"Exported from MedVault &nbsp;|&nbsp; {_today()}",
        styles['SmallGray']
    ))

    doc.build(story)
    return path


def export_summary_pdf(patient, medicines, diseases, allergies, recent_records):
    """Export full health summary as PDF."""
    ts = int(time.time())
    filename = f"health_summary_{ts}.pdf"
    path = os.path.join(EXPORT_DIR, filename)

    doc = SimpleDocTemplate(path, pagesize=A4,
                            topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2.5*cm, rightMargin=2.5*cm)
    styles = _base_styles()
    story = []

    # Header banner
    story.append(Paragraph("MedVault", styles['AppTitle']))
    story.append(Paragraph("Personal Health Summary Report", styles['SubTitle']))
    story.append(_divider())
    story.append(Spacer(1, 0.3*cm))

    # Patient card
    if patient:
        story.append(Paragraph("Patient Profile", styles['SectionHead']))
        pdata = [
            ['Name',             patient['name'] or '—'],
            ['Age',              (str(patient['age']) + ' years') if patient['age'] else '—'],
            ['Gender',           patient['gender'] or '—'],
            ['Blood Group',      patient['blood_group'] or '—'],
            ['Emergency Contact',patient['emergency_contact'] or '—'],
        ]
        pt = Table(pdata, colWidths=[5*cm, 10*cm])
        pt.setStyle(TableStyle([
            ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME',  (1,0), (1,-1), 'Helvetica'),
            ('FONTSIZE',  (0,0), (-1,-1), 10),
            ('TEXTCOLOR', (0,0), (0,-1), GRAY_TEXT),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [CREAM, colors.white]),
            ('TOPPADDING',  (0,0), (-1,-1), 6),
            ('BOTTOMPADDING',(0,0),(-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(pt)

    story.append(Spacer(1, 0.5*cm))
    story.append(_divider())

    # Medicines
    story.append(Paragraph("Current Medicines", styles['SectionHead']))
    if medicines:
        for m in medicines:
            story.append(Paragraph(f"• {m['medicine_text']}", styles['BodyText2']))
    else:
        story.append(Paragraph("No medicines recorded.", styles['SmallGray']))

    story.append(Spacer(1, 0.3*cm))
    story.append(_divider())

    # Past diseases
    story.append(Paragraph("Past Diseases", styles['SectionHead']))
    if diseases:
        for d in diseases:
            story.append(Paragraph(f"• {d['disease_name']}", styles['BodyText2']))
    else:
        story.append(Paragraph("No past diseases recorded.", styles['SmallGray']))

    story.append(Spacer(1, 0.3*cm))
    story.append(_divider())

    # Allergies
    story.append(Paragraph("Allergies", styles['SectionHead']))
    if allergies:
        for a in allergies:
            story.append(Paragraph(f"• {a['allergy_name']}", styles['BodyText2']))
    else:
        story.append(Paragraph("No allergies recorded.", styles['SmallGray']))

    story.append(Spacer(1, 0.3*cm))
    story.append(_divider())

    # Recent records table
    story.append(Paragraph("Recently Uploaded Records", styles['SectionHead']))
    if recent_records:
        header = [['Record Name', 'Category', 'Upload Date']]
        rows = [[r['file_name'], r['cat_name'], str(r['upload_date'])[:10]] for r in recent_records]
        tdata = header + rows
        t = Table(tdata, colWidths=[7*cm, 4*cm, 4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',   (0,0), (-1,0), GREEN_MID),
            ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
            ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTNAME',     (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE',     (0,0), (-1,-1), 9),
            ('ROWBACKGROUNDS',(0,1), (-1,-1), [CREAM, colors.white]),
            ('TOPPADDING',   (0,0), (-1,-1), 7),
            ('BOTTOMPADDING',(0,0), (-1,-1), 7),
            ('LEFTPADDING',  (0,0), (-1,-1), 8),
            ('GRID',         (0,0), (-1,-1), 0.3, GRAY_LIGHT),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No records uploaded yet.", styles['SmallGray']))

    # Footer
    story.append(Spacer(1, 1*cm))
    story.append(_divider())
    story.append(Paragraph(
        f"Confidential Health Record &nbsp;|&nbsp; MedVault &nbsp;|&nbsp; Generated: {_today()}",
        styles['SmallGray']
    ))

    doc.build(story)
    return path


def _today():
    from datetime import date
    return date.today().strftime("%d %B %Y")
