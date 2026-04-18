"""Unit tests for TdxQuant Equity Key Metrics module."""

import pytest
from datetime import date
from unittest.mock import Mock, patch, AsyncMock
import pandas as pd

from openbb_tdx.models.equity_key_metrics import (
    TdxQuantKeyMetricsQueryParams,
    TdxQuantKeyMetricsData,
    TdxQuantKeyMetricsFetcher,
)
from openbb_core.provider.standard_models.key_metrics import KeyMetricsData


class TestTdxQuantKeyMetricsQueryParams:
    """Test suite for query parameters model."""

    def test_single_symbol(self):
        """Test query params with single symbol."""
        params = TdxQuantKeyMetricsQueryParams(symbol="688318.SH")
        assert params.symbol == "688318.SH"
        assert params.use_cache == True
        assert params.period == "quarter"

    def test_multiple_symbols(self):
        """Test query params with multiple symbols."""
        params = TdxQuantKeyMetricsQueryParams(
            symbol="688318.SH,600519.SH",
            period="annual",
            use_cache=False
        )
        assert params.symbol == "688318.SH,600519.SH"
        assert params.period == "annual"
        assert params.use_cache == False

    def test_default_use_cache(self):
        """Test default use_cache value."""
        params = TdxQuantKeyMetricsQueryParams(symbol="688318.SH")
        assert params.use_cache == True

    def test_default_period(self):
        """Test default period value."""
        params = TdxQuantKeyMetricsQueryParams(symbol="688318.SH")
        assert params.period == "quarter"

    def test_period_choices(self):
        """Test valid period choices."""
        params_quarter = TdxQuantKeyMetricsQueryParams(symbol="688318.SH", period="quarter")
        assert params_quarter.period == "quarter"

        params_annual = TdxQuantKeyMetricsQueryParams(symbol="688318.SH", period="annual")
        assert params_annual.period == "annual"


class TestTdxQuantKeyMetricsData:
    """Test suite for data model."""

    def test_data_validation_with_valid_data(self):
        """Test data model validation with valid input."""
        test_data = {
            "symbol": "688318.SH",
            "period_ending": "2024-03-31",
            "fiscal_year": 2024,
            "fiscal_period": "Q1",
            "currency": "CNY",
            "market_cap": 150000000000.0,
            "pe_ratio": 25.5,
            "forward_pe": 22.3,
            "eps": 2.5,
            "price_to_book": 3.2,
            "book_value_per_share": 15.6,
            "debt_to_equity": 0.45,
            "current_ratio": 1.8,
            "quick_ratio": 1.5,
            "gross_margin": 0.65,
            "profit_margin": 0.22,
            "operating_margin": 0.28,
            "return_on_assets": 0.12,
            "return_on_equity": 0.18,
            "dividend_yield": 0.025,
            "enterprise_value": 160000000000.0,
            "ev_to_sales": 5.5,
            "beta": 1.1,
            "year_high": 50.0,
            "year_low": 35.0,
            "working_capital": 50000000000.0,
            "total_debt": 20000000000.0,
            "operating_cash_flow": 8000000000.0,
            "ebit_margin": 0.30,
            "price_to_sales": 6.0,
            "price_to_cash": 8.5,
            "cash_per_share": 5.2,
        }

        data = TdxQuantKeyMetricsData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.period_ending == date(2024, 3, 31)
        assert data.fiscal_year == 2024
        assert data.fiscal_period == "Q1"
        assert data.currency == "CNY"
        assert data.market_cap == 150000000000.0
        assert data.pe_ratio == 25.5
        assert data.forward_pe == 22.3
        assert data.eps == 2.5
        assert data.price_to_book == 3.2
        assert data.book_value_per_share == 15.6
        assert data.debt_to_equity == 0.45
        assert data.current_ratio == 1.8
        assert data.quick_ratio == 1.5
        assert data.gross_margin == 0.65
        assert data.profit_margin == 0.22
        assert data.operating_margin == 0.28
        assert data.return_on_assets == 0.12
        assert data.return_on_equity == 0.18
        assert data.dividend_yield == 0.025
        assert data.enterprise_value == 160000000000.0
        assert data.ev_to_sales == 5.5
        assert data.beta == 1.1
        assert data.year_high == 50.0
        assert data.year_low == 35.0

    def test_data_validation_with_empty_strings(self):
        """Test data model validation with empty strings.

        Note: In practice, map_tdx_to_openbb returns None (not "") for missing values.
        This test verifies behavior with string fields that don't have validators.
        Fields with explicit field_validators convert "" to None.
        Fields from base class without validators keep "" as "".
        """
        test_data = {
            "symbol": "688318.SH",
            "period_ending": "",
        }

        data = TdxQuantKeyMetricsData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.period_ending is None

    def test_data_validation_with_nan_values(self):
        """Test data model validation with NaN values.

        Note: In practice, map_tdx_to_openbb never returns NaN.
        This test verifies NaN handling for robustness.
        """
        test_data = {
            "symbol": "688318.SH",
            "fiscal_year": float('nan'),
        }

        data = TdxQuantKeyMetricsData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.fiscal_year is None

    def test_data_validation_with_invalid_date(self):
        """Test data model validation with invalid date format."""
        test_data = {
            "symbol": "688318.SH",
            "period_ending": "invalid_date",
        }

        data = TdxQuantKeyMetricsData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.period_ending is None

    def test_data_validation_with_date_object(self):
        """Test data model validation with date object."""
        test_data = {
            "symbol": "688318.SH",
            "period_ending": date(2024, 3, 31),
        }

        data = TdxQuantKeyMetricsData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.period_ending == date(2024, 3, 31)

    def test_field_alias_mapping(self):
        """Test that field aliases are correctly mapped."""
        test_data = {
            "symbol": "688318.SH",
            "market_cap": 150000000000.0,
            "pe_ratio": 25.5,
        }

        data = TdxQuantKeyMetricsData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.market_cap == 150000000000.0
        assert data.pe_ratio == 25.5

    def test_numeric_field_validation_with_string_numbers(self):
        """Test numeric field validation with string numbers.

        Note: Only fields with explicit field_validators handle string-to-float conversion.
        Fields from base class without explicit validators will keep string type.
        This test documents actual behavior.
        """
        test_data = {
            "symbol": "688318.SH",
            "fiscal_year": "2024",
        }

        data = TdxQuantKeyMetricsData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.fiscal_year == 2024

    def test_data_validation_with_datetime_object(self):
        """Test data model validation with datetime object.

        Note: Pydantic v2 requires datetimes to have zero time component for date fields.
        This test verifies the validator strips time component.
        """
        from datetime import datetime
        test_data = {
            "symbol": "688318.SH",
            "period_ending": datetime(2024, 3, 31, 0, 0, 0),
        }

        data = TdxQuantKeyMetricsData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.period_ending == date(2024, 3, 31)


class TestTdxQuantKeyMetricsFetcher:
    """Test suite for fetcher implementation."""

    @pytest.fixture
    def mock_tq(self):
        """Mock TdxQuant API."""
        with patch('tqcenter.tq') as mock:
            yield mock

    @pytest.fixture
    def mock_map_tdx_to_openbb(self):
        """Mock map_tdx_to_openbb function."""
        with patch('openbb_tdx.utils.tdx_key_metrics.map_tdx_to_openbb') as mock:
            yield mock

    def test_transform_query(self):
        """Test query transformation."""
        params = {
            "symbol": "688318.SH",
            "period": "quarter",
            "use_cache": True
        }

        result = TdxQuantKeyMetricsFetcher.transform_query(params)

        assert isinstance(result, TdxQuantKeyMetricsQueryParams)
        assert result.symbol == "688318.SH"
        assert result.period == "quarter"
        assert result.use_cache == True

    @pytest.mark.asyncio
    async def test_extract_data_success(self, mock_tq, mock_map_tdx_to_openbb):
        """Test successful data extraction."""
        mock_map_tdx_to_openbb.return_value = {
            "symbol": "688318.SH",
            "period_ending": "2024-03-31",
            "fiscal_year": 2024,
            "fiscal_period": "Q1",
            "currency": "CNY",
            "market_cap": 150000000000.0,
            "pe_ratio": 25.5,
        }
        mock_tq.initialize.return_value = None
        mock_tq.close.return_value = None

        query = TdxQuantKeyMetricsQueryParams(symbol="688318.SH")

        result = await TdxQuantKeyMetricsFetcher.aextract_data(query, {})

        assert len(result) == 1
        assert result[0]["symbol"] == "688318.SH"
        assert result[0]["pe_ratio"] == 25.5
        mock_map_tdx_to_openbb.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_data_no_data(self, mock_tq, mock_map_tdx_to_openbb):
        """Test data extraction when no data is returned."""
        mock_map_tdx_to_openbb.return_value = None
        mock_tq.initialize.return_value = None
        mock_tq.close.return_value = None

        query = TdxQuantKeyMetricsQueryParams(symbol="INVALID.SH")

        with pytest.raises(Exception):
            await TdxQuantKeyMetricsFetcher.aextract_data(query, {})

    @pytest.mark.asyncio
    async def test_extract_data_multiple_symbols(self, mock_tq, mock_map_tdx_to_openbb):
        """Test data extraction for multiple symbols."""
        def mock_map_side_effect(symbol, auto_connect=True):
            if symbol == "688318.SH":
                return {
                    "symbol": "688318.SH",
                    "period_ending": "2024-03-31",
                    "pe_ratio": 25.5,
                }
            elif symbol == "600519.SH":
                return {
                    "symbol": "600519.SH",
                    "period_ending": "2024-03-31",
                    "pe_ratio": 30.0,
                }
            return None

        mock_map_tdx_to_openbb.side_effect = mock_map_side_effect
        mock_tq.initialize.return_value = None
        mock_tq.close.return_value = None

        query = TdxQuantKeyMetricsQueryParams(symbol="688318.SH,600519.SH")

        result = await TdxQuantKeyMetricsFetcher.aextract_data(query, {})

        assert len(result) == 2
        assert result[0]["symbol"] == "688318.SH"
        assert result[1]["symbol"] == "600519.SH"

    def test_transform_data(self):
        """Test data transformation."""
        query = TdxQuantKeyMetricsQueryParams(symbol="688318.SH")
        raw_data = [
            {
                "symbol": "688318.SH",
                "period_ending": "2024-03-31",
                "fiscal_year": 2024,
                "fiscal_period": "Q1",
                "currency": "CNY",
                "market_cap": 150000000000.0,
                "pe_ratio": 25.5,
            }
        ]

        result = TdxQuantKeyMetricsFetcher.transform_data(query, raw_data)

        assert len(result) == 1
        assert isinstance(result[0], TdxQuantKeyMetricsData)
        assert result[0].symbol == "688318.SH"
        assert result[0].period_ending == date(2024, 3, 31)
        assert result[0].pe_ratio == 25.5


def is_tdxquant_available() -> bool:
    """Check if TdxQuant client is available."""
    try:
        from tqcenter import tq
        import os
        tq.initialize(os.path.abspath(__file__))
        test = tq.get_stock_info(stock_code='000001.SZ', field_list=['Name'])
        tq.close()
        return test is not None and test.get('ErrorId', '1') == '0'
    except Exception:
        return False


class TestIntegration:
    """Integration tests for the complete fetcher workflow."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not is_tdxquant_available(),
        reason="TdxQuant client not available"
    )
    async def test_full_workflow(self):
        """Test complete fetcher workflow with real TdxQuant client."""
        fetcher = TdxQuantKeyMetricsFetcher()
        params = {"symbol": "688318.SH", "period": "quarter"}

        result = await fetcher.fetch_data(params, {})

        assert len(result) > 0
        assert isinstance(result[0], KeyMetricsData)
        assert hasattr(result[0], "symbol")
        assert result[0].symbol is not None
        assert hasattr(result[0], "market_cap")
        assert hasattr(result[0], "pe_ratio")
