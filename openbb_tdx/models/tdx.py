"""TdxQuant data models."""

from typing import List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.abstract.data import Data
from pydantic import Field
import pandas as pd
from tqcenter import tq


class TdxPriceQueryParams(QueryParams):
    """TdxQuant price query parameters."""
    symbol: str = Field(description="Stock symbol")
    exchange: Optional[str] = Field(
        default=None, description="Exchange code, e.g., 'sh' for Shanghai, 'sz' for Shenzhen"
    )
    interval: str = Field(default="1d", description="Time interval")


class TdxPriceData(Data):
    """TdxQuant price data."""
    symbol: str = Field(description="Stock symbol")
    date: str = Field(description="Date")
    open: float = Field(description="Open price")
    high: float = Field(description="High price")
    low: float = Field(description="Low price")
    close: float = Field(description="Close price")
    volume: int = Field(description="Volume")
    exchange: Optional[str] = Field(
        default=None, description="Exchange code"
    )


class TdxPriceFetcher(Fetcher[TdxPriceQueryParams, List[TdxPriceData]]):
    """TdxQuant price fetcher."""

    @staticmethod
    def transform_query(params: dict) -> TdxPriceQueryParams:
        """Transform query parameters."""
        return TdxPriceQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TdxPriceQueryParams,
        credentials: Optional[dict] = None,
    ) -> List[dict]:
        """Extract data from TdxQuant API."""
        tq.initialize(__file__)
        
        exchange = query.exchange or "sh"
        stock_code = f"{query.symbol}.{exchange.upper()}"
        
        period_map = {
            "1d": "1d",
            "1w": "1w",
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "60m": "1h",
        }
        period = period_map.get(query.interval, "1d")
        
        try:
            data_dict = tq.get_market_data(
                field_list=[],
                stock_list=[stock_code],
                period=period,
                count=100,
                dividend_type='none',
                fill_data=False
            )
            
            result = []
            if stock_code in data_dict:
                df = data_dict[stock_code]
                if isinstance(df, pd.DataFrame) and not df.empty:
                    for idx, row in df.iterrows():
                        date_str = idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx)
                        result.append({
                            "symbol": query.symbol,
                            "date": date_str,
                            "open": float(row.get('Open', 0)),
                            "high": float(row.get('High', 0)),
                            "low": float(row.get('Low', 0)),
                            "close": float(row.get('Close', 0)),
                            "volume": int(row.get('Volume', 0)),
                            "exchange": exchange,
                        })
            
            return result
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []
        finally:
            tq.close()

    @staticmethod
    def transform_data(data: List[dict]) -> List[TdxPriceData]:
        """Transform data into TdxPriceData model."""
        return [TdxPriceData(**item) for item in data]
