
class CreateQueries:
    users = """
CREATE TABLE IF NOT EXISTS users (
    username_id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    passwd_hash BYTEA
)
    """

    status = """
CREATE TABLE IF NOT EXISTS status (
    username_id SERIAL,
    status BOOLEAN DEFAULT False
)
    """

    tokens = """
CREATE TABLE IF NOT EXISTS tokens (
    token_id SERIAL PRIMARY KEY,
    token TEXT,
    identity TEXT
)
    """

    access = """
CREATE TABLE IF NOT EXISTS access (
    access_id SERIAL PRIMARY KEY,
    request_path TEXT,
    access_name TEXT DEFAULT Null
)
    """

    access_tokens = """
CREATE TABLE IF NOT EXISTS access_tokens (
    access_id SERIAL,
    token_id SERIAL
)
    """

    cameras = """
CREATE TABLE IF NOT EXISTS cameras (
    camera_id SERIAL PRIMARY KEY,
    video_file TEXT,
    camera_name TEXT,
    comment TEXT
)
    """

    motion = """
CREATE TABLE IF NOT EXISTS motion_t (
    motion_id SERIAL PRIMARY KEY,
    motion_data BYTEA,
    camera_id SERIAL,
    motion_time INTEGER
)
    """


def get_create_queries():
    return [i for i in dir(CreateQueries) if not i.startswith('__')]
