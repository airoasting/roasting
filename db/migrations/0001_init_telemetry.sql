CREATE TABLE roasting_telemetry (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID NOT NULL,
    skill_version TEXT NOT NULL,
    case_id TEXT NOT NULL,
    final_score NUMERIC(3,1),
    round_count INT,
    slide_template_id TEXT,
    total_cost_usd NUMERIC(10,4),
    anti_patterns_detected JSONB,
    debate_triggered BOOLEAN,
    completion_status TEXT CHECK (completion_status IN ('passed','forced','user_aborted'))
);

CREATE INDEX idx_telemetry_case_id ON roasting_telemetry(case_id);
CREATE INDEX idx_telemetry_user_id ON roasting_telemetry(user_id);
CREATE INDEX idx_telemetry_timestamp ON roasting_telemetry(timestamp DESC);

-- Disable row-level reads except for service role.
ALTER TABLE roasting_telemetry ENABLE ROW LEVEL SECURITY;

-- Anonymous inserts only (no SELECT).
CREATE POLICY anon_insert ON roasting_telemetry
    FOR INSERT TO anon WITH CHECK (true);
