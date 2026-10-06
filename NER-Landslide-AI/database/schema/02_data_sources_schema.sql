-- Additional provenance-focused schema for dataset registration.

CREATE TABLE IF NOT EXISTS external_dataset_registry (
    dataset_id SERIAL PRIMARY KEY,
    source VARCHAR(200) NOT NULL,
    source_url TEXT,
    provider VARCHAR(200),
    dataset_name VARCHAR(200),
    dataset_version VARCHAR(100),
    dataset_date TIMESTAMPTZ,
    download_timestamp TIMESTAMPTZ,
    license TEXT,
    geographic_coverage TEXT,
    processing_step VARCHAR(100),
    file_hash VARCHAR(128),
    status VARCHAR(50) DEFAULT 'registered',
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
