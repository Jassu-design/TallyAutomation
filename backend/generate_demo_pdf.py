import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

PDF_PATH = "C:/Users/hp/.gemini/antigravity/scratch/bank-tally-automation/data/sample_bank_statements/demo_bank_statement.pdf"
os.makedirs(os.path.dirname(PDF_PATH), exist_ok=True)

def generate_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'BankTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#002e6e'),
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'BankSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )
    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor('#334155')
    )
    meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#0f172a')
    )
    tbl_hdr = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=colors.white
    )
    tbl_cell = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#0f172a')
    )
    tbl_cell_amt = ParagraphStyle(
        'TblCellAmt',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        alignment=2 # Right aligned
    )

    # 1. Header
    story.append(Paragraph("HDFC BANK LIMITED", title_style))
    story.append(Paragraph("Detailed Account Statement (Sample Demo Document)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#002e6e'), spaceAfter=14))

    # 2. Account Details Metadata Table
    meta_data = [
        [
            Paragraph("Account Holder:", meta_label), Paragraph("ABC PVT LTD", meta_val),
            Paragraph("Statement Period:", meta_label), Paragraph("01 Oct 2026 to 10 Oct 2026", meta_val)
        ],
        [
            Paragraph("Account Number:", meta_label), Paragraph("50200012345678", meta_val),
            Paragraph("Account Type:", meta_label), Paragraph("Current Account (INR)", meta_val)
        ],
        [
            Paragraph("Branch / IFSC:", meta_label), Paragraph("Koramangala, Bengaluru / HDFC0001234", meta_val),
            Paragraph("Opening Balance:", meta_label), Paragraph("Rs. 1,56,550.50 Cr", meta_val)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[100, 160, 100, 160])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 16))

    # 3. Transactions Table
    headers = [
        Paragraph("Date", tbl_hdr),
        Paragraph("Narration / Description", tbl_hdr),
        Paragraph("Chq / Ref No", tbl_hdr),
        Paragraph("Withdrawal (Dr)", tbl_hdr),
        Paragraph("Deposit (Cr)", tbl_hdr),
        Paragraph("Balance (INR)", tbl_hdr)
    ]
    
    rows = [
        ["01/10/2026", "UPI/AMAZON SELLER SERVICES/428190", "UPI428190331", "2,350.00", "", "1,54,200.50"],
        ["01/10/2026", "NEFT/ABC INDUSTRIES PVT LTD/SETTLEMENT", "NEFT889102", "", "50,000.00", "2,04,200.50"],
        ["02/10/2026", "ACH/RELIANCE JIO INFOCOM BILL", "ACH009812", "1,499.00", "", "2,02,701.50"],
        ["02/10/2026", "HDFC BANK CHARGES Q3 FOLIO", "CHG771829", "450.00", "", "2,02,251.50"],
        ["03/10/2026", "UPI/RAJESH KIRANA STORE/987123", "UPI987123001", "1,850.00", "", "2,00,401.50"],
        ["03/10/2026", "IMPS/SALARY OCTOBER RAJESH/EMP01", "IMPS449102", "45,000.00", "", "1,55,401.50"],
        ["04/10/2026", "BESCOM ELECTRICITY BILL BANGALORE", "EB9928172", "6,200.00", "", "1,49,201.50"],
        ["04/10/2026", "INTEREST PAID FOR Q2 FY26", "INT202610", "", "3,420.00", "1,52,621.50"],
        ["05/10/2026", "ATM WDL KORAMANGALA MAIN BR", "ATM881729", "10,000.00", "", "1,42,621.50"],
        ["06/10/2026", "UPI/UNKNOWN VENDOR HARDWARE", "UPI9921021", "3,200.00", "", "1,39,421.50"],
    ]

    tbl_data = [headers]
    for r in rows:
        dr_color = colors.HexColor('#dc2626') if r[3] else colors.HexColor('#0f172a')
        cr_color = colors.HexColor('#059669') if r[4] else colors.HexColor('#0f172a')

        dr_p = Paragraph(f"<font color='{dr_color.hexval()}'>{r[3]}</font>", tbl_cell_amt) if r[3] else Paragraph("—", tbl_cell_amt)
        cr_p = Paragraph(f"<font color='{cr_color.hexval()}'>{r[4]}</font>", tbl_cell_amt) if r[4] else Paragraph("—", tbl_cell_amt)

        tbl_data.append([
            Paragraph(r[0], tbl_cell),
            Paragraph(r[1], tbl_cell),
            Paragraph(r[2], tbl_cell),
            dr_p,
            cr_p,
            Paragraph(r[5], tbl_cell_amt)
        ])

    table = Table(tbl_data, colWidths=[55, 175, 75, 70, 70, 75])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#002e6e')),
        ('ALIGN', (0,0), (-1,0), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # 4. Summary & Demo Explanation Note
    note_title = ParagraphStyle('NoteTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0f172a'))
    note_body = ParagraphStyle('NoteBody', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor('#475569'), spaceBefore=4)

    story.append(Paragraph("Bank-to-Tally Automation Demo Legend:", note_title))
    story.append(Paragraph("• <b>Rows 1-4, 6-9:</b> Automatically classified by rules (Amazon, ABC Industries, Jio, Charges, Salary, Electricity, Interest, Cash Contra).", note_body))
    story.append(Paragraph("• <b>Row 5 & 10:</b> Flagged for Review Queue (Unknown Vendor / Rajesh Kirana Store) ensuring complete human audit control before posting.", note_body))
    story.append(Paragraph("• <b>Duplicate Safety:</b> Uploading this file a second time triggers 100% SHA-256 duplicate blocking.", note_body))

    doc.build(story)
    print(f"PDF generated successfully at: {PDF_PATH}")

if __name__ == '__main__':
    generate_pdf()
