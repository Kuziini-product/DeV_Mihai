import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import av
import speech_recognition as sr
import numpy as np
import queue

st.set_page_config(page_title="Microfon Test", layout="centered")

st.title("🎙️ Test recunoaștere vocală Kuziini")

result_text = st.empty()
status_indicator = st.empty()

audio_queue = queue.Queue()

# Funcție pentru prelucrarea streamului audio
class AudioProcessor:
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        volume = np.abs(audio).mean()
        status_indicator.markdown(f"**Nivel sunet:** {'🔴' if volume < 100 else '🟢'}")
        audio_queue.put(audio.tobytes())
        return frame

# Configurare microfon WebRTC
webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    in_audio=True,
    client_settings=ClientSettings(
        media_stream_constraints={
            "audio": True,
            "video": False,
        },
        rtc_configuration={},
    ),
    audio_processor_factory=AudioProcessor
)

# Recunoaștere cu SpeechRecognition
recognizer = sr.Recognizer()
with sr.Microphone() as source:
    st.info("Vorbește... microfonul este activ.")
    try:
        audio_data = recognizer.listen(source, timeout=5)
        text = recognizer.recognize_google(audio_data, language="ro-RO")
        result_text.success(f"🔊 Text recunoscut: {text}")
    except Exception as e:
        result_text.error(f"Eroare: {str(e)}")
