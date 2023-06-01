import os
import sqlite3
import time
import pandas as pd
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

# Gets the client IDs from the environment file
load_dotenv(".env")
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
PLAYLIST_LINK = "https://open.spotify.com/playlist/5RPzjBiegJ44eGqXHiUSXw?si=f602501386474153"

# Set up authentication and create an instance of the Spotipy API client
scope = "playlist-modify-public playlist-modify-private playlist-read-private user-modify-playback-state user-read-playback-state streaming"
redirect_uri = "http://localhost:8888/callback"  # Placeholder redirect URI
auth_manager = SpotifyOAuth(scope=scope, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=redirect_uri)
session = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=10, retries=10)

# Retrieve and print all playlists for the current user
playlists = []
offset = 0
limit = 50

playlist_name = input("Type the playlist you would like to select: ")
uri = ""
check = True
found = False
while check:
    try:
        results = session.current_user_playlists(limit=limit, offset=offset)
    except SpotifyException as e:
        if e.http_status == 429:
            print("Too many requests, retrying after 10 seconds...")
            time.sleep(10)
            continue
        else:
            raise e
    offset += limit
    if len(results['items']) < limit:
        for playlist in results["items"]:
            if playlist["name"] == playlist_name:
                print("Playlist found!")
                uri = playlist["uri"]
                found = True
                break
        if not found:
            print("Playlist not found!")
        break
    else:
        for playlist in results["items"]:
            if playlist["name"] == playlist_name:
                print("Playlist found!")
                uri = playlist["uri"]
                found = True
                break
        if found:
            break

if not found:
    exit()







def get_playlist_tracks(uri):
    results = session.playlist_tracks(uri)
    tracks = results['items']
    while results['next']:
        results = session.next(results)
        tracks.extend(results['items'])
    return tracks

def get_playlist_audio_features(tracks):
    uris=[]
    count=1
    audio_feature_list=[]
    skipped=0
    for track in tracks:
        if count>=101:
            audio_feature_list+=session.audio_features(uris)
            count=1
            uris=[]
        if track["track"] is None or "local" in track["track"]["uri"] or  "episode" in track["track"]["uri"]:
            skipped+=1
            continue
        uris.append(track["track"]["uri"])
        count+=1
    if uris:
        audio_feature_list += session.audio_features(uris)
    return audio_feature_list

def create_sql(tracks):
    start=time.time()
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
    print("Loading:")
    print("□"*10)
    audio_features_list=get_playlist_audio_features(tracks)
    count=0
    for item in tracks:
        if(n>=m/10*len(tracks)):
                print(("▧"*m)+("□"*(10-m)))
                m+=1
        n+=1
        track_uri=item["track"]["uri"]
        if("spotify:local" in track_uri): #used to ignore local tracks (format is spotify:local:<track name>)
            continue
        audio_features=audio_features_list[count]
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
    panda=pd.DataFrame(data)
    print(panda)

    end=time.time()
    print("▧"*10)
    print("Done!")
    print("Finished in "+str(end-start))
    return panda

def create_evil_playlist_sql(tracks):
    conn = sqlite3.connect('playlist_data.db')
    # Get the list of available database names in the .db file
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    database_names = cursor.fetchall()

    if ("~|EVIL~|"+playlist_name,) in database_names:
        original_df=create_dataframe_from_sql("~|EVIL~|"+playlist_name)
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
        audio_features_list=get_playlist_audio_features(tracks)
        n=0
        count=0
        for item in tracks:
            n+=1
            track_uri=item["track"]["uri"]
            if("spotify:local" in track_uri): #used to ignore local tracks (format is spotify:local:<track name>)
                continue
            audio_features=audio_features_list[count]
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
            liked.append(0)
        data={"track number":track_number,"track":track,"artist":artist,"album":album,"release_date":year,"explicit":explicit,"duration":duration,"popularity":popularity,"acousticness":acousticness,"energy":energy,"instrumentalness":instrumentalness,"liveness":liveness,"loudness":loudness,"speechiness":speechiness,"tempo":tempo,"valence":valence,"danceability":danceability,"uri":uris,"liked":liked}
        new_df=pd.DataFrame(data)
        combined_df=pd.concat([original_df,new_df])
        combined_df.to_sql("~|EVIL~|"+playlist_name, conn, if_exists='replace',index=False) 
    else:
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
        audio_features_list=get_playlist_audio_features(tracks)
        n=0
        count=0
        for item in tracks:
            n+=1
            track_uri=item["track"]["uri"]
            if("spotify:local" in track_uri): #used to ignore local tracks (format is spotify:local:<track name>)
                continue
            audio_features=audio_features_list[count]
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
            liked.append(0)
        data={"track number":track_number,"track":track,"artist":artist,"album":album,"release_date":year,"explicit":explicit,"duration":duration,"popularity":popularity,"acousticness":acousticness,"energy":energy,"instrumentalness":instrumentalness,"liveness":liveness,"loudness":loudness,"speechiness":speechiness,"tempo":tempo,"valence":valence,"danceability":danceability,"uri":uris,"liked":liked}
        new_df=pd.DataFrame(data)
        new_df.to_sql("~|EVIL~|"+playlist_name, conn, if_exists='replace')

    conn.commit
    conn.close

def create_dataframe_from_sql(playlist_name):
    conn = sqlite3.connect('playlist_data.db')
    playlist_data=pd.read_sql_query("SELECT * FROM '"+playlist_name+"'", conn)
    conn.close()
    return playlist_data

def add_track(uri):
    uri="0lYBSQXN6rCTvUZvg9S0lU" #let me love you by Justin Bieber
    conn=sqlite3.connect("playlist_data.db")
    single=session.track(uri)
    audio_features=session.audio_features(uri)[0]
    track_number= conn.execute(f"SELECT COUNT(*) FROM {playlist_name}").fetchone()[0]
    print(track_number)
    artists=", ".join([artist["name"] for artist in single["artists"]])
    track=([single["name"],artists,single["album"]["name"],audio_features["duration_ms"],single["popularity"],audio_features["acousticness"],audio_features["energy"],audio_features["instrumentalness"],audio_features["liveness"],audio_features["loudness"],audio_features["speechiness"],audio_features["tempo"],audio_features["valence"],audio_features["danceability"]])
    conn.execute("INSERT INTO '"+playlist_name+"' ('track number', track, artist, album, year, explicit, duration, popularity, acousticness, energy, instrumentalness, liveness, loudness, speechiness, tempo, valence, danceability,uri) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", track)
    conn.commit
    conn.close

def in_playlist(track):
    #dataframe=create_dataframe_from_sql(playlist_name)
    if track["uri"] in dataframe["uri"].values:
        return True
    potential_tracks = dataframe[dataframe["track"] == track["name"]]
    for index,row in potential_tracks.iterrows():
        if row["track"]==track["name"] and track["artists"][0]["name"]==row["artist"]:
            return True
    return False

def in_evil_playlist(track):
    dataframe=create_dataframe_from_sql("~|EVIL~|"+playlist_name)
    if track["uri"] in dataframe["uri"].values:
        return True
    potential_tracks = dataframe[dataframe["track"] == track["name"]]
    for index,row in potential_tracks.iterrows():
        if row["track"]==track["name"] and track["artists"][0]["name"]==row["artist"]:
            return True
    return False

def add_song_to_playlist(track_uri):
    session.playlist_add_items(playlist_id=uri,items=[track_uri])

def play_song(song_uri):
    session.add_to_queue(uri=song_uri)
    session.next_track()
    session.repeat(state="track")

def get_currently_playing_duration():
    return session.currently_playing()["item"]["duration_ms"]

def get_currently_playing_name():
    current=session.currently_playing()
    if current is None:
        return None
    return session.currently_playing()["item"]["name"]

def pause():
    session.pause_playback()

def disable_repeat():
    session.repeat(state="off")

def enable_repeat():
    session.repeat(state="track")

def add_to_queue(uri):
    session.add_to_queue(uri)

def is_playing():
    current_playback=session.currently_playing()
    if current_playback is not None:
        return session.currently_playing()["is_playing"]
    return False

def change_playback():
    playing=is_playing()
    if playing:
        session.pause_playback()
    else:
        session.start_playback()


'''def update_database(uri,playlist_name):
    tracks=get_playlist_tracks(uri)
    playlist_data=create_dataframe_from_sql(playlist_name)
    playlist_data.size
    tail_index=playlist_data.iloc[-1]["track number"]
    print(tail_index)
    count=1
    for track in tracks:
        if count>tail_index:
            add_track(track["track"]["uri"],playlist_name)
        count+=1'''





#takes 389.6 seconds to upload 3121 tracks (~8 tracks/s)

dataframe=create_sql(get_playlist_tracks(uri))




