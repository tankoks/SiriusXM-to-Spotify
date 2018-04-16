import sys
import spotipy
import spotipy.util as util
import os
import urllib.request
import re
from json.decoder import JSONDecodeError
import time
import datetime



client_id="YOUR CLIENT ID"
client_secret="YOUR CLIENT SECRET"
redirect_uri="YOUR REDIRECT URI"
username = 'YOUR USERNAME'
scope = 'playlist-modify-public'
playlist_id= 'YOUR PLAYLIST ID'
track_id = ['']


try:
    token = util.prompt_for_user_token(username,scope,client_id,client_secret,redirect_uri)
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username,scope,client_id,client_secret,redirect_uri)


if token:
    sp = spotipy.Spotify(auth=token)
    url = 'http://www.dogstarradio.com/channelrss/51.txt' #change 51 to your prefered channel
    while(True):

        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req)
        respData = resp.read().decode("utf-8")
        dataArray = respData.split("\n")
        artist = dataArray[3].split("/")
        results = sp.search(q='artist:' + artist[0] + " track:" + dataArray[4], type='track')
        try:
            track_id[0] = results['tracks']['items'][0]['id']
            sp.user_playlist_remove_all_occurrences_of_tracks(username, playlist_id, track_id, snapshot_id=None)
            sp.user_playlist_add_tracks(username, playlist_id, track_id)
        except:
            pass
            print("failed")



        #delete old songs
        activePlaylist = sp.user_playlist(username, playlist_id)
        for track in activePlaylist['tracks']['items']:
            dateAdded = datetime.datetime.strptime(track["added_at"], '%Y-%m-%dt%H:%M:%SZ')
            if (datetime.datetime.utcnow() - dateAdded).days > 7:
                sp.user_playlist_remove_all_occurrences_of_tracks(username, playlist_id, [track['track']['id']], snapshot_id=None)


        time.sleep(60)


else:
    print ("Can't get token for", username)
