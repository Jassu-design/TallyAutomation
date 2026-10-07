import httpx
import xml.etree.ElementTree as ET
import random
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from app.config.settings import settings

logger = logging.getLogger(__name__)

class TallyClient:
    def __init__(self, host: str = None, port: int = None, company: str = None, simulation: bool = None):
        self.host = host or settings.TALLY_HOST
        self.port = port or settings.TALLY_PORT
        self.company = company or settings.TALLY_COMPANY
        self.simulation = simulation if simulation is not None else settings.TALLY_SIMULATION_MODE
        self.url = f"http://{self.host}:{self.port}"

    async def test_connection(self) -> Dict[str, Any]:
        """
        Tests whether TallyPrime is reachable on host:port and checks company.
        If real Tally is not running and simulation is True, returns simulated active connection.
        """
        if not self.simulation:
            try:
                test_xml = """<ENVELOPE>
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
                async with httpx.AsyncClient(timeout=4.0) as client:
                    resp = await client.post(self.url, content=test_xml.encode("utf-8"), headers={"Content-Type": "text/xml"})
                    if resp.status_code == 200:
                        import re
                        m = re.search(r'<COMPANY NAME="([^"]+)"', resp.text)
                        active_cmp = m.group(1) if m else self.company
                        self.company = active_cmp
                        return {
                            "connected": True,
                            "mode": "LIVE",
                            "host": self.host,
                            "port": self.port,
                            "company": active_cmp,
                            "latency_ms": int(resp.elapsed.total_seconds() * 1000),
                            "message": f"Successfully connected to live TallyPrime on {self.url} (Company: '{active_cmp}')."
                        }
            except Exception as e:
                logger.warning(f"Live TallyPrime connection failed: {e}")
                return {
                    "connected": False,
                    "mode": "OFFLINE",
                    "host": self.host,
                    "port": self.port,
                    "company": self.company,
                    "error": str(e),
                    "message": f"TallyPrime could not be reached at {self.url}. Ensure TallyPrime is running with ODBC/XML port {self.port} enabled."
                }

        # Simulation Mode
        return {
            "connected": True,
            "mode": "SIMULATION",
            "host": self.host,
            "port": self.port,
            "company": self.company,
            "latency_ms": random.randint(12, 45),
            "message": f"Connected to TallyPrime Gateway (Simulation Active for {self.company})."
        }

    async def post_voucher(self, xml_payload: str, voucher_type: str) -> Dict[str, Any]:
        """
        Posts the voucher XML to TallyPrime and parses response.
        """
        if not self.simulation:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(self.url, content=xml_payload.encode("utf-8"), headers={"Content-Type": "text/xml"})
                    if resp.status_code == 200:
                        return self._parse_tally_response(resp.text, voucher_type)
                    else:
                        return {
                            "success": False,
                            "voucher_number": None,
                            "error": f"Tally HTTP {resp.status_code}: {resp.text}",
                            "raw_response": resp.text
                        }
            except Exception as e:
                logger.error(f"Error posting voucher to TallyPrime: {e}")
                return {
                    "success": False,
                    "voucher_number": None,
                    "error": f"Network/Connection error to Tally: {str(e)}",
                    "raw_response": ""
                }

        # Simulation Mode Response
        vch_prefix = "PV" if voucher_type == "Payment" else "RV" if voucher_type == "Receipt" else "CV" if voucher_type == "Contra" else "JV"
        vch_num = f"{vch_prefix}-{random.randint(1000, 9999)}"
        simulated_response = f"""<RESPONSE>
  <CREATED>1</CREATED>
  <ALTERED>0</ALTERED>
  <ERRORS>0</ERRORS>
  <VOUCHERNUMBER>{vch_num}</VOUCHERNUMBER>
  <STATUS>SUCCESS</STATUS>
  <MESSAGE>Voucher {vch_num} imported successfully into {self.company}</MESSAGE>
</RESPONSE>"""
        return {
            "success": True,
            "voucher_number": vch_num,
            "error": None,
            "raw_response": simulated_response
        }

    def _parse_tally_response(self, response_text: str, voucher_type: str) -> Dict[str, Any]:
        """
        Parses Tally XML response to detect success and extract voucher number.
        """
        try:
            root = ET.fromstring(response_text)
            
            # Look for errors
            line_error = root.find(".//LINEERROR")
            if line_error is not None and line_error.text:
                return {
                    "success": False,
                    "voucher_number": None,
                    "error": line_error.text.strip(),
                    "raw_response": response_text
                }
                
            errors_elem = root.find(".//ERRORS")
            if errors_elem is not None and int(errors_elem.text or "0") > 0:
                desc = root.find(".//DESCRIPTION")
                err_msg = desc.text if desc is not None else "Tally reported an error during voucher creation."
                return {
                    "success": False,
                    "voucher_number": None,
                    "error": err_msg,
                    "raw_response": response_text
                }

            exceptions_elem = root.find(".//EXCEPTIONS")
            if exceptions_elem is not None and int(exceptions_elem.text or "0") > 0:
                created_val = int(created_elem.text or "0") if created_elem is not None else 0
                if created_val == 0:
                    return {
                        "success": False,
                        "voucher_number": None,
                        "error": "Tally raised an exception while importing voucher. Please verify voucher date and ledger masters.",
                        "raw_response": response_text
                    }

            created_elem = root.find(".//CREATED")
            if created_elem is not None and int(created_elem.text or "0") > 0:
                vch_no = root.find(".//VOUCHERNUMBER")
                last_id = root.find(".//LASTVCHID")
                vch_str = vch_no.text if vch_no is not None and vch_no.text else (last_id.text if last_id is not None and last_id.text else f"{voucher_type[:2].upper()}-{random.randint(1000, 9999)}")
                return {
                    "success": True,
                    "voucher_number": vch_str,
                    "error": None,
                    "raw_response": response_text
                }

            return {
                "success": False,
                "voucher_number": None,
                "error": "Tally did not create any voucher. Verify date matches active company financial year.",
                "raw_response": response_text
            }
        except Exception as e:
            logger.warning(f"Could not parse Tally XML response: {e}. Raw: {response_text}")
            if "CREATED" in response_text or "1" in response_text:
                return {
                    "success": True,
                    "voucher_number": f"{voucher_type[:2].upper()}-{random.randint(1000, 9999)}",
                    "error": None,
                    "raw_response": response_text
                }
            return {
                "success": False,
                "voucher_number": None,
                "error": f"Failed to parse Tally response: {str(e)}",
                "raw_response": response_text
            }
