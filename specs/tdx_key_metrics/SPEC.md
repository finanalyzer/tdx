# TdxQuant Key Metrics Module Specification

## 1. Project Overview

### Project Name
`openbb_tdx` - TdxQuant Data Provider for OpenBB

### Module Name
`equity_key_metrics` - Equity Key Metrics Fetcher

### Core Functionality
The module provides equity fundamental key metrics data for Chinese A-share and Hong Kong stocks by integrating with TdxQuant (通达信量化平台). It fetches financial metrics including valuation ratios, profitability indicators, leverage metrics, and dividend information.

### Target Users
- Quantitative analysts and researchers
- Investment professionals analyzing Chinese markets
- Algo-trading system developers
- Financial data scientists

### Target Systems
- OpenBB Platform (https://openbb.co)
- TongDaXin client (通达信客户端)

---

## 2. Functionality Specification

### 2.1 Core Features

#### 2.1.1 Key Metrics Data Model
The module implements the OpenBB standard `KeyMetricsData` model with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | str | Stock symbol (e.g., "688318.SH") |
| `period_ending` | date | End date of reporting period |
| `fiscal_year` | int | Fiscal year |
| `fiscal_period` | str | Fiscal period (Q1, Q2, Q3, Q4) |
| `currency` | str | Currency (default: "CNY") |
| `market_cap` | float | Market capitalization |
| `pe_ratio` | float | Price-to-earnings ratio (TTM) |
| `forward_pe` | float | Forward P/E ratio |
| `eps` | float | Earnings per share |
| `price_to_book` | float | Price-to-book ratio |
| `book_value_per_share` | float | Book value per share |
| `debt_to_equity` | float | Debt-to-equity ratio |
| `current_ratio` | float | Current ratio |
| `quick_ratio` | float | Quick ratio |
| `gross_margin` | float | Gross margin |
| `profit_margin` | float | Profit margin |
| `operating_margin` | float | Operating margin |
| `return_on_assets` | float | Return on assets |
| `return_on_equity` | float | Return on equity |
| `dividend_yield` | float | Dividend yield |
| `enterprise_value` | float | Enterprise value |
| `ev_to_sales` | float | EV-to-sales ratio |
| `beta` | float | Beta coefficient |
| `year_high` | float | 52-week high |
| `year_low` | float | 52-week low |
| `working_capital` | float | Working capital |
| `total_debt` | float | Total debt |
| `operating_cash_flow` | float | Operating cash flow |
| `ebit_margin` | float | EBIT margin |
| `price_to_sales` | float | Price-to-sales ratio |
| `price_to_cash` | float | Price-to-cash ratio |
| `cash_per_share` | float | Cash per share |

#### 2.1.2 Query Parameters
- `symbol` (str): Stock symbol(s), supports multiple items separated by commas
- `period` (Literal["annual", "quarter"]): Reporting period, default "quarter"
- `use_cache` (bool): Whether to use cached data, default True

#### 2.1.3 Data Source
The module uses `openbb_tdx.utils.tdx_key_metrics.map_tdx_to_openbb()` which internally:
1. Initializes TdxQuant connection via `tq.initialize()`
2. Calls `tq.get_stock_info()` for basic stock information
3. Calls `tq.get_more_info()` for additional financial metrics
4. Calculates derived metrics (ratios, margins, etc.)
5. Maps TdxQuant field names to OpenBB standard field names
6. Closes connection via `tq.close()`

### 2.2 User Interactions and Flows

#### 2.2.1 Single Symbol Query
```python
from openbb import obb

result = obb.equity.fundamental.metrics(
    symbol="600519.SH",
    period="quarter",
    provider="tdxquant"
)
```

#### 2.2.2 Multiple Symbols Query
```python
result = obb.equity.fundamental.metrics(
    symbol="600519.SH,688318.SH",
    period="annual",
    provider="tdxquant"
)
```

#### 2.2.3 Direct Fetcher Usage
```python
from openbb_tdx.models.equity_key_metrics import (
    TdxQuantKeyMetricsQueryParams,
    TdxQuantKeyMetricsData,
    TdxQuantKeyMetricsFetcher
)

params = TdxQuantKeyMetricsQueryParams(symbol="600519.SH")
fetcher = TdxQuantKeyMetricsFetcher()
data = await fetcher.fetch_data(params.model_dump(), {})
```

### 2.3 Data Handling

#### 2.3.1 Data Transformation Pipeline
1. **Extract**: Call TdxQuant API via `map_tdx_to_openbb()`
2. **Validate**: Validate data against Pydantic model
3. **Transform**: Apply alias mappings and field validators
4. **Return**: List of `TdxQuantKeyMetricsData` objects

#### 2.3.2 Error Handling
- `EmptyDataError`: When no data returned for given symbols
- `OpenBBError`: For connection failures or API errors
- Warning messages for partial failures (some symbols succeeded)

### 2.4 Edge Cases
- Invalid symbol format → Return error with helpful message
- TdxQuant client not running → Clear error message with instructions
- Partial data availability → Return available data with warnings
- Empty data for a symbol → Skip that symbol, process others

---

## 3. Technical Specification

### 3.1 Module Structure
```
openbb_tdx/
├── models/
│   ├── equity_key_metrics.py    # Key metrics model implementation
│   └── __init__.py
├── utils/
│   └── tdx_key_metrics.py       # Already exists, provides map_tdx_to_openbb()
├── provider.py                   # Add KeyMetricsFetcher to fetcher_dict
└── tests/
    └── test_equity_key_metrics.py # Unit tests
```

### 3.2 Dependencies
- `openbb-core`: Core OpenBB functionality
- `pydantic`: Data validation
- `tqcenter`: TdxQuant API wrapper
- `mysharelib`: Internal utilities (normalize_symbol, setup_logger)

### 3.3 Key Classes

#### 3.3.1 TdxQuantKeyMetricsQueryParams
- Inherits from `KeyMetricsQueryParams`
- Adds `use_cache` field
- Sets `multiple_items_allowed=True` for symbol

#### 3.3.2 TdxQuantKeyMetricsData
- Inherits from `KeyMetricsData`
- Defines field aliases for TdxQuant data mapping
- Includes field validators for type conversion

#### 3.3.3 TdxQuantKeyMetricsFetcher
- Inherits from `Fetcher[TdxQuantKeyMetricsQueryParams, List[TdxQuantKeyMetricsData]]`
- Implements async data extraction with `aextract_data`
- Uses `asyncio.gather()` for concurrent symbol processing

---

## 4. Implementation Notes

### 4.1 Data Flow
```
Query Params → transform_query() → aextract_data()
    → map_tdx_to_openbb() → TdxQuant API
    → transform_data() → TdxQuantKeyMetricsData[]
```

### 4.2 Alias Mapping
The `__alias_dict__` in `TdxQuantKeyMetricsData` maps TdxQuant field names to OpenBB field names:
```python
__alias_dict__ = {
    "symbol": "证券代码",
    "fiscal_period": "报告类型",
    "period_ending": "报告日期",
    "market_cap": "流通值",
    "pe_ratio": "市盈率(动)",
    # ... etc
}
```

### 4.3 Period Processing
- **quarter**: Default, returns most recent quarterly data
- **annual**: Returns most recent annual data

The `map_tdx_to_openbb()` function extracts `period_ending` from `ReportDate` field and determines `fiscal_year` and `fiscal_period` from the date.

---

## 5. Acceptance Criteria

### 5.1 Functional Criteria
- [ ] Module successfully fetches key metrics for single symbol
- [ ] Module successfully fetches key metrics for multiple symbols
- [ ] Data correctly maps to OpenBB standard format
- [ ] Query parameters are properly validated
- [ ] Error handling works for invalid symbols
- [ ] Error handling works when TdxQuant client is unavailable

### 5.2 Technical Criteria
- [ ] Inherits from correct OpenBB standard models
- [ ] Uses async/await pattern correctly
- [ ] Implements proper logging
- [ ] Handles connection lifecycle (initialize/close)
- [ ] Unit tests pass with mocking
- [ ] Integration tests pass with real TdxQuant client

### 5.3 Code Quality Criteria
- [ ] Follows existing code style and conventions
- [ ] Includes docstrings for all public methods
- [ ] No pylint warnings (except allowed ones)
- [ ] Type hints for all parameters and return values

---

## 6. References

- OpenBB Key Metrics Documentation: https://docs.openbb.co/odp/python/reference/equity/fundamental/metrics
- AKShare Reference Implementation: `openbb_akshare/openbb_akshare/models/key_metrics.py`
- TdxQuant Key Metrics Utils: `openbb_tdx/utils/tdx_key_metrics.py`
- Existing TdxQuant Models: `openbb_tdx/models/equity_*.py`
