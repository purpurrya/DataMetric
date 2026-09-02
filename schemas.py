from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(description="Статус сервиса: ok / error")
    events_rows: int = Field(description="Количество строк в таблице events")


class FunnelResponse(BaseModel):
    total_sessions: int = Field(description="Всего сессий")
    reached_cart: int = Field(description="Сессий, дошедших до корзины")
    reached_purchase: int = Field(description="Сессий, завершившихся покупкой")


class CategoryPurchases(BaseModel):
    category_id: str = Field(description="Идентификатор категории")
    purchases: int = Field(description="Количество покупок в категории")


class DailyMetric(BaseModel):
    day: str = Field(description="Дата (YYYY-MM-DD)")
    sessions: int = Field(description="Количество сессий за день")
    transactions: int = Field(description="Количество транзакций за день")


class SummaryResponse(BaseModel):
    avg_items_per_transaction: float = Field(
        description="Среднее количество товаров в транзакции"
    )
    cart_abandonment_rate: float = Field(
        description="Доля корзин, не завершившихся покупкой"
    )
    view_to_cart_rate: float = Field(
        description="Доля просмотров, приведших к добавлению в корзину"
    )
    session_duration_avg: float = Field(description="Средняя длительность сессии, сек")
    session_duration_median: float = Field(
        description="Медианная длительность сессии, сек"
    )
    session_duration_max: float = Field(
        description="Максимальная длительность сессии, сек"
    )
    events_per_session_avg: float = Field(description="Среднее число событий в сессии")
    events_per_session_median: float = Field(
        description="Медианное число событий в сессии"
    )
    events_per_session_max: float = Field(
        description="Максимальное число событий в сессии"
    )
