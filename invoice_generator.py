import argparse
import json
import logging
import os
import sys
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable


def get_currency_symbol(currency: str) -> str:
    currency_symbols = {
        'USD': '$',
        'GBP': '£',
        'EUR': '€'
    }
    return currency_symbols.get(currency, '$')  # Default to $ if currency not found

def load_config(config_file: str) -> Dict[str, Any]:
    """Load and validate configuration from JSON file."""
    try:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file '{config_file}' not found")
        
        with open(config_file, "r") as f:
            config = json.load(f)
        
        validate_config(config)
        return config
    
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        logging.error(str(e))
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        sys.exit(1)


def validate_config(config: Dict[str, Any]) -> None:
    """Validate required configuration fields."""
    required_fields = [
        "company_name", "company_address", "bank_details",
        "client_name", "client_address", "rate"
    ]
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required configuration field: '{field}'")
    
    if not isinstance(config["rate"], (int, float)) or config["rate"] <= 0:
        raise ValueError("Rate must be a positive number")
    
    if not isinstance(config["company_address"], list) or len(config["company_address"]) < 2:
        raise ValueError("Company address must be a list with at least 2 lines")
    
    if not isinstance(config["client_address"], list) or len(config["client_address"]) < 1:
        raise ValueError("Client address must be a list with at least 1 line")
    
    if not isinstance(config["bank_details"], list) or len(config["bank_details"]) < 1:
        raise ValueError("Bank details must be a list with at least 1 line")


def generate_invoice(config_file: str, invoice_number: str, date: str, hours: float) -> None:
    """Generate PDF invoice from configuration and parameters."""
    config = load_config(config_file)

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
    elif unit_of_work == "MONTHLY":
        unit_header = "Number of Months"
        rate_header = "Monthly Rate"
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
        headers.extend(["Amount", "VAT (20%)", "Total Amount"])
    else:
        headers.append("Total Amount")

    amount_excl_vat = hours * rate
    row = [
        "Consulting Services",
        hours,
        f"{currency_symbol}{rate:.2f}",
        f"{currency_symbol}{amount_excl_vat:.2f}",
    ]
    if include_vat:
        vat_amount = amount_excl_vat * 0.2
        total_amount = amount_excl_vat + vat_amount
        row.extend([
            f"{currency_symbol}{vat_amount:.2f}",
            f"{currency_symbol}{total_amount:.2f}"
        ])

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

    try:
        doc.build(elements)
        logging.info(f"Invoice {file_name} generated successfully.")
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        sys.exit(1)


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate command-line arguments."""
    if not args.config:
        raise ValueError("Configuration file path is required")
    
    if not args.number or not args.number.strip():
        raise ValueError("Invoice number cannot be empty")
    
    if not args.date or not args.date.strip():
        raise ValueError("Invoice date cannot be empty")
    
    if args.units <= 0:
        raise ValueError("Units must be greater than 0")


def main() -> None:
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
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        validate_arguments(args)
        generate_invoice(args.config, args.number, args.date, args.units)
    except ValueError as e:
        logging.error(f"Invalid argument: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
