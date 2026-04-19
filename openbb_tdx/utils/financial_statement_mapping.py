# Financial Statement Mapping: TDX to OpenBB

"""
This script maps the output of TDX's get_financial_data and get_financial_data_by_date
functions to OpenBB's balance sheet, income statement, and cash flow statement formats.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from mysharelib.tools import setup_logger
from openbb_tdx import project_name

# Setup logger
setup_logger(project_name)
logger = logging.getLogger(__name__)

class BaseMapper:
    """Base class for financial statement mappers."""
    
    FIELD_MAPPING: Dict[str, str] = {}
    
    @classmethod
    def get_field_list(cls, exclude_date_fields: bool = True) -> List[str]:
        """
        Get the list of TDX field names (FN codes) for use with get_financial_data_by_date.
        
        Parameters
        ----------
        exclude_date_fields : bool
            If True, exclude 'tag_time' and 'announce_time' from the field list.
            These are not needed when calling get_financial_data_by_date as they
            are determined by the year and mmdd parameters.
        
        Returns
        -------
        List[str]
            List of TDX field names (e.g., ['FN8', 'FN9', 'FN10', ...])
        
        Examples
        --------
        >>> fields = BalanceSheetMapper.get_field_list()
        >>> fd = tq.get_financial_data_by_date(
        ...     stock_list=['600519.SH'],
        ...     field_list=fields,
        ...     year=0,
        ...     mmdd=0
        ... )
        """
        fields = []
        for tdx_field in cls.FIELD_MAPPING.keys():
            if exclude_date_fields and tdx_field in ['tag_time', 'announce_time']:
                continue
            fields.append(tdx_field)
        return fields
    
    @staticmethod
    def convert_date(tdx_date: Any) -> Optional[str]:
        """Convert TDX date format (YYYYMMDD) to ISO date format (YYYY-MM-DD)."""
        if not tdx_date:
            return None
        try:
            date_str = str(tdx_date)
            date_str = ''.join(filter(str.isdigit, date_str))
            if len(date_str) == 8:
                return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            pass
        return None

    @staticmethod
    def map_fiscal_period(tag_time: Any) -> Optional[str]:
        """Derive fiscal period from tag_time."""
        if not tag_time:
            return None
        try:
            date_str = str(tag_time)
            date_str = ''.join(filter(str.isdigit, date_str))
            if len(date_str) == 8:
                month = int(date_str[4:6])
                quarter = (month - 1) // 3 + 1
                return f'Q{quarter}'
        except (ValueError, TypeError):
            pass
        return None

    @staticmethod
    def map_fiscal_year(tag_time: Any) -> Optional[int]:
        """Derive fiscal year from tag_time."""
        if not tag_time:
            return None
        try:
            date_str = str(tag_time)
            date_str = ''.join(filter(str.isdigit, date_str))
            if len(date_str) == 8:
                return int(date_str[:4])
        except (ValueError, TypeError):
            pass
        return None

    @staticmethod
    def derive_mmdd_from_tag_time(tag_time: Any) -> int:
        """
        Derive mmdd parameter from tag_time for use with get_financial_data_by_date.
        
        Parameters
        ----------
        tag_time : Any
            TDX date in YYYYMMDD format
            
        Returns
        -------
        int
            mmdd value (e.g., 331, 630, 930, 1231 for quarterly reports)
        """
        if not tag_time:
            return 0
        try:
            date_str = str(tag_time)
            date_str = ''.join(filter(str.isdigit, date_str))
            if len(date_str) == 8:
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                return month * 100 + day
        except (ValueError, TypeError):
            pass
        return 0

    @staticmethod
    def get_latest_fiscal_info() -> Dict[str, Any]:
        """
        Get the latest fiscal period information based on current date.
        
        Returns
        -------
        Dict[str, Any]
            Dictionary with 'fiscal_year', 'fiscal_period', 'mmdd', and 'period_ending'
            
        Notes
        -----
        - If current date is before April 30, latest report is Q4 of previous year
        - If current date is before August 31, latest report is Q1 of current year
        - If current date is before October 31, latest report is Q2 of current year
        - Otherwise, latest report is Q3 of current year
        """
        today = datetime.now()
        current_year = today.year
        current_month = today.month
        current_day = today.day
        
        if current_month < 5:
            fiscal_year = current_year - 1
            fiscal_period = 'Q4'
            mmdd = 1231
            period_ending = f"{fiscal_year}-12-31"
        elif current_month < 9 or (current_month == 8 and current_day < 31):
            fiscal_year = current_year
            fiscal_period = 'Q1'
            mmdd = 331
            period_ending = f"{fiscal_year}-03-31"
        elif current_month < 11 or (current_month == 10 and current_day < 31):
            fiscal_year = current_year
            fiscal_period = 'Q2'
            mmdd = 630
            period_ending = f"{fiscal_year}-06-30"
        else:
            fiscal_year = current_year
            fiscal_period = 'Q3'
            mmdd = 930
            period_ending = f"{fiscal_year}-09-30"
        
        return {
            'fiscal_year': fiscal_year,
            'fiscal_period': fiscal_period,
            'mmdd': mmdd,
            'period_ending': period_ending
        }

    @staticmethod
    def get_fiscal_info_from_mmdd(year: int, mmdd: int) -> Dict[str, Any]:
        """
        Derive fiscal period information from year and mmdd parameters.
        
        Parameters
        ----------
        year : int
            The year parameter (e.g., 2024)
        mmdd : int
            The month-day parameter:
            - 331: Q1 (March 31)
            - 630: Q2 (June 30)
            - 930: Q3 (September 30)
            - 1231: Q4 (December 31)
            
        Returns
        -------
        Dict[str, Any]
            Dictionary with 'fiscal_year', 'fiscal_period', 'mmdd', and 'period_ending'
        """
        valid_mmdd_values = [331, 630, 930, 1231]
        
        if year < 0:
            logger.error(f"Invalid year value: {year}. Year must be a non-negative integer.")
        
        if mmdd not in valid_mmdd_values:
            logger.error(
                f"Invalid mmdd value: {mmdd}. Valid values are: "
                f"331 (Q1), 630 (Q2), 930 (Q3), 1231 (Q4)."
            )
        
        if mmdd == 331:
            fiscal_period = 'Q1'
            period_ending = f"{year}-03-31"
        elif mmdd == 630:
            fiscal_period = 'Q2'
            period_ending = f"{year}-06-30"
        elif mmdd == 930:
            fiscal_period = 'Q3'
            period_ending = f"{year}-09-30"
        elif mmdd == 1231:
            fiscal_period = 'Q4'
            period_ending = f"{year}-12-31"
        else:
            fiscal_period = None
            period_ending = None
        
        return {
            'fiscal_year': year,
            'fiscal_period': fiscal_period,
            'mmdd': mmdd,
            'period_ending': period_ending
        }

    @classmethod
    def map_from_get_financial_data_by_date(
        cls, 
        tdx_data: Dict[str, Dict[str, Any]], 
        year: int = 0, 
        mmdd: int = 0
    ) -> Dict[str, Dict[str, Any]]:
        """
        Map data from get_financial_data_by_date output to OpenBB format.
        
        Parameters
        ----------
        tdx_data : Dict[str, Dict[str, Any]]
            Raw data from TDX get_financial_data_by_date function
        year : int
            The year parameter used in the query:
            - If 0 and mmdd is 0: latest report
            - If 0 and mmdd < 300: mmdd periods back from latest
            - If 0 and mmdd is 331/630/930/1231: latest report for that quarter
            - If non-zero: that many years back from current period
        mmdd : int
            The month-day parameter used in the query:
            - 331: Q1 (March 31)
            - 630: Q2 (June 30)
            - 930: Q3 (September 30)
            - 1231: Q4 (December 31)
        
        Returns
        -------
        Dict[str, Dict[str, Any]]
            Mapped data with OpenBB field names, including year and mmdd info
        """
        mapped_data = {}
        for stock_code, stock_data in tdx_data.items():
            converted_data = {}
            for key, value in stock_data.items():
                if key in ['tag_time', 'announce_time']:
                    converted_data[key] = cls.convert_date(value)
                else:
                    try:
                        if isinstance(value, str):
                            converted_value = float(value)
                            converted_data[key] = int(converted_value) if converted_value.is_integer() else converted_value
                        else:
                            converted_data[key] = value
                    except (ValueError, TypeError):
                        converted_data[key] = value
            mapped_data[stock_code] = cls.map_to_openbb(converted_data, year=year, mmdd=mmdd)
        return mapped_data


class BalanceSheetMapper(BaseMapper):
    """Maps TDX financial data to OpenBB balance sheet format."""
    
    FIELD_MAPPING = {
        'tag_time': 'period_ending',
        'announce_time': 'filing_date',
        
        'FN8': 'cash_and_cash_equivalents',
        'FN9': 'short_term_investments',
        'FN10': 'notes_receivable',
        'FN11': 'accounts_receivable',
        'FN12': 'prepaid_expenses',
        'FN296': 'accounts_receivables',
        'FN13': 'other_receivables',
        'FN14': 'related_party_receivables',
        'FN15': 'interest_receivable',
        'FN16': 'dividends_receivable',
        'FN17': 'inventory',
        'FN18': 'consumptive_biological_assets',
        'FN19': 'non_current_assets_due_within_one_year',
        'FN20': 'other_current_assets',
        'FN21': 'total_current_assets',
        
        'FN22': 'available_for_sale_securities',
        'FN23': 'held_to_maturity_investments',
        'FN24': 'long_term_receivables',
        'FN25': 'long_term_investments',
        'FN26': 'investment_property',
        'FN27': 'plant_property_equipment_net',
        'FN28': 'construction_in_progress',
        'FN29': 'construction_materials',
        'FN30': 'fixed_assets_cleanup',
        'FN31': 'productive_biological_assets',
        'FN32': 'oil_and_gas_assets',
        'FN33': 'intangible_assets',
        'FN34': 'development_costs',
        'FN35': 'goodwill',
        'FN36': 'long_term_deferred_expenses',
        'FN37': 'tax_assets',
        'FN38': 'other_non_current_assets',
        'FN39': 'non_current_assets',
        'FN40': 'total_assets',
        
        'FN295': 'accounts_payable',
        'FN41': 'short_term_debt',
        'FN42': 'trading_financial_liabilities',
        'FN43': 'notes_payable',
        'FN44': 'accounts_payable_trade',
        'FN45': 'advance_from_customers',
        'FN46': 'employee_benefits_payable',
        'FN47': 'taxes_payable',
        'FN48': 'interest_payable',
        'FN49': 'dividends_payable',
        'FN50': 'other_payables',
        'FN51': 'related_party_payables',
        'FN52': 'current_portion_of_long_term_debt',
        'FN53': 'other_current_liabilities',
        'FN54': 'total_current_liabilities',
        
        'FN55': 'long_term_debt',
        'FN56': 'bonds_payable',
        'FN57': 'long_term_payables',
        'FN58': 'special_payables',
        'FN59': 'provisions',
        'FN60': 'deferred_tax_liabilities_non_current',
        'FN61': 'other_non_current_liabilities',
        'FN62': 'total_non_current_liabilities',
        'FN63': 'total_liabilities',
        
        'FN64': 'common_stock',
        'FN65': 'additional_paid_in_capital',
        'FN66': 'surplus_reserve',
        'FN67': 'treasury_stock',
        'FN68': 'retained_earnings',
        'FN69': 'minority_interest',
        'FN70': 'foreign_currency_translation',
        'FN71': 'non_recurring_items_adjustment',
        'FN72': 'total_common_equity',
        'FN73': 'total_liabilities_and_shareholders_equity',
        'FN271': 'total_parent_equity',
        'FN298': 'accumulated_other_comprehensive_income',
    }

    CHINESE_FIELD_NAMES = {
        'cash_and_cash_equivalents': '货币资金',
        'short_term_investments': '交易性金融资产',
        'notes_receivable': '应收票据',
        'accounts_receivable': '应收账款',
        'prepaid_expenses': '预付款项',
        'accounts_receivables': '应收票据及应收账款',
        'other_receivables': '其他应收款',
        'inventory': '存货',
        'total_current_assets': '流动资产合计',
        'plant_property_equipment_net': '固定资产',
        'goodwill': '商誉',
        'intangible_assets': '无形资产',
        'long_term_investments': '长期股权投资',
        'non_current_assets': '非流动资产合计',
        'total_assets': '资产总计',
        'short_term_debt': '短期借款',
        'accounts_payable': '应付票据及应付账款',
        'total_current_liabilities': '流动负债合计',
        'long_term_debt': '长期借款',
        'bonds_payable': '应付债券',
        'total_non_current_liabilities': '非流动负债合计',
        'total_liabilities': '负债合计',
        'common_stock': '实收资本',
        'retained_earnings': '未分配利润',
        'total_common_equity': '所有者权益合计',
        'total_liabilities_and_shareholders_equity': '负债和所有者权益合计',
    }

    @classmethod
    def map_to_openbb(cls, tdx_data: Dict[str, Any], year: int = 0, mmdd: int = 0) -> Dict[str, Any]:
        """
        Map TDX data to OpenBB balance sheet format.
        
        Parameters
        ----------
        tdx_data : Dict[str, Any]
            Raw TDX financial data
        year : int
            The year parameter used in the query (for get_financial_data_by_date)
        mmdd : int
            The mmdd parameter used in the query (for get_financial_data_by_date)
            
        Returns
        -------
        Dict[str, Any]
            Mapped data with OpenBB field names
        """
        openbb_data = {}
        
        openbb_data['query_year'] = year
        openbb_data['query_mmdd'] = mmdd
        
        for tdx_field, openbb_field in cls.FIELD_MAPPING.items():
            if tdx_field in tdx_data:
                if tdx_field in ['tag_time', 'announce_time']:
                    openbb_data[openbb_field] = cls.convert_date(tdx_data[tdx_field])
                else:
                    openbb_data[openbb_field] = tdx_data[tdx_field]
        
        if 'tag_time' in tdx_data:
            if 'fiscal_period' not in openbb_data:
                openbb_data['fiscal_period'] = cls.map_fiscal_period(tdx_data['tag_time'])
            if 'fiscal_year' not in openbb_data:
                openbb_data['fiscal_year'] = cls.map_fiscal_year(tdx_data['tag_time'])
        elif year == 0 and mmdd == 0:
            latest_info = cls.get_latest_fiscal_info()
            if 'period_ending' not in openbb_data:
                openbb_data['period_ending'] = latest_info['period_ending']
            if 'fiscal_period' not in openbb_data:
                openbb_data['fiscal_period'] = latest_info['fiscal_period']
            if 'fiscal_year' not in openbb_data:
                openbb_data['fiscal_year'] = latest_info['fiscal_year']
        elif year > 0 and mmdd in [331, 630, 930, 1231]:
            fiscal_info = cls.get_fiscal_info_from_mmdd(year, mmdd)
            if 'period_ending' not in openbb_data:
                openbb_data['period_ending'] = fiscal_info['period_ending']
            if 'fiscal_period' not in openbb_data:
                openbb_data['fiscal_period'] = fiscal_info['fiscal_period']
            if 'fiscal_year' not in openbb_data:
                openbb_data['fiscal_year'] = fiscal_info['fiscal_year']
        else:
            logger.warning(
                f"Unable to derive fiscal period from year={year}, mmdd={mmdd}. "
                f"Valid mmdd values are: 331 (Q1), 630 (Q2), 930 (Q3), 1231 (Q4). "
                f"Use year=0, mmdd=0 for latest report."
            )
        
        if 'cash_and_cash_equivalents' in openbb_data and 'short_term_investments' in openbb_data:
            openbb_data['cash_and_short_term_investments'] = (
                openbb_data['cash_and_cash_equivalents'] + openbb_data['short_term_investments']
            )
        
        if 'accounts_receivables' in openbb_data and 'other_receivables' in openbb_data:
            openbb_data['net_receivables'] = (
                openbb_data['accounts_receivables'] + openbb_data['other_receivables']
            )
        
        if 'goodwill' in openbb_data and 'intangible_assets' in openbb_data:
            openbb_data['goodwill_and_intangible_assets'] = (
                openbb_data['goodwill'] + openbb_data['intangible_assets']
            )
        
        if 'short_term_debt' in openbb_data and 'long_term_debt' in openbb_data:
            openbb_data['total_debt'] = (
                openbb_data['short_term_debt'] + openbb_data['long_term_debt']
            )
        
        if 'total_debt' in openbb_data and 'cash_and_cash_equivalents' in openbb_data:
            openbb_data['net_debt'] = (
                openbb_data['total_debt'] - openbb_data['cash_and_cash_equivalents']
            )
        
        if 'bonds_payable' in openbb_data and 'long_term_debt' in openbb_data:
            if 'total_debt' not in openbb_data:
                openbb_data['total_debt'] = openbb_data['long_term_debt']
            openbb_data['total_long_term_debt'] = (
                openbb_data['long_term_debt'] + openbb_data['bonds_payable']
            )
        
        required_fields = [
            'period_ending', 'fiscal_period', 'fiscal_year',
            'cash_and_cash_equivalents', 'total_current_assets',
            'total_assets', 'total_current_liabilities',
            'total_liabilities', 'total_common_equity',
            'total_liabilities_and_shareholders_equity'
        ]
        
        for field in required_fields:
            if field not in openbb_data:
                openbb_data[field] = None
        
        return openbb_data


class IncomeStatementMapper(BaseMapper):
    """Maps TDX financial data to OpenBB income statement format."""
    
    FIELD_MAPPING = {
        'tag_time': 'period_ending',
        'announce_time': 'filing_date',
        
        'FN230': 'revenue',
        'FN231': 'operating_income',
        'FN232': 'net_income',
        'FN233': 'net_income_from_continuing_operations',
        'FN206': 'net_income_attributable_to_common_shareholders',
        'FN134': 'consolidated_net_income',
        
        'FN1': 'basic_earnings_per_share',
        'FN2': 'diluted_earnings_per_share',
        
        'FN135': 'depreciation_and_amortization',
        
        'FN207': 'ebit',
        'FN208': 'ebitda',
        
        'FN238': 'weighted_average_basic_shares_outstanding',
        
        'FN197': 'return_on_equity',
        'FN199': 'net_profit_margin',
        'FN202': 'gross_margin',
        'FN183': 'revenue_growth',
        'FN184': 'net_income_growth',
        'FN209': 'ebitda_margin',
    }

    CHINESE_FIELD_NAMES = {
        'revenue': '营业收入',
        'operating_income': '营业利润',
        'net_income': '归属于母公司所有者的净利润',
        'net_income_from_continuing_operations': '扣除非经常性损益后的净利润',
        'net_income_attributable_to_common_shareholders': '扣除非经常性损益后的净利润',
        'consolidated_net_income': '净利润',
        'basic_earnings_per_share': '基本每股收益',
        'diluted_earnings_per_share': '扣除非经常性损益每股收益',
        'ebit': '息税前利润',
        'ebitda': '息税折旧摊销前利润',
        'depreciation_and_amortization': '资产减值准备',
        'weighted_average_basic_shares_outstanding': '总股本',
    }

    @classmethod
    def map_to_openbb(cls, tdx_data: Dict[str, Any], year: int = 0, mmdd: int = 0) -> Dict[str, Any]:
        """
        Map TDX data to OpenBB income statement format.
        
        Parameters
        ----------
        tdx_data : Dict[str, Any]
            Raw TDX financial data
        year : int
            The year parameter used in the query (for get_financial_data_by_date)
        mmdd : int
            The mmdd parameter used in the query (for get_financial_data_by_date)
            
        Returns
        -------
        Dict[str, Any]
            Mapped data with OpenBB field names
        """
        openbb_data = {}
        
        openbb_data['query_year'] = year
        openbb_data['query_mmdd'] = mmdd
        
        for tdx_field, openbb_field in cls.FIELD_MAPPING.items():
            if tdx_field in tdx_data:
                if tdx_field in ['tag_time', 'announce_time']:
                    openbb_data[openbb_field] = cls.convert_date(tdx_data[tdx_field])
                else:
                    openbb_data[openbb_field] = tdx_data[tdx_field]
        
        if 'tag_time' in tdx_data:
            if 'fiscal_period' not in openbb_data:
                openbb_data['fiscal_period'] = cls.map_fiscal_period(tdx_data['tag_time'])
            if 'fiscal_year' not in openbb_data:
                openbb_data['fiscal_year'] = cls.map_fiscal_year(tdx_data['tag_time'])
        elif year == 0 and mmdd == 0:
            latest_info = cls.get_latest_fiscal_info()
            if 'period_ending' not in openbb_data:
                openbb_data['period_ending'] = latest_info['period_ending']
            if 'fiscal_period' not in openbb_data:
                openbb_data['fiscal_period'] = latest_info['fiscal_period']
            if 'fiscal_year' not in openbb_data:
                openbb_data['fiscal_year'] = latest_info['fiscal_year']
        elif year > 0 and mmdd in [331, 630, 930, 1231]:
            fiscal_info = cls.get_fiscal_info_from_mmdd(year, mmdd)
            if 'period_ending' not in openbb_data:
                openbb_data['period_ending'] = fiscal_info['period_ending']
            if 'fiscal_period' not in openbb_data:
                openbb_data['fiscal_period'] = fiscal_info['fiscal_period']
            if 'fiscal_year' not in openbb_data:
                openbb_data['fiscal_year'] = fiscal_info['fiscal_year']
        else:
            logger.warning(
                f"Unable to derive fiscal period from year={year}, mmdd={mmdd}. "
                f"Valid mmdd values are: 331 (Q1), 630 (Q2), 930 (Q3), 1231 (Q4). "
                f"Use year=0, mmdd=0 for latest report."
            )
        
        if 'ebitda' in openbb_data and 'depreciation_and_amortization' in openbb_data:
            if 'ebit' not in openbb_data:
                openbb_data['ebit'] = openbb_data['ebitda'] - openbb_data['depreciation_and_amortization']
        
        if 'revenue' in openbb_data and 'net_income' in openbb_data:
            if openbb_data['revenue'] and openbb_data['revenue'] != 0:
                openbb_data['net_profit_margin'] = openbb_data['net_income'] / openbb_data['revenue']
        
        required_fields = [
            'period_ending', 'fiscal_period', 'fiscal_year',
            'revenue', 'net_income',
            'basic_earnings_per_share', 'diluted_earnings_per_share'
        ]
        
        for field in required_fields:
            if field not in openbb_data:
                openbb_data[field] = None
        
        return openbb_data


class CashFlowStatementMapper(BaseMapper):
    """Maps TDX financial data to OpenBB cash flow statement format."""
    
    FIELD_MAPPING = {
        'tag_time': 'period_ending',
        'announce_time': 'filing_date',
        
        'FN134': 'net_income',
        'FN135': 'depreciation_and_amortization',
        
        'FN107': 'net_cash_from_operating_activities',
        'FN119': 'net_cash_from_investing_activities',
        'FN128': 'net_cash_from_financing_activities',
        
        'FN131': 'net_change_in_cash_and_equivalents',
        'FN132': 'cash_at_beginning_of_period',
        'FN133': 'cash_at_end_of_period',
        
        'FN154': 'cash_and_cash_equivalents',
        'FN155': 'cash_at_beginning_of_period_alt',
        
        'FN114': 'capital_expenditure',
        
        'FN98': 'cash_received_from_sales',
        'FN99': 'tax_refunds_received',
        'FN100': 'other_cash_received_from_operating',
        'FN101': 'total_cash_inflows_from_operating',
        'FN102': 'cash_paid_for_goods',
        'FN103': 'cash_paid_to_employees',
        'FN104': 'taxes_paid',
        'FN105': 'other_cash_paid_for_operating',
        'FN106': 'total_cash_outflows_from_operating',
        
        'FN108': 'cash_received_from_disposal_of_investments',
        'FN109': 'investment_income_received',
        'FN110': 'cash_received_from_disposal_of_assets',
        'FN111': 'cash_received_from_disposal_of_subsidiaires',
        'FN112': 'other_cash_received_from_investing',
        'FN113': 'total_cash_inflows_from_investing',
        'FN115': 'cash_paid_for_investments',
        'FN116': 'cash_paid_for_acquisition_of_subsidiaries',
        'FN117': 'other_cash_paid_for_investing',
        'FN118': 'total_cash_outflows_from_investing',
        
        'FN120': 'cash_received_from_capital_injection',
        'FN121': 'cash_received_from_borrowings',
        'FN122': 'other_cash_received_from_financing',
        'FN123': 'total_cash_inflows_from_financing',
        'FN124': 'cash_paid_for_debt_repayment',
        'FN125': 'cash_paid_for_dividends_and_interest',
        'FN126': 'other_cash_paid_for_financing',
        'FN127': 'total_cash_outflows_from_financing',
        
        'FN129': 'effect_of_exchange_rate_changes',
        'FN130': 'other_effects_on_cash',
        
        'FN136': 'impairment_loss',
        'FN137': 'amortization_of_intangible_assets',
        'FN138': 'amortization_of_long_term_deferred_expenses',
        'FN139': 'loss_on_disposal_of_fixed_assets',
        'FN140': 'loss_on_scrapping_of_fixed_assets',
        'FN141': 'loss_on_fair_value_changes',
        'FN142': 'financial_expenses',
        'FN143': 'investment_loss',
        'FN144': 'decrease_in_deferred_tax_assets',
        'FN145': 'increase_in_deferred_tax_liabilities',
        'FN146': 'decrease_in_inventory',
        'FN147': 'decrease_in_operating_receivables',
        'FN148': 'increase_in_operating_payables',
        'FN149': 'other_operating_cash_adjustments',
        
        'FN219': 'cash_flow_per_share',
        'FN225': 'net_cash_flow_per_share',
        'FN228': 'ratio_of_operating_cash_to_net_income',
    }

    CHINESE_FIELD_NAMES = {
        'net_income': '净利润',
        'depreciation_and_amortization': '资产减值准备',
        'net_cash_from_operating_activities': '经营活动产生的现金流量净额',
        'net_cash_from_investing_activities': '投资活动产生的现金流量净额',
        'net_cash_from_financing_activities': '筹资活动产生的现金流量净额',
        'net_change_in_cash_and_equivalents': '现金及现金等价物净增加额',
        'cash_at_beginning_of_period': '期初现金及现金等价物余额',
        'cash_at_end_of_period': '期末现金及现金等价物余额',
        'capital_expenditure': '购建固定资产、无形资产和其他长期资产支付的现金',
        'cash_received_from_sales': '销售商品、提供劳务收到的现金',
        'cash_paid_for_goods': '购买商品、接受劳务支付的现金',
        'cash_paid_to_employees': '支付给职工以及为职工支付的现金',
        'taxes_paid': '支付的各项税费',
        'free_cash_flow': '自由现金流',
    }

    @classmethod
    def map_to_openbb(cls, tdx_data: Dict[str, Any], year: int = 0, mmdd: int = 0) -> Dict[str, Any]:
        """
        Map TDX data to OpenBB cash flow statement format.
        
        Parameters
        ----------
        tdx_data : Dict[str, Any]
            Raw TDX financial data
        year : int
            The year parameter used in the query (for get_financial_data_by_date)
        mmdd : int
            The mmdd parameter used in the query (for get_financial_data_by_date)
            
        Returns
        -------
        Dict[str, Any]
            Mapped data with OpenBB field names
        """
        openbb_data = {}
        
        openbb_data['query_year'] = year
        openbb_data['query_mmdd'] = mmdd
        
        for tdx_field, openbb_field in cls.FIELD_MAPPING.items():
            if tdx_field in tdx_data:
                if tdx_field in ['tag_time', 'announce_time']:
                    openbb_data[openbb_field] = cls.convert_date(tdx_data[tdx_field])
                else:
                    openbb_data[openbb_field] = tdx_data[tdx_field]
        
        if 'tag_time' in tdx_data:
            if 'fiscal_period' not in openbb_data:
                openbb_data['fiscal_period'] = cls.map_fiscal_period(tdx_data['tag_time'])
            if 'fiscal_year' not in openbb_data:
                openbb_data['fiscal_year'] = cls.map_fiscal_year(tdx_data['tag_time'])
        elif year == 0 and mmdd == 0:
            latest_info = cls.get_latest_fiscal_info()
            if 'period_ending' not in openbb_data:
                openbb_data['period_ending'] = latest_info['period_ending']
            if 'fiscal_period' not in openbb_data:
                openbb_data['fiscal_period'] = latest_info['fiscal_period']
            if 'fiscal_year' not in openbb_data:
                openbb_data['fiscal_year'] = latest_info['fiscal_year']
        elif year > 0 and mmdd in [331, 630, 930, 1231]:
            fiscal_info = cls.get_fiscal_info_from_mmdd(year, mmdd)
            if 'period_ending' not in openbb_data:
                openbb_data['period_ending'] = fiscal_info['period_ending']
            if 'fiscal_period' not in openbb_data:
                openbb_data['fiscal_period'] = fiscal_info['fiscal_period']
            if 'fiscal_year' not in openbb_data:
                openbb_data['fiscal_year'] = fiscal_info['fiscal_year']
        else:
            logger.warning(
                f"Unable to derive fiscal period from year={year}, mmdd={mmdd}. "
                f"Valid mmdd values are: 331 (Q1), 630 (Q2), 930 (Q3), 1231 (Q4). "
                f"Use year=0, mmdd=0 for latest report."
            )
        
        if 'net_cash_from_operating_activities' in openbb_data:
            openbb_data['operating_cash_flow'] = openbb_data['net_cash_from_operating_activities']
        
        if 'operating_cash_flow' in openbb_data and 'capital_expenditure' in openbb_data:
            capex = openbb_data['capital_expenditure']
            if capex and capex < 0:
                openbb_data['free_cash_flow'] = openbb_data['operating_cash_flow'] + capex
            elif capex:
                openbb_data['free_cash_flow'] = openbb_data['operating_cash_flow'] - capex
        
        if 'cash_at_beginning_of_period' not in openbb_data and 'cash_at_beginning_of_period_alt' in openbb_data:
            openbb_data['cash_at_beginning_of_period'] = openbb_data['cash_at_beginning_of_period_alt']
        
        required_fields = [
            'period_ending', 'fiscal_period', 'fiscal_year',
            'net_income', 'net_cash_from_operating_activities',
            'net_cash_from_investing_activities', 'net_cash_from_financing_activities',
            'net_change_in_cash_and_equivalents', 'cash_at_beginning_of_period',
            'cash_at_end_of_period'
        ]
        
        for field in required_fields:
            if field not in openbb_data:
                openbb_data[field] = None
        
        return openbb_data


if __name__ == "__main__":
    print("=" * 60)
    print("Testing get_field_list() methods...")
    print("=" * 60)
    
    balance_fields = BalanceSheetMapper.get_field_list()
    print(f"\nBalance Sheet Fields ({len(balance_fields)} fields):")
    print(f"  {balance_fields[:10]} ... (showing first 10)")
    
    income_fields = IncomeStatementMapper.get_field_list()
    print(f"\nIncome Statement Fields ({len(income_fields)} fields):")
    print(f"  {income_fields}")
    
    cash_fields = CashFlowStatementMapper.get_field_list()
    print(f"\nCash Flow Fields ({len(cash_fields)} fields):")
    print(f"  {cash_fields[:10]} ... (showing first 10)")
    
    print("\n" + "=" * 60)
    print("Example usage with tq.get_financial_data_by_date:")
    print("=" * 60)
    print("""
    from tqcenter import tq
    from openbb_tdx.utils.financial_statement_mapping import BalanceSheetMapper
    
    # Get field list for balance sheet
    balance_fields = BalanceSheetMapper.get_field_list()
    
    # Call TDX API
    fd = tq.get_financial_data_by_date(
        stock_list=['600519.SH'],
        field_list=balance_fields,
        year=0,      # 0 = latest report
        mmdd=1231    # 1231 = Q4 (Dec 31)
    )
    
    # Map to OpenBB format
    mapped_data = BalanceSheetMapper.map_from_get_financial_data_by_date(
        fd, year=0, mmdd=1231
    )
    """)
    
    print("\n" + "=" * 60)
    print("Testing Balance Sheet Mapper...")
    print("=" * 60)
    sample_tdx_balance_data = {
        'tag_time': 20231231,
        'announce_time': 20240331,
        'FN8': 1000000000.0,
        'FN9': 500000000.0,
        'FN296': 300000000.0,
        'FN13': 50000000.0,
        'FN17': 200000000.0,
        'FN20': 100000000.0,
        'FN21': 2150000000.0,
        'FN27': 800000000.0,
        'FN35': 200000000.0,
        'FN33': 150000000.0,
        'FN25': 300000000.0,
        'FN37': 50000000.0,
        'FN38': 100000000.0,
        'FN39': 1600000000.0,
        'FN40': 3750000000.0,
        'FN295': 400000000.0,
        'FN41': 300000000.0,
        'FN53': 100000000.0,
        'FN54': 800000000.0,
        'FN55': 500000000.0,
        'FN56': 300000000.0,
        'FN60': 50000000.0,
        'FN61': 100000000.0,
        'FN62': 950000000.0,
        'FN63': 1750000000.0,
        'FN64': 500000000.0,
        'FN67': 50000000.0,
        'FN68': 1200000000.0,
        'FN65': 300000000.0,
        'FN298': 50000000.0,
        'FN69': 50000000.0,
        'FN72': 2050000000.0,
        'FN73': 3750000000.0,
    }
    mapped_balance = BalanceSheetMapper.map_to_openbb(sample_tdx_balance_data, year=2023, mmdd=1231)
    print("Balance Sheet Mapped Successfully!")
    print(f"  query_year: {mapped_balance.get('query_year')}")
    print(f"  query_mmdd: {mapped_balance.get('query_mmdd')}")
    print(f"  period_ending: {mapped_balance.get('period_ending')}")
    print(f"  total_assets: {mapped_balance.get('total_assets')}")
    print(f"  total_liabilities: {mapped_balance.get('total_liabilities')}")
    print(f"  total_common_equity: {mapped_balance.get('total_common_equity')}")

    print("\n" + "=" * 60)
    print("Testing Income Statement Mapper...")
    print("=" * 60)
    sample_tdx_income_data = {
        'tag_time': 20231231,
        'announce_time': 20240331,
        'FN230': 383285000000.0,
        'FN231': 120000000000.0,
        'FN232': 96995000000.0,
        'FN134': 96995000000.0,
        'FN1': 6.16,
        'FN2': 6.11,
        'FN207': 125000000000.0,
        'FN208': 125800000000.0,
    }
    mapped_income = IncomeStatementMapper.map_to_openbb(sample_tdx_income_data, year=2023, mmdd=1231)
    print("Income Statement Mapped Successfully!")
    print(f"  query_year: {mapped_income.get('query_year')}")
    print(f"  query_mmdd: {mapped_income.get('query_mmdd')}")
    print(f"  revenue: {mapped_income.get('revenue')}")
    print(f"  net_income: {mapped_income.get('net_income')}")
    print(f"  ebitda: {mapped_income.get('ebitda')}")

    print("\n" + "=" * 60)
    print("Testing Cash Flow Statement Mapper...")
    print("=" * 60)
    sample_tdx_cash_data = {
        'tag_time': 20231231,
        'announce_time': 20240331,
        'FN134': 96995000000.0,
        'FN107': 110543000000.0,
        'FN119': -3720000000.0,
        'FN128': -108259000000.0,
        'FN131': -1090000000.0,
        'FN132': 100000000000.0,
        'FN133': 98910000000.0,
        'FN114': -5000000000.0,
    }
    mapped_cash = CashFlowStatementMapper.map_to_openbb(sample_tdx_cash_data, year=2023, mmdd=1231)
    print("Cash Flow Statement Mapped Successfully!")
    print(f"  query_year: {mapped_cash.get('query_year')}")
    print(f"  query_mmdd: {mapped_cash.get('query_mmdd')}")
    print(f"  net_cash_from_operating_activities: {mapped_cash.get('net_cash_from_operating_activities')}")
    print(f"  free_cash_flow: {mapped_cash.get('free_cash_flow')}")

    print("\n" + "=" * 60)
    print("Testing get_financial_data_by_date mapping...")
    print("=" * 60)
    sample_tdx_all_data_by_date = {
        '600519.SH': {
            'tag_time': 20231231,
            'announce_time': 20240331,
            'FN8': '1000000000.0',
            'FN9': '500000000.0',
            'FN40': '3750000000.0',
            'FN230': '383285000000.0',
            'FN232': '96995000000.0',
            'FN107': '110543000000.0',
        }
    }
    mapped_all_balance = BalanceSheetMapper.map_from_get_financial_data_by_date(
        sample_tdx_all_data_by_date, year=2023, mmdd=1231
    )
    print(f"Balance sheet for 600519.SH:")
    print(f"  query_year: {mapped_all_balance['600519.SH'].get('query_year')}")
    print(f"  query_mmdd: {mapped_all_balance['600519.SH'].get('query_mmdd')}")
    print(f"  total_assets: {mapped_all_balance['600519.SH'].get('total_assets')}")
    
    print("\n" + "=" * 60)
    print("Testing latest fiscal info (year=0, mmdd=0, no tag_time)...")
    print("=" * 60)
    sample_no_tag_time = {
        'FN8': 1000000000.0,
        'FN40': 3750000000.0,
    }
    mapped_latest = BalanceSheetMapper.map_to_openbb(sample_no_tag_time, year=0, mmdd=0)
    print(f"  query_year: {mapped_latest.get('query_year')}")
    print(f"  query_mmdd: {mapped_latest.get('query_mmdd')}")
    print(f"  period_ending: {mapped_latest.get('period_ending')}")
    print(f"  fiscal_period: {mapped_latest.get('fiscal_period')}")
    print(f"  fiscal_year: {mapped_latest.get('fiscal_year')}")
    
    print("\n" + "=" * 60)
    print("Testing fiscal info from year/mmdd (year=2024, mmdd=930, no tag_time)...")
    print("=" * 60)
    sample_no_tag_time_2 = {
        'FN8': 1000000000.0,
        'FN40': 3750000000.0,
    }
    mapped_from_mmdd = BalanceSheetMapper.map_to_openbb(sample_no_tag_time_2, year=2024, mmdd=930)
    print(f"  query_year: {mapped_from_mmdd.get('query_year')}")
    print(f"  query_mmdd: {mapped_from_mmdd.get('query_mmdd')}")
    print(f"  period_ending: {mapped_from_mmdd.get('period_ending')}")
    print(f"  fiscal_period: {mapped_from_mmdd.get('fiscal_period')}")
    print(f"  fiscal_year: {mapped_from_mmdd.get('fiscal_year')}")
    
    print("\n" + "=" * 60)
    print("Testing invalid mmdd (year=2024, mmdd=301, no tag_time)...")
    print("=" * 60)
    sample_invalid_mmdd = {
        'FN8': 1000000000.0,
        'FN40': 3750000000.0,
    }
    mapped_invalid = BalanceSheetMapper.map_to_openbb(sample_invalid_mmdd, year=2024, mmdd=301)
    print(f"  query_year: {mapped_invalid.get('query_year')}")
    print(f"  query_mmdd: {mapped_invalid.get('query_mmdd')}")
    print(f"  period_ending: {mapped_invalid.get('period_ending')}")
    print(f"  fiscal_period: {mapped_invalid.get('fiscal_period')}")
    print(f"  fiscal_year: {mapped_invalid.get('fiscal_year')}")
    
    print("\nAll tests completed successfully!")
