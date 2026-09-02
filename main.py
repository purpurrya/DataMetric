from contextlib import asynccontextmanager

import clickhouse_connect
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
from scripts.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ch_client = await clickhouse_connect.get_async_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        database=settings.clickhouse_db,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password,
    )
    redis = None
    try:
        redis = aioredis.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}"
        )
        FastAPICache.init(RedisBackend(redis), prefix="datametric-cache")
        yield
    finally:
        if redis:
            await redis.close()
        await app.state.ch_client.close()


app = FastAPI(title="DataMetric API", version="2.0.0", lifespan=lifespan)


def get_ch_client(request: Request):
    return request.app.state.ch_client


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health(client=Depends(get_ch_client)):
    try:
        result = await client.query("SELECT COUNT(*) FROM events")
        row_count = result.result_rows[0][0]
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": str(exc)},
        )
    return HealthResponse(status="ok", events_rows=row_count)


@app.get("/stat/funnel", response_model=FunnelResponse, tags=["Stat"])
@cache(expire=300)
async def funnel(client=Depends(get_ch_client)):
    total, cart, purchase = await sql_aggregation.funnel_conversion(client)
    return FunnelResponse(
        total_sessions=total, reached_cart=cart, reached_purchase=purchase
    )


@app.get(
    "/stat/purchases-by-category", response_model=list[CategoryPurchases], tags=["Stat"]
)
@cache(expire=300)
async def purchases_by_category(client=Depends(get_ch_client)):
    rows = await sql_aggregation.purchases_by_category(client)
    return [
        CategoryPurchases(category_id=str(row[0]), purchases=row[1]) for row in rows
    ]


@app.get("/stat/daily", response_model=list[DailyMetric], tags=["Stat"])
@cache(expire=300)
async def daily(client=Depends(get_ch_client)):
    rows = await sql_aggregation.daily_metrics(client)
    return [
        DailyMetric(day=str(row[0]), sessions=row[1], transactions=row[2])
        for row in rows
    ]


@app.get("/stat/summary", response_model=SummaryResponse, tags=["Stat"])
@cache(expire=300)
async def summary(client=Depends(get_ch_client)):
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
