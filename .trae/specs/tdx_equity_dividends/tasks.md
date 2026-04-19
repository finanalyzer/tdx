# TdxQuant Equity Dividends - Implementation Tasks

## Task List

### Phase 1: Specification and Planning
- [x] Create SPEC.md with detailed requirements
- [x] Create tasks.md (this file) with implementation steps
- [ ] Create checklist.md for verification

### Phase 2: Implementation

#### Task 1: Create the Equity Dividends Model
**File:** `openbb_tdx/models/equity_dividends.py`

**Steps:**
1. Create `TdxQuantEquityDividendsQueryParams` class
   - Inherit from `EquityDividendsQueryParams`
   - Add `symbol` field with description
   - Add `__json_schema_extra__` for symbol configuration

2. Create `TdxQuantEquityDividendsData` class
   - Inherit from `EquityDividendsData`
   - Define field aliases for TdxQuant API response mapping
   - Add date validators for date fields

3. Create `TdxQuantEquityDividendsFetcher` class
   - Implement `transform_query()` method
   - Implement `extract_data()` method using `tq.get_divid_factors()`
   - Implement `transform_data()` method
   - Add proper error handling and logging

#### Task 2: Update Models Module `__init__.py`
**File:** `openbb_tdx/models/__init__.py`

**Steps:**
1. Import the new classes:
   - `TdxQuantEquityDividendsQueryParams`
   - `TdxQuantEquityDividendsData`
   - `TdxQuantEquityDividendsFetcher`

2. Add all new classes to `__all__` list

#### Task 3: Update Provider Configuration
**File:** `openbb_tdx/provider.py`

**Steps:**
1. Import `TdxQuantEquityDividendsFetcher`
2. Add `"EquityDividends": TdxQuantEquityDividendsFetcher` to `fetcher_dict`

#### Task 4: Create Unit Tests
**File:** `tests/test_equity_dividends.py`

**Steps:**
1. Create test class `TestTdxQuantEquityDividendsFetcher`
2. Implement test for `transform_query()`
3. Implement test for `extract_data()` with mocking
4. Implement test for `transform_data()`
5. Implement edge case tests (empty data, invalid symbol)

### Phase 3: Verification

#### Task 5: Run Linting and Type Checking
**Commands:**
```bash
# Run pylint
pylint openbb_tdx/models/equity_dividends.py

# Run mypy
mypy openbb_tdx/models/equity_dividends.py
```

#### Task 6: Run Unit Tests
**Commands:**
```bash
# Run pytest
pytest tests/test_equity_dividends.py -v
```

#### Task 7: Integration Test (Manual)
**Steps:**
1. Ensure TongDaXin client is running
2. Run a quick integration test to verify real API calls work

## Implementation Details

### Helper Function Requirements

The implementation will utilize existing helpers where possible:

1. `normalize_symbol()` - from `mysharelib.tools` - for symbol parsing
2. `tq.get_divid_factors()` - from `tqcenter` - for fetching dividend data

### API Details for `get_divid_factors()`

Based on the test file reference, `get_divid_factors()` signature:
```python
divid_factors = tq.get_divid_factors(
    stock_code='688318.SH',
    start_time='',
    end_time='')
```

### Symbol Formats
- A-shares: `XXXXXX.SH` or `XXXXXX.SZ` (6 digits + market suffix)
- HK stocks: `XXXXX.HK` (5 digits + .HK)
- The `normalize_symbol()` function handles conversion to TdxQuant format

## Files to Modify/Create

| File | Action | Description |
|------|--------|-------------|
| `openbb_tdx/models/equity_dividends.py` | CREATE | New dividends model |
| `openbb_tdx/models/__init__.py` | MODIFY | Add dividends exports |
| `openbb_tdx/provider.py` | MODIFY | Register dividends fetcher |
| `tests/test_equity_dividends.py` | CREATE | Unit tests |

## Estimated Complexity

- **New Files:** 2 (model + tests)
- **Modified Files:** 2 (models/__init__.py, provider.py)
- **New Classes:** 3 (QueryParams, Data, Fetcher)
- **Estimated Lines of Code:** ~200-300
