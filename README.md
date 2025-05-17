# FFIEC Call Reports Downloader

A Python library for downloading and processing FFIEC Call Reports using the FFIEC API.

## Features

- Download call reports for specific RSSD IDs and reporting periods
- Parse XBRL data into pandas DataFrames
- Support for multiple report downloads
- Automatic retry mechanism for failed requests
- Comprehensive error handling
- Data validation and type conversion

## Installation

```bash
pip install ffiec-call-reports
```

## Usage

```python
from ffiec_call_reports import FFIECClient

# Initialize the client
client = FFIECClient(
    username="your_username",
    passphrase="your_passphrase"
)

# Download a single call report
report = client.get_call_report(
    rssd_id=1234567,
    period_end_date="2023/12/31"
)

# Get specific metrics
total_assets = report.get_metric("RCFD2170")
print(f"Total Assets: ${total_assets:,.2f}")

# Download multiple reports
reports = client.get_multiple_call_reports(
    rssd_ids=[1234567, 7654321],
    period_end_date="2023/12/31"
)

# Filter reports by specific metrics
important_metrics = ["RCFD2170", "RCFD2948", "RCFD3210"]
filtered_data = report.filter_by_metrics(important_metrics)
```

## API Reference

### FFIECClient

The main client class for interacting with the FFIEC API.

#### Methods

- `get_call_report(rssd_id: Union[int, str], period_end_date: Union[str, datetime]) -> Optional[CallReport]`
  - Download a call report for a specific RSSD ID and period
  - Returns a CallReport object if successful, None if no data found

- `get_multiple_call_reports(rssd_ids: List[Union[int, str]], period_end_date: Union[str, datetime]) -> List[CallReport]`
  - Download call reports for multiple RSSD IDs
  - Returns a list of CallReport objects

### CallReport

Represents a single call report from the FFIEC.

#### Methods

- `get_metric(metric_id: str) -> Optional[float]`
  - Get the value of a specific metric
  - Returns the metric value if found, None otherwise

- `get_metrics(metric_ids: list[str]) -> Dict[str, Optional[float]]`
  - Get values for multiple metrics
  - Returns a dictionary mapping metric IDs to their values

- `filter_by_metrics(metric_ids: list[str]) -> pd.DataFrame`
  - Filter the data to include only specific metrics
  - Returns a DataFrame containing only the specified metrics

- `get_summary() -> Dict[str, Any]`
  - Get a summary of the call report
  - Returns a dictionary containing summary information

## Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ffiec_call_reports.git
cd ffiec_call_reports
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FFIEC for providing the Call Report data
- Contributors and maintainers of the dependencies