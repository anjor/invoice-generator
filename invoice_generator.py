import argparse
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def generate_invoice(client_name, client_address, invoice_number, date, hours, rate):
    # Load company details from config.json
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    company_name = config['company_name']
    company_address = config['company_address']
    bank_details = config['bank_details']
    
    total_amount = hours * rate
    file_name = f"invoice_{invoice_number}.pdf"
    
    doc = SimpleDocTemplate(file_name, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add company name
    elements.append(Paragraph(company_name, styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Add company address and invoice details
    company_info = f"{'<br/>'.join(company_address)}<br/><br/>Invoice Number: {invoice_number}<br/>Date: {date}"
    elements.append(Paragraph(company_info, styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Add client information
    client_info = f"<b>Billed to:</b><br/>{client_name}<br/>{client_address}"
    elements.append(Paragraph(client_info, styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Add table with invoice details
    data = [
        ["Description", "Number of Hours", "Hourly Rate", "Total Amount"],
        ["Consulting Services", hours, f"${rate:.2f}", f"${total_amount:.2f}"]
    ]
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    
    # Add bank details
    elements.append(Paragraph('<br/>'.join(bank_details), styles['Normal']))
    
    doc.build(elements)
    print(f"Invoice {file_name} generated successfully.")

def main():
    parser = argparse.ArgumentParser(description="Generate an invoice.")
    parser.add_argument("client_name", help="Client's name")
    parser.add_argument("client_address", help="Client's address")
    parser.add_argument("invoice_number", help="Invoice number")
    parser.add_argument("date", help="Date of the invoice")
    parser.add_argument("hours", type=float, help="Number of hours worked")
    parser.add_argument("rate", type=float, help="Hourly rate")
    
    args = parser.parse_args()
    
    generate_invoice(
        args.client_name,
        args.client_address,
        args.invoice_number,
        args.date,
        args.hours,
        args.rate
    )

if __name__ == "__main__":
    main()

