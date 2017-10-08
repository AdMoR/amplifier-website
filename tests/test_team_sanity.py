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

        cleaned_team = []
        for t1 in teams:
            indicator = True
            if t1.name is None:
                for t2 in teams:
                    if t1.creator == t2.creator and t1.description is None:
                        print("Found empty duplicate team")
                        indicator = False
                        break
            if indicator:
                cleaned_team.append(t1)

        self.r.set('teams', pickle.dumps(cleaned_team))

        print("Found {}".format([t.__dict__ for t in teams_to_delete]))





