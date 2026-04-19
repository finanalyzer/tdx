# TdxQuant Equity Dividends Data Provider Specification

## 1. Project Overview

**Project Name:** openbb_tdx - Equity Dividends Module

**Core Functionality:** This module implements the historical dividends data fetcher for the TdxQuant (通达信量化平台) data provider, enabling retrieval of dividend history for Chinese A-shares and Hong Kong stocks through the OpenBB platform.

**Target Users:** Quantitative traders, investors, and analysts working with Chinese equity markets who need dividend history data for fundamental analysis, strategy development, and backtesting.

**Target Systems:** OpenBB Platform with TdxQuant data provider extension

## 2. Functionality Specification

### 2.1 Core Features

#### Data Retrieval
- Fetch historical dividend data for Chinese A-shares (上海/上海 and 深圳/深圳 exchanges)
- Fetch historical dividend data for Hong Kong stocks
- Support for multiple stock symbols in a single query
- Date range filtering for dividend records

#### TdxQuant API Integration
- Utilize `tq.get_divid_factors()` function to retrieve dividend data
- Support stock code format: `XXXXXX.SH`, `XXXXXX.SZ` for A-shares; `XXXXX.HK` for Hong Kong
- Handle both A-share and HK stock market dividend data

#### Data Fields
The module will return the following dividend-related fields:
| Field | Type | Description |
|-------|------|-------------|
| symbol | str | Stock symbol code |
| name | str | Company name (if available) |
| ex_dividend_date | date | Ex-dividend date |
| declaration_date | date | Dividend announcement date |
| record_date | date | Record date for shareholders |
| payable_date | date | Payment date |
| dividend_type | str | Type of dividend (cash, stock, etc.) |
| dividend_ratio | float | Dividend ratio per share |
| dividend_yield | float | Dividend yield percentage |
| bonus_share_ratio | float | Bonus share ratio |
| rights_issue_ratio | float | Rights issue ratio |
| tracking_number | str | Dividend tracking number |

### 2.2 User Interactions and Flows

#### Primary Flow
1. User requests dividend history via OpenBB SDK or API
2. System validates symbol format and accessibility
3. TdxQuant API is called to fetch dividend data
4. Data is transformed to OpenBB standard format
5. Results are returned to user

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| symbol | str | Yes | - | Stock symbol (e.g., "600000.SH", "000001.SZ", "00700.HK") |
| start_date | date | No | None | Start date for dividend records |
| end_date | date | No | None | End date for dividend records |

### 2.3 Data Handling

#### Symbol Normalization
- Use `normalize_symbol()` from `mysharelib.tools` for consistent symbol handling
- Extract base symbol, formatted symbol, and market identifier

#### Error Handling
- Handle empty data responses gracefully
- Validate API connection status
- Provide meaningful error messages for invalid symbols
- Support reconnection attempts for transient failures

### 2.4 Edge Cases

1. **Invalid Symbol:** Return empty result with warning log
2. **No Dividend Data:** Return empty list (not an error)
3. **API Connection Failure:** Raise appropriate exception
4. **Partial Data:** Return available data with warning
5. **HK Stock with no name:** Use symbol as fallback name

## 3. Technical Specification

### 3.1 Module Structure

```
openbb_tdx/
├── models/
│   ├── __init__.py
│   ├── equity_historical.py    (existing)
│   ├── equity_quote.py         (existing)
│   └── equity_dividends.py    (NEW - to be created)
├── utils/
│   ├── __init__.py
│   ├── helpers.py              (existing)
│   └── constants.py            (existing)
├── provider.py                  (to be updated)
└── router.py                   (to be updated if needed)
```

### 3.2 Class Definitions

#### Query Params Class
```python
class TdxQuantEquityDividendsQueryParams(EquityDividendsQueryParams):
    """Query parameters for TdxQuant Equity Dividends."""
    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}
```

#### Data Model Class
```python
class TdxQuantEquityDividendsData(EquityDividendsData):
    """TdxQuant Equity Dividends Data Model."""
    # Inherits base fields from EquityDividendsData
    # Additional fields as needed
```

#### Fetcher Class
```python
class TdxQuantEquityDividendsFetcher(
    Fetcher[TdxQuantEquityDividendsQueryParams, List[TdxQuantEquityDividendsData]]
):
    """Fetches historical dividend data from TdxQuant."""
```

### 3.3 Dependencies

- `openbb-core`: Core OpenBB functionality
- `tqcenter`: TdxQuant API wrapper (`tq`)
- `mysharelib.tools`: Symbol normalization utilities
- `pandas`: Data handling
- `pydantic`: Data validation

## 4. Acceptance Criteria

### 4.1 Functional Requirements
- [ ] Module correctly fetches dividend data for A-share stocks (e.g., "600000.SH")
- [ ] Module correctly fetches dividend data for HK stocks (e.g., "00700.HK")
- [ ] Symbol normalization works correctly for both markets
- [ ] Date filtering works when start_date and end_date are provided
- [ ] Empty data returns empty list without error
- [ ] Invalid symbol returns warning and empty result

### 4.2 Technical Requirements
- [ ] Follows OpenBB provider patterns and conventions
- [ ] Inherits from standard OpenBB models
- [ ] Implements all required Fetcher methods
- [ ] Proper error handling and logging
- [ ] Type hints for all parameters and return values
- [ ] Unit tests with >80% coverage of new code

### 4.3 Integration Requirements
- [ ] Fetcher added to provider.py fetcher_dict
- [ ] Models exported from models/__init__.py
- [ ] Compatible with existing OpenBB SDK usage patterns
- [ ] Documentation comments on all public classes and methods

## 5. Testing Strategy

### 5.1 Unit Tests
- Test transform_query with valid/invalid parameters
- Test extract_data with mocked TdxQuant API
- Test transform_data with sample dividend data
- Test edge cases (empty data, invalid symbol)

### 5.2 Integration Tests
- Test with live TdxQuant API (requires running TongDaXin client)
- Validate data accuracy against known dividend records
- Test multi-symbol queries

### 5.3 Test Data
- A-share example: "600000.SH" (上海浦东发展银行)
- HK stock example: "00700.HK" (腾讯控股)
