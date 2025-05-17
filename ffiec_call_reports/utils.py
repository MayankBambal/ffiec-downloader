"""
Utility functions for FFIEC Call Reports.
"""

from html import unescape
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, Optional, Any
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def parse_xbrl_to_dataframe(content: str, rssd_id: str) -> pd.DataFrame:
    """
    Parse XBRL content into a DataFrame with proper data types and validation.
    
    Args:
        content: The XBRL content to parse
        rssd_id: The RSSD ID of the institution
        
    Returns:
        DataFrame containing the parsed data
        
    Raises:
        ValueError: If the XBRL content is invalid or missing required elements
    """
    try:
        content = unescape(content)
        soup = BeautifulSoup(content, "xml")
        xbrl_tag = soup.find("xbrl")
        
        if not xbrl_tag:
            raise ValueError("No <xbrl> element found in the file!")
        
        records = []
        for tag in xbrl_tag.find_all():
            if not tag.has_attr("decimals"):
                continue
                
            fact_id = tag.name.split(":")[-1]
            value = tag.get_text(strip=True)
            
            # Skip empty values
            if not value:
                continue
                
            # Convert value to appropriate type
            try:
                decimal = int(tag["decimals"])
                if decimal < 0:
                    # Handle negative decimals (e.g., -2 means divide by 100)
                    value = float(value) / (10 ** abs(decimal))
                else:
                    value = float(value) / (10 ** decimal)
            except (ValueError, TypeError):
                # If conversion fails, keep as string
                pass
                
            # Get additional attributes if available
            context_ref = tag.get("contextRef", "")
            unit_ref = tag.get("unitRef", "")
            
            records.append({
                "rssd_id": rssd_id,
                "id": fact_id,
                "value": value,
                "decimal": decimal,
                "context_ref": context_ref,
                "unit_ref": unit_ref
            })
            
        if not records:
            raise ValueError("No valid data found in XBRL content")
            
        df = pd.DataFrame(records)
        
        # Convert numeric columns to appropriate types
        numeric_cols = ["value", "decimal"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                
        return df
        
    except Exception as e:
        logger.error(f"Error parsing XBRL content: {str(e)}")
        raise ValueError(f"Failed to parse XBRL content: {str(e)}")

def get_mapping_dict(mapping_file: str = "downloads/taxonomy/MDRM/MDRM_CSV.csv") -> Dict[str, str]:
    """
    Load and process the MDRM mapping file with validation.
    
    Args:
        mapping_file: Path to the MDRM mapping CSV file
        
    Returns:
        Dictionary mapping metric IDs to their descriptions
        
    Raises:
        FileNotFoundError: If the mapping file doesn't exist
        ValueError: If the mapping file is invalid
    """
    try:
        mdrm_df = pd.read_csv(
            mapping_file,
            skiprows=1,
            dtype={"Mnemonic": str, "Item Code": str}
        )
        
        # Validate required columns
        required_cols = ["Mnemonic", "Item Code", "Item Name"]
        missing_cols = [col for col in required_cols if col not in mdrm_df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in mapping file: {missing_cols}")
        
        # Clean and validate data
        mdrm_df["Mnemonic"] = mdrm_df["Mnemonic"].str.strip()
        mdrm_df["Item Code"] = mdrm_df["Item Code"].str.strip().str.zfill(4)
        
        # Validate data
        if mdrm_df["Mnemonic"].isnull().any() or mdrm_df["Item Code"].isnull().any():
            raise ValueError("Found null values in required columns")
            
        mdrm_df["metric"] = mdrm_df["Mnemonic"] + mdrm_df["Item Code"]
        
        # Check for duplicate metrics
        duplicates = mdrm_df[mdrm_df["metric"].duplicated()]
        if not duplicates.empty:
            logger.warning(f"Found duplicate metrics in mapping file: {duplicates['metric'].tolist()}")
        
        return pd.Series(
            mdrm_df["Item Name"].values,
            index=mdrm_df["metric"]
        ).to_dict()
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Mapping file not found: {mapping_file}")
    except Exception as e:
        raise ValueError(f"Error processing mapping file: {str(e)}")

def apply_mapping(df: pd.DataFrame, mapping_dict: Dict[str, str]) -> pd.DataFrame:
    """
    Apply metric mapping to a DataFrame with validation.
    
    Args:
        df: DataFrame containing the call report data
        mapping_dict: Dictionary mapping metric IDs to descriptions
        
    Returns:
        DataFrame with added 'label' column
        
    Raises:
        ValueError: If the input data is invalid
    """
    if df.empty:
        raise ValueError("Input DataFrame is empty")
        
    if not mapping_dict:
        raise ValueError("Mapping dictionary is empty")
        
    df = df.copy()
    
    # Apply mapping
    df["label"] = df["id"].map(mapping_dict)
    
    # Log unmapped metrics
    unmapped = df[df["label"].isna()]
    if not unmapped.empty:
        logger.warning(f"Found {len(unmapped)} unmapped metrics")
        
    # Fill missing labels
    df["label"] = df["label"].fillna("Unknown metric")
    
    return df

def validate_dataframe(df: pd.DataFrame) -> bool:
    """
    Validate the structure and content of a call report DataFrame.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if df.empty:
        logger.error("DataFrame is empty")
        return False
        
    required_cols = ["rssd_id", "id", "value"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        return False
        
    # Check for null values in required columns
    null_counts = df[required_cols].isnull().sum()
    if null_counts.any():
        logger.error(f"Found null values in required columns: {null_counts[null_counts > 0]}")
        return False
        
    return True 