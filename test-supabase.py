from supabase import create_client, Client
import os
from dotenv import load_dotenv # type: ignore

# Load environment variables from .env file
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_test_data():
    data = {
        "filename": "test_audio.mp3",
        "transcript": "This is a test transcript.",
        "summary": "This is a test summary."
    }
    response = supabase.table("transcriptions").insert(data).execute()
    print(response)

insert_test_data()
