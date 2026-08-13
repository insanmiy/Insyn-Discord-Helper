from google import genai
from src.config.settings import settings


def create_gemini_client():
	client = genai.Client(api_key=settings.GEMINI_API_KEY)
	return client
