CREATE DATABASE IF NOT EXISTS datametric;

CREATE TABLE IF NOT EXISTS datametric.events
(
    session_id String,
    user_id UInt32,
    city LowCardinality(String),
    user_action LowCardinality(String),
    amount UInt32,
    timestamp DateTime
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(timestamp)
ORDER BY (city, user_action, timestamp);