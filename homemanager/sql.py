CREATE = {
    'users': """
CREATE TABLE IF NOT EXISTS users_t (
    username_id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    passwd_hash BYTEA
)
    """,

    'status': """
CREATE TABLE IF NOT EXISTS status_t (
    username_id SERIAL,
    status BOOLEAN DEFAULT False
)
    """,

    'tokens': """
CREATE TABLE IF NOT EXISTS tokens_t (
    token_id SERIAL PRIMARY KEY,
    token TEXT,
    identity TEXT
)
    """,

    'access': """
CREATE TABLE IF NOT EXISTS access_t (
    access_id SERIAL PRIMARY KEY,
    request_path TEXT,
    access_name TEXT DEFAULT Null
)
    """,

    'access_tokens': """
CREATE TABLE IF NOT EXISTS access_tokens_t (
    access_id SERIAL,
    token_id SERIAL
)
    """,

    'video': """
CREATE TABLE IF NOT EXISTS video_t (
    video_id SERIAL PRIMARY KEY,
    video_path TEXT,
    source_name TEXT,
    comment TEXT
)
    """,

    'motion': """
CREATE TABLE IF NOT EXISTS motion_t (
    motion_id SERIAL PRIMARY KEY,
    motion_data BYTEA,
    source_identity TEXT,
    motion_time INTEGER
)
    """
}

INSERT = {
    'users': """
INSERT INTO users_t (username, passwd_hash) VALUES(%s, %s)
    """,

    'status': """
INSERT INTO status_t (username_id)
SELECT username_id FROM users_t WHERE username = %s
    """,

    'tokens': """
INSERT INTO tokens_t (token, identity) VALUES(%s, %s)
    """,

    'access': """
INSERT INTO access_t (request_path, access_name) VALUES(%s, %s)
    """,

    'access_tokens': """
INSERT INTO access_tokens_t (access_id, token_id)
SELECT %s, token_id FROM tokens_t WHERE identity = %s
    """,

    'video': """
INSERT INTO video_t (video_path, source_name, comment) VALUES(%s, %s, %s)
    """,

    'motion': """
INSERT INTO motion_t (motion_data, source_identity, motion_time)
VALUES (%s, %s, %s)
    """
}

SELECT = {
    'users': 'SELECT passwd_hash FROM users_t WHERE username = %s',

    'status': 'SELECT username_id FROM status_t WHERE status = True',

    'tokens': 'SELECT identity, token_id FROM tokens_t WHERE token = %s',

    'access': 'SELECT access_id, request_path, access_name FROM access_t',

    'access_tokens': """
SELECT
    t.identity
FROM
    access_tokens_t at

    INNER JOIN tokens_t t
    on at.token_id = t.token_id
WHERE
    t.token = %s and at.access_id = %s
    """,

    'video': 'SELECT video_id, video_path, source_name, comment FROM video_t'
}

UPDATE = {
    'status': 'UPDATE status_t SET status = %s WHERE username_id = %s'
}
