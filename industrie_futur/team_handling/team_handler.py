import pickle


class Team(object):

    def __init__(self, name, description, creator, image_url):
        self.name = name
        self.description = description
        self.creator = creator
        self.image_url = image_url
        self.members = [creator]

    def add_member(self, new_member):
        self.members.append(new_member)

    def is_complete(self):
        return len(self.members) > 2

    def _to_dict_(self):
        return self.__dict__


class TeamHandler(object):

    def __init__(self, redis):
        self.redis = redis

        teams_from_redis = self.redis.get('teams')
        if teams_from_redis is None:
            self.all_teams = [Team("SuperTeam", "A massive thank you to all the AMAZING people!",
                                   "Jean Pol", "http://m.memegen.com/yuzypt.jpg")]
        else:
            self.all_teams = pickle.loads(teams_from_redis)

    def get_incomplete_teams(self):
        return [t for t in self.all_teams if not t.is_complete()]

    def create_team(self, name, description, creator, image_url):
        self.all_teams.append(Team(name, description, creator, image_url))
        self.redis.set('teams', pickle.dumps(self.all_teams))

    def add_member_in_team_by_name(self, name, member_name):
        team = [t for t in self.all_teams if t.name == name]
        if len(team) > 0:
            team[0].add_member(member_name)

