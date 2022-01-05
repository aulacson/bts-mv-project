import os
import json
import numpy as np
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "yt_client_secret_file.json"

# Get credentials and create an API client
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

# define youtube API functions
def get_videos_from_playlist(playlist_id):

    request = youtube.playlistItems().list(
        part = "snippet,contentDetails",
        maxResults = 300,
        playlistId = playlist_id
    )
    response = request.execute()

    page = 1
    print(f'Processed Page {page}')

    try:
        next_page_token = response['nextPageToken']
    except: 
        next_page_token = 0

    while next_page_token:
        next_page_request = youtube.playlistItems().list(
                part = "snippet,contentDetails",
                maxResults = 300,
                pageToken = next_page_token,
                playlistId = playlist_id
            )

        next_page_response = next_page_request.execute()

        response['items'].extend(next_page_response['items'])

        page += 1
        print(f'Processed Page {page}')

        try:
            next_page_token = next_page_response['nextPageToken']
        except: 
            next_page_token = 0

    return response

def get_video_details(videoId):
    raw_official_mv_items = {'items':[]}

    for video_list in videoId:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_list,
            maxResults=100
        )
        response = request.execute()
        raw_official_mv_items['items'].extend(response['items'])

    with open('bts_official_mv_items.json', 'w') as json_file:
        json.dump(raw_official_mv_items, json_file)

    number_of_mvs = len(raw_official_mv_items['items'])
    
    print(f'Retrieved {number_of_mvs} Official Music Videos')

# Set playlist ID
playlist_id = "PL_Cqw69_m_yz4JcOfmZb2IDWwIuej1xfN"

# Get videos in youtube playlist
playlist_items = get_videos_from_playlist(playlist_id)

# Get video IDs of the official BTS MVs
official_mvs_videoId = []
for item in playlist_items['items']:
    title = item['snippet']['title']
    videoId = item['contentDetails']['videoId']
    if "Official MV" in title:
        official_mvs_videoId.append(videoId)

# When calling youtube API for video list, there is a max limit of 50

if len(official_mvs_videoId) > 50:
    official__mvs_videoId_list = []
    number_of_loops = int(np.ceil(len(official_mvs_videoId)/50))

    for i in range(0, number_of_loops):
        if i == number_of_loops -1:
            official__mvs_videoId_list.append(','.join(official_mvs_videoId[(i*50):len(official_mvs_videoId)]))
        else:
            official__mvs_videoId_list.append(','.join(official_mvs_videoId[(i*50):((i+1)*50)]))     
else:
    official__mvs_videoId_list = [','.join(official_mvs_videoId)]

get_video_details(official__mvs_videoId_list)