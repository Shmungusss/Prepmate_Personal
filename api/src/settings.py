import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ollama embedding server
LLM = os.getenv("LLM", "gpt-5.4-mini-2026-03-17")
VISION_LLM = os.getenv("VISION_LLM", "gpt-4o")
