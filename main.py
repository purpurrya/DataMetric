from contextlib import asynccontextmanager
from typing import Annotated

from clickhouse_connect.driver.asyncclient import AsyncClient
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

from schemas import (
    CategoryPurchases,
    DailyMetric,
    FunnelResponse,
    HealthResponse,
    SummaryResponse,
)
from scripts import sql_aggregation
from scripts.ch_client import get_async_client
from scripts.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ch_client = await get_async_client()
    redis = None
    try:
        redis = aioredis.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}"
        )
        FastAPICache.init(RedisBackend(redis), prefix=settings.cache_prefix)
        yield
    finally:
        if redis:
            await redis.close()
        await app.state.ch_client.close()


app = FastAPI(
    title="DataMetric API",
    version="2.3.0",
    lifespan=lifespan,
)


def get_ch_client(request: Request) -> AsyncClient:
    return request.app.state.ch_client


ChClient = Annotated[AsyncClient, Depends(get_ch_client)]


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Check ClickHouse availability",
)
async def health(client: ChClient):
    try:
        result = await client.query("SELECT COUNT(*) FROM events")
        row_count = result.result_rows[0][0]
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": str(exc)},
        )
    return HealthResponse(status="ok", events_rows=row_count)


@app.get(
    "/stat/funnel",
    response_model=FunnelResponse,
    tags=["Stats"],
    summary="Sales funnel: view → cart → purchase",
)
@cache(expire=300)
async def funnel(client: ChClient):
    total, cart, purchase = await sql_aggregation.funnel_conversion(client)
    return FunnelResponse(
        total_sessions=total, reached_cart=cart, reached_purchase=purchase
    )


@app.get(
    "/stat/purchases-by-category",
    response_model=list[CategoryPurchases],
    tags=["Stats"],
    summary="Number of purchases by product category",
)
@cache(expire=300)
async def purchases_by_category(client: ChClient):
    rows = await sql_aggregation.purchases_by_category(client)
    return [
        CategoryPurchases(category_id=str(row[0]), purchases=row[1]) for row in rows
    ]


@app.get(
    "/stat/daily",
    response_model=list[DailyMetric],
    tags=["Stats"],
    summary="Sessions and transactions by day",
)
@cache(expire=300)
async def daily(client: ChClient):
    rows = await sql_aggregation.daily_metrics(client)
    return [
        DailyMetric(day=str(row[0]), sessions=row[1], transactions=row[2])
        for row in rows
    ]


@app.get(
    "/stat/summary",
    response_model=SummaryResponse,
    tags=["Stats"],
    summary="Summary metrics: items per order, cart abandonment, session duration",
)
@cache(expire=300)
async def summary(client: ChClient):
    (
        duration_avg,
        duration_median,
        duration_max,
    ) = await sql_aggregation.session_duration(client)
    eps_avg, eps_median, eps_max = await sql_aggregation.events_per_session(client)
    return SummaryResponse(
        avg_items_per_transaction=await sql_aggregation.avg_items_per_transaction(
            client
        ),
        cart_abandonment_rate=await sql_aggregation.cart_abandonment_rate(client),
        view_to_cart_rate=await sql_aggregation.view_to_cart_rate(client),
        session_duration_avg=duration_avg,
        session_duration_median=duration_median,
        session_duration_max=duration_max,
        events_per_session_avg=eps_avg,
        events_per_session_median=eps_median,
        events_per_session_max=eps_max,
    )
