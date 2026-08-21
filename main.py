from fastapi import Depends, FastAPI, Response

from schemas import (
    CityRevenue,
    DailyMetric,
    FunnelResponse,
    HealthResponse,
    SummaryResponse,
)
from scripts import sql_aggregation
from scripts.ch_client import get_client

app = FastAPI(
    title="DataMetric API",
    version="1.0.0",
)


def get_ch_client():
    client = get_client()
    try:
        yield client
    finally:
        client.close()


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Состояние сервиса",
    description="Проверка доступности ClickHouse и проверка на пустоту таблицы events",
    tags=["Health"],
)
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


@app.get(
    "/stat/funnel",
    response_model=FunnelResponse,
    summary="Конверсия по воронке",
    description="Количество пользователей, достигших этапов cart, checkout, purchase",
    tags=["Stat"],
)
def funnel(client=Depends(get_ch_client)):
    cart, checkout, purchase = sql_aggregation.funnel_conversion(client)
    return FunnelResponse(
        reached_cart=cart, reached_checkout=checkout, reached_purchase=purchase
    )


@app.get(
    "/stat/revenue-by-city",
    response_model=list[CityRevenue],
    summary="Доход по городам",
    description="Общий доход от покупок, сгруппированный по городам, отсортирован по убыванию",
    tags=["Stat"],
)
def revenue_by_city(client=Depends(get_ch_client)):
    rows = sql_aggregation.revenue_by_city(client)
    return [CityRevenue(city=row[0], revenue=row[1]) for row in rows]


@app.get(
    "/stat/daily",
    response_model=list[DailyMetric],
    summary="Показатели по дням",
    description="Количество сессий и доход по дням, отсортированы по возрастанию даты",
    tags=["Stat"],
)
def daily(client=Depends(get_ch_client)):
    rows = sql_aggregation.daily_metrics(client)
    return [
        DailyMetric(day=str(row[0]), sessions=row[1], revenue=row[2]) for row in rows
    ]


@app.get(
    "/stat/summary",
    response_model=SummaryResponse,
    summary="Сводные показатели",
    description="Агрегации: средняя стоимость заказа, частоты негативных показателей, статистика сессий",
    tags=["Stat"],
)
def summary(client=Depends(get_ch_client)):
    duration_avg, duration_median, duration_max = sql_aggregation.session_duration(
        client
    )
    eps_avg, eps_median, eps_max = sql_aggregation.events_per_session(client)

    return SummaryResponse(
        avg_order_value=sql_aggregation.avg_order_value(client),
        cart_abandonment_rate=sql_aggregation.cart_abandonment_rate(client),
        purchase_fail_rate=sql_aggregation.purchase_fail_rate(client),
        session_duration_avg=duration_avg,
        session_duration_median=duration_median,
        session_duration_max=duration_max,
        events_per_session_avg=eps_avg,
        events_per_session_median=eps_median,
        events_per_session_max=eps_max,
    )
