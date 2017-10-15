# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from unittest import TestCase, skip
import random
import sys
sys.path.append('../..')
sys.path.append('/home/amor/Alliance_industrie_futur')
from industrie_futur.team_handling import Team, ThemeSelector
from redis import StrictRedis
from config import Config as config
import pickle
import json


class TestTeamRedis(TestCase):

    __name__ = "smartbook_test"

    def setUp(self):
        self.r = StrictRedis()

    @skip
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

        if len(cleaned_team) != len(teams):
            print("Found {}".format([t.__dict__ for t in cleaned_team]))
            raise Exception

    def test_assignement_update(self):

        user_list = self.create_dummy_users()
        user_pref = {}
        theme_list = ['t1', 't2', 't3']

        for u in user_list:
            random.shuffle(theme_list)
            user_pref[u] = {1: theme_list[0], 1.1: theme_list[1], 1.11: theme_list[2]}

        ts = ThemeSelector(preference_dicts=user_pref, teams=[])
        #ts.assign_theme_to_users()

        print([u for u in user_list if u not in ts.already_assigned])

        if not (sum([len(ts.repartitions[t]) for t in ts.repartitions.keys()]) == len(user_list)):
            print("Total assigned users", sum([len(ts.repartitions[t]) for t in ts.repartitions.keys()]))
            print("All users", len(user_list))
            assert(False)


    def create_dummy_users(self):

        def set_dummy(r, email):
            r.hset(email, 'password', "plop")
            r.hset(email, "session", None)

        user_list = []

        f = open("/Users/amorvan/Documents/code_dw/website-industrie-futur/repartition/all_users.txt")
        for line in f:
            if '@' in line:
                user = line.rstrip()
                if len(user) > 200:
                    continue
                set_dummy(self.r, user)
                user_list.append(user)

        return user_list







