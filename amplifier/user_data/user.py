#-*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
from flask_login import UserMixin
from .utils import UnknownUserError, CredentialsError, AccessError, get_logger
from .. import LOG


class User():
    __name__ = 'user'

    def __init__(self, cache, email, password, form=None):
        #self.logger = get_logger(self.__name__)
        self.db = cache
        self.email = email
        self.password = password
        self.is_authenticated = False
        if form is not None:
            self.form = dict(form)

    def check_user(self):
        try:
            return self.user_exists()
        except CredentialsError:
            LOG.debug("Bad credentials")
            return False
        except UnknownUserError:
            LOG.debug("Unknown user")
            return False

    def create_user(self):
        #print("User created with : {} {} {}".format(self.email, self.password, self.form))
        return self.db.add_user(self.email, self.password, self.form)

    def user_exists(self):
        try:
            user = self.db.get_user(self.email)
            LOG.debug('user check', user)
        except AccessError:
            print("Access error")
            raise UnknownUserError('No such user')
        if not user:
            print("Unknown user")
            raise UnknownUserError('No such user')
        if not self.validate_user(user):
            raise CredentialsError('Invalid credentials')
        return True

    def validate_user(self, user):
        if not user.get('email') == self.email:
            return False
        if not user.get('password') == self.password:
            return False
        self.is_authenticated = True
        return True

    def save_session(self):
        self.db.save_session(self.email, self.session)

    def is_authenticated(self):
        return self.is_authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.email)

    def __str__(self):
        return '<User: %s session: %s>' % (self.email, self.session)

    @classmethod
    def get(cls, cache, email):
        # Retrieve data from cache
        dict_user = cache.get_user(email)
        print(dict_user)
        if not dict_user:
            return None
        # regenerate user
        user = User(cache, dict_user.get('email'), dict_user.get('password'), dict_user.get('form'))
        if user.check_user() is True:
            user.form = cache.get_session(email)
            return user
        return None
