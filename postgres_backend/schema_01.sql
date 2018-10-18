CREATE DATABASE kisee;
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    email TEXT,
    password TEXT,
    is_superuser BOOLEAN DEFAULT FALSE
);
