# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import json
from flask import render_template, Blueprint, jsonify, request, send_from_directory, g
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.wrappers import Response
from pydub import AudioSegment
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

template = ["Looking for {PRODUCT_SUBCATEGORY}? Get on {CLIENT_WEBSITE}. We've got the best {PRODUCT_SUBCATEGORY}. {CLIENT_NAME}, {CLIENT_WEBSITE}.",
            "Thinking about {PRODUCT_SUBCATEGORY}. Select the best quality, go for {CLIENT_NAME}, {CLIENT_WEBSITE}."]



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
    return render_template("fill_form.html", template=template), 200


@api_v1.route("/form", methods=['POST'])
def post_form():
    sent_back_form = request.form

    name = sent_back_form.get("name")
    is_template = sent_back_form.get("selectMe") != ""
    ad_text = sent_back_form.get('ad_text') or sent_back_form.get("selectMe") or None
    website = sent_back_form.get("website")
    background_type = sent_back_form.get('music')

    if is_template:
        ad_text = ad_text.format(CLIENT_NAME=name, CLIENT_WEBSITE=website, PRODUCT_SUBCATEGORY="hammers")

    print(ad_text)
    sound_path = combine_audios(audio_a="amplifier/static/sound/test.wav", audio_b="amplifier/static/sound/{}.wav".format(background_type), export_name=name)

    print(">>>>>>> ", ad_text)
    sound_path = "sound/wurth1_with_music.wav"
    return render_template("music_display.html", caption=ad_text, audio_file=sound_path), 200


@api_v1.route("/music", methods=['GET'])
def music():
    sound_path = "sound/wurth1_with_music.wav"
    return render_template("music_display.html", audio_file=sound_path), 200


######### Helpers ###################################


def combine_audios(audio_a="test.wav", audio_b="ModernFashion.wav", export_name="export"):

    export_path = "sound/{}.wav".format(export_name)

    voice1 = AudioSegment.from_file(audio_a)
    soundtrack = AudioSegment.from_file(audio_b)
    combined = soundtrack.overlay(voice1, position=5000)

    combined.export("amplifier/static/" + export_path, format='wav')
    return export_path



######### Session ##############################################################
@login_manager.user_loader
def load_user(user_id):
    this_user = User.get(redis_access, user_id)
    return this_user


@login_manager.unauthorized_handler
def unauthaurized():
    return render_template("error.html",
                           message="You are not authorized to access this page. Please login first."), 403
