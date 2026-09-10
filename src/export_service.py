import csv
import uuid
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXPORT_DIR = PROJECT_ROOT / "data" / "generated"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def format_address(address):
    """
    Supports either:

    "123 Main Street, NY"

    or

    {
        "street":"123 Main Street",
        "city":"NY"
    }
    """

    if not address:
        return ""

    if isinstance(address, str):
        return address

    if isinstance(address,dict):
        return ", ".join(
            str(v)
            for v in address.values()
            if v
        )

    return str(address)


def format_money(invoice, field):
    """
    Preserve existing currency symbols.

    If the LLM returns

    "$145.00"

    keep it.

    If it returns

    "145.00"

    and

    currency_symbol="$"

    prepend "$".
    """

    value = invoice.get(field)

    if value is None:
        return ""

    value = str(value)

    if value == "":
        return ""

    symbol = invoice.get("currency_symbol")

    if symbol and not value.startswith(symbol):
        return symbol + value

    return value


# ---------------------------------------------------------
# CSV
# ---------------------------------------------------------

def export_invoice_csv(invoice):

    filename = f"invoice_{uuid.uuid4().hex}.csv"

    path = EXPORT_DIR / filename

    with open(path,"w",newline="",encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            "invoice_number",
            "invoice_date",
            "due_date",
            "vendor_name",
            "vendor_address",
            "customer_name",
            "customer_address",
            "currency",
            "currency_symbol",
            "subtotal",
            "tax",
            "total"
        ])

        writer.writerow([

            invoice.get("invoice_number",""),

            invoice.get("invoice_date",""),

            invoice.get("due_date",""),

            invoice.get("vendor_name",""),

            format_address(
                invoice.get("vendor_address")
            ),

            invoice.get("customer_name",""),

            format_address(
                invoice.get("customer_address")
            ),

            invoice.get("currency",""),

            invoice.get("currency_symbol",""),

            format_money(invoice,"subtotal"),

            format_money(invoice,"tax"),

            format_money(invoice,"total")

        ])

        writer.writerow([])

        writer.writerow([
            "description",
            "quantity",
            "unit_price",
            "amount"
        ])

        for item in invoice.get("items",[]):

            writer.writerow([

                item.get("description",""),

                item.get("quantity",""),

                item.get("unit_price",""),

                item.get("amount","")

            ])

    return filename


# ---------------------------------------------------------
# PDF
# ---------------------------------------------------------

def export_invoice_pdf(invoice):

    filename = f"invoice_{uuid.uuid4().hex}.pdf"

    path = EXPORT_DIR / filename

    document = SimpleDocTemplate(
        str(path),
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Extracted Invoice",
            styles["Title"]
        )
    )

    elements.append(
        Spacer(1,20)
    )

    fields = [

        [
            "Invoice Number",
            str(invoice.get("invoice_number",""))
        ],

        [
            "Invoice Date",
            str(invoice.get("invoice_date",""))
        ],

        [
            "Due Date",
            str(invoice.get("due_date",""))
        ],

        [
            "Vendor",
            str(invoice.get("vendor_name",""))
        ],

        [
            "Vendor Address",
            format_address(
                invoice.get("vendor_address")
            )
        ],

        [
            "Customer",
            str(invoice.get("customer_name",""))
        ],

        [
            "Customer Address",
            format_address(
                invoice.get("customer_address")
            )
        ],

        [
            "Currency",
            f"{invoice.get('currency_symbol','')} {invoice.get('currency','')}".strip()
        ],

        [
            "Subtotal",
            format_money(invoice,"subtotal")
        ],

        [
            "Tax",
            format_money(invoice,"tax")
        ],

        [
            "Total",
            format_money(invoice,"total")
        ]
    ]

    # Optional fields

    if invoice.get("bank_name"):

        fields.append([
            "Bank",
            invoice["bank_name"]
        ])

    if invoice.get("account_number"):

        fields.append([
            "Account Number",
            invoice["account_number"]
        ])

    if invoice.get("account_holder"):

        fields.append([
            "Account Holder",
            invoice["account_holder"]
        ])

    table = Table(
        fields,
        colWidths=[170,340]
    )

    table.setStyle(
        TableStyle([

            ("GRID",(0,0),(-1,-1),1,colors.grey),

            ("BACKGROUND",(0,0),(0,-1),colors.lightgrey),

            ("VALIGN",(0,0),(-1,-1),"TOP")

        ])
    )

    elements.append(table)

    elements.append(
        Spacer(1,20)
    )

    elements.append(
        Paragraph(
            "Invoice Items",
            styles["Heading2"]
        )
    )

    item_data = [[
        "Description",
        "Quantity",
        "Unit Price",
        "Amount"
    ]]

    for item in invoice.get("items",[]):

        item_data.append([

            str(item.get("description","")),

            str(item.get("quantity","")),

            str(item.get("unit_price","")),

            str(item.get("amount",""))

        ])

    item_table = Table(item_data)

    item_table.setStyle(

        TableStyle([

            ("GRID",(0,0),(-1,-1),1,colors.grey),

            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)

        ])

    )

    elements.append(item_table)

    document.build(elements)

    return filename