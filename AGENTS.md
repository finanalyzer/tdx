# AGENTS.md

## Commands

**Install:**
```bash
pip install -e .
```

**Test:**
```bash
pytest tests/test_equity_historical.py -v
pytest tests/ -k "equity" -v
```

**Build:**
```bash
python -m openbb_tdx.openbb build
```

## Architecture

**Entry Points:**
- `openbb_tdx/provider.py` - Provider registration (`tdxquant`), fetcher dict
- `openbb_tdx/router.py` - FastAPI route definitions with `@router.command()`
- `openbb_tdx/models/*.py` - Fetcher classes inheriting `Fetcher[QueryParams, Data]`
- `openbb_tdx/utils/helpers.py` - Data fetching (`tdx_download`, `check_cache`)

**Data Flow:**
Router → Fetcher.transform_query → Fetcher.extract_data → Fetcher.transform_data → Response

**Key Patterns:**
- All fetchers must implement: `transform_query(params)`, `extract_data(query, credentials)`, `transform_data(query, data)`
- Use `__json_schema_extra__` for `multiple_items_allowed` on symbols
- Use `__alias_dict__` for Chinese→English field mapping (e.g., `"date": "日期"`)

## Critical Dependencies

**TdxQuant Client (`tqcenter.tq`):**
- Must have TongDaXin client running and logged in
- SDK only available on Windows; `tq.initialize(__file__)` used in extract_data
- Mock `tqcenter.tq` in tests

**Normalization:**
- Use `normalize_symbol()` from `mysharelib.tools` for all stock codes
- Converts various formats to `{code}.{market}` (e.g., `600519.SH`)

**Caching:**
- `TableCache(EQUITY_HISTORY_SCHEMA, project=project_name, table_name=f"{market}{symbol_b}", primary_key="date")`
- `check_cache()` validates TTL by comparing cache max date with `last_closing_day()`

## Testing

**Mock TdxQuant:**
```python
from unittest.mock import patch
with patch('tqcenter.tq') as mock_tq:
    # test code
```

**Test Structure:**
- Tests in `tests/` directory, one file per feature
- Test fetcher methods: `transform_query()`, `extract_data()`, `transform_data()`
- Verify `EmptyDataError` on empty results

## Spec-Driven Development

Check `.trae/specs/` before implementing:
- `spec.md` - Requirements and design
- `tasks.md` - Implementation tasks
- `checklist.md` - Validation checklist

## Important Notes

- **Windows only**: `tqcenter.tq` SDK requires Windows
- **Initializes in extract_data**: `tq.initialize(__file__)` is called per symbol fetch
- **Period mapping**: `"daily"`→`"1d"`, `"weekly"`→`"1w"`, `"monthly"`→`"1m"`
- **Date format**: Input dates passed to TdxQuant must be `YYYYMMDD` string
- **Standard params**: Query params automatically include `start_date`, `end_date` if not provided
