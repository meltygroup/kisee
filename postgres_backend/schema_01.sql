CREATE DATABASE kisee;
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    is_superuser BOOLEAN DEFAULT FALSE
);
