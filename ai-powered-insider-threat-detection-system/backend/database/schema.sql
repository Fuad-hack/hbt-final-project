-- ═══════════════════════════════════════════════════════════════════════════
-- ITDT - AI-Powered Insider Threat Detection System
-- Production-Ready PostgreSQL Database Schema
-- Schema: threat_detection
-- ═══════════════════════════════════════════════════════════════════════════

-- Create schema
CREATE SCHEMA IF NOT EXISTS threat_detection;
SET search_path TO threat_detection;

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. CORE TABLES (must be created first for FK references)
-- ═══════════════════════════════════════════════════════════════════════════

-- USERS TABLE: Central reference table for all user-related data
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    department VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

COMMENT ON TABLE users IS 'Master table for all system users, referenced by all log and feature tables';

-- Create index on username for fast lookups
CREATE INDEX idx_users_username ON users(username);

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. RAW LOG TABLES (from simulate_logs.py)
-- ═══════════════════════════════════════════════════════════════════════════

-- LOGIN_SESSIONS: Daily login/logout records for each user
CREATE TABLE login_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    login_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    logout_time TIMESTAMP WITH TIME ZONE,
    session_duration_minutes INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (logout_time - login_time))/60
    ) STORED,
    
    CONSTRAINT valid_session CHECK (logout_time IS NULL OR logout_time > login_time)
);

COMMENT ON TABLE login_sessions IS 'Daily login/logout session records for behavioral analysis';

-- Indexes for common queries
CREATE INDEX idx_login_sessions_user ON login_sessions(user_id);
CREATE INDEX idx_login_sessions_time ON login_sessions(login_time);
CREATE INDEX idx_login_sessions_user_time ON login_sessions(user_id, login_time);

-- FILE_ACCESS_LOGS: Records of user file accesses
CREATE TABLE file_access_logs (
    access_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    access_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    file_size_bytes BIGINT,
    operation_type VARCHAR(20) DEFAULT 'read' -- read, write, delete
);

COMMENT ON TABLE file_access_logs IS 'User file access events for insider threat detection';

CREATE INDEX idx_file_access_user ON file_access_logs(user_id);
CREATE INDEX idx_file_access_time ON file_access_logs(access_time);
CREATE INDEX idx_file_access_user_time ON file_access_logs(user_id, access_time);

-- USB_USAGE_LOGS: USB device plug/unplug records
CREATE TABLE usb_usage_logs (
    usb_event_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    device_id VARCHAR(100) NOT NULL,
    plug_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    unplug_time TIMESTAMP WITH TIME ZONE,
    device_name VARCHAR(255),
    
    CONSTRAINT valid_usb_usage CHECK (unplug_time IS NULL OR unplug_time > plug_time)
);

COMMENT ON TABLE usb_usage_logs IS 'USB device connection/disconnection tracking for data exfiltration detection';

CREATE INDEX idx_usb_user ON usb_usage_logs(user_id);
CREATE INDEX idx_usb_time ON usb_usage_logs(plug_time);
CREATE INDEX idx_usb_user_time ON usb_usage_logs(user_id, plug_time);

-- EMAIL_LOGS: Sent email records with recipient tracking
CREATE TABLE email_logs (
    email_id SERIAL PRIMARY KEY,
    sender_user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    sender_email VARCHAR(100) NOT NULL,
    recipient_email VARCHAR(100) NOT NULL,
    sent_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    subject VARCHAR(500),
    body_text TEXT,
    has_attachments BOOLEAN DEFAULT FALSE,
    attachment_count INTEGER DEFAULT 0,
    is_external BOOLEAN DEFAULT FALSE -- flag for external recipients
);

COMMENT ON TABLE email_logs IS 'Email communication records for detecting suspicious outbound data transfers';

CREATE INDEX idx_email_sender ON email_logs(sender_user_id);
CREATE INDEX idx_email_time ON email_logs(sent_time);
CREATE INDEX idx_email_sender_time ON email_logs(sender_user_id, sent_time);
CREATE INDEX idx_email_external ON email_logs(is_external) WHERE is_external = TRUE;

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. FEATURE ENGINEERING TABLES
-- ═══════════════════════════════════════════════════════════════════════════

-- BEHAVIORAL_FEATURES: Calculated behavioral metrics per user
CREATE TABLE behavioral_features (
    feature_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    calculation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Login/Logout patterns
    mean_login_hour DECIMAL(4,2) CHECK (mean_login_hour >= 0 AND mean_login_hour <= 24),
    mean_logout_hour DECIMAL(4,2) CHECK (mean_logout_hour >= 0 AND mean_logout_hour <= 24),
    std_login_hour DECIMAL(4,2) CHECK (std_login_hour >= 0),
    
    -- Activity rates (per day)
    files_per_day DECIMAL(6,2) CHECK (files_per_day >= 0),
    usb_per_day DECIMAL(6,2) CHECK (usb_per_day >= 0),
    emails_per_day DECIMAL(6,2) CHECK (emails_per_day >= 0),
    
    -- Anomaly indicators
    out_of_session_access INTEGER CHECK (out_of_session_access >= 0),
    after_hours_logins INTEGER CHECK (after_hours_logins >= 0),
    weekend_activity_count INTEGER CHECK (weekend_activity_count >= 0),
    
    UNIQUE(user_id, calculation_date)
);

COMMENT ON TABLE behavioral_features IS 'Engineered behavioral features extracted from raw logs for ML model input';

CREATE INDEX idx_behavioral_user ON behavioral_features(user_id);
CREATE INDEX idx_behavioral_date ON behavioral_features(calculation_date);
CREATE INDEX idx_behavioral_user_date ON behavioral_features(user_id, calculation_date);

-- GRAPH_FEATURES: NetworkX graph centrality metrics
CREATE TABLE graph_features (
    graph_feature_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    calculation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Graph centrality metrics (0-1 range)
    degree_centrality DECIMAL(5,4) CHECK (degree_centrality >= 0 AND degree_centrality <= 1),
    betweenness_centrality DECIMAL(5,4) CHECK (betweenness_centrality >= 0 AND betweenness_centrality <= 1),
    closeness_centrality DECIMAL(5,4) CHECK (closeness_centrality >= 0 AND closeness_centrality <= 1),
    eigenvector_centrality DECIMAL(5,4) CHECK (eigenvector_centrality >= 0 AND eigenvector_centrality <= 1),
    clustering_coefficient DECIMAL(5,4) CHECK (clustering_coefficient >= 0 AND clustering_coefficient <= 1),
    
    UNIQUE(user_id, calculation_date)
);

COMMENT ON TABLE graph_features IS 'Graph network analysis features from user-file-USB bipartite graph';

CREATE INDEX idx_graph_user ON graph_features(user_id);
CREATE INDEX idx_graph_date ON graph_features(calculation_date);
CREATE INDEX idx_graph_user_date ON graph_features(user_id, calculation_date);

-- NLP_EMAIL_FEATURES: Natural language processing results for emails
CREATE TABLE nlp_email_features (
    nlp_feature_id SERIAL PRIMARY KEY,
    email_id INTEGER REFERENCES email_logs(email_id) ON DELETE CASCADE,
    sender_user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Suspicious keyword detection
    keyword_flag BOOLEAN DEFAULT FALSE,
    suspicious_keywords TEXT[], -- array of found keywords: ['confidential', 'urgent', 'password', 'secret', 'invoice', 'transfer']
    keyword_count INTEGER CHECK (keyword_count >= 0),
    
    -- Text features
    subject_len INTEGER CHECK (subject_len >= 0),
    body_len INTEGER CHECK (body_len >= 0),
    
    -- Sentiment analysis
    sentiment_score DECIMAL(5,4) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    sentiment_label VARCHAR(20), -- positive, negative, neutral
    
    urgency_score DECIMAL(5,4) CHECK (urgency_score >= 0 AND urgency_score <= 1),
    
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE nlp_email_features IS 'NLP extracted features from email content for detecting suspicious communications';

CREATE INDEX idx_nlp_sender ON nlp_email_features(sender_user_id);
CREATE INDEX idx_nlp_keyword ON nlp_email_features(keyword_flag) WHERE keyword_flag = TRUE;
CREATE INDEX idx_nlp_analyzed ON nlp_email_features(analyzed_at);

-- Partial index for suspicious emails only (requirement #9)
CREATE INDEX idx_nlp_suspicious ON nlp_email_features (sender_user_id, keyword_flag, urgency_score) 
WHERE keyword_flag = TRUE;

-- ═══════════════════════════════════════════════════════════════════════════
-- 4. MERGED_FEATURES: Combined features for model training
-- Relationship: merged_features aggregates data from behavioral_features, 
-- graph_features, and nlp_email_features through a materialized view pattern
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE merged_features (
    merged_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    calculation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Reference to source feature records
    behavioral_feature_id INTEGER REFERENCES behavioral_features(feature_id),
    graph_feature_id INTEGER REFERENCES graph_features(graph_feature_id),
    
    -- Behavioral features (copied/aggregated)
    mean_login_hour DECIMAL(4,2) CHECK (mean_login_hour >= 0 AND mean_login_hour <= 24),
    mean_logout_hour DECIMAL(4,2) CHECK (mean_logout_hour >= 0 AND mean_logout_hour <= 24),
    files_per_day DECIMAL(6,2) CHECK (files_per_day >= 0),
    usb_per_day DECIMAL(6,2) CHECK (usb_per_day >= 0),
    emails_per_day DECIMAL(6,2) CHECK (emails_per_day >= 0),
    out_of_session_access INTEGER CHECK (out_of_session_access >= 0),
    
    -- Graph features
    degree_centrality DECIMAL(5,4) CHECK (degree_centrality >= 0 AND degree_centrality <= 1),
    betweenness_centrality DECIMAL(5,4) CHECK (betweenness_centrality >= 0 AND betweenness_centrality <= 1),
    
    -- NLP aggregated features (aggregated by user)
    keyword_flag BOOLEAN DEFAULT FALSE,
    avg_subject_len DECIMAL(6,2) CHECK (avg_subject_len >= 0),
    avg_sentiment DECIMAL(5,4) CHECK (avg_sentiment >= -1 AND avg_sentiment <= 1),
    suspicious_email_ratio DECIMAL(5,4) CHECK (suspicious_email_ratio >= 0 AND suspicious_email_ratio <= 1),
    
    -- Target variable for training
    is_red_team BOOLEAN DEFAULT FALSE,
    
    UNIQUE(user_id, calculation_date)
);

COMMENT ON TABLE merged_features IS 'Consolidated feature set combining behavioral, graph, and NLP features for ML model training (1:1 relationship with behavioral and graph features, N:1 aggregation from NLP features)';

CREATE INDEX idx_merged_user ON merged_features(user_id);
CREATE INDEX idx_merged_date ON merged_features(calculation_date);
CREATE INDEX idx_merged_user_date ON merged_features(user_id, calculation_date);
CREATE INDEX idx_merged_redteam ON merged_features(is_red_team) WHERE is_red_team = TRUE;

-- ═══════════════════════════════════════════════════════════════════════════
-- 5. MODEL RUNS AND ANOMALY SCORES
-- ═══════════════════════════════════════════════════════════════════════════

-- MODEL_RUNS: Metadata for each training session
CREATE TABLE model_runs (
    run_id SERIAL PRIMARY KEY,
    run_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- IsolationForest, OneClassSVM, Autoencoder
    run_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    training_date_start DATE NOT NULL,
    training_date_end DATE NOT NULL,
    
    -- Model hyperparameters (stored as JSON for flexibility)
    hyperparameters JSONB,
    
    -- Model performance metrics
    training_samples INTEGER CHECK (training_samples > 0),
    contamination_rate DECIMAL(4,3) CHECK (contamination_rate >= 0 AND contamination_rate <= 1),
    precision_score DECIMAL(5,4) CHECK (precision_score >= 0 AND precision_score <= 1),
    recall_score DECIMAL(5,4) CHECK (recall_score >= 0 AND recall_score <= 1),
    f1_score DECIMAL(5,4) CHECK (f1_score >= 0 AND f1_score <= 1),
    
    model_file_path VARCHAR(500),
    is_active BOOLEAN DEFAULT FALSE,
    notes TEXT
);

COMMENT ON TABLE model_runs IS 'Training session metadata and model performance metrics for ML pipeline tracking';

CREATE INDEX idx_model_runs_time ON model_runs(run_timestamp);
CREATE INDEX idx_model_runs_type ON model_runs(model_type);
CREATE INDEX idx_model_runs_active ON model_runs(is_active) WHERE is_active = TRUE;

-- ANOMALY_SCORES: Individual model predictions for each user
CREATE TABLE anomaly_scores (
    score_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    run_id INTEGER NOT NULL REFERENCES model_runs(run_id) ON DELETE CASCADE,
    calculation_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Individual model scores
    isolation_forest_score DECIMAL(5,4) CHECK (isolation_forest_score >= 0 AND isolation_forest_score <= 1),
    oneclass_svm_score DECIMAL(5,4),
    autoencoder_score DECIMAL(5,4) CHECK (autoencoder_score >= 0),
    
    -- Combined/Aggregated score (calculated via trigger or view)
    composite_score DECIMAL(5,4) CHECK (composite_score >= 0 AND composite_score <= 1),
    
    -- Classification
    is_anomaly BOOLEAN DEFAULT FALSE,
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    
    UNIQUE(user_id, run_id)
);

COMMENT ON TABLE anomaly_scores IS 'Anomaly detection scores from 3 ML models (IsolationForest, OneClassSVM, Autoencoder) per user';

CREATE INDEX idx_scores_user ON anomaly_scores(user_id);
CREATE INDEX idx_scores_run ON anomaly_scores(run_id);
CREATE INDEX idx_scores_composite ON anomaly_scores(composite_score);
CREATE INDEX idx_scores_anomaly ON anomaly_scores(is_anomaly, risk_level) WHERE is_anomaly = TRUE;
CREATE INDEX idx_scores_user_run ON anomaly_scores(user_id, run_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- 6. XAI (EXPLAINABILITY) TABLE
-- ═══════════════════════════════════════════════════════════════════════════

-- XAI_EXPLANATIONS: SHAP and LIME explanations for model predictions
CREATE TABLE xai_explanations (
    explanation_id SERIAL PRIMARY KEY,
    score_id INTEGER NOT NULL REFERENCES anomaly_scores(score_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    explanation_type VARCHAR(20) NOT NULL CHECK (explanation_type IN ('SHAP', 'LIME', 'LIME_LOCAL')),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- SHAP global feature importance (JSON)
    shap_feature_importance JSONB,
    
    -- LIME local explanation (JSON array of feature-weight pairs)
    lime_explanations JSONB,
    
    -- Top contributing features (pre-calculated for quick access)
    top_feature_1 VARCHAR(50),
    top_feature_1_weight DECIMAL(6,4),
    top_feature_2 VARCHAR(50),
    top_feature_2_weight DECIMAL(6,4),
    top_feature_3 VARCHAR(50),
    top_feature_3_weight DECIMAL(6,4),
    
    explanation_summary TEXT
);

COMMENT ON TABLE xai_explanations IS 'SHAP and LIME explainability results for high-risk user anomaly predictions';

CREATE INDEX idx_xai_score ON xai_explanations(score_id);
CREATE INDEX idx_xai_user ON xai_explanations(user_id);
CREATE INDEX idx_xai_type ON xai_explanations(explanation_type);
CREATE INDEX idx_xai_highrisk ON xai_explanations(user_id, explanation_type) 
WHERE explanation_type = 'SHAP';

-- ═══════════════════════════════════════════════════════════════════════════
-- 7. RED TEAM TABLE
-- ═══════════════════════════════════════════════════════════════════════════

-- RED_TEAM_FLAGS: Tracking injected malicious behaviors for model validation
CREATE TABLE red_team_flags (
    flag_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    injected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Red team exercise details
    exercise_name VARCHAR(100),
    injected_behavior VARCHAR(100) NOT NULL, -- 'after_hours_access', 'mass_download', 'suspicious_usb'
    behavior_description TEXT,
    
    -- Attack simulation parameters
    data_volume_mb INTEGER CHECK (data_volume_mb >= 0),
    target_file_count INTEGER CHECK (target_file_count >= 0),
    
    -- Detection tracking
    was_detected BOOLEAN DEFAULT FALSE,
    detection_time TIMESTAMP WITH TIME ZONE,
    detection_latency_seconds INTEGER,
    
    -- Reference to merged_features for ground truth
    merged_feature_id INTEGER REFERENCES merged_features(merged_id),
    
    UNIQUE(user_id, injected_behavior)
);

COMMENT ON TABLE red_team_flags IS 'Red team attack simulation records for validating detection accuracy with ground truth labels';

CREATE INDEX idx_redteam_user ON red_team_flags(user_id);
CREATE INDEX idx_redteam_behavior ON red_team_flags(injected_behavior);
CREATE INDEX idx_redteam_detected ON red_team_flags(was_detected) WHERE was_detected = FALSE;

-- ═══════════════════════════════════════════════════════════════════════════
-- 8. VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Composite anomaly score view (requirement #12)
CREATE OR REPLACE VIEW vw_composite_anomaly_scores AS
SELECT 
    score_id,
    user_id,
    run_id,
    calculation_time,
    isolation_forest_score,
    oneclass_svm_score,
    autoencoder_score,
    -- Composite score: weighted average of 3 models
    -- IsolationForest: 40%, OneClassSVM: 35%, Autoencoder: 25%
    -- OneClassSVM output normalized to 0-1 range
    ROUND(
        (isolation_forest_score * 0.40) + 
        ((oneclass_svm_score + 1) / 2 * 0.35) + 
        (LEAST(autoencoder_score, 1.0) * 0.25), 
        4
    ) AS composite_score,
    is_anomaly,
    risk_level,
    CASE 
        WHEN risk_level = 'critical' THEN 4
        WHEN risk_level = 'high' THEN 3
        WHEN risk_level = 'medium' THEN 2
        ELSE 1
    END AS risk_priority
FROM anomaly_scores;

COMMENT ON VIEW vw_composite_anomaly_scores IS 'View calculating composite anomaly scores from 3 ML models with risk prioritization';

-- User risk summary view
CREATE OR REPLACE VIEW vw_user_risk_summary AS
SELECT 
    u.user_id,
    u.username,
    u.full_name,
    u.department,
    mf.calculation_date,
    mf.is_red_team,
    
    -- Latest anomaly scores
    ac.isolation_forest_score,
    ac.oneclass_svm_score,
    ac.autoencoder_score,
    ac.composite_score,
    ac.risk_level,
    ac.is_anomaly,
    
    -- Behavioral indicators
    mf.out_of_session_access,
    mf.files_per_day,
    mf.usb_per_day,
    mf.suspicious_email_ratio,
    
    -- Graph features
    mf.degree_centrality,
    mf.betweenness_centrality
FROM users u
LEFT JOIN LATERAL (
    SELECT * FROM merged_features 
    WHERE user_id = u.user_id 
    ORDER BY calculation_date DESC 
    LIMIT 1
) mf ON true
LEFT JOIN LATERAL (
    SELECT * FROM anomaly_scores 
    WHERE user_id = u.user_id 
    ORDER BY calculation_time DESC 
    LIMIT 1
) ac ON true;

COMMENT ON VIEW vw_user_risk_summary IS 'Comprehensive user risk profile combining features and anomaly scores';

-- ═══════════════════════════════════════════════════════════════════════════
-- 9. TRIGGERS
-- ═══════════════════════════════════════════════════════════════════════════

-- Trigger to auto-calculate composite score on insert/update
CREATE OR REPLACE FUNCTION calculate_composite_score()
RETURNS TRIGGER AS $$
BEGIN
    NEW.composite_score := ROUND(
        (NEW.isolation_forest_score * 0.40) + 
        ((NEW.oneclass_svm_score + 1) / 2 * 0.35) + 
        (LEAST(NEW.autoencoder_score, 1.0) * 0.25), 
        4
    );
    
    -- Auto-determine risk level
    IF NEW.composite_score >= 0.8 THEN
        NEW.risk_level := 'critical';
        NEW.is_anomaly := TRUE;
    ELSIF NEW.composite_score >= 0.6 THEN
        NEW.risk_level := 'high';
        NEW.is_anomaly := TRUE;
    ELSIF NEW.composite_score >= 0.35 THEN
        NEW.risk_level := 'medium';
        NEW.is_anomaly := FALSE;
    ELSE
        NEW.risk_level := 'low';
        NEW.is_anomaly := FALSE;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calc_composite
    BEFORE INSERT OR UPDATE ON anomaly_scores
    FOR EACH ROW
    EXECUTE FUNCTION calculate_composite_score();

-- ═══════════════════════════════════════════════════════════════════════════
-- RELATIONSHIP STRUCTURE EXPLANATION
-- ═══════════════════════════════════════════════════════════════════════════

/*
MERGED_FEATURES RELATIONSHIP STRUCTURE:

1. BEHAVIORAL_FEATURES → MERGED_FEATURES (1:1 relationship)
   - Each daily feature calculation for a user produces exactly one behavioral_features record
   - This is directly linked to merged_features via behavioral_feature_id FK
   - Pipeline: Raw logs → Behavioral metrics → merged_features.behavioral_feature_id

2. GRAPH_FEATURES → MERGED_FEATURES (1:1 relationship)
   - Graph centrality calculations happen once per user per day
   - Direct FK link: merged_features.graph_feature_id → graph_features.graph_feature_id
   - Pipeline: NetworkX graph → Centrality metrics → merged_features

3. NLP_EMAIL_FEATURES → MERGED_FEATURES (N:1 aggregation relationship)
   - Multiple emails per user generate multiple nlp_email_features records
   - These are AGGREGATED (avg, sum, count) during merge process
   - No direct FK, but user_id + date range links them
   - Pipeline: Email logs → NLP analysis → Aggregation by user → merged_features columns

The merged_features table serves as a MATERIALIZED VIEW pattern for ML input,
ensuring all features are aligned by user and calculation_date for model training.
*/

-- ═══════════════════════════════════════════════════════════════════════════
-- USAGE NOTES
-- ═══════════════════════════════════════════════════════════════════════════

/*
PRIMARY KEY JUSTIFICATION:
- SERIAL (auto-increment integers) used instead of UUID for:
  1. Better performance on indexing and joins
  2. Natural ordering (chronological without timestamp)
  3. Smaller storage (4 bytes vs 16 bytes)
  4. Human-readable IDs for debugging

CHECK CONSTRAINTS:
- Anomaly scores constrained to logical ranges (0-1 for normalized scores)
- Centrality metrics bounded to [0,1] as per graph theory
- Sentiment scores bounded to [-1,1] standard range

INDEX STRATEGY:
- Composite indexes on (user_id, timestamp) for time-series queries
- Partial indexes on boolean flags (is_anomaly, keyword_flag) for filtered queries
- Single-column indexes on frequent join columns

DATA RETENTION:
- Consider partitioning anomaly_scores and raw_logs by date for large datasets
- Archive old merged_features after model retraining
*/

-- Reset search path
SET search_path TO public;
