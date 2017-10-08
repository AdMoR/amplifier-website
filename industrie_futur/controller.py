# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import json
from flask import render_template, Blueprint, jsonify, request, send_from_directory, g
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.wrappers import Response
from dateutil.parser import parse
import random
from config import Config as config
from . import LOG, sentry, login_manager
from . import app
import requests
import pickle
from .user_data.user import User
from .databases import RedisUserHandler, UserAlreadyCreatedException
from .user_data import MissingFieldException, InvalidEmailException, LowLengthPasswordException,\
                       InvalidBirthdateException
from .team_handling import Team, TeamHandler, ThemeSelector


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


@api_v1.route("/", methods=['GET'])
@api_v1.route("/home", methods=['GET'])
def main():
    return render_template("home_factored.html"), 200


@api_v1.route("/t1", methods=['GET'])
def t1():
    return render_template("template_page_content.html",
                           title="Organisation et management dans l’industrie du futur",
                           indexes=["03", "05", "07", "09"]), 200


@api_v1.route("/t2", methods=['GET'])
def t2():
    return render_template("template_page_content.html",
                           title="Comment garantir l’employabilité des professionnels?",
                           indexes=["10", "12", "14", "16"]), 200


@api_v1.route("/t3", methods=['GET'])
def t3():
    return render_template("template_page_content.html",
                           title="Des structures et moyens pour accompagner",
                           indexes=["17", "19", "21", "23"]), 200


@api_v1.route("/fillform", methods=['GET'])
def get_form():
    return render_template("fill_form.html"), 200


@api_v1.route("/faq", methods=['GET'])
def faq():
    return render_template("FAQ.html"), 200


@api_v1.route("/fillform", methods=['POST'])
def fill_form():
    print(request.__dict__)
    sent_back_form = request.form
    try:
        print(sent_back_form.__dict__)
        name = sent_back_form.get('name')
        lastname = sent_back_form.get('lastname')
        email = sent_back_form.get('email')
        age = sent_back_form.get('age')
        password = sent_back_form.get('password')

        print(name, lastname, email, age, password)

        if (name is None or name == '') or\
           (lastname is None or lastname == '') or\
           (email is None or email == '') or\
           (password is None or password == '') or\
           (age is None or age == ''):
            raise MissingFieldException("Merci de remplir tous les champs.")

        if '@' not in email:
            raise InvalidEmailException

        if len(password) < 6:
            raise LowLengthPasswordException

        user = User(cache=redis_access,
                    email=sent_back_form.get('email'),
                    password=sent_back_form.get('password'),
                    form=sent_back_form)
        user.create_user()
        login_user(user, remember=True)

        invite_user_to_slack(first_name=name, last_name=lastname,
                             email=email, token=config.get('slack-invite-token'))

        return render_template("fill_form.html",
                               success="Merci {}, votre compte a ete cree.".format(user.email)), 200
    except MissingFieldException:
        return render_template("fill_form.html",
                               error="Le formulaire n'a pas ete rempli correctement!"), 200
    except InvalidBirthdateException:
        return render_template("fill_form.html",
                               error="La date de naissance est erronée : le format est jj/mm/aaaa"), 200
    except LowLengthPasswordException:
        return render_template("fill_form.html",
                               error="Le mot de passe doit faire au moins 6 caracteres"), 200
    except InvalidEmailException:
        return render_template("fill_form.html",
                               error="L'adresse email est incorrecte !"), 200
    except UserAlreadyCreatedException:
        return render_template("fill_form.html",
                               success="Utilisateur deja enregistre!"), 200


@api_v1.route("/login", methods=['GET'])
def guest_login():
    LOG.debug(type(current_user))
    try:
        valid = current_user.check_user()
        print("Valid is {}".format(valid))
        has_team = team_handler.get_user_team(current_user.email) is not None
        if valid is True:
            login_user(current_user, remember=True)
            return render_template("login.html", success="Deja authentifie", has_team=has_team), 200
        else:
            return render_template("login.html"), 200
    except AttributeError:
        return render_template("login.html"), 200


@api_v1.route("/login", methods=['POST'])
def login():
    user = User(cache=redis_access,
                email=request.form.get('email'),
                password=request.form.get('password').encode('utf-8'))
    LOG.debug('user is', user.__dict__)
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
def view_team_list(success=None):
    available_teams = team_handler.get_incomplete_teams()
    has_team = team_handler.get_user_team(current_user.email) is not None
    dict_formated_av_teams = [t._to_dict_() for t in available_teams]
    return render_template("choose_your_team.html", join_team=True,
                           success=success,
                           available_teams=dict_formated_av_teams, has_team=has_team), 200


@api_v1.route("/join_team", methods=['POST'])
@login_required
def join_team():

    # The post button will give the selected team id
    team_id = request.form["team"]
    # We assign the current user to the team
    team_creator = team_handler.add_member_in_team_by_name(team_id, current_user.email)
    requests.post(url=config.get('helpbot_warning_url'),
                  data=json.dumps({"email": team_creator}),
                  headers={"Content-Type": "application/json"})

    # Render the normal view of team
    return view_team_list(success="Candidature envoyee au gestionnaire de l'equipe")


@api_v1.route("/view_team", methods=['GET'])
@login_required
def view_team():
    user_team = team_handler.get_user_team(current_user.email)
    has_team = user_team is not None
    if user_team is None:
        return render_template("choose_your_team.html", has_team=has_team,
                               error="Tu ne dispose pas d'une equipe a gerer."), 200
    else:
        return render_template("view_team.html", has_team=has_team,
                               team=user_team._to_dict_()), 200


@api_v1.route("/view_team", methods=['POST'])
@login_required
def add_member_to_team():
    user_team = team_handler.get_user_team(current_user.email)
    if user_team is None:
        return render_template("view_team.html",
                               error="Erreur : impossible de retrouver l'équipe."), 200
    else:
        user_id = request.form["team"]
        user_team.validate_member(user_id)
        team_handler.save_teams()
        return render_template("view_team.html",
                               team=user_team._to_dict_()), 200


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
                        {'name': "touch robot", 'url': "img/robot_touch.gif"},
                        {'name': "fabric", 'url': "img/fabric.gif"},
                        {'name': "manufacture", 'url': "img/usine.gif"},
                        {'name': "science power", 'url': "img/science.gif"}
                        ]
    return render_template("choose_your_team.html",
                           available_images=available_images,
                           create_team=True), 200


@api_v1.route("/create_team", methods=['POST'])
@login_required
def create_team():
    sent_back_form = request.form

    #try:
    name = sent_back_form.get('name')
    image_url = sent_back_form.get('logo')
    description = sent_back_form.get('description')

    print(sent_back_form.__dict__)

    team_handler.create_team(name, description, current_user.email, image_url)

    dict_formated_av_teams = [team_handler.all_teams[-1]._to_dict_()]

    return render_template("choose_your_team.html", join_team=True,
                           has_team=True,
                           success="Equipe cree =)",
                           available_teams=dict_formated_av_teams), 200


@api_v1.route("/delete_team", methods=['POST'])
@login_required
def delete_team():
    user_team = team_handler.get_user_team(current_user.email)
    if user_team is None:
        return render_template("view_team.html",
                               error="Erreur : impossible de retrouver l'equipe."), 200
    else:
        team_handler.delete_team(user_team)
        return render_template("choose_your_team.html"), 200


@api_v1.route("/update_team", methods=['POST'])
@login_required
def update_team():
    user_team = team_handler.get_user_team(current_user.email)
    if user_team is None:
        return render_template("view_team.html",
                               error="Erreur : impossible de retrouver l'equipe."), 200
    else:
        description = request.form.get('description')
        user_team.description = description
        team_handler.save_teams()
        return render_template("view_team.html",
                               team=user_team._to_dict_()), 200


@api_v1.route("/challenge", methods=['GET'])
def view_challenge():
    return render_template("challenge.html"), 200


@api_v1.route("/alliance", methods=['GET'])
def view_alliance():
    return render_template("alliance.html"), 200


@api_v1.route("/slack", methods=['GET'])
def slack_info():
    return render_template("slack.html"), 200

@api_v1.route("/orga", methods=['GET'])
def organisation():
    return render_template("orga.html"), 200


@api_v1.route('/info', methods=['GET'])
def info():
    """Display API basic informations. Useful for Healthcheck."""
    code, response = 200, {'status': 'ok',
                           'status_message': 'everything is cool'}

    return jsonify(response), code


@api_v1.route('/79f4b714fb0a195e35613323cd1b0c1a', methods=['GET'])
def admin_info():
    available_actions = ['Visualize member']
    available_choices = {'Visualize member': redis_access.get_user_list(),
                         'Stats': []}
    print(available_choices)
    return render_template("admin.html",
                           available_actions=available_actions,
                           available_choices=available_choices,
                           view_option=True), 200


@api_v1.route('/79f4b714fb0a195e35613323cd1b0c1a', methods=['POST'])
def retrieve_admin_info():

    sent_back_form = request.form
    action = sent_back_form.get('action')

    if action == 'Visualize member':
        #member_email = sent_back_form.get('choice')
        #print('email', member_email)
        #data = User.get(redis_access, member_email)
        available_results = []
        schools = {}
        email_list = redis_access.get_user_list()
        email_list = [str_.decode('utf-8') for str_ in email_list]
        for email in redis_access.get_user_list():
            session = pickle.loads(redis_access.hget(email, "session"))
            available_results.append(session)
            if 'school' in session.keys():
                if session['school'][0] not in schools:
                    schools[session['school'][0]] = 0
                schools[session['school'][0]] += 1
        print('available result : ', available_results)

        return render_template("admin.html",
                               see_result=True,
                               num_results=len(available_results),
                               schools=schools,
                               email_list=email_list,
                               available_results=available_results), 200
    else:
        return admin_info()


@api_v1.route("/invite_all", methods=['GET'])
def view_missing_emails():

    response = requests.get(url=config.get('helpbot_email_list'),
                            headers={"Content-Type": "application/json"})
    email_list = json.loads(response.text)['email_list']
    email_list = [m for m in email_list]

    print(email_list)

    users_on_site = redis_access.get_user_list()
    users_on_site = [m.decode('utf-8') for m in users_on_site]
    missing_emails = [m for m in users_on_site if m not in email_list]
    print(missing_emails, len(users_on_site), len(email_list))

    # Render the normal view of team
    return render_template("invite.html",
                           missing_emails=missing_emails), 200


@api_v1.route("/invite_all", methods=['POST'])
def reinvite_missing_emails():

    response = requests.get(url=config.get('helpbot_email_list'),
                            headers={"Content-Type": "application/json"})
    email_list = json.loads(response.text)['email_list']
    email_list = [m for m in email_list]

    users_on_site = redis_access.get_user_list()
    users_on_site = [m.decode('utf-8') for m in users_on_site]
    missing_emails = [m for m in users_on_site if m not in email_list]
    print(missing_emails, len(users_on_site), len(email_list))

    # Missed users
    success = []
    for email in missing_emails:
        user = redis_access.get_user(email)
        first_name, last_name = user['form']['name'][0], user['form']['lastname'][0]
        resp = invite_user_to_slack(first_name, last_name, email, config.get('slack-invite-token'))
        resp = json.loads(resp)
        print(resp)
        if resp.get('ok'):
            success.append(email)

    return render_template("invite.html",
                           success=success), 200


@api_v1.route("/theme_selector", methods=['GET'])
def theme_selector():

    all_emails = redis_access.get_user_list()
    themes = ['t1', 't2', 't3']
    user_preferences = {}

    # We build the preference dict for all users
    print(all_emails)
    for user in all_emails:
        preference = {}
        session = redis_access.get_session(user)

        # First preference : always there
        pref1 = session['favtheme'][0]
        if pref1 == 't0':
            if random.randint(1, 10) % 2 == 0:
                preference = {1: 't3', 2: 't2', 3: 't1'}
            else:
                preference = {1: 't2', 2: 't3', 3: 't1'}
        else:
            preference[1] = pref1

        # Second preference is not always there and has different forms
        if len(preference) < 3:
            if len(session['favtheme']) > 1:
                pref2 = session['favtheme'][1]
            elif 'favtheme2' in session.keys():
                pref2 = session['favtheme2'][0]
            else:
                pref2 = 't0'
                if not pref2 == 't0' and not pref1 == pref2:
                    preference[2] = pref2

        # Put third pref as deduction from pref 1 and 2
        if len(preference) == 2:
            missing_key = [t for t in themes if t not in list(preference.values())]
            preference[3] = missing_key[0]

        if len(preference) == 1:
            missing_key = [t for t in themes if t not in list(preference.values())]
            rand_index = random.randint(1, 5) % len(missing_key)
            rand_index_po = (rand_index + 1) % len(missing_key)
            preference[2] = missing_key[rand_index]
            preference[3] = missing_key[rand_index_po]

        user_preferences[user] = preference

    print(user_preferences)

    th_se = ThemeSelector(user_preferences)
    results, score = th_se.assign_theme_to_users(themes, filler='t0')

    presented_results = {}
    for u in user_preferences:
        presented_results[u] = {'assigned': t for t in results.keys()
                                if u in results[t]}
        presented_results[u].update(user_preferences[u])

    return render_template("theme.html",
                           score=score,
                           results=presented_results), 200


######### Helper #############################


def get_user_per_preferences(redis_access):
    pass



def invite_user_to_slack(first_name, last_name, email, token):
    url = "https://slack.com/api/users.admin.invite?token={}&email={}&first_name={}&last_name={}"
    response = requests.post(url.format(token, email, first_name, last_name))
    return response.text


######### Session ##############################################################
@login_manager.user_loader
def load_user(user_id):
    this_user = User.get(redis_access, user_id)
    return this_user


@login_manager.unauthorized_handler
def unauthaurized():
    return render_template("error.html",
                           message="You are not authorized to access this page. Please login first."), 403
