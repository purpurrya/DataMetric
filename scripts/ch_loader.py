import logging
from pathlib import Path

import pandas as pd

from scripts.ch_client import get_client
from scripts.config.logging import set_logging
from scripts.config.settings import settings

set_logging()
logger = logging.getLogger(__name__)

SESSION_GAP = pd.Timedelta(minutes=30)
KEPT_PROPERTIES = ("categoryid", "available")


def _sessionize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["visitor_id", "timestamp"]).reset_index(drop=True)
    gap = df.groupby("visitor_id")["timestamp"].diff()
    is_new_session = gap.isna() | (gap > SESSION_GAP)
    session_seq = is_new_session.groupby(df["visitor_id"]).cumsum()
    df["session_id"] = df["visitor_id"].astype(str) + "-" + session_seq.astype(str)
    return df


def load_events(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.rename(
        columns={
            "visitorid": "visitor_id",
            "itemid": "item_id",
            "event": "event_type",
            "transactionid": "transaction_id",
        }
    )
    df["transaction_id"] = df["transaction_id"].astype("Int64")
    df = _sessionize(df)
    return df[
        [
            "session_id",
            "visitor_id",
            "item_id",
            "event_type",
            "transaction_id",
            "timestamp",
        ]
    ]


def load_item_properties(paths: list[Path]) -> pd.DataFrame:
    frames = [pd.read_csv(p) for p in paths]
    df = pd.concat(frames, ignore_index=True)
    df = df[df["property"].isin(KEPT_PROPERTIES)].copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.rename(columns={"itemid": "item_id"})
    return df[["timestamp", "item_id", "property", "value"]]


def load_category_tree(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["parentid"] = df["parentid"].astype("Int64")
    return df[["categoryid", "parentid"]]


def main() -> None:
    data_dir = Path(settings.data_dir)

    events = load_events(data_dir / "events.csv")
    logger.info("read %d event rows", len(events))

    item_props = load_item_properties(
        [data_dir / "item_properties_part1.csv", data_dir / "item_properties_part2.csv"]
    )
    logger.info(
        "read %d item_properties rows (categoryid/available only)", len(item_props)
    )

    categories = load_category_tree(data_dir / "category_tree.csv")
    logger.info("read %d category_tree rows", len(categories))

    client = get_client()

    client.command("TRUNCATE TABLE events")
    client.insert_df("events", events)

    client.command("TRUNCATE TABLE item_properties")
    client.insert_df("item_properties", item_props)

    client.command("TRUNCATE TABLE category_tree")
    client.insert_df("category_tree", categories)

    counts = {
        "events": client.query("SELECT COUNT(*) FROM events").result_rows[0][0],
        "item_properties": client.query(
            "SELECT COUNT(*) FROM item_properties"
        ).result_rows[0][0],
        "category_tree": client.query("SELECT COUNT(*) FROM category_tree").result_rows[
            0
        ][0],
    }
    logger.info("row counts after insert: %s", counts)

    assert counts["events"] == len(events), "events row count mismatch"
    assert counts["item_properties"] == len(item_props), (
        "item_properties row count mismatch"
    )
    assert counts["category_tree"] == len(categories), (
        "category_tree row count mismatch"
    )


if __name__ == "__main__":
    main()
