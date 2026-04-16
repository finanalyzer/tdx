"""AKShare Company News Model."""

# pylint: disable=unused-argument
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from pydantic import Field, field_validator

class AKshareCompanyNewsQueryParams(CompanyNewsQueryParams):
    """AKShare Company News Query.

    Source: https://so.eastmoney.com/news/s
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _symbol_mandatory(cls, v):
        """Symbol mandatory validator."""
        if not v:
            raise ValueError("Required field missing -> symbol")
        return v


class AKShareCompanyNewsData(CompanyNewsData):
    """AKShare Company News Data."""

    source: Optional[str] = Field(
        default=None, description="Source of the news article"
    )


class AKShareCompanyNewsFetcher(
    Fetcher[
        AKshareCompanyNewsQueryParams,
        List[AKShareCompanyNewsData],
    ]
):
    """Transform the query, extract and transform the data from the AKShare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKshareCompanyNewsQueryParams:
        """Define example transform_query.

        Here we can pre-process the query parameters and add any extra parameters that
        will be used inside the extract_data method.
        """
        # Normalize common aliases to `symbol` to improve compatibility with callers
        if not params.get("symbol"):
            for alias in ("query", "symbols", "ticker", "tickers"):
                if alias in params and params.get(alias):
                    params["symbol"] = params[alias]
                    break

        # If symbol provided as a list, join into comma-separated string
        symbol_val = params.get("symbol")
        if isinstance(symbol_val, (list, tuple)):
            params["symbol"] = ",".join(str(s) for s in symbol_val if s)

        return AKshareCompanyNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AKshareCompanyNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.errors import EmptyDataError
        import akshare as ak
        from mysharelib.tools import normalize_symbol

        results: list = []
        symbols = query.symbol.split(",")  # type: ignore
        async def get_one(symbol):
            from mysharelib.sina.scrape_hk_stock_news import scrape_hk_stock_news
            from mysharelib.em.stock_info_em import stock_info_em

            symbol_b, _, market = normalize_symbol(symbol)
            if market == "HK":
                data = scrape_hk_stock_news(symbol_b)
                if data is not None:
                    for d in data.to_dict(orient='records'):
                        new_content: dict = {}
                        new_content["date"] = d["date"]
                        new_content["title"] = d["title"]
                        new_content["url"] = d["url"]
                        results.append(new_content)
            else:
                data = stock_info_em(symbol)
                for idx, d in data.iterrows():
                    new_content: dict = {}
                    new_content["url"] = d["新闻链接"]
                    new_content["title"] = d["新闻标题"]
                    new_content["date"] = d["发布时间"]

                    results.append(new_content)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results:
            raise EmptyDataError("No data was returned for the given symbol(s)")

        return results

    @staticmethod
    def transform_data(
        query: AKshareCompanyNewsQueryParams, data: List[dict], **kwargs: Any
    ) -> List[AKShareCompanyNewsData]:
        """Define example transform_data.

        Right now, we're converting the data to fit our desired format.
        You can apply other transformations to it here.
        """
        return [AKShareCompanyNewsData(**d) for d in data]
