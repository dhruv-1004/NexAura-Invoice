import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from app.models.invoice import Invoice
from app.models.company import CompanySettings

BRAND_ORANGE = colors.HexColor("#FF5A00")
BRAND_BLACK = colors.HexColor("#0A0A0A")
BRAND_WHITE = colors.HexColor("#FFFFFF")
LIGHT_GRAY = colors.HexColor("#F5F5F5")
BORDER_GRAY = colors.HexColor("#E0E0E0")
LINK_BLUE = colors.HexColor("#0066CC")

def generate_invoice_pdf(invoice: Invoice, company: CompanySettings) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    # Custom Styles
    normal_style = styles['Normal']
    normal_style.fontSize = 9
    normal_style.textColor = BRAND_BLACK
    
    right_align_style = ParagraphStyle('RightAlign', parent=normal_style, alignment=TA_RIGHT)
    
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'], textColor=BRAND_ORANGE, fontSize=16, spaceAfter=20, alignment=TA_RIGHT
    )
    
    slogan_style = ParagraphStyle('Slogan', parent=normal_style, textColor=colors.gray, fontSize=10)
    heading_style = ParagraphStyle('Heading', parent=normal_style, fontName='Helvetica-Bold', fontSize=10)
    
    # 1. Top Header: Logo/Slogan (Left) and Company Info (Right)
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'LOGO.jpeg')
    logo_elements = []
    if os.path.exists(logo_path):
        logo_elements.append(Image(logo_path, width=70, height=70, kind='proportional'))
    else:
        logo_elements.append(Paragraph("<b>NexAura</b>", ParagraphStyle('BrandLogo', parent=styles['Heading1'], textColor=BRAND_BLACK, fontSize=24)))
        
    logo_elements.append(Spacer(1, 5))
    logo_elements.append(Paragraph("Simplify. Connect. Grow.", slogan_style))
    
    company_name = company.company_name if company and company.company_name else "NexAura Technologies"
    # Placeholder for company details as per user request to match the structure
    company_address = "SRTPL House, Behind Acrolawns Club, Kalawad Road,<br/>Rajkot, 360005 (GUJ), INDIA"
    company_contact = f"<font color='{LINK_BLUE}'>+91 XXXXX XXXXX | connect@nexaura.com | nexaura.com</font>"
    
    company_col = [
        Paragraph(f"<b>{company_name.upper()}</b>", ParagraphStyle('CompName', parent=right_align_style, fontName='Helvetica-Bold', fontSize=12, spaceAfter=5)),
        Paragraph(company_address, right_align_style),
        Spacer(1, 5),
        Paragraph(company_contact, right_align_style)
    ]
    
    header_table = Table([[logo_elements, company_col]], colWidths=[250, 265])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))
    
    # 2. INVOICE Title
    elements.append(Paragraph("<b>INVOICE</b>", title_style))
    
    # 3. Client & Invoice Info
    client_info = [
        Paragraph("<b>INVOICE TO:</b>", heading_style),
        Spacer(1, 8),
        Paragraph(f"<b><font color='{LINK_BLUE}'>{invoice.client_name}</font></b>", normal_style),
    ]
    if getattr(invoice, 'client_email', None):
        client_info.append(Paragraph(invoice.client_email, normal_style))
    if getattr(invoice, 'client_phone', None):
        client_info.append(Paragraph(invoice.client_phone, normal_style))
        
    client_info.append(Paragraph(invoice.billing_address.replace('\n', '<br/>'), normal_style))
    
    if getattr(invoice, 'client_tax_number', None):
        client_info.append(Spacer(1, 5))
        client_info.append(Paragraph(f"GST: {invoice.client_tax_number}", normal_style))

    invoice_info_data = [
        [Paragraph("<b>Invoice No:</b>", normal_style), Paragraph(invoice.invoice_number, right_align_style)],
        [Paragraph("<b>Invoice Date:</b>", normal_style), Paragraph(invoice.issue_date.strftime('%d %b %Y'), right_align_style)],
        [Paragraph("<b>Terms:</b>", normal_style), Paragraph("Due on receipt", right_align_style)],
        [Paragraph("<b>Due Date:</b>", normal_style), Paragraph(invoice.due_date.strftime('%d %b %Y'), right_align_style)],
    ]
    
    # Check if we have creator details
    if getattr(invoice, 'creator_name', None):
        invoice_info_data.append([Paragraph("<b>Created By:</b>", normal_style), Paragraph(invoice.creator_name, right_align_style)])
    if getattr(invoice, 'creator_phone', None):
        invoice_info_data.append([Paragraph("<b>Phone Number:</b>", normal_style), Paragraph(invoice.creator_phone, right_align_style)])
    if getattr(invoice, 'creator_email', None):
        invoice_info_data.append([Paragraph("<b>Company Email:</b>", normal_style), Paragraph(invoice.creator_email, right_align_style)])
        

    invoice_info_table = Table(invoice_info_data, colWidths=[100, 150])
    invoice_info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    info_table = Table([[client_info, invoice_info_table]], colWidths=[250, 265])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # 4. Items Table
    item_headers = [
        Paragraph("<b>#</b>", ParagraphStyle('TH', parent=normal_style, textColor=BRAND_ORANGE, alignment=TA_CENTER)),
        Paragraph("<b>Description</b>", ParagraphStyle('TH', parent=normal_style, textColor=BRAND_ORANGE)),
        Paragraph("<b>Amount</b>", ParagraphStyle('TH', parent=normal_style, textColor=BRAND_ORANGE, alignment=TA_RIGHT))
    ]
    
    item_data = [item_headers]
    
    for idx, item in enumerate(invoice.items, 1):
        desc_text = f"<b>{item.service_name.upper()}</b>"
        if item.description:
            desc_text += f"<br/><font color='gray'><i>{item.description}</i></font>"
            
        row = [
            Paragraph(str(idx), ParagraphStyle('TC', parent=normal_style, alignment=TA_CENTER)),
            Paragraph(desc_text, normal_style),
            Paragraph(f"₹{item.amount:,.2f}", right_align_style)
        ]
        item_data.append(row)
        
    t_items = Table(item_data, colWidths=[40, 355, 120])
    t_items.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1.5, BRAND_ORANGE),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, BRAND_ORANGE),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, BORDER_GRAY),
    ]))
    elements.append(t_items)
    elements.append(Spacer(1, 15))
    
    # 5. Totals & QR Section
    qr_placeholder = Table([
        [Paragraph("<b>[QR CODE WILL BE HERE]</b>", ParagraphStyle('QR', parent=normal_style, alignment=TA_CENTER))]
    ], colWidths=[120], rowHeights=[120])
    qr_placeholder.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 2, BRAND_BLACK),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
    ]))
    
    qr_box = [
        qr_placeholder,
        Table([[Paragraph("<b>SCAN TO PAY</b>", ParagraphStyle('Scan', parent=normal_style, alignment=TA_CENTER, textColor=BRAND_WHITE))]], colWidths=[120], rowHeights=[25], style=[('BACKGROUND', (0,0), (-1,-1), BRAND_BLACK), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 0)])
    ]
    
    totals_data = [
        [Paragraph("<b>Subtotal</b>", normal_style), Paragraph(f"₹{invoice.subtotal:,.2f}", right_align_style)],
    ]
    if invoice.discount > 0:
        totals_data.append([Paragraph("<b>Discount</b>", normal_style), Paragraph(f"- ₹{invoice.discount:,.2f}", right_align_style)])
        
    totals_data.append([Paragraph("<b>Total</b>", heading_style), Paragraph(f"<b>₹{invoice.grand_total:,.2f}</b>", right_align_style)])
    
    totals_table = Table(totals_data, colWidths=[120, 120])
    totals_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_GRAY),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, BRAND_BLACK),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, BRAND_BLACK),
    ]))
    
    bottom_section_table = Table([[qr_box, totals_table]], colWidths=[250, 265])
    bottom_section_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(bottom_section_table)
    elements.append(Spacer(1, 30))
    
    # 6. Amount in words & Bank Details
    amount_in_words = "[Amount in words pending implementation]"
    elements.append(Paragraph(f"<b>Amount in words:</b> {amount_in_words}", normal_style))
    elements.append(Spacer(1, 20))
    
    bank_details_data = [
        [Paragraph("<b>Bank Details</b>", ParagraphStyle('BankH', parent=normal_style, textColor=BRAND_ORANGE, fontName='Helvetica-Bold')), ''],
        [Paragraph("<b>Company Name:</b> [Your Company Name]", normal_style), Paragraph("<b>Account Number:</b> [Account Number]", normal_style)],
        [Paragraph("<b>Bank & Branch:</b> [Bank Name, Branch]", normal_style), Paragraph("<b>IFSC Code:</b> [IFSC Code]", normal_style)]
    ]
    bank_table = Table(bank_details_data, colWidths=[250, 265])
    bank_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('SPAN', (0, 0), (1, 0)),
    ]))
    elements.append(bank_table)
    elements.append(Spacer(1, 25))
    
    # 7. Terms & Conditions
    elements.append(Paragraph("<b>Terms & Conditions:</b>", normal_style))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("1. Subject to Jurisdiction.", ParagraphStyle('Term', parent=normal_style, textColor=colors.gray)))
    elements.append(Paragraph("2. All cheques payable to [Your Company Name].", ParagraphStyle('Term', parent=normal_style, textColor=colors.gray)))
    elements.append(Paragraph("3. Advance payment is non-refundable.", ParagraphStyle('Term', parent=normal_style, textColor=colors.gray)))
    elements.append(Paragraph("4. E&OE.", ParagraphStyle('Term', parent=normal_style, textColor=colors.gray)))
    
    elements.append(Spacer(1, 20))
    footer_style = ParagraphStyle('Footer', parent=normal_style, alignment=TA_CENTER, textColor=colors.gray, fontSize=8)
    elements.append(Paragraph("This is a computer generated invoice. No signature required.", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
