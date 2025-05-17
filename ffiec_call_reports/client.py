"""
FFIEC API Client for downloading Call Reports.
"""

import base64
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional, Union
import textwrap
import re
from requests.exceptions import RequestException, Timeout
import time

from .models import CallReport
from .utils import parse_xbrl_to_dataframe

class FFIECClientError(Exception):
    """Base exception for FFIEC client errors."""
    pass

class FFIECClient:
    """Client for interacting with the FFIEC Call Reports API."""
    
    BASE_URL = "https://cdr.ffiec.gov/public/pws/webservices/retrievalservice.asmx"
    DEFAULT_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    def __init__(self, username: str, passphrase: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the FFIEC client.
        
        Args:
            username: FFIEC API username
            passphrase: FFIEC API passphrase
            timeout: Request timeout in seconds
        """
        if not username or not passphrase:
            raise FFIECClientError("Username and passphrase are required")
            
        self.username = username
        self.passphrase = passphrase
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": "http://cdr.ffiec.gov/public/services/RetrieveFacsimile"
        }
    
    def _validate_period_end_date(self, period_end_date: str) -> str:
        """Validate and format the period end date."""
        if isinstance(period_end_date, datetime):
            return period_end_date.strftime("%Y/%m/%d")
            
        # Check format YYYY/MM/DD
        if not re.match(r'^\d{4}/\d{2}/\d{2}$', period_end_date):
            raise FFIECClientError("period_end_date must be in YYYY/MM/DD format")
            
        # Validate date components
        try:
            datetime.strptime(period_end_date, "%Y/%m/%d")
        except ValueError:
            raise FFIECClientError("Invalid date in period_end_date")
            
        return period_end_date
    
    def _validate_rssd_id(self, rssd_id: Union[int, str]) -> int:
        """Validate the RSSD ID."""
        try:
            rssd_id = int(rssd_id)
            if rssd_id <= 0:
                raise FFIECClientError("RSSD ID must be a positive integer")
            return rssd_id
        except ValueError:
            raise FFIECClientError("RSSD ID must be a valid integer")
    
    def _make_soap_body(self, rssd_id: int, period_end_date: str) -> str:
        """Build the SOAP envelope for the API request."""
        raw = f"""\
        <?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                         xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"
                         xmlns:wsa="http://www.w3.org/2005/08/addressing">
          <soap12:Header>
            <wsa:Action>http://cdr.ffiec.gov/public/services/RetrieveFacsimile</wsa:Action>
            <wsa:To>https://cdr.ffiec.gov/public/pws/webservices/retrievalservice.asmx</wsa:To>
            <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
              <wsse:UsernameToken>
                <wsse:Username>{self.username}</wsse:Username>
                <wsse:Password>{self.passphrase}</wsse:Password>
              </wsse:UsernameToken>
            </wsse:Security>
          </soap12:Header>
          <soap12:Body>
            <RetrieveFacsimile xmlns="http://cdr.ffiec.gov/public/services">
              <dataSeries>Call</dataSeries>
              <reportingPeriodEndDate>{period_end_date}</reportingPeriodEndDate>
              <fiIDType>ID_RSSD</fiIDType>
              <fiID>{rssd_id}</fiID>
              <facsimileFormat>XBRL</facsimileFormat>
            </RetrieveFacsimile>
          </soap12:Body>
        </soap12:Envelope>"""
        return textwrap.dedent(raw).strip()
    
    def _fetch_facsimile(self, body: str) -> requests.Response:
        """Make the API request to fetch the call report with retries."""
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.post(
                    self.BASE_URL,
                    data=body,
                    headers=self.headers,
                    timeout=self.timeout,
                    verify=True  # Enable SSL verification
                )
                response.raise_for_status()
                return response
            except Timeout:
                if attempt == self.MAX_RETRIES - 1:
                    raise FFIECClientError("Request timed out after multiple retries")
                time.sleep(self.RETRY_DELAY)
            except RequestException as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise FFIECClientError(f"API request failed: {str(e)}")
                time.sleep(self.RETRY_DELAY)
    
    def _parse_response(self, response: requests.Response) -> Optional[str]:
        """Parse the API response and extract the XBRL content."""
        try:
            namespaces = {
                "soap": "http://schemas.xmlsoap.org/soap/envelope/",
                "ns": "http://cdr.ffiec.gov/public/services"
            }
            root = ET.fromstring(response.text)
            result = root.find(".//ns:RetrieveFacsimileResult", namespaces)
            
            if result is None or not result.text:
                return None
                
            return base64.b64decode(result.text).decode('utf-8')
        except (ET.ParseError, UnicodeDecodeError) as e:
            raise FFIECClientError(f"Failed to parse API response: {str(e)}")
    
    def get_call_report(
        self,
        rssd_id: Union[int, str],
        period_end_date: Union[str, datetime]
    ) -> Optional[CallReport]:
        """
        Download a call report for a specific RSSD ID and period.
        
        Args:
            rssd_id: The RSSD ID of the institution
            period_end_date: The end date of the reporting period (YYYY/MM/DD)
            
        Returns:
            CallReport object if successful, None if no data found
            
        Raises:
            FFIECClientError: If there are any issues with the request or data
        """
        # Validate inputs
        rssd_id = self._validate_rssd_id(rssd_id)
        period_end_date = self._validate_period_end_date(period_end_date)
        
        # Make API request
        soap_body = self._make_soap_body(rssd_id, period_end_date)
        response = self._fetch_facsimile(soap_body)
        
        # Parse response
        xbrl_content = self._parse_response(response)
        if xbrl_content is None:
            return None
        
        try:
            # Parse XBRL to DataFrame
            df = parse_xbrl_to_dataframe(xbrl_content, str(rssd_id))
            
            return CallReport(
                rssd_id=rssd_id,
                period_end_date=period_end_date,
                data=df
            )
        except Exception as e:
            raise FFIECClientError(f"Failed to process call report data: {str(e)}")
    
    def get_multiple_call_reports(
        self,
        rssd_ids: List[Union[int, str]],
        period_end_date: Union[str, datetime]
    ) -> List[CallReport]:
        """
        Download call reports for multiple RSSD IDs.
        
        Args:
            rssd_ids: List of RSSD IDs
            period_end_date: The end date of the reporting period (YYYY/MM/DD)
            
        Returns:
            List of CallReport objects (may be empty if no data found)
            
        Raises:
            FFIECClientError: If there are any issues with the request or data
        """
        if not rssd_ids:
            raise FFIECClientError("rssd_ids list cannot be empty")
            
        reports = []
        for rssd_id in rssd_ids:
            try:
                report = self.get_call_report(rssd_id, period_end_date)
                if report is not None:
                    reports.append(report)
            except FFIECClientError as e:
                print(f"Error processing RSSD ID {rssd_id}: {str(e)}")
                continue
        
        return reports 