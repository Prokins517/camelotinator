import os
from flask import Flask, render_template, request, session, redirect, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="cba82416e2334bc99ac19671adbb9308",
                                               client_secret="2bc032351c8c42df8eb629b19cf2896f",
                                               redirect_uri="http://127.0.0.1:5000/callback",
                                               scope="user-library-read"))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urarandom(64)

client_id = 'cba82416e2334bc99ac19671adbb9308' #store these in environment variables or in a secure credential store, they should not be in the code like this.
client_secret = '2bc032351c8c42df8eb629b19cf2896f'
redirect_uri = http://127.0.0.1:5000/callback
scope = 'playlist-read-private,playlist-read-collaborative,playlist-modify-private,playlist-modify-public'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth ( #setting up authentication manager
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler
    show_dialog=true #shows login screen that user will see to login

)
if __name__ == '__app__':
    app.run(debug=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/message', methods=["POST"])
def message():
    message = request.form.get("message", "You did not enter a message.")
    return render_template("message.html", message=message)

@app.route('/login')
def login():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()): # make this into a 'check if logged in' function
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('camelotify'))

@app.route('/camelotify')
def camelotify():
    #run check if logged in function, do nothing if logged in, login if not
    
    # put all code for displaying playlists here, compile into html using a template, then render that template.
    return render_template("camelotify.html")

@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('camelotify'))