# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import json
from flask import render_template, Blueprint, jsonify, request, send_from_directory, g
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.wrappers import Response
import random
from config import Config as config
from . import LOG, sentry, login_manager
from . import app
import requests
import pickle
from .user_data.user import User
from .databases import RedisUserHandler, UserAlreadyCreatedException


redis_access = RedisUserHandler()
api_v1 = Blueprint('website_amplifier', __name__, template_folder='templates')

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



@api_v1.route("/form", methods=['GET'])
def form():
    return render_template("fill_form.html"), 200


@api_v1.route("/form", methods=['POST'])
def post_form():
    sent_back_form = request.form
    ad_text = sent_back_form.get('ad_text')
    print(">>>>>>> ", ad_text)
    return render_template("music_display.html", caption=ad_text), 200


@api_v1.route("/music", methods=['GET'])
def music():
    return render_template("music_display.html"), 200



######### Session ##############################################################
@login_manager.user_loader
def load_user(user_id):
    this_user = User.get(redis_access, user_id)
    return this_user


@login_manager.unauthorized_handler
def unauthaurized():
    return render_template("error.html",
                           message="You are not authorized to access this page. Please login first."), 403
