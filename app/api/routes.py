from fastapi import APIRouter
from pydantic import BaseModel
import openai

router = APIRouter()

# ✅ Use OpenRouter as base URL
client = openai.OpenAI(
    api_key="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",  # paste your key here
    base_url="https://openrouter.ai/api/v1"
)

class ChatInput(BaseModel):
    message: str

@router.post("/chat")
async def chat(chat_input: ChatInput):
    try:
        print("📩 User:", chat_input.message)

        response = client.chat.completions.create(
    model="mistralai/mistral-7b-instruct",
    messages=[
        {"role": "user", "content": chat_input.message}
    ]
)


        reply = response.choices[0].message.content
        print("🤖 Bot:", reply)

        return {"response": reply}

    except Exception as e:
        print("❌ ERROR:", str(e))
        return {"response": f"Error: {str(e)}"}
