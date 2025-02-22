from fastapi import FastAPI, UploadFile, File, HTTPException
import whisper
import openai
from transformers import pipeline
from supabase import create_client, Client
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize FastAPI
app = FastAPI()

# Load Whisper AI Model
whisper_model = whisper.load_model("small")

# Load Summarization Model (Hugging Face BART)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Directory to temporarily store uploaded audio
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload an audio file, transcribe it using Whisper AI, generate a summary, and store the results in Supabase.
    """
    try:
        file_path = f"{UPLOAD_DIR}/{file.filename}"

        # Save file locally
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Upload file to Supabase Storage
        supabase.storage.from_("podcasts").upload(file.filename, file_path)

        # Transcribe audio with Whisper AI
        result = whisper_model.transcribe(file_path)
        transcript = result["text"]

        # Summarize the transcript
        summary = summarizer(transcript, max_length=200, min_length=50, do_sample=False)[0]["summary_text"]

        # Store in Supabase Database
        response = supabase.table("transcriptions").insert({
            "filename": file.filename,
            "transcript": transcript,
            "summary": summary
        }).execute()

        return {
            "message": "Transcription successful",
            "transcript": transcript,
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
