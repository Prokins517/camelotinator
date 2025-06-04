import os
from flask import Flask, render_template, request, session, redirect, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)  # Fixed typo: urandom not urarandom

client_id = 'cba82416e2334bc99ac19671adbb9308'
client_secret = '2bc032351c8c42df8eb629b19cf2896f'
redirect_uri = 'http://127.0.0.1:5000/callback'
scope = 'playlist-read-private,playlist-read-collaborative,playlist-modify-private,playlist-modify-public'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)

def log_check():
    token_info = cache_handler.get_cached_token()
    return sp_oauth.validate_token(token_info)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/message', methods=["POST"])
def message():
    message = request.form.get("message", "You did not enter a message.")
    return render_template("message.html", message=message)

@app.route('/login')
def login():
    if not log_check():
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('camelotify'))

@app.route('/camelotify')
def camelotify():
    if not log_check():
        return redirect(url_for('login'))
    


    
    return render_template("camelotify.html")

@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('camelotify'))

if __name__ == '__main__':
    app.run(debug=True)