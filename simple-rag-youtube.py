import streamlit as st
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(video_url: str) -> str:
    if "youtube.com/watch?v=" in video_url:
        return video_url.split("v=")[-1].split("&")[0]
    elif "youtube.com/shorts/" in video_url:
        return video_url.split("/shorts/")[-1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL")

def fetch_transcript(video_url: str) -> str:
    try:
        video_id = extract_video_id(video_url)
        transcript_list = YouTubeTranscriptApi().fetch(video_id)
        return " ".join([entry.text for entry in transcript_list])
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return ""

def chat_with_transcript(transcript: str, question: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    Based on this YouTube video transcript, answer the following question:
    
    Transcript: {transcript[:4000]}...
    
    Question: {question}
    
    Answer:
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

st.title("Chat with YouTube Video 📺")
st.caption("Simple YouTube video chat using OpenAI API")

api_key = st.text_input("OpenAI API Key", type="password")
video_url = st.text_input("YouTube Video URL")

if api_key and video_url:
    if 'transcript' not in st.session_state:
        with st.spinner("Fetching transcript..."):
            st.session_state.transcript = fetch_transcript(video_url)
        
        if st.session_state.transcript:
            st.success("Transcript loaded!")
        else:
            st.error("Failed to load transcript")
    
    if st.session_state.get('transcript'):
        question = st.text_input("Ask a question about the video")
        
        if question:
            with st.spinner("Generating answer..."):
                answer = chat_with_transcript(st.session_state.transcript, question, api_key)
                st.write(answer)