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
            url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
        else:
            # Use Hugging Face without token (more limited)
            print("✅ Using Hugging Face without token...")
            headers = {"Content-Type": "application/json"}
            url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
        
        payload = {
            "inputs": f"Human: {chat_input.message}\nBot:",
            "parameters": {
                "max_length": 100,
                "temperature": 0.7,
                "do_sample": True,
                "top_p": 0.9
            }
        }
        
        print("✅ Sending request to Hugging Face...")
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"✅ Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Got response: {result}")
            
            if isinstance(result, list) and len(result) > 0:
                reply = result[0].get("generated_text", "")
                
                # Clean up the response
                if reply:
                    # Remove the input prompt from the response
                    if f"Human: {chat_input.message}" in reply:
                        reply = reply.split("Bot:")[-1].strip()
                    # Remove any remaining Human: or Bot: prefixes
                    reply = reply.replace("Human:", "").replace("Bot:", "").strip()
                    
                    if reply and len(reply) > 5:  # Make sure we have a meaningful response
                        return {"response": reply}
                
                # If no good response, fall back to simple chatbot
                print("⚠️ No good response from HF, falling back to simple chatbot")
                return await chat_simple_internal(chat_input)
            else:
                print("⚠️ Invalid response format from HF")
                return await chat_simple_internal(chat_input)
        else:
            print(f"❌ HF API Error: {response.text}")
            return await chat_simple_internal(chat_input)
            
    except Exception as e:
        print("❌ ERROR:", str(e))
        return {"response": f"Error: {str(e)}"}

@router.post("/chat-simple")
async def chat_simple(chat_input: ChatInput):
    """Simple chatbot without external APIs"""
    return await chat_simple_internal(chat_input)

async def chat_simple_internal(chat_input: ChatInput):
    """Internal function for simple chatbot logic"""
    try:
        message = chat_input.message.lower()
        
        # Enhanced rule-based responses
        if "hello" in message or "hi" in message or "hey" in message:
            return {"response": "Hello! How can I help you today?"}
        elif "how are you" in message:
            return {"response": "I'm doing well, thank you for asking! How are you?"}
        elif "bye" in message or "goodbye" in message:
            return {"response": "Goodbye! Have a great day!"}
        elif "fruit" in message:
            return {"response": "Here are 5 fruits: Apple, Banana, Orange, Mango, and Grapes! Do you have a favorite?"}
        elif "color" in message:
            return {"response": "Some beautiful colors include: Red, Blue, Green, Yellow, and Purple!"}
        elif "animal" in message:
            return {"response": "Here are some animals: Dog, Cat, Elephant, Lion, and Dolphin!"}
        elif "weather" in message:
            return {"response": "I don't have access to current weather data, but I hope it's nice where you are!"}
        elif "time" in message:
            return {"response": "I don't have access to real-time data, but you can check your device's clock!"}
        elif "name" in message and "your" in message:
            return {"response": "I'm your friendly chatbot! What's your name?"}
        elif "help" in message:
            return {"response": "I can help you with simple questions! Try asking about fruits, colors, animals, or just chat with me."}
        else:
            responses = [
                f"That's interesting! You mentioned '{chat_input.message}'. Tell me more about that.",
                f"I heard you say '{chat_input.message}'. What would you like to know about it?",
                f"Thanks for sharing '{chat_input.message}' with me. How can I help you with that?",
                "I'm still learning! Can you ask me about fruits, colors, animals, or something else?",
                "That's a great question! I'm a simple chatbot, so I might not have all the answers, but I'm here to help!"
            ]
            import random
            return {"response": random.choice(responses)}
            
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