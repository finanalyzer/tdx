---
name: openbb-data-provider
description: Comprehensive guidance for developing OpenBB data providers using Python and FastAPI. This skill helps developers create, implement, test, and troubleshoot OpenBB data provider extensions following official documentation guidelines. Use this skill when developing custom data providers for the OpenBB platform, implementing data provider classes and methods, working with FastAPI endpoints, handling data validation, or following OpenBB's coding standards and patterns. Special focus on TdxQuant (TongDaXin) data provider integration for China A-share and Hong Kong markets.
---

# OpenBB Data Provider Development

## Overview

This skill provides comprehensive guidance for creating, implementing, and troubleshooting OpenBB data providers. It covers the architecture, structure, and best practices for developing Python-based data providers that integrate seamlessly with the OpenBB ecosystem, leveraging FastAPI for endpoints and following OpenBB's standardization framework.

## Quick Start Checklist

Before implementing a new data provider, ensure you have:

- [ ] Reviewed existing providers for similar functionality
- [ ] Understood the data source API documentation
- [ ] Identified the appropriate caching strategy (BlobCache vs TableCache)
- [ ] Planned the data model fields and transformations
- [ ] Prepared mock data for unit testing
- [ ] Set up the development environment with `pip install -e .`

## Architecture Overview

OpenBB data providers follow a standardized architecture that ensures consistency across the platform:

- **Core Components**: Built on `openbb-core` as the foundation
- **Provider Extensions**: Independent data sources that implement a standardized pipeline
- **Standard Models**: Shared data structures that ensure consistency across providers
- **Fetcher Classes**: Handle data extraction and transformation from external APIs
- **Routers**: Manage input/output operations and endpoint routing

### Data Flow

```
User Request → Router → Fetcher.transform_query() → Fetcher.extract_data() → Fetcher.transform_data() → Response
```

## Development Workflow

### 1. Setting Up Your Environment

1. Install the OpenBB platform in editable mode:
   ```bash
   pip install -e .
   ```

2. Clone the GitHub repository and create a new branch for your provider:
   ```bash
   git clone https://github.com/OpenBB-finance/OpenBB.git
   cd OpenBB
   git checkout -b feature/my-new-provider
   ```

### 2. Creating a New Provider Extension

1. **Folder Structure**: Organize your provider with the following structure:
   ```
   my_provider/
   |-- __init__.py
   |-- provider.py          # Provider registration
   |-- router.py            # FastAPI route definitions
   |-- models/
   |   |-- __init__.py
   |   `-- historical.py    # Data models and fetchers
   |-- utils/
   |   |-- __init__.py
   |   `-- helpers.py       # Data fetching helpers
   |-- pyproject.toml
   `-- README.md
   ```

2. **TOML Configuration**: Define your provider as a Poetry plugin in `pyproject.toml`:
   ```toml
   [tool.poetry.plugins."openbb-extension"]
   "my_provider" = "openbb_my_provider.provider:provider"
   ```

3. **Provider Definition**: Initialize a `Provider` class in `provider.py`:
   ```python
   from openbb_core.provider.abstract.provider import Provider
   from openbb_my_provider.models.historical import MyProviderHistoricalFetcher

   provider = Provider(
       name="my_provider",
       description="Data provider for MyProvider.",
       website="https://myprovider.com",
       fetcher_dict={
           "Historical": MyProviderHistoricalFetcher,
       }
   )
   ```

### 3. Implementing Fetcher Classes

1. **Standard Models**: Create models that inherit from OpenBB's standard models:
   ```python
   from pydantic import Field
   from openbb_core.provider.abstract.data import Data
   from openbb_core.provider.abstract.query import QueryParams
   
   class MyProviderQueryParams(QueryParams):
       symbol: str = Field(description="Stock symbol")
   
   class MyProviderData(Data):
       date: str = Field(description="Date of data")
       close: float = Field(description="Closing price")
   ```

2. **Fetcher Implementation**: Create a Fetcher class to handle data extraction:
   ```python
   from openbb_core.provider.abstract.fetcher import Fetcher
   from openbb_core.provider.utils.helpers import amake_requests
   from typing import Dict, List, Optional, Any
   
   class MyProviderFetcher(Fetcher[MyProviderQueryParams, List[MyProviderData]]):
       """Transform the query, extract and transform the data from the endpoints."""

       @staticmethod
       def transform_query(params: Dict[str, Any]) -> MyProviderQueryParams:
           """Transform the query params."""
           return MyProviderQueryParams(**params)
       
       @staticmethod
       def extract_data(
           query: MyProviderQueryParams,
           credentials: Optional[Dict[str, str]],
           **kwargs: Any,
       ) -> List[Dict]:
           """Return the raw data from the endpoint."""
           # Your data extraction logic here
           return []
       
       @staticmethod
       def transform_data(
           query: MyProviderQueryParams,
           data: List[Dict],
           **kwargs: Any,
       ) -> List[MyProviderData]:
           """Return the transformed data."""
           return [MyProviderData.model_validate(d) for d in data]
   ```

### 4. Registering Your Fetcher

Add your fetcher to the provider's `fetcher_dict` in `provider.py`:
```python
from .models.historical import MyProviderHistoricalFetcher

provider = Provider(
    name="my_provider",
    fetcher_dict={
        "Historical": MyProviderHistoricalFetcher,
    },
)
```

### 5. Adding Router Endpoints

Create router endpoints in `router.py`:
```python
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import ProviderChoices
from openbb_core.app.command_context import CommandContext
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query import QueryParams, ExtraParams, StandardParams

router = Router()

@router.command(model="MyProviderHistorical")
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[Data]:
    """Get historical price data."""
    return await OBBject.from_query(Query(**locals()))
```

---

# Caching Strategies

## Choosing the Right Cache

OpenBB providers support two caching mechanisms:

| Feature | BlobCache | TableCache |
|---------|-----------|------------|
| **Use Case** | Financial statements, key metrics | Time series data (OHLCV) |
| **Storage** | Pickled DataFrame blobs | SQLite table with schema |
| **Query Flexibility** | Symbol + period based | Date range queries |
| **Schema Required** | No | Yes |
| **Best For** | Structured financial reports | Historical price data |

### When to Use BlobCache

Use `BlobCache` for:
- Financial statements (balance sheet, income statement, cash flow)
- Key metrics and ratios
- Company profile data
- Any data where the entire dataset is fetched at once

**BlobCache Pattern:**
```python
from mysharelib.blob_cache import BlobCache
from openbb_my_provider import project_name

def get_financial_data(
    symbol: str,
    period: str = "annual",
    use_cache: bool = True,
    limit: int = 5,
) -> DataFrame:
    """Get financial data with BlobCache."""
    cache = BlobCache(table_name="financial_data", project=project_name)
    logger.info(f"Fetching data for {symbol} with limit {limit}")
    return cache.load_cached_data(symbol, period, use_cache, _fetch_data, limit)

def _fetch_data(symbol: str, period: str = "annual", limit: int = 5) -> DataFrame:
    """Callback function to fetch data when cache miss."""
    # Your API call here
    return df
```

### When to Use TableCache

Use `TableCache` for:
- Historical price data (OHLCV)
- Time series with date-based queries
- Data requiring schema validation

**TableCache Pattern:**
```python
from mysharelib.table_cache import TableCache
from openbb_my_provider import project_name

SCHEMA = {
    "date": "TEXT PRIMARY KEY",
    "open": "REAL",
    "high": "REAL",
    "low": "REAL",
    "close": "REAL",
    "volume": "REAL",
}

def get_historical_data(symbol: str, use_cache: bool = True) -> DataFrame:
    """Get historical data with TableCache."""
    cache = TableCache(SCHEMA, project=project_name, table_name=f"hist_{symbol}", primary_key="date")
    cached_data = cache.fetch_date_range(start_date, end_date)
    if not cached_data.empty:
        return cached_data
    # Fetch from API and cache
    df = fetch_from_api(symbol)
    cache.write_dataframe(df)
    return df
```

### BlobCache with Additional Parameters

When using BlobCache with additional parameters (like `statement_type`), use closures:

```python
def get_financial_statement_data(
    symbol: str,
    statement_type: str,  # Additional parameter
    period: str = "annual",
    use_cache: bool = True,
    limit: int = 5,
) -> DataFrame:
    """Get financial statement data with BlobCache."""
    cache = BlobCache(table_name=statement_type, project=project_name)
    
    # Create a closure that captures statement_type
    fetch_func = _get_fetch_func(statement_type)
    return cache.load_cached_data(symbol, period, use_cache, fetch_func, limit)

def _get_fetch_func(statement_type: str):
    """Get the appropriate fetch function for the statement type."""
    def fetch_func(symbol: str, period: str = "annual", limit: int = 5) -> DataFrame:
        return _fetch_financial_statement_data(symbol, statement_type, period, limit)
    return fetch_func

def _fetch_financial_statement_data(
    symbol: str,
    statement_type: str,
    period: str = "annual",
    limit: int = 5,
) -> DataFrame:
    """Fetch financial statement data from API."""
    # Your implementation here
    pass
```

---

# Stock Price Adjustment (Dividend/Split Handling)

## 1. Stock Price Adjustment Overview

### 1.1 Why Adjust Stock Prices?

Stocks experience events such as rights issues, splits, consolidations, and dividend distributions that create significant gaps in price data. Using unadjusted prices for data processing and indicator calculations results in discontinuities and incorrect return calculations. To ensure data continuity, price series are typically adjusted using forward adjustment (前复权) or backward adjustment (后复权).

### 1.2 Forward Adjustment (前复权)

Keeps current prices unchanged while adjusting historical prices up or down to maintain continuity. Forward adjustment is very convenient for chart analysis, allowing clear visualization of historical price trends and smooth overlay of technical indicators. It is the default adjustment method in most market data software.

**Important Notes:**

- Historical prices are time-varying and must be readjusted each time a stock goes ex-dividend or ex-rights, potentially resulting in different historical forward-adjusted prices seen at different times.
- For companies with consistent dividend payouts, forward-adjusted prices may become negative.

### 1.3 Backward Adjustment (后复权)

Keeps historical prices unchanged while adjusting current stock prices after each equity event. Backward-adjusted prices may differ significantly from actual stock prices and are not suitable for chart analysis.

**Advantages:**

- Can be viewed as a long-term wealth growth curve for investors
- Reflects investors' true return situations
- Commonly used in quantitative investment research

---

## 2. OpenBB Adjustment Implementation

OpenBB supports retrieving adjusted data through the `adjustment` parameter in the `obb.equity.price.historical` command.

### 2.1 Supported Adjustment Types

| Adjustment Type        | Description                                                |
| ---------------------- | ---------------------------------------------------------- |
| `splits_only`          | Default - adjusts only for stock splits, not for dividends |
| `splits_and_dividends` | Adjusts for both splits and dividends                      |
| `unadjusted`           | Completely unadjusted raw data                             |

### 2.2 Usage Examples

```python
from openbb import obb

# Default method (不复权)
data = obb.equity.price.historical("600325", provider="akshare")

# 前复权
data = obb.equity.price.historical("600325", adjustment="qfq", provider="akshare")

# 后复权
data = obb.equity.price.historical("600325", adjustment="hfq", provider="akshare")

# Unadjusted raw data
data = obb.equity.price.historical("600325", adjustment="", provider="akshare")
```

### 2.3 Important Notes

- The `adjustment` parameter currently primarily supports `polygon` and `yfinance` providers
- `splits_only`, `splits_and_dividends` and `unadjusted` modes are supported by `polygon` and `yfinance` providers
- `openbb_akshare`, `openbb_tushare` and `openbb_tdx` uses `qfq` (前复权) and `hfq` (后复权) respectively

---

## 3. Chinese vs OpenBB Adjustment Concepts

OpenBB's adjustment concepts are not exactly the same as Chinese forward/backward adjustments. The implementation logic and applicable scenarios differ between the two approaches.

### 3.1 Chinese Adjustment Concepts

**Forward Adjustment (前复权)**

- Adjusts all historical prices upon each dividend or stock distribution
- Latest price remains unchanged, historical prices are adjusted downward
- Disadvantage: All historical prices change with each new dividend, requiring recalculation of indicators like moving averages

**Backward Adjustment (后复权)**

- Adjusts current and future prices upon each dividend or stock distribution
- Historical prices remain unchanged, latest price is adjusted upward
- Advantage: Historical prices are stable, suitable for backtesting

### 3.2 OpenBB's Adjustment Methods

Based on GitHub issue [#6917](https://github.com/OpenBB-finance/OpenBB/issues/6917) discussion:

**`splits_only` (Default)**

- Similar to backward adjustment: adjusts only for splits, not for dividends
- Historical prices remain stable
- Suitable for backtesting scenarios

**`splits_and_dividends`**

- Adjusts for both splits and dividends
- OpenBB team notes that prices adjusted this way "never actually happened" and may not be suitable for precise price analysis
- Often used to calculate total returns, but not the correct method

**`unadjusted`**

- Completely unadjusted raw data

### 3.3 Key Comparison

| Feature                    | Chinese Backward Adjustment | OpenBB `splits_only`                   |
| -------------------------- | --------------------------- | -------------------------------------- |
| Adjustment Target          | Splits + Dividends          | Splits only                            |
| Historical Price Stability | Stable                      | Stable                                 |
| Suitable Scenarios         | Backtesting                 | Backtesting (without dividend effects) |

### 3.4 Practical Recommendations

If you need **total return data including dividend effects**, OpenBB recommends:

1. Use `splits_only` to get price data
2. Retrieve dividend data separately
3. Build total return metrics yourself

Example:

```python
from openbb import obb

# Get split-adjusted prices (stable historical prices)
price_data = obb.equity.price.historical("AAPL", adjustment="splits_only", provider="yfinance")

# If total returns are needed, you must calculate them yourself
# because dividend handling varies significantly across data sources
```

---

## 4. Chinese Data Provider Adjustment Implementations

Most Chinese data providers support price adjustment. Here are the adjustment parameters for various platforms:

| Data Provider | A-share Interface | Hong Kong Interface | Adjustment Parameters                                     |
| akshare       | stock_zh_a_hist   | stock_hk_hist       | "" (unadjusted), "qfq" (forward), "hfq" (backward)        |
| tushare       | pro_bar           | hk_daily_adj        | None (unadjusted), "qfq" (forward), "hfq" (backward)      |
| tdxquant      | get_market_data   | get_market_data     | "none" (unadjusted), "front" (forward), "back" (backward) |

For detailed documentation including input/output parameters, adjustment options, and usage examples:

- **AKShare**: See [AKShare stock.md](references/akshare/stock.md) for `stock_zh_a_hist` and `stock_hk_hist`
- **Tushare**: See [Tushare equity_cn.md](references/tushare/equity_cn.md) for `pro_bar` (A-share) and [Tushare equity_hk.md](references/tushare/equity_hk.md) for `hk_daily_adj` (Hong Kong stock)
- **TdxQuant**: See [TdxQuant equity.md](references/tdxquant/get_market_data.md) for `get_market_data` (A-share and Hong Kong stock)

---

# TdxQuant Data Provider Implementation Guide

## Overview

TdxQuant (通达信量化平台) is a comprehensive financial data platform from TongDaXin (通达信), providing extensive market data for China A-shares, Hong Kong stocks, US markets, futures, and options. This section provides detailed guidance for implementing a TdxQuant data provider for OpenBB.

## TdxQuant vs AKShare: Comparative Analysis

Understanding the differences between TdxQuant and AKShare is crucial for making informed implementation decisions:

| Feature | TdxQuant | AKShare |
|---------|----------|---------|
| **Data Source** | Official TongDaXin terminal data | Multiple public data sources |
| **Authentication** | Requires running TongDaXin client | API-based (no client required) |
| **Real-time Data** | Yes, via client subscription | Limited real-time capabilities |
| **Coverage** | China A-share, HK, US, futures, options | Broad but less deep China coverage |
| **Installation** | Requires proprietary DLL | Pure Python package |
| **Latency** | Lower (local client) | Higher (HTTP requests) |
| **Professional Data** | Supported (requires download) | Limited professional data |

### When to Use TdxQuant

- **Choose TdxQuant** when you need:
  - Real-time market data streaming
  - Professional-grade financial data
  - Lower latency data access
  - Comprehensive China market coverage
  - Integration with existing TongDaXin workflows

- **Choose AKShare** when you need:
  - Easy deployment (no client installation)
  - Open-source transparency
  - Broader international coverage
  - Quick prototyping

## Integration Requirements

### Prerequisites

1. **TongDaXin Client**: Must have TongDaXin (通达信) client installed and logged in
2. **Python Dependencies**:
   ```bash
   pip install numpy pandas
   ```
3. **TPythClient.dll**: Provided with the TdxQuant package

### Environment Setup

The TdxQuant provider requires the TongDaXin client to be running. The `tqcenter.py` module handles DLL loading and client communication:

```python
from tqcenter import tq

tq.initialize(__file__)  # Initialize connection to TongDaXin client
```

## TdxQuant API Reference

### Core Data Functions

#### 1. Market Data (K-line)

```python
def get_market_data(
    field_list: List[str] = [],
    stock_list: List[str] = [],
    start_time: str = '',
    end_time: str = '',
    count: int = -1,
    dividend_type: str = 'none',
    period: str = '1d',
    fill_data: bool = False
) -> Dict
```

**Parameters:**
- `field_list`: Fields to return (empty = all fields)
- `stock_list`: Stock codes in format "XXXXXX.SH" or "XXXXXX.SZ"
- `start_time`: Start date (YYYYMMDD or YYYYMMDDHHMMSS)
- `end_time`: End date (YYYYMMDD or YYYYMMDDHHMMSS)
- `count`: Number of records (-1 = all available)
- `dividend_type`: "none", "front" (forward), "back" (backward)
- `period`: "1d", "1w", "1m", "5m", "15m", "30m", "60m"
- `fill_data`: Fill missing data with previous values

**Returns:** Dictionary with stock codes as keys, DataFrames as values

**Code Example:**
```python
df = tq.get_market_data(
    field_list=['Open', 'Close', 'High', 'Low', 'Volume'],
    stock_list=['688318.SH', '600519.SH'],
    start_time='20250101',
    end_time='20250601',
    period='1d',
    dividend_type='front'
)
```

#### 2. Market Snapshot

```python
def get_market_snapshot(
    stock_code: str,
    field_list: List[str] = []
) -> Dict
```

**Code Example:**
```python
snapshot = tq.get_market_snapshot(
    stock_code='688318.SH',
    field_list=['Open', 'High', 'Low', 'Close', 'Volume']
)
```

#### 3. Financial Data by Date

```python
def get_financial_data_by_date(
    stock_list: List[str] = [],
    field_list: List[str] = [],
    year: int = 0,
    mmdd: int = 0
) -> Dict
```

**Parameters:**
- `stock_list`: Stock codes (e.g., `['600519.SH']`)
- `field_list`: Field codes (e.g., `['FN193', 'FN194']`)
- `year`: Year parameter (see below)
- `mmdd`: Month-day parameter (see below)

**Year Parameter Semantics:**
- `year=0, mmdd=0`: Latest available report
- `year=0, mmdd=331/630/930/1231`: Latest report for that quarter
- `year=N (non-zero)`: Specific year (e.g., `year=2023` for 2023 data)

**Month-Day (mmdd) Values:**
- `331`: Q1 (March 31)
- `630`: Q2 (June 30)
- `930`: Q3 (September 30)
- `1231`: Q4 (December 31) - also used for annual reports

**Code Example:**
```python
# Get latest report
fd = tq.get_financial_data_by_date(
    stock_list=['600519.SH'],
    field_list=['FN193', 'FN194'],
    year=0,
    mmdd=0
)

# Get 2023 annual report
fd = tq.get_financial_data_by_date(
    stock_list=['600519.SH'],
    field_list=['FN193', 'FN194'],
    year=2023,
    mmdd=1231
)

# Get 2023 Q1 report
fd = tq.get_financial_data_by_date(
    stock_list=['600519.SH'],
    field_list=['FN193', 'FN194'],
    year=2023,
    mmdd=331
)
```

**Important Notes:**
- The `year` parameter is the **specific year**, not an offset
- To get multiple years of data, iterate through years (e.g., 2023, 2022, 2021)
- Always call `tq.initialize(__file__)` before using TdxQuant functions
- Call `tq.close()` when done to release resources

#### 4. Stock Information

```python
def get_stock_info(
    stock_code: str,
    field_list: List[str] = []
) -> Dict
```

**Code Example:**
```python
info = tq.get_stock_info(
    stock_code='688318.SH',
    field_list=['J_zgb', 'ActiveCapital']  # Total shares, circulating shares
)
```

#### 5. Trading Dates

```python
def get_trading_dates(
    market: str = 'SH',
    start_time: str = '',
    end_time: str = '',
    count: int = -1
) -> List
```

**Parameters:**
- `market`: "SH" (Shanghai), "SZ" (Shenzhen)

#### 6. Stock List

```python
def get_stock_list(list_type: str = '5') -> List[str]
```

**List Types:**
- `'5'`: All A-shares
- `'31'`: ETF funds
- `'51'`: ChiNext (创业板)
- `'53'`: Beijing Stock Exchange (北交所)
- `'23'`: CSI 300
- `'24'`: CSI 500

#### 7. Sector/Block Data

```python
def get_sector_list(list_type: int = 0) -> List
def get_stock_list_in_sector(block_code: str, list_type: int = 0) -> List[str]
```

### Real-time Subscription

#### Subscribe to Quote Updates

```python
def subscribe_quote(
    stock_list: List[str],
    callback: callable
) -> Dict
```

**Code Example:**
```python
def my_callback(data_str):
    print("Received:", data_str)

result = tq.subscribe_quote(
    stock_list=['688318.SH'],
    callback=my_callback
)
```

#### Subscribe to Market Data

```python
def subscribe_hq(
    stock_list: List[str],
    callback: callable
) -> Dict
```

### Data Download Functions

```python
def download_file(
    stock_code: str,
    down_time: str,
    down_type: int
) -> Dict
```

**down_type:**
- `1`: Top 10 shareholders (10 major shareholders)
- `2`: ETF subscription/redemption list
- `3`: Recent news/sentiment
- `4`: Comprehensive information file

### Formula Functions

```python
def formula_zb(formula_name: str, formula_arg: str, xsflag: int = 6) -> Dict
def formula_xg(formula_name: str, formula_arg: str) -> Dict
def formula_process_mul_xg(...) -> Dict
def formula_process_mul_zb(...) -> Dict
```

## Implementing TdxQuant Fetcher for OpenBB

### Provider Structure

```
openbb_tdx/
|-- __init__.py
|-- provider.py
|-- router.py
|-- models/
|   |-- __init__.py
|   |-- equity_historical.py
|   |-- equity_quote.py
|   |-- balance_sheet.py
|   |-- income_statement.py
|   `-- cash_flow.py
|-- utils/
|   |-- __init__.py
|   |-- helpers.py
|   `-- financial_statement_mapping.py
|-- pyproject.toml
`-- README.md
```

### Example: Historical Price Fetcher

```python
from typing import Dict, List, Optional, Any
from datetime import datetime

from pydantic import Field
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query import QueryParams
from openbb_core.provider.abstract.fetcher import Fetcher

from tqcenter import tq


class TdxQuantHistoricalQueryParams(QueryParams):
    symbol: str = Field(description="Stock symbol (e.g., 688318.SH)")
    start_date: Optional[str] = Field(None, description="Start date (YYYYMMDD)")
    end_date: Optional[str] = Field(None, description="End date (YYYYMMDD)")
    period: str = Field("1d", description="K-line period: 1d, 1w, 1m, 5m, 15m, 30m, 60m")
    dividend_type: str = Field("none", description="none, front, back")


class TdxQuantHistoricalData(Data):
    date: str = Field(description="Date of data")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price")
    low: float = Field(description="Lowest price")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Volume in lots")
    amount: float = Field(description="Amount in ten thousand yuan")


class TdxQuantHistoricalFetcher(Fetcher[TdxQuantHistoricalQueryParams, List[TdxQuantHistoricalData]]):

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TdxQuantHistoricalQueryParams:
        return TdxQuantHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TdxQuantHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        try:
            df_dict = tq.get_market_data(
                stock_list=[query.symbol],
                start_time=query.start_date or '',
                end_time=query.end_date or '',
                period=query.period,
                dividend_type=query.dividend_type,
                fill_data=True
            )
            
            if not df_dict or query.symbol not in df_dict:
                return []
            
            df = df_dict[query.symbol]
            return df.to_dict('records')
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data from TdxQuant: {str(e)}")

    @staticmethod
    def transform_data(
        query: TdxQuantHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TdxQuantHistoricalData]:
        return [TdxQuantHistoricalData(**item) for item in data]
```

### Example: Financial Statement Fetcher

```python
from typing import Dict, List, Optional, Any, Literal
from datetime import date, datetime

from pydantic import Field
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query import QueryParams
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.utils.errors import EmptyDataError


class TdxQuantBalanceSheetQueryParams(QueryParams):
    symbol: str = Field(description="Stock symbol (e.g., '600519.SH')")
    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description="Reporting period: 'annual' or 'quarter'"
    )
    limit: int = Field(default=5, description="Number of periods to return")
    use_cache: bool = Field(default=True, description="Whether to use cached data")


class TdxQuantBalanceSheetData(Data):
    period_ending: date = Field(description="The ending date of the fiscal period.")
    fiscal_period: str = Field(description="Fiscal period (Q1, Q2, Q3, Q4).")
    fiscal_year: int = Field(description="Fiscal year.")
    total_assets: Optional[float] = Field(default=None, description="Total assets.")
    total_liabilities: Optional[float] = Field(default=None, description="Total liabilities.")
    total_equity: Optional[float] = Field(default=None, description="Total equity.")


class TdxQuantBalanceSheetFetcher(
    Fetcher[
        TdxQuantBalanceSheetQueryParams,
        List[TdxQuantBalanceSheetData],
    ]
):
    """Transform the query, extract and transform the data from the TdxQuant endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TdxQuantBalanceSheetQueryParams:
        """Transform the query params."""
        return TdxQuantBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TdxQuantBalanceSheetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TdxQuant endpoint."""
        from openbb_tdx.utils.helpers import get_financial_statement_data

        limit = query.limit if query.limit is not None else 5

        data = get_financial_statement_data(
            symbol=query.symbol,
            statement_type="balance_sheet",
            period=query.period,
            use_cache=query.use_cache,
            limit=limit,
        )

        if data.empty:
            raise EmptyDataError()

        return data.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: TdxQuantBalanceSheetQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TdxQuantBalanceSheetData]:
        """Return the transformed data."""
        return [TdxQuantBalanceSheetData.model_validate(d) for d in data]
```

### Financial Statement Helper Function

```python
from typing import Dict, Any, List, Optional
import pandas as pd
from pandas import DataFrame
from mysharelib.blob_cache import BlobCache
from mysharelib.tools import normalize_symbol
from tqcenter import tq
import logging

logger = logging.getLogger(__name__)

VALID_STATEMENT_TYPES = ["balance_sheet", "income_statement", "cash_flow"]


def get_financial_statement_data(
    symbol: str,
    statement_type: str,
    period: str = "annual",
    use_cache: bool = True,
    limit: int = 5,
) -> DataFrame:
    """Get financial statement data for a given symbol."""
    if statement_type not in VALID_STATEMENT_TYPES:
        raise ValueError(f"Invalid statement_type: {statement_type}")

    cache = BlobCache(table_name=statement_type, project=project_name)
    logger.info(f"Fetching {statement_type} data for {symbol}")

    fetch_func = _get_fetch_func(statement_type)
    return cache.load_cached_data(symbol, period, use_cache, fetch_func, limit)


def _get_fetch_func(statement_type: str):
    """Get the appropriate fetch function for the statement type."""
    def fetch_func(symbol: str, period: str = "annual", limit: int = 5) -> DataFrame:
        return _fetch_financial_statement_data(symbol, statement_type, period, limit)
    return fetch_func


def _fetch_financial_statement_data(
    symbol: str,
    statement_type: str,
    period: str = "annual",
    limit: int = 5,
) -> DataFrame:
    """Fetch financial statement data from TdxQuant API."""
    from openbb_tdx.utils.financial_statement_mapping import (
        BalanceSheetMapper,
        IncomeStatementMapper,
        CashFlowStatementMapper,
    )

    symbol_b, symbol_f, market = normalize_symbol(symbol)
    stock_code = f"{symbol_b}.{market}"

    if statement_type == "balance_sheet":
        mapper = BalanceSheetMapper
    elif statement_type == "income_statement":
        mapper = IncomeStatementMapper
    elif statement_type == "cash_flow":
        mapper = CashFlowStatementMapper
    else:
        raise ValueError(f"Unknown statement type: {statement_type}")

    field_list = mapper.get_field_list()
    mmdd_values = [1231] if period == "annual" else [1231, 930, 630, 331]

    tq.initialize(__file__)

    try:
        # First get latest report to determine current year
        latest_data = tq.get_financial_data_by_date(
            stock_list=[stock_code],
            field_list=field_list,
            year=0,
            mmdd=0
        )

        if not latest_data or stock_code not in latest_data:
            logger.warning(f"No {statement_type} data found for {symbol}")
            return pd.DataFrame()

        latest_mapped = mapper.map_from_get_financial_data_by_date(
            latest_data, year=0, mmdd=0
        )
        
        if stock_code not in latest_mapped:
            logger.warning(f"No {statement_type} data found for {symbol}")
            return pd.DataFrame()

        latest_record = latest_mapped[stock_code]
        period_ending = latest_record.get("period_ending")
        
        if period_ending:
            if hasattr(period_ending, 'year'):
                current_year = period_ending.year
            else:
                current_year = int(str(period_ending)[:4])
        else:
            current_year = datetime.now().year

        all_data = []

        # Iterate through years to get historical data
        if period == "annual":
            for year_offset in range(limit):
                target_year = current_year - year_offset
                tdx_data = tq.get_financial_data_by_date(
                    stock_list=[stock_code],
                    field_list=field_list,
                    year=target_year,
                    mmdd=1231
                )

                if tdx_data and stock_code in tdx_data:
                    mapped_data = mapper.map_from_get_financial_data_by_date(
                        tdx_data, year=target_year, mmdd=1231
                    )
                    if stock_code in mapped_data:
                        record = mapped_data[stock_code]
                        all_data.append(record)
        else:
            for year_offset in range((limit // 4) + 1):
                target_year = current_year - year_offset
                for mmdd in mmdd_values:
                    if len(all_data) >= limit:
                        break
                    tdx_data = tq.get_financial_data_by_date(
                        stock_list=[stock_code],
                        field_list=field_list,
                        year=target_year,
                        mmdd=mmdd
                    )

                    if tdx_data and stock_code in tdx_data:
                        mapped_data = mapper.map_from_get_financial_data_by_date(
                            tdx_data, year=target_year, mmdd=mmdd
                        )
                        if stock_code in mapped_data:
                            record = mapped_data[stock_code]
                            all_data.append(record)
                if len(all_data) >= limit:
                    break

        if not all_data:
            logger.warning(f"No {statement_type} data found for {symbol}")
            return pd.DataFrame()

        df = pd.DataFrame(all_data)
        return df.head(limit)

    except Exception as e:
        logger.error(f"Error fetching {statement_type} data for {symbol}: {e}")
        return pd.DataFrame()
    finally:
        tq.close()
```

## Authentication and Connection Management

### Client Initialization

The TdxQuant provider requires the TongDaXin client to be running. The initialization process:

```python
import sys
from pathlib import Path
from tqcenter import tq

def initialize_tdxquant():
    """Initialize TdxQuant connection"""
    script_path = Path(__file__).resolve()
    tq.initialize(str(script_path))
    
    if not tq._initialized:
        raise RuntimeError(
            "Failed to initialize TdxQuant. "
            "Please ensure TongDaXin client is running and logged in."
        )

def cleanup_tdxquant():
    """Clean up TdxQuant connection"""
    tq.close()
```

### Error Handling

```python
from openbb_core.provider.abstract.error import OpenBBError

class TdxQuantError(OpenBBError):
    """Base exception for TdxQuant errors"""
    pass

class TdxQuantConnectionError(TdxQuantError):
    """Raised when connection to TongDaXin client fails"""
    pass

class TdxQuantDataError(TdxQuantError):
    """Raised when data retrieval fails"""
    pass

def handle_tdxquant_error(func):
    """Decorator for handling TdxQuant-specific errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            if "initialize" in str(e).lower():
                raise TdxQuantConnectionError(
                    "Cannot connect to TongDaXin client. "
                    "Please ensure the client is running."
                ) from e
            raise TdxQuantDataError(f"Data retrieval failed: {str(e)}") from e
        except Exception as e:
            raise TdxQuantError(f"TdxQuant error: {str(e)}") from e
    return wrapper
```

### Connection Validation

```python
def validate_connection() -> bool:
    """Validate TdxQuant connection"""
    try:
        test_data = tq.get_market_snapshot(
            stock_code='000001.SZ',  # Ping An Bank
            field_list=['Last']
        )
        return test_data is not None and '000001.SZ' in test_data
    except Exception:
        return False
```

## Data Format Specifications

### Stock Code Format

TdxQuant uses standard Chinese stock code format:
- **A-shares**: 6-digit code + `.SH` (Shanghai) or `.SZ` (Shenzhen)
  - Example: `688318.SH` (Kexin Co.), `600519.SH` (Kweichow Moutai)
- **Hong Kong**: 5-digit code + `.HK`
  - Example: `00700.HK` (Tencent)
- **Beijing Stock Exchange**: 8-digit code + `.BJ`
  - Example: `870523.BJ`

### Date Format

- **Input**: `YYYYMMDD` or `YYYYMMDDHHMMSS`
- **Output**: Index as `datetime64[ns]`

### Field Names Reference

| Field | Description | Unit |
|-------|-------------|------|
| Open | Opening price | Yuan |
| High | Highest price | Yuan |
| Low | Lowest price | Yuan |
| Close | Closing price | Yuan |
| Volume | Trading volume | Lots |
| Amount | Trading amount | Ten thousand Yuan |

---

# Testing Requirements

## Unit Test Structure

### Test File Organization

```
tests/
|-- conftest.py           # Shared fixtures
|-- test_equity_historical.py
|-- test_equity_quote.py
|-- test_balance_sheet.py
|-- test_income_statement.py
`-- test_cash_flow.py
```

### Conftest.py Template

```python
import os
import logging
import pytest
from mysharelib.tools import setup_logger
from openbb_tdx import project_name


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    setup_logger(project_name)


@pytest.fixture
def logger():
    return logging.getLogger(__name__)


@pytest.fixture
def default_provider():
    return "tdxquant"


@pytest.fixture
def tdxquant_api_key():
    return os.environ.get("TDXQUANT_API_KEY")
```

## Mocking Best Practices

### Critical Rule: Mock Where Used, Not Where Defined

When mocking helper functions, mock them in the module where they are **used**, not where they are **defined**:

```python
# CORRECT - Mock where the function is imported and used
@patch("openbb_tdx.models.balance_sheet.get_financial_statement_data")
def test_extract_data_success(self, mock_get_data):
    mock_get_data.return_value = pd.DataFrame({...})
    # Test code

# WRONG - Mock where the function is defined
@patch("openbb_tdx.utils.helpers.get_financial_statement_data")
def test_extract_data_success(self, mock_get_data):
    # This won't work because the function is imported in balance_sheet.py
```

### Mocking TdxQuant API

```python
from unittest.mock import patch, MagicMock
import pytest
import pandas as pd


class TestTdxQuantBalanceSheetFetcher:

    @patch("openbb_tdx.models.balance_sheet.get_financial_statement_data")
    def test_extract_data_success(self, mock_get_data):
        """Test extract_data returns correct data."""
        mock_data = MagicMock()
        mock_data.empty = False
        mock_data.to_dict.return_value = [
            {
                "period_ending": "2023-12-31",
                "fiscal_period": "Q4",
                "fiscal_year": 2023,
                "total_assets": 1000000000.0,
                "total_liabilities": 500000000.0,
                "total_equity": 500000000.0,
            }
        ]
        mock_get_data.return_value = mock_data

        query = TdxQuantBalanceSheetQueryParams(
            symbol="600519.SH",
            period="annual",
            limit=5,
        )

        result = TdxQuantBalanceSheetFetcher.extract_data(query, {})

        assert len(result) == 1
        assert result[0]["period_ending"] == "2023-12-31"
        mock_get_data.assert_called_once()

    @patch("openbb_tdx.models.balance_sheet.get_financial_statement_data")
    def test_extract_data_empty(self, mock_get_data):
        """Test extract_data raises EmptyDataError on empty data."""
        mock_data = MagicMock()
        mock_data.empty = True
        mock_get_data.return_value = mock_data

        query = TdxQuantBalanceSheetQueryParams(
            symbol="600519.SH",
            period="annual",
            limit=5,
        )

        with pytest.raises(EmptyDataError):
            TdxQuantBalanceSheetFetcher.extract_data(query, {})

    def test_transform_query(self):
        """Test transform_query creates correct params."""
        params = {
            "symbol": "600519.SH",
            "period": "annual",
            "limit": 10,
            "use_cache": False,
        }

        result = TdxQuantBalanceSheetFetcher.transform_query(params)

        assert result.symbol == "600519.SH"
        assert result.period == "annual"
        assert result.limit == 10
        assert result.use_cache is False

    def test_transform_data(self):
        """Test transform_data creates correct data models."""
        query = TdxQuantBalanceSheetQueryParams(symbol="600519.SH")
        data = [
            {
                "period_ending": "2023-12-31",
                "fiscal_period": "Q4",
                "fiscal_year": 2023,
                "total_assets": 1000000000.0,
            }
        ]

        result = TdxQuantBalanceSheetFetcher.transform_data(query, data)

        assert len(result) == 1
        assert isinstance(result[0], TdxQuantBalanceSheetData)
        assert result[0].fiscal_year == 2023
```

### Testing Date Fields

When testing date fields, use `date` objects for comparison:

```python
from datetime import date

def test_data_model_fields(self):
    """Test that data model fields are correctly typed."""
    data = TdxQuantBalanceSheetData(
        period_ending=date(2023, 12, 31),
        fiscal_period="Q4",
        fiscal_year=2023,
        total_assets=1000000000.0,
    )

    assert data.period_ending == date(2023, 12, 31)
    assert data.fiscal_year == 2023
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_balance_sheet.py -v

# Run tests matching pattern
pytest tests/ -k "balance" -v

# Run with coverage
pytest tests/ --cov=openbb_tdx --cov-report=html
```

---

# Common Pitfalls and Solutions

## 1. TableCache vs BlobCache Confusion

**Problem:** Using `TableCache` for financial statements causes errors because `fetch_all()` method doesn't exist.

**Solution:** Use `BlobCache` for financial statements and other non-time-series data.

```python
# WRONG
cache = TableCache(schema, project=project_name, table_name=name, primary_key="date")
cached_data = cache.fetch_all()  # AttributeError!

# CORRECT
cache = BlobCache(table_name="balance_sheet", project=project_name)
return cache.load_cached_data(symbol, period, use_cache, fetch_func, limit)
```

## 2. Year Parameter Misunderstanding

**Problem:** Treating TdxQuant's `year` parameter as an offset instead of actual year.

**Solution:** The `year` parameter is the specific year (e.g., 2023), not an offset.

```python
# WRONG - treating year as offset
for year_offset in range(limit):
    tdx_data = tq.get_financial_data_by_date(year=year_offset, ...)

# CORRECT - using actual years
for year_offset in range(limit):
    target_year = current_year - year_offset
    tdx_data = tq.get_financial_data_by_date(year=target_year, ...)
```

## 3. Mock Path Errors

**Problem:** Tests fail because mocks don't intercept the function calls.

**Solution:** Mock where the function is imported and used, not where it's defined.

```python
# If balance_sheet.py has: from openbb_tdx.utils.helpers import get_financial_statement_data
# Then mock it as:
@patch("openbb_tdx.models.balance_sheet.get_financial_statement_data")
```

## 4. Empty DataFrame Handling

**Problem:** Code crashes when API returns no data.

**Solution:** Always check for empty DataFrames and raise `EmptyDataError`.

```python
from openbb_core.provider.utils.errors import EmptyDataError

def extract_data(query, credentials):
    data = fetch_from_api(query.symbol)
    
    if data.empty:
        raise EmptyDataError()
    
    return data.to_dict(orient="records")
```

## 5. Resource Cleanup

**Problem:** TdxQuant connections not properly closed, causing resource leaks.

**Solution:** Always use try/finally to close connections.

```python
def fetch_data():
    tq.initialize(__file__)
    try:
        data = tq.get_market_data(...)
        return data
    finally:
        tq.close()
```

---

# Reference Implementations

## Reference Projects

- [openbb_akshare](references/openbb_akshare) - Example provider for AKShare
- [openbb_tdx](.) - TdxQuant provider implementation

## Key Files to Reference

| File | Purpose |
|------|---------|
| `provider.py` | Provider registration and fetcher dictionary |
| `router.py` | FastAPI route definitions |
| `models/*.py` | Data models and fetcher implementations |
| `utils/helpers.py` | Data fetching and caching helpers |
| `utils/financial_statement_mapping.py` | TDX to OpenBB field mappings |

---

# Version Compatibility

## Python Version

- Minimum: Python 3.9
- Recommended: Python 3.11+

## OpenBB Core Version

- Minimum: openbb-core 2.0.0
- Check `pyproject.toml` for current version requirements

## Dependency Management

```toml
[tool.poetry.dependencies]
python = "^3.9"
openbb-core = "^2.0.0"
pandas = "^2.0.0"
pydantic = "^2.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-asyncio = "^0.21.0"
```

---

# Documentation Templates

## Model Docstring Template

```python
"""TdxQuant [Feature Name] Model.

This module provides data models and fetchers for [description of functionality].

Example:
    >>> from openbb import obb
    >>> data = obb.equity.fundamental.balance_sheet(symbol="600519.SH", provider="tdxquant")
"""
```

## Fetcher Docstring Template

```python
class TdxQuant[Feature]Fetcher(
    Fetcher[
        TdxQuant[Feature]QueryParams,
        List[TdxQuant[Feature]Data],
    ]
):
    """Transform the query, extract and transform the data from the TdxQuant endpoints.

    This fetcher retrieves [description] from TdxQuant API.

    Parameters
    ----------
    symbol : str
        Stock symbol in format XXXXXX.SH or XXXXXX.SZ
    period : Literal["annual", "quarter"]
        Reporting period
    limit : int
        Number of periods to return

    Returns
    -------
    List[TdxQuant[Feature]Data]
        List of [feature] data records

    Raises
    ------
    EmptyDataError
        When no data is returned from the API
    """
```

---

# Best Practices Summary

1. **Use BlobCache for financial statements** - Not TableCache
2. **Mock where functions are used** - Not where they're defined
3. **Always handle empty data** - Raise `EmptyDataError`
4. **Clean up TdxQuant connections** - Use try/finally
5. **Use actual year values** - Not offsets for TdxQuant API
6. **Keep validation simple** - Use lists instead of complex schemas when schemas aren't needed
7. **Follow the three-method fetcher pattern** - `transform_query`, `extract_data`, `transform_data`
8. **Write comprehensive tests** - Cover success, empty data, and error cases
9. **Document all parameters** - Use Pydantic Field descriptions
10. **Follow existing patterns** - Check reference implementations before starting

---

Template files and boilerplate code for rapid provider development are available in the assets directory.
