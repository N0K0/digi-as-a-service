from flask import Flask, render_template, request
import os
import requests
import re
import sys
from pprint import pprint, pformat
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        url = request.form['full_url']
        app.logger.debug(url)

        resolved_url = resolve_url(url)
        return render_template("index.html", resolved_url=resolved_url)
    elif request.method == 'GET':
        return render_template('index.html')


def resolve_url(url):
    sess = requests.session()
    sess.headers.update({'User-Agent': 'Custom user agent'})
    digi_login(sess)
    url = fetch_article(url, sess)

    return url


def fetch_article(url, sess):
    _ = sess.get(url)
    response = sess.get(url)
    #app.logger.debug(response.url)
    #app.logger.debug(response.text)

    key = fetch_share_key(response.text)
    app.logger.debug(pformat(key))
    string = f"{response.url}?key={key}"
    return string


def digi_login(session):
    """
    :param url:  Full URL to the article
    :param session: A session manager
   """

    username = os.environ.get("digi_username")
    password = os.environ.get("digi_password")

    response = session.get("https://www.digi.no/innlogging")

    token = fetch_csrf_token(response.content)
    app.logger.debug(str(token))
    app.logger.debug(pformat(response.history))

    form_data = {
        "_token": token,
        "email": username,
        "password": password,
        "remember": "on",
        "loginButton": ""
    }

    response = session.post("https://auth.tumedia.no/logg-inn", data=form_data)
    if not response.ok:
        raise RuntimeError("Something went wrong at login")


def fetch_share_key(content):
    regex = r"shareKey: '(.*?)'"
    matches = re.findall(regex, content, re.MULTILINE)
    if len(matches) == 0:
        return False
    return matches[0]


def fetch_csrf_token(content):
    regex = r"<meta name=\"csrf-token\" content=\"(.*?)\">"
    matches = re.findall(regex, str(content), re.MULTILINE)
    return matches[0]


if __name__ == "__main__":
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.run(debug=True)
