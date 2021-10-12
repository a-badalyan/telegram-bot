CREATE TABLE IF NOT EXISTS data(
    bid_id INTEGER UNIQUE NOT NULL,
    organization_name VARCHAR,
    bid_status VARCHAR,
    published DATE,
    usage_list VARCHAR,
    location_name VARCHAR,
    cadastral_num VARCHAR,
    area VARCHAR,
    startPrice NUMERIC,
    link VARCHAR
);

SELECT * FROM data ORDER BY published DESC LIMIT 20