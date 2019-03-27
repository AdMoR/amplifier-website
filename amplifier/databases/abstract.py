# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)


class AbstractDatabase(object):

    def __init__(self, conn=None, host=None, port=None):
        self.host = host
        self.port = port
        self.conn = conn

    def set(self, table, key, data, field=''):
        raise NotImplementedError

    def get(self, table, key, field=''):
        raise NotImplementedError

    def connect(self):
        raise NotImplementedError
