import os

import httpx
import pandas as pd
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="DataMetric", layout="wide")
st.title("DataMetric")


@st.cache_data(ttl=60)
def fetch(path: str):
    response = httpx.get(f"{API_URL}{path}", timeout=10)
    response.raise_for_status()
    return response.json()


try:
    funnel = fetch("/stat/funnel")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total sessions", funnel["total_sessions"])
    col2.metric("Reached cart", funnel["reached_cart"])
    col3.metric("Purchased", funnel["reached_purchase"])

    st.divider()

    summary = fetch("/stat/summary")
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Items per order (avg)", round(summary["avg_items_per_transaction"], 2)
    )
    col2.metric("Cart abandonment", f"{summary['cart_abandonment_rate']:.1%}")
    col3.metric("View-to-cart conversion", f"{summary['view_to_cart_rate']:.1%}")

    st.divider()

    st.subheader("Sessions and transactions by day")
    daily = pd.DataFrame(fetch("/stat/daily"))
    daily["day"] = pd.to_datetime(daily["day"])
    st.line_chart(daily.set_index("day")[["sessions", "transactions"]])

    st.divider()

    st.subheader("Purchases by category")
    categories = pd.DataFrame(fetch("/stat/purchases-by-category"))
    st.bar_chart(categories.set_index("category_id")["purchases"])

except httpx.RequestError:
    st.error(
        f"Could not connect to the API at {API_URL}. "
        "Make sure the service is running"
    )
except httpx.HTTPStatusError as exc:
    st.error(f"API returned an error: {exc.response.status_code} {exc.response.text}")
