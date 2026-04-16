import pytest
from openbb_akshare.utils.helpers import get_post_tax_dividend_per_share

@pytest.mark.parametrize(
    "dividend_str,expected",
    [
        # Non-dividend cases
        ("不分红", 0.0),
        ("不分配不转增", 0.0),
        ("转增10股不分配", 0.0),
        ("公司不分红", 0.0),
        ("10送2股", 0.0),
        ("10转5股", 0.0),
        # Direct per-share values
        ("每股0.38港元", 0.38),
        ("每股人民币0.25元", 0.25),
        ("每股派发现金股利0.088332港元", 0.0883),
        ("每股派发现金红利0.1234元", 0.1234),
        # Base-share values
        ("10送1.5股派1.5元", 0.15),
        ("10转5股派1.5元(含税)", 0.15),
        ("10送1股转4股派0.5元(含税)", 0.05),
        ("10派1元", 0.1),
        ("10转10股派1元", 0.1),
        ("10派0.5元", 0.05),
        ("10.00派2.00元", 0.2),
        ("10现金股利1.5元", 0.15),
        ('A股10送3.5股派1.5元,B股10送2.426股派1.04元', 0.15),
        # Complex mixed formats
        ("每股派发现金股利0.088332港元,每10股派送股票股利3股", 0.0883),
        ("每股派发现金红利0.05元，10转10股派1元", 0.05),
        # Unrecognized/edge cases
        ("", 0.0),
        ("未知格式", 0.0),
        ("每10股送3股", 0.0),
    ]
)
def test_get_post_tax_dividend_per_share(dividend_str, expected):
    result = get_post_tax_dividend_per_share(dividend_str)
    assert result == pytest.approx(expected, rel=1e-4)

def test_ak_download(logger):
    from openbb_akshare.utils.helpers import ak_download
    from datetime import date

    symbol = "600036"
    start_date = date(2025, 6, 1)
    end_date = date(2025, 6, 30)

    logger.info(f"Downloading data for {symbol} from {start_date} to {end_date}")
    df = ak_download(symbol, start_date, end_date)
    assert not df.empty

def test_price_performance(logger):
    def get_data(code: str) -> dict:
        import pandas as pd
        from mysharelib.tools import calculate_price_performance, last_closing_day
        from openbb_akshare.utils.helpers import get_list_date, ak_download

        df = ak_download(symbol=code, start_date=get_list_date(code), end_date=last_closing_day())
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return calculate_price_performance(code, df)

    symbols = '601919,600028'
    symbols = symbols.split(",")
    logger.info([get_data(symbol) for symbol in symbols])