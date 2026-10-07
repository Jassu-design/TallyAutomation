import httpx
import xml.etree.ElementTree as ET

def get_active_company():
    xml = """<ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Company Collection</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES><SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT></STATICVARIABLES>
          <TDL><TDLMESSAGE><COLLECTION NAME="Company Collection" ISINITIALIZE="Yes"><TYPE>Company</TYPE><FETCH>Name</FETCH></COLLECTION></TDLMESSAGE></TDL>
        </DESC>
      </BODY>
    </ENVELOPE>"""
    r = httpx.post("http://localhost:9000", content=xml.encode("utf-8"), headers={"Content-Type": "text/xml"}, timeout=5.0)
    import re
    match = re.search(r'<COMPANY NAME="([^"]+)"', r.text)
    if match:
        return match.group(1)
    return "Pawan Glasses"

def create_masters_if_needed(company: str):
    masters_xml = f"""<ENVELOPE>
  <HEADER>
    <TALLYREQUEST>Import Data</TALLYREQUEST>
  </HEADER>
  <BODY>
    <IMPORTDATA>
      <REQUESTDESC>
        <REPORTNAME>All Masters</REPORTNAME>
        <STATICVARIABLES>
          <SVCURRENTCOMPANY>{company}</SVCURRENTCOMPANY>
        </STATICVARIABLES>
      </REQUESTDESC>
      <REQUESTDATA>
        <TALLYMESSAGE xmlns:UDF="TallyUDF">
          <LEDGER NAME="B R Duggar And Company" ACTION="Create">
            <NAME>B R Duggar And Company</NAME>
            <PARENT>Sundry Debtors</PARENT>
            <OPENINGBALANCE>0</OPENINGBALANCE>
            <ISBILLWISEON>Yes</ISBILLWISEON>
            <PARTYGSTIN>08AABCB1234F1Z5</PARTYGSTIN>
          </LEDGER>
          <LEDGER NAME="Sales @ 5%" ACTION="Create">
            <NAME>Sales @ 5%</NAME>
            <PARENT>Sales Accounts</PARENT>
          </LEDGER>
          <LEDGER NAME="Output CGST @ 2.5%" ACTION="Create">
            <NAME>Output CGST @ 2.5%</NAME>
            <PARENT>Duties &amp; Taxes</PARENT>
            <TAXTYPE>GST</TAXTYPE>
            <GSTDUTYHEAD>CGST</GSTDUTYHEAD>
          </LEDGER>
          <LEDGER NAME="Output SGST @ 2.5%" ACTION="Create">
            <NAME>Output SGST @ 2.5%</NAME>
            <PARENT>Duties &amp; Taxes</PARENT>
            <TAXTYPE>GST</TAXTYPE>
            <GSTDUTYHEAD>SGST</GSTDUTYHEAD>
          </LEDGER>
          <LEDGER NAME="Round Off" ACTION="Create">
            <NAME>Round Off</NAME>
            <PARENT>Indirect Expenses</PARENT>
          </LEDGER>
          <LEDGER NAME="HDFC Bank Account" ACTION="Create">
            <NAME>HDFC Bank Account</NAME>
            <PARENT>Bank Accounts</PARENT>
          </LEDGER>
          <UNIT NAME="Kgs" ACTION="Create">
            <NAME>Kgs</NAME>
            <ISSIMPLEUNIT>Yes</ISSIMPLEUNIT>
          </UNIT>
          <STOCKITEM NAME="Shree Ram Special Moong Papad (400g Pouch)" ACTION="Create">
            <NAME>Shree Ram Special Moong Papad (400g Pouch)</NAME>
            <BASEUNITS>Kgs</BASEUNITS>
          </STOCKITEM>
        </TALLYMESSAGE>
      </REQUESTDATA>
    </IMPORTDATA>
  </BODY>
</ENVELOPE>"""
    r = httpx.post("http://localhost:9000", content=masters_xml.encode("utf-8"), headers={"Content-Type": "text/xml"}, timeout=10.0)
    print("Masters Creation Response:", r.text)

if __name__ == "__main__":
    cmp = get_active_company()
    print("Active Company in Tally:", cmp)
    create_masters_if_needed(cmp)
