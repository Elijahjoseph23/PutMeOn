import time
from get_songs import song_queue,songs_link,songs_metadata
from init import add_song_to_playlist,play_song,get_currently_playing_duration,pause,disable_repeat,add_to_queue,enable_repeat,create_evil_playlist_sql,session,is_playing,change_playback,get_currently_playing_name
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import urllib.request
from PIL import Image
import tkinter as tk
from tkinter import PhotoImage
import os
from PIL import ImageTk
global opinion
opinion=0

def show_current_song_cover():
    def like_song():
        global opinion
        opinion=1
        window.destroy()

    def dislike_song():
        global opinion
        opinion=0
        window.destroy()

    def on_window_close():
        global opinion
        opinion=-1
        window.destroy()
        
    # Set up Spotipy client credentials
    load_dotenv(".env")
    CLIENT_ID = os.getenv("CLIENT_ID", "")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
    PLAYLIST_LINK = "https://open.spotify.com/playlist/5RPzjBiegJ44eGqXHiUSXw?si=f602501386474153"


    current_playback = session.current_playback()

    photo_image=None
    # Check if the user is currently playing a track and has an active device
    if current_playback is not None and 'item' in current_playback:
        track = current_playback['item']
        album = track['album']
        album_cover_url = album['images'][0]['url']  # Get the URL of the album cover (in this example, using the first available image)

                # Specify the path to the image file
        image_path = '/Users/eli/Projects/Spotify ML/album_cover.png'
        urllib.request.urlretrieve(album_cover_url, image_path)
        
        # Create a Tkinter window
        window = tk.Tk(className="~CURRENTLY PLAYING~")

        window.protocol("WM_DELETE_WINDOW", on_window_close)

        # Get the song name and artist
        song_name = track['name']
        artists = track['artists']
        artist_names = [artist['name'] for artist in artists]

        # Create a Tkinter label and display the image
        label = tk.Label(window, image=photo_image)
        label.pack()
        # Open the image using PIL's Image module
        pil_image = Image.open(image_path)
        pil_image = Image.open(image_path)

        # Resize the image to your desired dimensions
        resized_image = pil_image.resize((300, 300))  # Adjust the dimensions as needed

        # Convert the resized PIL image to a PhotoImage object
        photo_image = ImageTk.PhotoImage(resized_image)

        # Create a Tkinter label and display the image
        label = tk.Label(window, image=photo_image)
        label.pack(side="top")

        # Create a Tkinter label for the song name
        song_label = tk.Label(window, text=song_name)
        song_label.pack(side="top")

        # Create a Tkinter label for the artist
        artist_label = tk.Label(window, text=', '.join(artist_names))
        artist_label.pack(side="top")

        #Creates Tkinter buttons
        button_frame = tk.Frame(window)

        like_button = tk.Button(button_frame, text="👍", command=like_song)
        like_button.pack(side="left")

        pause_button=tk.Button(button_frame, text="⏯️", command=change_playback)
        pause_button.pack(side="left")

        dislike_button = tk.Button(button_frame, text="👎", command=dislike_song)
        dislike_button.pack(side="left")

        button_frame.pack(side="top")

        exit_button = tk.Button(window, text="❌", command=on_window_close)
        exit_button.pack(side="bottom")

        # Run the Tkinter event loop
        window.mainloop()
    else:
        print("No active device or playback information available.")


# Gets the client IDs from the environment file
played_once=True

disliked_songs=[]
while opinion!=-1:
    print()
    print("------------------------------------")
    if len(song_queue)==0:
        print("No more songs to recommend! Add more artists to your playlist for more!")
        break
        
    name=get_currently_playing_name()
    if name is None or song_queue[0].split(" by ")[0]!=name:
        song_queue.pop(0)
        continue
        
    song_uri=songs_metadata[song_queue[0]]["track"]["uri"]
    play_song(song_uri)
    
    print(song_queue[0])
    print("Thoughts on this song? \n ▢ Add the song to my playlist \n ▢ I don't like this song \n ▢ Exit the program \n")
    
    show_current_song_cover()
    if opinion==1:
        print("1")
        add_song_to_playlist(song_uri)
        print("Song added!")
        song_queue.pop(0)
        
    if opinion==0:
        print("0")
        played_once=True
        disliked_songs.append(songs_metadata[song_queue[0]])
        song_queue.pop(0)

create_evil_playlist_sql(disliked_songs)
pause()


