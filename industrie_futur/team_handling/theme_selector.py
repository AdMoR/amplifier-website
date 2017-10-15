import pickle
from ..user_data import User
import copy
import itertools
import random
import math
import numpy as np
import os
from config import Config as config

class ThemeSelector(object):

    def __init__(self, preference_dicts, teams):
        '''
        Algs
        '''
        if os.path.exists(os.path.join(config.get("base_dir"), "repartition")):
            self.already_assigned = self.load_previous_repartition(os.path.join(config.get("base_dir"), "repartition"))
            self.preferences = {u: preference_dicts[u]
                                for u in preference_dicts.keys()
                                if u not in self.already_assigned}

        else:
            self.preferences = preference_dicts
            self.already_assigned = []

        self.inverted_pref = {u: {preference_dicts[u][i]: i
                                  for i in preference_dicts[u]}
                              for u in preference_dicts}

        self.user_to_team = {}
        for team in teams:
            for user in team:
                self.user_to_team[user] = team




    def assign_theme_to_users(self, themes=['t1', 't2', 't3'], filler='t0'):
        """
        """

        # 1 : Calculate the split that we want to reach and
        # how many user should move from prefered theme
        n_users = len(self.preferences)

        # 2 : Get repartition and create correctness margin based on filler
        repartitions = {t: [] for t in (themes + [filler])}


        for user in self.preferences.keys():
            print(user.decode('utf-8'), self.user_to_team.keys())
            if user.decode('utf-8') not in self.user_to_team.keys():
                first_pref = self.preferences[user].get(1)
                repartitions[first_pref].append(user)


        # the margin is based on the number of fillers
        filler_margin = len(repartitions[filler]) / (len(themes) - 1)

        # 3 : Assign users from the largest theme to the smallest
        best_repartition = None
        best_score = 10000
        for attempt in range(1000):

            attempt_repartition = copy.deepcopy(repartitions)
            if attempt % 99 == 0:
                print("\n\n")

            res_repartition, res_score = self.random_filling(attempt_repartition,
                                                             themes, filler, filler_margin)
            if attempt % 99 == 0:
                print('Debug : Current score {}'.format(res_score))
            if res_score < best_score:
                print('New best score', res_score, best_score, 'optimal score', n_users)
                best_repartition = copy.deepcopy(res_repartition)
                best_score = copy.deepcopy(res_score)

        return best_repartition, best_score

    def random_filling(self, attempt_repartition, themes, filler, filler_margin=0):
        """
        Be stupid
        """

        # random assignement iteration
        def one_step(repartition, themes, act=True):
            themes_ordered_by_nb_users = sorted(themes, key=lambda t: len(repartition[t]))
            smallest_t, biggest_t = themes_ordered_by_nb_users[0], themes_ordered_by_nb_users[-1]
            if act:
                #randin_index = random.randint(1, 10000) % len(repartitions[biggest_t])
                Z = sum([math.exp(-self.inverted_pref[u][biggest_t])
                         for u in repartition[biggest_t]])
                rand_user = np.random.choice(repartition[biggest_t],
                                             p=[(1. / Z) * math.exp(-self.inverted_pref[u][biggest_t])
                                             for u in repartition[biggest_t]])
                randin = repartition[biggest_t].index(rand_user)
                random_user = repartition[biggest_t].pop(randin)
                #repartitions[smallest_t].append(random_user)
                repartition = self.add_user_to_theme(repartition, smallest_t, random_user)
            max_difference = len(repartition[biggest_t]) - len(repartition[smallest_t])
            return max_difference

        max_difference = one_step(attempt_repartition, themes, act=False)
        # Do the random assignement while the gap is too big
        while max_difference > filler_margin:
            max_difference = one_step(attempt_repartition, themes)


        # Assign randomly the filler
        if filler in attempt_repartition.keys():
            for i, user in enumerate(attempt_repartition[filler]):
                themes_ordered_by_nb_users = sorted(themes, key=lambda t: len(attempt_repartition[t]))
                theme_key = themes_ordered_by_nb_users[0]
                attempt_repartition = self.add_user_to_theme(attempt_repartition, theme_key, user)

            # delete the filler
            del attempt_repartition[filler]

        score = self.evaluate_solution(attempt_repartition, self.preferences)

        return attempt_repartition, score


###########
# HELPERS #
###########

    def team_correctness(self, repartition):
        has_changed = False
        for t in repartition.keys():
            for user in repartition[t]:
                if user in self.user_to_team.keys():
                    for teammate in self.user_to_team[user]:
                        other_theme = self.find_user_theme(repartition, teammate)
                        if other_theme != t:
                            not_user = repartition[other_theme].pop(repartition[other_theme].index(teammate))
                            repartition[t].append(teammate)
                            has_changed = True
        return has_changed

    def find_user_theme(self, repartition, user):
        for theme in repartition.keys():
            if user in repartition[theme]:
                return theme
        raise Exception("User not found")

    def add_user_to_theme(self, repartition, theme, user):
        repartition[theme].append(user)
        return repartition

    def evaluate_solution(self, solution, preferences):

        score = 0
        for t in solution.keys():
            for u in solution[t]:
                score_calculation = self.inverted_pref[u][t]
                score += score_calculation

        return score

    def load_previous_repartition(self, load_path):
        """
        Load from path like : path -- T1-*
                                    |-T2-*.txt
                                    |-T3-
        :param load_path:
        :return:
        """

        all_users = []
        all_themes = [t for t in os.listdir(load_path)
                      if t not in [".DS_Store", "all_users.txt"]]
        for t in all_themes:

            theme_dir = os.path.join(load_path, t)
            user_files = os.listdir(theme_dir)

            for user_file in user_files:
                f = open(os.path.join(theme_dir, user_file))
                for line in f:
                    if '@' in line:
                        user = line.rstrip()
                        if len(user) > 200:
                            continue
                        all_users.append(user)

        print("Loaded repartition", len(all_users))
        return all_users





