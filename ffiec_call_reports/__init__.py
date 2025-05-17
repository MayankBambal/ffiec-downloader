"""
FFIEC Call Reports Library

A Python library for downloading and processing FFIEC Call Reports.
"""

from .client import FFIECClient
from .models import CallReport
from .utils import parse_xbrl_to_dataframe, get_mapping_dict

__version__ = "0.1.0"
__all__ = ["FFIECClient", "CallReport", "parse_xbrl_to_dataframe", "get_mapping_dict"] 