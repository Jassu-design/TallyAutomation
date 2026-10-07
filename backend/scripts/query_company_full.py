import httpx

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
      <TDL><TDLMESSAGE><COLLECTION NAME="Company Collection" ISINITIALIZE="Yes"><TYPE>Company</TYPE><FETCH>*</FETCH></COLLECTION></TDLMESSAGE></TDL>
    </DESC>
  </BODY>
</ENVELOPE>"""

r = httpx.post("http://localhost:9000", content=xml.encode("utf-8"), headers={"Content-Type": "text/xml"}, timeout=5.0)
print(r.text[:3000])
