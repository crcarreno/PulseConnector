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
