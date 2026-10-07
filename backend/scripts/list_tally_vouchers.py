import httpx
import re

xml = """<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>Voucher Collection</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVCURRENTCOMPANY>Pawan Glasses</SVCURRENTCOMPANY>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="Voucher Collection" ISINITIALIZE="Yes">
            <TYPE>Voucher</TYPE>
            <FETCH>Date, VoucherTypeName, VoucherNumber, Reference, Narration, Amount</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>"""

r = httpx.post("http://localhost:9000", content=xml.encode("utf-8"), headers={"Content-Type": "text/xml"}, timeout=5.0)
clean = re.sub(r'&#[0-9]+;', '', r.text)
vouchers = re.findall(r'<VOUCHER[^>]*>([\s\S]*?)</VOUCHER>', clean)
print(f"Total Vouchers in Tally: {len(vouchers)}")
for v in vouchers:
    date = re.search(r'<DATE[^>]*>([^<]+)</DATE>', v)
    vtype = re.search(r'<VOUCHERTYPENAME[^>]*>([^<]+)</VOUCHERTYPENAME>', v)
    vno = re.search(r'<VOUCHERNUMBER[^>]*>([^<]+)</VOUCHERNUMBER>', v)
    ref = re.search(r'<REFERENCE[^>]*>([^<]+)</REFERENCE>', v)
    amt = re.search(r'<AMOUNT[^>]*>([^<]+)</AMOUNT>', v)
    print(f" -> Date: {date.group(1) if date else ''} | Type: {vtype.group(1) if vtype else ''} | No: {vno.group(1) if vno else ''} | Ref: {ref.group(1) if ref else ''} | Amt: {amt.group(1) if amt else ''}")
