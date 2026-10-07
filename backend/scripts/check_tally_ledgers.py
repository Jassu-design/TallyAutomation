import httpx
import re

xml = """<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>Ledger Collection</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVCURRENTCOMPANY>Pawan Glasses</SVCURRENTCOMPANY>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="Ledger Collection" ISINITIALIZE="Yes">
            <TYPE>Ledger</TYPE>
            <FETCH>Name, Parent</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>"""

try:
    r = httpx.post("http://localhost:9000", content=xml.encode("utf-8"), headers={"Content-Type": "text/xml"}, timeout=5.0)
    print("Status:", r.status_code)
    # Strip any control chars or XML entity invalid chars
    clean_text = re.sub(r'&#[0-9]+;', '', r.text)
    ledgers = re.findall(r'<LEDGER NAME="([^"]+)"', clean_text)
    print(f"Found {len(ledgers)} ledgers in Pawan Glasses:")
    for l in ledgers:
        print(f"  - {l}")
except Exception as e:
    print("Error:", e)
