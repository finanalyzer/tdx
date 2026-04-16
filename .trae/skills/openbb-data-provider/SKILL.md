---
name: openbb-data-provider
description: Comprehensive guidance for developing OpenBB data providers using Python and FastAPI. This skill helps developers create, implement, test, and troubleshoot OpenBB data provider extensions following official documentation guidelines. Use this skill when developing custom data providers for the OpenBB platform, implementing data provider classes and methods, working with FastAPI endpoints, handling data validation, or following OpenBB's coding standards and patterns. Special focus on TdxQuant (TongDaXin) data provider integration for China A-share and Hong Kong markets.
---

# OpenBB Data Provider Development

## Overview

This skill provides comprehensive guidance for creating, implementing, and troubleshooting OpenBB data providers. It covers the architecture, structure, and best practices for developing Python-based data providers that integrate seamlessly with the OpenBB ecosystem, leveraging FastAPI for endpoints and following OpenBB's standardization framework.

## Architecture Overview

OpenBB data providers follow a standardized architecture that ensures consistency across the platform:

- **Core Components**: Built on `openbb-core` as the foundation
- **Provider Extensions**: Independent data sources that implement a standardized pipeline
- **Standard Models**: Shared data structures that ensure consistency across providers
- **Fetcher Classes**: Handle data extraction and transformation from external APIs
- **Routers**: Manage input/output operations and endpoint routing

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
   |-- models/
   |   |-- __init__.py
   |   `-- historical.py
   |-- fetcher/
   |   |-- __init__.py
   |   `-- historical.py
   |-- views/
   |   |-- __init__.py
   |   `-- historical.py
   |-- pyproject.toml
   `-- README.md
   ```

2. **TOML Configuration**: Define your provider as a Poetry plugin in `pyproject.toml`:
   ```toml
   [tool.poetry.plugins."openbb-extension"]
   "my_provider" = "openbb_my_provider.provider:provider"
   ```

3. **Provider Definition**: Initialize a `Provider` class in your `__init__.py`:
   ```python
   from openbb_core.provider.abstract.provider import Provider

   provider = Provider(
       name="my_provider",
       fetcher_dict={},
       repr_count=3,
       full_name="My Custom Provider"
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
   from typing import Dict, List
   
   class MyProviderFetcher(Fetcher[MyProviderQueryParams, MyProviderData]):
       @staticmethod
       def transform_query(params: Dict[str, any]) -> MyProviderQueryParams:
           return MyProviderQueryParams(**params)
       
       @staticmethod
       async def aextract(data: MyProviderQueryParams, **kwargs) -> Dict:
           url = f"https://api.myprovider.com/data/{data.symbol}"
           return await amake_requests(url)
       
       @staticmethod
       def transform_data(response: Dict, data: MyProviderQueryParams, **kwargs) -> List[MyProviderData]:
           # Transform API response to standard format
           return [MyProviderData(date=item['date'], close=item['close']) for item in response['data']]
   ```

### 4. Registering Your Fetcher

Add your fetcher to the provider's `fetcher_dict` in `__init__.py`:
```python
from .fetcher.historical import MyProviderHistoricalFetcher

provider = Provider(
    name="my_provider",
    fetcher_dict={
        "stock_price_historical": MyProviderHistoricalFetcher,
    },
    repr_count=3,
    full_name="My Custom Provider"
)
```

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

#### 3. Financial Data

```python
def get_financial_data(
    stock_list: List[str],
    field_list: List[str],
    start_time: str = '',
    end_time: str = '',
    report_type: str = 'report_time'
) -> Dict
```

**Parameters:**
- `report_type`: "report_time" (by reporting date) or "announce_time" (by announcement date)

**Code Example:**
```python
fd = tq.get_financial_data(
    stock_list=['688318.SH'],
    field_list=['Fn193', 'Fn194', 'Fn195'],
    start_time='20250101',
    report_type='announce_time'
)
```

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
openbb_tdxquant/
|-- __init__.py
|-- models/
|   |-- __init__.py
|   |-- historical.py
|   ├── quote.py
|   └── fundamentals.py
|-- fetcher/
|   |-- __init__.py
|   |-- historical.py
|   ├── quote.py
|   └── fundamentals.py
|-- pyproject.toml
`-- README.md
```

### Example: Historical Price Fetcher

```python
from typing import Dict, List, Optional
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


class TdxQuantHistoricalFetcher(Fetcher[TdxQuantHistoricalQueryParams, TdxQuantHistoricalData]):

    @staticmethod
    def transform_query(params: Dict) -> TdxQuantHistoricalQueryParams:
        return TdxQuantHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TdxQuantHistoricalQueryParams,
        credentials: Dict
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
        data: List[Dict]
    ) -> List[TdxQuantHistoricalData]:
        return [TdxQuantHistoricalData(**item) for item in data]
```

### Example: Real-time Quote Fetcher

```python
from typing import Dict, List, Optional, Callable
from pydantic import Field
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query import QueryParams
from openbb_core.provider.abstract.fetcher import Fetcher


class TdxQuantQuoteQueryParams(QueryParams):
    symbol: str = Field(description="Stock symbol (e.g., 688318.SH)")


class TdxQuantQuoteData(Data):
    symbol: str = Field(description="Stock symbol")
    last: float = Field(description="Last price")
    open: float = Field(description="Open price")
    high: float = Field(description="High price")
    low: float = Field(description="Low price")
    volume: int = Field(description="Volume")
    amount: float = Field(description="Amount")
    timestamp: str = Field(description="Update timestamp")


class TdxQuantQuoteFetcher(Fetcher[TdxQuantQuoteQueryParams, TdxQuantQuoteData]):

    def __init__(self):
        super().__init__()
        self._callback_func = None
        self._cached_data = {}

    @staticmethod
    def transform_query(params: Dict) -> TdxQuantQuoteQueryParams:
        return TdxQuantQuoteQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TdxQuantQuoteQueryParams,
        credentials: Dict
    ) -> Dict:
        snapshot = tq.get_market_snapshot(
            stock_code=query.symbol,
            field_list=['Last', 'Open', 'High', 'Low', 'Volume', 'Amount']
        )
        
        if not snapshot or query.symbol not in snapshot:
            return {}
            
        return snapshot[query.symbol].to_dict()

    @staticmethod
    def transform_data(
        query: TdxQuantQuoteQueryParams,
        data: Dict
    ) -> TdxQuantQuoteData:
        return TdxQuantQuoteData(
            symbol=query.symbol,
            last=data.get('Last', 0),
            open=data.get('Open', 0),
            high=data.get('High', 0),
            low=data.get('Low', 0),
            volume=data.get('Volume', 0),
            amount=data.get('Amount', 0),
            timestamp=datetime.now().isoformat()
        )
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

## Testing Requirements

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from openbb_tdxquant.fetcher.historical import (
    TdxQuantHistoricalFetcher,
    TdxQuantHistoricalQueryParams
)


class TestTdxQuantHistoricalFetcher:

    @pytest.fixture
    def mock_tq(self):
        with patch('tqcenter.tq') as mock:
            yield mock

    def test_transform_query(self):
        params = {
            'symbol': '688318.SH',
            'start_date': '20250101',
            'end_date': '20250601'
        }
        result = TdxQuantHistoricalFetcher.transform_query(params)
        
        assert result.symbol == '688318.SH'
        assert result.start_date == '20250101'
        assert result.end_date == '20250601'

    @pytest.mark.asyncio
    async def test_fetch_with_mock(self, mock_tq):
        mock_tq.get_market_data.return_value = {
            '688318.SH': Mock(
                to_dict=lambda orient: [
                    {'date': '2025-01-01', 'open': 10.0, 'high': 11.0, 
                     'low': 9.5, 'close': 10.5, 'volume': 1000, 'amount': 10000}
                ]
            )
        }
        
        query = TdxQuantHistoricalQueryParams(
            symbol='688318.SH',
            start_date='20250101',
            end_date='20250601'
        )
        
        fetcher = TdxQuantHistoricalFetcher()
        data = fetcher.extract_data(query, {})
        
        assert len(data) > 0
        assert data[0]['close'] == 10.5
```

### Integration Tests

```python
import pytest
from openbb import obb


class TestTdxQuantIntegration:

    @pytest.mark.skipif(
        not is_tdxquant_available(),
        reason="TdxQuant client not available"
    )
    def test_historical_price(self):
        result = obb.equity.price.historical(
            symbol="600519",
            start_date="2025-01-01",
            end_date="2025-06-01",
            provider="tdxquant"
        )
        
        assert result is not None
        df = result.to_dataframe()
        assert len(df) > 0
        assert 'close' in df.columns

    @pytest.mark.skipif(
        not is_tdxquant_available(),
        reason="TdxQuant client not available"
    )
    def test_quote(self):
        result = obb.equity.quote(
            symbol="600519",
            provider="tdxquant"
        )
        
        assert result is not None
        assert result.data['last'] > 0
```

### Validation Criteria

1. **Data Accuracy**: Compare with known reference data
2. **Response Time**: Ensure queries complete within acceptable time
3. **Error Handling**: Verify proper error messages for invalid inputs
4. **Connection Recovery**: Test reconnection after client restart
5. **Data Completeness**: Verify all expected fields are populated

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

class TdxQuantCache:
    _cache = {}
    _cache_ttl = timedelta(minutes=5)
    
    @classmethod
    def get(cls, key: str):
        if key in cls._cache:
            data, timestamp = cls._cache[key]
            if datetime.now() - timestamp < cls._cache_ttl:
                return data
        return None
    
    @classmethod
    def set(cls, key: str, value):
        cls._cache[key] = (value, datetime.now())
```

### Batch Processing

```python
def fetch_multiple_stocks(stock_list: List[str], **kwargs):
    """Fetch data for multiple stocks efficiently"""
    return tq.get_market_data(stock_list=stock_list, **kwargs)
```

## Troubleshooting

### Common Issues

1. **Client Not Running**
   - Error: "TQ data interface initialization failed"
   - Solution: Start TongDaXin client and log in

2. **Invalid Stock Code**
   - Error: "股票代码格式错误"
   - Solution: Use correct format (6 digits + .SH/.SZ)

3. **Data Not Available**
   - Error: Empty DataFrame returned
   - Solution: Download required data in TongDaXin client

4. **DLL Loading Failure**
   - Error: "TPythClient.dll not found"
   - Solution: Ensure DLL is in correct path

### Debug Mode

```python
import logging

logging.basicConfig(level=logging.DEBUG)
tq.initialize(__file__)
```

## FastAPI Integration

OpenBB leverages FastAPI for its endpoint routing. When implementing your provider:

1. **Endpoint Structure**: Follow OpenBB's standard patterns:
   - `/equity/price/historical` for historical stock prices
   - `/equity/quote` for real-time quotes
   - `/equity/fundamentals` for financial data

2. **Parameter Validation**: Use Pydantic models for request validation:
   ```python
   from pydantic import BaseModel, Field
   
   class HistoricalPriceQueryParams(BaseModel):
       symbol: str = Field(..., description="Stock symbol to query")
       start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
       end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
   ```

3. **Error Handling**: Implement proper error handling:
   ```python
   from openbb_core.provider.abstract.error import OpenBBError
   
   try:
       data = tq.get_market_data(...)
   except Exception as e:
       raise OpenBBError(f"Failed to fetch data from TdxQuant: {str(e)}")
   ```

## Data Validation and Error Management

### Input Validation
- Validate all input parameters using Pydantic models
- Check for required fields and proper data types
- Validate symbol formats, date ranges, and other constraints

### Data Transformation
- Ensure data conforms to OpenBB's standard models
- Handle missing or null values appropriately
- Convert data types as needed (strings to floats, dates to proper format)

### Error Handling Strategies
1. **Provider-Specific Errors**: Handle TongDaXin client issues, DLL errors
2. **Data Quality Issues**: Validate data integrity and handle malformed responses
3. **Fallback Mechanisms**: Consider fallback to AKShare when TdxQuant unavailable

## Testing and Debugging

### Unit Testing
Create comprehensive unit tests for your provider:
```python
import pytest
from openbb_tdxquant.models.historical import TdxQuantHistoricalFetcher

@pytest.mark.asyncio
async def test_fetcher():
    params = {"symbol": "600519.SH"}
    fetcher = TdxQuantHistoricalFetcher()
    result = await fetcher.fetch(params)
    assert result is not None
```

### Integration Testing
Test your provider within the OpenBB ecosystem:
```python
from openbb import obb

result = await obb.equity.price.historical(
    symbol="600519",
    provider="tdxquant"
)
assert result is not None
```

### Debugging Tips
- Enable debug logging: `obb.debug = True`
- Use `obb.coverage.providers` to check installed provider coverage
- Verify your provider is properly registered with `obb.registered_providers`

## Coding Standards and Patterns

### Naming Conventions
- Use lowercase with underscores for module names: `historical_price.py`
- Use PascalCase for class names: `TdxQuantHistoricalFetcher`
- Use snake_case for function and variable names: `transform_query`

### Code Organization
- Separate concerns: models, fetchers, and views in distinct modules
- Keep fetcher classes focused on single responsibilities
- Use descriptive function names that clearly indicate their purpose

### Documentation Standards
- Include comprehensive docstrings for all public methods
- Document all parameters, return values, and exceptions
- Follow OpenBB's documentation patterns

## Integration with OpenBB Ecosystem

### Standard Model Compliance
Ensure your provider's data models comply with OpenBB's standard models to enable:
- Cross-provider comparison
- Consistent data structure
- Unified interface experience

### Configuration Management
- Store API keys securely using OpenBB's configuration system
- Implement proper credential validation
- Handle configuration changes gracefully

### Performance Optimization
- Implement efficient data caching mechanisms
- Use asynchronous operations where possible
- Optimize API calls to minimize response time

## Troubleshooting Common Issues

### Provider Not Recognized
- Verify your provider is correctly registered in `pyproject.toml`
- Run `openbb-build` after modifying the `fetcher_dict`
- Check that your package is properly installed

### Data Model Mismatches
- Ensure your models inherit from the correct standard models
- Verify field names and types match expectations
- Check that transformations maintain data integrity

### API Connection Issues
- Confirm TongDaXin client is running
- Check DLL path configuration
- Verify stock code formats

## Resources

### References
- [TdxQuant Official Documentation](https://help.tdx.com.cn/quant/docs/markdown/ctx.stock.md/)
- [tqcenter.py](references/tqcenter.py) - Full API implementation
- [tdxdata_test.py](references/tdxdata_test.py) - Usage examples
- [openbb_akshare](references/openbb_akshare) - Example provider for AKShare

### Related Projects
- [openbb-akshare](https://github.com/finanalyzer/openbb_akshare) - AKShare provider for comparison
- [openbb-tushare](https://github.com/finanalyzer/openbb_tushare) - Tushare provider

### Scripts
Helper scripts for common development tasks are available in the scripts directory.

### Assets
Template files and boilerplate code for rapid provider development are available in the assets directory.