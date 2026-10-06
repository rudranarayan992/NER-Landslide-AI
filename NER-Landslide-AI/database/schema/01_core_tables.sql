-- PostgreSQL + PostGIS schema skeleton for NER Landslide AI.
-- This file defines core tables and is intentionally a foundation for later data ingestion.

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

CREATE TABLE IF NOT EXISTS states (
    state_id SERIAL PRIMARY KEY,
    state_name VARCHAR(100) NOT NULL,
    state_code VARCHAR(20),
    geometry GEOMETRY(MultiPolygon, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS districts (
    district_id SERIAL PRIMARY KEY,
    state_id INTEGER REFERENCES states(state_id),
    district_name VARCHAR(150) NOT NULL,
    district_code VARCHAR(30),
    geometry GEOMETRY(MultiPolygon, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS villages (
    village_id SERIAL PRIMARY KEY,
    district_id INTEGER REFERENCES districts(district_id),
    village_name VARCHAR(150),
    population INTEGER,
    geometry GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roads (
    road_id SERIAL PRIMARY KEY,
    road_name VARCHAR(200),
    road_class VARCHAR(50),
    geometry GEOMETRY(LineString, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS landslides (
    event_id VARCHAR(100) PRIMARY KEY,
    event_date TIMESTAMPTZ,
    event_year INTEGER,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    state VARCHAR(100),
    district VARCHAR(150),
    subdistrict VARCHAR(150),
    village VARCHAR(150),
    location_name VARCHAR(200),
    landslide_type VARCHAR(100),
    trigger VARCHAR(100),
    severity VARCHAR(50),
    fatalities INTEGER,
    injuries INTEGER,
    infrastructure_damage BOOLEAN,
    road_blockage BOOLEAN,
    rainfall_before_event DOUBLE PRECISION,
    source_name VARCHAR(200),
    source_url TEXT,
    source_publication TEXT,
    source_date TIMESTAMPTZ,
    confidence DOUBLE PRECISION,
    geometry GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rainfall_observations (
    rainfall_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    rainfall_1h DOUBLE PRECISION,
    rainfall_3h DOUBLE PRECISION,
    rainfall_6h DOUBLE PRECISION,
    rainfall_12h DOUBLE PRECISION,
    rainfall_24h DOUBLE PRECISION,
    rainfall_3d DOUBLE PRECISION,
    rainfall_7d DOUBLE PRECISION,
    rainfall_30d DOUBLE PRECISION,
    geometry GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS soil (
    soil_id SERIAL PRIMARY KEY,
    soil_type VARCHAR(100),
    soil_texture VARCHAR(100),
    bulk_density DOUBLE PRECISION,
    soil_moisture DOUBLE PRECISION,
    organic_matter DOUBLE PRECISION,
    clay DOUBLE PRECISION,
    sand DOUBLE PRECISION,
    silt DOUBLE PRECISION,
    permeability DOUBLE PRECISION,
    geometry GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS geology (
    geology_id SERIAL PRIMARY KEY,
    lithology VARCHAR(200),
    geological_formation VARCHAR(200),
    rock_type VARCHAR(200),
    weathering_info TEXT,
    faults TEXT,
    geometry GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS terrain (
    terrain_id SERIAL PRIMARY KEY,
    elevation DOUBLE PRECISION,
    slope DOUBLE PRECISION,
    aspect DOUBLE PRECISION,
    curvature DOUBLE PRECISION,
    roughness DOUBLE PRECISION,
    topographic_wetness_index DOUBLE PRECISION,
    geometry GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS landcover (
    landcover_id SERIAL PRIMARY KEY,
    vegetation DOUBLE PRECISION,
    built_up DOUBLE PRECISION,
    agricultural_area DOUBLE PRECISION,
    forest DOUBLE PRECISION,
    bare_land DOUBLE PRECISION,
    geometry GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hydrology (
    hydrology_id SERIAL PRIMARY KEY,
    river_name VARCHAR(200),
    stream_name VARCHAR(200),
    drainage_density DOUBLE PRECISION,
    distance_to_watercourse DOUBLE PRECISION,
    geometry GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS satellite_observations (
    satellite_id SERIAL PRIMARY KEY,
    capture_timestamp TIMESTAMPTZ,
    platform VARCHAR(100),
    product_type VARCHAR(100),
    geometry GEOMETRY(Polygon, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS field_reports (
    report_id SERIAL PRIMARY KEY,
    report_timestamp TIMESTAMPTZ,
    reporter_name VARCHAR(200),
    location_name VARCHAR(200),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    observed_conditions TEXT,
    incident_type VARCHAR(100),
    notes TEXT,
    geometry GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_versions (
    model_version_id SERIAL PRIMARY KEY,
    model_name VARCHAR(200) NOT NULL,
    version_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS risk_predictions (
    prediction_id SERIAL PRIMARY KEY,
    model_version_id INTEGER REFERENCES model_versions(model_version_id),
    prediction_timestamp TIMESTAMPTZ DEFAULT NOW(),
    location_name VARCHAR(200),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    input_data_timestamps JSONB,
    features_used JSONB,
    prediction_output JSONB,
    geometry GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS data_sources (
    data_source_id SERIAL PRIMARY KEY,
    source VARCHAR(200) NOT NULL,
    source_url TEXT,
    provider VARCHAR(200),
    download_timestamp TIMESTAMPTZ,
    dataset_date TIMESTAMPTZ,
    dataset_version VARCHAR(100),
    license TEXT,
    processing_step VARCHAR(100),
    file_hash VARCHAR(128),
    geographic_coverage TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_states_geometry ON states USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_districts_geometry ON districts USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_villages_geometry ON villages USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_roads_geometry ON roads USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_landslides_geometry ON landslides USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_rainfall_geometry ON rainfall_observations USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_soil_geometry ON soil USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_geology_geometry ON geology USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_terrain_geometry ON terrain USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_landcover_geometry ON landcover USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_hydrology_geometry ON hydrology USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_field_reports_geometry ON field_reports USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_risk_predictions_geometry ON risk_predictions USING GIST (geometry);
