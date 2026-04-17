"""TdxQuant Constants.

This module defines constants and enumerations for TdxQuant API.
Reference: https://help.tdx.com.cn/quant/docs/markdown/Dict.html
"""

from enum import IntEnum


class Market(IntEnum):
    """Market type enumeration."""
    
    SZ = 0      # 深圳交易所
    SH = 1      # 上海交易所
    BJ = 2      # 北京交易所
    NQ = 44     # 新三板
    SHO = 8     # 上海个股期权
    SZO = 9     # 深圳个股期权
    HK = 31     # 香港交易所
    US = 74     # 美国股票
    CSI = 62    # 中证指数
    CNI = 102   # 国证指数
    HG = 38     # 国内宏观指标
    CFF = 47    # 中金期货
    CZC = 28    # 郑州期货
    DCE = 29    # 大连期货
    SHF = 30    # 上海期货
    GFE = 66    # 广州期货
    INE = 30    # 上海能源
    HI = 27     # 港股指数
    OF = 33     # 开放式基金净值
    CFFO = 7    # 中金所期权
    CZCO = 4    # 郑州期货期权
    DCEO = 5    # 大连期货期权
    SHFO = 6    # 上海期货期权
    GFEO = 67   # 广州期货期权
    QHZ = 42    # 期货类指数


class DividendType:
    """Dividend type constants for price adjustment."""
    
    NONE = "none"       # 不复权
    FRONT = "front"     # 前复权
    BACK = "back"       # 后复权


class Period:
    """Period constants for K-line data."""
    
    TICK = "tick"       # 分笔
    M1 = "1m"           # 1分钟
    M5 = "5m"           # 5分钟
    M15 = "15m"         # 15分钟
    M30 = "30m"         # 30分钟
    H1 = "1h"           # 60分钟（1小时）
    D1 = "1d"           # 1天
    W1 = "1w"           # 1周
    MON = "1mon"        # 1月
    Q = "1q"            # 1季
    Y = "1y"            # 1年


class OrderType(IntEnum):
    """Order type enumeration."""
    
    STOCK_BUY = 0               # 买
    STOCK_SELL = 1              # 卖
    CREDIT_BUY = 0              # 担保品买入
    CREDIT_SELL = 1             # 担保品卖出
    CREDIT_FIN_BUY = 69         # 融资买入
    CREDIT_SLO_SELL = 70        # 融券卖出
    ETF_PURCHASE = 45           # 基金申购
    ETF_REDEMPTION = 46         # 基金赎回
    FUTURE_OPEN_LONG = 101      # 期货开多
    FUTURE_OPEN_SHORT = 102     # 期货开空
    FUTURE_CLOSE_LONG = 103     # 期货平多
    FUTURE_CLOSE_SHORT = 104    # 期货平空
    OPTION_OPEN_LONG = 201      # 期权开多
    OPTION_OPEN_SHORT = 202     # 期权开空
    OPTION_CLOSE_LONG = 203     # 期权平多
    OPTION_CLOSE_SHORT = 204    # 期权平空


class PriceType(IntEnum):
    """Price type enumeration."""
    
    PRICE_MY = 0     # 自填价
    PRICE_SJ = 1     # 市价
    PRICE_ZTJ = 2    # 涨停价/笼子上限
    PRICE_DTJ = 3    # 跌停价/笼子下限


class Status(IntEnum):
    """Order status enumeration."""
    
    WTSTATUS_NULL = 0      # 无效单
    WTSTATUS_NOCJ = 1      # 未成交
    WTSTATUS_PARTCJ = 2    # 部分成交
    WTSTATUS_ALLCJ = 3     # 全部成交
    WTSTATUS_BCBC = 4      # 部分成交部分撤单
    WTSTATUS_ALLCD = 5     # 全部撤单


MARKET_SUFFIX_MAP = {
    Market.SZ: ".SZ",
    Market.SH: ".SH",
    Market.BJ: ".BJ",
    Market.NQ: ".NQ",
    Market.SHO: ".SHO",
    Market.SZO: ".SZO",
    Market.HK: ".HK",
    Market.US: ".US",
    Market.CSI: ".CSI",
    Market.CNI: ".CNI",
    Market.HG: ".HG",
    Market.CFF: ".CFF",
    Market.CZC: ".CZC",
    Market.DCE: ".DCE",
    Market.SHF: ".SHF",
    Market.GFE: ".GFE",
    Market.INE: ".INE",
    Market.HI: ".HI",
    Market.OF: ".OF",
    Market.CFFO: ".CFFO",
    Market.CZCO: ".CZCO",
    Market.DCEO: ".DCEO",
    Market.SHFO: ".SHFO",
    Market.GFEO: ".GFEO",
    Market.QHZ: ".QHZ",
}

SUFFIX_TO_MARKET_MAP = {v: k for k, v in MARKET_SUFFIX_MAP.items()}

MARKET_NAME_MAP = {
    Market.SZ: "深圳交易所",
    Market.SH: "上海交易所",
    Market.BJ: "北京交易所",
    Market.NQ: "新三板",
    Market.SHO: "上海个股期权",
    Market.SZO: "深圳个股期权",
    Market.HK: "香港交易所",
    Market.US: "美国股票",
    Market.CSI: "中证指数",
    Market.CNI: "国证指数",
    Market.HG: "国内宏观指标",
    Market.CFF: "中金期货",
    Market.CZC: "郑州期货",
    Market.DCE: "大连期货",
    Market.SHF: "上海期货",
    Market.GFE: "广州期货",
    Market.INE: "上海能源",
    Market.HI: "港股指数",
    Market.OF: "开放式基金净值",
    Market.CFFO: "中金所期权",
    Market.CZCO: "郑州期货期权",
    Market.DCEO: "大连期货期权",
    Market.SHFO: "上海期货期权",
    Market.GFEO: "广州期货期权",
    Market.QHZ: "期货类指数",
}

MARKET_CODE_NAME_MAP = {
    "SZ": "深圳交易所",
    "SH": "上海交易所",
    "BJ": "北京交易所",
    "NQ": "新三板",
    "SHO": "上海个股期权",
    "SZO": "深圳个股期权",
    "HK": "香港交易所",
    "US": "美国股票",
    "CSI": "中证指数",
    "CNI": "国证指数",
    "HG": "国内宏观指标",
    "CFF": "中金期货",
    "CZC": "郑州期货",
    "DCE": "大连期货",
    "SHF": "上海期货",
    "GFE": "广州期货",
    "INE": "上海能源",
    "HI": "港股指数",
    "OF": "开放式基金净值",
    "CFFO": "中金所期权",
    "CZCO": "郑州期货期权",
    "DCEO": "大连期货期权",
    "SHFO": "上海期货期权",
    "GFEO": "广州期货期权",
    "QHZ": "期货类指数",
}


def get_market_from_suffix(suffix: str) -> Market:
    """Get market type from suffix.
    
    Args:
        suffix: Market suffix (e.g., '.SZ', '.SH')
    
    Returns:
        Market enum value
    
    Raises:
        ValueError: If suffix is not recognized
    """
    if suffix not in SUFFIX_TO_MARKET_MAP:
        raise ValueError(f"Unknown market suffix: {suffix}")
    return SUFFIX_TO_MARKET_MAP[suffix]


def get_suffix_from_market(market: Market) -> str:
    """Get market suffix from market type.
    
    Args:
        market: Market enum value
    
    Returns:
        Market suffix string
    
    Raises:
        ValueError: If market is not recognized
    """
    if market not in MARKET_SUFFIX_MAP:
        raise ValueError(f"Unknown market type: {market}")
    return MARKET_SUFFIX_MAP[market]


def get_market_name(market: Market) -> str:
    """Get market name in Chinese.
    
    Args:
        market: Market enum value
    
    Returns:
        Market name in Chinese
    
    Raises:
        ValueError: If market is not recognized
    """
    if market not in MARKET_NAME_MAP:
        raise ValueError(f"Unknown market type: {market}")
    return MARKET_NAME_MAP[market]


def get_exchange_name(market_code: str) -> str:
    """Get exchange name from market code.
    
    Args:
        market_code: Market code string (e.g., 'SZ', 'SH')
    
    Returns:
        Exchange name in Chinese
    
    Raises:
        ValueError: If market code is not recognized
    """
    if market_code not in MARKET_CODE_NAME_MAP:
        raise ValueError(f"Unknown market code: {market_code}")
    return MARKET_CODE_NAME_MAP[market_code]
