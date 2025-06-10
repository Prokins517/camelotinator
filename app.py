import os
import random
from flask import Flask, render_template, request, session, redirect, url_for
import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)  

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

@app.route('/camelotify', methods=["GET","POST"]) #directs to first page of camelotify
def camelotify():
    if not log_check():
        return redirect(url_for('login'))
    playlists = gather_playlists()
    playlists_info = [(pl['name'], pl['id']) for pl in playlists]
    return render_template("camelotify.html", playlists=playlists_info)

@app.route('/camelotify/selected', methods=["POST"])
def camelotify_selected():
    if not log_check():
        return redirect(url_for('login'))
    playlist_id = request.form.get('playlist_id')

    return render_template("selected.html", playlist_id=playlist_id)
    
@app.route('/camelotify/selected/copy')
def camelotify_selected_copy():
    if not log_check():
        return redirect(url_for('login'))
    user_id = sp.current_user()['id'] # Get User ID
    playlist_id = request.form.get('playlist_id')
    playlist_data = playlist_datagather(playlist_id) # retrieve details of playlist
    sp.user_playlist_create(user=user_id, name='playlist_data["name"]', public=False, description='Camelotify made this playlist smooth like buttah. See [camelotify link here] for more details.')# create new playlist with almost identical details, only name different
    # modify that playlist with camelotification.
    return render_template("copy.html")

@app.route('/camelotify/selected/modify-same')
def camelotify_selected_modify_same():
    if not log_check():
        return redirect(url_for('login'))
    playlist_id = request.form.get('playlist_id')
    return render_template("modify_same.html")


@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('camelotify'))

@app.route('/test-session')
def test_session():
    session['foo'] = 'bar'
    return f"Session test: {session.get('foo')}"

# Global Variables
camelot_keys = [
    "1A", "2A", "3A", "4A", "5A", "6A", "7A", "8A", "9A", "10A", "11A", "12A",
    "1B", "2B", "3B", "4B", "5B", "6B", "7B", "8B", "9B", "10B", "11B", "12B"
]

# helper functions
def camelotify_algo(playlist_info): # Main code of application is here!!! 
    origin_tracks = playlist_info['tracks']
    track_uris = [track['uri'] for track in origin_tracks]
    audiofeats = gather_audiofeats(track_uris)
    unsorted_trackdata = [
        { #converting key and mode to camelot data, and storing all necessary data in a streamlined dict for looping
            "camelot": camelot_keys[track['key'] + (12 if track['mode'] == 1 else 0)], 
            "bpm": track['tempo'], 
            "uri": track['uri']} 
            for track in audiofeats
        ]
    sorted_track_uris = []
    first_track = random.choice(unsorted_trackdata)
    current_track = first_track
    sorted_track_uris.append(first_track)

    
    for track in unsorted_trackdata:
        next_track = nearest_track(current_track)
        sorted_track_uris.append(next_track['uri'])
        unsorted_trackdata.remove(current_track)
        current_track = next_track
    return sorted_track_uris # This returns a list of track URIs sorted.
    



def log_check():
    token_info = cache_handler.get_cached_token()
    print("Cached token info:", token_info)
    valid = sp_oauth.validate_token(token_info)
    print("Is token valid?", valid)
    return valid

def nearest_track(current_track, unsorted_tracks):

    matching_keys = [track for track in unsorted_tracks if track['camelot'] == current_track['camelot'] and track != current_track]
    if not matching_keys:
        matching_keys = compatible_key_tracks(current_track)
    if not matching_keys:
        #decide whether to return an error message or find next closest. This would be a disconnect that you dont want happening at all.
        
    matching_bpm = [track for track in matching_keys if track['bpm'] == current_track['bpm'] and track != current_track]
    if not matching_bpm:
        #find nearest bpm! use it!
    # search unsorted list for identical keys
        # if no identical, search unsorted list for compatible keys
        # if still no identical, search for nearest incompatible key
    # search from among selected key list for identical tempos
        # if no identical, search selected key list for nearest
    # The nearest tempo, compatible-key song (or nearest key) is the nearest. 

def compatible_key_tracks(current_track):
    # set up compatible key sorting here using your useful little camelot datapack table you set up before

    
    


def gather_audiofeats(uri_list):
    all_trackdata = []
    offset = 0
    limit = 100

    while True:
        response = sp.audio_features(uri_list, offset=offset, limit=limit)
        trackdata = response
        if not trackdata:
            break
        all_trackdata.extend(response)
        offset += limit


def playlist_datagather(playlist_uri):
    playlist_info = sp.playlist(playlist_uri) #get playlist info
    images = (playlist_info['images']) #get playlist cover art
    cover_url = images[0]['url'] if images else None #get cover art url
    data = { #store in a dict
        'name': playlist_info['name'],
        'cover_url': cover_url,
        'tracks': (playlist_trackgather(playlist_uri))
    }
    return data #return the dict.

def playlist_trackgather(playlist_uri):
    all_tracks = []
    offset = 0
    limit = 100

    while True:
        response = sp.playlist_items(playlist_uri, offset=offset, limit=limit)
        items = response['items']
        if not items:
            break
        all_tracks.extend(items)
        offset += limit
    return all_tracks

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

# app run code
if __name__ == '__main__':
    app.run(debug=True)