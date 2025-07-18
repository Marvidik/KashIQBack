from django.shortcuts import render
from dotenv import load_dotenv
import google.generativeai as genai
import os

# Load the .env file into environment variables
load_dotenv()
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("models/gemini-2.5-flash")

response = model.generate_content("Tell me a new Nigerian joke")
print(response.text)