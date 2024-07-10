# Invoice Generator

This is a simple command-line invoice generator that creates PDF invoices. The invoice includes client information, invoice details, and company information.

## Requirements

- Python 3.x
- `reportlab` library

## Installation

1. Clone the repository or download the script.
2. Install the required library:
   ```bash
   pip install reportlab
   ```

## Configuration

## Configuration

1. Copy the `config.json.template` file to `config.json`:
   ```bash
   cp config.json.template config.json
   ```

2. Update the `config.json` file with your company details:
   ```json
   {
       "company_name": "My Company",
       "company_address": "My Company Address",
       "bank_details": "Bank Details"
   }
   ```

Update the `config.json` file with your company details:
```json
{
    "company_name": "My Company",
    "company_address": "My Company Address",
    "bank_details": "Bank Details"
}
```

## Usage

Run the script with the following command:
```bash
python3 invoice_generator.py <client_name> <client_address> <invoice_number> <date> <hours> <rate>
```

### Example
```bash
python3 invoice_generator.py "Client Name" "Client Address" "001" "2023-10-01" 10 50
```

This will generate a PDF invoice with the specified details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
