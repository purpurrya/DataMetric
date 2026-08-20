import pandas as pd

CART_ACTIONS = ["add_to_cart", "remove_from_cart", "update_cart"]


def funnel_conversion(df: pd.DataFrame) -> None:
    """Check that observed conversion rates match the probabilities
    baked into event_generator.py (P_REACH_CART=0.4, P_REACH_CHECKOUT=0.6,
    P_PURCHASE_SUCCESS=0.8).
    """
    total_sessions = df["session_id"].nunique()

    reached_cart = df[df["user_action"].isin(CART_ACTIONS)]["session_id"].nunique()
    reached_checkout = df[df["user_action"] == "checkout"]["session_id"].nunique()
    reached_purchase = df[df["user_action"] == "purchase_success"][
        "session_id"
    ].nunique()

    print("--- funnel conversion ---")
    print(f"reach cart:      {reached_cart / total_sessions:.3f}")
    print(f"reach checkout:  {reached_checkout / reached_cart:.3f}")
    print(f"purchase success:{reached_purchase / reached_checkout:.3f}")


def events_per_session(df: pd.DataFrame) -> pd.Series:
    return df.groupby("session_id").size()


def avg_order_value(df: pd.DataFrame) -> float:
    return df[df["user_action"] == "purchase_success"]["amount"].mean()


def cart_abandonment_rate(df: pd.DataFrame) -> float:
    reached_cart = df[df["user_action"].isin(CART_ACTIONS)]["session_id"].nunique()
    reached_purchase = df[df["user_action"] == "purchase_success"][
        "session_id"
    ].nunique()
    return (reached_cart - reached_purchase) / reached_cart


def purchase_fail_rate(df: pd.DataFrame) -> float:
    reached_checkout = df[df["user_action"] == "checkout"]["session_id"].nunique()
    failed = df[df["user_action"] == "purchase_fail"]["session_id"].nunique()
    return failed / reached_checkout


def session_duration(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("session_id")["timestamp"]
        .agg(["min", "max"])
        .assign(duration_seconds=lambda x: (x["max"] - x["min"]).dt.total_seconds())
    )


def revenue_by_city(df: pd.DataFrame) -> pd.Series:
    return (
        df[df["user_action"] == "purchase_success"]
        .groupby("city")["amount"]
        .sum()
        .sort_values(ascending=False)
    )


def daily_metrics(df: pd.DataFrame) -> pd.DataFrame:
    daily_revenue = (
        df[df["user_action"] == "purchase_success"]
        .groupby(df["timestamp"].dt.date)["amount"]
        .sum()
    )
    daily_sessions = df.groupby(df["timestamp"].dt.date)["session_id"].nunique()
    return pd.DataFrame({"sessions": daily_sessions, "revenue": daily_revenue})


if __name__ == "__main__":
    df = pd.read_csv("site_actions.csv", parse_dates=["timestamp"])

    funnel_conversion(df)

    print("\n--- events per session ---")
    print(events_per_session(df).describe())

    print(f"\navg order value: {avg_order_value(df):.2f}")

    print(f"cart abandonment rate: {cart_abandonment_rate(df):.3f}")
    print(f"purchase fail rate: {purchase_fail_rate(df):.3f}")

    print("\n--- revenue by city ---")
    print(revenue_by_city(df))

    print("\n--- daily metrics ---")
    print(daily_metrics(df))

    print("\n--- session duration (seconds), summary ---")
    print(session_duration(df)["duration_seconds"].describe())
