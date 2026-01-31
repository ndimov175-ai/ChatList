-- Migration 002: Create prompt_enhancements table for storing enhanced prompts
-- This table stores the results of prompt enhancement operations

CREATE TABLE IF NOT EXISTS prompt_enhancements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_prompt TEXT NOT NULL,
    enhanced_prompt TEXT NOT NULL,
    alternatives TEXT,  -- JSON array with alternative prompts
    explanation TEXT,   -- Explanation of changes made
    recommendations TEXT,  -- JSON object with recommendations for different model types
    model_id INTEGER NOT NULL,
    enhancement_type TEXT NOT NULL,  -- general, code, analysis, creative
    prompt_id INTEGER,  -- FK to prompts table (optional)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id),
    FOREIGN KEY (model_id) REFERENCES models(id)
);

CREATE INDEX IF NOT EXISTS idx_prompt_enhancements_prompt_id ON prompt_enhancements(prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_enhancements_created_at ON prompt_enhancements(created_at);
CREATE INDEX IF NOT EXISTS idx_prompt_enhancements_model_id ON prompt_enhancements(model_id);
