import httpx

# Test with Sales voucher:
# 1. Without VOUCHERNUMBER tag (let Tally auto-number, or put reference in REFERENCE tag)
# 2. Correct signs:
#    Party (Debit): ISDEEMEDPOSITIVE=Yes, AMOUNT = -26853.00
#    Sales (Credit): ISDEEMEDPOSITIVE=No, AMOUNT = 25574.40
#    CGST (Credit): ISDEEMEDPOSITIVE=No, AMOUNT = 639.36
#    SGST (Credit): ISDEEMEDPOSITIVE=No, AMOUNT = 639.36
#    Round Off (-0.12 reduction / discount / debit):
#      Debit: ISDEEMEDPOSITIVE=Yes, AMOUNT = -0.12 (Wait! 25574.40 + 639.36 + 639.36 = 26853.12. Total is 26853.00. So Round Off is CREDIT 0.12?
#      No: 26853.12 - 0.12 = 26853.00.
#      Credit: Sales(25574.40) + CGST(639.36) + SGST(639.36) = 26853.12 Credit.
#      To reach 26853.00 Debit:
#      We need Round Off to be DEBIT 0.12? No!
#      Total Credit = 26853.12.
#      If Party Debit = 26853.00, then Debit is 26853.00 and Credit is 26853.12.
#      The credits exceed debits by 0.12!
#      Therefore, we need a DEBIT of 0.12:
#      Debit = Party (26853.00) + Round Off (0.12) = 26853.12 Debit!
#      Total Credit = 26853.12 Credit!
#      In Tally XML:
#      For a DEBIT entry: ISDEEMEDPOSITIVE=Yes, AMOUNT = -0.12!
#      In our earlier XML, we had AMOUNT = 0.12 with ISDEEMEDPOSITIVE=Yes! That was a contradiction!)

xml_sales = """<ENVELOPE>
  <HEADER>
    <TALLYREQUEST>Import Data</TALLYREQUEST>
  </HEADER>
  <BODY>
    <IMPORTDATA>
      <REQUESTDESC>
        <REPORTNAME>Vouchers</REPORTNAME>
        <STATICVARIABLES>
          <SVCURRENTCOMPANY>Pawan Glasses</SVCURRENTCOMPANY>
        </STATICVARIABLES>
      </REQUESTDESC>
      <REQUESTDATA>
        <TALLYMESSAGE xmlns:UDF="TallyUDF">
          <VOUCHER VCHTYPE="Sales" ACTION="Create">
            <DATE>20260802</DATE>
            <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
            <REFERENCE>BKN/3118/26-27</REFERENCE>
            <NARRATION>Tax Invoice BKN/3118/26-27 to B R Duggar And Company | Shree Ram Special Moong Papad (400g Pouch) Qty: 120 Kgs @ 220 | e-Way Bill: 791657124983 | Veh: RJ-07-GA-4521</NARRATION>
            <PARTYLEDGERNAME>B R Duggar And Company</PARTYLEDGERNAME>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>B R Duggar And Company</LEDGERNAME>
              <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
              <ISPARTYLEDGER>Yes</ISPARTYLEDGER>
              <AMOUNT>-26853.00</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>Sales @ 5%</LEDGERNAME>
              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
              <AMOUNT>25574.40</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>Output CGST @ 2.5%</LEDGERNAME>
              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
              <AMOUNT>639.36</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>Output SGST @ 2.5%</LEDGERNAME>
              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
              <AMOUNT>639.36</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>Round Off</LEDGERNAME>
              <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
              <AMOUNT>-0.12</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
          </VOUCHER>
        </TALLYMESSAGE>
      </REQUESTDATA>
    </IMPORTDATA>
  </BODY>
</ENVELOPE>"""

r = httpx.post("http://localhost:9000", content=xml_sales.encode("utf-8"), headers={"Content-Type": "text/xml"}, timeout=10.0)
print("Sales Test Response:\n", r.text)
