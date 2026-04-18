from tqcenter import tq
import traceback

def _safe_float(value, default=0.0):
    """Safely convert a value to float, returning default if conversion fails or value is None."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def _safe_divide(numerator, denominator, default=None):
    """Safely divide two values, returning default if denominator is zero or invalid."""
    try:
        num = _safe_float(numerator, 0.0)
        denom = _safe_float(denominator, 0.0)
        if denom == 0.0:
            return default
        return num / denom
    except ZeroDivisionError:
        return default
    except Exception as e:
        return default

def map_tdx_to_openbb(stock_code, auto_connect=True):
    try:
        if auto_connect:
            try:
                tq.initialize(__file__)
            except Exception:
                pass

        try:
            stock_info = tq.get_stock_info(stock_code=stock_code, field_list=[])
        except Exception as e:
            raise RuntimeError(f"Failed to get stock info for {stock_code}: {e}") from e

        try:
            more_info = tq.get_more_info(stock_code=stock_code, field_list=[])
        except Exception as e:
            raise RuntimeError(f"Failed to get more info for {stock_code}: {e}") from e

        market_cap = _safe_float(more_info.get('Zsz', 0)) * 1000000000

        report_date = more_info.get('ReportDate', '')
        period_ending = None
        fiscal_year = None
        fiscal_period = None

        if report_date and len(report_date) >= 6:
            try:
                period_ending = f"{report_date[:4]}-{report_date[4:6]}-{report_date[6:8]}" if len(report_date) >= 8 else None
                fiscal_year = int(report_date[:4]) if report_date[:4].isdigit() else None
                month = int(report_date[4:6]) if report_date[4:6].isdigit() else None
                if month:
                    if 1 <= month <= 3:
                        fiscal_period = "Q1"
                    elif 4 <= month <= 6:
                        fiscal_period = "Q2"
                    elif 7 <= month <= 9:
                        fiscal_period = "Q3"
                    elif 10 <= month <= 12:
                        fiscal_period = "Q4"
            except (ValueError, IndexError):
                pass

        j_zgb = _safe_float(stock_info.get('J_zgb', 0))
        j_jzc = _safe_float(stock_info.get('J_jzc', 0))
        j_ldfz = _safe_float(stock_info.get('J_ldfz', 0))
        j_ldzc = _safe_float(stock_info.get('J_ldzc', 0))
        j_ch = _safe_float(stock_info.get('J_ch', 0))
        j_yysy = _safe_float(stock_info.get('J_yysy', 0))
        j_yycb = _safe_float(stock_info.get('J_yycb', 0))
        j_yyly = _safe_float(stock_info.get('J_yyly', 0))
        j_tzsy = _safe_float(stock_info.get('J_tzsy', 0))
        j_zzc = _safe_float(stock_info.get('J_zzc', 0))
        j_jly = _safe_float(stock_info.get('J_jly', 0))
        cash_zj = _safe_float(more_info.get('CashZJ', 0))

        cash_per_share = _safe_divide(cash_zj, j_zgb)
        debt_to_equity = _safe_divide(j_ldfz, j_jzc)
        current_ratio = _safe_divide(j_ldzc, j_ldfz)
        quick_ratio = _safe_divide(j_ldzc - j_ch, j_ldfz)
        gross_margin = _safe_divide(j_yysy - j_yycb, j_yysy)
        operating_margin = _safe_divide(j_yyly, j_yysy)
        ebit_margin = _safe_divide(j_yyly - j_tzsy, j_yysy)
        return_on_assets = _safe_divide(j_jly, j_zzc)
        return_on_equity = _safe_divide(j_jly, j_jzc)
        working_capital = j_ldzc - j_ldfz
        price_to_sales = _safe_divide(market_cap, j_yysy)
        price_to_cash = _safe_divide(market_cap, cash_zj)

        total_debt = j_ldfz
        cash_and_equivalents = cash_zj
        enterprise_value = market_cap + total_debt - cash_and_equivalents

        def _get_float_or_none(data, key):
            value = data.get(key)
            if value is None or value == '' or value == '0' or value == 0:
                return None
            try:
                f = float(value)
                return f if f != 0 else None
            except (ValueError, TypeError):
                return None

        currency = "HKD" if stock_code.endswith(".HK") else "CNY"

        mapped_data = {
            "symbol": stock_code,
            "period_ending": period_ending,
            "fiscal_year": fiscal_year,
            "fiscal_period": fiscal_period,
            "currency": currency,
            "market_cap": market_cap if market_cap > 0 else None,
            "pe_ratio": _get_float_or_none(more_info, 'StaticPE_TTM'),
            "forward_pe": _get_float_or_none(more_info, 'DynaPE'),
            "eps": _get_float_or_none(stock_info, 'J_mgsy'),
            "price_to_sales": price_to_sales,
            "price_to_book": _get_float_or_none(more_info, 'PB_MRQ'),
            "book_value_per_share": _get_float_or_none(stock_info, 'J_mgjzc'),
            "price_to_cash": price_to_cash,
            "cash_per_share": cash_per_share,
            "price_to_free_cash_flow": None,
            "debt_to_equity": debt_to_equity,
            "long_term_debt_to_equity": None,
            "quick_ratio": quick_ratio,
            "current_ratio": current_ratio,
            "gross_margin": gross_margin,
            "profit_margin": _safe_divide(_safe_float(stock_info.get('J_jyl', 0)), 100),
            "operating_margin": operating_margin,
            "return_on_assets": return_on_assets,
            "return_on_investment": None,
            "return_on_equity": return_on_equity,
            "payout_ratio": None,
            "dividend_yield": _safe_divide(_safe_float(more_info.get('DYRatio', 0)), 100),
            "enterprise_value": enterprise_value,
            "ev_to_sales": _safe_divide(enterprise_value, j_yysy),
            "ev_to_ebitda": None,
            "beta": _get_float_or_none(more_info, 'BetaValue'),
            "year_high": _get_float_or_none(more_info, 'HisHigh'),
            "year_low": _get_float_or_none(more_info, 'HisLow'),
            "volume_avg": None,
            "working_capital": working_capital,
            "total_debt": total_debt if total_debt != 0 else None,
            "long_term_debt": None,
            "earnings_growth": None,
            "revenue_growth": None,
            "eps_growth": None,
            "operating_cash_flow": _get_float_or_none(stock_info, 'J_jyxjl'),
            "free_cash_flow_to_firm": None,
            "peg_ratio": None,
            "ebit_margin": ebit_margin
        }

        return mapped_data

    except ZeroDivisionError as e:
        raise RuntimeError(
            f"ZeroDivisionError in map_tdx_to_openbb for {stock_code}. "
            f"Traceback:\n{traceback.format_exc()}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Error in map_tdx_to_openbb for {stock_code}: {e.__class__.__name__}: {str(e)}. "
            f"Traceback:\n{traceback.format_exc()}"
        ) from e
    finally:
        if auto_connect:
            try:
                tq.close()
            except Exception:
                pass
