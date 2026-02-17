import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ollama embedding server
LLM = os.getenv("LLM", "gpt-5.2")
