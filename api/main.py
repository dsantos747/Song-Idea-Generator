# Tasks
# - Incorporate "popularity" or other filters into random song selection
# - Run query based on genre, key and bpm - to find how many songs exist with that exact combination

# Imports
from python_dotenv import load_dotenv # type: ignore
from flask import Flask, request, render_template, jsonify, session
from flask_session import Session
import os
import base64
from requests import post, get
import json
import random

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return{"Authorization": "Bearer " + token}

def get_song_by_id(token,song_id):
    url = f"https://api.spotify.com/v1/tracks/{song_id}/"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["name"] + " " + json.loads(result.content)["artists"][0]['name']
    return json_result

def get_all_genres(token):
    url = f"https://api.spotify.com/v1/recommendations/available-genre-seeds/"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["genres"]
    return json_result

def get_random_genre(token):
    url = f"https://api.spotify.com/v1/recommendations/available-genre-seeds/"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["genres"]
    return random.choice(json_result)

def convert_key(key,key_mode): # Convert Key in Pitch Class Notation into English
    key_dict = {-1:"Unknown",0:"C",1:"C#",2:"D",3:"D#",4:"E",5:"F",6:"F#",7:"G",8:"G#",9:"A",10:"A#",11:"B"}
    key_mode_dict = {0:"Minor", 1:"Major"}
    return f"{key_dict[key]} {key_mode_dict[key_mode]}"

def random_song(token,n,genres):
    url_ids = "https://api.spotify.com/v1/recommendations"    
    headers = get_auth_header(token)

    dict_keys = ['ID', 'name', 'artist', 'genre', 'key', 'bpm', 'time_signature']
    song_dict_arr = [{key: None for key in dict_keys} for _ in range(n)]
    id_arr = []

    # Generate n random song ID's
    for item in song_dict_arr:
        genre = random.choice(genres) 
        choice = random.randint(0,19)   
        query = f"?seed_genres={genre}"
        query_url = url_ids + query
        result = get(query_url, headers=headers)
        item['ID'] = json.loads(result.content)["tracks"][choice]['id']
        id_arr.append(item['ID'])
        item['genre'] = genre

    id_list = '%2C'.join(id_arr)

    # Use 1 API call to get track information for 3 songs, add to array>dictionary
    url_tracks = f"https://api.spotify.com/v1/tracks?ids={id_list}"
    result_tracks = get(url_tracks, headers=headers)

    # Use 1 API call to get track audio features for 3 songs, add to array>dictionary
    url_audio_features = f"https://api.spotify.com/v1/audio-features?ids={id_list}"
    result_audio_features = get(url_audio_features, headers=headers)
    
    # Add all info to the dict_arr
    i=0
    for item in song_dict_arr:
        item['name'] = json.loads(result_tracks.content)["tracks"][i]["name"]
        item['artist'] = json.loads(result_tracks.content)["tracks"][i]["artists"][0]['name']
        item['key'] = convert_key(json.loads(result_audio_features.content)["audio_features"][i]["key"],json.loads(result_audio_features.content)["audio_features"][i]["mode"])
        item['bpm'] = json.loads(result_audio_features.content)["audio_features"][i]["tempo"]
        item['time_signature'] = f'{json.loads(result_audio_features.content)["audio_features"][i]["time_signature"]}/4'
        i+=1
    
    return song_dict_arr


# Pre-setup variables
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

token = get_token()
genres_list = get_all_genres(token)
selected_genres = genres_list
embed_url = "https://open.spotify.com/embed/track/"

# Create the Flask app
app = Flask(__name__)

# Set up session - for user genre filter choice
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Define a route that handles a GET request
@app.route('/')
def index():
    return render_template('index.html', genres_list=genres_list)


@app.route('/post_genres', methods=['POST'])
def submit_genres():
    data = request.get_json()
    chosen_genres = data['chosenGenresList']
    session['selected_genres'] = [genre for genre in genres_list if genre in chosen_genres]

    return jsonify({'message': 'Genres updated'})

# Define a route that handles a POST request
@app.route('/get_songs', methods=['GET'])
def get_songs():
    if request.method == 'GET':
        print("request received")

        selected_genres=session.get('selected_genres',genres_list)
        song_arr = random_song(token,3,selected_genres)

        song_1_embed = embed_url + song_arr[0]['ID']
        song_1_name = song_arr[0]['name']
        song_1_artist = song_arr[0]['artist']
        song_1_genre = song_arr[0]['genre']
        song_2_embed = embed_url + song_arr[1]['ID']
        song_2_name = song_arr[1]['name']
        song_2_artist = song_arr[1]['artist']
        song_2_key = song_arr[1]['key']
        song_3_embed = embed_url + song_arr[2]['ID']
        song_3_name = song_arr[2]['name']
        song_3_artist = song_arr[2]['artist']
        song_3_bpm = song_arr[2]['bpm']
        song_3_time_signature = song_arr[2]['time_signature']
        
        return jsonify(song_1_embed=song_1_embed,song_1_name=song_1_name,song_1_artist=song_1_artist,
                       song_1_genre=song_1_genre,song_2_embed=song_2_embed,song_2_name=song_2_name,
                       song_2_artist=song_2_artist,song_2_key=song_2_key,song_3_embed=song_3_embed,
                       song_3_name=song_3_name,song_3_artist=song_3_artist,song_3_bpm=song_3_bpm,
                       song_3_time_signature=song_3_time_signature)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
