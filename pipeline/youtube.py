from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
from pytube import YouTube
from moviepy.editor import VideoFileClip
from openai import OpenAI
import os
import sys
import logging
from tqdm import tqdm

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

load_dotenv()

client = OpenAI()

# Replace the following variables with your values
api_key = os.getenv('YOUTUBE_API_KEY')

youtube = build('youtube', 'v3', developerKey=api_key)

def download_video(url, target_path="."):
    yt = YouTube(url)
    video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    filename = video_stream.default_filename
    video_stream.download(output_path=target_path, filename=filename)
    return f"{target_path}/{filename}"

def extract_audio(video_path, target_path="."):
    video_clip = VideoFileClip(video_path)
    audio_filename = f"{video_path}_audio.mp4_audio.mp3"
    video_clip.audio.write_audiofile(f"{target_path}/{audio_filename}")
    # close video file
    video_clip.close()
    # remove video file
    os.remove(video_path)
    return f"{target_path}/{audio_filename}"

def transcribe_audio(audio_path):
    # open audio file
    with open(audio_path, "rb") as file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            # the prompt option is only for hot fixing the model for acronyms
            file=file,
        )
    
    # close file
    file.close()

    # remove audio file
    os.remove(audio_path)

    return transcript.text
        
def get_channel_content(channel_id: str) -> dict:
    # e.g. channel_id = 'UCzQUP1qoWDoEbmsQxvdjxgQ'

    # Get the channel's content details
    channel_response = youtube.channels().list(id=channel_id, part='contentDetails').execute()

    return channel_response

def get_upload_playlist_id(channel_response: dict) -> str:
    # Extract the upload playlist ID
    upload_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    return upload_playlist_id

def list_videos_from_playlist(upload_playlist_id: str) -> list:
    # List videos from the upload playlist
    videos = []
    next_page_token = None
    while True:
        playlist_response = youtube.playlistItems().list(
            playlistId=upload_playlist_id,
            part='snippet',
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in playlist_response['items']:
            video_details = {
                'videoId': item['snippet']['resourceId']['videoId'],
                'title': item['snippet']['title'],
                'uploadDate': item['snippet']['publishedAt'],
                'channelId': item['snippet']['channelId'],
                'description': item['snippet']['description'],
                'channelTitle': item['snippet']['channelTitle'],
            }
            videos.append(video_details)

        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    return videos