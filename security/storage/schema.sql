PRAGMA foreign_keys = ON;

-- USERS
CREATE TABLE IF NOT EXISTS users (
    user TEXT PRIMARY KEY,
    display_name TEXT,
    password_hash TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);

-- GROUPS
CREATE TABLE IF NOT EXISTS groups (
    group_name TEXT PRIMARY KEY,
    display_name TEXT,
    active INTEGER NOT NULL DEFAULT 1
);

-- GROUP MEMBERS
CREATE TABLE IF NOT EXISTS group_users (
    group_name TEXT,
    user TEXT,
    PRIMARY KEY (group_name, user),
    FOREIGN KEY (group_name) REFERENCES groups(group_name) ON DELETE CASCADE,
    FOREIGN KEY (user) REFERENCES users(user) ON DELETE CASCADE
);

-- ENDPOINTS
CREATE TABLE IF NOT EXISTS endpoints (
    name TEXT PRIMARY KEY,
    dialect TEXT,
    database_name TEXT,
    type TEXT,
    source TEXT,
    namespace TEXT,
    primary_key TEXT
);

-- PERMISSIONS
CREATE TABLE IF NOT EXISTS permissions (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    by_type TEXT CHECK(by_type IN ('user','group')),
    target TEXT,
    active INTEGER NOT NULL DEFAULT 1
);

-- PERMISSION ENDPOINT ACTIONS
CREATE TABLE IF NOT EXISTS permission_actions (
    permission_uid INTEGER,
    endpoint_name TEXT,
    action TEXT,
    PRIMARY KEY (permission_uid, endpoint_name, action),
    FOREIGN KEY (permission_uid) REFERENCES permissions(uid) ON DELETE CASCADE,
    FOREIGN KEY (endpoint_name) REFERENCES endpoints(name) ON DELETE CASCADE
);


-- DIALECTS
CREATE TABLE IF NOT EXISTS dialects (
    id UUID PRIMARY KEY,
    key VARCHAR(30) UNIQUE NOT NULL,        -- mysql | postgres | mssql | sqlite
    name VARCHAR(50) NOT NULL,               -- MySQL, PostgreSQL, SQL Server, SQLite

    supported_versions VARCHAR(100) NOT NULL,
    -- Ej: ">=5.7", ">=12", ">=2017", ">=3.35"

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- CONNECTIONS
CREATE TABLE IF NOT EXISTS data_sources (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,

    dialect_id UUID NOT NULL,

    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    username VARCHAR(100) NOT NULL,
    password TEXT NOT NULL,
    database_name VARCHAR(100) NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_dialect
        FOREIGN KEY (dialect_id)
        REFERENCES dialects(id)
        ON DELETE RESTRICT
);

INSERT INTO dialects (
    id,
    key,
    name,
    supported_versions,
    is_active
)
SELECT
    'b6d2c1a1-1111-4f2a-aaaa-111111111111',
    'mysql',
    'MySQL',
    '>=5.7',
    1
WHERE NOT EXISTS (SELECT 1 FROM dialects)

UNION ALL
SELECT
    'b6d2c1a1-2222-4f2a-bbbb-222222222222',
    'postgres',
    'PostgreSQL',
    '>=12',
    1
WHERE NOT EXISTS (SELECT 1 FROM dialects)

UNION ALL
SELECT
    'b6d2c1a1-3333-4f2a-cccc-333333333333',
    'mssql',
    'SQL Server',
    '>=2017',
    1
WHERE NOT EXISTS (SELECT 1 FROM dialects)

UNION ALL
SELECT
    'b6d2c1a1-4444-4f2a-dddd-444444444444',
    'sqlite',
    'SQLite',
    '>=3.35',
    1
WHERE NOT EXISTS (SELECT 1 FROM dialects);


