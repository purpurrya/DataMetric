import pandas as pd

from scripts.ch_loader import _sessionize


def _events(rows: list[tuple[int, str]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["visitor_id", "timestamp"])

    df = pd.DataFrame(rows, columns=["visitor_id", "timestamp"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


def test_is_one_session():
    df = _sessionize(
        _events(
            [
                (1, "2023-01-01 00:00:00"),
                (1, "2023-01-01 00:10:00"),
                (1, "2023-01-01 00:20:00"),
            ]
        )
    )
    assert df["session_id"].nunique() == 1


def test_over_30_is_new_session():
    df = _sessionize(
        _events(
            [
                (1, "2023-01-01 00:00:00"),
                (1, "2023-01-01 00:20:00"),
                (1, "2023-01-01 00:53:00"),
            ]
        )
    )
    assert df["session_id"].nunique() == 2


def test_equal_30_is_onee_session():
    df = _sessionize(
        _events(
            [
                (1, "2023-01-01 00:00:00"),
                (1, "2023-01-01 00:20:00"),
                (1, "2023-01-01 00:50:00"),
            ]
        )
    )
    assert df["session_id"].nunique() == 1


def test_different_visitors_are_different_sessions():
    df = _sessionize(
        _events(
            [
                (1, "2023-01-01 00:00:00"),
                (2, "2023-01-01 00:10:00"),
                (1, "2023-01-01 00:20:00"),
            ]
        )
    )
    assert df["session_id"].nunique() == 2
