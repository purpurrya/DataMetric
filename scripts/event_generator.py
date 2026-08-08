import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

N_USERS = 2000
N_SESSIONS = 20000
DAYS = 30
START_DATE = pd.Timestamp('2026-01-01')

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

BROWSE_ACTIONS = [
    'view',
    'view_category',
    'like',
    'unlike',
    'compare',
    'share',
    'click',
    'search',
    'filter',
]

CART_ACTIONS = ['add_to_cart', 'remove_from_cart', 'update_cart']

MONETARY_ACTIONS = {'add_to_cart', 'checkout', 'purchase', 'purchase_success'}

P_REACH_CART = 0.4
P_REACH_CHECKOUT = 0.6
P_PURCHASE_SUCCESS = 0.8
P_LEAVE_REVIEW = 0.3

HOUR_WEIGHTS = np.array(
    [1, 1, 1, 1, 1, 2, 3, 5, 6, 7, 8, 9, 10, 9, 8, 7, 7, 8, 10, 9, 8, 6, 4, 2],
    dtype=float,
)
HOUR_WEIGHTS /= HOUR_WEIGHTS.sum()


def random_amount():
    return int(RNG.integers(1, 1000))


def build_session(user_id, city, session_id, session_start):
    events = []
    t = session_start

    def add_event(action):
        nonlocal t
        events.append({
            'session_id': session_id,
            'user_id': user_id,
            'city': city,
            'user_action': action,
            'amount': random_amount() if action in MONETARY_ACTIONS else 0,
            'timestamp': t,
        })
        t += pd.Timedelta(seconds=int(RNG.integers(1, 300)))

    for _ in range(int(RNG.integers(1, 10))):
        add_event(RNG.choice(BROWSE_ACTIONS))

    if RNG.random() < P_REACH_CART:
        add_event(RNG.choice(CART_ACTIONS, p=[0.5, 0.3, 0.2]))

        if RNG.random() < P_REACH_CHECKOUT:
            add_event('checkout')

            if RNG.random() < P_PURCHASE_SUCCESS:
                add_event('purchase')
                add_event('purchase_success')

                if RNG.random() < P_LEAVE_REVIEW:
                    add_event('review')
            else:
                add_event('purchase_fail')

    return events


def session_start_time():
    day_offset = int(RNG.integers(0, DAYS))
    hour = int(RNG.choice(24, p=HOUR_WEIGHTS))
    minute = int(RNG.integers(0, 60))
    return START_DATE + pd.Timedelta(days=day_offset, hours=hour, minutes=minute)


def generate_data():
    all_events = []

    for i in range(N_SESSIONS):
        user_id = int(RNG.integers(0, N_USERS))
        city = RNG.choice(CITIES)
        session_start = session_start_time()

        all_events.extend(build_session(user_id, city, f'sess-{i}', session_start))

    df = pd.DataFrame(all_events)
    df.to_csv('site_actions.csv', index=False, encoding='utf-8')

    return df


if __name__ == '__main__':
    generate_data()
