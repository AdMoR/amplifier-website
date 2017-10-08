import pickle
from ..user_data import User
import copy
import itertools
import random


class ThemeSelector(object):

    def __init__(self, preference_dicts):
        '''
        Algs
        '''
        self.preferences = preference_dicts

    def assign_theme_to_users(self, themes=['t1', 't2', 't3'], filler='t0'):
        """
        """

        # 1 : Calculate the split that we want to reach and
        # how many user should move from prefered theme
        n_users = len(self.preferences)
        n_user_per_theme = n_users / len(themes)

        # 2 : Get repartition and create correctness margin based on filler
        repartitions = {t: [] for t in themes + [filler]}
        for user in self.preferences.keys():
            first_pref = self.preferences[user].get(1)
            repartitions[first_pref].append(user)
        # the margin is based on the number of fillers
        filler_margin = len(repartitions[filler]) / (len(themes) - 1)

        # 3 : Assign users from the largest theme to the smallest
        attempt_repartition = copy.deepcopy(repartitions)
        best_repartition = None
        best_score = 10000
        for attempt in range(1000):
            repartition, score = self.random_filling(attempt_repartition, themes, filler, filler_margin)
            if attempt % 9 == 0:
                print('Debug : Current score {}'.format(score))
            if score < best_score:
                print('New best score', score, best_score, 'optimal score', n_users)
                best_repartition = copy.deepcopy(repartition)
                best_score = copy.deepcopy(score)

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
                randin_index = random.randint(1, 10000) % len(repartitions[biggest_t])
                random_user = repartitions[biggest_t].pop(randin_index)
                repartitions[smallest_t].append(random_user)
            max_difference = len(repartitions[biggest_t]) - len(repartitions[smallest_t])
            return max_difference

        max_difference = one_step(repartitions, themes, act=False)
        # Do the random assignement while the gap is too big
        while max_difference > filler_margin:
            max_difference = one_step(repartitions, themes)

        # Assign randomly the filler
        if filler in repartitions.keys():
            for i, user in enumerate(repartitions[filler]):
                theme_key = themes[i % len(themes)]
                repartitions[theme_key].append(user)

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

        return best_solution, best_score



###########
# HELPERS #
###########


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
        theme_selected_per_user = {}
        for t in solution:
            for u in solution[t]:
                theme_selected_per_user[u] = t

        score = 0
        for u in preferences:
            score_calculation = [k for k in preferences[u].keys()
                                 if preferences[u][k] == theme_selected_per_user[u]]
            if not (len(score_calculation) == 1):
                print('error', score_calculation, theme_selected_per_user[u], preferences[u])
                raise Exception
            score += sum(score_calculation)

        return score





