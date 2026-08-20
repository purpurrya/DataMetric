import logging

import clickhouse_connect
import pandas as pd

from scripts.config.logging import set_logging
from scripts.config.settings import settings

set_logging()
logger = logging.getLogger(__name__)


def load_data(csv_path: str = "site_actions.csv") -> None:
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    logger.info("read %d rows from %s", len(df), csv_path)

    client = clickhouse_connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        database=settings.clickhouse_db,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password,
    )

    client.command("TRUNCATE TABLE events")
    client.insert_df("events", df)

    row_count = client.query("SELECT COUNT(*) FROM events").result_rows[0][0]
    logger.info("clickhouse row count after insert: %d", row_count)

    assert row_count == len(df), (
        f"row count mismatch: csv={len(df)}, clickhouse={row_count}"
    )


if __name__ == "__main__":
    load_data()
