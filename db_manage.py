#!/usr/bin/env python3

import getpass
import argparse
from uuid import uuid4

import nacl.pwhash
import psycopg2

from home_manager.conf import DSN
from home_manager.sql_new.create import CreateTableQueries, CreateSchemaQueries
from home_manager.sql_new.insert import InsertQueries


def db_init():
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        for query in CreateSchemaQueries.get_create_queries():
            cur.execute(query)
        for query in CreateTableQueries.get_create_queries():
            cur.execute(query)

        cur.execute(InsertQueries.role, ('camera',))
        role_id = cur.fetchall()[0][0]
        cur.execute(
            InsertQueries.role_path,
            (role_id, '/api/camera/motion', False, True, False, False)
        )
        cur.execute(
            InsertQueries.role_path,
            (role_id, '/api/camera/setup', True, False, False, False)
        )

        cur.execute(InsertQueries.role, ('router',))
        role_id = cur.fetchall()[0][0]
        cur.execute(
            InsertQueries.role_path,
            (role_id, '/api/router/status/user', False, True, False, False)
        )


def add_user(username):
    password = getpass.getpass()
    password_hash = nacl.pwhash.str(password.encode())
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        cur.execute(InsertQueries.user, (username, password_hash))
        user_id = cur.fetchall()[0][0]
        cur.execute(InsertQueries.user_status, (user_id,))


def add_token(permanent):
    token = uuid4().hex
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        cur.execute(InsertQueries.token_session, (token,))
    # TODO: use api to get tokens pair


def add_role(role_name, path, get, post, put, delete):
    # TODO: get handlers list from app.py
    handlers = ('/api/user/status', '/api/camera/motion', '/api/camera/setup')
    if path not in handlers:
        raise
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        cur.execute(
            InsertQueries.role,
            (role_name, path, get, post, put, delete)
        )


def add_camera(camera_name, path_video, path_activation):
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        cur.execute(InsertQueries.device, (camera_name, 'camera'))
        device_id = cur.fetchall()[0][0]
        cur.execute(
            InsertQueries.camera, (device_id, path_video, path_activation)
        )
        cur.execute(InsertQueries.role_device, ('camera', device_id))


def assign_role(role_name, token_select):
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        cur.execute(InsertQueries.role_token, (role_name, token_select))


def main():
    commands = {
        'init-db': {
            'func': db_init,
            'kw': []
        },
        'user-add': {
            'func': add_user,
            'kw': ['username']
        },
        'token-add': {
            'func': add_token,
            'kw': ['permanent']
        },
        'role-add': {
            'func': add_role,
            'kw': ['role_name', 'path', 'get', 'post', 'put', 'delete']
        },
        'camera-add': {
            'func': add_camera,
            'kw': ['camera_name', 'path_video', 'path_activation']
        },
        'role-assign': {
            'func': assign_role,
            'kw': ['token_select', 'role_name']
        },
    }

    parser = argparse.ArgumentParser(prog='HomeManager')

    subparsers = parser.add_subparsers()

    init_db = subparsers.add_parser('init-db')
    init_db.set_defaults(used='init-db')

    user_add = subparsers.add_parser('user-add')
    user_add.set_defaults(used='user-add')
    user_add.add_argument('-u', '--username', type=str, required=True)

    token_add = subparsers.add_parser('token-add')
    token_add.set_defaults(used='token-add')
    # TODO: default=False
    token_add.add_argument('-p', '--permanent', action='store_true',
                           default=True)

    role_add = subparsers.add_parser('role-add')
    role_add.set_defaults(used='role-add')
    role_add.add_argument('-n', '--role-name', type=str, required=True)
    role_add.add_argument('-p', '--path', type=str, required=True)
    role_add.add_argument('--get', action='store_true', default=False)
    role_add.add_argument('--post', action='store_true', default=False)
    role_add.add_argument('--put', action='store_true', default=False)
    role_add.add_argument('--delete', action='store_true', default=False)

    role_assign = subparsers.add_parser('role-assign')
    role_assign.set_defaults(used='role-assign')
    role_assign.add_argument('-n', '--role-name', type=int)
    role_assign.add_argument('-t', '--token-select', type=int)

    camera_add = subparsers.add_parser('camera-add')
    camera_add.set_defaults(used='camera-add')
    camera_add.add_argument('-n', '--camera-name', type=str, required=True)
    camera_add.add_argument('-p', '--path-video', type=str, required=True,
                            help='video file path')
    camera_add.add_argument('-a', '--path-activation', type=str, required=True,
                            help='activation file path for systemd service')

    args = parser.parse_args()
    if 'used' not in args:
        return
    else:
        _args = vars(args)
        func = commands[args.used]['func']
        kw = {k: _args[k] for k in commands[args.used]['kw']}
        result = func(**kw)
        if result is not None:
            print(result)


if __name__ == '__main__':
    main()
