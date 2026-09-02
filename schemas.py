from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    events_rows: int


class FunnelResponse(BaseModel):
    total_sessions: int
    reached_cart: int
    reached_purchase: int


class CategoryPurchases(BaseModel):
    category_id: str
    purchases: int


class DailyMetric(BaseModel):
    day: str
    sessions: int
    transactions: int


class SummaryResponse(BaseModel):
    avg_items_per_transaction: float
    cart_abandonment_rate: float
    view_to_cart_rate: float
    session_duration_avg: float
    session_duration_median: float
    session_duration_max: float
    events_per_session_avg: float
    events_per_session_median: float
    events_per_session_max: float
