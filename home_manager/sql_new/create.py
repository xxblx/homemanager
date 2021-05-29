
import inspect


class CreateQueries:
    @staticmethod
    def sorted_key(x):
        return x

    @classmethod
    def get_create_queries(cls):
        cls_data = inspect.getmembers(cls, lambda x: not inspect.isroutine(x))
        for attr_name, value in sorted(cls_data, key=cls.sorted_key):
            if not attr_name.startswith('__') and not attr_name.startswith('_'):
                yield value


class CreateSchemaQueries(CreateQueries):
    schema = 'CREATE SCHEMA homemanager'


class CreateTableQueries(CreateQueries):
    @staticmethod
    def sorted_key(x):
        # yield users, tokens, roles and cameras at first
        _priority_dict = {'users': 1, 'tokens': 2, 'roles': 3, 'cameras': 4}
        if x[0] in _priority_dict:
            return _priority_dict[x[0]]
        return 5

    users = """
CREATE TABLE homemanager.users(
    user_id GENERATED ALWAYS AS IDENTITY,
    username TEXT,
    passwd_hash BYTEA,
    UNIQUE(username),
    PRIMARY KEY(user_id)
)
"""

    user_statuses = """
CREATE TABLE homemanager.user_statuses(
    user_id INT,
    status BOOLEAN DEFAULT False,
    CONSTRAINT fk_user_status_user_id
        FOREIGN KEY(user_id)
            REFERENCES homemanager.users(user_id)
            ON DELETE CASCADE
)
"""

    tokens = """
CREATE TABLE homemanager.tokens(
    token_id GENERATED ALWAYS AS IDENTITY,
    token_select INT,
    token_verify BYTEA,
    token_renew TEXT,
    expires_in TIMESTAMP DEFAULT,
    UNIQUE(token_select),
    PRIMARY KEY(token_id)
)
"""

# 0 - GET, 1 - POST, 2 - PUT, 3 - DELETE
    roles = """
CREATE TABLE homemanager.roles(
    role_id GENERATED ALWAYS AS IDENTITY,
    role_name TEXT,
    path TEXT,
    method_code INT
)
"""

    roles_tokens = """
CREATE TABLE homemanager.roles_tokens(
    role_id INT,
    token_id INT,
    CONSTRAINT fk_roles_tokens_role_id
        FOREIGN KEY(role_id)
            REFERENCES homemanager.roles(role_id)
            ON DELETE CASCADE,
    CONSTRAINT fk_roles_tokens_token_id
        FOREIGN KEY(token_id)
            REFERENCES homemanager.tokens(token_id)
            ON DELETE CASCADE
)
"""

    cameras = """
CREATE TABLE IF NOT EXISTS homemanager.cameras (
    camera_id GENERATED ALWAYS AS IDENTITY,
    camera_name TEXT,
    video_path TEXT
)
"""

    motions = """
CREATE TABLE IF NOT EXISTS homemanager.motions (
    motion_id GENERATED ALWAYS AS IDENTITY,
    motion_data BYTEA,
    camera_id INT,
    motion_time TIMESTAMP,
    CONSTRAINT fk_motions_camera_id
        FOREIGN KEY(camera_id)
            REFERENCES homemanager.cameras(camera_id)
            ON DELETE SET NULL
)
"""
