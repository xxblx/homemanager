
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
        _priority_dict = {'users': 1, 'devices': 2, 'tokens': 3, 'roles': 4,
                          'cameras': 5}
        if x[0] in _priority_dict:
            return _priority_dict[x[0]]
        return 5

    users = """
CREATE TABLE homemanager.users(
    user_id INT GENERATED ALWAYS AS IDENTITY,
    username TEXT,
    password_hash BYTEA,
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
    devices = """
CREATE TABLE homemanager.devices(
    device_id INT GENERATED ALWAYS AS IDENTITY,
    device_name TEXT,
    device_type TEXT,
    UNIQUE(device_name),
    PRIMARY KEY(device_id)
)
"""
    tokens = """
CREATE TABLE homemanager.tokens(
    token_id INT GENERATED ALWAYS AS IDENTITY,
    device_id INT,
    token_select INT,
    token_verify BYTEA,
    token_renew TEXT,
    expires_in TIMESTAMP DEFAULT NULL,
    UNIQUE(token_select),
    PRIMARY KEY(token_id),
    CONSTRAINT fk_tokens_device_id
        FOREIGN KEY(device_id)
            REFERENCES homemanager.devices(device_id)
            ON DELETE CASCADE
)
"""
    tokens_session = """
CREATE TABLE homemanager.tokens_session(
    token_id INT GENERATED ALWAYS AS IDENTITY,
    token TEXT,
    expires_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '1 hour',
    UNIQUE(token),
    PRIMARY KEY(token_id)
)
"""
    roles = """
CREATE TABLE homemanager.roles(
    role_id INT GENERATED ALWAYS AS IDENTITY,
    role_name TEXT,
    UNIQUE(role_name),
    PRIMARY KEY(role_id)
)
"""
    roles_paths = """
CREATE TABLE homemanager.roles_paths(
    role_id INT,
    path TEXT,
    method_get BOOLEAN DEFAULT False,
    method_post BOOLEAN DEFAULT False,
    method_put BOOLEAN DEFAULT False,
    method_delete BOOLEAN DEFAULT False,
    CONSTRAINT fk_roles_paths_role_id
        FOREIGN KEY(role_id)
            REFERENCES homemanager.roles(role_id)
            ON DELETE CASCADE
)
"""
    roles_devices = """
CREATE TABLE homemanager.roles_devices(
    role_id INT,
    device_id INT,
    CONSTRAINT fk_roles_devices_role_id
        FOREIGN KEY(role_id)
            REFERENCES homemanager.roles(role_id)
            ON DELETE CASCADE,
    CONSTRAINT fk_roles_devices_device_id
        FOREIGN KEY(device_id)
            REFERENCES homemanager.devices(device_id)
            ON DELETE CASCADE
)
"""
    cameras = """
CREATE TABLE homemanager.cameras(
    device_id INT,
    path_video TEXT,
    path_activation TEXT DEFAULT NULL,
    UNIQUE(path_video),
    CONSTRAINT fk_cameras_device_id
        FOREIGN KEY(device_id)
            REFERENCES homemanager.devices(device_id)
            ON DELETE CASCADE
)
"""
    routers = """
CREATE TABLE homemanager.routers(
    device_id INT,
    CONSTRAINT fk_cameras_device_id
        FOREIGN KEY(device_id)
            REFERENCES homemanager.devices(device_id)
            ON DELETE CASCADE
)
"""
    motions = """
CREATE TABLE homemanager.motions(
    motion_id INT GENERATED ALWAYS AS IDENTITY,
    motion_data BYTEA DEFAULT NULL,
    device_id INT,
    motion_time TIMESTAMP,
    CONSTRAINT fk_motions_device_id
        FOREIGN KEY(device_id)
            REFERENCES homemanager.devices(device_id)
            ON DELETE SET NULL
)
"""
