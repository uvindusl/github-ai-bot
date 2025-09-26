import google.generativeai as genai
from config import settings 

genai.configure(api_key=settings.gemini_api_key)
ai_model = genai.GenerativeModel("gemini-2.5-flash")