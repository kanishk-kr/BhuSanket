-- BhuSanket Database Initialization
-- Enables PostGIS and required extensions

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- Fuzzy text matching for identity resolution
