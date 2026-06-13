import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.models.invoice import Invoice
from app.models.company import CompanySettings

BRAND_ORANGE = colors.HexColor("#FF5A00")
BRAND_BLACK = colors.HexColor("#0A0A0A")
BRAND_WHITE = colors.HexColor("#FFFFFF")

def generate_invoice_pdf(invoice: Invoice, company: CompanySettings) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    # Custom Styles
    header_style = ParagraphStyle(
        'Header', parent=styles['Heading1'], textColor=BRAND_ORANGE, fontSize=24, spaceAfter=10
    )
    normal_style = styles['Normal']
    bold_style = ParagraphStyle('Bold', parent=normal_style, fontName='Helvetica-Bold')

    # Header section
    company_name = company.company_name if company else "NexAura AI Automation"
    elements.append(Paragraph(company_name, header_style))
    elements.append(Spacer(1, 10))

    # Invoice Info & Client Info
    data = [
        [
            Paragraph(f"<b>INVOICE TO:</b><br/>{invoice.client_name}<br/>{invoice.billing_address}", normal_style),
            Paragraph(f"<b>INVOICE NO:</b> {invoice.invoice_number}<br/><b>DATE:</b> {invoice.issue_date.strftime('%Y-%m-%d')}<br/><b>DUE DATE:</b> {invoice.due_date.strftime('%Y-%m-%d')}", normal_style)
        ]
    ]
    t = Table(data, colWidths=[270, 270])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # Items Table
    item_data = [["Service", "Description", "Amount"]]
    for item in invoice.items:
        item_data.append([item.service_name, item.description or "", f"${item.amount:.2f}"])
        
    item_data.append(["", "Subtotal", f"${invoice.subtotal:.2f}"])
    item_data.append(["", "Discount", f"${invoice.discount:.2f}"])
    item_data.append(["", "Grand Total", f"${invoice.grand_total:.2f}"])

    t_items = Table(item_data, colWidths=[150, 270, 120])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_ORANGE),
        ('TEXTCOLOR', (0, 0), (-1, 0), BRAND_WHITE),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -4), colors.HexColor("#F5F5F5")),
        ('GRID', (0, 0), (-1, -4), 1, BRAND_BLACK),
        ('LINEABOVE', (1, -3), (-1, -1), 1, BRAND_BLACK),
        ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(t_items)
    elements.append(Spacer(1, 30))

    # Payment Details & Footer
    if company:
        payment_info = f"<b>Bank Name:</b> {company.bank_name}<br/><b>Account Name:</b> {company.account_holder}<br/><b>Account No:</b> {company.account_number}<br/><b>IFSC:</b> {company.ifsc}<br/><b>UPI ID:</b> {company.upi_id}"
        elements.append(Paragraph("<b>Payment Details:</b>", bold_style))
        elements.append(Paragraph(payment_info, normal_style))
        elements.append(Spacer(1, 20))
        
        if company.footer_note:
            footer_style = ParagraphStyle('Footer', parent=normal_style, alignment=1, textColor=colors.gray)
            elements.append(Paragraph(company.footer_note, footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
