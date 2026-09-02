import logging

from scripts.config.logging import set_logging

set_logging()
logger = logging.getLogger(__name__)


async def funnel_conversion(client):
    result = await client.query("""
        SELECT
            uniqExact(session_id) AS total_sessions,
            uniqExactIf(session_id, event_type = 'addtocart') AS reached_cart,
            uniqExactIf(session_id, event_type = 'transaction') AS reached_purchase
        FROM events
    """)
    return result.result_rows[0]


async def events_per_session(client):
    result = await client.query("""
        SELECT avg(cnt), median(cnt), max(cnt)
        FROM (SELECT session_id, count() AS cnt FROM events GROUP BY session_id)
    """)
    return result.result_rows[0]


async def avg_items_per_transaction(client):
    result = await client.query("""
        SELECT avg(item_count)
        FROM (
            SELECT transaction_id, count() AS item_count
            FROM events
            WHERE event_type = 'transaction' AND transaction_id IS NOT NULL
            GROUP BY transaction_id
        )
    """)
    return result.result_rows[0][0]


async def cart_abandonment_rate(client):
    result = await client.query("""
        SELECT (cart_sessions - purchase_sessions) / cart_sessions AS abandonment_rate
        FROM (
            SELECT
                uniqExactIf(session_id, event_type = 'addtocart') AS cart_sessions,
                uniqExactIf(session_id, event_type = 'transaction') AS purchase_sessions
            FROM events
        )
    """)
    return result.result_rows[0][0]


async def view_to_cart_rate(client):
    result = await client.query("""
        SELECT reached_cart / total_sessions AS rate
        FROM (
            SELECT
                uniqExact(session_id) AS total_sessions,
                uniqExactIf(session_id, event_type = 'addtocart') AS reached_cart
            FROM events
        )
    """)
    return result.result_rows[0][0]


async def session_duration(client):
    result = await client.query("""
        SELECT avg(duration), median(duration), max(duration)
        FROM (
            SELECT session_id, dateDiff('second', min(timestamp), max(timestamp)) AS duration
            FROM events
            GROUP BY session_id
        )
    """)
    return result.result_rows[0]


async def purchases_by_category(client, limit: int = 20):
    result = await client.query(f"""
        WITH item_category AS (
            SELECT item_id, argMax(value, timestamp) AS category_id
            FROM item_properties
            WHERE property = 'categoryid'
            GROUP BY item_id
        )
        SELECT ic.category_id AS category_id, count() AS purchases
        FROM events AS e
        INNER JOIN item_category AS ic ON e.item_id = ic.item_id
        WHERE e.event_type = 'transaction'
        GROUP BY category_id
        ORDER BY purchases DESC
        LIMIT {limit}
    """)
    return result.result_rows


async def daily_metrics(client):
    result = await client.query("""
        SELECT toDate(timestamp) AS day, uniqExact(session_id) AS sessions,
               countIf(event_type = 'transaction') AS transactions
        FROM events
        GROUP BY day
        ORDER BY day
    """)
    return result.result_rows


async def _main():
    from scripts.ch_client import get_async_client

    client = await get_async_client()
    try:
        logger.info("funnel conversion: %s", await funnel_conversion(client))
        logger.info("events per session: %s", await events_per_session(client))
        logger.info(
            "avg items per transaction: %s", await avg_items_per_transaction(client)
        )
        logger.info("cart abandonment rate: %s", await cart_abandonment_rate(client))
        logger.info("view to cart rate: %s", await view_to_cart_rate(client))
        logger.info("session duration: %s", await session_duration(client))
        logger.info("purchases by category: %s", await purchases_by_category(client))
        logger.info("daily metrics: %s", await daily_metrics(client))
    finally:
        await client.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(_main())
