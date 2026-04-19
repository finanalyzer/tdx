# TdxQuant Equity Search Integration Spec

## Overview

This document outlines the specifications for developing an equity search integration module for TdxQuant, following the structure and implementation patterns demonstrated in the reference file `equity_search.py` and adhering to TdxQuant's API specifications.

## Implementation Structure

### 1. File Structure

```
openbb_tdx/
├── models/
│   └── equity_search.py  # Main implementation file
└── provider.py           # Provider configuration file
```

### 2. Module Components

#### 2.1 equity_search.py

The module will consist of the following components:

- **TdxQuantEquitySearchQueryParams** - Extends `EquitySearchQueryParams` with TdxQuant-specific parameters
- **TdxQuantEquitySearchData** - Extends `EquitySearchData` for TdxQuant-specific data fields
- **TdxQuantEquitySearchFetcher** - Implements the fetcher for equity search functionality

#### 2.2 provider.py

The provider.py file will be updated to include the new fetcher in the provider's `fetcher_dict`.

## Technical Implementation

### 1. Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| query | Optional[str] | None | Search query for equity symbol or name |
| limit | Optional[int] | 10000 | Maximum number of results to return |
| market | Optional[str] | "5" | Market type (default: all A-shares) |
| list_type | int | 1 | Return format (0: only codes, 1: codes and names) |

### 2. Data Model

The data model will include the following fields:

| Field | Type | Description |
|-------|------|-------------|
| symbol | str | Equity symbol with market suffix (e.g., 000001.SZ) |
| name | str | Equity name |
| exchange | Optional[str] | Exchange code |

### 3. Fetcher Implementation

#### 3.1 transform_query

Converts input parameters into `TdxQuantEquitySearchQueryParams` object.

#### 3.2 aextract_data

- Initializes the TdxQuant client using `tq.initialize()`
- Calls `tq.get_stock_list()` with the specified market and list_type
- Handles different return formats based on list_type
- Converts the result to a standardized format

#### 3.3 transform_data

- Filters results based on the search query (if provided)
- Removes exchange suffixes for accurate searching
- Maps TdxQuant's response format to the standard `EquitySearchData` format

## API Usage

### TdxQuant API Reference

The implementation will use the `get_stock_list` function from TdxQuant's API:

```python
def get_stock_list(market=None, list_type: int = 0) -> List:
    """Get stock list for specified market"""
```

**Market Codes:**
- "5": All A-shares (default)
- "102": Hong Kong stocks
- "103": US stocks
- Other market codes as defined in the TdxQuant documentation

**List Types:**
- 0: Return only codes
- 1: Return codes and names

## Integration Steps

1. Create the `equity_search.py` file in the `openbb_tdx/models/` directory
2. Implement the required classes and methods
3. Update `provider.py` to include the new fetcher
4. Add necessary imports and dependencies
5. Implement error handling and data validation
6. Add documentation and test cases

## Error Handling

The implementation will include error handling for:

- TdxQuant client initialization failures
- API request errors
- Data format inconsistencies
- Timeout errors

## Testing

### Test Framework

Tests will be implemented using pytest, with mock objects for TdxQuant API calls to ensure reliable testing without actual API dependencies.

### Test Cases

#### 1. Basic Search
- **Description**: Test searching for equities with a simple query
- **Input**: `query="bank"`
- **Expected Output**: List of equities with "bank" in name or symbol
- **Verification**: Check that results contain expected equities

#### 2. Empty Search
- **Description**: Test with no search query
- **Input**: `query=None`
- **Expected Output**: All equities for the specified market
- **Verification**: Check that results match expected count for the market

#### 3. Market Filtering
- **Description**: Test with different market codes
- **Inputs**: 
  - `market="5"` (A-shares)
  - `market="102"` (Hong Kong)
  - `market="103"` (US)
- **Expected Output**: Equities from the specified market
- **Verification**: Check that results match the expected market format

#### 4. Limit Parameter
- **Description**: Test with different limit values
- **Inputs**: 
  - `limit=10`
  - `limit=100`
  - `limit=1000`
- **Expected Output**: Number of results <= specified limit
- **Verification**: Check that result count matches or is less than limit

#### 5. Error Handling
- **Description**: Test with invalid inputs
- **Inputs**: 
  - `market="invalid"`
  - `list_type=999`
- **Expected Output**: Proper error handling
- **Verification**: Check that appropriate exceptions are raised

#### 6. Symbol Formatting
- **Description**: Test with different symbol formats
- **Inputs**: 
  - `query="000001"` (without suffix)
  - `query="000001.SZ"` (with suffix)
- **Expected Output**: Same results for both formats
- **Verification**: Check that both queries return the same equity

### Test Implementation

```python
# tests/test_equity_search.py

import pytest
from unittest.mock import Mock, patch
from openbb_tdx.models.equity_search import TdxQuantEquitySearchFetcher


@pytest.fixture
def mock_tq():
    """Mock tq module for testing"""
    with patch('openbb_tdx.models.equity_search.tq') as mock:
        mock.initialize.return_value = None
        yield mock


def test_basic_search(mock_tq):
    """Test basic search functionality"""
    # Mock response
    mock_tq.get_stock_list.return_value = [
        {'Code': '000001.SZ', 'Name': '平安银行'},
        {'Code': '600036.SH', 'Name': '招商银行'},
        {'Code': '601398.SH', 'Name': '工商银行'},
    ]
    
    # Test search
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': '银行', 'market': '5', 'list_type': 1}
    query = fetcher.transform_query(params)
    data = fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 3
    assert results[0].symbol == '000001.SZ'
    assert results[0].name == '平安银行'


def test_empty_search(mock_tq):
    """Test empty search functionality"""
    # Mock response
    mock_tq.get_stock_list.return_value = [
        {'Code': '000001.SZ', 'Name': '平安银行'},
        {'Code': '000002.SZ', 'Name': '万科A'},
    ]
    
    # Test search
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 1}
    query = fetcher.transform_query(params)
    data = fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 2


def test_limit_parameter(mock_tq):
    """Test limit parameter functionality"""
    # Mock response
    mock_tq.get_stock_list.return_value = [
        {'Code': '000001.SZ', 'Name': '平安银行'},
        {'Code': '000002.SZ', 'Name': '万科A'},
        {'Code': '000004.SZ', 'Name': '*ST国华'},
    ]
    
    # Test with limit=2
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 1, 'limit': 2}
    query = fetcher.transform_query(params)
    data = fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 2


def test_market_filtering(mock_tq):
    """Test market filtering functionality"""
    # Mock response for A-shares
    mock_tq.get_stock_list.side_effect = lambda market, list_type: [
        {'Code': '000001.SZ', 'Name': '平安银行'}
    ] if market == '5' else [
        {'Code': '00001.HK', 'Name': '长和'}
    ]
    
    # Test A-shares
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 1}
    query = fetcher.transform_query(params)
    data = fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 1
    assert results[0].symbol == '000001.SZ'

    # Test Hong Kong
    params = {'query': None, 'market': '102', 'list_type': 1}
    query = fetcher.transform_query(params)
    data = fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 1
    assert results[0].symbol == '00001.HK'


def test_error_handling(mock_tq):
    """Test error handling functionality"""
    # Mock exception
    mock_tq.get_stock_list.side_effect = Exception("API Error")
    
    # Test error handling
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 1}
    query = fetcher.transform_query(params)
    
    with pytest.raises(Exception, match="API Error"):
        fetcher.aextract_data(query, None)
```

### Verification Procedures

1. **Data Accuracy Verification**:
   - Compare TdxQuant API results with expected values
   - Verify symbol formats and naming conventions
   - Check that search results match query criteria

2. **Performance Verification**:
   - Measure response times for different query sizes
   - Test with large result sets to ensure efficient processing
   - Verify memory usage for large queries

3. **Integration Verification**:
   - Test integration with OpenBB platform
   - Verify proper error propagation
   - Test with different OpenBB client configurations

4. **Edge Case Verification**:
   - Test with empty result sets
   - Test with invalid market codes
   - Test with very long search queries
   - Test with special characters in search queries

## Documentation

The module will include:

- Docstrings for all classes and methods
- README.md file with usage examples
- Integration instructions for the OpenBB platform

## Performance Considerations

- Caching mechanisms to reduce API calls
- Efficient data processing for large result sets
- Proper error handling to ensure system stability

## Security Considerations

- Secure handling of TdxQuant client initialization
- Proper validation of input parameters
- Protection against API abuse

## Dependencies

- openbb-core
- tqcenter (TdxQuant client library)
- pandas
- pydantic

## Example Usage

```python
from openbb import obb

# Search for equities containing "bank"
results = obb.equity.search(query="bank", provider="tdxquant")

# Search with market filter
results = obb.equity.search(query="bank", market="5", provider="tdxquant")

# Get all A-shares
results = obb.equity.search(limit=100, provider="tdxquant")
```

## Expected Output Format

```python
[
    {"symbol": "000001.SZ", "name": "平安银行", "exchange": "SZ"},
    {"symbol": "600036.SH", "name": "招商银行", "exchange": "SH"},
    ...
]
```

## Conclusion

This spec outlines the implementation requirements for the TdxQuant equity search integration module. By following these specifications, the module will provide a seamless integration with the OpenBB platform, allowing users to search for equities using TdxQuant's API with proper error handling, data validation, and comprehensive testing.