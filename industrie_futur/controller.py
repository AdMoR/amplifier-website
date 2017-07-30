# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import json
from flask import render_template, Blueprint, jsonify, request, send_from_directory, g
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.wrappers import Response
from config import Config as config
from . import LOG, sentry, login_manager
from . import app


from .user_data.user import User
from .databases import RedisUserHandler, UserAlreadyCreatedException
from .user_data import MissingFieldException
from .team_handling import Team, TeamHandler


redis_access = RedisUserHandler()
team_handler = TeamHandler(redis_access)
api_v1 = Blueprint('website_industrie_futur', __name__, template_folder='templates')

#
# API calls handling tools
#


def format_response(response, status_code=200):
    response = Response(json.dumps(response), status=status_code,
                        mimetype='application/json')
    return response


@api_v1.route("/home", methods=['GET'])
def main():
    return render_template("home_factored.html"), 200


@api_v1.route("/test", methods=['GET'])
def test():
    return render_template("template_page_content.html"), 200


@api_v1.route("/fillform", methods=['GET'])
def get_form():
    return render_template("fill_form.html"), 200


@api_v1.route("/fillform", methods=['POST'])
def fill_form():
    print(request.__dict__)
    sent_back_form = request.form
    try:
        print(sent_back_form.__dict__)
        name = sent_back_form.get('name')
        if name is None or name == '':
            raise MissingFieldException
        user = User(cache=redis_access,
                    email=sent_back_form.get('email'),
                    password=sent_back_form.get('password'),
                    form=sent_back_form)
        user.create_user()
        valid = user.check_user()
        if valid is True:
            LOG.info("User {} was logged in !".format(name))
            login_user(user, remember=True)
        return render_template("fill_form.html",
                               success="Merci {}, votre compte a ete cree.".format(name)), 200
    except MissingFieldException:
        return render_template("fill_form.html",
                               error="Le formulaire n'a pas ete rempli correctement!"), 200
    except UserAlreadyCreatedException:
        return render_template("fill_form.html",
                               success="Utilisateur deja enregistre!"), 200


@api_v1.route("/login", methods=['GET'])
def guest_login():
    LOG.debug(current_user)
    return render_template("login.html"), 200


@api_v1.route("/login", methods=['POST'])
def login():
    user = User(cache=redis_access,
                email=request.form.get('email'),
                password=request.form.get('password'))
    LOG.debug(user)
    valid = user.check_user()
    print("Valid is {}".format(valid))
    if valid is True:
        login_user(user, remember=True)
        return render_template("login.html", success="Login reussi"), 200
    else:
        return render_template("login.html", error="Email ou mot de passe inccorect"), 200


@api_v1.route("/team", methods=['GET'])
@login_required
def team_choice():
    return render_template("choose_your_team.html"), 200


@api_v1.route("/join_team", methods=['GET'])
@login_required
def view_team_list():
    available_teams = team_handler.get_incomplete_teams()
    dict_formated_av_teams = [t._to_dict_() for t in available_teams]
    return render_template("choose_your_team.html", join_team=True,
                           available_teams=dict_formated_av_teams), 200

@api_v1.route("/join_team", methods=['POST'])
@login_required
def join_team():

    # The post button will give the selected team id
    team_id = request.form["team"]
    # We assign the current user to the team
    team_handler.add_member_in_team_by_name(team_id, current_user.email)

    # Render the normal view of team
    return view_team_list()


@api_v1.route("/create_team", methods=['GET'])
@login_required
def view_team_form():
    available_images = [{'name': "factory", 'url': "img/futur.jpg"},
                        {'name': "welcome", 'url': "img/welcome.jpg"},
                        {'name': "routourne", 'url': "img/roudente.jpg"},
                        {'name': "le futur", 'url': "img/futur.png"},
                        {'name': "tigre du turfun", 'url': "img/tigres_turfu.jpg"},
                        {'name': "revolution", 'url': "img/RI_old.png"},
                        {'name': "abstrait", 'url': "img/motards.jpg"},
                        {'name': "futurisme", 'url': "img/futurisme.jpg"},
                        {'name': "robot", 'url': "img/dance robot.gif"},
                        {'name': "revolution", 'url': "img/RI_old.png"},
                        {'name': "abstrait", 'url': "img/motards.jpg"},
                        {'name': "futurisme", 'url': "img/futurisme.jpg"},
                        {'name': "actual frankfurt", 'url': "img/modern_frankfurt.jpg"}
                        ]
    return render_template("choose_your_team.html",
                           available_images=available_images,
                           create_team=True), 200


@api_v1.route("/create_team", methods=['POST'])
@login_required
def create_team():
    sent_back_form = request.form

    print('post ', request.__dict__)

    #try:
    name = sent_back_form.get('name')
    image_url = sent_back_form.get('logo')
    description = sent_back_form.get('description')

    print(sent_back_form.__dict__)

    creator_name = current_user.email

    team_handler.create_team(name, description, creator_name, image_url)

    dict_formated_av_teams = [team_handler.all_teams[-1]._to_dict_()]
    print(dict_formated_av_teams)

    return render_template("choose_your_team.html", join_team=True,
                           success="Equipe cree =)",
                           available_teams=dict_formated_av_teams), 200


@api_v1.route("/challenge", methods=['GET'])
def view_challenge():
    return render_template("challenge.html"), 200


    #except:
    #    return render_template("choose_your_team.html", create_team=True,
    #                           error="Une erreur est survenue"), 200


@api_v1.route('/info', methods=['GET'])
def info():
    """Display API basic informations. Useful for Healthcheck."""
    code, response = 200, {'status': 'ok',
                           'status_message': 'everything is cool'}

    return jsonify(response), code


######### Helper #############################

def invite_user_to_slack(first_name, last_name, email, token):
    url = "https://slack.com/api/users.admin.invite?token={}&email={}&channels=C000000001,C000000002&first_name={}&last_name={}"
    return url.format(token, email, first_name, last_name)


######### Session ##############################################################
@login_manager.user_loader
def load_user(user_id):
    LOG.debug(user_id)
    return User.get(redis_access, user_id)


@login_manager.unauthorized_handler
def unauthaurized():
    return render_template("error.html",
                           message="You are not authorized to access this page. Please login first."), 403
