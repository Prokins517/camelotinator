from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="cba82416e2334bc99ac19671adbb9308",
                                               client_secret="2bc032351c8c42df8eb629b19cf2896f",
                                               redirect_uri="http://127.0.0.1:5000/callback",
                                               scope="user-library-read"))

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/message', methods=["POST"])
def message():
    message = request.form.get("message", "You did not enter a message.")
    return render_template("message.html", message=message)