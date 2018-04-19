import sys
import spotipy
import spotipy.util as util
import spotipy.oauth2 as oauth2
import os
import urllib.request
import re
from json.decoder import JSONDecodeError
import time
import datetime


#EDIT THESE
client_id="YOUR CLIENT ID"
client_secret="YOUR CLIENT SECRET"
redirect_uri="YOUR REDIRECT URI"
username = 'YOUR USERNAME'
playlist_id= 'YOUR PLAYLIST ID'

#Don't edit these
scope = 'playlist-modify-public'
track_id = ['']
token = 'this is a temp token'

def setup(username, scope=None, client_id = None, client_secret = None, redirect_uri = None):
    sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope)
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        print('''
            User authentication requires interaction with your
            web browser. Once you enter your credentials and
            give authorization, you will be redirected to
            a url.  Paste that url you were directed to to
            complete the authorization.
        ''')
        auth_url = sp_oauth.get_authorize_url()
        try:
            import webbrowser
            webbrowser.open(auth_url)
            print("Opened %s in your browser" % auth_url)
        except:
            print("Please navigate here: %s" % auth_url)

        print()
        print()
        try:
            response = raw_input("Enter the URL you were redirected to: ")
        except NameError:
            response = input("Enter the URL you were redirected to: ")

        print()
        print()

        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)
    # Auth'ed API request
    if token_info:
        global token
        token = token_info
        return sp_oauth
    else:
        return None


try:
    spoauth = setup(username, scope, client_id, client_secret, redirect_uri)
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{username}")
    spoauth = setup(username, scope, client_id, client_secret, redirect_uri)


if token:
    sp = spotipy.Spotify(auth=token['access_token'])
    url = 'http://www.dogstarradio.com/channelrss/51.txt' #change 51 to the channel to be watched.
    while(True):
        try:
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

        except:
            token = spoauth.refresh_access_token(token['refresh_token'])
            sp = spotipy.Spotify(auth=token['access_token'])


else:
    print ("Can't get token for", username)
