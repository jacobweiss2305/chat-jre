import spotify
import youtube
import pinecone
import vectordb
import pytube
import os
import sys
import logging
from tqdm import tqdm

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

def main():

    # Youtube
    channel_id = 'UCzQUP1qoWDoEbmsQxvdjxgQ'
    channel_content = youtube.get_channel_content(channel_id)
    upload_playlist_id = youtube.get_upload_playlist_id(channel_content)
    videos = youtube.list_videos_from_playlist(upload_playlist_id)

    # Pinecone
    index_name = os.getenv('PINECONE_INDEX')
    if not vectordb.check_index_exists(index_name):
        vectordb.create_index(index_name)
        
    # Upload videos to Pinecone
    namespace  = "youtube"
    for video in tqdm(videos[17:]):
        
            # Raises AgeRestrictedError
        download_path = youtube.download_video(f"https://www.youtube.com/watch?v={video['videoId']}")

        
        audio_path = youtube.extract_audio(download_path)
        transcript = youtube.transcribe_audio(audio_path)
        embedding = vectordb.get_openai_embedding(transcript)
        video['text'] = transcript

        vectordb.upload_pinecone(index_name, embedding, video, namespace)

    # Spotify
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    access_token = spotify.get_access_token(client_id, client_secret)
    show_id = "4rOoJ6Egrf8K2IrywzwOMk"
    namespace = "spotify"

    episodes = spotify.fetch_show_episodes(show_id, access_token)
    for episode in episodes:
        embedding = vectordb.get_openai_embedding(episode['description'])
        episode['text'] = episode['description']
        vectordb.upload_pinecone(index_name, embedding, episode, namespace)
        logging.info(f"Uploaded {episode['name']} to Pinecone")

if __name__ == "__main__":

    main()