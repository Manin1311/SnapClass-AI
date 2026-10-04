import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Read from st.secrets or fallback to environment variables / .env
supabase_url = None
supabase_key = None

try:
    if "SUPABASE_URL" in st.secrets:
        supabase_url = st.secrets["SUPABASE_URL"]
    if "SUPABASE_KEY" in st.secrets:
        supabase_key = st.secrets["SUPABASE_KEY"]
except Exception:
    pass

if not supabase_url:
    supabase_url = os.getenv("SUPABASE_URL")
if not supabase_key:
    supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    # Use dummy placeholder so imports don't immediately crash if keys are missing
    supabase_url = "https://placeholder.supabase.co"
    supabase_key = "placeholder-key"

supabase: Client = create_client(supabase_url, supabase_key)