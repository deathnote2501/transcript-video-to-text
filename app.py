import streamlit as st
import google.generativeai as genai
import os
from pydub import AudioSegment
import math

# Configure the Google Generative AI API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    return file

def split_audio(audio_path, segment_length_ms=300000):
    """Split audio into chunks of the specified segment length (default: 5 minutes)."""
    audio = AudioSegment.from_file(audio_path)
    duration_ms = len(audio)
    num_segments = math.ceil(duration_ms / segment_length_ms)
    
    segments = []
    for i in range(num_segments):
        start_time = i * segment_length_ms
        end_time = min((i + 1) * segment_length_ms, duration_ms)
        segment = audio[start_time:end_time]
        segment_path = f"segment_{i}.mp3"
        segment.export(segment_path, format="mp3")
        segments.append(segment_path)
    
    return segments

def transcribe_audio_segment(segment_path):
    """Transcribe a single audio segment."""
    file = upload_to_gemini(segment_path, mime_type="audio/mpeg")
    
    # Configuration du modèle
    generation_config = {
        "temperature": 0,
        "top_p": 0.9,
        "top_k": 50,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    # Start chat session for transcription
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    file,
                ],
            },
        ]
    )

    # Retrieve the transcription response
    response = chat_session.send_message("Retranscris cet audio en texte sans identifier les participants.")
    return response.text

# Password protection using st.secrets
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Mot de passe", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Mot de passe", type="password", on_change=password_entered, key="password")
        st.error("Mot de passe incorrect")
        return False
    else:
        return True

if check_password():
    # Display the main interface once the password is correct
    st.markdown("<h1 style='text-align: center;'>Retranscription textuelle de vos visios</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Par Jérome IAvarone - IAvaronce conseil</p>", unsafe_allow_html=True)
    st.write("")

    image_url = "https://www.iacademy-formation.com/wp-content/uploads/2024/08/iyus-sugiharto-jpkxJAcp6a4-unsplash-modified-1.png"
    st.image(image_url, use_column_width=True)
    # Upload audio file
    st.markdown("<h2 style='text-align: left;'>Chargez vos fichiers audio</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["mp3", "wav", "m4a"])

    st.write("")
    st.write("")
    st.write("")
    st.markdown("<p style='text-align: center;'>© 2024 Jérome IAvarone - jerome.iavarone@gmail.com</p>", unsafe_allow_html=True)

    if uploaded_file is not None:
        # Save uploaded file
        with open("temp_audio.mp3", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success("Fichier audio téléchargé avec succès!")

        # Transcription button
        if st.button("Retranscrire l'audio"):
            # Split the audio into 5-minute segments
            segments = split_audio("temp_audio.mp3")
            transcription_text = ""

            # Transcribe each segment and concatenate the result
            for i, segment_path in enumerate(segments):
                st.write(f"Transcription du segment {i + 1}/{len(segments)} en cours...")
                segment_text = transcribe_audio_segment(segment_path)
                transcription_text += segment_text + "\n"

            # Save the entire transcription to a text file
            with open("transcription.txt", "w") as text_file:
                text_file.write(transcription_text)

            st.success("Transcription terminée!")
            st.text_area("Texte transcrit", transcription_text)

            # Download button for the transcription
            with open("transcription.txt", "rb") as f:
                st.download_button(
                    label="Télécharger le fichier texte",
                    data=f,
                    file_name="transcription.txt",
                    mime="text/plain",
                )
