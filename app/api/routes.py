from dotenv import load_dotenv
import os
import openai
from fastapi import APIRouter
from pydantic import BaseModel

load_dotenv()

router = APIRouter()

client = openai.OpenAI(
    api_key=os.getenv("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"),
    base_url="https://openrouter.ai/api/v1"
)

class ChatInput(BaseModel):
    message: str

@router.post("/chat")
async def chat(chat_input: ChatInput):
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "user", "content": chat_input.message}
            ]
        )
        reply = response.choices[0].message.content
        return {"response": reply}
    except Exception as e:
        print("❌ ERROR:", str(e))
        return {"response": f"Error: {str(e)}"}
