import pandas as pd

from scripts import aggregation


def test_funnel_conversion_counts_full_conversion():
    df = pd.DataFrame(
        {
            "session_id": ["s1", "s1", "s1"],
            "event_type": ["view", "addtocart", "transaction"],
        }
    )

    total, cart, purchase = aggregation.funnel_conversion(df)

    assert (total, cart, purchase) == (1, 1, 1)


def test_funnel_conversion_session_without_conversion():
    df = pd.DataFrame(
        {
            "session_id": ["s1", "s2"],
            "event_type": ["view", "view"],
        }
    )

    total, cart, purchase = aggregation.funnel_conversion(df)

    assert (total, cart, purchase) == (2, 0, 0)


def test_cart_abandonment_rate_with_abandoned_cart():
    df = pd.DataFrame(
        {
            "session_id": ["s1", "s2", "s2"],
            "event_type": ["addtocart", "addtocart", "transaction"],
        }
    )

    assert aggregation.cart_abandonment_rate(df) == 0.5


def test_cart_abandonment_rate_with_no_abandonment():
    df = pd.DataFrame(
        {
            "session_id": ["s1", "s1"],
            "event_type": ["addtocart", "transaction"],
        }
    )

    assert aggregation.cart_abandonment_rate(df) == 0.0
