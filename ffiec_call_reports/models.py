"""
Data models for FFIEC Call Reports.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd

@dataclass
class CallReport:
    """
    Represents a single call report from the FFIEC.
    
    Attributes:
        rssd_id: The RSSD ID of the institution
        period_end_date: The end date of the reporting period
        data: DataFrame containing the call report data
        metadata: Optional dictionary containing additional metadata
    """
    rssd_id: int
    period_end_date: str
    data: pd.DataFrame
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate the call report data after initialization."""
        if not isinstance(self.rssd_id, int) or self.rssd_id <= 0:
            raise ValueError("rssd_id must be a positive integer")
            
        if not isinstance(self.period_end_date, str):
            raise ValueError("period_end_date must be a string")
            
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("data must be a pandas DataFrame")
            
        if self.data.empty:
            raise ValueError("data DataFrame cannot be empty")
            
        required_cols = ["rssd_id", "id", "value"]
        missing_cols = [col for col in required_cols if col not in self.data.columns]
        if missing_cols:
            raise ValueError(f"DataFrame missing required columns: {missing_cols}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the call report to a dictionary.
        
        Returns:
            Dictionary representation of the call report
        """
        return {
            "rssd_id": self.rssd_id,
            "period_end_date": self.period_end_date,
            "data": self.data.to_dict(orient="records"),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CallReport":
        """
        Create a CallReport instance from a dictionary.
        
        Args:
            data: Dictionary containing call report data
            
        Returns:
            CallReport instance
            
        Raises:
            ValueError: If the dictionary is missing required fields
        """
        required_fields = ["rssd_id", "period_end_date", "data"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Dictionary missing required fields: {missing_fields}")
            
        return cls(
            rssd_id=data["rssd_id"],
            period_end_date=data["period_end_date"],
            data=pd.DataFrame(data["data"]),
            metadata=data.get("metadata")
        )
    
    def get_metric(self, metric_id: str) -> Optional[float]:
        """
        Get the value of a specific metric.
        
        Args:
            metric_id: The ID of the metric to retrieve
            
        Returns:
            The metric value if found, None otherwise
        """
        metric_data = self.data[self.data["id"] == metric_id]
        if metric_data.empty:
            return None
        return metric_data["value"].iloc[0]
    
    def get_metrics(self, metric_ids: list[str]) -> Dict[str, Optional[float]]:
        """
        Get values for multiple metrics.
        
        Args:
            metric_ids: List of metric IDs to retrieve
            
        Returns:
            Dictionary mapping metric IDs to their values
        """
        return {metric_id: self.get_metric(metric_id) for metric_id in metric_ids}
    
    def filter_by_metrics(self, metric_ids: list[str]) -> pd.DataFrame:
        """
        Filter the data to include only specific metrics.
        
        Args:
            metric_ids: List of metric IDs to include
            
        Returns:
            DataFrame containing only the specified metrics
        """
        return self.data[self.data["id"].isin(metric_ids)]
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the call report.
        
        Returns:
            Dictionary containing summary information
        """
        return {
            "rssd_id": self.rssd_id,
            "period_end_date": self.period_end_date,
            "total_metrics": len(self.data),
            "unique_metrics": self.data["id"].nunique(),
            "has_metadata": self.metadata is not None
        } 