import argparse
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def generate_invoice(invoice_number, date, hours, rate):
    # Load company and client details from config.json
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    company_name = config['company_name']
    company_address = config['company_address']
    bank_details = config['bank_details']
    client_name = config['client_name']
    client_address = config['client_address']
    
    currency = config.get('currency', 'USD')
    currency_symbol = '$' if currency == 'USD' else '£'
    
    unit_of_work = config.get('unit_of_work', 'HOURLY')
    if unit_of_work == 'DAILY':
        unit_header = "Number of Days"
        rate_header = "Daily Rate"
    elif unit_of_work == 'WEEKLY':
        unit_header = "Number of Weeks"
        rate_header = "Weekly Rate"
    else:
        unit_header = "Number of Hours"
        rate_header = "Hourly Rate"
    
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
    client_info = f"<b>Billed to:</b><br/>{client_name}<br/>{'<br/>'.join(client_address)}"
    elements.append(Paragraph(client_info, styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Add table with invoice details
    data = [
        ["Description", unit_header, rate_header, "Total Amount"],
        ["Consulting Services", hours, f"{currency_symbol}{rate:.2f}", f"{currency_symbol}{total_amount:.2f}"]
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

    parser.add_argument("invoice_number", help="Invoice number")
    parser.add_argument("date", help="Date of the invoice")
    parser.add_argument("hours", type=float, help="Number of hours worked")
    parser.add_argument("rate", type=float, help="Hourly rate")
    
    args = parser.parse_args()
    
    generate_invoice(

        args.invoice_number,
        args.date,
        args.hours,
        args.rate
    )

if __name__ == "__main__":
    main()

