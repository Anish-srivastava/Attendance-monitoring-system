import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase: Client = None

def init_supabase():
    """Initialize Supabase client"""
    global supabase
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.error("❌ Supabase credentials not found in environment variables!")
            logger.info("Please set SUPABASE_URL and SUPABASE_KEY in .env file")
            return None
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase client initialized successfully")
        return supabase
    except Exception as e:
        logger.error(f"❌ Error initializing Supabase: {e}")
        return None

def get_supabase_client():
    """Get Supabase client instance"""
    global supabase
    if supabase is None:
        supabase = init_supabase()
    return supabase
