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
import requests
import json



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
currentdata = ''

sp_oauth = oauth2.SpotifyOAuth(client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri,scope=scope)
token_info = sp_oauth.get_cached_token()

if not token_info:
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    response = input('Paste the above link into your browser, then paste the redirect url here: ')

    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code)

    token = token_info['access_token']

if token:
    sp = spotipy.Spotify(auth=token)
    # for other channels you need to change the deepLinkId. This example code is for BPM which is channel 51.
    url = 'http://player.siriusxm.com/rest/v2/experience/modules/get/deeplink?deepLinkId=BPM&deepLink-type=live' 
    while(True):
        try:
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req)
            respData = resp.read().decode("utf-8")
            respJSON = json.loads(respData)


            track = respJSON['ModuleListResponse']['moduleList']['modules'][0]['moduleResponse']['moduleDetails']['liveChannelResponse']['liveChannelResponses'][0]['markerLists'][0]['markers'][0]['cut']['title']
            artist = respJSON['ModuleListResponse']['moduleList']['modules'][0]['moduleResponse']['moduleDetails']['liveChannelResponse']['liveChannelResponses'][0]['markerLists'][0]['markers'][0]['cut']['artists'][0]['name']
            artist.replace('/', ' ')

            print(artist, track)
            results = sp.search(q='artist:' + artist.replace('/', ' ') + " track:" + track, type='track')
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




        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            if sp_oauth.is_token_expired(token_info):
                token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
                token = token_info['access_token']
                sp = spotipy.Spotify(auth=token)
        
        # check again after a minute.
        time.sleep(60)

else:
    print ("Can't get token for", username)
