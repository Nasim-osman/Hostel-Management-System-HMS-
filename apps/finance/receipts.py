import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_receipt_pdf(payment):
    """
    Generates a professional, branded PDF receipt for an official verified HMS payment.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0b63b6'),
        alignment=1 # Center
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        alignment=1
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e293b')
    )
    normal_style = ParagraphStyle(
        'ReceiptNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    bold_style = ParagraphStyle(
        'ReceiptBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1e293b')
    )

    elements = []

    # Header
    elements.append(Paragraph("HMS — HOSTEL MANAGEMENT SYSTEM", title_style))
    elements.append(Paragraph("Official Payment Receipt & Acknowledgment", subtitle_style))
    elements.append(Spacer(1, 15))

    # Meta Table: Receipt Info & Resident Info
    resident = payment.resident
    bed_info = str(resident.current_bed) if resident.current_bed else "Not Allocated"
    
    info_data = [
        [
            Paragraph("<b>Receipt No:</b> " + payment.receipt_number, normal_style),
            Paragraph("<b>Date:</b> " + payment.payment_date.strftime('%B %d, %Y'), normal_style),
        ],
        [
            Paragraph("<b>Resident Name:</b> " + (resident.user.get_full_name() or resident.user.username), normal_style),
            Paragraph("<b>Resident ID:</b> " + resident.student_id, normal_style),
        ],
        [
            Paragraph("<b>Room & Bed:</b> " + bed_info, normal_style),
            Paragraph("<b>Status:</b> <font color='#16a34a'><b>" + payment.get_status_display() + "</b></font>", normal_style),
        ]
    ]

    info_table = Table(info_data, colWidths=[270, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    # Payment Item Breakdown Table
    charge_desc = payment.charge.description if payment.charge else "Hostel Fee Payment"
    items_data = [
        [Paragraph("Description", bold_style), Paragraph("Payment Method", bold_style), Paragraph("Reference No", bold_style), Paragraph("Amount (₹)", bold_style)],
        [
            Paragraph(charge_desc, normal_style),
            Paragraph(payment.get_payment_method_display(), normal_style),
            Paragraph(payment.transaction_reference or "N/A", normal_style),
            Paragraph(f"₹ {payment.amount:,.2f}", bold_style)
        ],
        [
            "", "", Paragraph("<b>Total Paid:</b>", bold_style), Paragraph(f"<b>₹ {payment.amount:,.2f}</b>", bold_style)
        ]
    ]

    items_table = Table(items_data, colWidths=[200, 110, 110, 110])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0b63b6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 9),
        ('BACKGROUND', (0,1), (-1,1), colors.white),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 30))

    # Signature / Verification Box
    verifier_name = payment.verified_by.get_full_name() if payment.verified_by else "Authorized Accounts Officer"
    sig_data = [
        [
            Paragraph("<b>Resident Signature:</b><br/><br/>______________________", normal_style),
            Paragraph(f"<b>Verified by Accounts:</b><br/>{verifier_name}<br/><br/>______________________<br/><i>Authorized Stamp</i>", normal_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 260])
    sig_table.setStyle(TableStyle([
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(sig_table)
    elements.append(Spacer(1, 20))

    # Footer note
    elements.append(Paragraph("<i>This is a computer-generated receipt issued by HMS (Hostel Management System). Please retain this copy for institutional records.</i>", subtitle_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
