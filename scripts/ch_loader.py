import clickhouse_connect
import pandas as pd

from config import settings

def load_data(csv_path: str = "site_actions.csv") -> None:
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])

    client = clickhouse_connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        database=settings.clickhouse_db,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password,
    )

    client.insert_df("events", df)

    row_count = client.query("SELECT COUNT(*) FROM events").result_rows[0][0]
    assert row_count == len(df)


if __name__ == "__main__":
    load_data()
