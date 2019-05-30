from flask import Flask, render_template,request
import os
import requests
import re
import sys
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)


@app.route("/", methods=["GET","POST"])
def home():
    if request.method == 'POST':
        url = request.form['full_url']
        app.logger.debug(url)

        resolved_url = resolve_url(url)
        return render_template('index.html', resolved_url=resolved_url)
    elif request.method == 'GET':
        return render_template('index.html')


def resolve_url(url):
    sess = requests.session()
    digi_login(url,sess)

def digi_login(url, session):
    """
    :param url:  Full URL to the article
    :param session: A session manager
   """

    username = os.environ.get("digi_username")
    password = os.environ.get("digi_password")

    response = session.get("https://auth.tumedia.no/logg-inn")

    token = fetch_csrf_token(response.content)

    form_data = {
        "_token": token,
        "email": username,
        "password": password,
        "remember": "on",
        "loginButton": ""
    }

    response = session.post("https://auth.tumedia.no/logg-inn",data=form_data)
    app.logger.debug(response.content)

def fetch_csrf_token(content):
    regex = r"<meta name=\"csrf-token\" content=\"(.*)\">"
    matches = re.findall(regex, str(content), re.MULTILINE)
    return matches[0]


if __name__ == "__main__":
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True)
