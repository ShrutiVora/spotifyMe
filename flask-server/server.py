from flask import Flask, jsonify, request, redirect, session, url_for
from flask_cors import CORS
import requests
import random
import time
from flask_session import Session
import os



app = Flask(__name__)
app.secret_key = "123456"  # required to use flask sessions
app.config['SESSION_TYPE'] = 'filesystem'  # configures FLASK to use filesystem based sessions
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Ensure the cookie is only accessible by the server
app.config['SESSION_COOKIE_SECURE'] = False 
Session(app)
CLIENT_ID = "db4e5cf609774d2993b4fe0bbeb7fb93"
CLIENT_SECRET = "e39778cbff7642379bdf5e83d1405965"
REDIRECT_URI = "http://localhost:3000/callback"

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True, allow_headers=["Authorization", "Content-Type"], expose_headers="Authorization")
#CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}}, supports_credentials=True)
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, DELETE'
    return response

'''
@app.route("/login", methods=["POST"])
def login():
    req = request.json
    username = req.get("username")
    password = req.get("password")
    if isinstance(username, str) and isinstance(password, str):
        return jsonify({"Message": "Login Successful!"})
    else:
        return jsonify({"Message": "Login Failed"})

'''
@app.route("/login")
def login():
    auth_url = (
        'https://accounts.spotify.com/authorize'
        '?response_type=code'
        f'&client_id={CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        '&scope=user-library-read user-follow-read user-read-recently-played user-library-modify playlist-modify-public playlist-modify-private user-read-private user-read-email user-top-read'
        '&show_dialog=true'
    )
    return redirect(auth_url)

@app.route("/callback", methods=["POST"])
def callback():
    req = request.json
    code = req.get('code')
    
    if not code:
        print("Authorization code not found")
        return "Authorization code not found", 400

    token_url = 'https://accounts.spotify.com/api/token'
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    token_response = requests.post(token_url, data=payload)

    #if token_response.status_code != 200:
    #    print(f"Failed to fetch access token, status code: {token_response.status_code}, response: {token_response.text}")
    #    return f"Failed to fetch access token, status code: {token_response.status_code}, response: {token_response.text}", 400

    token_data = token_response.json()
    access_token = token_data.get('access_token')
    #if not access_token:
    #    print("Access token not found in the response")
    #    return "Access token not found in the response", 400
    print("Session contents before storing token:", dict(session)) 
    if access_token:
        session['access_token'] = access_token
        with open('access_token.txt', 'w') as f:
            f.write(access_token)
        session.permanent = True 
        print("Access token stored in session:", session.get('access_token'))
        print("Session contents after storing token:", dict(session))
        return jsonify({"Message":"Access Successful! Retrieved Access Token!", "Access": session.get('access_token')})
    else:
        return jsonify({"error": "Failed to retrieve access token"}), 400

@app.route('/profile', methods=['GET'])
def profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"Message": "Authorization header is missing"}), 401

    # Extract the token from the "Bearer" prefix
    token = auth_header.split(" ")[1]
    
    # Use the access token to fetch the user's profile data from Spotify
    profile_response = requests.get(
        'https://api.spotify.com/v1/me',
        headers={
            'Authorization': f'Bearer {token}'
        }
    )

    if profile_response.status_code == 200:
        profile_json = profile_response.json()
        return jsonify(profile_json)
    else:
        return jsonify({"Message": "Failed to fetch profile data"}), profile_response.status_code
    
@app.route("/toptracks", methods=['GET'])
def toptracks():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"Message": "Authorization header is missing"}), 401

    # Extract the token from the "Bearer" prefix
    token = auth_header.split(" ")[1]
    
    headers={
            'Authorization': f'Bearer {token}'
        }
    top_tracks=requests.get("https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=30", headers=headers)
    unique_tracks=[]
    unique_names=[]
    while len(unique_tracks)<20:
        tracks_data=top_tracks.json()
        for track in tracks_data['items']:
            if track['name'] not in unique_names:
                unique_tracks.append(track)
                unique_names.append(track['name'])
            if (len(unique_tracks)==20):
                break

    return jsonify(unique_tracks[:20])



   



@app.route("/createmoodplaylist", methods=['GET','POST'])
def create_playlist():
    req = request.json
    mood = req.get("mood")
    name = req.get("name")
    des=req.get("des")
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"Message": "Authorization header is missing"}), 401

    # Extract the token from the "Bearer" prefix
    token = auth_header.split(" ")[1]
    
    headers={
            'Authorization': f'Bearer {token}'
        }
    top_tracks=requests.get("https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=20", headers=headers)
    tracks_json=top_tracks.json()
    track_ids=[]
    for track in tracks_json['items']:
        track_ids.append(track['id'])
    

    artist_ids=[]
    top_artists_response=requests.get("https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=10", headers=headers)
    top_artists = top_artists_response.json()
    for artist in top_artists['items']:
        artist_ids.append(artist['id'])
    '''
    moods={
        "happy": {"valence": 1.0, "danceability":0.8, "energy":0.8,"loudness":-10,"tempo":100},
        "energetic":{"valence": 0.8, "danceability":0.9, "energy":1.0,"loudness":-5,"tempo":150},
        "relaxed": {"valence": 0.5, "danceability":0.3, "energy": 0.3,"loudness":-15,"tempo":70},
        "sad": {"valence": 0.1, "danceability":0.1, "energy": 0.1,"loudness":-15,"tempo":60},
        "romantic": {"valence": 0.75, "danceability": 0.4, "energy": 0.5,"loudness":-10,"tempo":80}
    }
    '''
    moods={
        "happy": {"valence": (0.8, 1.0), "danceability": (0.7, 1.0), "energy": (0.7, 1.0), "loudness": (-10, -5), "tempo": (90, 130),},
        "energetic": {"valence": (0.7, 0.9), "danceability": (0.8, 1.0), "energy": (0.9, 1.0), "loudness": (-7, -3), "tempo": (130, 160)},
        "relaxed": {"valence": (0.4, 0.6), "danceability": (0.3, 0.5), "energy": (0.2, 0.4), "loudness": (-15, -10), "tempo": (60, 90)},
        "sad": {"valence": (0.1, 0.3), "danceability": (0.2, 0.4), "energy": (0.1, 0.3), "loudness": (-15, -10), "tempo": (50, 70)},
        "romantic": {"valence": (0.6, 0.8), "danceability": (0.3, 0.5), "energy": (0.3, 0.5), "loudness": (-10, -7), "tempo": (60, 90)}
    }
    mood_features = moods.get(mood.lower(), {"valence": 0.5, "danceability": 0.5,"energy": 0.5, "loudness": -12, "tempo": 70})
    valence_level=mood_features["valence"]
    danceability_level=mood_features["danceability"]
    energy_level=mood_features["energy"]
    loudness_level=mood_features['loudness']
    tempo_level=mood_features['tempo']

    random.shuffle(artist_ids)
    seed_artists=artist_ids[:2]
    seed_tracks=track_ids[:3]
    recommendation_params = {
        "limit": 30,
        "seed_artists": ','.join(seed_artists),
        "seed_tracks": ','.join(seed_tracks),
        "target_valence": random.uniform(*mood_features["valence"]),
        "target_energy": random.uniform(*mood_features["energy"]),
        "target_danceability": random.uniform(*mood_features["danceability"]),
        "target_loudness": random.uniform(*mood_features["loudness"]),
        "target_tempo": random.uniform(*mood_features["tempo"])
    }




    '''
    
    seed_artists_str = ','.join(seed_artists)
    seed_tracks_str = ','.join(seed_tracks)
    '''

    recommended_response=requests.get(f"https://api.spotify.com/v1/recommendations", headers=headers, params=recommendation_params)
    recommended = recommended_response.json()
    rec_ids=[]
    for track in recommended['tracks']:
        rec_ids.append(track['uri'])
    
    user_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    user_info = user_response.json()
    user_id = user_info['id']

    headers1={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload={
        "name": name,
        "description": des,
        "public": True

    }
    new_playlist_response=requests.post(f"https://api.spotify.com/v1/users/{user_id}/playlists",headers=headers1,json=payload)
    new_playlist=new_playlist_response.json()
    new_playlist_id=new_playlist['id']
    
    add_tracks_response=requests.post(f"https://api.spotify.com/v1/playlists/{new_playlist_id}/tracks",headers=headers1,json={"uris": rec_ids})
    get_playlist_response=requests.get(f"https://api.spotify.com/v1/playlists/{new_playlist_id}",headers=headers)
    get_playlist=get_playlist_response.json()
    return(jsonify(get_playlist))

@app.route("/fetch-all-tracks")
def fetch_all_tracks():
    with open('access_token.txt', 'r') as f:
        token = f.read().strip()
    if not token:
        return jsonify({'error': 'No access token in session'}), 401
    headers={
            'Authorization': f'Bearer {token}'
    }

    all_tracks=[]

    top_longtracks=requests.get("https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=50", headers=headers)
    if top_longtracks.status_code == 200:
        long_tracks=top_longtracks.json()['items']
        all_tracks.extend(long_tracks)
    
    top_medtracks=requests.get("https://api.spotify.com/v1/me/top/tracks?time_range=medium_term&limit=50", headers=headers)
    if top_medtracks.status_code == 200:
        med_tracks=top_medtracks.json()['items']
        all_tracks.extend(med_tracks)
    
    top_shorttracks=requests.get("https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=50", headers=headers)
    if top_shorttracks.status_code == 200:
        short_tracks=top_shorttracks.json()['items']
        all_tracks.extend(short_tracks)
    
    
    
    #recently played from before 1 year ago- because top tracks are taken from max 1 year time frame 
    one_year_ago_ms = int(time.time() * 1000) - (365 * 24 * 60 * 60 * 1000)
    recently_played=requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=50", headers=headers)
    
    recent_tracks=recently_played.json()['items']
    all_tracks.extend([item['track']for item in recent_tracks])
    
    
    #get all playlist data
    # get all playlists
    
    all_playlists=requests.get("https://api.spotify.com/v1/me/playlists?limit=50&offset=0", headers=headers)
    if all_playlists.status_code == 200:
        playlists = all_playlists.json()['items']
        for playlist in playlists:
            id_=playlist['id']
            playlist_tracks_url=f'https://api.spotify.com/v1/playlists/{id_}/tracks?limit=50&offset=0'
            while playlist_tracks_url:
                playlist_tracks_response=requests.get(playlist_tracks_url,headers=headers)
                if playlist_tracks_response.status_code == 200:
                    playlist_tracks_data=playlist_tracks_response.json()
                    playlist_tracks=playlist_tracks_data['items']
                    all_tracks.extend([item['track'] for item in playlist_tracks])
                    playlist_tracks_url=playlist_tracks_data['next']
                else:
                    break
    print(f"Total tracks fetched: {len(all_tracks)}")
    
    return jsonify({'tracks': all_tracks})

                


@app.route("/delete", methods=['DELETE'])
def delete():
    req = request.json
    playlist_id = req.get("playlist_id")
    print(playlist_id)
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"Message": "Authorization header is missing"}), 401

    # Extract the token from the "Bearer" prefix
    token = auth_header.split(" ")[1]
    
    headers={
            'Authorization': f'Bearer {token}'
        }
    delete_response=requests.delete(f"https://api.spotify.com/v1/playlists/{playlist_id}/followers", headers=headers)
    return jsonify({"Message": "Successfully Deleted the Playlist"})


    



    


@app.route('/logout')
def logout():
    session.clear()
    open('access_token.txt', 'w').close()
    os.remove("spotify_tracks.csv")

    return redirect('http://localhost:3000/login')



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5001)
    #app.run(debug=True, use_reloader=False, port=5001, host="localhost")