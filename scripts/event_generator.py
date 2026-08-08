import numpy as np
import pandas as pd

rng = np.random.default_rng(seed=42)

ROWS = 100000

ACTIONS = [
    'view',
    'view_category',
    'like',
    'unlike',
    'compare',
    'add_to_cart',
    'remove_from_cart',
    'update_cart',
    'checkout',
    'purchase',
    'purchase_success',
    'purchase_fail',
    'review',
    'share',
    'click',
    'search',
    'filter',
]

WEIGHTS = [
    0.15, 0.08, 0.12, 0.03, 0.02, 0.10, 0.05, 0.03,
    0.04, 0.06, 0.04, 0.02, 0.03, 0.02, 0.08, 0.07, 0.06,
]

CITIES = [
    'New York',
    'Los Angeles',
    'Chicago',
    'Houston',
    'Phoenix',
    'Philadelphia',
    'San Antonio',
    'San Diego',
    'Dallas',
    'San Jose',
]

MONETARY_ACTIONS = ['add_to_cart', 'checkout', 'purchase', 'purchase_success']

HOUR_WEIGHTS = np.array(
    [1, 1, 1, 1, 1, 2, 3, 5, 6, 7, 8, 9, 10, 9, 8, 7, 7, 8, 10, 9, 8, 6, 4, 2],
    dtype=float,
)
HOUR_WEIGHTS /= HOUR_WEIGHTS.sum()


def generate_data():
    user_ids = rng.integers(1, 1001, size=ROWS)
    user_actions = rng.choice(ACTIONS, size=ROWS, p=WEIGHTS)
    cities = rng.choice(CITIES, size=ROWS)

    amounts = rng.integers(1, 1000, size=ROWS)
    amounts = np.where(np.isin(user_actions, MONETARY_ACTIONS), amounts, 0)

    start_date = pd.Timestamp('2026-01-01')
    days_offset = rng.integers(0, 30, size=ROWS)
    hours = rng.choice(24, size=ROWS, p=HOUR_WEIGHTS)
    within_hour = rng.integers(0, 3599, size=ROWS)
    seconds_offset = hours * 3600 + within_hour

    timestamps = (
        start_date
        + pd.to_timedelta(days_offset, unit='D')
        + pd.to_timedelta(seconds_offset, unit='s')
    )

    df = pd.DataFrame({
        'user_id': user_ids,
        'city': cities,
        'user_action': user_actions,
        'amount': amounts,
        'timestamp': timestamps,
    })

    df.to_csv('site_actions.csv', index=False, encoding='utf-8')

    return df


if __name__ == '__main__':
    generate_data()
