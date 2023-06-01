Name: 
-----------------------------------------
PutMeOn


Author:
-----------------------------------------
@Elijahjoseph23


Description: 
-----------------------------------------
Wanna add more music to your spotify playlist? This program gives you
a constant stream of music that you can automatically listen to as well as add to your playlist. 
The more you use it, the better it gets!


Needed Packages:          Version:
-----------------------------------------
-spotipy                  2.23
-urllib3                  1.26.13
-Pillow                   9.3.0
-SQLAlchemy               1.4.45
-sqlparse                 0.4.3
-numpy                    1.24.0
-pandas                   1.5.2
-sklearn                  0.0.post1
-scipy                    1.10.1
-scikit-learn             1.2.2


Instructions:
-----------------------------------------
- create a spotify app (https://developer.spotify.com/documentation/web-api/tutorials/getting-started)

- find your project's Client ID and Client Secret

- create a .env file with the following text:
CLIENT_ID="<YOUR CLIENT ID HERE>"
CLIENT_SECRET="<YOUR CLIENT SECRET HERE>"

- when running the program, make sure your queue is cleared as well as that a song is playing before running. If there
is no active device, the program will not work

- run the Main.py file, allow the permissions on the link it forwards you too

- enter the name of the playlist you want to add more songs to (make sure to type it exactly how it appears on Spotify)

- here's what each button does:
    - 👍 (thumbs up button): adds the song to your playlist, then skips the song
    - ⏯️ (pause/play button): pauses/plays the song
    - 👎 (thumbs down button): skips the song, adds it to a list of songs you don't like so that the program can make more accurate predictions
    - ❌ (X button): exits the program

- WHEN FINISHED, ALWAYS CLOSE OUT THE PROGRAM USING THE ❌ (X) BUTTON. The way this program works is that it locally stores 
the songs you dislike in order for the program to more accurately predict what songs you like

Contact:
-----------------------------------------
if you find a bug or have a suggestion, you can email elijahsjoseph23@gmail.com

Happy Listening!





