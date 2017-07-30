# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .abstract import AbstractDatabase
from redis import StrictRedis
import pickle
import json


class UserAlreadyCreatedException(Exception):
    pass


class Redis(AbstractDatabase):

    def __init__(self, host=None, port=None, namespace=None, expiration=86400):
        self.host = host
        self.port = port
        self.namespace = namespace
        self.expiration = expiration

    def set(self, album_id, analysis_type, data):
        key_name = self._get_key_name(album_id, analysis_type)
        self.conn.setex(name=key_name, time=self.expiration, value=json.dumps(data))
        return self.conn.incr('smartbook:cache:set')

    def get(self, album_id, analysis_type):
        key_name = self._get_key_name(album_id, analysis_type)
        data = self.conn.get(key_name)

        if data:
            self.conn.incr('smartbook:cache:hit')
        else:
            self.conn.incr('smartbook:cache:miss')

        return json.loads(data) if data else None

    def connect(self, now=True):
        if now:
            self.conn = StrictRedis(self.host, self.port)

    def _get_key_name(self, album_id, analysis_type):
        return '%s:%s:%s' % (self.namespace, album_id, analysis_type)


class RedisUserHandler(StrictRedis):

    def get_user(self, email):
        user = {}
        all_keys = [str(k) for k in self.keys()]
        if email in all_keys:
            user['email'] = email
            user['password'] = self.hget(email, "password")
            user['form'] = self.get_session(email)
            return user
        else:
            return None

    def add_user(self, email, password, form=None):
        ret_user = self.get_user(email)
        if ret_user is not None and len(ret_user) > 0:
            raise UserAlreadyCreatedException("User was already created")
        self.hset(email, "password", password)
        if form:
            self.save_session(email, form)
        return True

    def get_session(self, username):
        pick = self.hget(username, "session")
        if pick is not None:
            return pickle.loads(pick)

    def save_session(self, username, session):
        if session is not None:
            self.hset(username, "session", pickle.dumps(session))
