import os
import pickle
import os.path as path

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube"]
credentials = ""
youtube = ""


def init():
    global credentials, youtube
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"
    if path.exists(path.join(os.getcwd(), "cache")):
        f = open("cache", "rb")
        credentials = pickle.load(f)
        f.close()
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        f = open("cache", "wb")
        pickle.dump(credentials, f)
        f.close()

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)


def get_playlists():
    playlist = {}
    token = ""
    while True:
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            maxResults=50,
            mine=True,
            pageToken=token
        )

        resp = request.execute()
        for i in resp["items"]:
            playlist[i["snippet"]["title"]] = i["id"]
        if "nextPageToken" not in resp.keys():
            break
        else:
            token = resp["nextPageToken"]
    return playlist


def get_music_videos():
    id = []
    token = ""
    while True:
        request = youtube.videos().list(
            part="snippet",
            myRating="like",
            pageToken=token,
            maxResults=50
        )
        resp = request.execute()
        for i in resp["items"]:
            id.append((i["id"], i["snippet"]["categoryId"]))
        if "nextPageToken" not in resp.keys():
            break
        else:
            token = resp["nextPageToken"]

    id_music = []
    for i in id:
        if i[1] == '10':
            id_music.append(i[0])
    return id_music


def add_video_to_playlist(playlist, video):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist,
                "position": 0,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video
                }
            }
        }
    )
    resp = request.execute()
    return resp


def get_playlist_items(playlist_id):
    token = ""
    id = []
    while True:
        request = youtube.playlistItems().list(
            part="id",
            maxResults=50,
            playlistId=playlist_id,
            pageToken=token
        )
        resp = request.execute()
        for i in resp["items"]:
            id.append(i["id"])
        if "nextPageToken" not in resp.keys():
            break
        else:
            token = resp["nextPageToken"]
    return id


def update_music_playlist():
    playlists = get_playlists()
    music_playlist = []
    id = []
    if "Music" not in playlists.keys():
        request = youtube.playlists().insert(
            part="snippet",
            body={
                "snippet": {
                    "title": "Music"
                }
            }
        )
        response = request.execute()
        id.extend(response["id"])
    else:
        id = playlists["Music"]
        music_playlist.extend(get_playlist_items(id))
    for i in get_music_videos():
        if i not in music_playlist:
            add_video_to_playlist(id, i)


if __name__ == "__main__":
    init()
    update_music_playlist()
