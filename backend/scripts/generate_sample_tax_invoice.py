import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_shree_ram_papad_invoice(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        alignment=1,
        textColor=colors.HexColor('#1E293B')
    )
    sub_title_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        alignment=1,
        textColor=colors.HexColor('#475569')
    )
    cell_bold = ParagraphStyle('CellB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10)
    cell_norm = ParagraphStyle('CellN', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    cell_right = ParagraphStyle('CellR', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, alignment=2)
    cell_right_bold = ParagraphStyle('CellRB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=2)

    elements = []

    # Title
    elements.append(Paragraph("TAX INVOICE", title_style))
    elements.append(Paragraph("(Issued Under Section 31 of CGST Act, 2017)", sub_title_style))
    elements.append(Spacer(1, 10))

    # Header Box: Seller details & Invoice Details
    seller_html = """
    <b>SHREE RAM PAPAD'S PVT. LTD.</b><br/>
    F-124, Bichhwal Industrial Area, Bikaner, Rajasthan - 334006<br/>
    <b>GSTIN/UIN:</b> 08AAECS5023Q1Z7 | <b>State:</b> Rajasthan (08)<br/>
    <b>PAN:</b> AAECS5023Q | <b>FSSAI:</b> 12215017000123<br/>
    <b>Email:</b> sales@shreerampapad.com | <b>Phone:</b> +91 151 2250123
    """

    invoice_meta_html = """
    <b>Invoice No:</b> BKN/3118/26-27<br/>
    <b>Date:</b> 02-Aug-2026<br/>
    <b>e-Way Bill No:</b> 791657124983<br/>
    <b>Vehicle No:</b> RJ-07-GA-4521<br/>
    <b>Place of Supply:</b> Rajasthan (08)<br/>
    <b>Reverse Charge:</b> No
    """

    hdr_data = [
        [Paragraph(seller_html, cell_norm), Paragraph(invoice_meta_html, cell_norm)]
    ]
    hdr_table = Table(hdr_data, colWidths=[320, 215])
    hdr_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(hdr_table)
    elements.append(Spacer(1, 6))

    # Buyer & Consignee Box
    buyer_html = """
    <b>Details of Receiver / Billed to:</b><br/>
    <b>Name:</b> B R DUGGAR AND COMPANY<br/>
    <b>Address:</b> KEM Road, Bikaner, Rajasthan - 334001<br/>
    <b>GSTIN/UIN:</b> 08AABCB1234F1Z5<br/>
    <b>State:</b> Rajasthan, Code: 08
    """

    consignee_html = """
    <b>Details of Consignee / Shipped to:</b><br/>
    <b>Name:</b> B R DUGGAR AND COMPANY<br/>
    <b>Address:</b> Godown No. 4, Transport Nagar, Bikaner - 334001<br/>
    <b>GSTIN/UIN:</b> 08AABCB1234F1Z5<br/>
    <b>State:</b> Rajasthan, Code: 08
    """

    party_data = [
        [Paragraph(buyer_html, cell_norm), Paragraph(consignee_html, cell_norm)]
    ]
    party_table = Table(party_data, colWidths=[267, 268])
    party_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(party_table)
    elements.append(Spacer(1, 6))

    # Items Table
    item_header = [
        Paragraph("<b>S.No</b>", cell_bold),
        Paragraph("<b>Description of Goods</b>", cell_bold),
        Paragraph("<b>HSN/SAC</b>", cell_bold),
        Paragraph("<b>Quantity</b>", cell_right_bold),
        Paragraph("<b>Rate (₹)</b>", cell_right_bold),
        Paragraph("<b>Disc %</b>", cell_right_bold),
        Paragraph("<b>Taxable Value (₹)</b>", cell_right_bold)
    ]

    item_row_1 = [
        Paragraph("1", cell_norm),
        Paragraph("<b>Shree Ram Special Moong Papad (400g Pouch)</b><br/>Batch: SRP-2608 | Pkd: 01/08/2026", cell_norm),
        Paragraph("1905", cell_norm),
        Paragraph("120.00 Kgs", cell_right),
        Paragraph("220.00", cell_right),
        Paragraph("3.125 %", cell_right),
        Paragraph("25,574.40", cell_right)
    ]

    item_table_data = [item_header, item_row_1]

    # Summary rows
    item_table_data.append([
        "", Paragraph("<b>Total Taxable Amount</b>", cell_bold), "", "", "", "", Paragraph("<b>25,574.40</b>", cell_right_bold)
    ])
    item_table_data.append([
        "", Paragraph("Output CGST @ 2.50%", cell_norm), "", "", "", "2.50 %", Paragraph("639.36", cell_right)
    ])
    item_table_data.append([
        "", Paragraph("Output SGST @ 2.50%", cell_norm), "", "", "", "2.50 %", Paragraph("639.36", cell_right)
    ])
    item_table_data.append([
        "", Paragraph("Round Off (+/-)", cell_norm), "", "", "", "", Paragraph("(-) 0.12", cell_right)
    ])
    item_table_data.append([
        "", Paragraph("<b>Total Invoice Value (in Figures)</b>", cell_bold), "", "", "", "", Paragraph("<b>₹ 26,853.00</b>", cell_right_bold)
    ])

    items_table = Table(item_table_data, colWidths=[30, 205, 60, 65, 55, 45, 75])
    items_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94A3B8')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#94A3B8')),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.HexColor('#94A3B8')),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor('#0F172A')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 8))

    # Total in Words & Bank Details
    footer_text = """
    <b>Amount Chargeable (in words):</b> INR Twenty-Six Thousand Eight Hundred Fifty-Three Only.<br/>
    <b>IRN:</b> a29df9c536480b182cb62174c1ee6618588040a4ab8ef4cb97e1f422ebc96f20<br/>
    <b>Bank Details:</b> HDFC Bank | <b>A/c No:</b> 50200012345678 | <b>IFSC:</b> HDFC0000123 | <b>Branch:</b> KEM Road, Bikaner<br/>
    <i>Declaration: We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.</i>
    """
    elements.append(Paragraph(footer_text, cell_norm))

    doc.build(elements)
    print(f"Generated sample tax invoice PDF at {output_path}")

if __name__ == "__main__":
    generate_shree_ram_papad_invoice("data/sample_bank_statements/shree_ram_papad_invoice.pdf")
