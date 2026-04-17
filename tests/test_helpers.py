"""Test get_exchange_name_from_symbol function."""

from openbb_tdx.utils.helpers import get_exchange_name_from_symbol


def test_get_exchange_name_from_symbol():
    """Test get_exchange_name_from_symbol function."""
    print("Testing get_exchange_name_from_symbol function...\n")
    
    # Test cases
    test_cases = [
        ("000001.SZ", "深圳交易所"),
        ("600000.SH", "上海交易所"),
        ("430047.BJ", "北京交易所"),
        ("00700.HK", "香港交易所"),
        ("AAPL.US", "美国股票"),
    ]
    
    passed = 0
    failed = 0
    
    for symbol, expected_name in test_cases:
        try:
            result = get_exchange_name_from_symbol(symbol)
            if result == expected_name:
                print(f"✓ {symbol} -> {result}")
                passed += 1
            else:
                print(f"✗ {symbol} -> {result} (expected: {expected_name})")
                failed += 1
        except Exception as e:
            print(f"✗ {symbol} -> Error: {e}")
            failed += 1
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed.")


if __name__ == "__main__":
    test_get_exchange_name_from_symbol()
