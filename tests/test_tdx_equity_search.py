"""Test cases for TdxQuant Equity Search Utility Functions."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from openbb_tdx.utils.tdx_equity_search import (
    get_symbols,
    get_symbols_df,
    get_name,
    SYMBOLS_TABLE_SCHEMA,
)


class TestGetSymbolsDf:
    """Test cases for get_symbols_df function."""

    @patch('openbb_tdx.utils.tdx_equity_search.tq')
    def test_basic_fetch(self, mock_tq):
        """Test basic symbol fetch."""
        mock_tq.get_stock_list.return_value = [
            {"Code": "000001.SZ", "Name": "平安银行"},
            {"Code": "600000.SH", "Name": "浦发银行"},
        ]

        df = get_symbols_df(market="5", list_type=1)

        assert len(df) == 2
        assert "symbol" in df.columns
        assert "name" in df.columns
        assert "exchange" in df.columns
        assert df.iloc[0]["symbol"] == "000001.SZ"
        assert df.iloc[0]["name"] == "平安银行"
        assert df.iloc[0]["exchange"] == "SZSE"

    @patch('openbb_tdx.utils.tdx_equity_search.tq')
    def test_list_type_zero(self, mock_tq):
        """Test list_type=0 returns codes only."""
        mock_tq.get_stock_list.return_value = ["000001.SZ", "000002.SZ"]

        df = get_symbols_df(market="5", list_type=0)

        assert len(df) == 2
        assert df.iloc[0]["symbol"] == "000001.SZ"
        assert df.iloc[0]["name"] == ""

    @patch('openbb_tdx.utils.tdx_equity_search.tq')
    def test_hk_market(self, mock_tq):
        """Test HK market fetch."""
        mock_tq.get_stock_list.return_value = ["00700.HK"]

        df = get_symbols_df(market="102", list_type=0)

        assert len(df) == 1
        assert df.iloc[0]["symbol"] == "00700.HK"
        assert df.iloc[0]["exchange"] == "HKEX"

    @patch('openbb_tdx.utils.tdx_equity_search.tq', None)
    def test_missing_tqcenter_module(self):
        """Test ImportError when tqcenter is not available."""
        with pytest.raises(ImportError, match="tqcenter module not found"):
            get_symbols_df(market="5")

    @patch('openbb_tdx.utils.tdx_equity_search.tq')
    def test_unknown_exchange_code(self, mock_tq):
        """Test handling of unknown exchange codes."""
        mock_tq.get_stock_list.return_value = ["80011.HK"]

        df = get_symbols_df(market="102", list_type=0)

        assert len(df) == 1
        assert df.iloc[0]["symbol"] == "80011.HK"
        assert df.iloc[0]["exchange"] == ""


class TestGetSymbols:
    """Test cases for get_symbols function."""

    @patch('openbb_tdx.utils.tdx_equity_search.get_symbols_df')
    @patch('openbb_tdx.utils.tdx_equity_search.TableCache')
    def test_use_cache_true_with_cached_data(self, mock_cache_class, mock_get_symbols_df):
        """Test that cached data is returned when available."""
        mock_cache = MagicMock()
        mock_cache.read_dataframe.return_value = pd.DataFrame([
            {"symbol": "000001.SZ", "name": "平安银行", "exchange": "SZSE"},
        ])
        mock_cache_class.return_value = mock_cache

        df = get_symbols(use_cache=True)

        assert len(df) == 1
        assert df.iloc[0]["symbol"] == "000001.SZ"
        mock_get_symbols_df.assert_not_called()

    @patch('openbb_tdx.utils.tdx_equity_search.get_symbols_df')
    @patch('openbb_tdx.utils.tdx_equity_search.TableCache')
    def test_use_cache_true_without_cached_data(self, mock_cache_class, mock_get_symbols_df):
        """Test that data is fetched when cache is empty."""
        mock_cache = MagicMock()
        mock_cache.read_dataframe.return_value = pd.DataFrame()
        mock_cache_class.return_value = mock_cache
        mock_get_symbols_df.return_value = pd.DataFrame([
            {"symbol": "000001.SZ", "name": "平安银行", "exchange": "SZSE"},
        ])

        df = get_symbols(use_cache=True, market="5")

        assert len(df) == 1
        mock_get_symbols_df.assert_called_once_with(market="5", list_type=1)

    @patch('openbb_tdx.utils.tdx_equity_search.get_symbols_df')
    @patch('openbb_tdx.utils.tdx_equity_search.TableCache')
    def test_use_cache_false(self, mock_cache_class, mock_get_symbols_df):
        """Test that cache is bypassed when use_cache=False."""
        mock_cache = MagicMock()
        mock_cache.read_dataframe.return_value = pd.DataFrame([
            {"symbol": "000001.SZ", "name": "平安银行", "exchange": "SZSE"},
        ])
        mock_cache_class.return_value = mock_cache
        mock_get_symbols_df.return_value = pd.DataFrame([
            {"symbol": "600000.SH", "name": "浦发银行", "exchange": "SSE"},
        ])

        df = get_symbols(use_cache=False, market="5")

        assert len(df) == 1
        assert df.iloc[0]["symbol"] == "600000.SH"
        mock_cache.read_dataframe.assert_not_called()

    @patch('openbb_tdx.utils.tdx_equity_search.get_symbols_df')
    @patch('openbb_tdx.utils.tdx_equity_search.TableCache')
    def test_custom_cache_table_name(self, mock_cache_class, mock_get_symbols_df):
        """Test custom cache table name."""
        mock_cache = MagicMock()
        mock_cache.read_dataframe.return_value = pd.DataFrame()
        mock_cache_class.return_value = mock_cache
        mock_get_symbols_df.return_value = pd.DataFrame()

        get_symbols(use_cache=True, cache_table_name="custom_table")

        mock_cache_class.assert_called_once()
        call_kwargs = mock_cache_class.call_args[1]
        assert call_kwargs["table_name"] == "custom_table"


class TestTableSchema:
    """Test cases for table schema."""

    def test_schema_has_required_columns(self):
        """Test that schema has all required columns."""
        assert "symbol" in SYMBOLS_TABLE_SCHEMA
        assert "name" in SYMBOLS_TABLE_SCHEMA
        assert "exchange" in SYMBOLS_TABLE_SCHEMA

    def test_symbol_is_primary_key(self):
        """Test that symbol is the primary key."""
        assert "PRIMARY KEY" in SYMBOLS_TABLE_SCHEMA["symbol"]


class TestGetName:
    """Test cases for get_name function."""

    @patch('openbb_tdx.utils.tdx_equity_search.get_symbols')
    def test_get_name_with_suffix(self, mock_get_symbols):
        """Test getting name with symbol suffix."""
        from openbb_tdx.utils import tdx_equity_search
        tdx_equity_search._SYMBOLS_CACHE = None

        def side_effect(use_cache, market, list_type, cache_table_name=None):
            if market == "5":
                return pd.DataFrame([
                    {"symbol": "000001.SZ", "name": "平安银行", "exchange": "SZSE"},
                    {"symbol": "600000.SH", "name": "浦发银行", "exchange": "SSE"},
                ])
            else:
                return pd.DataFrame()

        mock_get_symbols.side_effect = side_effect

        name = get_name("000001.SZ")

        assert name == "平安银行"
        tdx_equity_search._SYMBOLS_CACHE = None

    @patch('openbb_tdx.utils.tdx_equity_search.get_symbols')
    def test_get_name_without_suffix(self, mock_get_symbols):
        """Test getting name without symbol suffix."""
        from openbb_tdx.utils import tdx_equity_search
        tdx_equity_search._SYMBOLS_CACHE = None

        def side_effect(use_cache, market, list_type, cache_table_name=None):
            if market == "5":
                return pd.DataFrame([
                    {"symbol": "000001.SZ", "name": "平安银行", "exchange": "SZSE"},
                    {"symbol": "600000.SH", "name": "浦发银行", "exchange": "SSE"},
                ])
            else:
                return pd.DataFrame()

        mock_get_symbols.side_effect = side_effect

        name = get_name("000001")

        assert name == "平安银行"
        tdx_equity_search._SYMBOLS_CACHE = None

    def test_get_name_empty_symbol(self):
        """Test empty symbol returns empty string."""
        from openbb_tdx.utils import tdx_equity_search
        original_cache = tdx_equity_search._SYMBOLS_CACHE
        tdx_equity_search._SYMBOLS_CACHE = pd.DataFrame()

        name = get_name("")

        assert name == ""
        tdx_equity_search._SYMBOLS_CACHE = original_cache

    @patch('openbb_tdx.utils.tdx_equity_search.get_symbols')
    def test_get_name_not_found(self, mock_get_symbols):
        """Test not found symbol returns empty string."""
        from openbb_tdx.utils import tdx_equity_search
        tdx_equity_search._SYMBOLS_CACHE = None

        def side_effect(use_cache, market, list_type, cache_table_name=None):
            if market == "5":
                return pd.DataFrame([
                    {"symbol": "000001.SZ", "name": "平安银行", "exchange": "SZSE"},
                ])
            else:
                return pd.DataFrame()

        mock_get_symbols.side_effect = side_effect

        name = get_name("999999")

        assert name == ""
        tdx_equity_search._SYMBOLS_CACHE = None

    @patch('openbb_tdx.utils.tdx_equity_search.get_symbols')
    def test_get_name_with_hk_symbol(self, mock_get_symbols):
        """Test getting name for HK symbol."""
        from openbb_tdx.utils import tdx_equity_search
        tdx_equity_search._SYMBOLS_CACHE = None

        def side_effect(use_cache, market, list_type, cache_table_name=None):
            if market == "5":
                return pd.DataFrame([
                    {"symbol": "000001.SZ", "name": "平安银行", "exchange": "SZSE"},
                ])
            else:
                return pd.DataFrame([
                    {"symbol": "00700.HK", "name": "腾讯控股", "exchange": "HKEX"},
                ])

        mock_get_symbols.side_effect = side_effect

        name = get_name("00700.HK")

        assert name == "腾讯控股"
        tdx_equity_search._SYMBOLS_CACHE = None

    @patch('openbb_tdx.utils.tdx_equity_search.get_symbols')
    def test_get_name_hk_vs_a_share_distinction(self, mock_get_symbols):
        """Test that HK symbol returns HK name even when similar A-share symbol exists."""
        from openbb_tdx.utils import tdx_equity_search
        tdx_equity_search._SYMBOLS_CACHE = None

        def side_effect(use_cache, market, list_type, cache_table_name=None):
            if market == "5":
                return pd.DataFrame([
                    {"symbol": "003000.SZ", "name": "劲仔食品", "exchange": "SZSE"},
                ])
            else:
                return pd.DataFrame([
                    {"symbol": "00300.HK", "name": "美的集团", "exchange": "HKEX"},
                ])

        mock_get_symbols.side_effect = side_effect

        name = get_name("00300.HK")

        assert name == "美的集团"
        tdx_equity_search._SYMBOLS_CACHE = None

    @patch('openbb_tdx.utils.tdx_equity_search.get_symbols')
    def test_get_name_a_share_vs_hk_distinction(self, mock_get_symbols):
        """Test that A-share symbol returns A-share name even when similar HK symbol exists."""
        from openbb_tdx.utils import tdx_equity_search
        tdx_equity_search._SYMBOLS_CACHE = None

        def side_effect(use_cache, market, list_type, cache_table_name=None):
            if market == "5":
                return pd.DataFrame([
                    {"symbol": "003000.SZ", "name": "劲仔食品", "exchange": "SZSE"},
                ])
            else:
                return pd.DataFrame([
                    {"symbol": "00300.HK", "name": "美的集团", "exchange": "HKEX"},
                ])

        mock_get_symbols.side_effect = side_effect

        name = get_name("003000.SZ")

        assert name == "劲仔食品"
        tdx_equity_search._SYMBOLS_CACHE = None
