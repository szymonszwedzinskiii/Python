import requests
import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth


from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build


## Array with special chars and keyworlds to delete from title
IGNORE = ['(', '[', ' x', ')', ']', '&', 'lyrics', 'lyric',
          'video', '/', ' proximity', ' ft', '.', ' edit', ' feat', ' vs', ',','-','official music','official music video','official','cała płyta','2000','2001','2002','2003',
          '2004','2005','2006','2007','2008','2009','2010','2011','2012','2013',
          '2014','2015','2016','2017','2018','2019','2020','2021']


##Spotify constant value
SCOPE = 'playlist-modify-private'

##youtube constant values
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "MyClientSecret.json"



##End of constant values

def GetSpotifyAcc():
    listOfVarriables = []
    try:
        g = open('ApiData.txt')
        with g:
            temp = g.read()
            listOfVarriables = temp.split('\n')
    except OSError:
        temp = input("Proszę podać Spotify Client Id: ")
        temp1 = input("Proszę podać spotify Client Secret: ")
        temp2 = input("Proszę podać spotify redirect URI: ")
        temp3 = input("Proszę podać username: ")
        listOfVarriables.append(temp)
        listOfVarriables.append(temp1)
        listOfVarriables.append(temp2)
        listOfVarriables.append(temp3)
    return listOfVarriables


def MakeSpotifyObject(clientid, clientsecret, uri):
    token = SpotifyOAuth(client_id=clientid, client_secret=clientsecret, redirect_uri=uri, scope=SCOPE)
    spotifyObject = spotipy.Spotify(auth_manager = token)
    return spotifyObject



def ConnectToYoutube():
    developer_key =input("Type a developer key from youtube api: ")
    service = build(serviceName=api_service_name, version=api_version, developerKey=developer_key)
    return service

def FindThePLaylist(YtService):
    chanelId = input("Type a Channel ID of youtube channel:")
    request = YtService.playlists().list(
        part="snippet,contentDetails",
        channelId=chanelId,
        maxResults=25
    )
    response = request.execute()
    playlistName = input("Podaj nazwę playlisty: ")
    j = 0
    for item in response:
        if response['items'][j]['snippet']['title'] == playlistName and j < len(response):
            responseItem = response['items'][j]
        else:
            j = j + 1
    iD = responseItem['id']
    return iD


def DownloadPlaylistItems(playlist, playid):
    playlistelements = playlist.playlistItems().list(
        part='snippet,contentDetails',
        playlistId=playid,
        maxResults=500
    )
    responsePlaylist = playlistelements.execute()
    list=[]

    for item in responsePlaylist['items']:
        list.append(item['snippet']['title'])
    validtitles = ValidTitles(list)
    return validtitles


def ValidTitles(invalidPLaylist):
    validList = []
    for item in invalidPLaylist:
        title = item.lower()
        for ch in IGNORE:
            if ch in title:
                title = title.replace(ch, ' ')
        validList.append(title)
    return validList


def SearchForItems(titles,object):
    notfound = []
    elements = []
    for item in titles:
        elementId = object.search(q=item,limit=1,type='track')
        if elementId['tracks']['total'] ==0:
            print(f'Nie znaleziono utworu: {item}')
            notfounf.append(item)
        else:
            print(f'Szukanie utworu: {item}')
            elements.append(elementId['tracks']['items'][0]['uri'])
    return elements

def MakeAddItemsToPlaylist(elements,spotifyObject, clientId, clientSecret, redirect_uri, username ):
    playlist_name = input("Podaj nazwę playlisty: ")
    public_description = input("Podaj opis playlisty: ")
    spotifyObject.user_playlist_create(user=username, name=playlist_name, public=False, collaborative=False,
                                       description=public_description)

    token2 = SpotifyOAuth(client_id=clientId, client_secret=clientSecret,
                          redirect_uri=redirect_uri, scope='playlist-read-private')

    getAPlaylist = spotipy.Spotify(auth_manager=token2)

    listOfPlaylists = getAPlaylist.current_user_playlists()

    ourPlaylist = listOfPlaylists['items'][0]['id']
    spotifyObject.playlist_add_items(playlist_id=ourPlaylist, items=elements)


def main():
    SpotifyAccessList= GetSpotifyAcc()

    SPOTIPY_CLIENT_ID =SpotifyAccessList[0]
    SPOTIPY_CLIENT_SECRET = SpotifyAccessList[1]
    SPOTIPY_REDIRECT_URI=SpotifyAccessList[2]
    username=SpotifyAccessList[3]

    spotifyObject = MakeSpotifyObject(clientid=SPOTIPY_CLIENT_ID, clientsecret=SPOTIPY_CLIENT_SECRET, uri=SPOTIPY_REDIRECT_URI)

    youtubeObject = ConnectToYoutube()

    playlistID = FindThePLaylist(youtubeObject)
    titles = DownloadPlaylistItems(youtubeObject, playlistID)

    listOfElements = SearchForItems(titles, spotifyObject)
    MakeAddItemsToPlaylist(listOfElements, spotifyObject,SPOTIPY_CLIENT_ID,SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,
                           username)


if __name__ == "__main__":
    main()
