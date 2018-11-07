CREATE DATABASE kisee;
CREATE TABLE IF NOT EXISTS users(
    user_id TEXT PRIMARY KEY,
    username TEXT,
    email TEXT,
    password TEXT,
    is_superuser BOOLEAN DEFAULT FALSE
);
