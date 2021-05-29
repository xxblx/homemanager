#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpass
import argparse
from uuid import uuid4

import bcrypt
import psycopg2

from home_manager.conf import DSN
from home_manager.sql import CREATE, INSERT
from home_manager.sql_new.select import SelectQueries


def create_tables():
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        for key in CREATE:
            cur.execute(CREATE[key])


def insert_users(username, passwd_hash):
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        cur.execute(INSERT['users'], (username, passwd_hash))
        cur.execute(INSERT['status'], (username,))


def insert_tokens(identity):
    token = uuid4().hex
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        cur.execute(INSERT['tokens'], (token, identity))

    return token


def insert_access(path, access_name):
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        cur.execute(INSERT['access'], (path, access_name))


def list_access():
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        cur.execute(SelectQueries.access)
        res = cur.fetchall()

    return res


def insert_access_token(access_id, identities):
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        for idt in identities:
            cur.execute(INSERT['access_tokens'], (access_id, idt))


def insert_video(path, source_name, comment):
    with psycopg2.connect(DSN) as conn:
        cur = conn.cursor()
        cur.execute(INSERT['video'], (path, source_name, comment))


def main():
    parser = argparse.ArgumentParser(prog='HomeManager')

    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser('init', help='Create tables')
    init_parser.set_defaults(used='init')

    users_parser = subparsers.add_parser('users')
    users_parser.set_defaults(used='users')
    users_parser.add_argument('-u', '--username', type=str, required=True)

    tokens_parser = subparsers.add_parser('tokens')
    tokens_parser.set_defaults(used='tokens')
    tokens_parser.add_argument('-i', '--identity', type=str, required=True)

    access_parser = subparsers.add_parser('access')
    access_parser.set_defaults(used='access')
    access_parser.add_argument('-p', '--path', type=str, required=True,
                               help='path in the url, like "/api/person"')
    access_parser.add_argument('-n', '--name', type=str, default=None)

    list_access_parser = subparsers.add_parser('list-access')
    list_access_parser.set_defaults(used='list-access')

    set_access_parser = subparsers.add_parser('set-access')
    set_access_parser.set_defaults(used='set-access')
    set_access_parser.add_argument('-a', '--accessid', type=int,
                                   help='id of the access')
#    set_access_parser.add_argument('-u', '--username', type=str, nargs='+',
#                                   help='list usernames')
    set_access_parser.add_argument('-i', '--identities', type=str, nargs='+',
                                   help='list tokens identities')

    video_parser = subparsers.add_parser('video')
    video_parser.set_defaults(used='video')
    video_parser.add_argument('-p', '--path', type=str, required=True,
                              help='absolute path to m3u8')
    video_parser.add_argument('-n', '--source_name', type=str, required=True,
                              help='video\'s source name')
    video_parser.add_argument('-c', '--comment', type=str, default=None)

    camera_parser = subparsers.add_parser('camera')
    camera_parser.set_defaults(used='camera')
    camera_parser.add_argument('-i', '--identity', type=str, required=True,
                               help='camera\'s identity , like "camera-room"')
    camera_parser.add_argument('-p', '--path', type=str, required=True,
                               help='absolute path to m3u8')
    camera_parser.add_argument('-c', '--comment', type=str, default=None)

    args = parser.parse_args()
    if 'used' not in args:
        return

    if args.used == 'init':
        create_tables()

    elif args.used == 'users':
        passwd = getpass.getpass()
        passwd_hash = bcrypt.hashpw(passwd.encode(), bcrypt.gensalt())
        insert_users(args.username, passwd_hash)

    elif args.used == 'tokens':
        token = insert_tokens(args.identity)
        print(token)

    elif args.used == 'access':
        insert_access(args.path, args.name)

    elif args.used == 'list-access':
        res = list_access()
        for row in [('id', 'Path', 'Name')]+res:
            print('%s\t%s\t%s' % row)

    elif args.used == 'set-access':
        insert_access_token(args.accessid, args.identities)

    elif args.used == 'video':
        insert_video(args.path, args.source_name, args.comment)

    elif args.used == 'camera':
        insert_video(args.path, args.identity, args.comment)
        token = insert_tokens(args.identity)
        print(token)


if __name__ == '__main__':
    main()
