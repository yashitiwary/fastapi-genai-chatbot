from dotenv import load_dotenv
import os
import openai
from fastapi import APIRouter
from pydantic import BaseModel

# ✅ Only load .env file in local development, not on Render
if os.getenv("RENDER") != "true":
    load_dotenv()

router = APIRouter()

class ChatInput(BaseModel):
    message: str

@router.get("/debug")
async def debug():
    """Debug endpoint to check environment variables"""
    return {
        "render_env": os.getenv("RENDER"),
        "api_key_exists": os.getenv("OPENROUTER_API_KEY") is not None,
        "api_key_length": len(os.getenv("OPENROUTER_API_KEY", "")),
        "api_key_preview": os.getenv("OPENROUTER_API_KEY", "")[:15] + "..." if os.getenv("OPENROUTER_API_KEY") else "None",
        "all_env_vars": list(os.environ.keys())
    }

@router.post("/chat")
async def chat(chat_input: ChatInput):
    try:
        # Debug environment
        api_key = os.getenv("OPENROUTER_API_KEY")
        render_env = os.getenv("RENDER")
        
        print(f"🔍 Running on Render: {render_env}")
        print(f"🔍 API Key exists: {api_key is not None}")
        print(f"🔍 API Key length: {len(api_key) if api_key else 0}")
        print(f"🔍 API Key starts with: {api_key[:10] if api_key else 'None'}...")
        print(f"🔍 Message received: {chat_input.message}")
        
        # Check if API key exists
        if not api_key:
            print("❌ No API key found in environment variables")
            return {"response": "Error: API key not found in environment variables"}
        
        # Check if API key format is correct
        if not api_key.startswith("sk-or-v1-"):
            print("❌ API key format seems incorrect")
            return {"response": "Error: API key format seems incorrect"}
        
        print("✅ Creating OpenAI client...")
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        print("✅ Sending request to OpenRouter...")
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "user", "content": chat_input.message}
            ]
        )
        
        reply = response.choices[0].message.content
        print(f"✅ Got response: {reply[:50]}...")
        
        return {"response": reply}
        
    except Exception as e:
        print("❌ ERROR:", str(e))
        print("❌ Error type:", type(e).__name__)
        return {"response": f"Error: {str(e)}"}

@router.get("/test-connection")
async def test_connection():
    """Test endpoint to verify OpenRouter connection"""
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            return {"status": "error", "message": "No API key found"}
        
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "user", "content": "Hello, just testing connection"}
            ]
        )
        
        return {
            "status": "success", 
            "message": "Connection working",
            "response": response.choices[0].message.content
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}