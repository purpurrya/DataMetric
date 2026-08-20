import logging

from scripts.ch_client import get_client
from scripts.config.logging import set_logging

set_logging()
logger = logging.getLogger(__name__)


def funnel_conversion(client):
    result = client.query("""
        SELECT
            countIf(
                user_action IN ('add_to_cart', 'remove_from_cart', 'update_cart')
            ) AS reached_cart,
            countIf(user_action = 'checkout') AS reached_checkout,
            countIf(user_action = 'purchase_success') AS reached_purchase
        FROM (
            SELECT DISTINCT session_id, user_action
            FROM datametric.events
            WHERE user_action IN (
                'add_to_cart',
                'remove_from_cart',
                'update_cart',
                'checkout',
                'purchase_success'
            )
        )
    """)
    return result.result_rows[0]


def events_per_session(client):
    result = client.query("""
        SELECT avg(cnt), median(cnt), max(cnt)
        FROM (
            SELECT session_id, count() AS cnt
            FROM events
            GROUP BY session_id
        )
    """)
    return result.result_rows[0]


def avg_order_value(client):
    result = client.query("""
        SELECT avg(amount)
        FROM events
        WHERE user_action = 'purchase_success'
    """)
    return result.result_rows[0][0]


def cart_abandonment_rate(client):
    result = client.query("""
        SELECT
            (cart_sessions - purchase_sessions) / cart_sessions AS abandonment_rate
        FROM (
            SELECT
                uniqExactIf(
                    session_id,
                    user_action IN ('add_to_cart', 'remove_from_cart', 'update_cart')
                ) AS cart_sessions,
                uniqExactIf(session_id, user_action = 'purchase_success') AS purchase_sessions
            FROM events
        )
    """)
    return result.result_rows[0][0]


def purchase_fail_rate(client):
    result = client.query("""
        SELECT
            failed_sessions / checkout_sessions AS fail_rate
        FROM (
            SELECT
                uniqExactIf(session_id, user_action = 'checkout') AS checkout_sessions,
                uniqExactIf(session_id, user_action = 'purchase_fail') AS failed_sessions
            FROM events
        )
    """)
    return result.result_rows[0][0]


def session_duration(client):
    result = client.query("""
        SELECT avg(duration), median(duration), max(duration)
        FROM (
            SELECT
                session_id,
                dateDiff('second', min(timestamp), max(timestamp)) AS duration
            FROM events
            GROUP BY session_id
        )
    """)
    return result.result_rows[0]


def revenue_by_city(client):
    result = client.query("""
        SELECT city, sum(amount) AS revenue
        FROM events
        WHERE user_action = 'purchase_success'
        GROUP BY city
        ORDER BY revenue DESC
    """)
    return result.result_rows


def daily_metrics(client):
    result = client.query("""
        SELECT
            toDate(timestamp) AS day,
            uniqExact(session_id) AS sessions,
            sumIf(amount, user_action = 'purchase_success') AS revenue
        FROM events
        GROUP BY day
        ORDER BY day
    """)
    return result.result_rows


if __name__ == "__main__":
    client = get_client()

    logger.info("funnel conversion: %s", funnel_conversion(client))
    logger.info("events per session: %s", events_per_session(client))
    logger.info("avg order value: %s", avg_order_value(client))
    logger.info("cart abandonment rate: %s", cart_abandonment_rate(client))
    logger.info("purchase fail rate: %s", purchase_fail_rate(client))
    logger.info("session duration: %s", session_duration(client))
    logger.info("revenue by city: %s", revenue_by_city(client))
    logger.info("daily metrics: %s", daily_metrics(client))
