import streamlit as st
import google.generativeai as genai
import os

# Configure the Google Generative AI API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    return file

# Setup Streamlit interface
st.title("Transcription Audio en Texte")

# Upload audio file
uploaded_file = st.file_uploader("Upload your audio file", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    # Save uploaded file
    with open("temp_audio.mp3", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success("Fichier audio téléchargé avec succès!")

    # Transcription button
    if st.button("Retranscrire l'audio"):
        # Upload file to Gemini
        file = upload_to_gemini("temp_audio.mp3", mime_type="audio/mpeg")
        
        # Configuration du modèle
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
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
        
        # Save the transcription to a text file
        transcription_text = response.text
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
