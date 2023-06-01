
import numpy as np
import pandas as pd
import spotipy
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from scipy.stats import norm
import math
import sqlite3
from init import playlist_name
#gets the client ids from the env file
load_dotenv(".env")
CLIENT_ID=os.getenv("CLIENT_ID","")
CLIENT_SECRET=os.getenv("CLIENT_SECRET","")


# authenticates session
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
#creates spotify session
session=spotipy.Spotify(client_credentials_manager=client_credentials_manager,requests_timeout=10,retries=10)

conn = sqlite3.connect('playlist_data.db')
playlist_data=pd.read_sql_query("SELECT * FROM "+"'"+playlist_name+"'", conn)
track_features=["release_date","explicit","duration","popularity","acousticness","energy","instrumentalness","liveness","loudness","speechiness","tempo","danceability"]
for feature in track_features:
    playlist_data[feature] = playlist_data[feature].astype(float)
conn.close()



def find_sim_score(x,mean, std):
    distance = abs(x - mean)
    max_distance = 3 * std  
    if distance >= max_distance:
        return 0  
    
    normalized_distance = distance / max_distance
    score = (1 - normalized_distance) * 100
    if math.isnan(score):
        return 0
    return int(score)

def get_track_similarity(playlist_name,uri,single,audio_features):
    sum=0
    if audio_features is None:
        return 0
    for feature in track_features:
        if feature=="popularity" or feature=="explicit":
            sum+=find_sim_score(single[feature],playlist_data[feature].mean(),playlist_data[feature].std())
        elif feature=="release_date":
            if(single["album"]["release_date"] is None):
                return 0
            sum+=find_sim_score(float(single["album"]["release_date"][0:4]),playlist_data["release_date"].mean(),playlist_data["release_date"].std())
        elif feature=="duration":
            sum+=find_sim_score(audio_features["duration_ms"],playlist_data["duration"].mean(),playlist_data["duration"].std())
        else:
            if feature!='explicit' and audio_features[feature] is None:
                return 0
            sum+=find_sim_score(audio_features[feature],playlist_data[feature].mean(),playlist_data[feature].std())
    similarity_score=sum/len(track_features)
    return similarity_score
    

