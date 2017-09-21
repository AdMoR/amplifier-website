# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from unittest import TestCase, skip
import random
import sys
sys.path.append('../..')
from industrie_futur.controller import invite_user_to_slack
from config import Config as config
import json


class TestSlack(TestCase):

    __name__ = "smartbook_test"

    def setUp(self):
        pass

    def test_slack_invite(self):
        invite_res = json.loads(invite_user_to_slack("test", "tester_{}".format(random.random()),
                                          "test_email@yopmail.com", config.get('slack-invite-token')))
        print(invite_res)
        assert(invite_res['ok'] is True)
