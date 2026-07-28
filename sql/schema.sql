CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    radius_km DOUBLE PRECISION NOT NULL DEFAULT 800
);

CREATE TABLE IF NOT EXISTS aircraft (
    icao24 VARCHAR(8) PRIMARY KEY,
    callsign VARCHAR(20),
    origin_country VARCHAR(100),
    time_position TIMESTAMP,
    last_contact TIMESTAMP,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    baro_altitude DOUBLE PRECISION,
    velocity DOUBLE PRECISION,
    true_track DOUBLE PRECISION,
    vertical_rate DOUBLE PRECISION,
    geo_altitude DOUBLE PRECISION,
    squawk VARCHAR(4),
    spi BOOLEAN,
    country_id INT REFERENCES countries(id) ON DELETE SET NULL
);
