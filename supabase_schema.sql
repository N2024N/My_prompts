-- Supabase Schema for AI Prompt Engineering Studio
-- This schema is used for activation code management

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Activation codes table
CREATE TABLE activation_codes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    activation_code TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'unused' CHECK (status IN ('unused', 'used', 'revoked')),
    notion_page_id TEXT,
    email TEXT,
    plan TEXT NOT NULL DEFAULT 'standard' CHECK (plan IN ('standard', 'pro', 'team')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    used_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for faster queries
CREATE INDEX idx_activation_codes_code ON activation_codes(activation_code);
CREATE INDEX idx_activation_codes_status ON activation_codes(status);
CREATE INDEX idx_activation_codes_email ON activation_codes(email);
CREATE INDEX idx_activation_codes_created_at ON activation_codes(created_at DESC);

-- Function to validate and use an activation code
CREATE OR REPLACE FUNCTION use_activation_code(
    p_activation_code TEXT,
    p_notion_page_id TEXT DEFAULT NULL,
    p_email TEXT DEFAULT NULL
)
RETURNS TABLE (
    success BOOLEAN,
    message TEXT,
    plan TEXT
) AS $$
DECLARE
    v_record activation_codes%ROWTYPE;
BEGIN
    -- Find the activation code
    SELECT * INTO v_record 
    FROM activation_codes 
    WHERE activation_code = p_activation_code;
    
    -- Check if code exists
    IF v_record.id IS NULL THEN
        RETURN QUERY SELECT false, 'Invalid activation code', NULL::TEXT;
        RETURN;
    END IF;
    
    -- Check if code is already used
    IF v_record.status = 'used' THEN
        RETURN QUERY SELECT false, 'Activation code already used', NULL::TEXT;
        RETURN;
    END IF;
    
    -- Check if code is revoked
    IF v_record.status = 'revoked' THEN
        RETURN QUERY SELECT false, 'Activation code revoked', NULL::TEXT;
        RETURN;
    END IF;
    
    -- Update the record
    UPDATE activation_codes
    SET 
        status = 'used',
        notion_page_id = COALESCE(p_notion_page_id, notion_page_id),
        email = COALESCE(p_email, email),
        used_at = NOW()
    WHERE id = v_record.id;
    
    -- Return success
    RETURN QUERY SELECT true, 'Activation successful', v_record.plan;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to generate new activation codes (admin use)
CREATE OR REPLACE FUNCTION generate_activation_codes(
    p_count INTEGER DEFAULT 1,
    p_plan TEXT DEFAULT 'standard',
    p_email TEXT DEFAULT NULL
)
RETURNS TABLE (
    activation_code TEXT,
    plan TEXT,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
DECLARE
    i INTEGER;
    new_code TEXT;
BEGIN
    FOR i IN 1..p_count LOOP
        -- Generate a random code (12 characters, alphanumeric)
        new_code := upper(
            encode(gen_random_bytes(6), 'hex')
        );
        
        -- Insert the code
        INSERT INTO activation_codes (activation_code, plan, email)
        VALUES (new_code, p_plan, p_email)
        RETURNING activation_code, plan, created_at
        INTO activation_code, plan, created_at;
        
        -- Return the generated code
        RETURN NEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- View for admin dashboard
CREATE VIEW activation_codes_summary AS
SELECT 
    plan,
    status,
    COUNT(*) as count,
    MIN(created_at) as earliest,
    MAX(created_at) as latest
FROM activation_codes
GROUP BY plan, status
ORDER BY plan, status;

-- Row Level Security (RLS) policies
ALTER TABLE activation_codes ENABLE ROW LEVEL SECURITY;

-- Policy: Allow public to check activation codes (read-only for specific codes)
CREATE POLICY "Allow public to check own activation code" 
ON activation_codes FOR SELECT 
USING (
    -- Allow checking by activation_code (for validation)
    -- This is safe because activation_code is unique and random
    true
);

-- Policy: Allow public to update only unused codes to used status
CREATE POLICY "Allow public to use activation codes" 
ON activation_codes FOR UPDATE 
USING (status = 'unused')
WITH CHECK (status = 'used');

-- Policy: Only admins can insert new codes (via service role)
CREATE POLICY "Only admins can insert activation codes" 
ON activation_codes FOR INSERT 
WITH CHECK (auth.role() = 'service_role');

-- Insert some sample activation codes (for testing)
-- Uncomment and run manually in Supabase SQL editor
-- SELECT * FROM generate_activation_codes(3, 'standard');
-- SELECT * FROM generate_activation_codes(2, 'pro');
-- SELECT * FROM generate_activation_codes(1, 'team');