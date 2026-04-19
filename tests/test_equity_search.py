"""Test cases for TdxQuant Equity Search."""

import pytest
import asyncio
import pandas as pd
from unittest.mock import Mock, patch
from openbb_tdx.models.equity_search import TdxQuantEquitySearchFetcher


@pytest.fixture
def mock_get_symbols():
    """Mock get_symbols function for testing"""
    with patch('openbb_tdx.models.equity_search.get_symbols') as mock:
        yield mock


@pytest.mark.asyncio
async def test_basic_search(mock_get_symbols):
    """Test basic search functionality"""
    mock_get_symbols.return_value = pd.DataFrame([
        {'symbol': '000001.SZ', 'name': '平安银行', 'exchange': 'SZSE'},
        {'symbol': '600036.SH', 'name': '招商银行', 'exchange': 'SSE'},
        {'symbol': '601398.SH', 'name': '工商银行', 'exchange': 'SSE'},
    ])
    
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': '银行', 'market': '5', 'list_type': 1, 'use_cache': False}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 3
    assert results[0].symbol == '000001.SZ'
    assert results[0].name == '平安银行'
    assert results[0].exchange == 'SZSE'


@pytest.mark.asyncio
async def test_empty_search(mock_get_symbols):
    """Test empty search functionality"""
    mock_get_symbols.return_value = pd.DataFrame([
        {'symbol': '000001.SZ', 'name': '平安银行', 'exchange': 'SZSE'},
        {'symbol': '000002.SZ', 'name': '万科A', 'exchange': 'SZSE'},
    ])
    
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 1, 'use_cache': False}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 2


@pytest.mark.asyncio
async def test_limit_parameter(mock_get_symbols):
    """Test limit parameter functionality"""
    mock_get_symbols.return_value = pd.DataFrame([
        {'symbol': '000001.SZ', 'name': '平安银行', 'exchange': 'SZSE'},
        {'symbol': '000002.SZ', 'name': '万科A', 'exchange': 'SZSE'},
        {'symbol': '000004.SZ', 'name': '*ST国华', 'exchange': 'SZSE'},
    ])
    
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 1, 'limit': 2, 'use_cache': False}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 2


@pytest.mark.asyncio
async def test_market_filtering(mock_get_symbols):
    """Test market filtering functionality"""
    def mock_symbols_side_effect(use_cache, market, list_type):
        if market == '5':
            return pd.DataFrame([
                {'symbol': '000001.SZ', 'name': '平安银行', 'exchange': 'SZSE'}
            ])
        else:
            return pd.DataFrame([
                {'symbol': '00001.HK', 'name': '长和', 'exchange': 'HKEX'}
            ])
    
    mock_get_symbols.side_effect = mock_symbols_side_effect
    
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 1, 'use_cache': False}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 1
    assert results[0].symbol == '000001.SZ'
    assert results[0].exchange == 'SZSE'

    params = {'query': None, 'market': '102', 'list_type': 1, 'use_cache': False}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 1
    assert results[0].symbol == '00001.HK'
    assert results[0].exchange == 'HKEX'


@pytest.mark.asyncio
async def test_error_handling(mock_get_symbols):
    """Test error handling functionality"""
    # Mock exception
    mock_get_symbols.side_effect = Exception("API Error")
    
    # Test error handling
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 1, 'use_cache': False}
    query = fetcher.transform_query(params)
    
    with pytest.raises(Exception, match="API Error"):
        await fetcher.aextract_data(query, None)


@pytest.mark.asyncio
async def test_symbol_formatting(mock_get_symbols):
    """Test symbol formatting functionality"""
    mock_get_symbols.return_value = pd.DataFrame([
        {'symbol': '000001.SZ', 'name': '平安银行', 'exchange': 'SZSE'},
    ])
    
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': '000001.SZ', 'market': '5', 'list_type': 1, 'use_cache': False}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results_with_suffix = fetcher.transform_data(query, data)
    
    params = {'query': '000001', 'market': '5', 'list_type': 1, 'use_cache': False}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results_without_suffix = fetcher.transform_data(query, data)
    
    assert len(results_with_suffix) == 1
    assert len(results_without_suffix) == 1
    assert results_with_suffix[0].symbol == results_without_suffix[0].symbol


@pytest.mark.asyncio
async def test_list_type_zero(mock_get_symbols):
    """Test list_type=0 functionality"""
    mock_get_symbols.return_value = pd.DataFrame([
        {'symbol': '000001.SZ', 'name': '', 'exchange': 'SZSE'},
        {'symbol': '000002.SZ', 'name': '', 'exchange': 'SZSE'},
    ])
    
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 0, 'use_cache': False}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 2
    assert results[0].symbol == '000001.SZ'
    assert results[0].name == ''
    assert results[1].symbol == '000002.SZ'
    assert results[1].name == ''


class TestIsValidSymbol:
    """Test cases for _is_valid_symbol method."""

    def test_valid_6_digit_symbols(self):
        """Test valid 6-digit numeric symbols."""
        fetcher = TdxQuantEquitySearchFetcher()
        assert fetcher._is_valid_symbol("600519") is True
        assert fetcher._is_valid_symbol("000001") is True
        assert fetcher._is_valid_symbol("123456") is True

    def test_valid_5_digit_symbols(self):
        """Test valid 5-digit numeric symbols."""
        fetcher = TdxQuantEquitySearchFetcher()
        assert fetcher._is_valid_symbol("00700") is True
        assert fetcher._is_valid_symbol("00300") is True
        assert fetcher._is_valid_symbol("12345") is True

    def test_valid_symbols_with_suffix(self):
        """Test valid symbols with market suffixes."""
        fetcher = TdxQuantEquitySearchFetcher()
        assert fetcher._is_valid_symbol("600519.SH") is True
        assert fetcher._is_valid_symbol("600519.SZ") is True
        assert fetcher._is_valid_symbol("00700.HK") is True
        assert fetcher._is_valid_symbol("830001.BJ") is True

    def test_invalid_symbols(self):
        """Test invalid symbol formats."""
        fetcher = TdxQuantEquitySearchFetcher()
        assert fetcher._is_valid_symbol("平安银行") is False
        assert fetcher._is_valid_symbol("") is False
        assert fetcher._is_valid_symbol("600") is False
        assert fetcher._is_valid_symbol("1234567") is False
        assert fetcher._is_valid_symbol("abc123") is False
        assert fetcher._is_valid_symbol("600519.SH.X") is False


class TestTransformQueryMarketDetection:
    """Test cases for market detection in transform_query."""

    def test_6_digit_a_share_symbol(self):
        """Test 6-digit A-share symbol detection."""
        fetcher = TdxQuantEquitySearchFetcher()
        params = fetcher.transform_query({'query': '600519'})
        assert params.market == "5"

    def test_5_digit_hk_symbol(self):
        """Test 5-digit HK symbol detection."""
        fetcher = TdxQuantEquitySearchFetcher()
        params = fetcher.transform_query({'query': '00700'})
        assert params.market == "102"

    def test_symbol_with_sh_suffix(self):
        """Test symbol with .SH suffix."""
        fetcher = TdxQuantEquitySearchFetcher()
        params = fetcher.transform_query({'query': '600519.SH'})
        assert params.market == "5"

    def test_symbol_with_sz_suffix(self):
        """Test symbol with .SZ suffix."""
        fetcher = TdxQuantEquitySearchFetcher()
        params = fetcher.transform_query({'query': '000001.SZ'})
        assert params.market == "5"

    def test_symbol_with_hk_suffix(self):
        """Test symbol with .HK suffix."""
        fetcher = TdxQuantEquitySearchFetcher()
        params = fetcher.transform_query({'query': '00700.HK'})
        assert params.market == "102"

    def test_symbol_with_bj_suffix(self):
        """Test symbol with .BJ suffix."""
        fetcher = TdxQuantEquitySearchFetcher()
        params = fetcher.transform_query({'query': '830001.BJ'})
        assert params.market == "5"

    def test_name_query_uses_default_market(self):
        """Test that name queries use default market."""
        fetcher = TdxQuantEquitySearchFetcher()
        params = fetcher.transform_query({'query': '平安银行'})
        assert params.market == "5"

    def test_empty_query_uses_default_market(self):
        """Test that empty query uses default market."""
        fetcher = TdxQuantEquitySearchFetcher()
        params = fetcher.transform_query({'query': None})
        assert params.market == "5"

    def test_explicit_market_not_overridden(self):
        """Test that explicit market parameter is not overridden."""
        fetcher = TdxQuantEquitySearchFetcher()
        params = fetcher.transform_query({'query': '600519', 'market': '102'})
        assert params.market == "102"