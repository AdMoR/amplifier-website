# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import json
from flask import render_template, Blueprint, jsonify, request, send_from_directory, g
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.wrappers import Response
from functools import wraps
from config import Config as config
from . import LOG, sentry, login_manager
import os
import requests
from . import app
import ast
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
        return render_template("fill_form.html", success="Thanks {}".format(name)), 200
    except:
        return render_template("fill_form.html", error="The form was not correctly filled!"), 200


@api_v1.route('/info', methods=['GET'])
def info():
    """Display API basic informations. Useful for Healthcheck."""
    code, response = 200, {'status': 'ok',
                           'status_message': 'everything is cool'}

    return jsonify(response), code

