import httpx
import xml.etree.ElementTree as ET

xml = """<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>Company Collection</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="Company Collection" ISINITIALIZE="Yes">
            <TYPE>Company</TYPE>
            <FETCH>Name, StartingFrom, Guid</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>"""

try:
    r = httpx.post("http://localhost:9000", content=xml.encode("utf-8"), headers={"Content-Type": "text/xml"}, timeout=5.0)
    print("Status:", r.status_code)
    print("Response text:\n", r.text[:2000])
except Exception as e:
    print("Error:", e)
