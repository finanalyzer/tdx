"""AKShare Available Indices Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from datetime import (
    date as dateType
)

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indices import (
    AvailableIndicesData,
    AvailableIndicesQueryParams,
)
from pydantic import Field


class AKShareAvailableIndicesQueryParams(AvailableIndicesQueryParams):
    """AKShare Available Indices Query.

    Source: https://akshare.akfamily.xyz/data/index/index.html#id22
    """


class AKShareAvailableIndicesData(AvailableIndicesData):
    """AKShare Available Indices Data."""

    __alias_dict__ = {
        "name": "display_name",
        "symbol": "index_code",
    }

    publish_date: Optional[dateType] = Field(
        default=None,
        description="The date of the index published.",
    )
    symbol: str = Field(description="Symbol for the index.")


class AKShareAvailableIndicesFetcher(
    Fetcher[
        AKShareAvailableIndicesQueryParams,
        List[AKShareAvailableIndicesData],
    ]
):
    """Transform the query, extract and transform the data from the AKShare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareAvailableIndicesQueryParams:
        """Transform the query params."""
        return AKShareAvailableIndicesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: AKShareAvailableIndicesQueryParams,  # pylint disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data."""
        import akshare as ak

        index_stock_info_df = ak.index_stock_info()
        index_stock_info_df["currency"] = "CNY"

        return index_stock_info_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareAvailableIndicesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[AKShareAvailableIndicesData]:
        """Return the transformed data."""
        return [AKShareAvailableIndicesData.model_validate(d) for d in data]
