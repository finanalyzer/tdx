"""Test TdxQuant Constants."""

from openbb_tdx.utils.constants import (
    Market,
    DividendType,
    Period,
    OrderType,
    PriceType,
    Status,
    get_market_from_suffix,
    get_suffix_from_market,
    get_market_name,
    get_exchange_name,
)


def test_market_enum():
    """Test Market enum."""
    assert Market.SZ == 0
    assert Market.SH == 1
    assert Market.BJ == 2
    assert Market.HK == 31
    assert Market.US == 74
    print("✓ Market enum test passed")


def test_dividend_type():
    """Test DividendType constants."""
    assert DividendType.NONE == "none"
    assert DividendType.FRONT == "front"
    assert DividendType.BACK == "back"
    print("✓ DividendType test passed")


def test_period():
    """Test Period constants."""
    assert Period.TICK == "tick"
    assert Period.M1 == "1m"
    assert Period.M5 == "5m"
    assert Period.M15 == "15m"
    assert Period.M30 == "30m"
    assert Period.H1 == "1h"
    assert Period.D1 == "1d"
    assert Period.W1 == "1w"
    assert Period.MON == "1mon"
    assert Period.Q == "1q"
    assert Period.Y == "1y"
    print("✓ Period test passed")


def test_order_type():
    """Test OrderType enum."""
    assert OrderType.STOCK_BUY == 0
    assert OrderType.STOCK_SELL == 1
    assert OrderType.CREDIT_FIN_BUY == 69
    assert OrderType.CREDIT_SLO_SELL == 70
    assert OrderType.ETF_PURCHASE == 45
    assert OrderType.ETF_REDEMPTION == 46
    assert OrderType.FUTURE_OPEN_LONG == 101
    assert OrderType.FUTURE_OPEN_SHORT == 102
    assert OrderType.OPTION_OPEN_LONG == 201
    assert OrderType.OPTION_OPEN_SHORT == 202
    print("✓ OrderType test passed")


def test_price_type():
    """Test PriceType enum."""
    assert PriceType.PRICE_MY == 0
    assert PriceType.PRICE_SJ == 1
    assert PriceType.PRICE_ZTJ == 2
    assert PriceType.PRICE_DTJ == 3
    print("✓ PriceType test passed")


def test_status():
    """Test Status enum."""
    assert Status.WTSTATUS_NULL == 0
    assert Status.WTSTATUS_NOCJ == 1
    assert Status.WTSTATUS_PARTCJ == 2
    assert Status.WTSTATUS_ALLCJ == 3
    assert Status.WTSTATUS_BCBC == 4
    assert Status.WTSTATUS_ALLCD == 5
    print("✓ Status test passed")


def test_market_suffix_mapping():
    """Test market suffix mapping functions."""
    # Test get_suffix_from_market
    assert get_suffix_from_market(Market.SZ) == ".SZ"
    assert get_suffix_from_market(Market.SH) == ".SH"
    assert get_suffix_from_market(Market.HK) == ".HK"
    assert get_suffix_from_market(Market.US) == ".US"
    
    # Test get_market_from_suffix
    assert get_market_from_suffix(".SZ") == Market.SZ
    assert get_market_from_suffix(".SH") == Market.SH
    assert get_market_from_suffix(".HK") == Market.HK
    assert get_market_from_suffix(".US") == Market.US
    
    print("✓ Market suffix mapping test passed")


def test_market_name():
    """Test market name function."""
    assert get_market_name(Market.SZ) == "深圳交易所"
    assert get_market_name(Market.SH) == "上海交易所"
    assert get_market_name(Market.BJ) == "北京交易所"
    assert get_market_name(Market.HK) == "香港交易所"
    assert get_market_name(Market.US) == "美国股票"
    print("✓ Market name test passed")


def test_exchange_name():
    """Test exchange name function."""
    assert get_exchange_name("SZ") == "深圳交易所"
    assert get_exchange_name("SH") == "上海交易所"
    assert get_exchange_name("BJ") == "北京交易所"
    assert get_exchange_name("HK") == "香港交易所"
    assert get_exchange_name("US") == "美国股票"
    print("✓ Exchange name test passed")


if __name__ == "__main__":
    print("Testing TdxQuant Constants...\n")
    
    tests = [
        test_market_enum,
        test_dividend_type,
        test_period,
        test_order_type,
        test_price_type,
        test_status,
        test_market_suffix_mapping,
        test_market_name,
        test_exchange_name,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} failed: {e}")
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed.")
