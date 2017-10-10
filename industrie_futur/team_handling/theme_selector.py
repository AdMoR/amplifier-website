import pickle
from ..user_data import User
import copy
import itertools
import random
import math
import numpy as np


class ThemeSelector(object):

    def __init__(self, preference_dicts, teams):
        '''
        Algs
        '''
        self.preferences = preference_dicts
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
            first_pref = self.preferences[user].get(1)
            repartitions[first_pref].append(user)
        # the margin is based on the number of fillers
        filler_margin = len(repartitions[filler]) / (len(themes) - 1)

        # 3 : Assign users from the largest theme to the smallest
        best_repartition = None
        best_score = 10000
        for attempt in range(1000):
            print("\n\n")
            attempt_repartition = copy.deepcopy(repartitions)
            if attempt % 99 == 0:
                print('User preferences : ', self.preferences)
                print('attempt repartition before filling', attempt_repartition)
            res_repartition, res_score = self.random_filling(attempt_repartition,
                                                             themes, filler, filler_margin)
            if attempt % 99 == 0:
                print('Debug : Current score {}'.format(res_score))
            if res_score < best_score:
                print('New best score', res_score, best_score, 'optimal score', n_users)
                best_repartition = copy.deepcopy(res_repartition)
                best_score = copy.deepcopy(res_score)

        return best_repartition, best_score

    def random_filling(self, repartitions, themes, filler, filler_margin=0):
        """
        Be stupid
        """

        # random assignement iteration
        def one_step(repartitions, themes, act=True):
            themes_ordered_by_nb_users = sorted(themes, key=lambda t: len(repartitions[t]))
            smallest_t, biggest_t = themes_ordered_by_nb_users[0], themes_ordered_by_nb_users[-1]
            if act:
                #randin_index = random.randint(1, 10000) % len(repartitions[biggest_t])
                Z = sum([math.exp(-self.inverted_pref[u][biggest_t])
                         for u in repartitions[biggest_t]])
                rand_user = np.random.choice(repartitions[biggest_t],
                                             p=[(1. / Z) * math.exp(-self.inverted_pref[u][biggest_t])
                                             for u in repartitions[biggest_t]])
                randin = repartitions[biggest_t].index(rand_user)
                random_user = repartitions[biggest_t].pop(randin)
                #repartitions[smallest_t].append(random_user)
                repartitions = self.add_user_to_theme(repartitions, smallest_t, random_user)
            max_difference = len(repartitions[biggest_t]) - len(repartitions[smallest_t])
            return max_difference

        max_difference = one_step(repartitions, themes, act=False)
        # Do the random assignement while the gap is too big
        while max_difference > filler_margin:
            max_difference = one_step(repartitions, themes)

        # Assign randomly the filler
        if filler in repartitions.keys():
            for i, user in enumerate(repartitions[filler]):
                themes_ordered_by_nb_users = sorted(themes, key=lambda t: len(repartitions[t]))
                theme_key = themes_ordered_by_nb_users[0]
                repartitions = self.add_user_to_theme(repartitions, theme_key, user)

            # delete the filler
            del repartitions[filler]

        score = self.evaluate_solution(repartitions, self.preferences)

        return repartitions, score

    def brute_force_filling(self, repartitions, themes, filler, filler_margin=10):

        user_ordered = sum([repartitions[t] for t in repartitions.keys()], [])
        print(user_ordered)

        all_solutions = self.generate_solution_space(users=user_ordered,
                                                     themes=themes)
        best_solution = None
        best_score = 100000

        for solution in all_solutions:
            score = self.evaluate_solution(solution, self.preferences)
            if score < best_score:
                best_solution = solution
                best_score = score

        print(best_solution)
        final_best_solution = {t: [u.decode('utf-8')
                                   for u in best_solution[t]]
                               for t in best_solution.keys()}

        return final_best_solution, best_score



###########
# HELPERS #
###########

    def find_user_theme(self, repartition, user):
        for theme in repartition.keys():
            if user in repartition[theme]:
                return theme
        raise Exception("User not found")

    def add_user_to_theme(self, repartition, theme, user):
        repartition[theme].append(user)
        if user in self.user_to_team.keys():
            for teammate in self.user_to_team[user]:
                if teammate != user:
                    t_theme = self.find_user_theme(repartition, teammate)
                    verif_teammate = repartition[t_theme].pop(repartition[t_theme].index(teammate))
                    assert(teammate == verif_teammate)
                    repartition[theme].append(teammate)
        return repartition



    def generate_solution_space(self, users, themes, limit=10000):
        index_to_user = {i: user for i, user in enumerate(users)}
        all_permutations = itertools.permutations(range(len(users)))

        n_group = int(len(users) / len(themes))

        all_solutions = []
        for perm in all_permutations:
            solution = {}
            for i, theme in enumerate(themes):
                if i != len(themes) - 1:
                    solution[theme] = perm[i * n_group: (i + 1) * n_group]
                else:
                    solution[theme] = perm[i * n_group:]

            real_solution = {t: [index_to_user[s] for s in solution[t]] for t in solution.keys()}
            all_solutions.append(real_solution)
            if len(all_solutions) > limit:
                break

        return all_solutions

    def evaluate_solution(self, solution, preferences):

        score = 0
        for t in solution.keys():
            for u in solution[t]:
                score_calculation = self.inverted_pref[u][t]
                score += score_calculation

        return score





