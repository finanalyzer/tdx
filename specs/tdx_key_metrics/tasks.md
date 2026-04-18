# TdxQuant Key Metrics Module - Implementation Tasks

## Overview
This document outlines the implementation tasks for creating the TdxQuant Key Metrics module for the OpenBB Platform.

---

## Task List

### Phase 1: Module Implementation

#### Task 1.1: Create equity_key_metrics.py Model File
**File**: `openbb_tdx/models/equity_key_metrics.py`

**Steps**:
1. Import required modules:
   - `typing`: Any, Dict, List, Optional
   - `openbb_core.provider.abstract.fetcher.Fetcher`
   - `openbb_core.provider.standard_models.key_metrics` (KeyMetricsData, KeyMetricsQueryParams)
   - `openbb_core.provider.utils.descriptions.QUERY_DESCRIPTIONS`
   - `openbb_core.provider.utils.errors.EmptyDataError`
   - `pydantic.Field`
   - `openbb_core.app.model.abstract.error.OpenBBError`
   - `asyncio` for concurrent processing
   - Logging utilities from mysharelib

2. Create `TdxQuantKeyMetricsQueryParams` class:
   - Inherit from `KeyMetricsQueryParams`
   - Add `__json_schema_extra__` with `multiple_items_allowed` for symbol
   - Add `period` field with choices ["annual", "quarter"], default "quarter"
   - Add `use_cache` field with default True

3. Create `TdxQuantKeyMetricsData` class:
   - Inherit from `KeyMetricsData`
   - Define `__alias_dict__` mapping TdxQuant fields to OpenBB fields:
     - "symbol": "证券代码"
     - "fiscal_period": "报告类型"
     - "period_ending": "报告日期"
     - "market_cap": "流通值"
     - "pe_ratio": "市盈率(动)"
   - Add field validators for numeric and date fields

4. Create `TdxQuantKeyMetricsFetcher` class:
   - Implement `transform_query()` static method
   - Implement `aextract_data()` async static method:
     - Initialize TdxQuant connection
     - Split symbols and process concurrently with asyncio.gather()
     - Call `map_tdx_to_openbb()` for each symbol
     - Handle errors and collect results
   - Implement `transform_data()` static method

**Estimated Time**: 2-3 hours

---

#### Task 1.2: Update models/__init__.py
**File**: `openbb_tdx/models/__init__.py`

**Steps**:
1. Add import for the new key_metrics classes:
   ```python
   from openbb_tdx.models.equity_key_metrics import (
       TdxQuantKeyMetricsData,
       TdxQuantKeyMetricsFetcher,
       TdxQuantKeyMetricsQueryParams,
   )
   ```

2. Add classes to `__all__` list

**Estimated Time**: 10 minutes

---

#### Task 1.3: Update provider.py
**File**: `openbb_tdx/provider.py`

**Steps**:
1. Add import for `TdxQuantKeyMetricsFetcher`

2. Add entry to `fetcher_dict`:
   ```python
   "KeyMetrics": TdxQuantKeyMetricsFetcher,
   ```

**Estimated Time**: 10 minutes

---

### Phase 2: Testing

#### Task 2.1: Create Unit Tests
**File**: `tests/test_equity_key_metrics.py`

**Steps**:
1. Create test classes:
   - `TestTdxQuantKeyMetricsQueryParams`: Test query parameter validation
   - `TestTdxQuantKeyMetricsData`: Test data model validation
   - `TestTdxQuantKeyMetricsFetcher`: Test fetcher methods
   - `TestIntegration`: Integration tests with TdxQuant client

2. Implement test cases:
   - Single symbol query
   - Multiple symbols query
   - Data validation with valid/empty/invalid data
   - Mock tests for API calls
   - Integration tests (skip if client unavailable)

**Estimated Time**: 2-3 hours

---

### Phase 3: Verification

#### Task 3.1: Code Review
- Review for pylint warnings
- Check for type hints
- Verify docstrings
- Check error handling

#### Task 3.2: Run Tests
- Run unit tests with pytest
- Verify all tests pass
- Fix any failures

#### Task 3.3: Manual Verification
- Test with actual TdxQuant client if available
- Verify data accuracy

---

## Implementation Sequence

1. **Task 1.1** → Create the main model file (equity_key_metrics.py)
2. **Task 1.2** → Update models/__init__.py
3. **Task 1.3** → Update provider.py
4. **Task 2.1** → Create unit tests
5. **Task 3.1-3.3** → Verification

---

## Dependencies

- Requires `openbb_tdx/utils/tdx_key_metrics.py` (already exists)
- Requires OpenBB core library
- Requires TdxQuant client for integration tests

---

## Success Criteria

- [ ] Model file created with all required classes
- [ ] Provider correctly registers the new fetcher
- [ ] Unit tests pass with mocking
- [ ] Integration tests pass (if TdxQuant available)
- [ ] Code follows existing patterns and conventions
- [ ] No pylint errors
