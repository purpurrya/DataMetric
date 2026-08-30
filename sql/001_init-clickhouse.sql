CREATE DATABASE IF NOT EXISTS datametric;

CREATE TABLE IF NOT EXISTS datametric.events
(
    session_id String,
    visitor_id UInt32,
    item_id UInt32,
    event_type LowCardinality(String),
    transaction_id Nullable(UInt32),
    timestamp DateTime
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(timestamp)
ORDER BY (event_type, timestamp);

CREATE TABLE IF NOT EXISTS datametric.item_properties
(
    timestamp DateTime,
    item_id   UInt32,
    property  LowCardinality(String),
    value     String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(timestamp)
ORDER BY (item_id, property, timestamp);

CREATE TABLE IF NOT EXISTS datametric.category_tree
(
    categoryid UInt32,
    parentid   Nullable(UInt32)
)
ENGINE = MergeTree
ORDER BY categoryid;