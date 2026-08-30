from fastapi import Depends, FastAPI, Response

from schemas import (
    CategoryPurchases,
    DailyMetric,
    FunnelResponse,
    HealthResponse,
    SummaryResponse,
)
from scripts import sql_aggregation
from scripts.ch_client import get_client

app = FastAPI(
    title="DataMetric API",
    version="2.0.0",
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
    description="Количество сессий, дошедших до этапов cart (addtocart), purchase (transaction)",
    tags=["Stat"],
)
def funnel(client=Depends(get_ch_client)):
    total, cart, purchase = sql_aggregation.funnel_conversion(client)
    return FunnelResponse(
        total_sessions=total, reached_cart=cart, reached_purchase=purchase
    )


@app.get(
    "/stat/purchases-by-category",
    response_model=list[CategoryPurchases],
    summary="Покупки по категориям",
    description="Количество транзакций, сгруппированных по категории товара (по последней известной categoryid), отсортировано по убыванию",
    tags=["Stat"],
)
def purchases_by_category(client=Depends(get_ch_client)):
    rows = sql_aggregation.purchases_by_category(client)
    return [
        CategoryPurchases(category_id=str(row[0]), purchases=row[1]) for row in rows
    ]


@app.get(
    "/stat/daily",
    response_model=list[DailyMetric],
    summary="Показатели по дням",
    description="Количество сессий и транзакций по дням, отсортированы по возрастанию даты",
    tags=["Stat"],
)
def daily(client=Depends(get_ch_client)):
    rows = sql_aggregation.daily_metrics(client)
    return [
        DailyMetric(day=str(row[0]), sessions=row[1], transactions=row[2])
        for row in rows
    ]


@app.get(
    "/stat/summary",
    response_model=SummaryResponse,
    summary="Сводные показатели",
    description="Агрегации: среднее число товаров в заказе, cart abandonment rate, view-to-cart rate, статистика сессий",
    tags=["Stat"],
)
def summary(client=Depends(get_ch_client)):
    duration_avg, duration_median, duration_max = sql_aggregation.session_duration(
        client
    )
    eps_avg, eps_median, eps_max = sql_aggregation.events_per_session(client)

    return SummaryResponse(
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
