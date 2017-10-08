# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from unittest import TestCase, skip
import random
import sys
sys.path.append('../..')
sys.path.append('/home/amor/Alliance_industrie_futur')
from industrie_futur.team_handling.team_handler import Team
from redis import StrictRedis
from config import Config as config
import pickle
import json


class TestTeamRedis(TestCase):

    __name__ = "smartbook_test"

    def setUp(self):
        self.r = StrictRedis()

    def test_find_empty_teams(self):
        teams = pickle.loads(self.r.get('teams'))
        self.r.set('old_teams', self.r.get('teams'))
        teams_to_delete = []

        for t1 in teams:
            if t1.name is None:
                for t2 in teams:
                    if t1.creator == t2.creator:
                        print("Found empty duplicate team")
                        teams_to_delete.append(t1)

        for t in teams_to_delete:
            teams.delete(t)
        self.r.set('teams', pickle.dumps(teams))

        print("Found {}".format([t.__dict__ for t in teams_to_delete]))





