"""
Script to generate sample PDF banking documents for testing.
Run this script after installing reportlab: pip install reportlab
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import os

def create_loan_application_pdf():
    """Create John Doe's home loan application PDF"""
    pdf_path = "data/sample_pdfs/loan_application_john_doe.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1)
    story.append(Paragraph("HOME LOAN APPLICATION", title_style))
    story.append(Spacer(1, 0.3*inch))

    # Applicant Information
    story.append(Paragraph("<b>Applicant Information</b>", styles['Heading2']))
    applicant_data = [
        ['Name:', 'John Doe'],
        ['Account Number:', 'ACC-2024-1001'],
        ['Email:', 'john.doe@email.com'],
        ['Phone:', '(555) 111-2222'],
        ['Employer:', 'TechCorp'],
        ['Position:', 'Senior Software Engineer'],
        ['Annual Salary:', '$120,000'],
    ]
    table = Table(applicant_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))

    # Loan Details
    story.append(Paragraph("<b>Loan Request Details</b>", styles['Heading2']))
    loan_data = [
        ['Loan Amount:', '$350,000'],
        ['Property Value:', '$400,000'],
        ['Property Address:', '123 Oak Street'],
        ['Loan Purpose:', 'Home Purchase'],
        ['Down Payment:', '$50,000 (14.3%)'],
    ]
    table2 = Table(loan_data, colWidths=[2*inch, 4*inch])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table2)
    story.append(Spacer(1, 0.2*inch))

    # Financial Summary
    story.append(Paragraph("<b>Financial Summary</b>", styles['Heading2']))
    story.append(Paragraph("Years with Bank: 8 years", styles['Normal']))
    story.append(Paragraph("Credit History: Excellent", styles['Normal']))
    story.append(Paragraph("Existing Debts: $15,000 (Car Loan)", styles['Normal']))

    doc.build(story)
    print(f"Created: {pdf_path}")

def create_kyc_update_pdf():
    """Create Sarah Williams' KYC update PDF"""
    pdf_path = "data/sample_pdfs/kyc_update_sarah_williams.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1)
    story.append(Paragraph("KYC UPDATE DOCUMENTATION", title_style))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("<b>Customer Information</b>", styles['Heading2']))
    customer_data = [
        ['Name:', 'Sarah Williams'],
        ['Account Number:', 'ACC-2019-5432'],
        ['Date of Birth:', 'March 15, 1988'],
        ['Email:', 'sarah.williams@email.com'],
    ]
    table = Table(customer_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("<b>Address Update</b>", styles['Heading2']))
    address_data = [
        ['Previous Address:', '789 Old Street, Springfield, CA 90200'],
        ['New Address:', '456 Maple Avenue, Apt 5B, Springfield, CA 90210'],
        ['Effective Date:', 'January 10, 2024'],
    ]
    table2 = Table(address_data, colWidths=[2*inch, 4*inch])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table2)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("<b>Supporting Documents Attached:</b>", styles['Heading2']))
    story.append(Paragraph("1. Utility Bill (Electric) - January 2024", styles['Normal']))
    story.append(Paragraph("2. California Driver's License - Updated Address", styles['Normal']))

    doc.build(story)
    print(f"Created: {pdf_path}")

def create_fraud_transactions_pdf():
    """Create Michael Chen's fraud transaction screenshots PDF"""
    pdf_path = "data/sample_pdfs/fraud_transactions_screenshots.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1)
    story.append(Paragraph("FRAUD REPORT - UNAUTHORIZED TRANSACTIONS", title_style))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("<b>Account Holder:</b> Michael Chen", styles['Heading2']))
    story.append(Paragraph("<b>Account Number:</b> ACC-2021-7788", styles['Normal']))
    story.append(Paragraph("<b>Report Date:</b> January 17, 2024", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("<b>Unauthorized Transactions:</b>", styles['Heading2']))
    transactions_data = [
        ['Date', 'Description', 'Location', 'Amount'],
        ['01/16/2024', 'ATM Withdrawal', 'New York, NY', '$500.00'],
        ['01/16/2024', 'Online Purchase', 'Unknown Merchant', '$1,200.00'],
        ['01/16/2024', 'Transfer', 'Unknown Account', '$350.00'],
        ['', '', '<b>Total:</b>', '<b>$2,050.00</b>'],
    ]
    table = Table(transactions_data, colWidths=[1.2*inch, 2*inch, 1.8*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("<b>Cardholder Statement:</b>", styles['Heading2']))
    story.append(Paragraph("I, Michael Chen, certify that:", styles['Normal']))
    story.append(Paragraph("1. I did not authorize these transactions", styles['Normal']))
    story.append(Paragraph("2. My card is still in my physical possession", styles['Normal']))
    story.append(Paragraph("3. I was in California at the time of the New York ATM withdrawal", styles['Normal']))
    story.append(Paragraph("4. I request immediate card cancellation and fraud investigation", styles['Normal']))

    doc.build(story)
    print(f"Created: {pdf_path}")

def create_business_loan_pdf():
    """Create Robert Martinez's business loan application PDF"""
    pdf_path = "data/sample_pdfs/business_loan_application.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1)
    story.append(Paragraph("BUSINESS LOAN APPLICATION", title_style))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("<b>Business Information</b>", styles['Heading2']))
    business_data = [
        ['Business Name:', 'Martinez Auto Repair LLC'],
        ['Owner:', 'Robert Martinez'],
        ['Business Account:', 'BUS-ACC-2012-3344'],
        ['Years in Operation:', '12 years'],
        ['Business Type:', 'Auto Repair Services'],
        ['Annual Revenue:', '$450,000'],
    ]
    table = Table(business_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("<b>Loan Request</b>", styles['Heading2']))
    loan_data = [
        ['Loan Amount:', '$200,000'],
        ['Purpose:', 'Business Expansion'],
        ['Intended Use:', 'Equipment purchase and second location'],
        ['Preferred Term:', '7 years'],
    ]
    table2 = Table(loan_data, colWidths=[2*inch, 4*inch])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table2)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("<b>Financial Summary (Last 3 Years)</b>", styles['Heading2']))
    financial_data = [
        ['Year', 'Revenue', 'Net Profit', 'Growth'],
        ['2021', '$380,000', '$75,000', '-'],
        ['2022', '$415,000', '$85,000', '9.2%'],
        ['2023', '$450,000', '$95,000', '8.4%'],
    ]
    table3 = Table(financial_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1*inch])
    table3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    story.append(table3)

    doc.build(story)
    print(f"Created: {pdf_path}")

def create_remaining_pdfs():
    """Create remaining simple PDF documents"""

    # Employment update PDF
    pdf_path = "data/sample_pdfs/employment_update_david_brown.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1)
    story.append(Paragraph("EMPLOYMENT UPDATE - KYC", title_style))
    story.append(Spacer(1, 0.3*inch))

    data = [
        ['Account Holder:', 'David Brown'],
        ['Account Number:', 'ACC-2018-4455'],
        ['Previous Employer:', 'ABC Corporation'],
        ['New Employer:', 'Global Tech Solutions'],
        ['New Position:', 'Director of Operations'],
        ['New Annual Income:', '$180,000'],
        ['Start Date:', 'January 1, 2024'],
    ]
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    doc.build(story)
    print(f"Created: {pdf_path}")

    # Chargeback dispute PDF
    pdf_path = "data/sample_pdfs/chargeback_dispute_amanda.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    story.append(Paragraph("CREDIT CARD CHARGEBACK DISPUTE", title_style))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("<b>Cardholder:</b> Amanda Garcia", styles['Heading2']))
    story.append(Paragraph("<b>Card:</b> **** **** **** 7890", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    dispute_data = [
        ['Transaction Date:', 'January 18, 2024'],
        ['Merchant:', 'Online Electronics Store'],
        ['Amount:', '$899.99'],
        ['Item:', 'Laptop Computer'],
        ['Return Date:', 'January 20, 2024'],
        ['Reason:', 'Refund not processed by merchant'],
    ]
    table = Table(dispute_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Evidence:</b> Return tracking number: TRK-998877", styles['Normal']))
    doc.build(story)
    print(f"Created: {pdf_path}")

    # Auto loan documents PDF
    pdf_path = "data/sample_pdfs/auto_loan_documents.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    story.append(Paragraph("AUTO LOAN PRE-APPROVAL APPLICATION", title_style))
    story.append(Spacer(1, 0.3*inch))

    applicant_data = [
        ['Name:', 'Patricia Lee'],
        ['Account:', 'ACC-2019-8877'],
        ['Annual Income:', '$75,000'],
        ['Employment:', '6 years at current employer'],
        ['Credit Score:', '720 (Estimated)'],
    ]
    table = Table(applicant_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))

    vehicle_data = [
        ['Vehicle:', '2024 Honda Accord'],
        ['Loan Amount:', '$35,000'],
        ['Term Requested:', '60 months'],
    ]
    table2 = Table(vehicle_data, colWidths=[2*inch, 4*inch])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table2)
    doc.build(story)
    print(f"Created: {pdf_path}")

    # Phishing email forward PDF
    pdf_path = "data/sample_pdfs/phishing_email_forward.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    story.append(Paragraph("PHISHING EMAIL REPORT", title_style))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("<b>Reported by:</b> Thomas Anderson (ACC-2020-5566)", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Suspicious Email Details:</b>", styles['Heading2']))
    story.append(Paragraph("From: support@bank-security-verify.com (SUSPICIOUS)", styles['Normal']))
    story.append(Paragraph("Subject: URGENT: Verify Your Account Now", styles['Normal']))
    story.append(Paragraph("Content: Requested immediate account verification with threat of closure", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Red Flags Identified:</b>", styles['Heading2']))
    story.append(Paragraph("1. Non-official sender domain", styles['Normal']))
    story.append(Paragraph("2. Generic greeting", styles['Normal']))
    story.append(Paragraph("3. Urgent/threatening tone", styles['Normal']))
    story.append(Paragraph("4. Suspicious link to non-bank website", styles['Normal']))
    doc.build(story)
    print(f"Created: {pdf_path}")

    # Joint account documents PDF
    pdf_path = "data/sample_pdfs/joint_account_documents.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    story.append(Paragraph("JOINT ACCOUNT OPENING REQUEST", title_style))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("<b>Primary Account Holder</b>", styles['Heading2']))
    data1 = [
        ['Name:', 'Maria Rodriguez'],
        ['Existing Account:', 'ACC-2021-4433'],
        ['Date of Birth:', 'June 10, 1985'],
    ]
    table = Table(data1, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("<b>Secondary Account Holder</b>", styles['Heading2']))
    data2 = [
        ['Name:', 'Carlos Rodriguez'],
        ['Existing Account:', 'ACC-2021-4434'],
        ['Date of Birth:', 'August 22, 1983'],
        ['Relationship:', 'Spouse'],
    ]
    table2 = Table(data2, colWidths=[2*inch, 4*inch])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table2)
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Supporting Documents:</b> Marriage Certificate, Joint Utility Bill", styles['Normal']))
    doc.build(story)
    print(f"Created: {pdf_path}")

if __name__ == "__main__":
    print("Generating sample PDF banking documents...")
    print("Note: Install reportlab first: pip install reportlab")
    print()

    try:
        create_loan_application_pdf()
        create_kyc_update_pdf()
        create_fraud_transactions_pdf()
        create_business_loan_pdf()
        create_remaining_pdfs()
        print("\n✓ All PDF documents created successfully!")
    except Exception as e:
        print(f"\n✗ Error creating PDFs: {e}")
        print("Make sure you have installed reportlab: pip install reportlab")
