import logging

import pandas as pd

from scripts.ch_loader import _sessionize
from scripts.config.logging import set_logging

set_logging()
logger = logging.getLogger(__name__)


def funnel_conversion(df: pd.DataFrame) -> tuple[int, int, int]:
    total_sessions = df["session_id"].nunique()
    reached_cart = df[df["event_type"] == "addtocart"]["session_id"].nunique()
    reached_purchase = df[df["event_type"] == "transaction"]["session_id"].nunique()
    return total_sessions, reached_cart, reached_purchase


def events_per_session(df: pd.DataFrame) -> pd.Series:
    return df.groupby("session_id").size()


def avg_items_per_transaction(df: pd.DataFrame) -> float:
    purchases = df[df["event_type"] == "transaction"].dropna(subset=["transaction_id"])
    return purchases.groupby("transaction_id").size().mean()


def cart_abandonment_rate(df: pd.DataFrame) -> float:
    cart_sessions = df[df["event_type"] == "addtocart"]["session_id"].nunique()
    purchase_sessions = df[df["event_type"] == "transaction"]["session_id"].nunique()
    return (cart_sessions - purchase_sessions) / cart_sessions


def view_to_cart_rate(df: pd.DataFrame) -> float:
    total_sessions = df["session_id"].nunique()
    reached_cart = df[df["event_type"] == "addtocart"]["session_id"].nunique()
    return reached_cart / total_sessions


def session_duration(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("session_id")["timestamp"]
        .agg(["min", "max"])
        .assign(duration_seconds=lambda x: (x["max"] - x["min"]).dt.total_seconds())
    )


def purchases_by_category(df: pd.DataFrame, item_categories: pd.Series) -> pd.Series:
    """item_categories: item_id -> category_id (см. загрузку ниже)."""
    purchases = df[df["event_type"] == "transaction"].copy()
    purchases["category_id"] = purchases["item_id"].map(item_categories)
    return purchases.groupby("category_id").size().sort_values(ascending=False)


def daily_metrics(df: pd.DataFrame) -> pd.DataFrame:
    daily_sessions = df.groupby(df["timestamp"].dt.date)["session_id"].nunique()
    daily_transactions = (
        df[df["event_type"] == "transaction"]
        .groupby(df["timestamp"].dt.date)
        .size()
        .reindex(daily_sessions.index, fill_value=0)
    )
    return pd.DataFrame(
        {"sessions": daily_sessions, "transactions": daily_transactions}
    )


if __name__ == "__main__":
    events_df = pd.read_csv("data/raw/events.csv")
    events_df["timestamp"] = pd.to_datetime(events_df["timestamp"], unit="ms")
    events_df = events_df.rename(
        columns={
            "visitorid": "visitor_id",
            "itemid": "item_id",
            "event": "event_type",
            "transactionid": "transaction_id",
        }
    )

    events_df = _sessionize(events_df)

    logger.info("funnel conversion: %s", funnel_conversion(events_df))
    logger.info("events per session:\n%s", events_per_session(events_df).describe())
    logger.info("avg items per transaction: %s", avg_items_per_transaction(events_df))
    logger.info("cart abandonment rate: %s", cart_abandonment_rate(events_df))
    logger.info("view to cart rate: %s", view_to_cart_rate(events_df))
    logger.info("daily metrics:\n%s", daily_metrics(events_df))
    logger.info(
        "session duration:\n%s",
        session_duration(events_df)["duration_seconds"].describe(),
    )
