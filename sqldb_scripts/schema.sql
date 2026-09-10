PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT,
    position TEXT,
    annual_leave INTEGER NOT NULL DEFAULT 0,
    used_leave INTEGER NOT NULL DEFAULT 0,
    remaining_leave INTEGER NOT NULL DEFAULT 0,
    performance TEXT
);


CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE NOT NULL,

    password_hash TEXT NOT NULL,

    employee_id TEXT UNIQUE NOT NULL,

    role TEXT NOT NULL DEFAULT 'employee',

    is_active INTEGER NOT NULL DEFAULT 1,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
        ON DELETE RESTRICT,

    CHECK (
        role IN (
            'employee',
            'manager',
            'hr_admin'
        )
    )
);


CREATE TABLE IF NOT EXISTS manager_employee_access (
    manager_user_id INTEGER NOT NULL,

    employee_id TEXT NOT NULL,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (
        manager_user_id,
        employee_id
    ),

    FOREIGN KEY (manager_user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,

    user_id INTEGER NOT NULL,

    title TEXT NOT NULL DEFAULT 'New conversation',

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,

    conversation_id TEXT NOT NULL,

    role TEXT NOT NULL,

    content TEXT NOT NULL,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (conversation_id)
        REFERENCES conversations(conversation_id)
        ON DELETE CASCADE,

    CHECK (
        role IN (
            'user',
            'assistant'
        )
    )
);


CREATE INDEX IF NOT EXISTS idx_users_username
ON users(username);


CREATE INDEX IF NOT EXISTS idx_users_employee_id
ON users(employee_id);


CREATE INDEX IF NOT EXISTS idx_conversations_user_id
ON conversations(user_id);


CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
ON messages(conversation_id);



