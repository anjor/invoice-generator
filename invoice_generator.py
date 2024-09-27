import argparse
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable


def get_currency_symbol(currency):
    currency_symbols = {
        'USD': '$',
        'GBP': '£',
        'EUR': '€'
    }
    return currency_symbols.get(currency, '$')  # Default to $ if currency not found

def generate_invoice(config_file, invoice_number, date, hours):
    # Load company and client details from the specified config file
    with open(config_file, "r") as f:
        config = json.load(f)

    company_name = config["company_name"]
    company_address = config["company_address"]
    bank_details = config["bank_details"]
    client_name = config["client_name"]
    client_address = config["client_address"]
    rate = float(config["rate"])

    currency = config.get("currency", "USD")
    currency_symbol = get_currency_symbol(currency)

    unit_of_work = config.get("unit_of_work", "HOURLY")
    if unit_of_work == "DAILY":
        unit_header = "Number of Days"
        rate_header = "Daily Rate"
    elif unit_of_work == "WEEKLY":
        unit_header = "Number of Weeks"
        rate_header = "Weekly Rate"
    else:
        unit_header = "Number of Hours"
        rate_header = "Hourly Rate"

    include_vat = config.get("include_vat", False)

    total_amount = hours * rate
    file_name = f"invoice_{invoice_number}.pdf"

    doc = SimpleDocTemplate(file_name, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Define color scheme
    blue_color = colors.Color(0, 0.3, 0.5)  # Dark blue for title and amount due

    # Add company name
    title_style = ParagraphStyle(
        "Title", parent=styles["Title"], textColor=blue_color, spaceAfter=6
    )
    elements.append(Paragraph(company_name, title_style))

    # Add horizontal line under the title
    elements.append(
        HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=6)
    )

    # Create a right-aligned style for invoice details
    right_style = ParagraphStyle(
        "RightAlign", parent=styles["Normal"], alignment=TA_RIGHT
    )

    # Create a table for company address and invoice details
    data = [
        [
            Paragraph(company_address[0], styles["Normal"]),
            Paragraph(f"Invoice Number: {invoice_number}", right_style),
        ],
        [
            Paragraph(company_address[1], styles["Normal"]),
            Paragraph(f"Date: {date}", right_style),
        ],
    ]

    # Add remaining address lines if any
    for line in company_address[2:]:
        data.append([Paragraph(line, styles["Normal"]), ""])

    address_table = Table(data, colWidths=[doc.width / 2] * 2)
    address_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    # Add the address table to the elements list
    elements.append(address_table)
    elements.append(Spacer(1, 12))

    # Add horizontal line after the company address
    elements.append(
        HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=6)
    )

    # Add client information
    client_info = (
        f"<b>Billed to:</b><br/>{client_name}<br/>{'<br/>'.join(client_address)}"
    )
    elements.append(Paragraph(client_info, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Add table with invoice details
    headers = ["Description", unit_header, rate_header]
    if include_vat:
        headers.append("VAT")
    headers.append("Total Amount")

    row = [
        "Consulting Services",
        hours,
        f"{currency_symbol}{rate:.2f}",
    ]
    if include_vat:
        row.append("20%")
        total_amount = total_amount * 1.2
        row.append(f"{currency_symbol}{total_amount:.2f}")
    else:
        row.append(f"{currency_symbol}{total_amount:.2f}")

    data = [headers, row]

    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 24))

    # Create styles for bank details and amount due
    left_style = ParagraphStyle("LeftAlign", parent=styles["Normal"], alignment=TA_LEFT)
    right_style_large = ParagraphStyle(
        "RightAlignLarge",
        parent=styles["Normal"],
        alignment=TA_RIGHT,
        fontSize=14,
        fontName="Helvetica-Bold",
        textColor=blue_color,
    )

    # Create a table for bank details and amount due
    bank_details_text = "<br/>".join(bank_details)
    amount_due_text = f"Amount Due: {currency_symbol}{total_amount:.2f}"

    bottom_table = Table(
        [
            [
                Paragraph(bank_details_text, left_style),
                Paragraph(amount_due_text, right_style_large),
            ]
        ],
        colWidths=[doc.width / 2] * 2,
    )
    bottom_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))

    elements.append(bottom_table)

    doc.build(elements)
    print(f"Invoice {file_name} generated successfully.")


def main():
    parser = argparse.ArgumentParser(description="Generate an invoice.")

    parser.add_argument(
        "-c", "--config", required=True, help="Path to the configuration file"
    )
    parser.add_argument("-n", "--number", required=True, help="Invoice number")
    parser.add_argument("-d", "--date", required=True, help="Date of the invoice")
    parser.add_argument(
        "-u",
        "--units",
        type=float,
        required=True,
        help="Number of units (hours/days/weeks) worked",
    )

    args = parser.parse_args()

    generate_invoice(args.config, args.number, args.date, args.units)


if __name__ == "__main__":
    main()
