import os
import requests
import tempfile
import base64
import time,edge_tts,asyncio
import streamlit as st
from gtts import gTTS
import google.generativeai as genai

# Keys
ASSEMBLYAI_API_KEY = st.secrets["ASSEMBLYAI_API_KEY"]
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

ASSEMBLYAI_HEADERS = {"authorization": ASSEMBLYAI_API_KEY}

# -----------------------------
# Upload audio file to AssemblyAI
# -----------------------------
def upload_file(filename: str) -> str:
    """Upload a file to AssemblyAI and return the URL."""
    upload_url = "https://api.assemblyai.com/v2/upload"
    CHUNK_SIZE = 5_242_880  # 5MB

    with open(filename, "rb") as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            response = requests.post(upload_url, headers=ASSEMBLYAI_HEADERS, data=data)
            if response.status_code != 200:
                raise RuntimeError(f"Upload failed: {response.status_code} {response.text}")

    return response.json()["upload_url"]

# -----------------------------
# Text-to-Speech playback
# -----------------------------
async def speak_local_async(text: str):
    """Convert text to speech using Edge TTS, fallback to text if it fails."""
    if not text:
        return

    try:
        # Use a modern neural voice
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")

        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            await communicate.save(fp.name)
            audio_bytes = open(fp.name, "rb").read()

        # Encode audio for Streamlit playback
        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        audio_html = f"""
        <audio autoplay controls style="width: 100%;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

    except Exception as e:
        # Fallback: just show text if audio fails
        st.warning(f"(Audio unavailable, showing text instead: {e})")
        st.write(text)

def speak_local(text: str):
    """Wrapper to run async Edge TTS in Streamlit."""
    asyncio.run(speak_local_async(text))

def stop_speaking():
    """No-op placeholder for compatibility."""
    pass

# -----------------------------
# Browser mic capture + STT
# -----------------------------
def listen_once_browser() -> str:
    """Capture audio from browser mic and transcribe with AssemblyAI."""
    audio_file = st.audio_input("🎤 Speak your query")
    if audio_file is not None:
        with open("temp.wav", "wb") as f:
            f.write(audio_file.getbuffer())

        try:
            audio_url = upload_file("temp.wav")
        except Exception as e:
            st.error(f"Upload failed: {e}")
            return ""

        transcript_url = "https://api.assemblyai.com/v2/transcript"
        response = requests.post(transcript_url,
                                 json={"audio_url": audio_url},
                                 headers=ASSEMBLYAI_HEADERS)
        if response.status_code != 200:
            st.error(f"Transcription request failed: {response.text}")
            return ""

        transcript_id = response.json().get("id")
        if not transcript_id:
            st.error("No transcript ID returned.")
            return ""

        # Poll until transcription completes
        while True:
            poll = requests.get(f"{transcript_url}/{transcript_id}", headers=ASSEMBLYAI_HEADERS)
            status = poll.json().get("status")
            if status == "completed":
                return poll.json().get("text", "")
            elif status == "error":
                st.error(f"AssemblyAI error: {poll.json().get('error')}")
                return ""
            else:
                st.info("⏳ Transcribing… please wait")
                time.sleep(2)
    return ""

def career_ai_reply(user_text: str) -> str:
    """Generate intelligent career guidance reply using Google Gemini."""
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")  # fast + stable
        response = model.generate_content(
            f"You are a career guidance assistant. User asked: {user_text}"
        )
        return response.text
    except Exception as e:
        return f"(Career AI error: {e})"
