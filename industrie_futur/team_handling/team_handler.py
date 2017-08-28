import pickle
from ..user_data import User


class Team(object):

    def __init__(self, name, description, creator, image_url):
        '''
        Very basic object to represent a team
        The creator can accept pending users in his team
        '''
        self.name = name
        self.description = description
        self.creator = creator
        self.image_url = image_url
        self.pending_members = []
        self.members = [creator]

    def validate_member(self, user_id):
        '''
        After validation from the creator, a user can then be a member of the team
        '''
        self.members.append(user_id)
        self.pending_members.remove(user_id)

    def add_member(self, user_id):
        '''
        Add a member to the pending list that must be verified by the user
        '''
        self.pending_members.append(user_id)

    def is_complete(self):
        return len(self.members) > 2

    def _to_dict_(self):
        str_dict = self.__dict__
        #str_dict['creator'] = self.available_members[self.creator].pretty_name
        return str_dict


class TeamHandler(object):

    def __init__(self, redis):
        '''
        TeamHandler is just a wrapper to handle all the teams together and save to db
        when an update is done
        '''
        self.redis = redis

        teams_from_redis = self.redis.get('teams')
        if teams_from_redis is None:
            self.all_teams = []
        else:
            self.all_teams = pickle.loads(teams_from_redis)

    def save_teams(self):
        '''
        Function used to save the teams
        '''
        self.redis.set('teams', pickle.dumps(self.all_teams))

    def get_incomplete_teams(self):
        '''
        Show the team where the user can join
        '''
        return [t for t in self.all_teams if not t.is_complete()]

    def create_team(self, name, description, creator, image_url):
        '''
        Create a team and saves
        '''
        self.all_teams.append(Team(name, description, creator, image_url))
        self.save_teams()

    def delete_team(self, team):
        print(team, team.__dict__, self.all_teams)
        self.all_teams.remove(team)
        print(self.all_teams)
        self.save_teams()

    def add_member_in_team_by_name(self, name, member_name):
        '''
        Add a user to a team if the team exists and save to DB
        '''

        for team in self.all_teams:
            if team.name == name:
                team.add_member(member_name)
                self.save_teams()
                break

    def get_user_team(self, user_id):
        '''
        Retrieve the logged in user team
        '''
        for team in self.all_teams:
            if team.creator == user_id:
                return team
        return None
