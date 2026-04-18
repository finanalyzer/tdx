# Comprehensive Mapping: TDX Functions to OpenBB Equity Fundamental Metrics

## 1. Required Data Fields from OpenBB Documentation

The OpenBB `equity.fundamental.metrics` endpoint requires the following key fields:

### Core Identifiers

- symbol
- period_ending
- fiscal_year
- fiscal_period
- currency

### Valuation Metrics

- market_cap
- pe_ratio
- forward_pe
- eps
- price_to_sales
- price_to_book
- book_value_per_share
- price_to_cash
- cash_per_share
- price_to_free_cash_flow
- enterprise_value
- ev_to_sales
- ev_to_ebitda
- peg_ratio

### Financial Health

- debt_to_equity
- long_term_debt_to_equity
- quick_ratio
- current_ratio
- working_capital
- total_debt
- long_term_debt

### Profitability

- gross_margin
- profit_margin
- operating_margin
- ebit_margin
- return_on_assets
- return_on_equity
- return_on_invested_capital

### Growth Metrics

- earnings_growth
- revenue_growth
- eps_growth

### Dividend Metrics

- dividend_yield
- payout_ratio

### Market Metrics

- beta
- year_high
- year_low
- volume_avg

### Cash Flow

- free_cash_flow_to_firm
- operating_cash_flow

## 2. Mapping Between TDX Functions and OpenBB Requirements

### From `get_stock_info`

| OpenBB Field           | TDX Field | Conversion             | Notes                            |
| ---------------------- | --------- | ---------------------- | -------------------------------- |
| symbol                 | N/A       | Input parameter        | Pass directly from input         |
| period_ending          | N/A       | Get from get_more_info | Use ReportDate                   |
| fiscal_year            | N/A       | Get from get_more_info | Extract from ReportDate          |
| fiscal_period          | N/A       | Get from get_more_info | Derive from ReportDate           |
| currency               | N/A       | Default to 'CNY'       | Assume Chinese yuan for A-shares |
| market_cap             | N/A       | Get from get_more_info | Use Zsz                          |
| eps                    | J_mgsy    | Convert to float       | Use annual EPS                   |
| book_value_per_share   | J_mgjzc   | Convert to float       | Use per share book value         |
| cash_per_share         | N/A       | Calculate              | CashZJ / J_zgb                   |
| debt_to_equity         | N/A       | Calculate              | J_ldfz / J_jzc                   |
| current_ratio          | N/A       | Calculate              | J_ldzc / J_ldfz                  |
| gross_margin           | N/A       | Calculate              | (J_yysy - J_yycb) / J_yysy       |
| profit_margin          | J_jyl     | Convert to float       | Already a percentage             |
| return_on_assets       | N/A       | Calculate              | J_jly / J_zzc                    |
| return_on_equity       | N/A       | Calculate              | J_jly / J_jzc                    |
| working_capital        | N/A       | Calculate              | J_ldzc - J_ldfz                  |
| revenue_growth         | N/A       | Default to None        | Not available in TDX             |
| earnings_growth        | N/A       | Default to None        | Not available in TDX             |
| eps_growth             | N/A       | Default to None        | Not available in TDX             |
| payout_ratio           | N/A       | Default to None        | Not available in TDX             |
| free_cash_flow_to_firm | N/A       | Default to None        | Not directly available           |
| operating_cash_flow    | J_jyxjl   | Convert to float       | Operating cash flow              |

### From `get_more_info`

| OpenBB Field               | TDX Field    | Conversion                           | Notes                                |
| -------------------------- | ------------ | ------------------------------------ | ------------------------------------ |
| period_ending              | ReportDate   | Convert string to date               | Format: YYYYMMDD to YYYY-MM-DD       |
| fiscal_year                | ReportDate   | Extract year                         | From ReportDate (YYYYMMDD)           |
| fiscal_period              | ReportDate   | Derive from month                    | 1-3: Q1, 4-6: Q2, 7-9: Q3, 10-12: Q4 |
| market_cap                 | Zsz          | Convert to float (billions to units) | Multiply by 1,000,000,000            |
| pe_ratio                   | StaticPE_TTM | Convert to float                     | Use TTM P/E                          |
| forward_pe                 | DynaPE       | Convert to float                     | Use dynamic P/E                      |
| price_to_book              | PB_MRQ       | Convert to float                     | Use市净率(MRQ)                          |
| dividend_yield             | DYRatio      | Convert to float                     | Already a percentage                 |
| beta                       | BetaValue    | Convert to float                     | Direct mapping                       |
| year_high                  | HisHigh      | Convert to float                     | 52周最高                                |
| year_low                   | HisLow       | Convert to float                     | 52周最低                                |
| volume_avg                 | N/A          | Default to None                      | Not available in TDX                 |
| enterprise_value           | N/A          | Calculate                            | market_cap + total_debt - CashZJ     |
| ev_to_ebitda               | N/A          | Calculate                            | enterprise_value / ebitda            |
| price_to_sales             | N/A          | Calculate                            | market_cap / J_yysy                  |
| price_to_cash              | N/A          | Calculate                            | market_cap / CashZJ                  |
| price_to_free_cash_flow    | N/A          | Default to None                      | Not directly available               |
| long_term_debt_to_equity   | N/A          | Default to None                      | Not available in TDX                 |
| quick_ratio                | N/A          | Calculate                            | (J_ldzc - J_ch) / J_ldfz             |
| operating_margin           | N/A          | Calculate                            | J_yyly / J_yysy                      |
| ebit_margin                | N/A          | Calculate                            | (J_yyly - J_tzsy) / J_yysy           |
| return_on_invested_capital | N/A          | Default to None                      | Not directly available               |
| peg_ratio                  | N/A          | Default to None                      | Not available in TDX                 |
| total_debt                 | N/A          | Default to J_ldfz                    | Use current liabilities as proxy     |
| long_term_debt             | N/A          | Default to None                      | Not available in TDX                 |
| ebitda                     | N/A          | Default to None                      | Not directly available               |

## 3. Data Type Conversions

| TDX Field Type      | OpenBB Field Type | Conversion                                   |
| ------------------- | ----------------- | -------------------------------------------- |
| String (numeric)    | int/float         | Convert using float() or int()               |
| String (date)       | date              | Convert YYYYMMDD to YYYY-MM-DD               |
| String (percentage) | float             | Convert to decimal (divide by 100 if needed) |
| String (currency)   | float             | Convert to appropriate units                 |

## 4. Handling Missing Fields

| Missing Field              | Default Value | Reasoning                                   |
| -------------------------- | ------------- | ------------------------------------------- |
| volume_avg                 | None          | Not available in TDX                        |
| peg_ratio                  | None          | Not available in TDX                        |
| long_term_debt_to_equity   | None          | Not available in TDX                        |
| return_on_invested_capital | None          | Not directly calculable from available data |
| ebitda                     | None          | Not directly available in TDX               |
| price_to_free_cash_flow    | None          | Not directly calculable from available data |
| revenue_growth             | None          | Not available in TDX                        |
| earnings_growth            | None          | Not available in TDX                        |
| eps_growth                 | None          | Not available in TDX                        |
| payout_ratio               | None          | Not available in TDX                        |
| forward_pe                 | None          | Use DynaPE as proxy, but may not be exact   |

## 5. Final Mapped Data Structure

```python
def map_tdx_to_openbb(stock_code):
    # Get data from TDX functions
    stock_info = tq.get_stock_info(stock_code=stock_code, field_list=[])
    more_info = tq.get_more_info(stock_code=stock_code, field_list=[])

    # Calculate market cap in units (from billions)
    market_cap = float(more_info.get('Zsz', 0)) * 1000000000

    # Process report date for fiscal information
    report_date = more_info.get('ReportDate', '')
    period_ending = None
    fiscal_year = None
    fiscal_period = None

    if report_date:
        period_ending = f"{report_date[:4]}-{report_date[4:6]}-{report_date[6:8]}"
        fiscal_year = int(report_date[:4])
        month = int(report_date[4:6])
        if 1 <= month <= 3:
            fiscal_period = "Q1"
        elif 4 <= month <= 6:
            fiscal_period = "Q2"
        elif 7 <= month <= 9:
            fiscal_period = "Q3"
        elif 10 <= month <= 12:
            fiscal_period = "Q4"

    # Calculate derived metrics
    cash_per_share = float(more_info.get('CashZJ', 0)) / float(stock_info.get('J_zgb', 1)) if stock_info.get('J_zgb', '0') != '0' else None
    debt_to_equity = float(stock_info.get('J_ldfz', 0)) / float(stock_info.get('J_jzc', 1)) if stock_info.get('J_jzc', '0') != '0' else None
    current_ratio = float(stock_info.get('J_ldzc', 0)) / float(stock_info.get('J_ldfz', 1)) if stock_info.get('J_ldfz', '0') != '0' else None
    quick_ratio = (float(stock_info.get('J_ldzc', 0)) - float(stock_info.get('J_ch', 0))) / float(stock_info.get('J_ldfz', 1)) if stock_info.get('J_ldfz', '0') != '0' else None
    gross_margin = (float(stock_info.get('J_yysy', 0)) - float(stock_info.get('J_yycb', 0))) / float(stock_info.get('J_yysy', 1)) if stock_info.get('J_yysy', '0') != '0' else None
    operating_margin = float(stock_info.get('J_yyly', 0)) / float(stock_info.get('J_yysy', 1)) if stock_info.get('J_yysy', '0') != '0' else None
    ebit_margin = (float(stock_info.get('J_yyly', 0)) - float(stock_info.get('J_tzsy', 0))) / float(stock_info.get('J_yysy', 1)) if stock_info.get('J_yysy', '0') != '0' else None
    return_on_assets = float(stock_info.get('J_jly', 0)) / float(stock_info.get('J_zzc', 1)) if stock_info.get('J_zzc', '0') != '0' else None
    return_on_equity = float(stock_info.get('J_jly', 0)) / float(stock_info.get('J_jzc', 1)) if stock_info.get('J_jzc', '0') != '0' else None
    working_capital = float(stock_info.get('J_ldzc', 0)) - float(stock_info.get('J_ldfz', 0))
    price_to_sales = market_cap / float(stock_info.get('J_yysy', 1)) if stock_info.get('J_yysy', '0') != '0' else None
    price_to_cash = market_cap / float(more_info.get('CashZJ', 1)) if more_info.get('CashZJ', '0') != '0' else None

    # Calculate enterprise value (simplified)
    total_debt = float(stock_info.get('J_ldfz', 0))
    cash_and_equivalents = float(more_info.get('CashZJ', 0))
    enterprise_value = market_cap + total_debt - cash_and_equivalents

    # Map to OpenBB structure
    mapped_data = {
        "symbol": stock_code,
        "period_ending": period_ending,
        "fiscal_year": fiscal_year,
        "fiscal_period": fiscal_period,
        "currency": "CNY",  # Assume Chinese yuan for A-shares
        "market_cap": market_cap,
        "pe_ratio": float(more_info.get('StaticPE_TTM', 0)) if more_info.get('StaticPE_TTM') != '0' else None,
        "forward_pe": float(more_info.get('DynaPE', 0)) if more_info.get('DynaPE') != '0' else None,
        "eps": float(stock_info.get('J_mgsy', 0)) if stock_info.get('J_mgsy') != '0' else None,
        "price_to_sales": price_to_sales,
        "price_to_book": float(more_info.get('PB_MRQ', 0)) if more_info.get('PB_MRQ') != '0' else None,
        "book_value_per_share": float(stock_info.get('J_mgjzc', 0)) if stock_info.get('J_mgjzc') != '0' else None,
        "price_to_cash": price_to_cash,
        "cash_per_share": cash_per_share,
        "price_to_free_cash_flow": None,  # Not available
        "debt_to_equity": debt_to_equity,
        "long_term_debt_to_equity": None,  # Not available
        "quick_ratio": quick_ratio,
        "current_ratio": current_ratio,
        "gross_margin": gross_margin,
        "profit_margin": float(stock_info.get('J_jyl', 0)) / 100 if stock_info.get('J_jyl') != '0' else None,  # Convert percentage to decimal
        "operating_margin": operating_margin,
        "return_on_assets": return_on_assets,
        "return_on_investment": None,  # Not available
        "return_on_equity": return_on_equity,
        "payout_ratio": None,  # Not available
        "dividend_yield": float(more_info.get('DYRatio', 0)) / 100 if more_info.get('DYRatio') != '0' else None,  # Convert percentage to decimal
        "enterprise_value": enterprise_value,
        "ev_to_sales": enterprise_value / float(stock_info.get('J_yysy', 1)) if stock_info.get('J_yysy', '0') != '0' else None,
        "ev_to_ebitda": None,  # EBITDA not available
        "beta": float(more_info.get('BetaValue', 0)) if more_info.get('BetaValue') != '0' else None,
        "year_high": float(more_info.get('HisHigh', 0)) if more_info.get('HisHigh') != '0' else None,
        "year_low": float(more_info.get('HisLow', 0)) if more_info.get('HisLow') != '0' else None,
        "volume_avg": None,  # Not available
        "working_capital": working_capital,
        "total_debt": total_debt,
        "long_term_debt": None,  # Not available
        "earnings_growth": None,  # Not available
        "revenue_growth": None,  # Not available
        "eps_growth": None,  # Not available
        "operating_cash_flow": float(stock_info.get('J_jyxjl', 0)) if stock_info.get('J_jyxjl') != '0' else None,
        "free_cash_flow_to_firm": None,  # Not available
        "peg_ratio": None,  # Not available
        "ebit_margin": ebit_margin
    }

    return mapped_data
```

## 6. Key Considerations

1. **Data Availability**: Some OpenBB fields are not directly available in TDX data, requiring assumptions or calculations.

2. **Data Type Consistency**: TDX returns most numeric values as strings, requiring conversion to appropriate numeric types.

3. **Calculation Methods**: For derived metrics, we use simplified calculations based on available data.

4. **Currency Handling**: We assume CNY for A-shares, but this should be adjusted based on the actual stock exchange.

5. **Missing Data**: For unavailable fields, we use None as the default value, which aligns with OpenBB's nullable field approach.

6. **Fiscal Period Handling**: We derive fiscal period from the report date month, assuming a calendar year fiscal period. For companies with different fiscal years, this may need adjustment.

This mapping provides a comprehensive approach to align TDX function outputs with OpenBB's equity fundamental metrics requirements, ensuring compatibility while handling data limitations appropriately.