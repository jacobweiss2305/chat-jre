import requests
from requests.exceptions import HTTPError
import os

def get_access_token(client_id, client_secret):
    # Authenticate and get an access token
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_response.raise_for_status()
    access_token = auth_response.json()['access_token']
    return access_token


def fetch_show_episodes(show_id, access_token):
    # Retrieve episodes
    # Paginate episodes
    offset = 0
    limit = 20
    all_episodes = []

    while True:
        episodes_url = f'https://api.spotify.com/v1/shows/{show_id}/episodes?offset={offset}&limit={limit}'
        episodes_response = requests.get(episodes_url, headers={'Authorization': f'Bearer {access_token}'})
        episodes_response.raise_for_status()
        episodes = episodes_response.json()['items']
        all_episodes.extend(episodes)

        if len(episodes) < limit:
            break

        offset += limit

    # Flatten the JSON object
    flattened_episodes = []
    for episode in all_episodes:
        flattened_episode = {
            'name': episode['name'],
            'description': episode['description'],
            'release_date': episode['release_date'],
            'audio_preview_url': episode['audio_preview_url'],
            'external_urls': episode['external_urls']['spotify']
        }
        flattened_episodes.append(flattened_episode)

    return flattened_episodes