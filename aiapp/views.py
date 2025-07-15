from django.shortcuts import render
import os
# Create your views here.
import os

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")



import google.generativeai as genai

genai.configure(api_key=GOOGLE_API_KEY)


model = genai.GenerativeModel("models/gemini-2.5-flash")

response = model.generate_content("Tell me a new Nigerian joke")
print(response.text)