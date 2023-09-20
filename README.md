# YouTube Video Summarizer

A Flask application that leverages OpenAI's APIs to transcribe and summarize YouTube videos.

## Features

- **Video Downloading**: Downloads a YouTube video's best audio stream and extracts it as a WAV file using yt-dlp.
- **Audio Transcription**: Transcribes the audio file using OpenAI's Whisper ASR API.
- **Text Summarization**: Summarizes the transcription using OpenAI's GPT model.
- **Token Calculation**: Calculates the number of tokens in the transcription text using Tiktoken.

## Requirements

- Python 3.8 or later
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [OpenAI Python](https://github.com/openai/openai-python)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Tiktoken](https://github.com/openai/tiktoken)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

## Setup

1. **Clone the Repository**

    ```sh
    git clone https://github.com/yourusername/your-repo-name.git
    cd your-repo-name
    ```

2. **Set Up a Virtual Environment**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install Dependencies**

    ```sh
    pip install -r requirements.txt
    ```

4. **Setup Environment Variables**

   Copy `.env.template` to a new file named `.env` and fill in your actual values.

    ```sh
    cp .env.template .env
    ```

5. **Run the Application**

    ```sh
    flask run
    ```

   The application will be running on [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Usage

1. Open a web browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).
2. Paste a YouTube URL into the input field and click "Submit".
3. The application will download the video's audio, transcribe it, and then summarize the transcription. The summary will be displayed on the web page, along with the number of tokens in the transcription.

## License

This project is open-sourced under the [MIT License](LICENSE).