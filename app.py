from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import openai
import yt_dlp
import tiktoken
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key and other OpenAI settings
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
system_message = os.getenv("SYSTEM_MESSAGE", "You are a helpful assistant that summarizes text from youtube videos. Ignore all mentions of Commenting, Subscribing, or any sort of sponsor spot.")

# Initialize the Tiktoken encoding for the specified OpenAI model
encoding = tiktoken.encoding_for_model(openai_model)

def delete_file(file_path):
    """Delete a file at the specified path.

    Args:
    file_path (str): The path to the file to delete.
    """
    try:
        os.remove(file_path)
        logging.info(f"Successfully deleted file at {file_path}")
    except Exception as e:
        logging.error(f"Failed to delete file at {file_path}. Error: {e}")

def download_video(youtube_url):
    """Download the best audio stream of a YouTube video and extract it as a WAV file.

    Args:
    youtube_url (str): The URL of the YouTube video to download.

    Returns:
    str: The safe title of the downloaded video, which can be used to construct the audio file path.
    """
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        video_title = info_dict.get('title', None)

    # Construct a safe file name by replacing non-alphanumeric characters with underscores
    safe_video_title = "".join([c if c.isalnum() or c.isspace() else "_" for c in video_title])

    # Define options for yt_dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'outtmpl': f'downloaded_videos/{safe_video_title}.%(ext)s',
        'quiet': True,
    }

    # Download and extract audio from the YouTube video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return safe_video_title

def transcribe_audio(audio_file_path):
    """Transcribe an audio file using the OpenAI Whisper ASR API.

    Args:
    audio_file_path (str): The path to the audio file to transcribe.

    Returns:
    str or None: The transcription text if successful, None otherwise.
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        text_transcript = transcript["text"]
        return text_transcript
    except Exception as e:
        logging.error(f"Failed to transcribe the audio file. Error: {e}")
        return None

def summarize_transcription(transcription):
    """Summarize a transcription text using OpenAI's model defined in .env.

    Args:
    transcription (str): The transcription text to summarize.

    Returns:
    str: The summary text.
    """
    if transcription:
        try:
            completion = openai.ChatCompletion.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Can you summarize the following text?\n\n{transcription}"}
                ]
            )
            return completion.choices[0].message['content']
        except Exception as e:
            logging.error(f"Failed to create a summary. Error: {e}")
            return 'Could not summarize the transcription due to an error.'
    else:
        return 'No transcription available to summarize.'

def num_tokens_from_string(string):
    """Calculate the number of tokens in a string using Tiktoken.

    Args:
    string (str): The string to calculate the number of tokens for.

    Returns:
    int: The number of tokens in the string.
    """
    return len(encoding.encode(string))

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle GET and POST requests to the home page.

    Returns:
    str: Rendered HTML template for the home page with populated summary data if available.
    """
    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        safe_video_title = download_video(youtube_url)
        
        if safe_video_title:
            audio_file_path = f'downloaded_videos/{safe_video_title}.mp3'
            transcription = transcribe_audio(audio_file_path)
            
            # Delete the audio file after transcribing
            delete_file(audio_file_path)
            
            if transcription:
                num_tokens = num_tokens_from_string(transcription)
                
                if num_tokens <= 7000:  
                    summary = summarize_transcription(transcription)
                else:
                    summary = 'The transcription is too long to be summarized.'
            else:
                num_tokens = 'No transcription available to check tokens.'
                summary = 'No transcription available to summarize.'
        else:
            num_tokens = 'Could not fetch the video title.'
            summary = 'Could not fetch the video title.'
        
        return render_template('index.html', youtube_url=youtube_url, num_tokens=num_tokens, summary=summary)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)
