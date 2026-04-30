-- DocExtract Pro — Supabase Schema
-- Run this in Supabase SQL Editor

-- Credits table
CREATE TABLE IF NOT EXISTS credits (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    balance     INTEGER NOT NULL DEFAULT 0,
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Usage log
CREATE TABLE IF NOT EXISTS usage_log (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    filename    TEXT,
    doc_type    TEXT,
    doc_number  TEXT,
    success     BOOLEAN DEFAULT TRUE,
    latency_s   FLOAT,
    cost_eur    FLOAT DEFAULT 0.49,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- API Keys
CREATE TABLE IF NOT EXISTS api_keys (
    id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id      UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    key_hash     TEXT NOT NULL UNIQUE,
    key_prefix   TEXT NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ
);

-- Stripe payments (for audit)
CREATE TABLE IF NOT EXISTS payments (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID REFERENCES auth.users(id),
    stripe_session  TEXT UNIQUE,
    credits_bought  INTEGER NOT NULL,
    amount_eur      FLOAT NOT NULL,
    status          TEXT DEFAULT 'pending',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE credits    ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_log  ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys   ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments   ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users own credits"    ON credits    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users own usage_log"  ON usage_log  FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users own api_keys"   ON api_keys   FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users own payments"   ON payments   FOR ALL USING (auth.uid() = user_id);
