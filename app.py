import os
from flask import Flask, render_template, request, session, redirect, url_for
import spotipy
from spotipy import Spotify
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

sp = Spotify(auth_manager=sp_oauth)

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

@app.route('/camelotify', methods=POST) #directs to first page of camelotify
def camelotify():
    if not log_check():
        return redirect(url_for('login'))
    playlists = gather_playlists()
    playlists_info = [(pl['name'], pl['id']) for pl in playlists]
    return render_template("camelotify.html", playlists=playlists_info)

@app.route('/camelotify/selected', methods=POST)
def camelotify_selected():
    if not log_check():
        return redirect(url_for('login'))
    playlist_id = request.form.get('playlist_id')
    return render_template("selected.html", playlist_id=playlist_id)
    


@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('camelotify'))

@app.route('/test-session')
def test_session():
    session['foo'] = 'bar'
    return f"Session test: {session.get('foo')}"

def log_check():
    token_info = cache_handler.get_cached_token()
    print("Cached token info:", token_info)
    valid = sp_oauth.validate_token(token_info)
    print("Is token valid?", valid)
    return valid

def gather_playlists(): #returns a list of all user playlists
    playlists = []
    limit = 50
    offset = 0

    while True:
        response = sp.current_user_playlists(limit=limit, offset=offset)
        items = response['items']
        if not items:
            break
        playlists.extend(items)
        offset += limit
    return playlists


if __name__ == '__main__':
    app.run(debug=True)