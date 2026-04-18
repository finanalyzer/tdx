"""
TDX to OpenBB Equity Metrics Mapper

This module provides comprehensive mapping between TDX (通达信) quantitative platform
functions and OpenBB obb.equity.fundamental.metrics function requirements.

Author: MiniMax Agent
Version: 1.0
Date: 2026-04-18

Usage:
    from tdx_to_openbb_mapper import TDXMetricsMapper, map_tdx_to_openbb_metrics

    # Get data from TDX
    stock_info = tq.get_stock_info(stock_code, field_list=[])
    more_info = tq.get_more_info(stock_code, field_list=[])

    # Map to OpenBB format
    metrics = map_tdx_to_openbb_metrics(stock_code, stock_info, more_info)
"""

from datetime import datetime, date
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# Type Definitions
# =============================================================================

TDXData = Dict[str, Any]
OpenBBResult = Dict[str, Any]


# =============================================================================
# Data Type Conversion Functions
# =============================================================================

def convert_tdx_numeric(value: str) -> Optional[float]:
    """
    Convert TDX numeric string to float.

    Args:
        value: String representation of a number

    Returns:
        Float value or None if conversion fails
    """
    if value is None or value == '':
        return None
    try:
        return float(str(value))
    except (ValueError, TypeError, InvalidOperation):
        logger.warning(f"Failed to convert numeric value: {value}")
        return None


def convert_tdx_integer(value: str) -> Optional[int]:
    """
    Convert TDX numeric string to integer.

    Args:
        value: String representation of an integer

    Returns:
        Integer value or None if conversion fails
    """
    if value is None or value == '':
        return None
    try:
        return int(float(str(value)))
    except (ValueError, TypeError, InvalidOperation):
        logger.warning(f"Failed to convert integer value: {value}")
        return None


def convert_tdx_date(value: str) -> Optional[date]:
    """
    Convert TDX date string (YYYYMMDD) to Python date object.

    Args:
        value: Date string in format YYYYMMDD

    Returns:
        Python date object or None if conversion fails
    """
    if value is None or value == '':
        return None
    try:
        return datetime.strptime(str(value), '%Y%m%d').date()
    except (ValueError, TypeError):
        logger.warning(f"Failed to convert date value: {value}")
        return None


def convert_tdx_fiscal_year(value: str) -> Optional[int]:
    """
    Extract fiscal year from TDX date string.

    Args:
        value: Date string in format YYYYMMDD

    Returns:
        Year as integer or None if extraction fails
    """
    if value is None or value == '':
        return None
    try:
        return int(str(value)[:4])
    except (ValueError, TypeError, IndexError):
        logger.warning(f"Failed to extract fiscal year from: {value}")
        return None


def convert_tdx_market_cap(value: str) -> Optional[float]:
    """
    Convert TDX market cap from 亿元 (100 million CNY) to 元 (CNY).

    Args:
        value: Market cap in 亿元 units

    Returns:
        Market cap in 元 units or None if conversion fails
    """
    if value is None or value == '':
        return None
    try:
        return float(value) * 100000000
    except (ValueError, TypeError, InvalidOperation):
        logger.warning(f"Failed to convert market cap: {value}")
        return None


def convert_tdx_units_万元(value: str) -> Optional[float]:
    """
    Convert TDX units from 万元 (10,000 CNY) to 元 (CNY).

    Args:
        value: Amount in 万元 units

    Returns:
        Amount in 元 units or None if conversion fails
    """
    if value is None or value == '':
        return None
    try:
        return float(value) * 10000
    except (ValueError, TypeError, InvalidOperation):
        logger.warning(f"Failed to convert 万元 units: {value}")
        return None


def convert_tdx_units_万股(value: str) -> Optional[float]:
    """
    Convert TDX units from 万股 (10,000 shares) to individual shares.

    Args:
        value: Share count in 万股 units

    Returns:
        Share count in individual shares or None if conversion fails
    """
    if value is None or value == '':
        return None
    try:
        return float(value) * 10000
    except (ValueError, TypeError, InvalidOperation):
        logger.warning(f"Failed to convert 万股 units: {value}")
        return None


def convert_percentage(value: str) -> Optional[float]:
    """
    Convert TDX percentage value to decimal format (0-1 scale).

    TDX sometimes returns percentages as decimal values (e.g., 4.97 for 4.97%)
    or as whole numbers (e.g., 497 for 4.97%). This function handles both.

    Args:
        value: Percentage value as string

    Returns:
        Percentage value (e.g., 4.97) or None if conversion fails
    """
    if value is None or value == '':
        return None
    try:
        num = float(value)
        # If value is > 100, it's likely in basis points or needs division
        if num > 100:
            return num / 100
        return num
    except (ValueError, TypeError, InvalidOperation):
        logger.warning(f"Failed to convert percentage: {value}")
        return None


# =============================================================================
# Default Value Definitions
# =============================================================================

DEFAULT_VALUES = {
    'currency': 'CNY',
    'numeric': None,
    'percentage': None,
    'date': None,
    'string': None,
    'boolean': False,
    'count': 0,
}


# =============================================================================
# OpenBB KeyMetrics Data Class
# =============================================================================

@dataclass
class OpenBBKeyMetrics:
    """
    OpenBB KeyMetrics data structure representing equity fundamental metrics.

    This class contains only fields that can be populated from TDX data.
    """

    symbol: Optional[str] = None
    period_ending: Optional[date] = None
    fiscal_year: Optional[int] = None
    fiscal_period: Optional[str] = None
    currency: Optional[str] = "CNY"
    market_cap: Optional[float] = None

    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    eps: Optional[float] = None
    price_to_book: Optional[float] = None
    book_value_per_share: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    gross_margin: Optional[float] = None
    profit_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    return_on_assets: Optional[float] = None
    return_on_equity: Optional[float] = None
    dividend_yield: Optional[float] = None

    enterprise_value: Optional[float] = None
    free_cash_flow_to_firm: Optional[float] = None
    tangible_asset_value: Optional[float] = None

    beta: Optional[float] = None
    year_high: Optional[float] = None
    year_low: Optional[float] = None
    shares_outstanding: Optional[int] = None
    free_float: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metrics to dictionary format for OpenBB compatibility.

        Returns:
            Dictionary with all metric fields and their values
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, date):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result

    def to_openbb_format(self) -> OpenBBResult:
        """
        Convert to OpenBB standard output format.

        Returns:
            Dictionary with 'results', 'provider', 'warnings', 'chart', 'extra' keys
        """
        return {
            'results': self.to_dict(),
            'provider': 'tdx',
            'warnings': [],
            'chart': None,
            'extra': {
                'source': 'tdx',
                'mapping_version': '1.0',
                'data_completeness': self._calculate_completeness()
            }
        }

    def _calculate_completeness(self) -> Dict[str, float]:
        """
        Calculate data completeness percentage.

        Returns:
            Dictionary with category-wise completeness percentages
        """
        categories = {
            'standard': ['symbol', 'period_ending', 'fiscal_year', 'currency', 'market_cap'],
            'valuation': ['pe_ratio', 'eps', 'price_to_book', 'book_value_per_share'],
            'profitability': ['return_on_equity', 'return_on_assets', 'gross_margin', 'profit_margin'],
            'leverage': ['current_ratio', 'debt_to_equity'],
            'dividend': ['dividend_yield'],
            'risk': ['beta', 'year_high', 'year_low']
        }

        completeness = {}
        for category, fields in categories.items():
            total = len(fields)
            filled = sum(1 for f in fields if getattr(self, f, None) is not None)
            completeness[category] = (filled / total * 100) if total > 0 else 0

        return completeness


# =============================================================================
# TDX Metrics Mapper Class
# =============================================================================

class TDXMetricsMapper:
    """
    Maps TDX function outputs to OpenBB metrics format.

    This class provides methods for safely retrieving and converting data
    from TDX get_stock_info and get_more_info functions.
    """

    def __init__(self, stock_info: TDXData, more_info: TDXData):
        """
        Initialize the mapper with TDX data sources.

        Args:
            stock_info: Output from get_stock_info function
            more_info: Output from get_more_info function
        """
        self.stock_info = stock_info
        self.more_info = more_info

    def safe_get(
        self,
        source: str,
        field: str,
        convert_func: Optional[Callable] = None,
        default: Any = None
    ) -> Any:
        """
        Safely retrieve and convert a field from TDX data.

        Args:
            source: 'stock_info' or 'more_info'
            field: Field name in TDX data
            convert_func: Optional conversion function
            default: Default value if field is missing or invalid

        Returns:
            Converted value or default
        """
        data = self.stock_info if source == 'stock_info' else self.more_info

        try:
            value = data.get(field)
            if value is None or value == '':
                return default
            if convert_func is not None:
                return convert_func(str(value))
            return value
        except (ValueError, TypeError, InvalidOperation) as e:
            logger.warning(f"Error retrieving {source}.{field}: {e}")
            return default

    # -------------------------------------------------------------------------
    # Standard Field Mappers
    # -------------------------------------------------------------------------

    def map_symbol(self, stock_code: str) -> str:
        """Map stock code to symbol."""
        return stock_code or ''

    def map_period_ending(self) -> Optional[date]:
        """Map report date to period ending."""
        return self.safe_get('stock_info', 'ReportDate', convert_tdx_date)

    def map_fiscal_year(self) -> Optional[int]:
        """Map report date to fiscal year."""
        return self.safe_get('stock_info', 'ReportDate', convert_tdx_fiscal_year)

    def map_currency(self) -> str:
        """Map currency (always CNY for TDX data)."""
        return 'CNY'

    # -------------------------------------------------------------------------
    # Valuation Field Mappers
    # -------------------------------------------------------------------------

    def map_market_cap(self) -> Optional[float]:
        """Map total market cap from 亿元 to 元."""
        return self.safe_get('more_info', 'Zsz', convert_tdx_market_cap)

    def map_pe_ratio(self) -> Optional[float]:
        """Map P/E ratio (TTM)."""
        return self.safe_get('more_info', 'StaticPE_TTM', convert_tdx_numeric)

    def map_forward_pe(self) -> Optional[float]:
        """Map forward P/E ratio."""
        return self.safe_get('more_info', 'DynaPE', convert_tdx_numeric)

    def map_eps(self) -> Optional[float]:
        """Map earnings per share."""
        return self.safe_get('stock_info', 'J_mgsy', convert_tdx_numeric)

    def map_book_value_per_share(self) -> Optional[float]:
        """Map book value per share."""
        return self.safe_get('stock_info', 'J_mgjzc', convert_tdx_numeric)

    def map_price_to_book(self) -> Optional[float]:
        """Map price to book ratio."""
        return self.safe_get('more_info', 'PB_MRQ', convert_tdx_numeric)

    # -------------------------------------------------------------------------
    # Profitability Field Mappers
    # -------------------------------------------------------------------------

    def map_return_on_equity(self) -> Optional[float]:
        """Map return on equity (ROE)."""
        return self.safe_get('stock_info', 'J_jyl', convert_percentage)

    def map_return_on_assets(self) -> Optional[float]:
        """Calculate return on assets from TDX data."""
        net_profit = self.safe_get('stock_info', 'J_jly', convert_tdx_units_万元)
        total_assets = self.safe_get('stock_info', 'J_zzc', convert_tdx_units_万元)
        if net_profit is not None and total_assets is not None and total_assets != 0:
            return (net_profit / total_assets) * 100
        return None

    def map_gross_margin(self) -> Optional[float]:
        """Calculate gross margin from TDX data."""
        revenue = self.safe_get('stock_info', 'J_yysy', convert_tdx_units_万元)
        costs = self.safe_get('stock_info', 'J_yycb', convert_tdx_units_万元)
        if revenue is not None and costs is not None and revenue != 0:
            return ((revenue - costs) / revenue) * 100
        return None

    def map_profit_margin(self) -> Optional[float]:
        """Calculate profit margin from TDX data."""
        revenue = self.safe_get('stock_info', 'J_yysy', convert_tdx_units_万元)
        net_profit = self.safe_get('stock_info', 'J_jly', convert_tdx_units_万元)
        if revenue is not None and net_profit is not None and revenue != 0:
            return (net_profit / revenue) * 100
        return None

    def map_operating_margin(self) -> Optional[float]:
        """Calculate operating margin from TDX data."""
        revenue = self.safe_get('stock_info', 'J_yysy', convert_tdx_units_万元)
        operating_profit = self.safe_get('stock_info', 'J_yyly', convert_tdx_units_万元)
        if revenue is not None and operating_profit is not None and revenue != 0:
            return (operating_profit / revenue) * 100
        return None

    # -------------------------------------------------------------------------
    # Leverage Field Mappers
    # -------------------------------------------------------------------------

    def map_current_ratio(self) -> Optional[float]:
        """Calculate current ratio from TDX data."""
        current_assets = self.safe_get('stock_info', 'J_ldzc', convert_tdx_units_万元)
        current_liabilities = self.safe_get('stock_info', 'J_ldfz', convert_tdx_units_万元)
        if current_assets is not None and current_liabilities is not None:
            if current_liabilities != 0:
                return current_assets / current_liabilities
        return None

    def map_debt_to_equity(self) -> Optional[float]:
        """Calculate debt to equity ratio from TDX data."""
        current_liabilities = self.safe_get('stock_info', 'J_ldfz', convert_tdx_units_万元)
        minority_interest = self.safe_get('stock_info', 'J_cqfz', convert_tdx_units_万元)
        equity = self.safe_get('stock_info', 'J_jzc', convert_tdx_units_万元)

        if equity is not None and equity != 0:
            total_liabilities = 0
            if current_liabilities is not None:
                total_liabilities += current_liabilities
            if minority_interest is not None:
                total_liabilities += minority_interest
            return total_liabilities / equity
        return None

    # -------------------------------------------------------------------------
    # Dividend Field Mappers
    # -------------------------------------------------------------------------

    def map_dividend_yield(self) -> Optional[float]:
        """Map dividend yield."""
        return self.safe_get('more_info', 'DYRatio', convert_tdx_numeric)

    # -------------------------------------------------------------------------
    # Risk Field Mappers
    # -------------------------------------------------------------------------

    def map_beta(self) -> Optional[float]:
        """Map beta coefficient."""
        return self.safe_get('more_info', 'BetaValue', convert_tdx_numeric)

    def map_year_high(self) -> Optional[float]:
        """Map 52-week high price."""
        return self.safe_get('more_info', 'HisHigh', convert_tdx_numeric)

    def map_year_low(self) -> Optional[float]:
        """Map 52-week low price."""
        return self.safe_get('more_info', 'HisLow', convert_tdx_numeric)

    # -------------------------------------------------------------------------
    # Share Data Mappers
    # -------------------------------------------------------------------------

    def map_shares_outstanding(self) -> Optional[int]:
        """Map total shares outstanding from 万股 to shares."""
        return self.safe_get('stock_info', 'J_zgb', convert_tdx_units_万股)

    def map_free_float(self) -> Optional[int]:
        """Map free float from 万股 to shares."""
        return self.safe_get('more_info', 'FreeLtgb', convert_tdx_units_万股)

    # -------------------------------------------------------------------------
    # Cash Flow Mappers
    # -------------------------------------------------------------------------

    def map_operating_cash_flow(self) -> Optional[float]:
        """Map operating cash flow from 万元 to CNY."""
        return self.safe_get('stock_info', 'J_jyxjl', convert_tdx_units_万元)

    def map_free_cash_flow(self) -> Optional[float]:
        """Map free cash flow from 万元 to CNY."""
        return self.safe_get('stock_info', 'J_zxjl', convert_tdx_units_万元)

    # -------------------------------------------------------------------------
    # Enterprise Value Calculation
    # -------------------------------------------------------------------------

    def calculate_enterprise_value(self) -> Optional[float]:
        """
        Calculate enterprise value from TDX data.

        Formula: EV = Market Cap + Total Debt - Cash
        """
        market_cap = self.map_market_cap()
        if market_cap is None:
            return None

        total_debt = self.safe_get('stock_info', 'J_ldfz', convert_tdx_units_万元)
        cash = self.safe_get('more_info', 'CashZJ', convert_tdx_units_万元)

        ev = market_cap
        if total_debt is not None:
            ev += total_debt
        if cash is not None:
            ev -= cash

        return ev

    def calculate_tangible_book_value(self) -> Optional[float]:
        """
        Calculate tangible book value from TDX data.

        Formula: TBV = Equity - Intangible Assets
        """
        equity = self.safe_get('stock_info', 'J_jzc', convert_tdx_units_万元)
        intangible_assets = self.safe_get('stock_info', 'J_wxzc', convert_tdx_units_万元)

        if equity is not None and intangible_assets is not None:
            return equity - intangible_assets
        elif equity is not None:
            return equity
        return None


# =============================================================================
# Main Mapping Function
# =============================================================================

def map_tdx_to_openbb_metrics(
    stock_code: str,
    stock_info: TDXData,
    more_info: TDXData
) -> OpenBBKeyMetrics:
    """
    Map TDX function outputs to OpenBB KeyMetrics format.

    This is the main entry point for converting TDX data to OpenBB format.

    Args:
        stock_code: Stock symbol/code
        stock_info: Output from get_stock_info function
        more_info: Output from get_more_info function

    Returns:
        OpenBBKeyMetrics instance with mapped and calculated data

    Example:
        >>> stock_info = tq.get_stock_info('688318.SH', field_list=[])
        >>> more_info = tq.get_more_info('688318.SH', field_list=[])
        >>> metrics = map_tdx_to_openbb_metrics('688318.SH', stock_info, more_info)
        >>> print(f"P/E Ratio: {metrics.pe_ratio}")
        >>> print(f"Market Cap: {metrics.market_cap}")
    """
    mapper = TDXMetricsMapper(stock_info, more_info)

    # Build metrics object with all mapped fields
    metrics = OpenBBKeyMetrics(
        # Standard fields
        symbol=mapper.map_symbol(stock_code),
        period_ending=mapper.map_period_ending(),
        fiscal_year=mapper.map_fiscal_year(),
        fiscal_period=None,  # Not available from TDX
        currency=mapper.map_currency(),
        market_cap=mapper.map_market_cap(),

        # Valuation metrics
        pe_ratio=mapper.map_pe_ratio(),
        forward_pe=mapper.map_forward_pe(),
        eps=mapper.map_eps(),
        price_to_book=mapper.map_price_to_book(),
        book_value_per_share=mapper.map_book_value_per_share(),

        # Profitability metrics
        return_on_assets=mapper.map_return_on_assets(),
        return_on_equity=mapper.map_return_on_equity(),
        gross_margin=mapper.map_gross_margin(),
        profit_margin=mapper.map_profit_margin(),
        operating_margin=mapper.map_operating_margin(),

        # Leverage metrics
        current_ratio=mapper.map_current_ratio(),
        debt_to_equity=mapper.map_debt_to_equity(),

        # Dividend metrics
        dividend_yield=mapper.map_dividend_yield(),

        # Risk metrics
        beta=mapper.map_beta(),
        year_high=mapper.map_year_high(),
        year_low=mapper.map_year_low(),

        # Share data
        shares_outstanding=mapper.map_shares_outstanding(),
        free_float=mapper.map_free_float(),

        # Cash flow
        free_cash_flow_to_firm=mapper.map_free_cash_flow(),
    )

    # Calculate additional derived metrics
    metrics.enterprise_value = mapper.calculate_enterprise_value()
    metrics.tangible_asset_value = mapper.calculate_tangible_book_value()

    return metrics


# =============================================================================
# Batch Processing Functions
# =============================================================================

def map_multiple_stocks(
    stock_codes: List[str],
    get_stock_info_func: Callable,
    get_more_info_func: Callable
) -> Dict[str, OpenBBKeyMetrics]:
    """
    Map multiple stocks from TDX to OpenBB format.

    Args:
        stock_codes: List of stock codes to process
        get_stock_info_func: Function to call get_stock_info
        get_more_info_func: Function to call get_more_info

    Returns:
        Dictionary mapping stock codes to OpenBBKeyMetrics instances
    """
    results = {}
    for code in stock_codes:
        try:
            stock_info = get_stock_info_func(code, field_list=[])
            more_info = get_more_info_func(code, field_list=[])
            results[code] = map_tdx_to_openbb_metrics(code, stock_info, more_info)
        except Exception as e:
            logger.error(f"Error processing {code}: {e}")
            results[code] = None
    return results


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    'TDXMetricsMapper',
    'OpenBBKeyMetrics',
    'map_tdx_to_openbb_metrics',
    'map_multiple_stocks',
    'convert_tdx_numeric',
    'convert_tdx_date',
    'convert_tdx_market_cap',
    'convert_tdx_units_万元',
    'convert_tdx_units_万股',
]


if __name__ == '__main__':
    from tqcenter import tq
    # Example usage demonstration
    print("TDX to OpenBB Metrics Mapper")
    print("=" * 50)
    print("\nUsage:")
    print("  from tdx_to_openbb_mapper import map_tdx_to_openbb_metrics")
    print("\n  stock_info = tq.get_stock_info('688318.SH', field_list=[])")
    print("  more_info = tq.get_more_info('688318.SH', field_list=[])")
    print("  metrics = map_tdx_to_openbb_metrics('688318.SH', stock_info, more_info)")
    print("\n  Access fields: metrics.pe_ratio, metrics.market_cap, etc.")

    #初始化
    tq.initialize(__file__) #所有策略连接通达信客户端都必须调用此函数进行初始化
    stock_info = tq.get_stock_info('688318.SH', field_list=[])
    more_info = tq.get_more_info('688318.SH', field_list=[])
    metrics = map_tdx_to_openbb_metrics('688318.SH', stock_info, more_info)
    print(f"Return from mapping: {metrics}")

