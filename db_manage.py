#!/usr/bin/env python3

import json
import getpass
import argparse
from uuid import uuid4

from urllib.parse import urljoin, urlencode
from urllib.request import Request, urlopen
import nacl.pwhash
import psycopg2

from homemanager.conf import DB_SETTINGS, HOST, PORT
from homemanager.sql_new.create import CreateTableQueries, CreateSchemaQueries
from homemanager.sql_new.delete import DeleteQueries
from homemanager.sql_new.insert import InsertQueries


def db_init():
    with psycopg2.connect(**DB_SETTINGS) as conn:
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
    with psycopg2.connect(**DB_SETTINGS) as conn:
        cur = conn.cursor()
        cur.execute(InsertQueries.user, (username, password_hash))
        user_id = cur.fetchall()[0][0]
        cur.execute(InsertQueries.user_status, (user_id,))


def add_session_token(device_name, permanent):
    token = uuid4().hex
    with psycopg2.connect(**DB_SETTINGS) as conn:
        cur = conn.cursor()
        cur.execute(
            InsertQueries.token_session, (token, permanent, device_name)
        )
    return token


def add_token(device_name, permanent):
    token = add_session_token(device_name, permanent)
    base_url = 'http://{}:{}'.format(HOST, PORT)
    url = urljoin(base_url, '/api/tokens/new')
    req = Request(url, data=urlencode({'token_session': token}).encode())
    resp = urlopen(req)
    return json.loads(resp.read())


def add_camera(camera_name, path_video, path_activation):
    with psycopg2.connect(**DB_SETTINGS) as conn:
        cur = conn.cursor()
        cur.execute(InsertQueries.device, (camera_name, 'camera'))
        device_id = cur.fetchall()[0][0]
        cur.execute(
            InsertQueries.camera, (device_id, path_video, path_activation)
        )
        cur.execute(InsertQueries.role_device, ('camera', device_id))


def add_router(router_name):
    with psycopg2.connect(**DB_SETTINGS) as conn:
        cur = conn.cursor()
        cur.execute(InsertQueries.device, (router_name, 'router'))
        device_id = cur.fetchall()[0][0]
        cur.execute(InsertQueries.router, (device_id,))
        cur.execute(InsertQueries.role_device, ('router', device_id))


def delete_device(device_name):
    with psycopg2.connect(**DB_SETTINGS) as conn:
        cur = conn.cursor()
        cur.execute(DeleteQueries.device_name, (device_name,))


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
            'kw': ['device_name', 'permanent']
        },
        'camera-add': {
            'func': add_camera,
            'kw': ['camera_name', 'path_video', 'path_activation']
        },
        'router-add': {
            'func': add_router,
            'kw': ['router_name']
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
    token_add.add_argument('-n', '--device-name', type=str, required=True)
    # TODO: default=False
    token_add.add_argument('-p', '--permanent', action='store_true',
                           default=True)

    camera_add = subparsers.add_parser('camera-add')
    camera_add.set_defaults(used='camera-add')
    camera_add.add_argument('-n', '--camera-name', type=str, required=True)
    camera_add.add_argument('-p', '--path-video', type=str, required=True,
                            help='video file path')
    camera_add.add_argument('-a', '--path-activation', type=str, required=True,
                            help='activation file path for systemd service')

    router_add = subparsers.add_parser('router-add')
    router_add.set_defaults(used='router-add')
    router_add.add_argument('-n', '--router-name', type=str, required=True)

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
