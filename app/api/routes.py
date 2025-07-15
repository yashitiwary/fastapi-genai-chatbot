from dotenv import load_dotenv
import os
import requests
from fastapi import APIRouter
from pydantic import BaseModel
import json

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
        "hf_token_exists": os.getenv("HUGGINGFACE_TOKEN") is not None,
        "all_env_vars": list(os.environ.keys())
    }

@router.post("/chat")
async def chat(chat_input: ChatInput):
    try:
        print(f"🔍 Message received: {chat_input.message}")
        
        # Use Hugging Face Inference API (free)
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        
        if hf_token:
            # Use Hugging Face with token (better rate limits)
            print("✅ Using Hugging Face with token...")
            headers = {
                "Authorization": f"Bearer {hf_token}",
                "Content-Type": "application/json"
            }
            url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        else:
            # Use Hugging Face without token (more limited)
            print("✅ Using Hugging Face without token...")
            headers = {"Content-Type": "application/json"}
            url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
        payload = {
            "inputs": chat_input.message,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7
            }
        }
        
        print("✅ Sending request to Hugging Face...")
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"✅ Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Got response: {result}")
            
            if isinstance(result, list) and len(result) > 0:
                reply = result[0].get("generated_text", "Sorry, I couldn't generate a response.")
                # Clean up the response (remove the input prompt)
                if chat_input.message in reply:
                    reply = reply.replace(chat_input.message, "").strip()
                return {"response": reply}
            else:
                return {"response": "Sorry, I couldn't generate a response."}
        else:
            print(f"❌ Error: {response.text}")
            return {"response": f"Error: {response.text}"}
            
    except Exception as e:
        print("❌ ERROR:", str(e))
        return {"response": f"Error: {str(e)}"}

@router.post("/chat-simple")
async def chat_simple(chat_input: ChatInput):
    """Simple chatbot without external APIs"""
    try:
        message = chat_input.message.lower()
        
        # Simple rule-based responses
        if "hello" in message or "hi" in message:
            return {"response": "Hello! How can I help you today?"}
        elif "how are you" in message:
            return {"response": "I'm doing well, thank you for asking! How are you?"}
        elif "bye" in message or "goodbye" in message:
            return {"response": "Goodbye! Have a great day!"}
        elif "weather" in message:
            return {"response": "I don't have access to current weather data, but I hope it's nice where you are!"}
        elif "time" in message:
            return {"response": "I don't have access to real-time data, but you can check your device's clock!"}
        elif "name" in message:
            return {"response": "I'm your friendly chatbot! What's your name?"}
        else:
            return {"response": f"You said: '{chat_input.message}'. That's interesting! Tell me more about that."}
            
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

@router.get("/test-hf")
async def test_hf():
    """Test Hugging Face connection"""
    try:
        headers = {"Content-Type": "application/json"}
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
        payload = {
            "inputs": "Hello, how are you?",
            "parameters": {"max_length": 100}
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
        
    except Exception as e:
        return {"error": str(e)}