# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import json
import hashlib
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
from . import audiotools
from . import wavenet


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
    name = request.form.get("name")
    background_type = request.form.get('music')
    is_template = request.form.get("selectMe") != ""
    subcategory = request.form.get("subcategory")

    ad_text = request.form.get('ad_text') or request.form.get("selectMe") or None
    website = request.form.get("website")

    if is_template:
        ad_text = ad_text.format(CLIENT_NAME=name, CLIENT_WEBSITE=website, PRODUCT_SUBCATEGORY=subcategory)

    print(ad_text)

    final_ad_filenname = build_ad(ad_text, background_type)

    return render_template("music_display.html", caption=ad_text, audio_file="sound/{}".format(final_ad_filenname)), 200


@api_v1.route("/music", methods=['GET'])
def music():
    sound_path = "sound/wurth1_with_music.wav"
    return render_template("music_display.html", audio_file=sound_path), 200


@api_v1.route("/dashboard", methods=['GET'])
def dashboard():
    return render_template("dashboard.html"), 200


######### Helpers ###################################

def build_ad(text, background_type):
    wavenet_filename = hashlib.sha1(b'text').hexdigest()
    wavenet_path = "{}/{}.mp3".format(config.SOUND_PATH, wavenet_filename)

    background_path = "{}/{}".format(config.SOUND_PATH, background_type)

    wavenet.generate_speech(output_path=wavenet_path, text=text)

    output_file_name = "{}.{}.mp3".format(wavenet_filename, background_type, config.SPEAKING_RATE, config.PITCH)
    output_path = "{}/{}".format(config.SOUND_PATH, output_file_name)
    audiotools.mix_audio(background_path, wavenet_path, output_path, loundness_diff=config.LOUDNESS_DIFF)

    return output_file_name

######### Session ##############################################################
@login_manager.user_loader
def load_user(user_id):
    this_user = User.get(redis_access, user_id)
    return this_user


@login_manager.unauthorized_handler
def unauthaurized():
    return render_template("error.html",
                           message="You are not authorized to access this page. Please login first."), 403
