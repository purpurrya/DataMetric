import pytest
from fastapi.testclient import TestClient

from main import app, get_ch_client
from scripts import sql_aggregation


class _FakeClient:
    pass


@pytest.fixture(autouse=True)
def _override_ch_client():
    app.dependency_overrides[get_ch_client] = lambda: _FakeClient()
    yield
    app.dependency_overrides.clear()


def test_funnel_endpoint_returns_metrics(mocker):
    mocker.patch.object(
        sql_aggregation, "funnel_conversion", return_value=(100, 40, 10)
    )

    client = TestClient(app)
    response = client.get("/stat/funnel")

    assert response.status_code == 200
    assert response.json() == {
        "total_sessions": 100,
        "reached_cart": 40,
        "reached_purchase": 10,
    }


def test_funnel_endpoint_returns_500_when_aggregation_fails(mocker):
    mocker.patch.object(
        sql_aggregation,
        "funnel_conversion",
        side_effect=RuntimeError("clickhouse error"),
    )

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/stat/funnel")

    assert response.status_code == 500
