from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    events_rows: int


class FunnelResponse(BaseModel):
    reached_cart: int
    reached_checkout: int
    reached_purchase: int


class CityRevenue(BaseModel):
    city: str
    revenue: float


class DailyMetric(BaseModel):
    day: str
    sessions: int
    revenue: float


class SummaryResponse(BaseModel):
    avg_order_value: float
    cart_abandonment_rate: float
    purchase_fail_rate: float
    session_duration_avg: float
    session_duration_median: float
    session_duration_max: float
    events_per_session_avg: float
    events_per_session_median: float
    events_per_session_max: float
