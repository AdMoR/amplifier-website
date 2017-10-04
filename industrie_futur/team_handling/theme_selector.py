import pickle
from ..user_data import User


class ThemeSelector(object):

    def __init__(self, preferences, teams, themes=['t1', 't2', 't3']):
        '''
        Algs
        '''
        self.preferences = preferences
        self.teams = teams
        self.themes = themes

    def find_admissible_repartition(self):
        """
        """

        # 1 : give everyne what they want
        repartitions = {t: self.preferences[t] for t in self.preferences.keys()
                        if t in self.themes}
        nb_per_theme = {t: len(repartitions[t]) for t in self.themes}
        print(nb_per_theme)

        # 2 : Assign the undecided to the needed themes
        no_pref_themes = [key for key in self.preferences
                          if key not in self.themes]
        print(no_pref_themes)
        for nopref in no_pref_themes:
            if nopref not in self.preferences.keys():
                continue

            while len(self.preferences[nopref]) > 0:
                smallest_theme = sorted(self.themes, key=lambda t: nb_per_theme[t])
                user_to_add = self.preferences[nopref].pop()
                print(repartitions)
                repartitions[smallest_theme[0]].append(user_to_add)
                print(repartitions)
                nb_per_theme = {t: len(repartitions[t]) for t in self.themes}

        print(nb_per_theme)
        return repartitions




