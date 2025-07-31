# services/ai_service.py
import google.generativeai as genai
import os
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini Model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")


def get_user_transaction_summary(user):
    """
    Fetch recent transactions for the given user.
    """
    from mono.models import Transaction
    # ✅ Fixed query to use account__user
    transactions = (
        Transaction.objects.filter(account__user=user)
        .values('date', 'amount', 'type', 'narration')
    )
    return list(transactions)


def build_prompt(user, question):
    """
    Build a detailed prompt using transaction history and previous chats.
    """
    from aiapp.models import ChatHistory

    # Fetch last 5 previous chats
    history = ChatHistory.objects.filter(user=user).order_by('-timestamp')[:5]
    previous_chats = "\n".join([f"User: {h.question}\nAI: {h.response}" for h in history])

    # Fetch user transaction summary
    transactions = get_user_transaction_summary(user)

    # If no transactions found, adjust the message
    transaction_info = transactions if transactions else "No recent transactions found."

    prompt = f"""
You are a financial AI assistant.
Here is the user's recent transaction history: {transaction_info}.
Previous conversation:
{previous_chats}

User's question: {question}
Provide clear, actionable financial insights based on their transaction data.
"""
    return prompt


def get_ai_response(user, question):
    """
    Generate AI response using Gemini and save the chat history.
    """
    from aiapp.models import ChatHistory

    prompt = build_prompt(user, question)
    response = model.generate_content(prompt)

    # Save chat history
    ChatHistory.objects.create(
        user=user,
        question=question,
        response=response.text if response.text else "No response generated."
    )

    return response.text if response.text else "I couldn't generate a response at this moment."
