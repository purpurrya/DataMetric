from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response
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
from scripts.ch_client import get_client
from scripts.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
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


app = FastAPI(title="DataMetric API", version="2.0.0", lifespan=lifespan)


def get_ch_client():
    client = get_client()
    try:
        yield client
    finally:
        client.close()


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health(client=Depends(get_ch_client)):
    try:
        row_count = client.query("SELECT COUNT(*) FROM events").result_rows[0][0]
    except Exception as exc:
        return Response(
            content=f'{{"status": "error", "detail": "{exc}"}}',
            status_code=503,
            media_type="application/json",
        )
    return HealthResponse(status="ok", events_rows=row_count)


@app.get("/stat/funnel", response_model=FunnelResponse, tags=["Stat"])
@cache(expire=300)
def funnel():
    client = get_client()
    try:
        total, cart, purchase = sql_aggregation.funnel_conversion(client)
    finally:
        client.close()
    return FunnelResponse(
        total_sessions=total, reached_cart=cart, reached_purchase=purchase
    )


@app.get(
    "/stat/purchases-by-category", response_model=list[CategoryPurchases], tags=["Stat"]
)
@cache(expire=300)
def purchases_by_category():
    client = get_client()
    try:
        rows = sql_aggregation.purchases_by_category(client)
    finally:
        client.close()
    return [
        CategoryPurchases(category_id=str(row[0]), purchases=row[1]) for row in rows
    ]


@app.get("/stat/daily", response_model=list[DailyMetric], tags=["Stat"])
@cache(expire=300)
def daily():
    client = get_client()
    try:
        rows = sql_aggregation.daily_metrics(client)
    finally:
        client.close()
    return [
        DailyMetric(day=str(row[0]), sessions=row[1], transactions=row[2])
        for row in rows
    ]


@app.get("/stat/summary", response_model=SummaryResponse, tags=["Stat"])
@cache(expire=300)
def summary():
    client = get_client()
    try:
        duration_avg, duration_median, duration_max = sql_aggregation.session_duration(
            client
        )
        eps_avg, eps_median, eps_max = sql_aggregation.events_per_session(client)
        result = SummaryResponse(
            avg_items_per_transaction=sql_aggregation.avg_items_per_transaction(client),
            cart_abandonment_rate=sql_aggregation.cart_abandonment_rate(client),
            view_to_cart_rate=sql_aggregation.view_to_cart_rate(client),
            session_duration_avg=duration_avg,
            session_duration_median=duration_median,
            session_duration_max=duration_max,
            events_per_session_avg=eps_avg,
            events_per_session_median=eps_median,
            events_per_session_max=eps_max,
        )
    finally:
        client.close()
    return result
