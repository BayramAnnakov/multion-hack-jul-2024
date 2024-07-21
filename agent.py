
import dotenv

dotenv.load_dotenv()

from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool

from multion.client import MultiOn

from mem0 import Memory

import re

import requests
import requests_cache
import os
import csv
import json

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

import random

from datetime import datetime

from typing import Dict, Any, List

from youtube_transcript_api import YouTubeTranscriptApi

from llama_index.core.agent import ReActAgent

from elevenlabs.client import ElevenLabs
from elevenlabs import play

import yt_dlp

from pydub import AudioSegment

from llama_index.core import set_global_handler

set_global_handler("agentops", api_key=os.getenv("AGENTOPS_API_KEY"))

from suno import custom_generate_audio

from llama_index.llms.groq import Groq

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    ApplicationBuilder
)



elevenLabsClient = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
client = MultiOn(
    api_key=os.getenv("MULTION_API_KEY")
)

config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "host": "localhost",
                    "port": 6333,
                }
            },
        }

memoryStorage = Memory.from_config(config)

LLM_MODEL_TYPE = "gpt-4o"



def get_watch_later_videos(query: str) -> str:
    retrieve_response = client.retrieve(
    cmd="Retrieve top 3 videos from my Watch Later playlist",
        url="https://www.youtube.com/playlist?list=WL",
        fields=["title", "url"],
        local= True
    )

    data = retrieve_response.data

    return str(data)

def search_memories(query: str) -> str:
    """ Search relevant memories to use in the video summary"""
    memories = memoryStorage.search(query, user_id="Bayram")

    return memories


def generate_audio(text: str) -> str:
    """ Generate audio from text using ElevenLabs API and save it to a file """

    audio_generator = elevenLabsClient.generate(text=text, voice="Jessica", model="eleven_multilingual_v2")
    audio_bytes = b''.join(audio_generator)


    #save audio to file
    audio_file_path = "output_" + datetime.now().strftime("%Y%m%d%H%M%S")+ ".mp3"

    with open(audio_file_path, "wb") as file:
        file.write(audio_bytes)

    return audio_file_path

def get_youtube_transcript(video_id: str) -> str:
    """ Get the transcript of a youtube video """

    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    print(transcript)

    return transcript

def download_audio_segments(video_id:str, segments: List[Dict[str, Any]]) -> List[str]:
    """ Download audio segments from youtube video """

    audio_segments = []

    ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'output': video_id + '.m4a',
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }]
}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(["https://www.youtube.com/watch?v="+video_id])

        #find file with video_id
        downloaded_file = None
        for file in os.listdir():
            if file.endswith(f"[{video_id}].m4a"):
                downloaded_file = file
                break

        audio = AudioSegment.from_file(file, format="m4a")
        #extract audio segments
        
        i=0
        for segment in segments:
            start_time = segment["start_time"] * 1000
            end_time = (segment["end_time"] + 30) * 1000

            audio_segment = audio[start_time:end_time]

            i += 1
            audio_segment_path = f"{video_id}_segment_{i}.mp3"
            audio_segment.export(audio_segment_path, format="mp3")
        
            audio_segments.append(audio_segment_path)
    
    return audio_segments


def get_video_highlights(video_id: str) -> Dict[str, Any]:
    """ Get the timestamp of the top 3 highlights from a youtube video """

    url = "https://yt.lemnoslife.com/videos?part=mostReplayed&id=" + video_id

    response = requests.get(url).json()

    markers = response["items"][0]["mostReplayed"]["markers"]

    # #remove marker that starts at 0
    # markers = [marker for marker in markers if marker["startMillis"] != 0]

    sorted_markers = sorted(markers, key=lambda x: x["intensityScoreNormalized"], reverse=True)

    top_markers = sorted_markers[:10]

    return top_markers

def get_video_highlights_in_text(video_id: str) -> List[str]:
    """ Get the timestamp of the top 5 highlights from a youtube video """


    top_markers = get_video_highlights(video_id)

    transcript = get_youtube_transcript(video_id)

    highlights = []

    for marker in top_markers:
        start_time = marker["startMillis"]/1000
        end_time = start_time + 60
        
        highlight_text = ""

        for line in transcript:
            if line["start"] >= start_time and line["start"] <= end_time:
                highlight_text += line["text"] + " "

        highlights.append({
            "start_time": start_time,
            "end_time": end_time,
            "text": highlight_text
        })
       

    return highlights

def generate_song(prompt: str) -> str:
    """Generate a song with the given lyrics, style and title."""
    response = custom_generate_audio(prompt)

    audio_urls = [item['audio_url'] for item in response]

    #download audio to file
    audio_file_path = "podcast_intro.mp3"

    with open(audio_file_path, "wb") as file:
        file.write(requests.get(audio_urls[0]).content)


    return audio_file_path

def combine_audio_segments_and_summary(segments: List[str], summary_file:str, video_id:str) -> str:

    combined_audio = AudioSegment.empty()

    combined_audio += AudioSegment.from_file("podcast_intro.mp3", format="mp3")

    combined_audio += AudioSegment.from_file(summary_file, format="mp3")

    for segment in segments:
        audio = AudioSegment.from_file(segment, format="mp3")
        combined_audio += audio

    combined_audio_path = f"combined_audio_{video_id}.mp3"
    combined_audio.export(combined_audio_path, format="mp3")

    return combined_audio_path


def get_openai_agent():
    watch_later_videos_tool = FunctionTool.from_defaults(fn=get_watch_later_videos)
    video_highlights_tool = FunctionTool.from_defaults(fn=get_video_highlights_in_text)
    audio_generation_tool = FunctionTool.from_defaults(fn=generate_audio)
    download_audio_segments_tool = FunctionTool.from_defaults(fn=download_audio_segments)
    combine_audio_segments_and_summary_tool = FunctionTool.from_defaults(fn=combine_audio_segments_and_summary)
    generate_song_tool = FunctionTool.from_defaults(fn=generate_song)
    memory_search_tool = FunctionTool.from_defaults(fn=search_memories)

    llm = OpenAI(model=LLM_MODEL_TYPE, temperature=0.1, timeout=180)

    agent = OpenAIAgent.from_tools([watch_later_videos_tool, video_highlights_tool, audio_generation_tool, download_audio_segments_tool, combine_audio_segments_and_summary_tool, generate_song_tool, memory_search_tool], llm=llm, verbose=True, system_prompt="""
                               You are Bayram's AI podcast assistant. Your goal is to generate podcast from a list of youtube videos.
                               """)
                                   
    return agent

def get_groq_agent():
    watch_later_videos_tool = FunctionTool.from_defaults(fn=get_watch_later_videos)
    video_highlights_tool = FunctionTool.from_defaults(fn=get_video_highlights_in_text)
    audio_generation_tool = FunctionTool.from_defaults(fn=generate_audio)
    download_audio_segments_tool = FunctionTool.from_defaults(fn=download_audio_segments)
    combine_audio_segments_and_summary_tool = FunctionTool.from_defaults(fn=combine_audio_segments_and_summary)
    generate_song_tool = FunctionTool.from_defaults(fn=generate_song)

    llm = Groq(model="llama3-70b-8192")

    agent = ReActAgent.from_tools([watch_later_videos_tool, video_highlights_tool, audio_generation_tool, download_audio_segments_tool, combine_audio_segments_and_summary_tool, generate_song_tool], llm=llm, verbose=True, system_prompt="""
                               You are Bayram's AI podcast assistant. Your goal is to generate podcast from a list of youtube videos.
                               """)
    
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    from llama_index.core import Settings

    Settings.llm = llm
    Settings.embed_model = embed_model

                                   
    return agent

async def generate_podcast(update: Update, context: ContextTypes) -> None:
    agent = get_openai_agent()
    #agent = get_groq_agent()

    print("chat id: "+ str(update.effective_chat.id))

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Starting podcast generation🔧... This may take a while.")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Getting the top 3 videos from your Watch Later playlist...")

    response = agent.chat("Get the top 3 videos from my Watch Later playlist.")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Got videos: {str(response)}. Processing them now...🔄")

    pattern = r"watch\?v=([^&]+)"

    video_ids = re.findall(pattern, str(response))

    for video_id in video_ids:

        print(f"Processing video {video_id}")

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Getting the top highlights of the video...")
        video_highlights = agent.chat(f"Get the top highlights of the following video: {video_id}")

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Downloading audio segments for the top highlights of the video...🎧")

        audio_segments = agent.chat(f"Download audio segments for the top highlights of the video")

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Fetching memories related to the video...🧠")
        memories = agent.chat(f"Get memories related to this video")

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Generating a summary of the top highlights of the video...📝")

        summary_file = agent.chat(f"Generate a summary of the top highlights of the video in a format of personal podcast for Bayram. Use relevant memores. Use friendly and conversational tone.  E.g. 'Hi Bayram, I hope you are enjoying your walk. Let me tell you about this video from your Watch Later list. This video is about <description of video, what is it about, who is in this video> . <Then describe key highlights in a conversational tone and explain why they are important for Bayram as an entrepreneur and AI enthusisast. Mention memories relevant to this video. Keep it informal>. Now you can listen to these highlights or skip to the next video '. Generate audio and save to a file")

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Combining the audio segments of the top highlights of the video and the audio summary of the highlights into a single audio file...🎙️")
        combined_audio = agent.chat(f"Combine the audio segments of the top highlights of the video and the audio summary of the highlights into a single audio file")

        print(combined_audio)

        combined_audio_path = f"combined_audio_{video_id}.mp3"

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Here is an episode just for you! Enjoy!🎧")
        await update.message.reply_audio(audio=open(combined_audio_path, "rb"))

    await update.message.reply_text("Podcast generation completed ✅")

    return ConversationHandler.END

# memories = memoryStorage.get_all()
# print(memories)


app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

app.add_handler(CommandHandler("generate_podcast", generate_podcast))

app.run_polling()


# agent = get_agent()

# # video_ids = [
# #     "SyWC8ZFVxGo",
# #     "e-gwvmhyU7A",
# #     "PgGKhsWhUu8",
# # ]

# response = agent.chat("Get the top 3 videos from my Watch Later playlist.")

# pattern = r"watch\?v=([^&]+)"

# video_ids = re.findall(pattern, str(response))

# #print(video_ids)

# for video_id in video_ids:

#     print(f"Processing video {video_id}")

#     # podcast_intro_file = agent.chat(f"Generate short introductory song for the podcast with 5 seconds duration.")

#     video_highlights = agent.chat(f"Get the top highlights of the following video: {video_id}")

#     audio_segments = agent.chat(f"Download audio segments for the top highlights of the video")

#     summary_file = agent.chat(f"Generate a summary of the top highlights of the video in a format of personal podcast for Bayram. Use friendly and conversational tone.  E.g. 'Hi Bayram, I hope you are enjoying your walk. Let me tell you about this video from your Watch Later list. This video is about <description of video, what is it about, who is in this video> . <Then describe key highlights in a conversational tone and explain why they are important for Bayram as an entrepreneur and AI enthusisast. Keep it informal>. Now you can listen to these highlights or skip to the next video '. Generate audio and save to a file")

#     combined_audio = agent.chat(f"Combine the audio segments of the top highlights of the video and the audio summary of the highlights into a single audio file")


    
