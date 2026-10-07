import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, Optional, List

def format_date_tally(date_str: str) -> str:
    """Converts YYYY-MM-DD to YYYYMMDD for Tally XML."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y%m%d")
    except Exception:
        clean = "".join(filter(str.isdigit, str(date_str)))
        return clean if len(clean) == 8 else datetime.now().strftime("%Y%m%d")

def escape_xml(s: Any) -> str:
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

def build_voucher_xml(
    company_name: str,
    voucher_type: str,
    date_str: str,
    amount: float,
    transaction_type: str,
    bank_ledger: str,
    party_ledger: str,
    narration: str,
    reference: Optional[str] = None
) -> str:
    """
    Builds standard TallyPrime XML voucher import payload (Payment, Receipt, Contra, Journal).
    In Tally XML:
    Debit amount is signed negative (-amount)
    Credit amount is signed positive (+amount)
    """
    tally_date = format_date_tally(date_str)
    ref_clean = escape_xml(reference)
    narration_clean = escape_xml(narration)
    bank_ledger_clean = escape_xml(bank_ledger)
    party_ledger_clean = escape_xml(party_ledger)

    if voucher_type == "Payment":
        party_is_deemed_positive = "Yes"
        party_amount = f"-{amount:.2f}"
        bank_is_deemed_positive = "No"
        bank_amount = f"{amount:.2f}"
    elif voucher_type == "Receipt":
        bank_is_deemed_positive = "Yes"
        bank_amount = f"-{amount:.2f}"
        party_is_deemed_positive = "No"
        party_amount = f"{amount:.2f}"
    elif voucher_type == "Contra":
        if transaction_type == "DEBIT":
            party_is_deemed_positive = "Yes"
            party_amount = f"-{amount:.2f}"
            bank_is_deemed_positive = "No"
            bank_amount = f"{amount:.2f}"
        else:
            bank_is_deemed_positive = "Yes"
            bank_amount = f"-{amount:.2f}"
            party_is_deemed_positive = "No"
            party_amount = f"{amount:.2f}"
    else:  # Journal or default
        party_is_deemed_positive = "Yes"
        party_amount = f"-{amount:.2f}"
        bank_is_deemed_positive = "No"
        bank_amount = f"{amount:.2f}"

    xml_payload = f"""<ENVELOPE>
  <HEADER>
    <TALLYREQUEST>Import Data</TALLYREQUEST>
  </HEADER>
  <BODY>
    <IMPORTDATA>
      <REQUESTDESC>
        <REPORTNAME>Vouchers</REPORTNAME>
        <STATICVARIABLES>
          <SVCURRENTCOMPANY>{escape_xml(company_name)}</SVCURRENTCOMPANY>
        </STATICVARIABLES>
      </REQUESTDESC>
      <REQUESTDATA>
        <TALLYMESSAGE xmlns:UDF="TallyUDF">
          <VOUCHER VCHTYPE="{voucher_type}" ACTION="Create">
            <DATE>{tally_date}</DATE>
            <VOUCHERTYPENAME>{voucher_type}</VOUCHERTYPENAME>
            <REFERENCE>{ref_clean}</REFERENCE>
            <NARRATION>{narration_clean}</NARRATION>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>{party_ledger_clean}</LEDGERNAME>
              <ISDEEMEDPOSITIVE>{party_is_deemed_positive}</ISDEEMEDPOSITIVE>
              <AMOUNT>{party_amount}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>{bank_ledger_clean}</LEDGERNAME>
              <ISDEEMEDPOSITIVE>{bank_is_deemed_positive}</ISDEEMEDPOSITIVE>
              <AMOUNT>{bank_amount}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
          </VOUCHER>
        </TALLYMESSAGE>
      </REQUESTDATA>
    </IMPORTDATA>
  </BODY>
</ENVELOPE>"""
    return xml_payload


def build_sales_invoice_xml(
    company_name: str,
    invoice_no: str,
    date_str: str,
    buyer_name: str,
    buyer_gstin: str,
    sub_total: float,
    cgst_amount: float,
    sgst_amount: float,
    igst_amount: float,
    round_off: float,
    total_amount: float,
    items: Optional[List[Dict[str, Any]]] = None,
    sales_ledger: str = "Sales @ 5%",
    cgst_ledger: str = "Output CGST @ 2.5%",
    sgst_ledger: str = "Output SGST @ 2.5%",
    igst_ledger: str = "Output IGST",
    round_off_ledger: str = "Round Off",
    narration: Optional[str] = None,
    irn: Optional[str] = None,
    eway_bill_no: Optional[str] = None,
    vehicle_no: Optional[str] = None
) -> str:
    """
    Builds authentic TallyPrime Sales Invoice XML payload (Item Invoice View with GST).
    Matches standard GST e-Invoice structure.
    """
    tally_date = format_date_tally(date_str)
    
    # Narration string with e-Invoice details
    full_narration = narration or f"Tax Invoice {invoice_no}"
    if eway_bill_no:
        full_narration += f" | e-Way Bill: {eway_bill_no}"
    if vehicle_no:
        full_narration += f" | Veh: {vehicle_no}"
    if irn:
        full_narration += f" | IRN: {irn[:24]}..."

    # Inventory entries XML
    inventory_xml = ""
    if items:
        for itm in items:
            name = escape_xml(itm.get("item_name", "General Goods"))
            qty = itm.get("qty", 1.0)
            unit = itm.get("unit", "Kgs")
            rate = itm.get("rate", 0.0)
            disc = itm.get("discount_percent", 0.0)
            amt = itm.get("amount", 0.0)

            inventory_xml += f"""
            <ALLINVENTORYENTRIES.LIST>
              <STOCKITEMNAME>{name}</STOCKITEMNAME>
              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
              <RATE>{rate:.2f}/{unit}</RATE>
              <DISCOUNT>{disc}</DISCOUNT>
              <ACTUALQTY>{qty:.3f} {unit}</ACTUALQTY>
              <BILLEDQTY>{qty:.3f} {unit}</BILLEDQTY>
              <AMOUNT>{amt:.2f}</AMOUNT>
              <ACCOUNTINGALLOCATIONS.LIST>
                <LEDGERNAME>{escape_xml(sales_ledger)}</LEDGERNAME>
                <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                <AMOUNT>{amt:.2f}</AMOUNT>
              </ACCOUNTINGALLOCATIONS.LIST>
            </ALLINVENTORYENTRIES.LIST>"""

    # Taxes XML
    tax_ledgers_xml = ""
    if cgst_amount > 0:
        tax_ledgers_xml += f"""
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>{escape_xml(cgst_ledger)}</LEDGERNAME>
              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
              <AMOUNT>{cgst_amount:.2f}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>"""
    if sgst_amount > 0:
        tax_ledgers_xml += f"""
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>{escape_xml(sgst_ledger)}</LEDGERNAME>
              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
              <AMOUNT>{sgst_amount:.2f}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>"""
    if igst_amount > 0:
        tax_ledgers_xml += f"""
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>{escape_xml(igst_ledger)}</LEDGERNAME>
              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
              <AMOUNT>{igst_amount:.2f}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>"""
    if round_off != 0.0:
        # Negative round off means decrease total (credit to customer / debit to round off)
        # In Tally XML, ISDEEMEDPOSITIVE=Yes requires negative amount, No requires positive amount
        ro_is_deemed_positive = "Yes" if round_off < 0 else "No"
        ro_amount = f"-{abs(round_off):.2f}" if round_off < 0 else f"{abs(round_off):.2f}"
        tax_ledgers_xml += f"""
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>{escape_xml(round_off_ledger)}</LEDGERNAME>
              <ISDEEMEDPOSITIVE>{ro_is_deemed_positive}</ISDEEMEDPOSITIVE>
              <AMOUNT>{ro_amount}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>"""

    xml_payload = f"""<ENVELOPE>
  <HEADER>
    <TALLYREQUEST>Import Data</TALLYREQUEST>
  </HEADER>
  <BODY>
    <IMPORTDATA>
      <REQUESTDESC>
        <REPORTNAME>Vouchers</REPORTNAME>
        <STATICVARIABLES>
          <SVCURRENTCOMPANY>{escape_xml(company_name)}</SVCURRENTCOMPANY>
        </STATICVARIABLES>
      </REQUESTDESC>
      <REQUESTDATA>
        <TALLYMESSAGE xmlns:UDF="TallyUDF">
          <VOUCHER VCHTYPE="Sales" ACTION="Create" OBJVIEW="Invoice Voucher View">
            <DATE>{tally_date}</DATE>
            <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
            <VOUCHERNUMBER>{escape_xml(invoice_no)}</VOUCHERNUMBER>
            <REFERENCE>{escape_xml(invoice_no)}</REFERENCE>
            <PARTYNAME>{escape_xml(buyer_name)}</PARTYNAME>
            <PARTYLEDGERNAME>{escape_xml(buyer_name)}</PARTYLEDGERNAME>
            <BASICBUYERNAME>{escape_xml(buyer_name)}</BASICBUYERNAME>
            <PARTYGSTIN>{escape_xml(buyer_gstin)}</PARTYGSTIN>
            <NARRATION>{escape_xml(full_narration)}</NARRATION>
            
            <!-- Customer / Debtor Ledger (Debit) -->
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>{escape_xml(buyer_name)}</LEDGERNAME>
              <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
              <ISPARTYLEDGER>Yes</ISPARTYLEDGER>
              <AMOUNT>-{total_amount:.2f}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>

            <!-- Sales Account (Credit) -->
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>{escape_xml(sales_ledger)}</LEDGERNAME>
              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
              <AMOUNT>{sub_total:.2f}</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
{tax_ledgers_xml}
{inventory_xml}
          </VOUCHER>
        </TALLYMESSAGE>
      </REQUESTDATA>
    </IMPORTDATA>
  </BODY>
</ENVELOPE>"""
    return xml_payload
