CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS sources (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  base_url TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT sources_name_unique UNIQUE (name),
  CONSTRAINT sources_base_url_unique UNIQUE (base_url)
);

CREATE TABLE IF NOT EXISTS crawl_runs (
  id BIGSERIAL PRIMARY KEY,
  source_id BIGINT NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
  status TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT crawl_runs_status_check CHECK (status IN ('running', 'success', 'failed'))
);

CREATE TABLE IF NOT EXISTS jobs (
  id BIGSERIAL PRIMARY KEY,
  source_id BIGINT NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
  source_job_id TEXT NOT NULL,
  source_url TEXT NOT NULL,
  canonical_hash TEXT NOT NULL,
  first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT jobs_source_unique UNIQUE (source_id, source_job_id),
  CONSTRAINT jobs_canonical_hash_unique UNIQUE (canonical_hash)
);

CREATE TABLE IF NOT EXISTS job_versions (
  id BIGSERIAL PRIMARY KEY,
  job_id BIGINT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  company TEXT NOT NULL,
  location TEXT NOT NULL,
  description TEXT,
  scraped_at TIMESTAMPTZ NOT NULL,
  content_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT job_versions_unique UNIQUE (job_id, content_hash)
);

CREATE TABLE IF NOT EXISTS artifacts (
  id BIGSERIAL PRIMARY KEY,
  crawl_run_id BIGINT NOT NULL REFERENCES crawl_runs(id) ON DELETE CASCADE,
  job_version_id BIGINT REFERENCES job_versions(id) ON DELETE SET NULL,
  artifact_type TEXT NOT NULL,
  url TEXT NOT NULL,
  path TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT artifacts_unique UNIQUE (crawl_run_id, artifact_type, url)
);

CREATE INDEX IF NOT EXISTS idx_crawl_runs_source_started_at
  ON crawl_runs (source_id, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_jobs_source_last_seen_at
  ON jobs (source_id, last_seen_at DESC);

CREATE INDEX IF NOT EXISTS idx_job_versions_job_scraped_at
  ON job_versions (job_id, scraped_at DESC);

CREATE INDEX IF NOT EXISTS idx_artifacts_crawl_run
  ON artifacts (crawl_run_id);

CREATE INDEX IF NOT EXISTS idx_artifacts_job_version
  ON artifacts (job_version_id);

DROP TRIGGER IF EXISTS set_updated_at_sources ON sources;
CREATE TRIGGER set_updated_at_sources
BEFORE UPDATE ON sources
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS set_updated_at_crawl_runs ON crawl_runs;
CREATE TRIGGER set_updated_at_crawl_runs
BEFORE UPDATE ON crawl_runs
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS set_updated_at_jobs ON jobs;
CREATE TRIGGER set_updated_at_jobs
BEFORE UPDATE ON jobs
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS set_updated_at_job_versions ON job_versions;
CREATE TRIGGER set_updated_at_job_versions
BEFORE UPDATE ON job_versions
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS set_updated_at_artifacts ON artifacts;
CREATE TRIGGER set_updated_at_artifacts
BEFORE UPDATE ON artifacts
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
