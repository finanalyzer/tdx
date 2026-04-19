# Financial Statement Mapping: TDX to OpenBB

## Overview

This document summarizes the mapping between TDX's `get_financial_data` and `get_financial_data_by_date` functions and OpenBB's balance sheet, income statement, and cash flow statement formats.

## Components

### BaseMapper

The `BaseMapper` class provides shared functionality for all statement mappers:
- `get_field_list()`: Get the list of TDX field names (FN codes) for use with `get_financial_data_by_date`
- `convert_date`: Converts TDX dates (YYYYMMDD) to OpenBB format (YYYY-MM-DD)
- `map_fiscal_period`: Derives fiscal quarter from tag_time
- `map_fiscal_year`: Derives fiscal year from tag_time
- `derive_mmdd_from_tag_time`: Derives mmdd parameter from tag_time
- `map_from_get_financial_data_by_date`: Maps nested data from TDX's get_financial_data_by_date function

### get_field_list() Method

Returns the list of TDX field names (FN codes) for use with `get_financial_data_by_date`:

```python
from openbb_tdx.utils.financial_statement_mapping import BalanceSheetMapper

# Get field list for balance sheet
balance_sheet_fields = BalanceSheetMapper.get_field_list()
# Returns: ['FN8', 'FN9', 'FN10', 'FN11', ...] (70 fields)

income_statement_fields = IncomeStatementMapper.get_field_list()
# Returns: ['FN230', 'FN231', 'FN232', ...] (18 fields)

cash_flow_fields = CashFlowStatementMapper.get_field_list()
# Returns: ['FN134', 'FN135', 'FN107', ...] (57 fields)
```

### year and mmdd Parameters

The `year` and `mmdd` parameters are used with `get_financial_data_by_date`:

| Parameter | Description |
|-----------|-------------|
| `year=0, mmdd=0` | Latest financial report |
| `year=0, mmdd<300` | mmdd periods back from latest |
| `year=0, mmdd=331/630/930/1231` | Latest report for that quarter |
| `year=N, mmdd=0` | N years back from current period |

**mmdd values for quarterly reports:**
| mmdd | Quarter | Description |
|------|---------|-------------|
| 331 | Q1 | March 31 (一季报) |
| 630 | Q2 | June 30 (半年报) |
| 930 | Q3 | September 30 (三季报) |
| 1231 | Q4 | December 31 (年报) |

---

## Balance Sheet Mapping

### Field Mappings

| TDX Field | OpenBB Field | Chinese Name | Description |
|-----------|--------------|--------------|-------------|
| `tag_time` | `period_ending` | 报告期 | End of reporting period |
| `announce_time` | `filing_date` | 公告日期 | Filing date |
| `FN8` | `cash_and_cash_equivalents` | 货币资金 | Cash and equivalents |
| `FN9` | `short_term_investments` | 交易性金融资产 | Short-term investments |
| `FN10` | `notes_receivable` | 应收票据 | Notes receivable |
| `FN11` | `accounts_receivable` | 应收账款 | Accounts receivable |
| `FN12` | `prepaid_expenses` | 预付款项 | Prepaid expenses |
| `FN296` | `accounts_receivables` | 应收票据及应收账款 | Receivables |
| `FN13` | `other_receivables` | 其他应收款 | Other receivables |
| `FN14` | `related_party_receivables` | 应收关联公司款 | Related party receivables |
| `FN15` | `interest_receivable` | 应收利息 | Interest receivable |
| `FN16` | `dividends_receivable` | 应收股利 | Dividends receivable |
| `FN17` | `inventory` | 存货 | Inventory |
| `FN18` | `consumptive_biological_assets` | 消耗性生物资产 | Consumptive biological assets |
| `FN19` | `non_current_assets_due_within_one_year` | 一年内到期的非流动资产 | Non-current assets due within one year |
| `FN20` | `other_current_assets` | 其他流动资产 | Other current assets |
| `FN21` | `total_current_assets` | 流动资产合计 | Total current assets |
| `FN22` | `available_for_sale_securities` | 可供出售金融资产 | Available for sale securities |
| `FN23` | `held_to_maturity_investments` | 持有至到期投资 | Held to maturity investments |
| `FN24` | `long_term_receivables` | 长期应收款 | Long-term receivables |
| `FN25` | `long_term_investments` | 长期股权投资 | Long-term investments |
| `FN26` | `investment_property` | 投资性房地产 | Investment property |
| `FN27` | `plant_property_equipment_net` | 固定资产 | Net PPE |
| `FN28` | `construction_in_progress` | 在建工程 | Construction in progress |
| `FN29` | `construction_materials` | 工程物资 | Construction materials |
| `FN30` | `fixed_assets_cleanup` | 固定资产清理 | Fixed assets cleanup |
| `FN31` | `productive_biological_assets` | 生产性生物资产 | Productive biological assets |
| `FN32` | `oil_and_gas_assets` | 油气资产 | Oil and gas assets |
| `FN33` | `intangible_assets` | 无形资产 | Intangible assets |
| `FN34` | `development_costs` | 开发支出 | Development costs |
| `FN35` | `goodwill` | 商誉 | Goodwill |
| `FN36` | `long_term_deferred_expenses` | 长期待摊费用 | Long-term deferred expenses |
| `FN37` | `tax_assets` | 递延所得税资产 | Tax assets |
| `FN38` | `other_non_current_assets` | 其他非流动资产 | Other non-current assets |
| `FN39` | `non_current_assets` | 非流动资产合计 | Total non-current assets |
| `FN40` | `total_assets` | 资产总计 | Total assets |
| `FN295` | `accounts_payable` | 应付票据及应付账款 | Payables |
| `FN41` | `short_term_debt` | 短期借款 | Short-term debt |
| `FN42` | `trading_financial_liabilities` | 交易性金融负债 | Trading financial liabilities |
| `FN43` | `notes_payable` | 应付票据 | Notes payable |
| `FN44` | `accounts_payable_trade` | 应付账款 | Accounts payable trade |
| `FN45` | `advance_from_customers` | 预收款项 | Advance from customers |
| `FN46` | `employee_benefits_payable` | 应付职工薪酬 | Employee benefits payable |
| `FN47` | `taxes_payable` | 应交税费 | Taxes payable |
| `FN48` | `interest_payable` | 应付利息 | Interest payable |
| `FN49` | `dividends_payable` | 应付股利 | Dividends payable |
| `FN50` | `other_payables` | 其他应付款 | Other payables |
| `FN51` | `related_party_payables` | 应付关联公司款 | Related party payables |
| `FN52` | `current_portion_of_long_term_debt` | 一年内到期的非流动负债 | Current portion of long-term debt |
| `FN53` | `other_current_liabilities` | 其他流动负债 | Other current liabilities |
| `FN54` | `total_current_liabilities` | 流动负债合计 | Total current liabilities |
| `FN55` | `long_term_debt` | 长期借款 | Long-term debt |
| `FN56` | `bonds_payable` | 应付债券 | Bonds payable |
| `FN57` | `long_term_payables` | 长期应付款 | Long-term payables |
| `FN58` | `special_payables` | 专项应付款 | Special payables |
| `FN59` | `provisions` | 预计负债 | Provisions |
| `FN60` | `deferred_tax_liabilities_non_current` | 递延所得税负债 | Deferred tax liabilities |
| `FN61` | `other_non_current_liabilities` | 其他非流动负债 | Other non-current liabilities |
| `FN62` | `total_non_current_liabilities` | 非流动负债合计 | Total non-current liabilities |
| `FN63` | `total_liabilities` | 负债合计 | Total liabilities |
| `FN64` | `common_stock` | 实收资本 | Common stock |
| `FN65` | `additional_paid_in_capital` | 资本公积 | Additional paid-in capital |
| `FN66` | `surplus_reserve` | 盈余公积 | Surplus reserve |
| `FN67` | `treasury_stock` | 库存股 | Treasury stock |
| `FN68` | `retained_earnings` | 未分配利润 | Retained earnings |
| `FN69` | `minority_interest` | 少数股东权益 | Minority interest |
| `FN70` | `foreign_currency_translation` | 外币报表折算价差 | Foreign currency translation |
| `FN71` | `non_recurring_items_adjustment` | 非正常经营项目收益调整 | Non-recurring items adjustment |
| `FN72` | `total_common_equity` | 所有者权益合计 | Total equity |
| `FN73` | `total_liabilities_and_shareholders_equity` | 负债和所有者权益合计 | Total liabilities & equity |
| `FN271` | `total_parent_equity` | 归属于母公司股东权益 | Total parent equity |
| `FN298` | `accumulated_other_comprehensive_income` | 其他综合收益 | AOCI |

### Derived Fields

| Field | Calculation | Chinese Name |
|-------|-------------|--------------|
| `cash_and_short_term_investments` | `cash_and_cash_equivalents` + `short_term_investments` | 货币资金及短期投资 |
| `net_receivables` | `accounts_receivables` + `other_receivables` | 应收款项净额 |
| `goodwill_and_intangible_assets` | `goodwill` + `intangible_assets` | 商誉及无形资产 |
| `total_debt` | `short_term_debt` + `long_term_debt` | 总债务 |
| `net_debt` | `total_debt` - `cash_and_cash_equivalents` | 净债务 |
| `total_long_term_debt` | `long_term_debt` + `bonds_payable` | 长期债务总额 |

---

## Income Statement Mapping

### Field Mappings

| TDX Field | OpenBB Field | Chinese Name | Description |
|-----------|--------------|--------------|-------------|
| `tag_time` | `period_ending` | 报告期 | End of reporting period |
| `announce_time` | `filing_date` | 公告日期 | Filing date |
| `FN230` | `revenue` | 营业收入 | Revenue |
| `FN231` | `operating_income` | 营业利润 | Operating income |
| `FN232` | `net_income` | 归属于母公司所有者的净利润 | Net income |
| `FN233` | `net_income_from_continuing_operations` | 扣除非经常性损益后的净利润 | Net income from continuing operations |
| `FN206` | `net_income_attributable_to_common_shareholders` | 扣除非经常性损益后的净利润 | Net income to common |
| `FN134` | `consolidated_net_income` | 净利润 | Consolidated net income |
| `FN1` | `basic_earnings_per_share` | 基本每股收益 | Basic EPS |
| `FN2` | `diluted_earnings_per_share` | 扣除非经常性损益每股收益 | Diluted EPS |
| `FN135` | `depreciation_and_amortization` | 资产减值准备 | Depreciation & amortization |
| `FN207` | `ebit` | 息税前利润 | EBIT |
| `FN208` | `ebitda` | 息税折旧摊销前利润 | EBITDA |
| `FN238` | `weighted_average_basic_shares_outstanding` | 总股本 | Weighted average shares |
| `FN197` | `return_on_equity` | 净资产收益率 | ROE |
| `FN199` | `net_profit_margin` | 销售净利率 | Net profit margin |
| `FN202` | `gross_margin` | 销售毛利率 | Gross margin |
| `FN183` | `revenue_growth` | 营业收入增长率 | Revenue growth |
| `FN184` | `net_income_growth` | 净利润增长率 | Net income growth |
| `FN209` | `ebitda_margin` | EBITDA/营业总收入 | EBITDA margin |

### Derived Fields

| Field | Calculation | Chinese Name |
|-------|-------------|--------------|
| `ebit` | `ebitda` - `depreciation_and_amortization` | 息税前利润 |
| `net_profit_margin` | `net_income` / `revenue` | 销售净利率 |

---

## Cash Flow Statement Mapping

### Field Mappings

| TDX Field | OpenBB Field | Chinese Name | Description |
|-----------|--------------|--------------|-------------|
| `tag_time` | `period_ending` | 报告期 | End of reporting period |
| `announce_time` | `filing_date` | 公告日期 | Filing date |
| `FN134` | `net_income` | 净利润 | Net income |
| `FN135` | `depreciation_and_amortization` | 资产减值准备 | Depreciation & amortization |
| `FN107` | `net_cash_from_operating_activities` | 经营活动产生的现金流量净额 | Cash from operations |
| `FN119` | `net_cash_from_investing_activities` | 投资活动产生的现金流量净额 | Cash from investing |
| `FN128` | `net_cash_from_financing_activities` | 筹资活动产生的现金流量净额 | Cash from financing |
| `FN131` | `net_change_in_cash_and_equivalents` | 现金及现金等价物净增加额 | Net change in cash |
| `FN132` | `cash_at_beginning_of_period` | 期初现金及现金等价物余额 | Cash at start |
| `FN133` | `cash_at_end_of_period` | 期末现金及现金等价物余额 | Cash at end |
| `FN154` | `cash_and_cash_equivalents` | 货币资金 | Cash and cash equivalents |
| `FN155` | `cash_at_beginning_of_period_alt` | 期初现金及现金等价物余额 | Cash at beginning (alt) |
| `FN114` | `capital_expenditure` | 购建固定资产、无形资产和其他长期资产支付的现金 | Capital expenditure |
| `FN98` | `cash_received_from_sales` | 销售商品、提供劳务收到的现金 | Cash received from sales |
| `FN99` | `tax_refunds_received` | 收到的税费返还 | Tax refunds received |
| `FN100` | `other_cash_received_from_operating` | 收到其他与经营活动有关的现金 | Other cash from operating |
| `FN101` | `total_cash_inflows_from_operating` | 经营活动现金流入小计 | Total operating inflows |
| `FN102` | `cash_paid_for_goods` | 购买商品、接受劳务支付的现金 | Cash paid for goods |
| `FN103` | `cash_paid_to_employees` | 支付给职工以及为职工支付的现金 | Cash paid to employees |
| `FN104` | `taxes_paid` | 支付的各项税费 | Taxes paid |
| `FN105` | `other_cash_paid_for_operating` | 支付其他与经营活动有关的现金 | Other cash paid for operating |
| `FN106` | `total_cash_outflows_from_operating` | 经营活动现金流出小计 | Total operating outflows |
| `FN108` | `cash_received_from_disposal_of_investments` | 收回投资收到的现金 | Cash from disposal of investments |
| `FN109` | `investment_income_received` | 取得投资收益收到的现金 | Investment income received |
| `FN110` | `cash_received_from_disposal_of_assets` | 处置固定资产、无形资产和其他长期资产收回的现金净额 | Cash from disposal of assets |
| `FN111` | `cash_received_from_disposal_of_subsidiaires` | 处置子公司及其他营业单位收到的现金净额 | Cash from disposal of subsidiaries |
| `FN112` | `other_cash_received_from_investing` | 收到其他与投资活动有关的现金 | Other cash from investing |
| `FN113` | `total_cash_inflows_from_investing` | 投资活动现金流入小计 | Total investing inflows |
| `FN115` | `cash_paid_for_investments` | 投资支付的现金 | Cash paid for investments |
| `FN116` | `cash_paid_for_acquisition_of_subsidiaries` | 取得子公司及其他营业单位支付的现金净额 | Cash paid for acquisitions |
| `FN117` | `other_cash_paid_for_investing` | 支付其他与投资活动有关的现金 | Other cash paid for investing |
| `FN118` | `total_cash_outflows_from_investing` | 投资活动现金流出小计 | Total investing outflows |
| `FN120` | `cash_received_from_capital_injection` | 吸收投资收到的现金 | Cash from capital injection |
| `FN121` | `cash_received_from_borrowings` | 取得借款收到的现金 | Cash from borrowings |
| `FN122` | `other_cash_received_from_financing` | 收到其他与筹资活动有关的现金 | Other cash from financing |
| `FN123` | `total_cash_inflows_from_financing` | 筹资活动现金流入小计 | Total financing inflows |
| `FN124` | `cash_paid_for_debt_repayment` | 偿还债务支付的现金 | Cash paid for debt repayment |
| `FN125` | `cash_paid_for_dividends_and_interest` | 分配股利、利润或偿付利息支付的现金 | Cash paid for dividends |
| `FN126` | `other_cash_paid_for_financing` | 支付其他与筹资活动有关的现金 | Other cash paid for financing |
| `FN127` | `total_cash_outflows_from_financing` | 筹资活动现金流出小计 | Total financing outflows |
| `FN129` | `effect_of_exchange_rate_changes` | 汇率变动对现金的影响 | Exchange rate effect |
| `FN130` | `other_effects_on_cash` | 其他对现金的影响 | Other effects on cash |
| `FN136` | `impairment_loss` | 资产减值损失 | Impairment loss |
| `FN137` | `amortization_of_intangible_assets` | 无形资产摊销 | Amortization of intangibles |
| `FN138` | `amortization_of_long_term_deferred_expenses` | 长期待摊费用摊销 | Amortization of deferred expenses |
| `FN139` | `loss_on_disposal_of_fixed_assets` | 处置固定资产损失 | Loss on disposal of fixed assets |
| `FN140` | `loss_on_scrapping_of_fixed_assets` | 固定资产报废损失 | Loss on scrapping of fixed assets |
| `FN141` | `loss_on_fair_value_changes` | 公允价值变动损失 | Loss on fair value changes |
| `FN142` | `financial_expenses` | 财务费用 | Financial expenses |
| `FN143` | `investment_loss` | 投资损失 | Investment loss |
| `FN144` | `decrease_in_deferred_tax_assets` | 递延所得税资产减少 | Decrease in deferred tax assets |
| `FN145` | `increase_in_deferred_tax_liabilities` | 递延所得税负债增加 | Increase in deferred tax liabilities |
| `FN146` | `decrease_in_inventory` | 存货的减少 | Decrease in inventory |
| `FN147` | `decrease_in_operating_receivables` | 经营性应收项目的减少 | Decrease in operating receivables |
| `FN148` | `increase_in_operating_payables` | 经营性应付项目的增加 | Increase in operating payables |
| `FN149` | `other_operating_cash_adjustments` | 其他经营性现金调整 | Other operating cash adjustments |
| `FN219` | `cash_flow_per_share` | 每股经营性现金流 | Cash flow per share |
| `FN225` | `net_cash_flow_per_share` | 每股现金流量净额 | Net cash flow per share |
| `FN228` | `ratio_of_operating_cash_to_net_income` | 经营活动现金净流量与净利润比率 | Operating cash to net income ratio |

### Derived Fields

| Field | Calculation | Chinese Name |
|-------|-------------|--------------|
| `operating_cash_flow` | `net_cash_from_operating_activities` | 经营现金流 |
| `free_cash_flow` | `operating_cash_flow` - `capital_expenditure` | 自由现金流 |

---

## Usage Examples

### Get Field Lists for API Calls

```python
from openbb_tdx.utils.financial_statement_mapping import (
    BalanceSheetMapper,
    IncomeStatementMapper,
    CashFlowStatementMapper
)

# Get field lists for get_financial_data_by_date
balance_fields = BalanceSheetMapper.get_field_list()
income_fields = IncomeStatementMapper.get_field_list()
cash_fields = CashFlowStatementMapper.get_field_list()

print(f"Balance sheet: {len(balance_fields)} fields")
print(f"Income statement: {len(income_fields)} fields")
print(f"Cash flow: {len(cash_fields)} fields")
```

### Balance Sheet

```python
from openbb_tdx.utils.financial_statement_mapping import BalanceSheetMapper

tdx_data = {
    'tag_time': 20231231,
    'announce_time': 20240331,
    'FN8': 1000000000.0,
    'FN9': 500000000.0,
    'FN40': 3750000000.0,
}

openbb_balance = BalanceSheetMapper.map_to_openbb(tdx_data, year=2023, mmdd=1231)
# Result includes query_year=2023 and query_mmdd=1231
```

### Income Statement

```python
from openbb_tdx.utils.financial_statement_mapping import IncomeStatementMapper

tdx_data = {
    'tag_time': 20231231,
    'FN230': 383285000000.0,
    'FN134': 96995000000.0,
    'FN1': 6.16,
    'FN2': 6.11,
}

openbb_income = IncomeStatementMapper.map_to_openbb(tdx_data, year=2023, mmdd=1231)
```

### Cash Flow Statement

```python
from openbb_tdx.utils.financial_statement_mapping import CashFlowStatementMapper

tdx_data = {
    'tag_time': 20231231,
    'FN134': 96995000000.0,
    'FN107': 110543000000.0,
    'FN131': -1090000000.0,
}

openbb_cash = CashFlowStatementMapper.map_to_openbb(tdx_data, year=2023, mmdd=1231)
```

### Using get_financial_data_by_date

```python
from tqcenter import tq
from openbb_tdx.utils.financial_statement_mapping import BalanceSheetMapper

# Get field list for balance sheet
balance_fields = BalanceSheetMapper.get_field_list()

# Call TDX API for latest Q4 report
fd = tq.get_financial_data_by_date(
    stock_list=['600519.SH'],
    field_list=balance_fields,
    year=0,      # 0 = latest report
    mmdd=1231    # 1231 = Q4 (Dec 31)
)

# Map to OpenBB format (year and mmdd are preserved in output)
mapped_data = BalanceSheetMapper.map_from_get_financial_data_by_date(
    fd, year=0, mmdd=1231
)

# Access mapped data
stock_data = mapped_data['600519.SH']
print(f"Query year: {stock_data['query_year']}")
print(f"Query mmdd: {stock_data['query_mmdd']}")
print(f"Total assets: {stock_data['total_assets']}")
```

### Derive mmdd from tag_time

```python
from openbb_tdx.utils.financial_statement_mapping import BaseMapper

# Derive mmdd from a date
mmdd = BaseMapper.derive_mmdd_from_tag_time(20231231)
# Returns: 1231

mmdd = BaseMapper.derive_mmdd_from_tag_time(20230630)
# Returns: 630
```

## Output Fields

When using `map_to_openbb()` or `map_from_get_financial_data_by_date()`, the output includes:

| Field | Description |
|-------|-------------|
| `query_year` | The year parameter used in the query |
| `query_mmdd` | The mmdd parameter used in the query |
| `period_ending` | End of reporting period (YYYY-MM-DD) |
| `filing_date` | Filing date (YYYY-MM-DD) |
| `fiscal_period` | Fiscal quarter (Q1, Q2, Q3, Q4) |
| `fiscal_year` | Fiscal year |
| ... | All mapped financial fields |

## Conclusion

This package provides a comprehensive way to convert TDX financial data to OpenBB's format for all three major financial statements. The mappers handle date conversions, field name mappings, derived fields, and nested data structures from both TDX API functions. The `get_field_list()` method simplifies generating field lists for API calls, and the `year`/`mmdd` parameters are preserved in the output for traceability.
