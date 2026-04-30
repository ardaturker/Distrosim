CREATE TABLE IF NOT EXISTS api_cache (
    cache_key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    created_at REAL NOT NULL,
    expires_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS simulations (
    id TEXT PRIMARY KEY,
    request_json TEXT NOT NULL,
    result_json TEXT NOT NULL,
    created_at REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cache_expires ON api_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_simulations_created ON simulations(created_at);
