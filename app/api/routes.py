from dotenv import load_dotenv
import os
import openai
from fastapi import APIRouter
from pydantic import BaseModel

load_dotenv()  # Only needed for local development

router = APIRouter()

# Pydantic model for user input
class ChatInput(BaseModel):
    message: str

# API route
@router.post("/chat")
async def chat(chat_input: ChatInput):
    try:
        # ✅ Define OpenAI client inside route to access env vars properly on Render
        client = openai.OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )

        # LLM call
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",  # You can change this to any OpenRouter-supported model
            messages=[
                {"role": "user", "content": chat_input.message}
            ]
        )

        reply = response.choices[0].message.content
        return {"response": reply}

    except Exception as e:
        print("❌ ERROR:", str(e))
        return {"response": f"Error: {str(e)}"}
