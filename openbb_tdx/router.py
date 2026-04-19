"""TdxQuant router commands."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (ExtraParams, ProviderChoices,
                                                StandardParams)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="")


# pylint: disable=unused-argument
@router.command(model="TdxQuantEquityHistorical")
async def equity_historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get TdxQuant equity historical price data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="TdxQuantBalanceSheet")
async def balance_sheet(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get TdxQuant balance sheet data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="TdxQuantIncomeStatement")
async def income_statement(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get TdxQuant income statement data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="TdxQuantCashFlowStatement")
async def cash_flow(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get TdxQuant cash flow statement data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="TdxQuantEquityQuote")
async def equity_quote(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get TdxQuant equity quote data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="TdxQuantEquityDividends")
async def equity_dividends(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get TdxQuant equity dividends data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="TdxQuantEquityProfile")
async def equity_profile(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get TdxQuant equity profile data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="TdxQuantEquitySearch")
async def equity_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get TdxQuant equity search data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="TdxQuantKeyMetrics")
async def key_metrics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get TdxQuant key metrics data."""
    return await OBBject.from_query(Query(**locals()))
