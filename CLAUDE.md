# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the OpenBB TdxQuant extension, integrating financial data from the 通达信量化平台 (TdxQuant) into the OpenBB Platform. It provides historical price data, real-time quotes, dividends, equity profiles, stock search, and key metrics for Chinese A-shares.

## Development Commands

### Installation and Setup

```bash
# Install dependencies in editable mode
pip install -e .

# Run tests
pytest

# Run a specific test
pytest tests/test_equity_historical.py -v

# Run all tests
pytest tests/ -v
```

### Building the Extension

```bash
# Build the extension (OpenBB standard command)
python -m openbb_tdx.openbb build
```

## Architecture

### Provider Structure

This extension follows OpenBB's provider architecture with the following components:

```
openbb_tdx/
├── models/                    # Pydantic models for data structures
│   ├── equity_historical.py   # Historical price data model
│   ├── equity_quote.py        # Real-time quote model
│   ├── equity_dividends.py    # Dividend data model
│   ├── equity_profile.py      # Stock profile model
│   ├── equity_search.py       # Stock search model
│   └── equity_key_metrics.py  # Key metrics model
├── utils/
│   ├── constants.py           # Market types, periods, enums
│   ├── helpers.py             # Data fetching helpers (tdx_download)
│   └── financial_statement_mapping.py  # Financial statement mappings
├── provider.py               # Provider initialization
├── router.py                 # FastAPI route definitions
└── __init__.py               # Module init
```

### Data Flow

1. **User Request**: OpenBB API call (e.g., `obb.equity.price.historical()`)
2. **Router**: Routes to appropriate handler in `router.py`
3. **Fetcher**: `openbb_tdx/models/*.py` contains `Fetcher` classes
4. **Transform**: Query parameters validated, data extracted from TdxQuant
5. **Transform**: Raw data transformed to OpenBB standard models
6. **Response**: OpenBB response object with data

### Key Integration Points

**Provider Registration** (`provider.py`):
- Defines the `tdxquant` provider with available fetchers
- Registered in `pyproject.toml` as `openbb-core-extension`

**Router** (`router.py`):
- FastAPI route definitions using `@router.command()`
- Creates `OBBject` from query parameters

**Fetcher Pattern**:
All fetchers inherit from `openbb_core.provider.abstract.fetcher.Fetcher`:
```python
class TdxQuantFetcher(Fetcher[QueryParams, Data]):
    @staticmethod
    def transform_query(params: Dict) -> QueryParams:
        # Validate and transform input

    @staticmethod
    def extract_data(query: QueryParams, credentials: Dict) -> List[Dict]:
        # Fetch raw data from TdxQuant

    @staticmethod
    def transform_data(query: QueryParams, data: List[Dict]) -> List[Data]:
        # Transform to standard model
```

### Data Source: TdxQuant

TdxQuant requires the TongDaXin (通达信) client to be running. The main data fetching is handled through the `tqcenter.tq` module.

**Main Functions**:
- `tq.get_market_data()`: Fetch K-line data
- `tq.get_stock_info()`: Get stock basic info
- `tq.get_financial_data()`: Get financial reports

**Stock Code Format**:
- A-shares: `{6-digit_code}.{SH|SZ}` (e.g., `600519.SH`, `000001.SZ`)
- Hong Kong: `{5-digit_code}.HK`
- Beijing: `{8-digit_code}.BJ`

## Coding Standards

### Naming Conventions
- Classes: `PascalCase` (e.g., `TdxQuantEquityHistoricalFetcher`)
- Modules: `snake_case` (e.g., `equity_historical.py`)
- Functions: `snake_case` (e.g., `transform_query`)
- Constants: `UPPER_SNAKE_CASE`

### Pydantic Models
All data models must inherit from OpenBB's standard models:
- `QueryParams`: Input validation and transformation
- `Data`: Output data structure

Use `__json_schema_extra__` for custom schema definitions and `__alias_dict__` for field mapping.

### Error Handling
- Use `openbb_core.provider.utils.errors.EmptyDataError` for empty results
- Wrap TdxQuant-specific exceptions in OpenBB errors
- Use `logging` module (already configured via `mysharelib.tools.setup_logger`)

### Stock Code Normalization
Use `normalize_symbol()` from `mysharelib.tools` to convert various stock code formats to standard format (base + suffix).

## Constants and Configuration

### Market Types (`utils/constants.py`)
- `Market.SZ`, `Market.SH`, `Market.BJ`: Stock exchanges
- `Period`: Time periods (`1d`, `1w`, `1m`, `5m`, etc.)
- `DividendType`: Price adjustment types (`none`, `front`, `back`)

### Helper Functions
- `tdx_download()`: Fetch historical data with optional caching
- `check_cache()`: Validate cached data freshness
- `get_exchange_name_from_symbol()`: Get exchange name from stock code

## Testing

### Test Structure
Tests are organized in `tests/` directory with separate test files for each feature.

### Running Tests
```bash
pytest tests/test_equity_historical.py -v --cov=openbb_tdx
pytest tests/ -k "equity" -v
```

### Mocking TdxQuant
When testing, mock the `tqcenter.tq` module:
```python
from unittest.mock import patch
with patch('tqcenter.tq') as mock_tq:
    # Test code using mock
```

## Specification-Driven Development

This project uses spec-driven development in `.trae/specs/`:

- `spec.md`: Detailed requirements and design
- `tasks.md`: Implementation tasks
- `checklist.md`: Validation checklist

When implementing new features, check if a spec exists first.

## Important Notes

1. **TdxQuant Client**: Must have TongDaXin client running and logged in
2. **Platform Compatibility**: Currently optimized for Windows (TdxQuant SDK requirement)
3. **Caching**: Uses `mysharelib.table_cache.TableCache` for local caching with TTL validation
4. **Async Operations**: OpenBB uses async patterns; ensure fetchers handle async correctly
5. **Multiple Symbols**: Some endpoints support multiple symbols (check `__json_schema_extra__`)
6. **Field Mapping**: Chinese field names from TdxQuant are mapped to English via `__alias_dict__`
