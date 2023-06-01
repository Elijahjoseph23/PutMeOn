import json
import sqlite3
import numpy as np
import pandas as pd
import spotipy
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from init import get_playlist_tracks,in_playlist,get_playlist_audio_features,get_playlist_audio_features,create_dataframe_from_sql,in_evil_playlist
import time
from similar_track import get_track_similarity
from init import playlist_name,uri,dataframe
from ML import predict_likeability
import random
t=time.time()
#gets the client ids from the env file
load_dotenv(".env")
CLIENT_ID=os.getenv("CLIENT_ID","")
CLIENT_SECRET=os.getenv("CLIENT_SECRET","")
#authenticates session
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,)
#creates spotify session
session=spotipy.Spotify(client_credentials_manager=client_credentials_manager,requests_timeout=10,retries=10,status_retries=10,backoff_factor=0.3,status_forcelist=(500,502,504))

try:
    with open('user_reccomendations.json') as f:
        user_reccomendations = json.load(f)
except FileNotFoundError:
    user_reccomendations={}



conn = sqlite3.connect('playlist_data.db')


# Get the list of available database names in the .db file
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
database_names = cursor.fetchall()
print(database_names)



def find_this_is_playlist(artist):
    #finds the corresponding "This Is <artist>" playlist, given the artist
    tracks=[]
    if artist in user_reccomendations:
        return user_reccomendations[artist]
    results = session.search(q='This Is ' + artist, type='playlist')
    if len(results["playlists"]["items"])!=0:
        tracks=get_playlist_tracks(results["playlists"]["items"][0]["uri"])
    else:
        return []
    return remove_playlist_duplicates(playlist_name,tracks)

def remove_playlist_duplicates(playlist_name,tracks):
    temp=tracks[:]
    for track in tracks:
        if track["track"] is None or in_playlist(track["track"]) or "local" in track["track"]["uri"] or "episode" in track["track"]["uri"] or ("remix" in track["track"]["name"] or "Remix" in track["track"]["name"] or "REMIX" in track["track"]["name"]):
            temp.remove(track)
    return temp

def remove_remixes(tracks):
    temp=tracks[:]
    for track in tracks:
        if track["track"] is None:
            continue
        if ("remix" in track["track"]["name"] or "Remix" in track["track"]["name"] or "REMIX" in track["track"]["name"]):
            temp.remove(track)
    return temp

different=False
print("Getting Reccomendations...")
try:
    with open('artist_song_count.json') as f:
        artist_song_count = json.load(f)
except FileNotFoundError:
    artist_song_count={}

if playlist_name in artist_song_count:
    song_count=artist_song_count[playlist_name]
else:
    song_count={}

playlist_artists=set()
for index,track in dataframe.iterrows():
    print(track["artist"]+"---------------------------------")
    artists=track["artist"].split("|")
    for artist in artists:
        if artist in playlist_artists:
            song_count[artist]=song_count[artist]+1
        else:
            song_count[artist]=1
            playlist_artists.add(artist)
        if not artist in user_reccomendations:
            user_reccomendations[artist]=(find_this_is_playlist(artist))
            different=True         
        break #remove if you want artist features as well as the first artist
    print(index+1)



new_artists=[]

sorted_items = sorted(song_count.items(), key=lambda x: x[1], reverse=True)
max_artist_count = [item[0] for item in sorted_items[:5]]


for artist in max_artist_count:
    new_artists=new_artists+session.artist_related_artists(artist_id=session.search(q=artist,limit=1,type='artist')["artists"]['items'][0]['uri'])['artists']

for item in new_artists:
    artist=item['name']
    if not artist in playlist_artists:
        playlist_artists.add(artist)
        print(artist+"--------------")
        if artist not in user_reccomendations:
            user_reccomendations[artist]=(find_this_is_playlist(artist))
        different=True



artist_song_count[playlist_name]=song_count
with open("user_reccomendations.json", "w") as f:
        # convert dictionary to JSON and write to file
        json.dump(user_reccomendations, f,indent=4)

with open("artist_song_count.json","w") as f:
        json.dump(artist_song_count,f,indent=4)

all_recommended_songs=[]
for artist in playlist_artists:
    all_recommended_songs+=user_reccomendations[artist]


#all_recommended_songs = (list(itertools.chain.from_iterable(rec_dict.values())))

songs_ranked={}
songs_link={}
songs_metadata={}


i=0




if not (("~|EVIL~|"+playlist_name,)in database_names):
    audio_features_list=get_playlist_audio_features(all_recommended_songs)
    for item in all_recommended_songs:
        track=item["track"]
        if track==None:
            continue
        similarity_score=get_track_similarity(playlist_name,track["uri"],track,audio_features_list[i])
        if similarity_score>=75 and not (track['name']+" by "+track['artists'][0]["name"] in songs_ranked) and not in_playlist(track):
            songs_ranked[track['name']+" by "+track['artists'][0]["name"]]=similarity_score
            songs_link[track['name']+" by "+track['artists'][0]["name"]]=track["external_urls"]['spotify']
            songs_metadata[track['name']+" by "+track['artists'][0]["name"]]=item
        i+=1
    song_queue=sorted(songs_ranked, key=songs_ranked.get, reverse=True)
else:
    evil_playlist=create_dataframe_from_sql("~|EVIL~|"+playlist_name)
    track_number=[]
    track=[]
    artist=[]
    album=[]
    year=[]
    explicit=[]
    duration=[]
    popularity=[]
    acousticness=[]
    energy=[]
    instrumentalness=[]
    liveness=[]
    loudness=[]
    speechiness=[]
    tempo=[]
    valence=[]
    danceability=[]
    uris=[]
    liked=[]
    n=0
    m=1
    audio_features_list=get_playlist_audio_features(all_recommended_songs)
    count=0
    temp=all_recommended_songs
    for item in temp:
        n+=1
        track_uri=item["track"]["uri"]
        audio_features=audio_features_list[count]
        if("spotify:local" in track_uri) or audio_features is None: #used to ignore local tracks (format is spotify:local:<track name>)
            all_recommended_songs.remove(item)
            continue
        count+=1
        track_number.append(n)
        track.append(item["track"]["name"])
        artist.append("|".join([artist["name"] for artist in item["track"]["artists"]]))
        album.append(item["track"]["album"]["name"])
        year.append((int(item["track"]["album"]['release_date'][0:4])))
        if item["track"]['explicit']:
            explicit.append(1)
        else:
            explicit.append(0)
        duration.append(audio_features["duration_ms"])
        popularity.append(item["track"]["popularity"])
        acousticness.append(audio_features["acousticness"])
        energy.append(audio_features["energy"])
        instrumentalness.append(audio_features["instrumentalness"])
        liveness.append(audio_features["liveness"])
        loudness.append(audio_features["loudness"])
        speechiness.append(audio_features["speechiness"])
        tempo.append(audio_features["tempo"])
        valence.append(audio_features["valence"])
        danceability.append(audio_features["danceability"])
        uris.append(track_uri)
        liked.append(1)
    data={"track number":track_number,"track":track,"artist":artist,"album":album,"release_date":year,"explicit":explicit,"duration":duration,"popularity":popularity,"acousticness":acousticness,"energy":energy,"instrumentalness":instrumentalness,"liveness":liveness,"loudness":loudness,"speechiness":speechiness,"tempo":tempo,"valence":valence,"danceability":danceability,"uri":uris,"liked":liked}
    potential_songs=pd.DataFrame(data)
    user_feedback=pd.concat([dataframe,evil_playlist])
    score_list=predict_likeability(user_feedback,potential_songs)
    for song, score in zip(all_recommended_songs, score_list):
        song_name = song["track"]['name']
        artist_name = song["track"]['artists'][0]["name"]
        if score>=.75 and not (song_name + " by " + artist_name in songs_ranked) and not in_playlist(song["track"]) and not in_evil_playlist(song["track"]):
            songs_ranked[song_name + " by " + artist_name] = score
            songs_link[song_name + " by " + artist_name]=song["track"]["external_urls"]['spotify']
            songs_metadata[song_name + " by " + artist_name]=song
    song_queue=sorted(songs_ranked, key=songs_ranked.get, reverse=True)
    random.shuffle(song_queue)
    print(str(len(song_queue))+" songs found!")




print("Took "+str(time.time()-t)+" seconds to run.")
