-- Leads Table
CREATE TABLE leads (
    id BIGSERIAL PRIMARY KEY,
    company_name TEXT,
    website TEXT,
    industry TEXT,
    employee_count TEXT,
    icp_score FLOAT,
    status TEXT DEFAULT 'new', -- new, enriched, qualified, engaged, converted, disqualified
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contacts / Decision Makers
CREATE TABLE contacts (
    id BIGSERIAL PRIMARY KEY,
    lead_id BIGINT REFERENCES leads(id),
    name TEXT,
    title TEXT,
    email TEXT,
    phone TEXT,
    linkedin_url TEXT,
    is_decision_maker BOOLEAN
);

-- Interaction History (Calls/Emails)
CREATE TABLE interactions (
    id BIGSERIAL PRIMARY KEY,
    lead_id BIGINT REFERENCES leads(id),
    type TEXT, -- 'email', 'voice', 'linkedin'
    direction TEXT, -- 'inbound', 'outbound'
    content TEXT, -- transcript or email body
    sentiment_score FLOAT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);